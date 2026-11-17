# RESULTADOS — TCC perfis sintéticos

## 0. Identificação
- Repositório: https://github.com/Aderson79/tcc-motor.git · commit lock-v1: e2d8076dc7e3c5d72492fddc0669bcc82d46bd4b · commit results-v1: o commit apontado pela tag `results-v1` (`git rev-parse results-v1`; pai: e2d8076dc7e3c5d72492fddc0669bcc82d46bd4b)
- Data de execução: 2026-11-16
- Modelos (ID devolvido pela API e data de acesso): síntese e reordenação: claude-sonnet-5 · relatos: gemini-3.8-flash · acesso em 2026-11-16
- Embedding: all-mpnet-base-v2, revisão e8c3b32edf5434bc2275fc9bab85f82640a19130, sentence-transformers 6.3.0
- Preços usados (USD/1M tokens, entrada/saída, data, URL): claude-sonnet-5 2.0/10.0, 2026-11-16, https://platform.claude.com/docs/en/about-claude/pricing · gemini-3.8-flash 0.75/3.75, 2026-11-16, https://ai.google.dev/gemini-api/docs/pricing
- O*NET: 31.0, download em 2026-11-16, SHA-256 55033fc68b4c13ec23e7f74dc6378660f6e854e75d55d6e333ae0a761d3987cd
- Máquina: AMD Ryzen 5 3400G with Radeon Vega Graphics, 8 núcleos, 17 GB RAM, sem GPU; Windows-10-10.0.19045-SP0; Python 3.13.15; embedding em cpu

## 1. Catálogo
- Ocupações em occupation_data: 1016 · excluídas por critério: sem descrição 0, sem tarefas 93, sem RIASEC completo 93, sem relacionadas 93
- Catálogo final: 923
- Elegíveis por tipo predominante: R 388, I 112, A 28, S 129, E 100, C 166
- Ocupações que exigiram divisão em trechos: 489 (52.979%) · trechos por ocupação: média 1.542, máx 3
- Enunciados acima de 384 tokens: 0 · textos de perfil acima de 384 tokens: σ = 1,0: V-A 0, V-B 0; σ = 0,5: V-A 0, V-B 0
- Ocupações com variância zero no perfil OI (Pearson tratado como −1 em B2): 0

## 2. Conjunto de avaliação
- Perfis por tipo: R 38, I 34, A 23, S 33, E 35, C 35 · redistribuição por falta de elegíveis: sim — tipos em falta {'A': 23}, déficit 10, sorteadas ['R:47-4099.03', 'R:17-2171.00', 'R:51-9161.00', 'C:23-1021.00', 'I:29-2011.02', 'R:49-9051.00', 'E:11-3111.00', 'E:27-3031.00', 'R:47-5012.00', 'C:13-2022.00'] (regra: uniform_over_remaining_occupations_of_other_types)
- Substituições por falha no filtro (dev / avaliação): 0 / 2 (lista em substituicoes.csv)
- Regerações de relato (tentativas 2 e 3): 14
- Relatos: frases média 4.000 (4–4), palavras média 93.354
- Sobreposição relato × texto da origem: média 0.083, DP 0.068, mediana 0.073, mín 0.000, máx 0.255
- Relacionadas no catálogo por perfil: média 5.000, mín 5, máx 5; perfis com < 5: 0

## 3. Desempenho — condição principal (σ = 1,0), n = 198
| Sistema | nDCG@5 média (DP) [mediana] | P@5 | MAP@5 | MRR@5 origem |
|---|---|---|---|---|
| B1 | 0.120 (0.202) [0.000] | 0.107 (0.168) [0.000] | 0.070 (0.131) [0.000] | 0.114 (0.293) [0.000] |
| B2 | 0.157 (0.204) [0.000] | 0.141 (0.179) [0.000] | 0.082 (0.127) [0.000] | 0.159 (0.291) [0.000] |
| V-A | 0.231 (0.266) [0.127] | 0.199 (0.231) [0.200] | 0.140 (0.199) [0.040] | 0.247 (0.370) [0.000] |
| V-B | 0.198 (0.241) [0.098] | 0.182 (0.209) [0.200] | 0.126 (0.176) [0.040] | 0.166 (0.318) [0.000] |
| V-C | 0.384 (0.310) [0.408] | 0.318 (0.266) [0.400] | 0.273 (0.252) [0.200] | 0.398 (0.449) [0.077] |

