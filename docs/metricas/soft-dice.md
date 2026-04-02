# Soft Dice

## Status no repositorio

O `Soft Dice` foi aprovado como a proxima metrica de segmentacao bruta a entrar
no projeto.

Nesta etapa, a documentacao fixa o comportamento esperado e os testes definem o
contrato antes da implementacao.

## O que a metrica significa

O `Soft Dice` mede o quanto a massa de score da mascara prevista coincide com o
ground truth binario.

Ao contrario do Dice classico, que compara mascaras binarias `0/1`, o `Soft
Dice` usa o score continuo por pixel ja normalizado em `[0, 1]`.

Entradas esperadas:

- `g_i in {0, 1}`: ground truth binario;
- `p_i in [0, 1]`: score continuo da predicao.

Formula:

```text
SoftDice = 2 * sum(p_i * g_i) / (sum(p_i) + sum(g_i))
```

Leitura pratica da formula:

- o termo `sum(p_i * g_i)` cresce quando scores altos caem dentro do bufalo;
- `sum(p_i)` aumenta quando o modelo espalha score pela imagem;
- `sum(g_i)` representa a area positiva do ground truth.

## Intuicao sem matematica

O Dice classico responde:

`quanto do que eu marquei bate com a verdade?`

O `Soft Dice` responde:

`quanto da minha confianca esta colocada no lugar certo?`

Isso faz a metrica capturar nao apenas acerto ou erro, mas tambem a intensidade
do score onde ele deveria estar.

## Como interpretar

- valor `1.0`: o modelo concentra score alto apenas onde o ground truth e `1`,
  com score baixo no fundo;
- valor proximo de `0.0`: a confianca esta mal distribuida, com vazamento no
  fundo, cobertura incompleta do animal ou ambos;
- quanto maior o `Soft Dice`, melhor a cobertura do bufalo com menor vazamento.

## Exemplos intuitivos

- se o modelo pinta o bufalo com scores altos e o fundo com scores baixos, o
  `Soft Dice` sobe;
- se aparece um halo cinza amplo no fundo, o `Soft Dice` cai;
- se apenas uma parte pequena do bufalo recebe score alto, o `Soft Dice` tambem
  cai;
- se a incerteza fica concentrada na borda, o valor tende a cair menos do que
  em casos de vazamento espalhado pelo fundo.

## Por que ele e util no pipeline

O `Soft Dice` ajuda a distinguir dois cenarios que visualmente podem parecer
parecidos em mascaras brutas:

- incerteza localizada na borda do animal;
- confianca vazando pelo fundo.

Ele tambem cria uma ponte natural com a etapa binaria, porque mascaras com bom
`Soft Dice` tendem a ser mais faceis de binarizar com menos dependencia de um
threshold especifico.

## Relacao com AUPRC

`AUPRC` e `Soft Dice` nao medem a mesma coisa.

- `AUPRC` e mais forte para avaliar ranking de scores: se os pixels do bufalo
  ficam acima dos pixels de fundo;
- `Soft Dice` e mais forte para avaliar cobertura e concentracao: se a massa de
  score realmente ficou em cima do animal, sem vazamento excessivo.

Por isso, elas se complementam na avaliacao de mascaras com score continuo.

## Como reportar

Recomendacao para analise:

- calcular `Soft Dice` por imagem;
- reportar mediana e IQR, ou media e desvio padrao;
- cruzar a distribuicao com tags de curadoria para identificar cenarios onde a
  metrica despenca.

## Limitacoes

- a metrica ainda depende de um ground truth binario;
- ela nao mede diretamente a geometria fina do contorno;
- saidas pouco saturadas podem perder `Soft Dice` mesmo sem erro visual grave;
- comparacoes entre modelos exigem o mesmo protocolo de normalizacao para
  `score_mask`.

## Escopo desta documentacao

Este documento descreve apenas o `Soft Dice` e seu papel na avaliacao de
segmentacao bruta.

Mascaras em escala `0-255` devem ser normalizadas para `[0, 1]` antes do
calculo.
