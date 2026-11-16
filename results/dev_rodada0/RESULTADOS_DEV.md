# RESULTADOS — TCC perfis sintéticos (conjunto de DESENVOLVIMENTO)

## 0. Identificação
- Repositório: https://github.com/Aderson79/tcc-motor.git · commit lock-v1: n/d · commit results-v1: o commit apontado pela tag `results-v1` (`git rev-parse results-v1`; pai: bcf95b5c20e2ef7ee8413b631588c36bbe59ffca)
- Data de execução: 2026-11-16
- Modelos (ID devolvido pela API e data de acesso): síntese e reordenação: claude-sonnet-5 · relatos: claude-sonnet-5, gemini-3.8-flash · acesso em None
- Embedding: all-mpnet-base-v2, revisão e8c3b32edf5434bc2275fc9bab85f82640a19130, sentence-transformers 6.3.0
- Preços usados (USD/1M tokens, entrada/saída, data, URL): claude-sonnet-5 2.0/10.0, 2026-11-16, https://platform.claude.com/docs/en/about-claude/pricing · gemini-3.8-flash 0.75/3.75, 2026-11-16, https://ai.google.dev/gemini-api/docs/pricing
- O*NET: 31.0, download em 2026-11-16, SHA-256 55033fc68b4c13ec23e7f74dc6378660f6e854e75d55d6e333ae0a761d3987cd
- Máquina: AMD Ryzen 5 3400G with Radeon Vega Graphics, 8 núcleos, 17 GB RAM, sem GPU; Windows-10-10.0.19045-SP0; Python 3.13.15; embedding em cpu

## 1. Catálogo
- Ocupações em occupation_data: 1016 · excluídas por critério: sem descrição 0, sem tarefas 93, sem RIASEC completo 93, sem relacionadas 93
- Catálogo final: 923
- Elegíveis por tipo predominante: R 388, I 112, A 28, S 129, E 100, C 166
- Ocupações que exigiram divisão em trechos: 489 (52.979%) · trechos por ocupação: média 1.542, máx 3
- Enunciados acima de 384 tokens: 0 · textos de perfil acima de 384 tokens: desenvolvimento, σ = 1,0: V-A 0, V-B 0
- Ocupações com variância zero no perfil OI (Pearson tratado como −1 em B2): 0

## 2. Conjunto de desenvolvimento
- Perfis por tipo: R 5, I 5, A 5, S 5, E 5, C 5 · redistribuição por falta de elegíveis: não
- Substituições por falha no filtro (dev / avaliação): 0 / 0 (lista em substituicoes.csv)
- Regerações de relato (tentativas 2 e 3): 2
- Relatos: frases média 4.000 (4–4), palavras média 93.967
- Sobreposição relato × texto da origem: média 0.069, DP 0.059, mediana 0.058, mín 0.000, máx 0.241
- Relacionadas no catálogo por perfil: média 5.000, mín 5, máx 5; perfis com < 5: 0

## 3. Desempenho — condição principal (desenvolvimento, σ = 1,0), n = 30
| Sistema | nDCG@5 média (DP) [mediana] | P@5 | MAP@5 | MRR@5 origem |
|---|---|---|---|---|
| B1 | 0.087 (0.143) [0.000] | 0.087 (0.146) [0.000] | 0.063 (0.114) [0.000] | 0.022 (0.085) [0.000] |
| B2 | 0.190 (0.229) [0.143] | 0.193 (0.213) [0.200] | 0.120 (0.167) [0.050] | 0.123 (0.225) [0.000] |
| V-A | 0.248 (0.316) [0.055] | 0.220 (0.285) [0.100] | 0.187 (0.273) [0.025] | 0.215 (0.358) [0.000] |
| V-B | 0.234 (0.297) [0.063] | 0.227 (0.266) [0.100] | 0.164 (0.222) [0.033] | 0.200 (0.337) [0.000] |
| V-C | 0.384 (0.347) [0.326] | 0.331 (0.293) [0.320] | 0.282 (0.266) [0.251] | 0.391 (0.481) [0.000] |

## 4–5. (comparações e sensibilidade só existem na avaliação)

