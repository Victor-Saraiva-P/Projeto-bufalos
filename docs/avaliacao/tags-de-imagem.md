# Tags de Curadoria de Imagens

Este documento define a taxonomia usada na revisao manual das imagens.

O objetivo das tags e permitir agrupar casos que tendem a afetar a qualidade da segmentacao.

## Decisao adotada

- manter uma taxonomia fechada de tags para reduzir ambiguidade durante a curadoria.

## Motivo

- isso facilita a leitura dos resultados e a comparacao entre grupos de imagens com caracteristicas semelhantes.

## Regras gerais

- Uma imagem pode receber mais de uma tag.
- A tag `ok` so deve ser usada quando nenhuma tag de problema se aplica.
- Ausencia de tag significa `nao_revisada`, e nao imagem aprovada.
- As tags descrevem dificuldade de leitura visual da imagem, nao o desempenho final do modelo.

## Conjunto de tags

- `ok`
- `multi_bufalos`
- `cortado`
- `angulo_extremo`
- `baixo_contraste`
- `ocluido`

## Definicoes

### `ok`

Use quando a imagem estiver adequada para analise, sem ressalvas relevantes.

Criterios praticos:

- um unico bufalo como sujeito principal;
- corpo majoritariamente visivel;
- sem corte relevante;
- sem oclusao relevante;
- sem angulo que distorca fortemente o contorno.

### `multi_bufalos`

Use quando houver mais de um bufalo visivel na cena com presenca relevante para a leitura da imagem.

Sinais tipicos:

- existe um sujeito principal, mas outros bufalos visiveis tambem influenciam a leitura da cena;
- a presenca de outros animais pode confundir a segmentacao ou a atribuicao do contorno principal;
- os outros bufalos nao estao tao pequenos ou distantes a ponto de serem irrelevantes.

Regra pratica:

- use `multi_bufalos` quando os outros bufalos ainda tiverem presenca suficiente para impactar a leitura visual do caso;
- nao use `multi_bufalos` apenas porque existe outro bufalo muito pequeno, muito distante ou sem impacto pratico na cena;
- uma imagem pode continuar como `ok` quando houver outros bufalos ao fundo, desde que eles sejam claramente secundarios e pouco relevantes.

### `cortado`

Use quando parte relevante do corpo ficou fora do enquadramento.

Exemplos:

- cabeca fora do frame;
- patas cortadas;
- traseiro, dorso ou cauda fora da imagem.

Regra pratica:

- use `cortado` quando a informacao desapareceu por causa do enquadramento.

### `angulo_extremo`

Use quando o angulo dificulta comparar o volume corporal ou o contorno do animal.

Exemplos:

- foto muito de frente;
- foto muito de tras;
- foto muito de cima ou de baixo;
- perspectiva que deforma comprimento, altura ou largura aparentes.

### `baixo_contraste`

Use quando o contorno do bufalo se mistura ao fundo por semelhanca de cor, luminosidade ou textura.

Exemplos:

- animal escuro sobre fundo escuro;
- borda do corpo pouco destacada;
- cenario reduzindo a separacao entre figura e fundo.

Regra pratica:

- use `baixo_contraste` quando o problema principal estiver no contraste com o fundo, e nao em corte, oclusao ou angulo.

### `ocluido`

Use quando parte relevante do corpo esta no enquadramento, mas foi encoberta por outro elemento.

Exemplos:

- cerca ou grade na frente do corpo;
- outro animal cobrindo parte do sujeito;
- poste, tronco ou pessoa ocultando regioes importantes.

Regra pratica:

- use `ocluido` quando a informacao esta na imagem, mas algo a esconde.

## Distincoes importantes

### `cortado` x `ocluido`

- `cortado`: a parte do corpo ficou fora da imagem;
- `ocluido`: a parte do corpo esta na imagem, mas encoberta.

### `ocluido` x `baixo_contraste`

- `ocluido`: existe um elemento entre a camera e o animal;
- `baixo_contraste`: o corpo esta visivel, mas se confunde com o fundo.

Exemplos combinados:

- perna atras da cerca: `ocluido`;
- corpo inteiro visivel, mas com pouca separacao do fundo: `baixo_contraste`;
- grade na frente do corpo e fundo parecido com a pelagem: `ocluido` e `baixo_contraste`.

## Convencao de uso

- Marque `ok` apenas quando nao houver nenhuma observacao relevante.
- Se houver problema, marque somente as tags aplicaveis ao caso.
- Evite criar variacoes fora desse conjunto sem atualizar esta documentacao.
