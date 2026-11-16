"""V-A - fixed template (scores in words) + self-description, no LLM."""
from __future__ import annotations

from ..common import TYPES, prompt


def level(score: float) -> str:
    return "high" if score >= 5 else "moderate" if score >= 3 else "low"


def fill_template(scores: list[float], relato: str) -> str:
    order = sorted(range(6), key=lambda i: (-scores[i], i))  # ties: R, I, A, S, E, C
    text = prompt("B_molde_va.txt")
    for pos, i in enumerate(order, start=1):
        text = text.replace(f"{{type_{pos}}}", TYPES[i]).replace(f"{{level_{pos}}}", level(scores[i]))
    return text.replace("{self_description}", relato)
