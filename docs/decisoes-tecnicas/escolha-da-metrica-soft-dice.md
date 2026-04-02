# Escolha da metrica Soft Dice

## Decisao

Adotar `Soft Dice` como metrica de segmentacao bruta do projeto, em paralelo a
`AUPRC` e `Brier Score`.

## Contexto

As mascaras brutas dos modelos carregam score continuo por pixel. O projeto
precisa avaliar esse score antes da escolha de um threshold fixo, principalmente
para separar:

- incerteza normal concentrada na borda do animal;
- confianca vazando pelo fundo da imagem;
- cobertura insuficiente do bufalo.

Tambem existe interesse em usar uma metrica que tenha leitura intuitiva para
segmentacao: cobriu o animal sem vazar?

## Motivo da escolha

O `Soft Dice` foi escolhido porque:

- usa diretamente o score continuo da mascara;
- recompensa score alto dentro do ground truth;
- penaliza score alto espalhado no fundo;
- penaliza cobertura incompleta do animal;
- complementa a `AUPRC`, que mede melhor o ranking dos scores do que a
  cobertura em si;
- ajuda a antecipar se a mascara sera facil ou dificil de binarizar depois.

## Consequencias

- o calculo deve receber `score_mask` normalizado em `[0, 1]`;
- o `ground_truth_mask` permanece binario;
- a metrica deve ser calculada por imagem;
- a agregacao recomendada e mediana e IQR, ou media e desvio padrao;
- a metrica nao substitui analises de contorno na etapa binarizada;
- comparacoes entre modelos devem manter o mesmo protocolo de normalizacao.