## 4. Comparações (σ = 1,0, nDCG@5)
| Comp. | d = | média d | mediana d | n | n não nulos | W | p bruto | p Bonferroni | Decisão |
|---|---|---|---|---|---|---|---|---|---|
| (a) H1 | V-B − V-A | -0.033 | 0.000 | 198 | 135 | 3930.500 | 0.147 | 0.59 | não favorece |
| (b) H2 | V-C − V-B | 0.187 | 0.152 | 198 | 141 | 753.500 | 2.11e-18 | 8.43e-18 | favorece o sistema mais elaborado |
| (c) H3 | V-C − B1 | 0.264 | 0.258 | 198 | 162 | 1506.000 | 1.57e-17 | 6.26e-17 | favorece o sistema mais elaborado |
| (d) H4 | V-C − B2 | 0.227 | 0.231 | 198 | 166 | 1994.500 | 1.73e-15 | 6.93e-15 | favorece o sistema mais elaborado |

## 5. Sensibilidade (σ = 0,5) — descritivo
| Sistema | nDCG@5 média (DP) [mediana] | P@5 | MAP@5 | MRR@5 origem |
|---|---|---|---|---|
| B1 | 0.120 (0.202) [0.000] | 0.107 (0.168) [0.000] | 0.070 (0.131) [0.000] | 0.114 (0.293) [0.000] |
| B2 | 0.360 (0.248) [0.345] | 0.267 (0.197) [0.200] | 0.189 (0.183) [0.180] | 0.480 (0.415) [0.333] |
| V-A | 0.234 (0.269) [0.127] | 0.201 (0.232) [0.200] | 0.142 (0.200) [0.040] | 0.251 (0.376) [0.000] |
| V-B | 0.207 (0.237) [0.118] | 0.194 (0.216) [0.200] | 0.136 (0.181) [0.050] | 0.162 (0.317) [0.000] |
| V-C | 0.384 (0.315) [0.413] | 0.318 (0.270) [0.330] | 0.273 (0.264) [0.200] | 0.408 (0.445) [0.247] |

Diferença do nDCG@5 médio (σ = 0,5 − σ = 1,0): B1 +0.000 · B2 +0.203 · V-A +0.003 · V-B +0.010 · V-C +0.000

## 6. Variação da reordenação (V-C)
| Condição | DP médio nDCG@5 | DP máx | sobreposição média | % perfis com 10 listas idênticas | reenvios | fallbacks |
|---|---|---|---|---|---|---|
| σ = 1,0 | 0.015 | 0.150 | 0.937 | 6.061 | 0 | 0 |
| σ = 0,5 | 0.014 | 0.118 | 0.937 | 8.081 | 3 | 2 |

## 7. Tempo e custo (σ = 1,0)
| Sistema | tempo média (s) | mediana | p95 | custo médio/consulta (USD) |
|---|---|---|---|---|
| B1 | 0.0162 | 0.0157 | 0.0223 | 0.00000 |
| B2 | 0.0008 | 0.0008 | 0.0011 | 0.00000 |
| V-A | 0.4026 | 0.3984 | 0.4599 | 0.00000 |
| V-B | 4.2815 | 4.2838 | 4.7071 | 0.00345 |
| V-C | 5.4997 | 5.4846 | 5.9748 | 0.00800 |
- Custo total do motor no experimento: 19.36 USD · custo de construção do conjunto (relatos): 1.57 USD
- Tempo e custo usam 4 e 5 casas decimais porque B1/B2 e o custo por consulta ficariam zerados com 3. A condição de sensibilidade está em timing_cost.csv.

