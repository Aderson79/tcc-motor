# Especificação do motor e do experimento — TCC (perfis sintéticos)

**Para:** Claude Code
**Autor do TCC:** Aderson Jônatas Ribeiro Mesquita — Engenharia de Software, iCEV
**Orientador:** Prof. Francisco Luciani de Miranda Vieira
**Título do TCC:** *Síntese do perfil e reordenação por LLM na recomendação de ocupações a partir de interesses RIASEC: avaliação comparativa com perfis sintéticos sobre o catálogo O\*NET*
**Versão deste documento:** 16/11/2026

---

## 0. Como usar este documento

1. **Objetivo único.** O objetivo é produzir, com o mínimo de código necessário, os números que vão preencher a Seção 4 (Resultados e Discussão) do TCC. Isso não inclui interface, API web nem produto. O que se entrega é um repositório reprodutível e um **pacote de resultados** (Seção 15).
2. **A Seção 3 do TCC e o Protocolo de Avaliação já descrevem o experimento como fato.** Este documento traduz esse texto em instruções de implementação. Se houver dúvida, vale o que está aqui. Se algo aqui contradisser o texto, pare e pergunte.
3. **Nada fora do protocolo entra no experimento.** Isso vale para sistemas, métricas, testes, parâmetros e modelos. Qualquer coisa que precise mudar (um modelo indisponível, um arquivo com outra estrutura, um tipo RIASEC sem ocupações suficientes) é registrada em `DESVIOS.md` com motivo, data e efeito. Nunca é contornada em silêncio.
4. **Pontos de parada obrigatórios** (pare e avise o Aderson) estão na Seção 17.
5. **Idioma.** O código e os textos enviados aos modelos ficam em inglês. `RESULTADOS.md`, `DESVIOS.md` e o README ficam em português.

---

## 1. Prazo

A entrega final do TCC é em **27/11/2026**. A revisão do orientador acontece entre 19 e 21/11, por isso **o pacote de resultados precisa estar pronto até 18/11 à noite**.

| Quando | Marco |
|---|---|
| 16/11 | Repositório, catálogo, índice pgvector e os cinco sistemas rodando sobre o conjunto de desenvolvimento (30 perfis) |
| 17/11 (manhã) | Ajuste no conjunto de desenvolvimento, com no máximo duas rodadas. **Travamento**: commit e tag `lock-v1` |
| 17/11 (tarde) | Geração do conjunto de avaliação (198 relatos, ruído nas duas condições, gabarito) e execução dos cinco sistemas |
| 18/11 | Métricas, testes estatísticos, tempo, custo e o **pacote de resultados** |

Se algo ameaçar esse prazo, avise logo. Não corte etapas do protocolo para ganhar tempo.

---

## 2. Visão geral do experimento

- **Catálogo:** as ocupações do O\*NET 31.0 que têm descrição, ao menos um enunciado de tarefa, perfil RIASEC completo e ao menos uma ocupação relacionada.
- **Perfis sintéticos:** cada perfil nasce de uma *ocupação de origem* e tem duas partes:
  - as seis notas RIASEC da origem, com ruído gaussiano;
  - um relato em primeira pessoa escrito pelo Gemini a partir das tarefas da origem, sem o título.
- **Conjuntos:**
  - Desenvolvimento: 30 perfis (5 por tipo RIASEC), usados só para ajuste.
  - Avaliação: 198 perfis (33 por tipo).
- **Condições de ruído:** σ = 1,0 é a condição principal e σ = 0,5 é a de sensibilidade.
- **Gabarito:**
  - a origem tem relevância 2;
  - as ocupações *Primary-Short* da origem que estão no catálogo têm relevância 1;
  - todas as demais têm relevância 0.
- **Cinco sistemas:**

| Sistema | Entrada | LLM | Ordenação |
|---|---|---|---|
| B1 | relato | — | BM25 sobre o texto indexado; cinco primeiras |
| B2 | seis notas | — | Pearson com o perfil RIASEC da ocupação; cinco primeiras |
| V-A | molde fixo (notas em palavras) + relato | — | cosseno entre embeddings; cinco primeiras |
| V-B | perfil sintetizado pelo LLM (notas + relato) | síntese | cosseno; recupera 20 e apresenta as cinco primeiras |
| V-C | perfil de V-B + os 20 candidatos de V-B | síntese + reordenação | o LLM escolhe e ordena cinco; 10 execuções |

- **Métricas:**
  - nDCG@5 é a principal.
  - P@5, MAP@5 e MRR@5 de origem são complementares.
- **Comparações inferenciais:** são só quatro, todas na condição σ = 1,0:
  - V-A × V-B
  - V-B × V-C
  - V-C × B1
  - V-C × B2

  Usam Wilcoxon pareado com Bonferroni, p < 0,0125. Uma comparação conta como sucesso quando a diferença das médias de nDCG@5 é de pelo menos 0,05 **e** p < 0,0125.

---

## 3. Stack e estrutura do repositório

