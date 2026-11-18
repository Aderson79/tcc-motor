"""Tamanho de efeito e intervalo de confiança das quatro comparações (complemento da Tabela 2).

Análise feita DEPOIS de results-v1: lê results/per_profile_metrics.csv e não altera nenhum resultado.
O teste de Wilcoxon e a decisão continuam os do protocolo (src/tcc/stats.py); aqui só se acrescentam:
  - IC da média de d (t pareado), a 95% e a 98,75% (nível ajustado por Bonferroni para 4 comparações);
  - IC de bootstrap percentil da média de d (10.000 reamostragens, semente 20261125), para conferência;
  - correlação bisserial de postos pareada (r_rb), tamanho de efeito associado ao Wilcoxon:
    (soma dos postos positivos − soma dos negativos) / soma total dos postos, sem as diferenças nulas;
  - d_z de Cohen (média de d / desvio padrão de d).

Uso: python analises/efeito_ic.py   ->   analises/efeito_ic.txt e analises/efeito_ic.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
COMP = [("(a) H1", "V-B", "V-A"), ("(b) H2", "V-C", "V-B"), ("(c) H3", "V-C", "B1"), ("(d) H4", "V-C", "B2")]
SEED, B, ALPHA, LIMIAR = 20261125, 10_000, 0.05, 0.05


def rank_biserial(d: np.ndarray) -> float:
    # Diferenças que deveriam empatar mas diferem só no último bit do ponto flutuante passam a empatar
    # em qualquer máquina (sem isso, 16 pares de |d| recebiam postos diferentes conforme o ambiente).
    d = np.round(d, 12)
    nz = d[d != 0]
    r = stats.rankdata(np.abs(nz))
    return float((r[nz > 0].sum() - r[nz < 0].sum()) / r.sum())


def main() -> None:
    pp = pd.read_csv(ROOT / "results" / "per_profile_metrics.csv")
    rows = []
    for cond in ("main", "sens"):
        w = pp[pp.condition == cond].pivot(index="profile_id", columns="system", values="ndcg5").sort_index()
        rng = np.random.default_rng(SEED)
        for label, a, b in COMP:
            d = (w[a] - w[b]).to_numpy()
            n, m, se = len(d), d.mean(), d.std(ddof=1) / np.sqrt(len(d))
            t95, tbf = stats.t.ppf(1 - ALPHA / 2, n - 1), stats.t.ppf(1 - ALPHA / 8, n - 1)
            boot = np.array([d[rng.integers(0, n, n)].mean() for _ in range(B)])
            rows.append({"condicao": cond, "comparacao": label, "d": f"{a} − {b}", "n": n, "media_d": m,
                         "ic95_inf": m - t95 * se, "ic95_sup": m + t95 * se,
                         "ic9875_inf": m - tbf * se, "ic9875_sup": m + tbf * se,
                         "boot95_inf": np.percentile(boot, 2.5), "boot95_sup": np.percentile(boot, 97.5),
                         "r_rb": rank_biserial(d), "dz": m / d.std(ddof=1)})
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "analises" / "efeito_ic.csv", index=False, lineterminator="\n", encoding="utf-8")
    lines = ["Tamanho de efeito e IC da média de d (nDCG@5)"]
    for r in df.itertuples():
        lines.append(f"{r.condicao:4s} {r.comparacao} {r.d:9s} média {r.media_d:+.3f} | IC95% [{r.ic95_inf:+.3f}; "
                     f"{r.ic95_sup:+.3f}] | IC98,75% [{r.ic9875_inf:+.3f}; {r.ic9875_sup:+.3f}] | bootstrap95% "
                     f"[{r.boot95_inf:+.3f}; {r.boot95_sup:+.3f}] | r_rb {r.r_rb:+.3f} | d_z {r.dz:+.3f}")
    h1 = df[(df.condicao == "main") & (df.comparacao == "(a) H1")].iloc[0]
    lines.append(f"H1: limite superior do IC95% = {h1.ic95_sup:+.4f}; do IC98,75% = {h1.ic9875_sup:+.4f}; "
                 f"ambos abaixo do limiar de {LIMIAR}.")
    (ROOT / "analises" / "efeito_ic.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
