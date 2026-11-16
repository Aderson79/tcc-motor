"""V-C - the LLM selects and ranks five of the 20 candidates of V-B."""
from __future__ import annotations

import re

from .. import llm
from ..common import config, prompt


def rerank_prompt(profile_text: str, candidates: list[tuple[str, str]]) -> str:
    """candidates: [(title, description)] in the order of V-B; numbered from 1."""
    head = prompt("D_reordenacao.txt").split("1. {title_1}")[0].replace("{profile_text}", profile_text)
    return head + "\n".join(f"{i}. {t}: {d}" for i, (t, d) in enumerate(candidates, start=1))


def parse(text: str, n_candidates: int = 20) -> list[int] | None:
    """Valid iff exactly five distinct integers between 1 and n_candidates."""
    numbers = [int(x) for x in re.findall(r"\d+", text)]
    if len(numbers) == 5 and len(set(numbers)) == 5 and all(1 <= n <= n_candidates for n in numbers):
        return numbers
    return None


def rerank(profile_text: str, candidates: list[tuple[str, str]], candidate_codes: list[str], **meta) -> dict:
    """One run: at most one format resend; falls back to V-B's top five."""
    cfg = config()["rerank"]
    text = rerank_prompt(profile_text, candidates)
    calls, picks = [], None
    for send in (1, 2):
        call = llm.claude(text, cfg["model"], cfg["max_tokens"], "reordenacao", send=send, **meta)
        calls.append(call)
        picks = parse(call.text, len(candidates))
        if picks:
            break
    return {
        "codes": [candidate_codes[n - 1] for n in picks] if picks else candidate_codes[:5],
        "picks": picks, "fallback": picks is None, "resent": len(calls) == 2,
        "responses": [c.text for c in calls],
        "latency_s": sum(c.latency_s for c in calls),
        "input_tokens": sum(c.input_tokens for c in calls),
        "output_tokens": sum(c.output_tokens for c in calls),
        "model_returned": calls[-1].model_returned,
    }