- **Linguagem:** Python 3.11+.
- **Dependências:**
  - `pandas`, `numpy`, `scipy`
  - `sentence-transformers`, `rank-bm25`, `scikit-learn` (só para a lista de stopwords)
  - `psycopg[binary]`, `pgvector`
  - `anthropic`, `google-genai`
  - `pyyaml`, `python-dotenv`, `pytest`
- **Banco:** PostgreSQL com pgvector em Docker, imagem `pgvector/pgvector:pg16`, numa instância própria.
- **Segredos:** `ANTHROPIC_API_KEY` e `GEMINI_API_KEY` ficam em `.env`. O `.env` entra no `.gitignore` e **nunca vai para commit**.
- **Visibilidade:** o repositório fica **privado** até o Aderson decidir publicá-lo.
- **Independência:** não use nenhum código, prompt, dado ou infraestrutura da Career Angel/Vero Solutions. O repositório é novo e independente.

Estrutura sugerida:

```
tcc-motor/
├── README.md                 # como reproduzir, passo a passo
├── config.yaml               # TODOS os parâmetros, sementes, modelos e preços
├── docker-compose.yml        # pgvector
├── prompts/
│   ├── A_relato.txt          # Apêndice A
│   ├── B_molde_va.txt        # Apêndice B
│   ├── C_sintese.txt         # Apêndice C
│   └── D_reordenacao.txt     # Apêndice D
├── src/tcc/
│   ├── onet.py               # leitura dos CSV do O*NET
│   ├── catalog.py            # filtro de elegibilidade e texto indexado
│   ├── embed.py              # chunking, embeddings, carga no pgvector
│   ├── sampling.py           # sorteio estratificado dev/avaliação
│   ├── profiles.py           # ruído, geração de relatos, filtro de título, sobreposição
│   ├── gold.py               # gabarito
│   ├── systems/{b1,b2,va,vb,vc}.py
│   ├── llm.py                # clientes Anthropic e Gemini + log de chamadas
│   ├── run.py                # execução dos sistemas
│   ├── metrics.py            # nDCG@5, P@5, AP@5, MRR@5 de origem
│   ├── stats.py              # Wilcoxon, Bonferroni, descritivas
│   └── report.py             # gera o pacote de resultados
├── tests/                    # testes obrigatórios (Seção 16)
├── data/
│   ├── raw/                  # CSV do O*NET (não versionar o zip; versionar o checksum)
│   └── generated/            # relatos, notas, sínteses, rankings (versionar)
├── logs/calls.jsonl          # toda chamada a LLM
├── results/                  # pacote de resultados (Seção 15)
├── AJUSTES.md                # log do ajuste no conjunto de desenvolvimento
└── DESVIOS.md                # todo desvio do protocolo
```

Cada etapa é um comando idempotente: `python -m tcc.<etapa>`, ou um `Makefile`. Uma etapa que gera texto por LLM **não regera** o que já está salvo. Para refazer, é preciso apagar o arquivo de propósito, e isso também vai para `DESVIOS.md` se acontecer depois do travamento.

---

## 4. Etapa 1 — Dados do O\*NET e catálogo

**Fonte:** O\*NET 31.0 em CSV.
- ZIP completo: `https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip`
- Arquivos avulsos: `https://www.onetcenter.org/dl_files/database/db_31_0_csv/<arquivo>.csv`

Registre a data do download e o SHA-256 do zip (ou dos arquivos) em `config.yaml`.

Arquivos usados (confira os nomes e cabeçalhos reais no download):

| Arquivo | Uso | Colunas relevantes |
|---|---|---|
| `occupation_data.csv` (~1.016 linhas) | título e descrição | O\*NET-SOC Code, Title, Description |
| `task_statements.csv` | enunciados de tarefas | O\*NET-SOC Code, Task, Task Type |
| `career_interest_types.csv` | perfil RIASEC | O\*NET-SOC Code, Element Name, Scale ID, Data Value |
| `related_occupations.csv` | gabarito | O\*NET-SOC Code, Related O\*NET-SOC Code, Relatedness Tier, Index |

**Atenção:** na versão 30.3 o antigo arquivo *Interests* passou a se chamar *Career Interest Types*.
- A escala **OI** traz o nível de cada tipo (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).
- A escala **IH** traz os códigos de ponto alto e **não é usada**.
- Filtre `Scale ID == "OI"` e use os seis `Element Name` acima.
- **Valide que os valores de OI estão entre 1 e 7.** Se não estiverem, pare (Seção 17).

**Elegibilidade.** Uma ocupação entra no catálogo se tiver todos os itens abaixo:
- descrição não vazia;
- ao menos um enunciado de tarefa;
- as seis notas OI;
- ao menos uma linha em `related_occupations.csv` (qualquer tier).

**Texto indexado** de cada ocupação: `"{Title}. {Description} {Task_1} {Task_2} ... {Task_n}"`, com todas as tarefas (Core e Supplemental) na ordem do arquivo.

