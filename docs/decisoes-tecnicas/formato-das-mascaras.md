# Formato das Mascaras

Este documento registra a decisao sobre o formato de armazenamento das mascaras binarias.

## Decisao adotada

- manter `PNG` como formato padrao para mascaras intermediarias e finais.

## Motivo

- `PNG` e um formato sem perdas, o que evita distorcoes nos contornos e preserva a integridade da mascara;
- a mascara binaria precisa manter os valores de pixel exatamente como foram gerados, sem alteracao introduzida por compressao com perdas;
- formatos como `.jpg` nao sao adequados para essa finalidade, porque a compressao pode alterar os valores de cor e comprometer uma mascara binaria.

## Relacao com os formatos de entrada e saida

As imagens originais de entrada continuam em `.jpg`, porque esse e o formato em que o dataset foi originalmente obtido.

As mascaras de saida sao salvas em `.png`, porque nessa etapa o objetivo nao e representar uma fotografia, e sim preservar exatamente os valores da mascara gerada ou binarizada.

Essa diferenca de formato entre entrada e saida e intencional:

- entrada: imagem fotografica original em `.jpg`;
- saida: mascara em `.png`, sem compressao com perdas.