## 6. Variação da reordenação (V-C)
| Condição | DP médio nDCG@5 | DP máx | sobreposição média | % perfis com 10 listas idênticas | reenvios | fallbacks |
|---|---|---|---|---|---|---|
| desenvolvimento, σ = 1,0 | 0.014 | 0.056 | 0.941 | 13.333 | 22 | 20 |

## 7. Tempo e custo (desenvolvimento, σ = 1,0)
| Sistema | tempo média (s) | mediana | p95 | custo médio/consulta (USD) |
|---|---|---|---|---|
| B1 | 0.0165 | 0.0160 | 0.0216 | 0.00000 |
| B2 | 0.0009 | 0.0009 | 0.0014 | 0.00000 |
| V-A | 0.4026 | 0.3955 | 0.4635 | 0.00000 |
| V-B | 4.5632 | 4.5588 | 4.9183 | 0.00351 |
| V-C | 5.9426 | 5.7932 | 7.1520 | 0.00837 |
- Custo total do motor no experimento: 1.56 USD · custo de construção do conjunto (relatos): 0.30 USD
- Tempo e custo usam 4 e 5 casas decimais porque B1/B2 e o custo por consulta ficariam zerados com 3. A condição de sensibilidade está em timing_cost.csv.

## 8. Ajuste e desvios
- Obediência às regras (informativo, nada foi rejeitado por estes critérios):
  - relatos fora de 3–5 frases: 0 de 30
  - sínteses (desenvolvimento, σ = 1,0): palavras média 117.700 (108–129); fora de 80–120: 8; com dígitos: 0; com "RIASEC": 0; cortadas por max_tokens: 0
- AJUSTES.md (íntegra):

# AJUSTES — log do ajuste no conjunto de desenvolvimento

No máximo duas rodadas. Só podem mudar os textos dos prompts A, C e D e o molde B.
Cada mudança registra: texto anterior, texto novo, motivo e métricas do desenvolvimento antes e depois.

## Rodada 0 (versões iniciais)
Prompts A, C, D e molde B iguais aos Apêndices A–D do TCC. Nenhuma mudança até agora.

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
- 2 perfis escolhidos pela semente 20261122 (não escolhidos a dedo): D01, D07

### D01 — origem: 39-4011.00 Embalmers
- Notas (desenvolvimento, σ = 1,0): R 4.180, I 3.323, A 1.001, S 2.055, E 1.995, C 3.705
- Relato: I have a steady, gentle hand and take pride in meticulous behind-the-scenes work where I can care for people with dignity and help them look peaceful and natural. I enjoy the blend of careful hands-on preparation, artistic touch-ups, and maintaining an exceptionally clean and safe environment. Just as importantly, I find meaning in supporting grieving families with patience, guiding them through stressful choices, and organizing memorial gatherings down to the last detail. Bringing quiet comfort and reassurance to people facing a profound loss is what motivates me the most.
- Síntese de V-B: This person is drawn to hands-on, practical work that requires precision, steady focus, and a methodical approach, preferring tasks with clear procedures and tangible, careful outcomes over abstract or highly creative pursuits. They are comfortable in structured, orderly environments where cleanliness, organization, and attention to detail matter, and they appreciate having systems and routines to follow rather than open-ended exploration. While not strongly driven by leadership or persuasion, they find quiet satisfaction in supporting others through sensitive, emotionally significant moments, offering calm reassurance and practical help rather than overt social engagement. They would feel most at ease in a controlled, dignified setting that blends careful manual work with modest interpersonal support, valuing competence, reliability, and thoughtful attentiveness over excitement, novelty, or highly expressive artistic outlets.
- B1: 21-1093.00 Social and Human Service Assistants [rel 0]; 39-4031.00 Morticians, Undertakers, and Funeral Arrangers [rel 1]; 51-9023.00 Mixing and Blending Machine Setters, Operators, and Tenders [rel 0]; 39-9011.00 Childcare Workers [rel 0]; 21-2011.00 Clergy [rel 0]
- B2: 19-4051.00 Nuclear Technicians [rel 0]; 19-5012.00 Occupational Health and Safety Technicians [rel 0]; 19-4071.00 Forest and Conservation Technicians [rel 0]; 19-4051.02 Nuclear Monitoring Technicians [rel 0]; 33-2021.00 Fire Inspectors and Investigators [rel 0]
- V-A: 39-4031.00 Morticians, Undertakers, and Funeral Arrangers [rel 1]; 39-4021.00 Funeral Attendants [rel 1]; 11-9171.00 Funeral Home Managers [rel 1]; 39-4011.00 Embalmers [rel 2]; 25-1121.00 Art, Drama, and Music Teachers, Postsecondary [rel 0]
- V-B: 29-1129.01 Art Therapists [rel 0]; 27-1013.00 Fine Artists, Including Painters, Sculptors, and Illustrators [rel 0]; 29-1122.00 Occupational Therapists [rel 0]; 31-2011.00 Occupational Therapy Assistants [rel 0]; 29-1129.02 Music Therapists [rel 0]
- V-C (execução 1): 29-1129.01 Art Therapists [rel 0]; 27-1013.00 Fine Artists, Including Painters, Sculptors, and Illustrators [rel 0]; 29-1122.00 Occupational Therapists [rel 0]; 31-2011.00 Occupational Therapy Assistants [rel 0]; 29-1129.02 Music Therapists [rel 0]

