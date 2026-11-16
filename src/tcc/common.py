"""Shared configuration, paths and small helpers."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "data" / "generated"
RESULTS = ROOT / "results"
LOGS = ROOT / "logs"
PROMPTS = ROOT / "prompts"

TYPES = ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"]
LETTERS = ["R", "I", "A", "S", "E", "C"]

# condition name -> which profile set it belongs to
SET_CONDITIONS = {"dev": ["dev"], "eval": ["main", "sens"]}
ID_PREFIX = {"dev": ("D", 2), "eval": ("P", 3)}


@lru_cache(maxsize=1)
def config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8").rstrip("\n")


def profile_id(set_name: str, i: int) -> str:
    prefix, width = ID_PREFIX[set_name]
    return f"{prefix}{i:0{width}d}"


def content_words(text: str) -> list[str]:
    """Alphabetic lowercase tokens with 3+ letters that are not stopwords."""
    return [t for t in re.findall(r"[a-z]+", text.lower())
            if len(t) >= 3 and t not in ENGLISH_STOP_WORDS]


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
