"""Checks the API keys and that both protocol models answer as themselves (Seção 17).

Usage: python -m tcc.check   (two tiny calls; cost of a fraction of a cent)
"""
from __future__ import annotations

from . import llm
from .common import config


def main() -> None:
    cfg = config()
    g = llm.gemini("Reply with the single word: ok", cfg["relato"]["model"], "check")
    print(f"Gemini  OK — pedido {cfg['relato']['model']}, devolvido {g.model_returned}, "
          f"tokens entrada/saída/raciocínio {g.input_tokens}/{g.output_tokens}/{g.thinking_tokens}")
    c = llm.claude("Reply with the single word: ok", cfg["synthesis"]["model"], 50, "check")
    print(f"Sonnet  OK — pedido {cfg['synthesis']['model']}, devolvido {c.model_returned}, "
          f"tokens entrada/saída {c.input_tokens}/{c.output_tokens}")
    for model, price in cfg["prices"].items():
        if price["input"] is None or price["output"] is None or price["date"] is None:
            print(f"ATENÇÃO: preço de {model} ainda não registrado em config.yaml ({price['url']}).")


if __name__ == "__main__":
    main()
