# DIÁRIO DO EXPERIMENTO — registro cronológico do que foi feito

Este arquivo registra, em ordem, tudo o que foi executado, decidido e observado, para que o texto do TCC
descreva exatamente o que o experimento fez. Os desvios do protocolo ficam detalhados em `DESVIOS.md`; o
ajuste dos prompts, em `AJUSTES.md`; cada chamada a LLM, em `logs/calls.jsonl`. Aqui fica a narrativa.

Horários no fuso de Brasília (UTC−3).

## 16/11/2026

### Estado herdado (commits `2d692a0` e `bcf95b5`, feitos em outra máquina, Linux)
- Código completo do motor: catálogo, embeddings, sorteio, perfis, gabarito, cinco sistemas, métricas,
  estatística e relatório; 16 testes obrigatórios.
- Já executado naquela máquina: catálogo (923 ocupações), índice de embeddings e sorteio do conjunto de
  desenvolvimento (`data/generated/sample_dev.csv`, 30 ocupações, `seed_dev = 20261116`).
- Nenhuma chamada a LLM havia sido feita.
- Desvio D1 já registrado: o tipo Artístico tem só 28 elegíveis (menos que os 38 necessários).

### Montagem do ambiente nesta máquina (Windows 10 Pro, AMD Ryzen 5 3400G, 16 GB RAM, sem GPU utilizável)
- Python 3.13 em ambiente virtual fora do OneDrive (`C:\Users\User\.venvs\tcc-motor`), com as versões exatas
  do `requirements.lock` (entre elas: torch 2.15.0, sentence-transformers 6.3.0, pandas 3.1.1,
  anthropic 2.8.0, google-genai 3.3.0, rank-bm25 0.2.2, scipy 1.18.1, pgvector 0.5.1, psycopg 3.3.9).
  Os pacotes `nvidia-*`/`cuda-*` do lock são só de Linux e não foram instalados; o embedding roda em CPU.
- O\*NET 31.0 baixado de novo de `https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip`; o SHA-256
  confere com o registrado (`55033fc6…3987cd`).
- **Banco (desvio D2):** a máquina não tem Docker nem WSL. PostgreSQL 16.15 + pgvector 0.8.6 instalados do
  conda-forge (micromamba 2.10.0) em `C:\Users\User\.tcc-pg`, instância própria na porta 54329, mesma DSN.
- `python -m tcc.catalog`: mesmos números da máquina anterior — 1.016 linhas em `occupation_data`, 93
  excluídas (sem tarefas, sem RIASEC completo e sem relacionadas; nenhuma sem descrição), catálogo final
  de 923; elegíveis R 388, I 112, A 28, S 129, E 100, C 166.
- `pytest`: 16 testes passando.
- `python -m tcc.embed`: índice refeito nesta máquina, em CPU (resultado registrado abaixo quando terminar).

### Verificação dos modelos e ocorrências
- Primeira tentativa de `python -m tcc.check`: a chamada ao `gemini-3.8-flash` ficou presa sem resposta. Causa:
  a conta do Gemini estava sem saldo (o Aderson pôs saldo em seguida) e o SDK `google-genai` não tem tempo
  limite por padrão e repete tentativas por conta própria, sem registro. Chamadas diretas à API alternaram
  entre 503 ("high demand"), espera acima de 100 s e resposta normal em 2 s.
- **Correção no código (`src/tcc/llm.py`):** cliente Gemini com tempo limite de 60 s por chamada e sem as
  tentativas internas do SDK; as novas tentativas ficam no laço do próprio projeto, que registra cada uma em
  `logs/calls.jsonl` (espera exponencial, no máximo 8 tentativas).
- `check` refeito: `gemini-3.8-flash` e `claude-sonnet-5` responderam identificando-se com esses mesmos IDs.
- **Correção no código (`src/tcc/report.py`):** leitura de CPU e RAM também no Windows (antes só Linux).

