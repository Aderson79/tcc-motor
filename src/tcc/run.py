"""Runs the five systems over a profile set (Etapas 7 and 8).

Usage: python -m tcc.run dev|eval
Deterministic systems are recomputed; LLM outputs already saved are never regenerated.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from . import catalog, embed, gold, llm
from .common import GEN, LETTERS, SET_CONDITIONS, append_jsonl, config, read_jsonl
from .profiles import load_relatos
from .systems import va, vb, vc
from .systems.b1 import B1
from .systems.b2 import B2

_lock = threading.Lock()


def rankings_path(set_name: str):
    return GEN / ("rankings.csv" if set_name == "eval" else "rankings_dev.csv")


def timings_path(set_name: str):
    return GEN / ("timings.csv" if set_name == "eval" else "timings_dev.csv")


def run(set_name: str) -> None:
    if not gold.gold_path(set_name).exists():
        raise SystemExit("O gabarito precisa existir antes da execução dos sistemas (python -m tcc.gold).")
    cat, cfg = catalog.load(), config()
    k, n_cand = cfg["retrieval"]["k"], cfg["rerank"]["n_candidates"]
    profiles = pd.read_csv(GEN / f"profiles_{set_name}.csv", dtype=str)
    pids = list(profiles["profile_id"])
    relatos = {pid: r["relato"] for pid, r in load_relatos(set_name).items()}
    limit = cfg["embedding"]["max_seq_length"]

    b1 = B1(cat.codes, [cat.indexed_text(c) for c in cat.codes])           # indexing: not timed
    b2 = B2(cat.codes, cat.df[LETTERS].to_numpy(dtype=float))
    embed.embed_query("warm-up")                                           # model load: not timed
    embed.search(np.zeros(cfg["embedding"]["dim"], dtype=np.float32) + 1e-3, 1)

    rank_rows, time_rows, report = [], [], {"b2_zero_variance_occupations": b2.zero_variance}

    def add(system, cond, pid, run_id, codes, seconds):
        rank_rows.extend({"system": system, "condition": cond, "profile_id": pid, "run": run_id,
                          "rank": i, "code": c} for i, c in enumerate(codes, start=1))
        time_rows.append({"system": system, "condition": cond, "profile_id": pid, "run": run_id, "seconds": seconds})

    for cond in SET_CONDITIONS[set_name]:
        scores_df = pd.read_csv(GEN / f"scores_{cond}.csv", dtype={"profile_id": str}).set_index("profile_id")
        scores = {pid: [float(scores_df.at[pid, l]) for l in LETTERS] for pid in pids}
        over = {"va_texts_over_limit": 0, "vb_texts_over_limit": 0}

        for pid in pids:
            t = time.perf_counter()
            codes = b1.rank(relatos[pid], k)
            add("B1", cond, pid, 0, codes, time.perf_counter() - t)

            t = time.perf_counter()
            codes = b2.rank(np.array(scores[pid]), k)
            add("B2", cond, pid, 0, codes, time.perf_counter() - t)

            t = time.perf_counter()
            text = va.fill_template(scores[pid], relatos[pid])
            codes = embed.search(embed.embed_query(text), k)
            add("V-A", cond, pid, 0, codes, time.perf_counter() - t)
            over["va_texts_over_limit"] += int(embed.n_tokens(text) > limit)

        # V-B: synthesis generated once per profile and condition, then never regenerated.
        synth_path = GEN / f"sinteses_{cond}.jsonl"
        synths = {s["profile_id"]: s for s in read_jsonl(synth_path)}

        def synthesize(pid):
            call = vb.synthesize(scores[pid], relatos[pid], condition=cond, profile_id=pid)
            record = {"profile_id": pid, "condition": cond, "sintese": call.text.strip(),
                      "n_words": len(call.text.split()), "latency_s": call.latency_s,
                      "input_tokens": call.input_tokens, "output_tokens": call.output_tokens,
                      "thinking_tokens": call.thinking_tokens,
                      "model_returned": call.model_returned, "stop_reason": call.stop_reason}
            with _lock:
                append_jsonl(synth_path, record)
            return record

        with ThreadPoolExecutor(cfg["rerank"]["concurrency"]) as pool:
            for record in pool.map(synthesize, [p for p in pids if p not in synths]):
                synths[record["profile_id"]] = record

        candidates, vb_seconds = {}, {}
        for pid in pids:
            t = time.perf_counter()
            candidates[pid] = embed.search(embed.embed_query(synths[pid]["sintese"]), n_cand)
            vb_seconds[pid] = synths[pid]["latency_s"] + time.perf_counter() - t
            add("V-B", cond, pid, 0, candidates[pid][:k], vb_seconds[pid])
            over["vb_texts_over_limit"] += int(embed.n_tokens(synths[pid]["sintese"]) > limit)
        pd.DataFrame([{"profile_id": pid, "rank": i, "code": c}
                      for pid in pids for i, c in enumerate(candidates[pid], start=1)]
                     ).to_csv(GEN / f"vb_candidates_{cond}.csv", index=False)

        # V-C: 10 independent runs over the same 20 candidates, at most 4 simultaneous calls.
        runs_path = GEN / f"vc_runs_{cond}.jsonl"
        runs = {(r["profile_id"], r["run"]): r for r in read_jsonl(runs_path)}

        def rerank(task):
            pid, run_id = task
            cand = candidates[pid]
            pairs = [(cat.df.at[c, "title"], cat.df.at[c, "description"]) for c in cand]
            result = vc.rerank(synths[pid]["sintese"], pairs, cand, condition=cond, profile_id=pid, run=run_id)
            record = {"profile_id": pid, "condition": cond, "run": run_id, "candidates": cand, **result}
            with _lock:
                append_jsonl(runs_path, record)
            return record

        todo = [(pid, r) for pid in pids for r in range(1, cfg["rerank"]["runs"] + 1) if (pid, r) not in runs]
        with ThreadPoolExecutor(cfg["rerank"]["concurrency"]) as pool:
            for record in pool.map(rerank, todo):
                runs[(record["profile_id"], record["run"])] = record
        for pid in pids:
            for run_id in range(1, cfg["rerank"]["runs"] + 1):
                r = runs[(pid, run_id)]
                if r["candidates"] != candidates[pid]:
                    raise SystemExit(f"Candidatos de V-B mudaram para {pid}/{cond}; execuções de V-C inconsistentes.")
                add("V-C", cond, pid, run_id, r["codes"], vb_seconds[pid] + r["latency_s"])
        n_runs = len(pids) * cfg["rerank"]["runs"]
        fallbacks = sum(runs[(p, r)]["fallback"] for p in pids for r in range(1, cfg["rerank"]["runs"] + 1))
        report[cond] = {**over, "vc_runs": n_runs, "vc_fallbacks": int(fallbacks),
                        "vc_resends": int(sum(runs[(p, r)]["resent"] for p in pids
                                              for r in range(1, cfg["rerank"]["runs"] + 1)))}
        if fallbacks > 0.05 * n_runs:
            print(f"PARE (Seção 17): mais de 5% das reordenações em fallback na condição {cond}.")

    pd.DataFrame(rank_rows).to_csv(rankings_path(set_name), index=False)
    pd.DataFrame(time_rows).to_csv(timings_path(set_name), index=False)
    (GEN / f"run_report_{set_name}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        run(sys.argv[1])
    except llm.ModelMismatch as exc:
        raise SystemExit(str(exc))