## 8. Ajuste e desvios
- Obediência às regras (informativo, nada foi rejeitado por estes critérios):
  - relatos fora de 3–5 frases: 0 de 198
  - sínteses (σ = 1,0): palavras média 110.515 (99–120); fora de 80–120: 0; com dígitos: 0; com "RIASEC": 0; cortadas por max_tokens: 0
  - sínteses (σ = 0,5): palavras média 109.985 (99–121); fora de 80–120: 1; com dígitos: 0; com "RIASEC": 0; cortadas por max_tokens: 0
- AJUSTES.md (íntegra):

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

- DESVIOS.md (íntegra):

# DESVIOS — todo desvio do protocolo, com motivo, data e efeito

## D1 — Tipo Artístico com menos de 38 elegíveis (16/11/2026)
- **Fato:** o catálogo tem 28 ocupações de tipo predominante A (R 388, I 112, S 129, E 100, C 166).
- **Regra aplicada (Seção 6, item 3):** depois das 5 do desenvolvimento, as 23 restantes de A entram todas
  na avaliação; as 10 que faltam são sorteadas de modo uniforme entre as ocupações elegíveis restantes
  dos demais tipos (logo, proporcional ao tamanho de cada tipo), com `seed_eval`.
- **Efeito:** a avaliação terá 23 perfis A e 175 dos outros tipos (em vez de 33 por tipo); o total continua 198.
- **Consequência para substituições:** na avaliação não sobra nenhuma ocupação A para substituir um relato
  que falhe três vezes no filtro. Nesse caso a substituta é sorteada pela mesma regra (uniforme entre as
  elegíveis restantes dos demais tipos) e o caso é acrescentado aqui.
- **Situação:** aguardando ciência do Aderson (ponto de parada da Seção 17).

## D2 — PostgreSQL com pgvector fora do Docker (16/11/2026)
- **Fato:** a máquina de execução (Windows 10 Pro) não tem Docker nem WSL, e a instalação exigiria
  privilégio de administrador e reinicialização.
- **O que foi feito:** PostgreSQL 16.15 e pgvector 0.8.6 instalados do conda-forge (via micromamba) numa
  pasta do usuário (`C:\Users\User\.tcc-pg`), em instância própria na porta 54329, com a mesma DSN do
  `config.yaml`. O `docker-compose.yml` continua no repositório para quem for reproduzir com Docker.
- **Efeito:** nenhum sobre o método. A tabela, a consulta (`ORDER BY embedding <=> %s, code`), a ausência
  de índice aproximado e a busca exata são as mesmas; muda só a forma de instalar o servidor. Os tempos de
  resposta refletem esta máquina.
- **Situação:** decidido pelo Aderson em 16/11/2026.

## D3 — Troca dos papéis dos modelos: tentada e desfeita (16/11/2026, antes do `lock-v1`)
- **Fato:** por causa do saldo inicial na API da Anthropic (US$ 5), os papéis foram trocados por algumas
  horas: `claude-sonnet-5` nos relatos e `gemini-3.8-flash` na síntese e na reordenação. O conjunto de
  desenvolvimento foi executado nessa configuração (30 relatos, 30 sínteses e 280 das 300 reordenações; a execução foi interrompida quando se decidiu desfazer a troca).
- **O que se observou:** na reordenação, o raciocínio padrão do Gemini consumiu em média cerca de 3.560
  tokens por chamada (para ~15 tokens de resposta), com latência mediana de 27 s e custo de ~US$ 0,014 por
  chamada. Projetado para as 3.960 reordenações da avaliação: ~US$ 57 e 7–8 horas, acima do limite de
  US$ 50 da Seção 17. Além disso, os limites de 400 e 50 tokens não podiam ser aplicados no Gemini, porque
  o raciocínio conta dentro do limite de saída (com limite de 50, a resposta veio vazia).
- **Decisão (Aderson, 16/11/2026):** desfazer a troca e voltar ao desenho original do protocolo — Gemini
  nos relatos, Sonnet na síntese e na reordenação, com `max_tokens` de 400 e 50. O saldo da Anthropic foi
  reforçado.
- **Efeito:** nenhum sobre o experimento final nem sobre o texto do TCC. Tudo o que foi gerado na
  configuração trocada (relatos, sínteses, reordenações, substituições) foi movido para
  `data/generated/_troca_desfeita/` e **não é usado**; o conjunto de desenvolvimento foi refeito do zero,
  a partir do mesmo sorteio (`sample_dev.csv`). O `logs/calls.jsonl` mantém todas as chamadas.

