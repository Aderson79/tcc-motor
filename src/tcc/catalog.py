"""Eligibility filter, indexed text and predominant RIASEC type (Etapa 1)."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from . import onet
from .common import LETTERS, RESULTS, TYPES


@dataclass(frozen=True)
class Catalog:
    df: pd.DataFrame              # index = code; columns: title, description, R..C, type
    tasks: dict[str, list[str]]   # code -> task statements in file order
    related: pd.DataFrame         # related_occupations rows
    summary: dict

    @property
    def codes(self) -> list[str]:
        return list(self.df.index)

    def indexed_text(self, code: str) -> str:
        row = self.df.loc[code]
        return " ".join([f"{row.title}. {row.description}"] + self.tasks[code])

    def scores(self, code: str) -> list[float]:
        return [float(self.df.at[code, l]) for l in LETTERS]


def predominant(scores: list[float]) -> str:
    """Letter of the highest score; ties broken by the order R, I, A, S, E, C."""
    return LETTERS[max(range(6), key=lambda i: (scores[i], -i))]


@lru_cache(maxsize=1)
def load() -> Catalog:
    occ = onet.read("occupation_data.csv")
    tasks_df = onet.read("task_statements.csv")
    cit = onet.read("career_interest_types.csv")
    rel = onet.read("related_occupations.csv")

    oi = cit[(cit["Scale ID"] == "OI") & (cit["Element Name"].isin(TYPES))].copy()
    oi["Data Value"] = oi["Data Value"].astype(float)
    if oi.empty or oi["Data Value"].min() < 1 or oi["Data Value"].max() > 7:
        raise SystemExit("PARE (Seção 17): notas OI fora do intervalo [1, 7] ou ausentes.")
    wide = oi.pivot_table(index="O*NET-SOC Code", columns="Element Name", values="Data Value", aggfunc="first")
    wide = wide.reindex(columns=TYPES).dropna()
    wide.columns = LETTERS

    tasks_df = tasks_df[tasks_df["Task"].str.strip() != ""]
    tasks: dict[str, list[str]] = {}
    for code, task in zip(tasks_df["O*NET-SOC Code"], tasks_df["Task"]):
        tasks.setdefault(code, []).append(task.strip())
    with_related = set(rel["O*NET-SOC Code"])

    occ = occ.rename(columns={"O*NET-SOC Code": "code", "Title": "title", "Description": "description"})
    occ = occ.set_index("code")[["title", "description"]]
    has_desc = occ["description"].str.strip() != ""
    has_task = occ.index.isin(tasks)
    has_oi = occ.index.isin(wide.index)
    has_rel = occ.index.isin(with_related)
    eligible = has_desc & has_task & has_oi & has_rel

    df = occ[eligible].join(wide).sort_index()
    df["type"] = [predominant([r[l] for l in LETTERS]) for _, r in df.iterrows()]
    by_type = df["type"].value_counts()
    summary = {
        "occupation_data_rows": int(len(occ)),
        "excluded_no_description": int((~has_desc).sum()),
        "excluded_no_tasks": int((~has_task).sum()),
        "excluded_no_full_riasec": int((~has_oi).sum()),
        "excluded_no_related": int((~has_rel).sum()),
        "catalog_size": int(len(df)),
        **{f"eligible_{l}": int(by_type.get(l, 0)) for l in LETTERS},
    }
    return Catalog(df=df, tasks={c: tasks[c] for c in df.index}, related=rel, summary=summary)


def main() -> None:
    cat = load()
    RESULTS.mkdir(exist_ok=True)
    pd.DataFrame([{"item": k, "value": v} for k, v in cat.summary.items()]).to_csv(
        RESULTS / "catalog_summary.csv", index=False)
    for k, v in cat.summary.items():
        print(f"{k}: {v}")
    short = [l for l in LETTERS if cat.summary[f"eligible_{l}"] < 38]
    if short:
        print(f"AVISO (Seção 17): tipos com menos de 38 elegíveis: {short}")


if __name__ == "__main__":
    main()