**Tipo RIASEC predominante:** é a dimensão de maior nota OI. Empates são desfeitos pela ordem R, I, A, S, E, C.

**Registre em `results/`:**
- o número de ocupações em `occupation_data.csv`;
- quantas foram excluídas por cada critério;
- o **tamanho final do catálogo**;
- o número de elegíveis por tipo predominante.

O TCC afirma que a versão 31.0 tem 923 ocupações em nível de dados. Reporte o número que encontrar, seja ele qual for.

---

## 5. Etapa 2 — Embeddings e pgvector

- **Modelo:** `sentence-transformers/all-mpnet-base-v2`, executado localmente, com 768 dimensões.
  - Registre a revisão (commit/sha do Hugging Face, por exemplo via `huggingface_hub.model_info(...).sha`) e a versão do `sentence-transformers`.
  - O mesmo modelo serve para ocupações e perfis.
- **Limite:** `max_seq_length = 384` tokens do tokenizador do modelo, contando os tokens especiais.
- **Divisão em trechos (chunking):**
  - Monte os trechos de forma gulosa, na ordem do texto indexado.
  - O primeiro trecho começa com `"{Title}. {Description}"`, e as tarefas vão sendo acrescentadas.
  - Abre-se um trecho novo quando a próxima tarefa faria o trecho atual passar do limite.
  - **Nunca parta um enunciado.**
  - Se um único enunciado sozinho passar do limite, ele fica num trecho próprio (truncado pelo modelo), e esses casos são contados e reportados.
- **Vetor da ocupação:** é a média dos vetores dos trechos (cada um com `normalize_embeddings=True`), normalizada de novo em L2.
- **Vetor do perfil:**
  - O texto do perfil é vetorizado inteiro, normalizado.
  - Verifique e reporte quantos textos de perfil passam de 384 tokens. O TCC afirma que nenhum passa. Se algum passar, registre em `DESVIOS.md`.
- **pgvector:**
  - A tabela é `occupations(code text primary key, title text, embedding vector(768))`.
  - **Não crie índice aproximado** (nem HNSW nem IVFFlat): a busca é exata.
  - A consulta é `ORDER BY embedding <=> %s, code LIMIT k`. O operador `<=>` é a distância de cosseno; o desempate é pelo código.

**Reporte:** o número de ocupações que exigiram divisão e a distribuição de trechos por ocupação (média e máximo).

---

## 6. Etapa 3 — Sorteio dos conjuntos

Todas as sementes ficam em `config.yaml`. Use `numpy.random.default_rng(seed)`.

1. **Desenvolvimento (antes do travamento):** para cada tipo, sorteie 5 ocupações entre as elegíveis daquele tipo, com `seed_dev`, o que dá 30 no total.
2. **Avaliação:** para cada tipo, sorteie 33 entre as elegíveis restantes daquele tipo, com `seed_eval`, o que dá 198 no total.
   - As sementes são definidas antes do travamento.
   - O sorteio da avaliação e a geração dos perfis só são **executados depois** do travamento.
3. **Falta de ocupações num tipo:** cada tipo precisa de 38 elegíveis.
   - Se um tipo tiver menos, todas as que restarem dele depois do conjunto de desenvolvimento entram na avaliação.
   - A diferença é sorteada entre os demais tipos, de forma proporcional ou uniforme. A regra escolhida fica documentada e reportada em `DESVIOS.md` e em `results/`.
4. **Substituição:** quando um relato falha três vezes no filtro de título (Etapa 4), a ocupação é trocada por outra **do mesmo tipo**, sorteada entre as elegíveis ainda não usadas em nenhum conjunto, com `seed_replacement`.
   - Cada substituição é registrada com a origem descartada, a nova origem e as palavras que dispararam o filtro.
   - A regra vale também para o conjunto de desenvolvimento.

**IDs:** `D01`–`D30` para o desenvolvimento e `P001`–`P198` para a avaliação.

---

## 7. Etapa 4 — Perfis sintéticos

### 7.1 Notas RIASEC com ruído
- Partem das seis notas OI da origem, na escala de 1 a 7.
- Some ruído gaussiano independente N(0, σ) a cada dimensão e **limite o resultado a [1, 7]** com clip.
- **Duas condições independentes:**
  - σ = 1,0 (principal), com `seed_noise_main`;
  - σ = 0,5 (sensibilidade), com `seed_noise_sens`.
- O desenvolvimento usa só σ = 1,0, com semente própria.
- Salve as notas com precisão total em `data/generated/scores_{cond}.csv`.

