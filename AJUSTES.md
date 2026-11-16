# AJUSTES — log do ajuste no conjunto de desenvolvimento

No máximo duas rodadas. Só podem mudar os textos dos prompts A, C e D e o molde B.
Cada mudança registra: texto anterior, texto novo, motivo e métricas do desenvolvimento antes e depois.

## Rodada 0 (versões iniciais) — 16/11/2026
Prompts A, C, D e molde B iguais aos Apêndices A–D do TCC. Resultado nos 30 perfis de desenvolvimento
(σ = 1,0), guardado em `results/dev_rodada0/` e `data/generated/_ajuste_rodada0/`:

- **Relatos (prompt A):** 30 de 30 com 4 frases; 2 regerações pelo filtro de título; nenhuma substituição.
- **Sínteses (prompt C):** média de 117,7 palavras (108–129); **8 de 30 acima de 120 palavras**; nenhuma com
  dígitos ou com "RIASEC".
- **Reordenação (prompt D):** 300 execuções, **22 reenvios e 20 fallbacks (6,7%)**, acima do limite de 5% da
  Seção 17. Todos em três perfis (D01 e D02 nas 10 execuções, D12 em 2): o modelo começava a resposta com
  uma explicação ("Looking at this person's profile…") e o limite de 50 tokens cortava antes dos números.
- **nDCG@5 médio:** B1 0,087 · B2 0,190 · V-A 0,248 · V-B 0,234 · V-C 0,384.

## Rodada 1 — 16/11/2026
Mudaram os prompts C e D. O prompt A e o molde B não mudaram.

### Prompt C (síntese)
- **Motivo:** 8 de 30 sínteses passaram do limite de 120 palavras.
- **Texto anterior:** `Output only the paragraph.`
- **Texto novo:** `Output only the paragraph. Stay strictly within the word range: aim for about 100 words
  and never exceed 120 words.`

### Prompt D (reordenação)
- **Motivo:** respostas que começavam com explicação em vez dos cinco números (20 fallbacks em 300).
- **Texto anterior:** `(for example: 7, 2, 15, 1, 9).`
- **Texto novo:** `(for example: 7, 2, 15, 1, 9). Your entire response must be that single line of five
  numbers: do not write any explanation, reasoning, or other text before or after it.`

### Métricas do desenvolvimento antes → depois
| Medida | Rodada 0 | Rodada 1 |
|---|---|---|
| Sínteses: palavras, média (mín–máx) | 117,7 (108–129) | 110,2 (103–117) |
| Sínteses fora de 80–120 palavras | 8 de 30 | 0 de 30 |
| Reordenação: reenvios / fallbacks em 300 | 22 / 20 (6,7%) | 7 / 7 (2,3%) |
| nDCG@5 médio de V-B | 0,234 | 0,200 |
| nDCG@5 médio de V-C | 0,384 | 0,380 |
| nDCG@5 médio de B1, B2 e V-A (não dependem dos prompts C e D) | 0,087 · 0,190 · 0,248 | iguais |

Os 7 fallbacks restantes são todos do perfil D12 (mesmo tipo de resposta com explicação). Como as sínteses
foram regeradas com o prompt novo, os 20 candidatos de V-B mudaram, e por isso o nDCG@5 de V-B e V-C mudou.
O ajuste visou a obediência às regras, não o nDCG@5.

## Rodada 2
Não foi feita. Os critérios de obediência foram atendidos na rodada 1 (fallbacks abaixo de 5%, sínteses
dentro do intervalo). As versões da rodada 1 são as travadas em `lock-v1`.
