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

## Notas de interpretação (não alteram o protocolo; registradas por transparência)
- **Raciocínio do Sonnet:** no `claude-sonnet-5`, omitir o parâmetro `thinking` ativa o raciocínio adaptativo
  por padrão. Como o protocolo manda não ativar raciocínio estendido (e `max_tokens` é 400 e 50), as chamadas
  enviam `thinking={"type": "disabled"}`. Nenhum parâmetro de amostragem é enviado.
- **Tarefas sem tipo:** 418 linhas de `task_statements.csv` têm `Task Type` vazio (nem Core nem Supplemental).
  Elas foram mantidas: o texto indexado e o prompt A usam todas as tarefas da ocupação, na ordem do arquivo.
- **Desvio padrão descritivo:** amostral (ddof = 1).
- **Python:** 3.13 (o protocolo pede 3.11 ou superior).