### 7.2 Relato (Gemini)
- **Modelo:** `gemini-3.8-flash`, com a configuração padrão. **Não defina temperatura**, nem outro parâmetro de amostragem, nem orçamento de raciocínio.
- **Prompt:** Apêndice A (Apêndice ao final deste documento), em que `{task_statements}` é a lista de **todas** as tarefas da origem, uma por linha, precedidas de "- ".
- **Um relato por origem**, igual nas duas condições de ruído. O relato é gerado uma vez e salvo em `data/generated/relatos.jsonl`.
- **Filtro de título:**
  1. As palavras significativas do título são os tokens alfabéticos em minúsculas, com 3 ou mais letras, que não estão em `sklearn.feature_extraction.text.ENGLISH_STOP_WORDS`.
  2. Os tokens do relato passam pelo mesmo tratamento.
  3. Compare com uma normalização leve: remova o "s" final dos dois lados.
  4. Se houver qualquer coincidência, o relato é rejeitado e gerado de novo.
  5. Depois de 3 tentativas rejeitadas, a ocupação é substituída (Etapa 3, item 4).
  6. Registre cada tentativa e as palavras coincidentes.
- **Não rejeite** por outros critérios, como número de frases ou termos técnicos. O protocolo só prevê o filtro de título. Registre apenas o número de frases e de palavras de cada relato.
- **Erros de transporte** (rede, 429, 5xx): use nova tentativa com espera exponencial. Essas tentativas **não contam** como tentativas do filtro, mas ficam registradas.
- Registre no `logs/calls.jsonl`:
  - o modelo devolvido pela API;
  - a latência;
  - os tokens de entrada e de saída, e os de raciocínio, se a API informar.

### 7.3 Sobreposição de palavras (só relatórios)
- Para cada relato da avaliação: sobreposição = |tipos de palavra de conteúdo do relato ∩ tipos de palavra de conteúdo do texto indexado da origem| ÷ |tipos de palavra de conteúdo do relato|.
- Palavra de conteúdo é o mesmo tratamento do filtro (alfabética, minúscula, 3 ou mais letras, sem stopwords), mas **sem** a normalização do "s".
- Reporte média, desvio padrão, mediana, mínimo e máximo.

---

## 8. Etapa 5 — Gabarito

O gabarito é construído **antes** de executar os sistemas sobre a avaliação. Para cada perfil:

- a origem tem relevância 2;
- as ocupações com `Relatedness Tier == "Primary-Short"` da origem **que estão no catálogo** têm relevância 1 (são até cinco);
- todo o resto do catálogo tem relevância 0.

As ocupações relacionadas que estão fora do catálogo são descartadas.

- **Salve em** `data/generated/gold.csv`, com as colunas `profile_id, code, rel`.
- **Reporte:**
  - a média, o mínimo e o máximo do número de relacionadas no catálogo por perfil;
  - quantos perfis têm menos de cinco relacionadas.

---

## 9. Etapa 6 — Os cinco sistemas

Regras comuns a todos:
- recebem o perfil e devolvem uma lista ordenada de códigos O\*NET-SOC;
- o catálogo inteiro é candidato, inclusive a própria origem;
- **desempate determinístico** pelo código, em ordem crescente.

### B1 — BM25
- **Documentos:** o texto indexado (sem divisão em trechos).
- **Consulta:** o relato.
- **Pré-processamento** (o mesmo para consulta e documentos):
  - minúsculas;
  - tokens por `re.findall(r"[a-z0-9]+", ...)`;
  - remoção de `ENGLISH_STOP_WORDS`.
- **Ranqueamento:** `rank_bm25.BM25Okapi` com **k1 = 1,2 e b = 0,75**. O padrão da biblioteca é k1 = 1,5, então passe os valores explicitamente.
- **Saída:** as cinco primeiras.
- As notas RIASEC **não** entram.

### B2 — casamento RIASEC
- Calcule a correlação de Pearson entre as seis notas do perfil e as seis notas OI de cada ocupação.
- Ordene de forma decrescente e pegue as cinco primeiras.
- Se uma ocupação tiver variância zero, Pearson fica indefinido: trate como −1 e registre quantos casos houve.

### V-A — molde fixo, sem LLM
- Preencha o molde do Apêndice B (Apêndice ao final deste documento):
  - os seis tipos aparecem em ordem decrescente de nota, com empate pela ordem R, I, A, S, E, C;
  - a intensidade é `high` para nota ≥ 5, `moderate` para 3 ≤ nota < 5 e `low` para nota < 3, usando a nota com ruído sem arredondar.
- Acrescente `Self-description: {relato}`.
- Vetorize o texto e busque no pgvector as cinco primeiras.

### V-B — síntese do perfil + recuperação
- **Síntese:**
  - Modelo: `claude-sonnet-5`, com o prompt do Apêndice C. As notas vão com 1 casa decimal no prompt.
  - **Não defina temperatura** nem nenhum parâmetro de amostragem, e não ative raciocínio estendido. Use `max_tokens = 400`.
  - Nenhum cache de prompt e nenhuma Batch API: a latência é medida chamada a chamada.
  - A síntese é **gerada uma única vez por perfil e por condição de ruído** (as notas mudam entre condições) e salva em `data/generated/sinteses_{cond}.jsonl`, com latência e tokens.
  - Registre o número de palavras da síntese, mas não rejeite nenhuma.