### D07 — origem: 15-1299.04 Penetration Testers
- Notas (desenvolvimento, σ = 1,0): R 4.785, I 5.315, A 2.382, S 1.000, E 2.778, C 6.465
- Relato: I really enjoy thinking like an intruder to see if I can uncover blind spots and find sneaky ways past digital barriers. I am constantly fascinated by the clever tricks people use to bypass locks, and I like trying those same moves to see how well our defenses hold up. When an unwanted break-in happens, I like piecing together clues to figure out how someone slipped inside. Afterwards, I take a lot of satisfaction in explaining those gaps in simple terms and helping people build better protections.
- Síntese de V-B: This person is drawn to structured, detail-oriented work that involves systematically testing systems, identifying weaknesses, and solving analytical puzzles. They enjoy hands-on technical investigation, methodically probing for vulnerabilities, tracing how a breach occurred, and organizing findings into clear, logical explanations. They are most comfortable in orderly, process-driven environments where precision, accuracy, and careful documentation matter, rather than in highly social or overtly creative settings. Their curiosity leans toward understanding mechanisms and uncovering hidden flaws through disciplined reasoning rather than artistic expression or persuasive influence. They likely prefer working independently or in small technical teams, focusing on concrete problems with defined rules, and take satisfaction in translating complex technical issues into straightforward, actionable guidance that helps others strengthen their defenses and improve overall system reliability.
- B1: 51-6041.00 Shoe and Leather Workers and Repairers [rel 0]; 35-3041.00 Food Servers, Nonrestaurant [rel 0]; 21-1092.00 Probation Officers and Correctional Treatment Specialists [rel 0]; 53-6061.00 Passenger Attendants [rel 0]; 21-2011.00 Clergy [rel 0]
- B2: 19-4099.01 Quality Control Analysts [rel 0]; 15-1299.02 Geographic Information Systems Technologists and Technicians [rel 0]; 17-2112.00 Industrial Engineers [rel 0]; 15-1299.08 Computer Systems Engineers/Architects [rel 1]; 15-1299.05 Information Security Engineers [rel 1]
- V-A: 13-1199.07 Security Management Specialists [rel 0]; 33-3021.06 Intelligence Analysts [rel 0]; 15-1299.06 Digital Forensics Analysts [rel 0]; 33-9021.00 Private Detectives and Investigators [rel 0]; 49-9094.00 Locksmiths and Safe Repairers [rel 0]
- V-B: 15-1299.06 Digital Forensics Analysts [rel 0]; 15-1299.04 Penetration Testers [rel 2]; 15-1299.05 Information Security Engineers [rel 1]; 13-1199.07 Security Management Specialists [rel 0]; 15-1212.00 Information Security Analysts [rel 1]
- V-C (execução 1): 15-1299.04 Penetration Testers [rel 2]; 15-1299.06 Digital Forensics Analysts [rel 0]; 15-1212.00 Information Security Analysts [rel 1]; 15-1299.05 Information Security Engineers [rel 1]; 15-1253.00 Software Quality Assurance Analysts and Testers [rel 1]
