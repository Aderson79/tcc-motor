# tcc-motor

Motor e experimento do TCC *Síntese do perfil e reordenação por LLM na recomendação de ocupações a partir de
interesses RIASEC: avaliação comparativa com perfis sintéticos sobre o catálogo O\*NET* (Aderson Jônatas Ribeiro
Mesquita, iCEV). Repositório independente; produz o pacote de resultados em `results/`.

## Estado atual
Pronto até o ponto em que faltam só as chaves de API: catálogo (923 ocupações), índice pgvector, sorteio do
conjunto de desenvolvimento e os 16 testes obrigatórios estão feitos. Nenhuma chamada a LLM foi feita ainda.

## Como reproduzir
1. `make setup` — Python 3.11+ e dependências.
2. `make data` — baixa o O\*NET 31.0 e confere o SHA-256.
3. `make db` — sobe o PostgreSQL com pgvector (Docker, porta 54329).
4. `make catalog index test` — catálogo, embeddings (busca exata, sem índice aproximado) e testes.
5. Copie `.env.example` para `.env` e preencha `ANTHROPIC_API_KEY` e `GEMINI_API_KEY`. O `.env` nunca vai para commit.
6. Confirme os preços em `config.yaml` (bloco `prices`) e preencha `models_access_date`.
7. `make check` — confere as chaves e se os dois modelos respondem como eles mesmos.
8. `make dev` — pipeline completo nos 30 perfis de desenvolvimento; saída em `results/dev/RESULTADOS_DEV.md`.
9. Ajuste (no máximo duas rodadas, só prompts A, C, D e molde B), registrado em `AJUSTES.md`.
   Para regerar um texto já salvo é preciso apagar o arquivo de propósito.
10. Travamento: `git commit` + `git tag lock-v1`.
11. `make eval` — sorteio da avaliação, relatos, gabarito, cinco sistemas nas duas condições e pacote em `results/`.
12. `git commit` + `git tag results-v1`.

## Etapas (todas idempotentes)
| Comando | O que faz |
|---|---|
| `python -m tcc.catalog` | filtro de elegibilidade, `results/catalog_summary.csv` |
| `python -m tcc.embed` | divisão em trechos, embeddings, carga no pgvector |
| `python -m tcc.sampling dev\|eval` | sorteio estratificado |
| `python -m tcc.profiles dev\|eval` | relatos (Gemini), filtro de título, substituições, notas com ruído |
| `python -m tcc.gold dev\|eval` | gabarito |
| `python -m tcc.run dev\|eval` | B1, B2, V-A, V-B, V-C; `rankings*.csv`, `timings*.csv` |
| `python -m tcc.report dev\|eval` | métricas, Wilcoxon, tempo, custo, `RESULTADOS*.md` |

Condições: `dev` (σ = 1,0, desenvolvimento), `main` (σ = 1,0, principal), `sens` (σ = 0,5, sensibilidade).
Toda chamada a LLM fica em `logs/calls.jsonl`. Desvios do protocolo ficam em `DESVIOS.md`.