### Preços conferidos nas páginas oficiais (16/11/2026) e gravados no `config.yaml`
- `claude-sonnet-5`: US$ 2,00 entrada / US$ 10,00 saída por milhão de tokens
  (https://platform.claude.com/docs/en/about-claude/pricing).
- `gemini-3.8-flash`, nível pago Standard: US$ 0,75 entrada / US$ 3,75 saída (tokens de raciocínio cobrados
  como saída), vigente até 31/12/2026 (https://ai.google.dev/gemini-api/docs/pricing).

### Troca dos papéis dos modelos (desvio D3, decidido pelo Aderson)
- Saldos informados: US$ 5 na API da Anthropic e R$ 170 na API do Gemini. A estimativa para síntese +
  reordenação com o Sonnet era de US$ 13–20, acima do saldo.
- Decisão: **o Sonnet (`claude-sonnet-5`) passa a escrever os relatos; o Gemini (`gemini-3.8-flash`) passa
  a fazer a síntese (V-B) e a reordenação (V-C).** Feita antes de qualquer relato, síntese ou reordenação
  ser gerada e antes do `lock-v1`.
- Teste que motivou retirar o limite de saída no Gemini: com `maxOutputTokens = 50`, a resposta veio vazia
  (`finishReason = MAX_TOKENS`, 47 tokens de raciocínio consumiram o limite); com 400, a resposta veio
  correta, mas com 377 tokens de raciocínio. Por isso síntese e reordenação rodam no Gemini sem limite de
  saída e sem orçamento de raciocínio definido (configuração padrão).
- Relatos no Sonnet: sem temperatura, `thinking` desativado, `max_tokens = 400`.
- Mudanças no código: função `llm.call` que escolhe o cliente pelo nome do modelo; tokens de raciocínio
  gravados junto de cada síntese e reordenação e somados à saída no cálculo do custo; `config.yaml` com os
  novos modelos por papel; rótulos do relatório por papel, e não por fornecedor.
- `check` refeito depois da troca: os dois modelos responderam com os IDs esperados; 16 testes passando.
- **O texto do TCC precisa refletir isso** (ver "Efeito sobre o TCC" em `DESVIOS.md`, D3).

### Execução do desenvolvimento na configuração trocada (depois desfeita)
- Relatos com o Sonnet: 30 perfis, 42 chamadas (12 rejeições pelo filtro de título), 3 substituições
  (D04, D27, D29), todos com 4 ou 5 frases; custo de ~US$ 0,16.
- Primeira execução dos sistemas falhou na síntese com "Cannot send a request, as the client has been
  closed": quatro threads criavam o cliente Gemini ao mesmo tempo e o descarte das duplicatas fechava a
  conexão. **Correção em `src/tcc/llm.py`:** criação do cliente protegida por lock. As 3 sínteses já salvas
  foram mantidas.
- Segunda execução: 30 sínteses e 278 das 300 reordenações no Gemini. Medido na reordenação: ~1.250 tokens de
  entrada, ~15 de resposta e **~3.560 de raciocínio por chamada**, latência mediana de 27 s, custo de
  ~US$ 0,014 por chamada; 6 erros 504 (tempo esgotado no servidor). Projeção para as 3.960 reordenações da
  avaliação: ~US$ 57 e 7–8 horas.
- **Decisão do Aderson: desfazer a troca** e voltar ao desenho original; saldo da Anthropic reforçado em
  US$ 20 (total de US$ 25). A execução foi interrompida e tudo o que ela gerou foi movido para
  `data/generated/_troca_desfeita/` (não usado). Gasto do Gemini nessa tentativa: ~US$ 4.

### Desenvolvimento no desenho original (Gemini nos relatos; Sonnet na síntese e na reordenação)
- `config.yaml` de volta ao protocolo: `gemini-3.8-flash` nos relatos (configuração padrão);
  `claude-sonnet-5` na síntese (`max_tokens = 400`) e na reordenação (`max_tokens = 50`), `thinking`
  desativado, sem temperatura.
- Relatos refeitos com o Gemini a partir do mesmo sorteio (`sample_dev.csv`): 30 relatos, todos com
  4 frases, média de 94 palavras; 2 regerações pelo filtro de título; **nenhuma substituição**.
- Ruído (σ = 1,0, `seed = 20261119`) e gabarito: 5 relacionadas no catálogo em todos os 30 perfis.
- **Rodada 0** (prompts iniciais): nDCG@5 médio B1 0,087 · B2 0,190 · V-A 0,248 · V-B 0,234 · V-C 0,384.
  Problemas de obediência: 8 de 30 sínteses acima de 120 palavras; 20 fallbacks em 300 reordenações (6,7%,
  acima do limite de 5% da Seção 17), concentrados em 3 perfis, por respostas que começavam com explicação.
- **Rodada 1 de ajuste** (prompts C e D, textos em `AJUSTES.md`): sínteses todas entre 103 e 117 palavras;
  7 fallbacks em 300 (2,3%), todos do perfil D12. nDCG@5 médio: V-B 0,200 · V-C 0,380 (B1, B2 e V-A iguais).
- Não houve rodada 2.
- Tempo por consulta no desenvolvimento (média): B1 0,017 s · B2 0,001 s · V-A 0,41 s · V-B 4,39 s ·
  V-C 5,68 s. Custo médio por consulta: V-B US$ 0,0034 · V-C US$ 0,0080.
- Gasto acumulado até o travamento: Anthropic ~US$ 3,20 · Gemini ~US$ 4,70 (quase tudo da troca desfeita).

### Travamento
- `models_access_date` = 16/11/2026 no `config.yaml`. Commit com código, prompts, configuração, `AJUSTES.md`,
  `DESVIOS.md`, este diário e os dados do desenvolvimento; tag `lock-v1` (hash registrado abaixo).
- Hash da tag `lock-v1`: `e8aff242918b4fea435e481f04a4d4adb7799e8d`.

### Avaliação (depois de `lock-v1`, ainda em 16/11/2026)
- O Aderson decidiu executar a avaliação no mesmo dia, em vez de 17–18/11, e reforçou o saldo da Anthropic
  em mais US$ 5 (total de US$ 30).
- **Sorteio (`seed_eval = 20261117`):** 198 ocupações. Como previsto em D1, o tipo A entrou com as 23
  restantes; as 10 vagas que faltavam foram sorteadas de modo uniforme entre as elegíveis restantes dos
  demais tipos: 47-4099.03, 17-2171.00, 51-9161.00, 49-9051.00 e 47-5012.00 (R); 23-1021.00 e 13-2022.00
  (C); 11-3111.00 e 27-3031.00 (E); 29-2011.02 (I).
- **Relatos (Gemini):** 198 relatos; 2 substituições por três falhas no filtro de título — P098
  (31-2021.00 → 25-3021.00, palavra "physical") e P105 (25-2059.01 → 25-2022.00, palavra "physical").
  As duas substitutas são do mesmo tipo das descartadas.
- **Composição final por tipo:** R 38, I 34, A 23, S 33, E 35, C 35.
- **Ruído:** `scores_main.csv` (σ = 1,0, semente 20261120) e `scores_sens.csv` (σ = 0,5, semente 20261121).
- **Gabarito (`gold.csv`), construído antes de executar os sistemas:** 5 relacionadas no catálogo em todos
  os 198 perfis.
- **Correção no relatório depois do travamento (desvio D4):** o `report.py` passou a ignorar as chamadas de
  relato feitas ao Sonnet na troca desfeita, que continuam no log. Não afeta listas, métricas nem tempos.
- **Execução dos cinco sistemas** nas duas condições: 396 sínteses e 3.960 reordenações com o
  `claude-sonnet-5` (o ID devolvido pela API foi sempre esse). Nenhum texto de perfil passou de 384 tokens.
  Reordenação: σ = 1,0 sem reenvios nem fallbacks; σ = 0,5 com 3 reenvios e 2 fallbacks em 1.980 execuções.
  Sínteses: todas entre 99 e 120 palavras, exceto uma de 121 palavras na condição σ = 0,5.
- **Resultados (σ = 1,0, n = 198), nDCG@5 médio:** B1 0,120 · B2 0,157 · V-A 0,231 · V-B 0,198 · V-C 0,384.
- **Comparações (Wilcoxon bilateral, Bonferroni, critério: média de d ≥ 0,05 e p < 0,0125):**
  - (a) H1, V-B − V-A: média −0,033, p = 0,147 → **não favorece** (a síntese não melhorou a recuperação).
  - (b) H2, V-C − V-B: média +0,187, p = 2,1 × 10⁻¹⁸ → favorece V-C.
  - (c) H3, V-C − B1: média +0,264, p = 1,6 × 10⁻¹⁷ → favorece V-C.
  - (d) H4, V-C − B2: média +0,227, p = 1,7 × 10⁻¹⁵ → favorece V-C.
- **Sensibilidade (σ = 0,5), nDCG@5 médio:** B1 0,120 · B2 0,360 · V-A 0,234 · V-B 0,207 · V-C 0,384. Só o B2
  muda de forma relevante (+0,203), como esperado, por depender apenas das notas.
- **Tempo médio por consulta (σ = 1,0):** B1 0,016 s · B2 0,001 s · V-A 0,40 s · V-B 4,28 s · V-C 5,50 s.
- **Custo:** motor na avaliação US$ 19,36 (V-B US$ 0,0035 e V-C US$ 0,0080 por consulta); construção do
  conjunto de avaliação (relatos do Gemini) US$ 1,57.
- **Pacote de resultados** em `results/` (`RESULTADOS.md`, CSVs e `prompts_travados/`); commit com a tag
  `results-v1`.
- Hash da tag `results-v1`: `676d1872667035e61d9ec6a4aa15d7966f13bb16`.

### Acertos de documentação depois de `results-v1` (16/11/2026)
- `main` e as tags `lock-v1` e `results-v1` enviados ao GitHub (repositório público).
- `DESVIOS.md`: situação do D1 atualizada (ciência do Aderson) e hash "depois" do D4 preenchido.
- `results/RESULTADOS.md`: hash do `results-v1` gravado na seção 0 e os mesmos dois acertos na cópia do
  `DESVIOS.md` da seção 8. Editado à mão, sem regerar o relatório; nenhum número mudou. Esses acertos estão
  num commit posterior à tag `results-v1`, que continua apontando para `676d187`.

### Reescrita das mensagens de commit (16/11/2026)
- A pedido do Aderson, o histórico do Git foi reescrito para deixar as mensagens de commit mais
  explicativas e a autoria uniforme. Mudou **apenas** o que identifica cada commit, não o conteúdo:
  - mensagens reescritas e sem a linha automática de coautoria da ferramenta (Claude Code) usada no
    desenvolvimento;
  - os dois primeiros commits, feitos num ambiente remoto com identidade genérica (`tcc-motor@localhost`) e
    assinatura que o GitHub mostrava como "Unverified", passaram a ter o Aderson como autor;
  - os três commits de acerto de documentação posteriores a `results-v1` foram reunidos em um só;
  - as datas de autoria e de commit foram preservadas nos quatro primeiros commits.
- Os hashes dos commits mudaram, e as tags foram recriadas nos commits equivalentes:
  - `lock-v1`: antes `e2d8076`, agora `e8aff242918b4fea435e481f04a4d4adb7799e8d`;
  - `results-v1`: antes `7f54111`, agora `676d1872667035e61d9ec6a4aa15d7966f13bb16`.
  Os hashes antigos não haviam sido repassados a ninguém. Este diário e os demais documentos citam os novos.
- **Conferência de que o conteúdo não mudou:** o hash da árvore de arquivos depende só do conteúdo e é o
  mesmo antes e depois da reescrita:
  - `git rev-parse lock-v1^{tree}` → `76e6c2f1173533c9f8fd54d5cc8541d76974c4e5`;
  - `git rev-parse results-v1^{tree}` → `aeca458cfb81432bd4585967d5fa35477b57284c`.
