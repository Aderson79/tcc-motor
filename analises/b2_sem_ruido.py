"""B2 com as notas exatas da ocupação de origem, sem ruído (teto descritivo do casamento pelo RIASEC).

Análise feita DEPOIS de results-v1, não prevista no protocolo. Não chama nenhum modelo de linguagem,
não usa o banco vetorial e não altera dados nem resultados: lê o catálogo O*NET 31.0, os perfis e o
gabarito da avaliação e roda o mesmo B2 de src/tcc/systems/b2.py com as notas OI publicadas da origem.

Uso (na raiz do repositório, com o O*NET 31.0 em data/raw/db_31_0_csv):
  python analises/b2_sem_ruido.py
Saída: analises/b2_sem_ruido.txt (resumo) e analises/b2_sem_ruido.csv (métricas por perfil).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc import catalog, gold, metrics  # noqa: E402
from tcc.common import GEN, LETTERS  # noqa: E402
from tcc.systems.b2 import B2  # noqa: E402


def main() -> None:
    cat = catalog.load()
    assert len(cat.codes) == 923, f"catálogo com {len(cat.codes)} ocupações (esperado 923)"
    b2 = B2(cat.codes, cat.df[LETTERS].to_numpy(dtype=float))
    profiles = pd.read_csv(GEN / "profiles_eval.csv", dtype=str)
    gabarito = gold.load("eval")
    k = 5

    # Conferência: com as notas com ruído salvas, este script reproduz o B2 publicado (σ = 1,0 e 0,5).
    pub = pd.read_csv(ROOT / "results" / "per_profile_metrics.csv")
    for cond in ("main", "sens"):
        sc = pd.read_csv(GEN / f"scores_{cond}.csv", dtype={"profile_id": str}).set_index("profile_id")
        got = np.mean([metrics.ndcg(b2.rank(sc.loc[p, LETTERS].to_numpy(float), k), gabarito[p])
                       for p in profiles["profile_id"]])
        ref = pub[(pub.system == "B2") & (pub.condition == cond)]["ndcg5"].mean()
        assert abs(got - ref) < 1e-9, f"B2 {cond} não reproduz o publicado: {got} != {ref}"

    rows = []
    for pid, origin in zip(profiles["profile_id"], profiles["code"]):
        exact = np.array(cat.scores(origin), dtype=float)
        ranking = b2.rank(exact, k)
        r = b2.correlations(exact)
        ties = int((np.isclose(r, 1.0)).sum()) - 1        # outras ocupações com o mesmo formato de perfil
        rows.append({"profile_id": pid, "origem_em": (ranking.index(origin) + 1) if origin in ranking else 0,
                     "empates_r1": ties, **metrics.all_metrics(ranking, gabarito[pid])})
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "analises" / "b2_sem_ruido.csv", index=False, lineterminator="\n", encoding="utf-8")

    lines = [
        "B2 sem ruído (notas OI exatas da ocupação de origem), 198 perfis da avaliação",
        f"nDCG@5 média {df.ndcg5.mean():.3f} (DP {df.ndcg5.std(ddof=1):.3f}; mediana {df.ndcg5.median():.3f})",
        f"P@5 {df.p5.mean():.3f} · MAP@5 {df.ap5.mean():.3f} · MRR@5 de origem {df.mrr5_origem.mean():.3f}",
        f"origem na 1ª posição: {(df.origem_em == 1).sum()} perfis; fora das 5 primeiras: {(df.origem_em == 0).sum()}",
        f"perfis em que outra ocupação tem correlação 1 com a origem: {(df.empates_r1 > 0).sum()}",
        f"perfis sem nenhuma ocupação relevante nas 5: {(df.ndcg5 == 0).sum()}",
        "Conferência: o mesmo código reproduz o nDCG@5 publicado de B2 com σ = 1,0 e σ = 0,5.",
    ]
    (ROOT / "analises" / "b2_sem_ruido.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
