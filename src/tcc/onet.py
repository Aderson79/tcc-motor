"""Reading of the O*NET CSV files."""
from __future__ import annotations

import pandas as pd

from .common import ROOT, config

EXPECTED = {
    "occupation_data.csv": ["O*NET-SOC Code", "Title", "Description"],
    "task_statements.csv": ["O*NET-SOC Code", "Task", "Task Type"],
    "career_interest_types.csv": ["O*NET-SOC Code", "Element Name", "Scale ID", "Data Value"],
    "related_occupations.csv": ["O*NET-SOC Code", "Related O*NET-SOC Code", "Relatedness Tier", "Index"],
}


def read(name: str) -> pd.DataFrame:
    path = ROOT / config()["onet"]["dir"] / name
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [c for c in EXPECTED[name] if c not in df.columns]
    if missing:
        raise SystemExit(f"PARE (Seção 17): {name} sem as colunas esperadas {missing}; colunas = {list(df.columns)}")
    return df
