"""Checks the API keys and that both protocol models answer as themselves (Seção 17).

Usage: python -m tcc.check   (two tiny calls; cost of a fraction of a cent)
"""
from __future__ import annotations

from . import llm
from .common import config


def main() -> None:
    cfg = config()
    for model in sorted({cfg[k]["model"] for k in ("relato", "synthesis", "rerank")}):
        c = llm.call("Reply with the single word: ok", model, 50, "check")
        print(f"OK — pedido {model}, devolvido {c.model_returned}, "
              f"tokens entrada/saída/raciocínio {c.input_tokens}/{c.output_tokens}/{c.thinking_tokens}")
    for model, price in cfg["prices"].items():
        if price["input"] is None or price["output"] is None or price["date"] is None:
            print(f"ATENÇÃO: preço de {model} ainda não registrado em config.yaml ({price['url']}).")


if __name__ == "__main__":
    main()
