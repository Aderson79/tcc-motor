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
- **Situação:** o Aderson tomou ciência em 16/11/2026 e a regra foi aplicada no sorteio da avaliação
  (23 perfis A; as 10 vagas restantes ficaram com R 5, C 2, E 2 e I 1).

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
- **Hash antes:** `e8aff24` (`lock-v1`). **Hash depois:** `676d187` (`results-v1`).
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
