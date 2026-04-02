# Escolha da metrica Brier Score

## Decisao

Adicionar Brier Score como metrica de avaliacao da segmentacao bruta, em paralelo a
metrica AUPRC.

## Contexto

As mascaras brutas produzidas pelos modelos sao imagens em tons de cinza. Ate aqui,
o pipeline usa AUPRC para avaliar se esses scores separam bem pixels de bufalo e de
fundo. Essa metrica continua adequada para o problema de classe positiva rara, mas
ela nao mede diretamente calibracao probabilistica.

Para a discussao tecnica deste projeto, ha interesse em distinguir dois casos:

- modelo que ordena bem os pixels, mas erra na intensidade da confianca;
- modelo que produz scores coerentes com a ideia de probabilidade por pixel.

## Justificativa

O Brier Score foi escolhido porque mede erro quadratico medio entre score previsto e
ground truth binario. Isso o torna apropriado para avaliar confianca numerica da
mascara continua.

Ele ajuda a capturar cenarios como:

- score alto no fundo, que representa confianca errada;
- score baixo dentro do bufalo, que representa sub-confianca no positivo;
- tons intermediarios em regioes ambiguas, que podem ser aceitaveis quando o erro
  permanece controlado.

## Consequencias

- a avaliacao de segmentacao bruta passa a ter duas leituras complementares:
  separacao via AUPRC e erro probabilistico via Brier Score;
- o calculo deve receber `score_mask` normalizado em `[0, 1]`;
- a normalizacao de mascaras `0-255` deve acontecer no carregamento da mascara
  predita, para evitar ambiguidade entre probabilidade real e PNG 8-bit escuro;
- a camada de persistencia precisara armazenar `brier_score` em `SegmentacaoBruta`;
- o coletor analitico devera expor a nova coluna para analise posterior;
- o valor nao deve ser usado isoladamente, porque o desbalanceamento do dataset faz
  com que o fundo tenha peso dominante no erro medio.

## Estado atual

O `Brier Score` esta integrado a pipeline principal:

- o calculo acontece na avaliacao da segmentacao bruta;
- `SegmentacaoBruta` persiste o campo `brier_score`;
- o coletor analitico expõe a coluna para analise posterior.
