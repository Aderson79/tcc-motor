"""Metrics over a ranked list of five codes (Etapa 9)."""
from __future__ import annotations

from math import log2

K = 5


def rels(ranking: list[str], gold: dict[str, int]) -> list[int]:
    assert len(ranking) == K, "a lista avaliada sempre tem 5 posições"
    return [gold.get(code, 0) for code in ranking]


def n_related(gold: dict[str, int]) -> int:
    return sum(1 for r in gold.values() if r == 1)


def dcg(values: list[int]) -> float:
    return sum(r / log2(i + 1) for i, r in enumerate(values, start=1))  # linear gain


def ndcg(ranking: list[str], gold: dict[str, int]) -> float:
    ideal = ([2] + [1] * n_related(gold) + [0] * K)[:K]
    return dcg(rels(ranking, gold)) / dcg(ideal)


def precision(ranking: list[str], gold: dict[str, int]) -> float:
    return sum(r >= 1 for r in rels(ranking, gold)) / K


def average_precision(ranking: list[str], gold: dict[str, int]) -> float:
    hits, total = 0, 0.0
    for i, r in enumerate(rels(ranking, gold), start=1):
        if r >= 1:
            hits += 1
            total += hits / i
    return total / min(K, 1 + n_related(gold))


def mrr_origin(ranking: list[str], gold: dict[str, int]) -> float:
    for i, r in enumerate(rels(ranking, gold), start=1):
        if r == 2:
            return 1 / i
    return 0.0


METRICS = {"ndcg5": ndcg, "p5": precision, "ap5": average_precision, "mrr5_origem": mrr_origin}


def all_metrics(ranking: list[str], gold: dict[str, int]) -> dict[str, float]:
    return {name: fn(ranking, gold) for name, fn in METRICS.items()}