- **Recuperação:**
  - Vetorize a síntese e busque as **20** mais próximas no pgvector.
  - Salve as 20 em ordem: elas são os candidatos de V-C.
  - A saída de V-B são as cinco primeiras.

### V-C — reordenação
- **Entrada:**
  - a síntese de V-B;
  - os 20 candidatos de V-B, numerados de 1 a 20, cada um com `Title: Description`. Só título e descrição, sem tarefas.
- **Modelo e prompt:** `claude-sonnet-5`, prompt do Apêndice D, temperatura padrão, `max_tokens = 50`.
- **10 execuções independentes** por perfil e por condição, sobre os mesmos 20 candidatos.
- **Leitura da resposta:**
  - Extraia os inteiros. A resposta é válida se tiver exatamente cinco números **distintos** entre 1 e 20.
  - Se for inválida, **reenvie uma vez**.
  - Se continuar inválida, use **a lista de V-B** (as cinco primeiras) nessa execução e marque `fallback = true`.
  - Conte e reporte os reenvios e os fallbacks.
- **Erros de transporte:** use nova tentativa com espera exponencial. Isso não conta como reenvio de formato.
- **Concorrência:** no máximo 4 chamadas simultâneas, valor que fica registrado em `config.yaml`. A latência é medida em cada chamada individual.

Volume aproximado de chamadas ao Sonnet:
- síntese: 198 × 2 = 396;
- reordenação: 198 × 2 × 10 = 3.960;
- mais as do conjunto de desenvolvimento.

São cerca de 10 milhões de tokens de entrada no total. Confirme o preço antes de rodar.

---

## 10. Etapa 7 — Desenvolvimento, ajuste e travamento

1. Rode o pipeline completo sobre os 30 perfis de desenvolvimento (σ = 1,0): relatos, os cinco sistemas, métricas, tempo e custo. **Isso também valida que tudo funciona de ponta a ponta.**
2. **O que pode ser ajustado:** **apenas** os textos dos prompts A, C e D e o molde B. Modelos, temperatura, níveis de ruído, k, número de candidatos, métricas e testes estão fixados no protocolo e não mudam.
3. **Critério de ajuste:** principalmente a obediência às regras.
   - Relato: 3 a 5 frases, sem títulos, cargos ou termos técnicos, e passando no filtro.
   - Síntese: de 80 a 120 palavras, sem título de ocupação, sem letras RIASEC e sem notas.
   - Reordenação: cinco números válidos.

   Pode-se olhar o nDCG@5 do desenvolvimento, mas não é preciso otimizá-lo.
4. **No máximo duas rodadas de ajuste.** Cada mudança vai para `AJUSTES.md` com o texto anterior, o texto novo, o motivo e as métricas do desenvolvimento antes e depois.
5. **Travamento:**
   - Faça o commit de `config.yaml`, `prompts/`, o código e `AJUSTES.md`.
   - Crie a tag `lock-v1` e registre o hash.
   - O `config.yaml` travado contém:
     - os modelos com IDs exatos e a data de acesso;
     - a revisão do embedding;
     - as sementes, σ, k e a concorrência;
     - os preços por milhão de tokens, com a data e a URL da página de preços de cada fornecedor.
6. **Depois da tag, nada no código, nos prompts ou na configuração muda.** Se for inevitável (um bug que impede a execução, por exemplo), corrija, registre em `DESVIOS.md` com o hash antes e depois e avise o Aderson.

---

## 11. Etapa 8 — Execução da avaliação (depois de `lock-v1`)

1. Sorteio da avaliação, com as substituições, e gabarito.
2. Ruído nas duas condições.
3. Relatos (198) com o Gemini.
4. B1, B2 e V-A nas duas condições (B1 é idêntico nas duas e pode ser calculado uma vez e copiado).
5. V-B: síntese e recuperação nas duas condições.
6. V-C: 10 execuções nas duas condições.
7. Salve todas as listas em `data/generated/rankings.csv`, com as colunas `system, condition, profile_id, run, rank, code` (`run` = 0 para os sistemas determinísticos e de 1 a 10 para V-C).

Faça um commit dos dados gerados ao final, com uma tag `results-v1`.

---

## 12. Etapa 9 — Métricas (implementação exata)

`rel(code)` vem do gabarito do perfil. A lista avaliada sempre tem 5 posições, com i = 1..5.

- **nDCG@5**
  - O ganho é **linear**: DCG@5 = Σ rel_i / log2(i + 1).
  - IDCG@5 é o DCG@5 da lista ideal: [2] seguido de tantos 1 quantas forem as relacionadas no catálogo, até completar 5 posições, e o restante com 0.
  - nDCG@5 = DCG@5 / IDCG@5.
- **P@5** = (número de itens com rel ≥ 1 entre os 5) / 5.
- **AP@5**
  - AP@5 = Σ P@i, somando só nas posições i em que rel_i ≥ 1, dividido por **min(5, R)**.
  - R = 1 + número de relacionadas no catálogo.
  - MAP@5 é a média dos AP@5 sobre os perfis.
