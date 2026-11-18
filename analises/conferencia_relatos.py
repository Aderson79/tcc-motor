"""Conferência humana dos relatos sintéticos (feita DEPOIS da execução; não altera dados nem resultados).

Uso (na raiz do repositório):
  python analises/conferencia_relatos.py sortear   # sorteia 50 dos 198 relatos e gera as duas fichas
  python analises/conferencia_relatos.py exemplos  # sorteia 1 relato por tipo RIASEC para o apêndice
  python analises/conferencia_relatos.py kappa     # lê as duas fichas preenchidas e calcula aceite e Kappa

Sementes desta análise (registradas aqui porque o config.yaml está travado desde o lock-v1):
  SEED_AMOSTRA  = 20261123  -> amostra de 50 relatos
  SEED_EXEMPLOS = 20261124  -> 1 relato por tipo RIASEC (apêndice)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "data" / "generated"
OUT = ROOT / "analises" / "conferencia"
SEED_AMOSTRA, SEED_EXEMPLOS, N = 20261123, 20261124, 50
LETTERS = ["R", "I", "A", "S", "E", "C"]
PERGUNTAS = {
    "leigo": "Parece relato escrito por uma pessoa leiga, em linguagem cotidiana?",
    "adivinha": "Dá para adivinhar a ocupação específica a partir do relato?",
}


def relatos_eval() -> pd.DataFrame:
    rows = [json.loads(l) for l in (GEN / "relatos.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rel = pd.DataFrame([r for r in rows if r["set"] == "eval"])[["profile_id", "code", "relato"]]
    prof = pd.read_csv(GEN / "profiles_eval.csv", dtype=str)
    df = prof.merge(rel, on=["profile_id", "code"], how="left", validate="one_to_one")
    assert len(df) == 198 and df["relato"].notna().all(), "esperados 198 relatos da avaliação"
    return df.sort_values("profile_id").reset_index(drop=True)


def sortear() -> None:
    df = relatos_eval()
    rng = np.random.default_rng(SEED_AMOSTRA)
    idx = rng.choice(len(df), size=N, replace=False)          # ordem sorteada = ordem de apresentação
    amostra = df.iloc[idx].reset_index(drop=True)
    amostra.insert(0, "item", [f"R{i:02d}" for i in range(1, N + 1)])
    OUT.mkdir(parents=True, exist_ok=True)
    amostra[["item", "profile_id", "type", "code"]].to_csv(OUT / "amostra_50.csv", index=False, lineterminator="\n", encoding="utf-8")
    for avaliador in ("avaliador1", "avaliador2"):
        ficha = amostra[["item", "relato"]].copy()
        ficha["leigo (Sim/Não)"] = ""
        ficha["adivinha (Sim/Não)"] = ""
        ficha["palpite de ocupação (opcional)"] = ""
        ficha.to_csv(OUT / f"ficha_{avaliador}.csv", index=False, lineterminator="\n", encoding="utf-8")
    print(f"amostra: {N} de {len(df)} (semente {SEED_AMOSTRA}); tipos:",
          amostra["type"].value_counts().reindex(LETTERS, fill_value=0).to_dict())


def exemplos() -> None:
    df = relatos_eval()
    rng = np.random.default_rng(SEED_EXEMPLOS)
    rows = []
    for t in LETTERS:
        g = df[df["type"] == t].reset_index(drop=True)
        rows.append(g.iloc[int(rng.integers(len(g)))])
    ex = pd.DataFrame(rows)[["type", "profile_id", "code", "relato"]]
    OUT.mkdir(parents=True, exist_ok=True)
    ex.to_csv(OUT / "exemplos_por_tipo.csv", index=False, lineterminator="\n", encoding="utf-8")
    print(ex.to_string(index=False))


def _sim(col: pd.Series) -> pd.Series:
    v = col.astype(str).str.strip().str.lower().str.replace("ã", "a")
    bad = ~v.isin(["sim", "nao"])
    if bad.any():
        raise SystemExit(f"respostas fora de Sim/Não nos itens: {list(col[bad].index)}")
    return v == "sim"


def _ficha(nome: str) -> pd.DataFrame:
    """Lê a ficha preenchida (.xlsx, aba "Ficha", ou .csv) de um avaliador."""
    xlsx, csv = OUT / f"ficha_{nome}_preenchida.xlsx", OUT / f"ficha_{nome}_preenchida.csv"
    df = pd.read_excel(xlsx, sheet_name="Ficha", dtype=str) if xlsx.exists() else pd.read_csv(csv, dtype=str)
    return df.fillna("").set_index("item")


def cohen_kappa(a: pd.Series, b: pd.Series) -> float:
    a, b = a.astype(bool).to_numpy(), b.astype(bool).to_numpy()
    po = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def kappa() -> None:
    f1, f2 = (_ficha(n) for n in ("avaliador1", "avaliador2"))
    assert list(f1.index) == list(f2.index) and len(f1) == N
    linhas = []
    for chave, col in (("leigo", "leigo (Sim/Não)"), ("adivinha", "adivinha (Sim/Não)")):
        a, b = _sim(f1[col]), _sim(f2[col])
        linhas.append({"pergunta": PERGUNTAS[chave], "sim_avaliador1": f"{a.mean():.1%}",
                       "sim_avaliador2": f"{b.mean():.1%}", "sim_nos_dois": f"{(a & b).mean():.1%}",
                       "concordancia": f"{(a == b).mean():.1%}", "kappa": round(cohen_kappa(a, b), 3)})
    # Aceite = parece relato de leigo E não permite adivinhar a ocupação, na opinião do avaliador.
    ac1 = _sim(f1["leigo (Sim/Não)"]) & ~_sim(f1["adivinha (Sim/Não)"])
    ac2 = _sim(f2["leigo (Sim/Não)"]) & ~_sim(f2["adivinha (Sim/Não)"])
    linhas.append({"pergunta": "Aceite (leigo = Sim e adivinha = Não)", "sim_avaliador1": f"{ac1.mean():.1%}",
                   "sim_avaliador2": f"{ac2.mean():.1%}", "sim_nos_dois": f"{(ac1 & ac2).mean():.1%}",
                   "concordancia": f"{(ac1 == ac2).mean():.1%}", "kappa": round(cohen_kappa(ac1, ac2), 3)})
    res = pd.DataFrame(linhas)
    res.to_csv(OUT / "resultado_conferencia.csv", index=False, lineterminator="\n", encoding="utf-8")
    print(res.to_string(index=False))


if __name__ == "__main__":
    {"sortear": sortear, "exemplos": exemplos, "kappa": kappa}[sys.argv[1]]()
