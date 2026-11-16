"""Anthropic and Gemini clients with per-call logging (logs/calls.jsonl)."""
from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache

from dotenv import load_dotenv

from .common import LOGS, ROOT, append_jsonl, config

load_dotenv(ROOT / ".env")
_lock = threading.Lock()


class ModelMismatch(SystemExit):
    """The API answered with a model other than the one fixed in the protocol (Seção 17)."""


@dataclass
class Call:
    text: str
    model_returned: str
    latency_s: float
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    stop_reason: str
    transport_retries: int


def _key(name: str) -> str:
    # TCC_* é aceito como alternativa para ambientes em que o nome padrão é reservado.
    value = os.getenv(name) or os.getenv(f"TCC_{name}")
    if not value:
        raise SystemExit(f"Defina {name} no arquivo .env (veja .env.example).")
    return value


def _log(provider: str, purpose: str, meta: dict, model: str, call: Call | None, error: str | None) -> None:
    record = {"ts": datetime.now(timezone.utc).isoformat(), "provider": provider, "purpose": purpose,
              "model_requested": model, **meta, "error": error}
    if call:
        record.update({k: v for k, v in asdict(call).items() if k != "text"})
    with _lock:
        append_jsonl(LOGS / "calls.jsonl", record)


def _with_retry(provider: str, purpose: str, meta: dict, model: str, once, is_transport) -> Call:
    cfg = config()["transport_retry"]
    for attempt in range(cfg["max_attempts"]):
        try:
            call = once()
        except Exception as exc:  # classified below; non-transport errors are re-raised
            _log(provider, purpose, {**meta, "transport_attempt": attempt + 1}, model, None, repr(exc)[:500])
            if not is_transport(exc) or attempt + 1 == cfg["max_attempts"]:
                raise
            delay = min(cfg["max_delay_s"], cfg["base_delay_s"] * 2 ** attempt)
            time.sleep(delay * (0.5 + random.random() / 2))
            continue
        call.transport_retries = attempt
        _log(provider, purpose, {**meta, "transport_attempt": attempt + 1}, model, call, None)
        if not call.model_returned.startswith(model):
            raise ModelMismatch(f"PARE (Seção 17): pedido {model}, a API respondeu com {call.model_returned}.")
        return call
    raise AssertionError("unreachable")


@lru_cache(maxsize=1)
def _anthropic():
    import anthropic
    # max_retries=0: as novas tentativas são feitas aqui, para medir a latência de cada chamada.
    return anthropic.Anthropic(api_key=_key("ANTHROPIC_API_KEY"), max_retries=0, timeout=120.0)


def claude(prompt: str, model: str, max_tokens: int, purpose: str, **meta) -> Call:
    import anthropic

    def once() -> Call:
        start = time.perf_counter()
        # Sem temperatura/top_p/top_k, sem cache_control, sem Batch API.
        msg = _anthropic().messages.create(
            model=model, max_tokens=max_tokens,
            thinking={"type": config()["anthropic"]["thinking"]},
            messages=[{"role": "user", "content": prompt}])
        latency = time.perf_counter() - start
        text = "".join(b.text for b in msg.content if b.type == "text")
        return Call(text=text, model_returned=msg.model, latency_s=latency,
                    input_tokens=msg.usage.input_tokens, output_tokens=msg.usage.output_tokens,
                    thinking_tokens=0, stop_reason=str(msg.stop_reason), transport_retries=0)

    def is_transport(exc: Exception) -> bool:
        if isinstance(exc, (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError)):
            return True
        return isinstance(exc, anthropic.APIStatusError) and exc.status_code >= 500

    return _with_retry("anthropic", purpose, meta, model, once, is_transport)


@lru_cache(maxsize=1)
def _gemini():
    from google import genai
    return genai.Client(api_key=_key("GEMINI_API_KEY"))


def gemini(prompt: str, model: str, purpose: str, **meta) -> Call:
    from google.genai import errors

    def once() -> Call:
        start = time.perf_counter()
        # Configuração padrão: sem temperatura, sem amostragem, sem orçamento de raciocínio.
        resp = _gemini().models.generate_content(model=model, contents=prompt)
        latency = time.perf_counter() - start
        usage = resp.usage_metadata
        finish = resp.candidates[0].finish_reason if resp.candidates else None
        return Call(text=resp.text or "", model_returned=resp.model_version or "", latency_s=latency,
                    input_tokens=usage.prompt_token_count or 0, output_tokens=usage.candidates_token_count or 0,
                    thinking_tokens=usage.thoughts_token_count or 0, stop_reason=str(finish), transport_retries=0)

    def is_transport(exc: Exception) -> bool:
        if isinstance(exc, errors.APIError):
            return exc.code == 429 or (exc.code or 0) >= 500
        # erros de rede de qualquer cliente HTTP (conexão, timeout, protocolo)
        names = {c.__name__ for c in type(exc).__mro__}
        return isinstance(exc, OSError) or bool(names & {"TransportError", "RequestError", "ClientError"} - {"APIError"})

    return _with_retry("gemini", purpose, meta, model, once, is_transport)


def cost(model: str, input_tokens: float, output_tokens: float) -> float:
    """USD at the prices fixed in config.yaml (thinking tokens count as output)."""
    price = config()["prices"][model]
    if price["input"] is None or price["output"] is None:
        raise SystemExit(f"Preço de {model} não registrado em config.yaml.")
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1e6