- **MRR@5 de origem** = 1 / posição da origem se ela estiver entre as cinco primeiras; caso contrário, 0.
- **V-C:**
  - o valor por perfil de cada métrica é a **média das 10 execuções**;
  - as execuções com fallback entram normalmente, com a lista de V-B.
- **Variação de V-C**, por condição:
  - **Desvio padrão do nDCG@5:** calcule para cada perfil o DP das 10 execuções (ddof = 1) e reporte a média e o máximo entre os perfis.
  - **Sobreposição média das listas:** para cada perfil, faça a média de |A ∩ B| / 5 sobre os 45 pares de execuções; reporte a média entre os perfis.
  - **Listas idênticas:** reporte a proporção de perfis em que as 10 listas são idênticas, considerando a ordem.

Os exemplos obrigatórios de teste estão na Seção 16.

---

## 13. Etapa 10 — Estatística

- **Descritivas:** para cada sistema, cada condição e cada métrica, calcule média, desvio padrão e mediana sobre os 198 perfis.
- **Inferencial:** **só** as quatro comparações, **só** na condição σ = 1,0, sobre o nDCG@5 por perfil. A diferença é sempre o sistema mais elaborado menos o mais simples:

| Comparação | d = | Hipótese |
|---|---|---|
| (a) | V-B − V-A | H1 |
| (b) | V-C − V-B | H2 |
| (c) | V-C − B1 | H3 |
| (d) | V-C − B2 | H4 |

- **Teste:** `scipy.stats.wilcoxon(x_mais_elaborado, x_mais_simples, alternative="two-sided", zero_method="wilcox")`. É **bilateral** e descarta as diferenças nulas.
- **Reporte, para cada comparação:**
  - média de d;
  - mediana de d;
  - n total;
  - n de diferenças não nulas;
  - estatística W;
  - p bruto;
  - p ajustado por Bonferroni = min(1, 4p).
- **Decisão:** "favorece o sistema mais elaborado" exige **média de d ≥ 0,05 e p bruto < 0,0125**. Se isso não acontecer, o resultado é "não favorece".
  - Quando d for negativo e significativo, registre apenas o sentido. A interpretação fica para a redação.
  - Ausência de significância **não** significa equivalência.
- **Condição de sensibilidade (σ = 0,5):** só descritiva, sem teste.
- **Não acrescente** outros testes, intervalos, tamanhos de efeito nem comparações. Fazer isso fere o protocolo.

---

## 14. Etapa 11 — Tempo de resposta e custo

**Tempo por consulta**, do recebimento do perfil à entrega da lista final, sem a indexação do catálogo. Use `time.perf_counter()`.

| Sistema | O que entra no tempo |
|---|---|
| B1 e B2 | o cálculo da lista |
| V-A | o preenchimento do molde + o embedding do texto + a busca no pgvector |
| V-B | a latência da síntese **na geração original** + o embedding + a busca |
| V-C | o tempo de V-B + a latência da reordenação; o valor de V-C é a média das 10 execuções (inclua o reenvio, quando houver) |

Reporte média, mediana e percentil 95 por sistema, na condição σ = 1,0. A condição de sensibilidade vai em anexo.

**Custo por consulta**, com os tokens efetivamente cobrados que a API devolve no `usage`, ao preço registrado no `config.yaml`:
- **B1, B2 e V-A:** custo zero de API.
- **V-B:** custo da síntese.
- **V-C:** custo da síntese + custo médio de uma reordenação (incluindo os reenvios).

Reporte média por consulta e total do experimento.

**Custo de construção do conjunto** é reportado à parte: o custo dos relatos do Gemini (incluindo as regerações e os tokens de raciocínio, se forem cobrados).

**Ambiente:** registre a máquina (CPU/GPU, RAM), o sistema operacional e se o embedding rodou em CPU ou GPU.

---

## 15. Pacote de resultados (o que deve voltar para a redação do TCC)

O pacote é a pasta `results/` com **`RESULTADOS.md`** seguindo exatamente o modelo abaixo, mais os CSVs. Use 3 casas decimais e ponto decimal (a conversão para vírgula é feita na redação). O Aderson vai trazer esta pasta para a conversa em que o TCC está sendo escrito.

