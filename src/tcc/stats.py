"""Descriptive statistics and the four pre-registered Wilcoxon comparisons (Etapa 10)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from .common import config

COMPARISONS = [("(a) H1", "V-B", "V-A"), ("(b) H2", "V-C", "V-B"), ("(c) H3", "V-C", "B1"), ("(d) H4", "V-C", "B2")]


def compare(elaborate: np.ndarray, simple: np.ndarray, n_tests: int = 4) -> dict:
    cfg = config()["stats"]
    d = np.asarray(elaborate) - np.asarray(simple)
    nonzero = int((d != 0).sum())
    if nonzero:
        res = wilcoxon(elaborate, simple, alternative="two-sided", zero_method="wilcox")
        w, p = float(res.statistic), float(res.pvalue)
    else:
        w, p = float("nan"), float("nan")
    favors = bool(d.mean() >= cfg["min_mean_diff"] and p < cfg["alpha_bonferroni"])
    decision = "favorece o sistema mais elaborado" if favors else "não favorece"
    if not favors and d.mean() < 0 and p < cfg["alpha_bonferroni"]:
        decision += " (diferença negativa e significativa)"
    return {"media_d": float(d.mean()), "mediana_d": float(np.median(d)), "n": int(len(d)),
            "n_nao_nulos": nonzero, "W": w, "p_bruto": p,
            "p_bonferroni": min(1.0, n_tests * p) if nonzero else float("nan"), "decisao": decision}


def comparisons(per_profile: pd.DataFrame, condition: str = "main") -> pd.DataFrame:
    """per_profile: system, condition, profile_id, ndcg5, ... (V-C already averaged over runs)."""
    wide = per_profile[per_profile["condition"] == condition].pivot(
        index="profile_id", columns="system", values="ndcg5").sort_index()
    rows = []
    for label, elaborate, simple in COMPARISONS:
        rows.append({"comparacao": label, "d": f"{elaborate} − {simple}",
                     **compare(wide[elaborate].to_numpy(), wide[simple].to_numpy(), len(COMPARISONS))})
    return pd.DataFrame(rows)


def descriptives(per_profile: pd.DataFrame, metric_names: list[str]) -> pd.DataFrame:
    rows = []
    for (system, condition), g in per_profile.groupby(["system", "condition"], sort=False):
        for m in metric_names:
            rows.append({"system": system, "condition": condition, "metric": m, "media": g[m].mean(),
                         "dp": g[m].std(ddof=1), "mediana": g[m].median(), "n": len(g)})
    return pd.DataFrame(rows)
