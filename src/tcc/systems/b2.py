"""B2 - Pearson correlation between the profile scores and each occupation's OI scores."""
from __future__ import annotations

import numpy as np


class B2:
    def __init__(self, codes: list[str], matrix: np.ndarray):
        self.codes = codes
        self.centered = matrix - matrix.mean(axis=1, keepdims=True)
        self.norms = np.linalg.norm(self.centered, axis=1)
        self.zero_variance = int((self.norms == 0).sum())  # Pearson undefined -> treated as -1

    def correlations(self, scores: np.ndarray) -> np.ndarray:
        x = np.asarray(scores, dtype=float)
        x = x - x.mean()
        nx = np.linalg.norm(x)
        with np.errstate(divide="ignore", invalid="ignore"):
            r = (self.centered @ x) / (self.norms * nx)
        return np.where(np.isfinite(r), r, -1.0)

    def rank(self, scores: np.ndarray, k: int) -> list[str]:
        r = self.correlations(scores)
        order = sorted(range(len(self.codes)), key=lambda i: (-r[i], self.codes[i]))
        return [self.codes[i] for i in order[:k]]