```markdown
# RESULTADOS — TCC perfis sintéticos

## 0. Identificação
- Repositório: <url ou caminho> · commit lock-v1: <hash> · commit results-v1: <hash>
- Data de execução: <data>
- Modelos (ID devolvido pela API e data de acesso): Sonnet: <...> · Gemini: <...>
- Embedding: all-mpnet-base-v2, revisão <sha>, sentence-transformers <versão>
- Preços usados (USD/1M tokens, entrada/saída, data, URL): Sonnet <...> · Gemini <...>
- O*NET: 31.0, download em <data>, SHA-256 <...>
- Máquina: <...>

## 1. Catálogo
- Ocupações em occupation_data: <n> · excluídas por critério: sem descrição <n>, sem tarefas <n>, sem RIASEC completo <n>, sem relacionadas <n>
- Catálogo final: <n>
- Elegíveis por tipo predominante: R <n>, I <n>, A <n>, S <n>, E <n>, C <n>
- Ocupações que exigiram divisão em trechos: <n> (<%>) · trechos por ocupação: média <x>, máx <n>
- Enunciados acima de 384 tokens: <n> · textos de perfil acima de 384 tokens: <n>

## 2. Conjunto de avaliação
- Perfis por tipo: R <n> ... C <n> · redistribuição por falta de elegíveis: <sim/não, detalhes>
- Substituições por falha no filtro (dev / avaliação): <n> / <n> (lista em substituicoes.csv)
- Regerações de relato (tentativas 2 e 3): <n>
- Relatos: frases média <x> (mín–máx), palavras média <x>
- Sobreposição relato × texto da origem: média <x>, DP <x>, mediana <x>, mín <x>, máx <x>
- Relacionadas no catálogo por perfil: média <x>, mín <n>, máx <n>; perfis com < 5: <n>

## 3. Desempenho — condição principal (σ = 1,0), n = 198
| Sistema | nDCG@5 média (DP) [mediana] | P@5 | MAP@5 | MRR@5 origem |
| B1 | | | | |
| B2 | | | | |
| V-A | | | | |
| V-B | | | | |
| V-C | | | | |

## 4. Comparações (σ = 1,0, nDCG@5)
| Comp. | d = | média d | mediana d | n não nulos | W | p bruto | p Bonferroni | Decisão |
| (a) H1 | V-B − V-A | | | | | | | |
| (b) H2 | V-C − V-B | | | | | | | |
| (c) H3 | V-C − B1 | | | | | | | |
| (d) H4 | V-C − B2 | | | | | | | |

## 5. Sensibilidade (σ = 0,5) — descritivo
(mesma tabela da seção 3) + linha com a diferença de cada sistema entre σ = 0,5 e σ = 1,0 no nDCG@5

## 6. Variação da reordenação (V-C)
| Condição | DP médio nDCG@5 | DP máx | sobreposição média | % perfis com 10 listas idênticas | reenvios | fallbacks |

## 7. Tempo e custo (σ = 1,0)
| Sistema | tempo média (s) | mediana | p95 | custo médio/consulta (USD) |
- Custo total do motor no experimento: <USD> · custo de construção do conjunto (Gemini): <USD>

## 8. Ajuste e desvios
- Resumo do AJUSTES.md (o que mudou em cada prompt/molde e por quê)
- Resumo do DESVIOS.md (ou "nenhum desvio")

## 9. Exemplos ilustrativos (para a discussão, sem análise adicional)
- 2 perfis da avaliação, escolhidos pela semente <seed_examples> (não escolhidos a dedo): ocupação de origem, notas, relato, síntese de V-B e o top-5 de cada sistema com a relevância de cada item.
```

CSVs que acompanham o pacote:
- `per_profile_metrics.csv`: sistema, condição, perfil e as quatro métricas.
- `vc_runs.csv`: perfil, condição, execução, nDCG@5 e fallback.
- `comparisons.csv`
- `timing_cost.csv`
- `substituicoes.csv`
- `catalog_summary.csv`

Copie também para `results/prompts_travados/` os **textos finais travados** dos prompts A, C e D e do molde B. Se mudaram no ajuste, os Apêndices A–D do TCC serão atualizados a partir deles.

---

## 16. Testes obrigatórios (pytest)

- **Métricas, exemplo 1.** Gabarito: origem O e relacionadas R1–R5, todas no catálogo. Lista [R1, X, O, Y, R2], com rel = [1, 0, 2, 0, 1].
  - DCG = 2,386853 e IDCG = 3,948459.
  - nDCG@5 = **0,604502**
  - P@5 = **0,6**
  - AP@5 = (1 + 2/3 + 3/5) / 5 = **0,453333**
  - MRR@5 de origem = **0,333333**
- **Métricas, exemplo 2.** Só 2 relacionadas no catálogo (R = 3). Lista [X, R1, Y, Z, O], com rel = [0, 1, 0, 0, 2].
  - IDCG da lista ideal [2, 1, 1, 0, 0] = 3,130930.
  - nDCG@5 = **0,448632**
  - P@5 = **0,4**
  - AP@5 = (1/2 + 2/5) / 3 = **0,300000**
  - MRR@5 de origem = **0,2**
- **Lista perfeita:** nDCG@5 = 1. **Lista sem relevantes:** todas as métricas valem 0.
- **Sorteio:**
  - o desenvolvimento tem 5 por tipo e a avaliação tem 33 por tipo;
  - não há interseção entre os conjuntos;
  - a mesma semente produz o mesmo resultado.
- **Filtro de título:**
  - "Registered Nurses" rejeita um relato com "nurse";
  - stopwords e palavras com menos de 3 letras não disparam o filtro.
