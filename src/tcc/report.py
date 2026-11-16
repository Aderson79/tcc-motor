"""Builds the results package (Seção 15). Usage: python -m tcc.report dev|eval"""
from __future__ import annotations

import itertools
import json
import os
import platform
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

from . import catalog, gold, llm, metrics, stats
from .common import GEN, LETTERS, LOGS, PROMPTS, RESULTS, ROOT, SET_CONDITIONS, config, read_jsonl
from .profiles import load_relatos, overlap
from .run import rankings_path, timings_path

SYSTEMS = ["B1", "B2", "V-A", "V-B", "V-C"]
METRIC_NAMES = list(metrics.METRICS)
SIGMA_LABEL = {"dev": "desenvolvimento, σ = 1,0", "main": "σ = 1,0", "sens": "σ = 0,5"}


def f3(x) -> str:
    return "n/d" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or "n/d"


def machine() -> str:
    try:
        import torch
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "sem GPU"
    except Exception:
        gpu = "n/d"
    cpu = platform.processor() or platform.machine()
    try:
        cpu = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
        ram = int(next(l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemTotal"))) / 1e6
    except Exception:
        ram = float("nan")
    device = json.loads((GEN / "embed_report.json").read_text())["device"]
    return (f"{cpu}, {os.cpu_count()} núcleos, {ram:.0f} GB RAM, {gpu}; {platform.platform()}; "
            f"Python {platform.python_version()}; embedding em {device}")


def per_run_metrics(set_name: str) -> pd.DataFrame:
    golds = gold.load(set_name)
    rk = pd.read_csv(rankings_path(set_name), dtype={"profile_id": str, "code": str})
    rows = []
    for (system, cond, pid, run_id), g in rk.groupby(["system", "condition", "profile_id", "run"], sort=False):
        ranking = list(g.sort_values("rank")["code"])
        rows.append({"system": system, "condition": cond, "profile_id": pid, "run": run_id,
                     **metrics.all_metrics(ranking, golds[pid]), "ranking": ranking})
    return pd.DataFrame(rows)


def vc_variation(per_run: pd.DataFrame, set_name: str) -> pd.DataFrame:
    report = json.loads((GEN / f"run_report_{set_name}.json").read_text())
    rows = []
    for cond in SET_CONDITIONS[set_name]:
        vc = per_run[(per_run["system"] == "V-C") & (per_run["condition"] == cond)]
        sds, overlaps, identical = [], [], []
        for _, g in vc.groupby("profile_id"):
            lists = list(g.sort_values("run")["ranking"])
            sds.append(g["ndcg5"].std(ddof=1))
            overlaps.append(np.mean([len(set(a) & set(b)) / 5 for a, b in itertools.combinations(lists, 2)]))
            identical.append(all(l == lists[0] for l in lists))
        rows.append({"condicao": cond, "dp_medio_ndcg5": np.mean(sds), "dp_max_ndcg5": np.max(sds),
                     "sobreposicao_media": np.mean(overlaps), "pct_10_listas_identicas": 100 * np.mean(identical),
                     "reenvios": report[cond]["vc_resends"], "fallbacks": report[cond]["vc_fallbacks"]})
    return pd.DataFrame(rows)


def timing_cost(set_name: str) -> tuple[pd.DataFrame, float]:
    cfg = config()
    tm = pd.read_csv(timings_path(set_name), dtype={"profile_id": str})
    per_query = tm.groupby(["system", "condition", "profile_id"], sort=False)["seconds"].mean().reset_index()
    rows, total = [], 0.0
    for cond in SET_CONDITIONS[set_name]:
        synth = pd.DataFrame(read_jsonl(GEN / f"sinteses_{cond}.jsonl"))
        runs = pd.DataFrame(read_jsonl(GEN / f"vc_runs_{cond}.jsonl"))
        synth["cost"] = [llm.cost(cfg["synthesis"]["model"], i, o)
                         for i, o in zip(synth["input_tokens"], synth["output_tokens"])]
        runs["cost"] = [llm.cost(cfg["rerank"]["model"], i, o)
                        for i, o in zip(runs["input_tokens"], runs["output_tokens"])]
        total += synth["cost"].sum() + runs["cost"].sum()
        vc_cost = synth.set_index("profile_id")["cost"] + runs.groupby("profile_id")["cost"].mean()
        costs = {"B1": 0.0, "B2": 0.0, "V-A": 0.0, "V-B": synth["cost"].mean(), "V-C": vc_cost.mean()}
        for system in SYSTEMS:
            s = per_query[(per_query["system"] == system) & (per_query["condition"] == cond)]["seconds"]
            rows.append({"system": system, "condition": cond, "tempo_media_s": s.mean(), "tempo_mediana_s": s.median(),
                         "tempo_p95_s": s.quantile(0.95), "custo_medio_consulta_usd": costs[system]})
    return pd.DataFrame(rows), total


def gemini_cost(set_name: str) -> float:
    model = config()["relato"]["model"]
    calls = [c for c in read_jsonl(LOGS / "calls.jsonl")
             if c["purpose"] == "relato" and c.get("set") == set_name and not c["error"]]
    return sum(llm.cost(model, c["input_tokens"], c["output_tokens"] + c["thinking_tokens"]) for c in calls)


def performance_table(desc: pd.DataFrame, cond: str) -> list[str]:
    lines = ["| Sistema | nDCG@5 média (DP) [mediana] | P@5 | MAP@5 | MRR@5 origem |", "|---|---|---|---|---|"]
    for system in SYSTEMS:
        d = desc[(desc["system"] == system) & (desc["condition"] == cond)].set_index("metric")
        cell = lambda m: f"{f3(d.at[m, 'media'])} ({f3(d.at[m, 'dp'])}) [{f3(d.at[m, 'mediana'])}]"
        lines.append(f"| {system} | {cell('ndcg5')} | {cell('p5')} | {cell('ap5')} | {cell('mrr5_origem')} |")
    return lines


def build(set_name: str) -> None:
    cfg, cat = config(), catalog.load()
    out = RESULTS if set_name == "eval" else RESULTS / "dev"
    out.mkdir(parents=True, exist_ok=True)
    conds = SET_CONDITIONS[set_name]
    main = conds[0]

    per_run = per_run_metrics(set_name)
    per_profile = per_run.groupby(["system", "condition", "profile_id"], sort=False)[METRIC_NAMES].mean().reset_index()
    per_profile.to_csv(out / "per_profile_metrics.csv", index=False)
    runs_all = pd.concat([pd.DataFrame(read_jsonl(GEN / f"vc_runs_{c}.jsonl")) for c in conds])
    vc_runs = per_run[per_run["system"] == "V-C"][["profile_id", "condition", "run", "ndcg5"]].merge(
        runs_all[["profile_id", "condition", "run", "fallback"]], on=["profile_id", "condition", "run"])
    vc_runs.to_csv(out / "vc_runs.csv", index=False)
    desc = stats.descriptives(per_profile, METRIC_NAMES)
    desc.to_csv(out / "descriptives.csv", index=False)
    variation = vc_variation(per_run, set_name)
    tc, motor_total = timing_cost(set_name)
    tc.to_csv(out / "timing_cost.csv", index=False)
    build_cost = gemini_cost(set_name)

    embed_report = json.loads((GEN / "embed_report.json").read_text())
    run_report = json.loads((GEN / f"run_report_{set_name}.json").read_text())
    summary = {**cat.summary, **embed_report,
               **{f"{c}_{k}": v for c in conds for k, v in run_report[c].items() if "over_limit" in k},
               "b2_zero_variance_occupations": run_report["b2_zero_variance_occupations"]}
    pd.DataFrame([{"item": k, "value": v} for k, v in summary.items()]).to_csv(out / "catalog_summary.csv", index=False)
    subs_path = GEN / "substituicoes.csv"
    subs = pd.read_csv(subs_path, dtype=str, keep_default_na=False) if subs_path.exists() else pd.DataFrame(
        columns=["conjunto", "profile_id", "origem_descartada", "nova_origem", "palavras"])
    subs.to_csv(out / "substituicoes.csv", index=False)
    locked = out / "prompts_travados"
    locked.mkdir(exist_ok=True)
    for p in PROMPTS.glob("*.txt"):
        shutil.copy(p, locked / p.name)

    profiles = pd.read_csv(GEN / f"profiles_{set_name}.csv", dtype=str)
    relatos = load_relatos(set_name)
    rel = pd.DataFrame([relatos[p] for p in profiles["profile_id"]])
    attempts = [a for a in read_jsonl(GEN / "relato_attempts.jsonl") if a["set"] == set_name]
    regen = sum(1 for a in attempts if a["attempt"] < cfg["relato"]["max_filter_attempts"])
    ov = pd.Series([overlap(relatos[p]["relato"], cat.indexed_text(c))
                    for p, c in zip(profiles["profile_id"], profiles["code"])])
    golds = gold.load(set_name)
    n_rel = pd.Series([metrics.n_related(golds[p]) for p in profiles["profile_id"]])
    by_type = profiles["type"].value_counts()
    redistribution = GEN / "sample_eval_redistribution.json"
    redis = json.loads(redistribution.read_text()) if set_name == "eval" and redistribution.exists() else None
    synths = {c: pd.DataFrame(read_jsonl(GEN / f"sinteses_{c}.jsonl")) for c in conds}
    sonnet_models = sorted({m for c in conds for m in synths[c]["model_returned"]} | set(runs_all["model_returned"]))
    gem_models = sorted({c["model_returned"] for c in read_jsonl(LOGS / "calls.jsonl")
                         if c["purpose"] == "relato" and not c["error"]})
    price = cfg["prices"]
    ps, pg = price[cfg["synthesis"]["model"]], price[cfg["relato"]["model"]]

    L: list[str] = []
    title = "RESULTADOS — TCC perfis sintéticos" + ("" if set_name == "eval" else " (conjunto de DESENVOLVIMENTO)")
    L += [f"# {title}", "", "## 0. Identificação",
          f"- Repositório: {git('config', '--get', 'remote.origin.url')} · commit lock-v1: "
          f"{git('rev-parse', '--verify', '-q', 'lock-v1^{commit}')} · commit results-v1: o commit apontado pela tag "
          f"`results-v1` (`git rev-parse results-v1`; pai: {git('rev-parse', 'HEAD')})",
          f"- Data de execução: {pd.Timestamp.now().date()}",
          f"- Modelos (ID devolvido pela API e data de acesso): Sonnet: {', '.join(sonnet_models)} · "
          f"Gemini: {', '.join(gem_models)} · acesso em {cfg['models_access_date']}",
          f"- Embedding: all-mpnet-base-v2, revisão {cfg['embedding']['revision']}, "
          f"sentence-transformers {cfg['embedding']['sentence_transformers_version']}",
          f"- Preços usados (USD/1M tokens, entrada/saída, data, URL): Sonnet {ps['input']}/{ps['output']}, "
          f"{ps['date']}, {ps['url']} · Gemini {pg['input']}/{pg['output']}, {pg['date']}, {pg['url']}",
          f"- O*NET: {cfg['onet']['version']}, download em {cfg['onet']['download_date']}, SHA-256 {cfg['onet']['zip_sha256']}",
          f"- Máquina: {machine()}", ""]
    s = cat.summary
    L += ["## 1. Catálogo",
          f"- Ocupações em occupation_data: {s['occupation_data_rows']} · excluídas por critério: sem descrição "
          f"{s['excluded_no_description']}, sem tarefas {s['excluded_no_tasks']}, sem RIASEC completo "
          f"{s['excluded_no_full_riasec']}, sem relacionadas {s['excluded_no_related']}",
          f"- Catálogo final: {s['catalog_size']}",
          "- Elegíveis por tipo predominante: " + ", ".join(f"{l} {s[f'eligible_{l}']}" for l in LETTERS),
          f"- Ocupações que exigiram divisão em trechos: {embed_report['occupations_split']} "
          f"({f3(embed_report['occupations_split_pct'])}%) · trechos por ocupação: média "
          f"{f3(embed_report['chunks_mean'])}, máx {embed_report['chunks_max']}",
          f"- Enunciados acima de 384 tokens: {embed_report['statements_over_limit']} · textos de perfil acima de "
          "384 tokens: " + "; ".join(f"{SIGMA_LABEL[c]}: V-A {run_report[c]['va_texts_over_limit']}, "
                                     f"V-B {run_report[c]['vb_texts_over_limit']}" for c in conds),
          f"- Ocupações com variância zero no perfil OI (Pearson tratado como −1 em B2): "
          f"{run_report['b2_zero_variance_occupations']}", ""]
    L += [f"## 2. Conjunto de {'avaliação' if set_name == 'eval' else 'desenvolvimento'}",
          "- Perfis por tipo: " + ", ".join(f"{l} {int(by_type.get(l, 0))}" for l in LETTERS)
          + " · redistribuição por falta de elegíveis: "
          + (f"sim — tipos em falta {redis['short_types']}, déficit {redis['deficit']}, sorteadas {redis['extra']} "
             f"(regra: {cfg['sampling']['shortage_rule']})" if redis else "não"),
          f"- Substituições por falha no filtro (dev / avaliação): {(subs['conjunto'] == 'dev').sum()} / "
          f"{(subs['conjunto'] == 'eval').sum()} (lista em substituicoes.csv)",
          f"- Regerações de relato (tentativas 2 e 3): {regen}",
          f"- Relatos: frases média {f3(rel['n_sentences'].mean())} ({rel['n_sentences'].min()}–"
          f"{rel['n_sentences'].max()}), palavras média {f3(rel['n_words'].mean())}",
          f"- Sobreposição relato × texto da origem: média {f3(ov.mean())}, DP {f3(ov.std(ddof=1))}, mediana "
          f"{f3(ov.median())}, mín {f3(ov.min())}, máx {f3(ov.max())}",
          f"- Relacionadas no catálogo por perfil: média {f3(n_rel.mean())}, mín {n_rel.min()}, máx {n_rel.max()}; "
          f"perfis com < 5: {(n_rel < 5).sum()}", ""]
    L += [f"## 3. Desempenho — condição principal ({SIGMA_LABEL[main]}), n = {len(profiles)}"]
    L += performance_table(desc, main) + [""]

    if set_name == "eval":
        comp = stats.comparisons(per_profile, "main")
        comp.to_csv(out / "comparisons.csv", index=False)
        L += ["## 4. Comparações (σ = 1,0, nDCG@5)",
              "| Comp. | d = | média d | mediana d | n | n não nulos | W | p bruto | p Bonferroni | Decisão |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in comp.iterrows():
            L.append(f"| {r['comparacao']} | {r['d']} | {f3(r['media_d'])} | {f3(r['mediana_d'])} | {r['n']} | "
                     f"{r['n_nao_nulos']} | {f3(r['W'])} | {r['p_bruto']:.3g} | {r['p_bonferroni']:.3g} | {r['decisao']} |")
        L += ["", "## 5. Sensibilidade (σ = 0,5) — descritivo"] + performance_table(desc, "sens")
        nd = desc[desc["metric"] == "ndcg5"].pivot(index="system", columns="condition", values="media")
        L += ["", "Diferença do nDCG@5 médio (σ = 0,5 − σ = 1,0): "
              + " · ".join(f"{sy} {nd.at[sy, 'sens'] - nd.at[sy, 'main']:+.3f}" for sy in SYSTEMS), ""]
    else:
        L += ["## 4–5. (comparações e sensibilidade só existem na avaliação)", ""]

    L += ["## 6. Variação da reordenação (V-C)",
          "| Condição | DP médio nDCG@5 | DP máx | sobreposição média | % perfis com 10 listas idênticas | reenvios | fallbacks |",
          "|---|---|---|---|---|---|---|"]
    for _, r in variation.iterrows():
        L.append(f"| {SIGMA_LABEL[r['condicao']]} | {f3(r['dp_medio_ndcg5'])} | {f3(r['dp_max_ndcg5'])} | "
                 f"{f3(r['sobreposicao_media'])} | {f3(r['pct_10_listas_identicas'])} | {r['reenvios']} | {r['fallbacks']} |")
    L += ["", f"## 7. Tempo e custo ({SIGMA_LABEL[main]})",
          "| Sistema | tempo média (s) | mediana | p95 | custo médio/consulta (USD) |", "|---|---|---|---|---|"]
    for _, r in tc[tc["condition"] == main].iterrows():
        L.append(f"| {r['system']} | {r['tempo_media_s']:.4f} | {r['tempo_mediana_s']:.4f} | {r['tempo_p95_s']:.4f} | "
                 f"{r['custo_medio_consulta_usd']:.5f} |")
    L += [f"- Custo total do motor no experimento: {motor_total:.2f} USD · custo de construção do conjunto (Gemini): "
          f"{build_cost:.2f} USD",
          "- Tempo e custo usam 4 e 5 casas decimais porque B1/B2 e o custo por consulta ficariam zerados com 3. "
          "A condição de sensibilidade está em timing_cost.csv.", ""]

    L += ["## 8. Ajuste e desvios", "- Obediência às regras (informativo, nada foi rejeitado por estes critérios):",
          f"  - relatos fora de 3–5 frases: {((rel['n_sentences'] < 3) | (rel['n_sentences'] > 5)).sum()} de {len(rel)}"]
    for c in conds:
        sy = synths[c]
        L.append(f"  - sínteses ({SIGMA_LABEL[c]}): palavras média {f3(sy['n_words'].mean())} "
                 f"({sy['n_words'].min()}–{sy['n_words'].max()}); fora de 80–120: "
                 f"{((sy['n_words'] < 80) | (sy['n_words'] > 120)).sum()}; com dígitos: "
                 f"{sy['sintese'].str.contains(r'[0-9]').sum()}; com \"RIASEC\": "
                 f"{sy['sintese'].str.contains('RIASEC').sum()}; cortadas por max_tokens: "
                 f"{(sy['stop_reason'] == 'max_tokens').sum()}")
    for name in ("AJUSTES.md", "DESVIOS.md"):
        L += [f"- {name} (íntegra):", "", (ROOT / name).read_text(encoding="utf-8").strip(), ""]

    L += ["## 9. Exemplos ilustrativos (para a discussão, sem análise adicional)"]
    rng = np.random.default_rng(cfg["sampling"]["seed_examples"])
    chosen = sorted(rng.choice(profiles["profile_id"], size=2, replace=False))
    L.append(f"- 2 perfis escolhidos pela semente {cfg['sampling']['seed_examples']} (não escolhidos a dedo): "
             + ", ".join(chosen))
    scores = pd.read_csv(GEN / f"scores_{main}.csv", dtype={"profile_id": str}).set_index("profile_id")
    for pid in chosen:
        code = profiles.set_index("profile_id").at[pid, "code"]
        L += ["", f"### {pid} — origem: {code} {cat.df.at[code, 'title']}",
              "- Notas (" + SIGMA_LABEL[main] + "): " + ", ".join(f"{l} {scores.at[pid, l]:.3f}" for l in LETTERS),
              f"- Relato: {relatos[pid]['relato']}",
              f"- Síntese de V-B: {synths[main].set_index('profile_id').at[pid, 'sintese']}"]
        for system in SYSTEMS:
            g = per_run[(per_run["system"] == system) & (per_run["condition"] == main) & (per_run["profile_id"] == pid)]
            ranking = g.sort_values("run").iloc[0]["ranking"]
            label = f"{system}" + (" (execução 1)" if system == "V-C" else "")
            L.append(f"- {label}: " + "; ".join(f"{c} {cat.df.at[c, 'title']} [rel {golds[pid].get(c, 0)}]"
                                                 for c in ranking))
    name = "RESULTADOS.md" if set_name == "eval" else "RESULTADOS_DEV.md"
    (out / name).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"pacote gerado em {out}")

    b2_main = desc[(desc["system"] == "B2") & (desc["condition"] == main) & (desc["metric"] == "ndcg5")]["media"].iloc[0]
    if b2_main > 0.9:
        print("PARE (Seção 17): B2 com nDCG@5 perto de 1 — verifique se o ruído foi aplicado.")
    if motor_total + build_cost > 50:
        print("PARE (Seção 17): custo acima de US$ 50.")


if __name__ == "__main__":
    build(sys.argv[1])