## D4 — Correção no relatório depois do `lock-v1` (16/11/2026)
- **Fato:** `logs/calls.jsonl` guarda também as 42 chamadas de relato feitas ao `claude-sonnet-5` durante a
  troca desfeita (D3). O `src/tcc/report.py` travado lia todas as chamadas de relato do log, de modo que
  (a) a linha "Modelos" do `RESULTADOS.md` listaria o Sonnet como modelo dos relatos e (b) o custo de
  construção do conjunto de desenvolvimento somaria essas chamadas ao preço do Gemini.
- **Correção:** o relatório passa a considerar só as chamadas de relato feitas ao modelo de relatos do
  `config.yaml`. Duas condições acrescentadas em `report.py`; nada mais mudou.
- **Hash antes:** `e2d8076` (`lock-v1`). **Hash depois:** o do commit `results-v1`.
- **Efeito:** nenhum sobre relatos, sínteses, listas, métricas, testes ou tempos. Corrige só a identificação
  do modelo e o custo de construção informados no relatório. Feita antes de o pacote ser gerado.

## Notas de interpretação (não alteram o protocolo; registradas por transparência)
- **Raciocínio do Sonnet:** no `claude-sonnet-5`, omitir o parâmetro `thinking` ativa o raciocínio adaptativo
  por padrão; as chamadas enviam `thinking={"type": "disabled"}`.
- **Tempo limite do Gemini:** cada chamada tem limite de 60 s no cliente; estouro ou 429/5xx contam como erro
  de transporte (nova tentativa com espera exponencial, registrada em `logs/calls.jsonl`).
- **Tarefas sem tipo:** 418 linhas de `task_statements.csv` têm `Task Type` vazio (nem Core nem Supplemental).
  Elas foram mantidas: o texto indexado e o prompt A usam todas as tarefas da ocupação, na ordem do arquivo.
- **Desvio padrão descritivo:** amostral (ddof = 1).
- **Python:** 3.13 (o protocolo pede 3.11 ou superior).

## 9. Exemplos ilustrativos (para a discussão, sem análise adicional)
- 2 perfis escolhidos pela semente 20261122 (não escolhidos a dedo): P001, P043

### P001 — origem: 51-2023.00 Electromechanical Equipment Assemblers
- Notas (σ = 1,0): R 7.000, I 3.046, A 3.019, S 2.520, E 1.000, C 5.788
- Relato: I really enjoy working with my hands to put complex items together and see all the separate pieces become something whole. I like following detailed diagrams, shaving down rough spots, and making tiny tweaks so every single part fits snugly. Hooking up cords, tightening hardware, and guiding workshop machinery are all deeply satisfying to me. When I finish, I take a lot of pride in trying out the final creation to make sure it runs smoothly and functions exactly as intended.
- Síntese de V-B: This person thrives on hands-on, tangible work that involves building, assembling, and fine-tuning physical objects. They take satisfaction in following structured plans and diagrams, methodically adjusting and calibrating pieces until everything fits together precisely, and they enjoy operating tools and machinery to bring a project to completion. Testing the finished product to confirm it works correctly gives them a strong sense of accomplishment. They prefer organized, orderly environments where tasks have clear steps and measurable outcomes, rather than abstract theorizing, persuasive communication, or highly social settings. A workshop, technical, or mechanical environment that rewards precision, practical skill, and steady, methodical effort would suit them well.
- B1: 51-7011.00 Cabinetmakers and Bench Carpenters [rel 0]; 51-6031.00 Sewing Machine Operators [rel 0]; 17-3012.00 Electrical and Electronics Drafters [rel 0]; 51-9195.05 Potters, Manufacturing [rel 0]; 15-1251.00 Computer Programmers [rel 0]
- B2: 25-4013.00 Museum Technicians and Conservators [rel 0]; 49-9061.00 Camera and Photographic Equipment Repairers [rel 0]; 27-4011.00 Audio and Video Technicians [rel 0]; 49-2097.00 Audiovisual Equipment Installers and Repairers [rel 0]; 51-9195.00 Molders, Shapers, and Casters, Except Metal and Plastic [rel 0]
- V-A: 27-1012.00 Craft Artists [rel 0]; 27-1013.00 Fine Artists, Including Painters, Sculptors, and Illustrators [rel 0]; 51-7011.00 Cabinetmakers and Bench Carpenters [rel 0]; 17-3013.00 Mechanical Drafters [rel 0]; 51-4041.00 Machinists [rel 0]
- V-B: 51-2041.00 Structural Metal Fabricators and Fitters [rel 0]; 51-7011.00 Cabinetmakers and Bench Carpenters [rel 0]; 51-4041.00 Machinists [rel 0]; 47-2031.00 Carpenters [rel 0]; 17-3013.00 Mechanical Drafters [rel 0]
- V-C (execução 1): 51-4041.00 Machinists [rel 0]; 51-4111.00 Tool and Die Makers [rel 0]; 51-4061.00 Model Makers, Metal and Plastic [rel 0]; 51-2041.00 Structural Metal Fabricators and Fitters [rel 0]; 51-9161.00 Computer Numerically Controlled Tool Operators [rel 0]

