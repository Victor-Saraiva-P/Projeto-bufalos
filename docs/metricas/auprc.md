# AUPRC

## O que a métrica significa

AUPRC significa `Area Under the Precision-Recall Curve`. Na prática, ela mede
quão bem um mapa de score da máscara consegue separar pixels de búfalo dos
pixels de fundo ao longo de vários limiares possíveis.

Ao contrário de métricas que dependem de um threshold fixo, a AUPRC usa o score
contínuo da predição e avalia o comportamento da segmentação em toda a faixa de
decisão. Isso é especialmente útil quando o modelo produz uma máscara em tons
de cinza, probabilidades ou scores por pixel antes da binarização final.

## Como interpretar

- Valor próximo de `1.0`: os pixels do búfalo aparecem consistentemente com
  scores maiores do que os pixels de fundo.
- Valor próximo de `0.0`: o modelo não consegue ordenar bem os pixels
  positivos acima do fundo.
- Quanto maior a AUPRC, melhor a separação entre búfalo e fundo.

## Quando usar

A AUPRC é apropriada para avaliação de segmentação quando:

- a classe positiva é rara;
- o fundo domina a maior parte da imagem;
- a análise deve considerar o score bruto da máscara, sem depender de um único
  threshold.

## Implementação no projeto

O cálculo foi implementado em `src/binarizacao/metricas/auprc.py` e segue o
mesmo padrão de interface abstrata usado nas demais métricas do projeto, mas
adaptado ao contexto de binarização: entrada com `score_mask` contínuo e
`ground_truth_mask` binário.