- **Molde de V-A:**
  - os limites de intensidade (4,99 → moderate; 5,0 → high; 2,99 → low; 3,0 → moderate);
  - a ordem em caso de empate.
- **Parser da reordenação:**
  - "7, 2, 15, 1, 9" é válido;
  - menos de 5 números, números repetidos ou números fora de 1–20 são inválidos.
- **B2:** um perfil igual ao de uma ocupação dá Pearson = 1 para ela.
- **BM25:** confirme que o objeto foi criado com k1 = 1,2 e b = 0,75.
- **Ruído:** os valores ficam dentro de [1, 7] e a mesma semente produz o mesmo resultado.

---

## 17. Pare e avise o Aderson se…

- `claude-sonnet-5` ou `gemini-3.8-flash` não estiver disponível, ou responder com outro modelo. **Não troque de modelo por conta própria**: o modelo faz parte do protocolo e aparece no TCC.
- Os arquivos do O\*NET 31.0 tiverem estrutura diferente da descrita aqui, ou as notas OI não estiverem entre 1 e 7.
- Algum tipo RIASEC tiver menos de 38 elegíveis (aplique a regra da Seção 6, mas avise).
- Mais de 10% das origens precisarem de substituição, ou mais de 5% das reordenações caírem em fallback.
- O custo estimado com os preços vigentes passar de US$ 50.
- Algo depois de `lock-v1` precisar mudar.
- Qualquer resultado parecer impossível. Por exemplo, B2 com nDCG@5 perto de 1 na condição σ = 1,0 indica que o ruído não foi aplicado.

## 18. Não fazer

- Não acrescentar sistemas, métricas, testes estatísticos, condições ou análises que não estejam aqui.
- Não traduzir nada para o português nem usar a CBO.
- Não usar índice aproximado no pgvector.
- Não definir temperatura nem outros parâmetros de amostragem. Não usar cache de prompt nem Batch API.
- Não regerar relatos ou sínteses já salvos sem registrar.
- Não usar código, dados ou prompts da Career Angel.
- Não versionar chaves de API.

---

## Apêndice — Prompts e molde (versões iniciais, iguais aos Apêndices A–D do TCC)

Os textos abaixo devem ser copiados para `prompts/`. Os marcadores entre chaves são substituídos pelo código.

### A — Geração dos relatos (Gemini) — `prompts/A_relato.txt`

```
You are helping build an evaluation set for an occupation recommender. Write a short
self-description, in the first person, of a person who would enjoy the work activities
listed below, as if this person were telling a career counselor what they like to do.

Rules:
1. Write 3 to 5 sentences in plain, everyday English.
2. Describe what the person likes to do, not a job: do not mention any occupation title,
   job title, profession, industry, or employer.
3. Do not reuse technical terms from the activity list; describe the activities in
   ordinary words.
4. Do not mention education, degrees, certifications, salary, or years of experience.
5. Output only the self-description, with no title or explanation.

Work activities:
{task_statements}
```

### B — Molde de V-A (sem LLM) — `prompts/B_molde_va.txt`

Os seis tipos aparecem em ordem decrescente de nota (empate pela ordem R, I, A, S, E, C). A intensidade é `high` para nota ≥ 5, `moderate` para 3 ≤ nota < 5 e `low` para nota < 3. Os nomes dos tipos são Realistic, Investigative, Artistic, Social, Enterprising e Conventional.

```
Interest profile, from strongest to weakest:
{type_1} interests: {level_1}; {type_2} interests: {level_2};
{type_3} interests: {level_3}; {type_4} interests: {level_4};
{type_5} interests: {level_5}; {type_6} interests: {level_6}.

Self-description: {self_description}
```

### C — Síntese do perfil (Sonnet, V-B) — `prompts/C_sintese.txt`

```
You will receive a person's vocational interest scores on the six RIASEC dimensions
(scale from 1 to 7) and a short self-description written by the person.

Write one paragraph in English, of 80 to 120 words, describing this person's interests:
the kinds of activities they prefer, the problems they like to work on, and the work
settings in which they would feel comfortable. Combine the scores and the
self-description into a single coherent description. Do not mention any occupation
title or job title, and do not mention the RIASEC letters or the scores themselves.
Output only the paragraph.

RIASEC scores:
Realistic: {R}   Investigative: {I}   Artistic: {A}
Social: {S}   Enterprising: {E}   Conventional: {C}

Self-description:
{self_description}
```

### D — Reordenação (Sonnet, V-C) — `prompts/D_reordenacao.txt`

```
Below is a description of a person's interests and a numbered list of 20 candidate
occupations, each with its title and description.

Select the 5 occupations that best match this person's interests and rank them from
best to worst match. Consider only the fit between the person's interests and the
work described; do not consider salary, job demand, or education requirements.
Answer only with the 5 candidate numbers, in order, separated by commas
(for example: 7, 2, 15, 1, 9).

Person's interests:
{profile_text}

Candidates:
1. {title_1}: {description_1}
...
20. {title_20}: {description_20}
```
