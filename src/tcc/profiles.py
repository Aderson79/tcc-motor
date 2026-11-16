"""Synthetic profiles (Etapa 4): self-descriptions, title filter, replacements, noise."""
from __future__ import annotations

import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from . import catalog, llm, sampling
from .common import GEN, LETTERS, SET_CONDITIONS, append_jsonl, config, content_words, prompt, read_jsonl

_lock = threading.Lock()
ATTEMPTS = GEN / "relato_attempts.jsonl"
RELATOS = GEN / "relatos.jsonl"
SUBS = GEN / "substituicoes.csv"
SUB_COLS = ["conjunto", "profile_id", "origem_descartada", "nova_origem", "palavras"]


def _norm(word: str) -> str:
    return word[:-1] if word.endswith("s") else word


def title_filter(title: str, relato: str) -> list[str]:
    """Significant title words (final "s" removed) that also occur in the relato."""
    return sorted({_norm(w) for w in content_words(title)} & {_norm(w) for w in content_words(relato)})


def overlap(relato: str, indexed_text: str) -> float:
    words = set(content_words(relato))
    return len(words & set(content_words(indexed_text))) / len(words) if words else 0.0


def count_sentences(text: str) -> int:
    return len(re.findall(r"[^.!?]+[.!?]+", text.strip())) or int(bool(text.strip()))


def add_noise(scores: np.ndarray, sigma: float, seed: int, clip=(1.0, 7.0)) -> np.ndarray:
    """Independent N(0, sigma) per dimension, clipped to [1, 7]."""
    rng = np.random.default_rng(seed)
    return np.clip(scores + rng.normal(0.0, sigma, size=scores.shape), clip[0], clip[1])


def relato_prompt(tasks: list[str]) -> str:
    return prompt("A_relato.txt").replace("{task_statements}", "\n".join(f"- {t}" for t in tasks))


def load_relatos(set_name: str) -> dict[str, dict]:
    return {r["profile_id"]: r for r in read_jsonl(RELATOS) if r["set"] == set_name}


def _substitutions() -> pd.DataFrame:
    return pd.read_csv(SUBS, dtype=str, keep_default_na=False) if SUBS.exists() else pd.DataFrame(columns=SUB_COLS)


def _ensure_relato(set_name: str, pid: str, code: str) -> bool:
    """Generate until the title filter accepts, at most 3 rejected attempts per origin."""
    cat, cfg = catalog.load(), config()["relato"]
    title = cat.df.at[code, "title"]
    with _lock:
        rejected = sum(1 for a in read_jsonl(ATTEMPTS) if a["profile_id"] == pid and a["code"] == code)
    while rejected < cfg["max_filter_attempts"]:
        attempt = rejected + 1
        call = llm.call(relato_prompt(cat.tasks[code]), cfg["model"], cfg["max_tokens"], "relato",
                          set=set_name, profile_id=pid, code=code, attempt=attempt)
        text = call.text.strip()
        matched = title_filter(title, text)
        record = {"set": set_name, "profile_id": pid, "code": code, "attempt": attempt, "relato": text,
                  "matched": matched, "accepted": not matched,
                  "n_sentences": count_sentences(text), "n_words": len(text.split())}
        with _lock:
            if matched:
                append_jsonl(ATTEMPTS, record)
            else:
                append_jsonl(RELATOS, {k: v for k, v in record.items() if k not in ("matched", "accepted")})
        if not matched:
            return True
        rejected += 1
    return False


def generate_relatos(set_name: str) -> None:
    sample = pd.read_csv(GEN / f"sample_{set_name}.csv", dtype=str)
    subs = _substitutions()
    current = dict(zip(sample["profile_id"], sample["code"]))
    for _, s in subs[subs["conjunto"] == set_name].iterrows():
        current[s["profile_id"]] = s["nova_origem"]
    types = dict(zip(sample["profile_id"], sample["type"]))
    done = load_relatos(set_name)
    todo = [pid for pid in sample["profile_id"] if pid not in done]

    with ThreadPoolExecutor(config()["relato"]["concurrency"]) as pool:
        ok = list(pool.map(lambda pid: _ensure_relato(set_name, pid, current[pid]), todo))
    failed = [pid for pid, good in zip(todo, ok) if not good]

    eligible = sampling.eligible_by_type()
    for pid in failed:  # sequential, in profile order, so replacements are reproducible
        while True:
            subs = _substitutions()
            old = current[pid]
            new = sampling.draw_replacement(eligible, types[pid], sampling.used_codes(),
                                            config()["sampling"]["seed_replacement"], set_name,
                                            int((subs["conjunto"] == set_name).sum()))
            if new is None:
                # Tipo esgotado: aplica a mesma regra de falta do sorteio (Seção 6.3), isto é,
                # sorteio uniforme entre as elegíveis restantes dos demais tipos.
                pool = {"*": [c for codes in eligible.values() for c in codes]}
                new = sampling.draw_replacement(pool, "*", sampling.used_codes(),
                                                config()["sampling"]["seed_replacement"], set_name,
                                                int((subs["conjunto"] == set_name).sum()))
                print(f"AVISO: tipo {types[pid]} esgotado; {pid} substituído por ocupação de outro tipo "
                      f"({new}). Registre em DESVIOS.md.")
                types[pid] = catalog.load().df.at[new, "type"]
            words = sorted({w for a in read_jsonl(ATTEMPTS)
                            if a["profile_id"] == pid and a["code"] == old for w in a["matched"]})
            row = pd.DataFrame([[set_name, pid, old, new, " ".join(words)]], columns=SUB_COLS)
            pd.concat([subs, row]).to_csv(SUBS, index=False)
            current[pid] = new
            if _ensure_relato(set_name, pid, new):
                break

    sample.assign(code=sample["profile_id"].map(current), type=sample["profile_id"].map(types)).to_csv(GEN / f"profiles_{set_name}.csv", index=False)
    n_subs = int((_substitutions()["conjunto"] == set_name).sum())
    print(f"relatos {set_name}: {len(sample)} perfis, {n_subs} substituições.")
    if n_subs > 0.10 * len(sample):
        print("PARE (Seção 17): mais de 10% das origens precisaram de substituição.")
    (GEN / f"relatos_{set_name}.done").write_text("ok\n")


def generate_scores(set_name: str) -> None:
    cat = catalog.load()
    profiles = pd.read_csv(GEN / f"profiles_{set_name}.csv", dtype=str)
    base = np.array([cat.scores(c) for c in profiles["code"]])
    for cond in SET_CONDITIONS[set_name]:
        path = GEN / f"scores_{cond}.csv"
        if path.exists():
            continue
        ncfg = config()["noise"]
        noisy = add_noise(base, ncfg["conditions"][cond]["sigma"], ncfg["conditions"][cond]["seed"], ncfg["clip"])
        out = pd.DataFrame(noisy, columns=LETTERS)
        out.insert(0, "profile_id", profiles["profile_id"])
        out.to_csv(path, index=False, float_format="%.17g")
        print(f"notas com ruído salvas em {path.name}")


def main() -> None:
    set_name = sys.argv[1]
    generate_relatos(set_name)
    generate_scores(set_name)


if __name__ == "__main__":
    main()
