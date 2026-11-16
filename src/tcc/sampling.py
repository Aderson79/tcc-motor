"""Stratified draw of the development and evaluation sets (Etapa 3)."""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from . import catalog
from .common import GEN, LETTERS, config, profile_id


def draw_dev(eligible: dict[str, list[str]], seed: int, per_type: int) -> list[tuple[str, str]]:
    """eligible: type letter -> sorted codes. Returns [(type, code)] in profile order."""
    rng = np.random.default_rng(seed)
    out = []
    for letter in LETTERS:
        codes = sorted(eligible.get(letter, []))
        n = min(per_type, len(codes))
        out += [(letter, str(c)) for c in rng.choice(codes, size=n, replace=False)] if n else []
    return out


def draw_eval(eligible: dict[str, list[str]], used: set[str], seed: int, per_type: int
              ) -> tuple[list[tuple[str, str]], dict]:
    """Draw per type among the eligible occupations not in `used`.

    Shortage rule: a type with fewer than `per_type` remaining contributes all of them and
    the deficit is drawn uniformly among the remaining occupations of the other types.
    """
    rng = np.random.default_rng(seed)
    out, deficit, short = [], 0, {}
    for letter in LETTERS:
        codes = sorted(c for c in eligible.get(letter, []) if c not in used)
        n = min(per_type, len(codes))
        if n < per_type:
            deficit += per_type - n
            short[letter] = n
        out += [(letter, str(c)) for c in rng.choice(codes, size=n, replace=False)] if n else []
    extra = []
    if deficit:
        taken = used | {c for _, c in out}
        pool = sorted((c, l) for l in LETTERS for c in eligible.get(l, []) if c not in taken)
        idx = rng.choice(len(pool), size=min(deficit, len(pool)), replace=False)
        extra = [(pool[i][1], pool[i][0]) for i in idx]
        out += extra
    info = {"redistributed": bool(deficit), "deficit": deficit, "short_types": short,
            "extra": [f"{l}:{c}" for l, c in extra]}
    return out, info


def draw_replacement(eligible: dict[str, list[str]], letter: str, used: set[str], seed: int,
                     set_name: str, n_previous: int) -> str | None:
    """Replacement of the same type among eligible occupations not used in any set."""
    pool = sorted(c for c in eligible.get(letter, []) if c not in used)
    if not pool:
        return None
    rng = np.random.default_rng([seed, 0 if set_name == "dev" else 1, n_previous])
    return str(rng.choice(pool))


def eligible_by_type() -> dict[str, list[str]]:
    df = catalog.load().df
    return {l: sorted(df.index[df["type"] == l]) for l in LETTERS}


def used_codes() -> set[str]:
    """Every occupation already used (drawn, replaced in or discarded) in any set."""
    used: set[str] = set()
    for name in ("sample_dev.csv", "sample_eval.csv"):
        if (GEN / name).exists():
            used |= set(pd.read_csv(GEN / name, dtype=str)["code"])
    if (GEN / "substituicoes.csv").exists():
        sub = pd.read_csv(GEN / "substituicoes.csv", dtype=str)
        used |= set(sub["origem_descartada"]) | set(sub["nova_origem"])
    return used


def main() -> None:
    set_name = sys.argv[1]
    out_path = GEN / f"sample_{set_name}.csv"
    if out_path.exists():
        print(f"{out_path.name} já existe; nada a fazer.")
        return
    cfg = config()["sampling"]
    eligible = eligible_by_type()
    if set_name == "dev":
        drawn, info = draw_dev(eligible, cfg["seed_dev"], cfg["dev_per_type"]), {}
    else:
        if not (GEN / "relatos_dev.done").exists():
            raise SystemExit("O conjunto de desenvolvimento precisa estar concluído antes do sorteio da avaliação.")
        drawn, info = draw_eval(eligible, used_codes(), cfg["seed_eval"], cfg["eval_per_type"])
    GEN.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"profile_id": profile_id(set_name, i + 1), "type": l, "code": c}
                  for i, (l, c) in enumerate(drawn)]).to_csv(out_path, index=False)
    print(f"{len(drawn)} ocupações sorteadas para {set_name}. {info}")
    if info.get("redistributed"):
        print("AVISO (Seção 17): houve redistribuição por falta de elegíveis; registre em DESVIOS.md.")
        pd.Series(info).to_json(GEN / "sample_eval_redistribution.json")


if __name__ == "__main__":
    main()
