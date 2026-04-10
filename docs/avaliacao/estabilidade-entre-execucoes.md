# Estabilidade Entre Execucoes

Este documento registra a leitura dos resultados de estabilidade da segmentacao bruta a partir dos graficos gerados no notebook 05.

Arquivos usados como evidencia:

- `graficos_notebook_05/segmentacao_bruta_cv_execucoes_auprc_por_modelo.png`
- `graficos_notebook_05/segmentacao_bruta_cv_execucoes_soft_dice_por_modelo.png`
- `graficos_notebook_05/segmentacao_bruta_cv_execucoes_brier_score_por_modelo.png`

## Pergunta

Os modelos variam muito entre execucoes repetidas?

## Resposta curta

Nao. Os resultados indicam que os modelos sao altamente estaveis entre execucoes.

O `cv_execucoes` observado e nulo ou extremamente proximo de zero para a maior parte dos modelos. As variacoes nao sustentam a ideia de instabilidade pratica do pipeline.

## Leitura por metrica

### `AUPRC`

No grafico de `cv_execucoes` para `AUPRC`, quase todos os modelos aparecem com `0.000000` na precisao exibida.

As excecoes visiveis sao:

- `u2net`: `0.000197`
- `u2net_human_seg`: `0.000134`
- `silueta`: `0.000073`

Leitura:

- a variacao existe, mas e muito pequena;
- mesmo no pior caso observado, o coeficiente de variacao continua extremamente baixo.

### `Soft Dice`

No grafico de `cv_execucoes` para `Soft Dice`, o comportamento continua altamente estavel.

As maiores variacoes visiveis sao:

- `u2net`: `0.000052`
- `u2net_human_seg`: `0.000028`
- `silueta`: `0.000025`

Os demais modelos aparecem como `0.000000` na precisao mostrada pelo grafico.

Leitura:

- a ordem de grandeza da variacao e ainda menor do que em `AUPRC`;
- isso reforca a interpretacao de alta repetibilidade entre execucoes.

### `Brier Score`

No grafico de `cv_execucoes` para `Brier Score`, a maioria dos modelos segue com variacao nula na precisao exibida, mas aparecem alguns valores residuais adicionais.

Valores visiveis:

- `silueta`: `0.000069`
- `u2net`: `0.000011`
- `u2net_human_seg`: `0.000004`
- `u2netp`: `0.000001`
- `isnet-anime`: `0.000001`

Leitura:

- mesmo quando o grafico mostra variacao nao nula, os valores continuam muito pequenos;
- a metrica nao sugere instabilidade operacional relevante.

## Conclusao

A afirmacao central e verdadeira:

- os modelos nao variam muito entre execucoes;
- os resultados observados apontam alta estabilidade.

Mas a formulacao precisa precisa de um ajuste:

- nao e correto dizer que todos os modelos produzem resultados identicos em todas as metricas;
- o correto e dizer que a maioria aparece com `cv_execucoes` igual a zero na precisao exibida, e que os poucos casos com variacao nao nula ainda ficam em magnitudes muito pequenas.

Em termos praticos, a conclusao defensavel e:

- o pipeline de segmentacao bruta apresenta alta repetibilidade entre execucoes;
- a instabilidade entre repeticoes nao aparece como um fator dominante para interpretar os resultados dos modelos nesta etapa;
- quando ha variacao, ela se concentra principalmente em `u2net`, `u2net_human_seg` e `silueta`, com pequenos residuos adicionais em `Brier Score` para `u2netp` e `isnet-anime`.

## Formula sugerida para documentacao futura

Uma formulacao segura para reutilizar em texto do projeto e:

> Os graficos de `cv_execucoes` indicam que os modelos sao altamente estaveis entre repeticoes. A maior parte apresenta variacao nula na precisao exibida, e os poucos casos com variacao nao nula permanecem em magnitudes muito pequenas, sem evidenciar instabilidade pratica do pipeline.
