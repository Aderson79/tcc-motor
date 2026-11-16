"""V-B - profile synthesis by the LLM + retrieval of 20 candidates."""
from __future__ import annotations

from .. import llm
from ..common import LETTERS, config, prompt


def synthesis_prompt(scores: list[float], relato: str) -> str:
    text = prompt("C_sintese.txt")
    for letter, score in zip(LETTERS, scores):
        text = text.replace(f"{{{letter}}}", f"{score:.1f}")
    return text.replace("{self_description}", relato)


def synthesize(scores: list[float], relato: str, **meta) -> llm.Call:
    cfg = config()["synthesis"]
    return llm.claude(synthesis_prompt(scores, relato), cfg["model"], cfg["max_tokens"], "sintese", **meta)
