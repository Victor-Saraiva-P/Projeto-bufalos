# Brier Score

## Status no repositorio

O `Brier Score` esta implementado na pipeline principal como metrica de
segmentacao bruta com score continuo.

## O que a metrica significa

O Brier Score mede erro probabilistico. No nosso caso, ele compara o score continuo
da mascara predita com o ground truth binario, pixel a pixel.

Para cada pixel:

- `p_i` representa a probabilidade prevista de o pixel pertencer ao bufalo;
- `g_i` representa o ground truth binario (`0` para fundo e `1` para bufalo).

O valor final e a media do erro quadratico entre `p_i` e `g_i`.

## Como interpretar

- `0.0` significa previsao perfeita;
- quanto menor o valor, melhor;
- erros muito confiantes sao penalizados com mais forca.

Isso torna a metrica util para responder a seguinte pergunta:

"quando a mascara cinza parece confiante, esse numero esta realmente alinhado ao
ground truth?"

## Por que ela entra no projeto

O pipeline ja usa AUPRC para medir capacidade de separacao entre bufalo e fundo.
O Brier Score entra como complemento:

- AUPRC diz se os scores ordenam bem os pixels positivos e negativos;
- Brier Score diz se esses scores estao numericamente proximos de probabilidades
  coerentes.

Na pratica, um modelo pode ter boa separacao e ainda assim ser mal calibrado. Isso
aparece quando ele empurra muitos pixels de fundo para valores relativamente altos,
ou quando deixa pixels do animal com scores muito baixos.

## Cuidados de interpretacao

Como o dataset e desbalanceado, o fundo domina a contagem total de pixels. Por isso,
o Brier Score nao deve ser lido sozinho. Ele e mais util quando analisado junto da
AUPRC, que continua sendo a metrica mais sensivel ao positivo raro.

## Contrato usado no projeto

No projeto atual:

- a metrica concreta se chama `BrierScore`;
- ela pertence ao grupo `src.metricas.segmentacao_bruta`;
- a entidade `SegmentacaoBruta` persiste o campo `brier_score`;
- o valor deve ficar no intervalo `[0, 1]`;
- `BrierScore` recebe `score_mask` ja normalizado em `[0, 1]`;
- a normalizacao de mascaras em escala `0-255` deve acontecer em
  `carregar_score_mask_predita()`, antes de o pipeline repassar o dado para
  `AUPRC`, `SoftDice` e `BrierScore`.
