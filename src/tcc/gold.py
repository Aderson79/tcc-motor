"""Gold standard (Etapa 5): origin = 2, Primary-Short related in the catalog = 1."""
from __future__ import annotations

import sys

import pandas as pd

from . import catalog
from .common import GEN


def build(origins: dict[str, str], related: pd.DataFrame, catalog_codes: set[str]) -> pd.DataFrame:
    short = related[related["Relatedness Tier"] == "Primary-Short"]
    by_code = short.groupby("O*NET-SOC Code")["Related O*NET-SOC Code"].apply(list).to_dict()
    rows = []
    for pid, origin in origins.items():
        rows.append({"profile_id": pid, "code": origin, "rel": 2})
        for code in by_code.get(origin, []):
            if code in catalog_codes and code != origin:
                rows.append({"profile_id": pid, "code": code, "rel": 1})
    return pd.DataFrame(rows)


def gold_path(set_name: str):
    return GEN / ("gold.csv" if set_name == "eval" else "gold_dev.csv")


def load(set_name: str) -> dict[str, dict[str, int]]:
    df = pd.read_csv(gold_path(set_name), dtype={"profile_id": str, "code": str})
    return {pid: dict(zip(g["code"], g["rel"])) for pid, g in df.groupby("profile_id")}


def main() -> None:
    set_name = sys.argv[1]
    cat = catalog.load()
    profiles = pd.read_csv(GEN / f"profiles_{set_name}.csv", dtype=str)
    df = build(dict(zip(profiles["profile_id"], profiles["code"])), cat.related, set(cat.codes))
    df.to_csv(gold_path(set_name), index=False)
    n_rel = df[df["rel"] == 1].groupby("profile_id").size().reindex(profiles["profile_id"], fill_value=0)
    print(f"gabarito {set_name}: relacionadas por perfil média {n_rel.mean():.3f}, mín {n_rel.min()}, "
          f"máx {n_rel.max()}; perfis com < 5: {(n_rel < 5).sum()}")


if __name__ == "__main__":
    main()
