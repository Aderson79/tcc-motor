"""B1 - BM25 over the indexed text; query = self-description."""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from ..common import config


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in ENGLISH_STOP_WORDS]


class B1:
    def __init__(self, codes: list[str], texts: list[str]):
        cfg = config()["bm25"]
        self.codes = codes
        self.bm25 = BM25Okapi([tokenize(t) for t in texts], k1=cfg["k1"], b=cfg["b"])

    def rank(self, relato: str, k: int) -> list[str]:
        scores = self.bm25.get_scores(tokenize(relato))
        order = sorted(range(len(self.codes)), key=lambda i: (-scores[i], self.codes[i]))
        return [self.codes[i] for i in order[:k]]
