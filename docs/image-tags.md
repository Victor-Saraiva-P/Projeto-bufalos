# Tags de Curadoria de Imagens

Este documento define as tags de curadoria usadas para caracterizar as imagens do projeto.

O objetivo dessas tags é apoiar a análise dos testes de segmentação e, indiretamente, ajudar a identificar condições de imagem que podem afetar a predição de peso dos búfalos.

## Regra Geral

- As tags descrevem a qualidade e a dificuldade da imagem.
- Uma imagem pode ter mais de uma tag.
- A tag `ok` deve ser usada apenas quando nenhuma tag de problema se aplica.
- Imagem sem tag deve ser tratada como `nao_revisada`, isto é, ainda não foi avaliada manualmente.

## Conjunto Fechado de Tags

- `ok`
- `multi_bufalos`
- `cortado`
- `angulo_extremo`
- `ocluido`

## Glossário

### `ok`

Imagem adequada para análise, sem problema relevante de enquadramento ou visibilidade.

Critério prático:
- um único búfalo como sujeito principal
- corpo majoritariamente visível
- sem corte relevante
- sem oclusão relevante
- sem ângulo que distorça fortemente a percepção corporal

### `multi_bufalos`

A imagem contém mais de um búfalo visível no frame.

Quando usar:
- há dois ou mais búfalos na cena
- outro búfalo compete com o sujeito principal
- existe risco de confundir a segmentação ou a interpretação do porte corporal

Observação:
- mesmo que apenas um búfalo seja o alvo principal, a presença de outros animais já justifica a tag

### `cortado`

Parte relevante do corpo do búfalo ficou fora do enquadramento da imagem.

Quando usar:
- cabeça saiu do frame
- patas não aparecem por corte do enquadramento
- traseiro, dorso ou cauda ficaram fora da imagem

Regra prática:
- use `cortado` quando a informação sumiu por causa do enquadramento

### `angulo_extremo`

A foto foi feita em um ângulo que dificulta a leitura do volume corporal ou do contorno do animal.

Quando usar:
- foto muito de trás
- foto muito de frente
- foto muito de cima ou muito de baixo
- perspectiva forte que deforma comprimento, altura ou largura aparentes

Regra prática:
- use `angulo_extremo` quando a geometria visual do animal fica pouco comparável às imagens laterais mais úteis para segmentação e peso

### `ocluido`

Parte relevante do búfalo está visível no frame, mas foi encoberta por outro elemento da cena.

Quando usar:
- cerca ou grade passando na frente do corpo
- outro búfalo cobrindo parte do animal
- tronco, poste, pessoa ou estrutura ocultando regiões do corpo

Regra prática:
- use `ocluido` quando a informação está dentro do enquadramento, mas algo na frente a esconde

## Diferença Entre `cortado` e `ocluido`

- `cortado`: a parte do corpo ficou fora da imagem
- `ocluido`: a parte do corpo está dentro da imagem, mas algo a tampou

Exemplos:
- cabeça fora do frame: `cortado`
- perna atrás da cerca: `ocluido`
- foto com cabeça fora do frame e corpo atrás da grade: `cortado` e `ocluido`

## Uso Recomendado na Curadoria

- Marque `ok` apenas quando a imagem não tiver nenhuma ressalva relevante.
- Se houver qualquer problema importante, use apenas as tags de problema aplicáveis.
- Não trate ausência de tag como imagem boa; trate como imagem ainda não revisada.