### P043 — origem: 15-1252.00 Software Developers
- Notas (σ = 1,0): R 2.681, I 6.808, A 3.541, S 2.867, E 2.672, C 5.977
- Relato: I really enjoy listening to people describe their everyday challenges and figuring out how to build digital tools that make their work easier. I love solving complex logic puzzles, finding and fixing tricky glitches, and making sure everything runs smoothly and reliably. I also like guiding a team through a build, dividing up tasks, and bouncing ideas off each other to find the smartest solutions. When a new creation is finished, I take pride in walking people through how to use it so they feel confident and supported.
- Síntese de V-B: This person thrives on deep analytical thinking, enjoying the process of untangling complex logic puzzles and diagnosing tricky problems until everything functions smoothly. They are drawn to structured, methodical environments where accuracy, organization, and careful attention to detail matter, preferring well-defined systems over ambiguous or purely expressive tasks. While not especially driven by persuasion or artistic expression, they appreciate collaborating with a team, dividing responsibilities, and exchanging ideas to reach effective solutions. They also find satisfaction in explaining finished work clearly so others feel capable using it. Overall, they would feel most comfortable in orderly, intellectually challenging settings that blend careful problem-solving with occasional teamwork and mentoring.
- B1: 29-1122.00 Occupational Therapists [rel 0]; 15-1251.00 Computer Programmers [rel 1]; 27-4021.00 Photographers [rel 0]; 27-4032.00 Film and Video Editors [rel 0]; 17-3024.01 Robotics Technicians [rel 0]
- B2: 15-2051.00 Data Scientists [rel 0]; 15-2041.00 Statisticians [rel 0]; 19-3093.00 Historians [rel 0]; 19-3022.00 Survey Researchers [rel 0]; 19-4061.00 Social Science Research Assistants [rel 0]
- V-A: 25-1021.00 Computer Science Teachers, Postsecondary [rel 0]; 15-1221.00 Computer and Information Research Scientists [rel 0]; 25-1121.00 Art, Drama, and Music Teachers, Postsecondary [rel 0]; 17-2112.01 Human Factors Engineers and Ergonomists [rel 0]; 13-1141.00 Compensation, Benefits, and Job Analysis Specialists [rel 0]
- V-B: 15-2021.00 Mathematicians [rel 0]; 19-3033.00 Clinical and Counseling Psychologists [rel 0]; 31-2011.00 Occupational Therapy Assistants [rel 0]; 19-3032.00 Industrial-Organizational Psychologists [rel 0]; 25-1022.00 Mathematical Science Teachers, Postsecondary [rel 0]
- V-C (execução 1): 15-1221.00 Computer and Information Research Scientists [rel 0]; 15-2021.00 Mathematicians [rel 0]; 15-2051.00 Data Scientists [rel 0]; 15-2051.01 Business Intelligence Analysts [rel 0]; 43-9111.00 Statistical Assistants [rel 0]
