# Escolha da métrica AUPRC

## Decisão

Adotar AUPRC como uma das métricas de avaliação para o estágio de binarização e
análise de máscaras com score contínuo.

## Contexto

No problema deste projeto, os pixels do búfalo representam uma parcela pequena
da imagem, enquanto o fundo ocupa a maior parte do espaço. Esse desbalanceamento
faz com que métricas menos sensíveis à classe positiva rara possam transmitir
uma impressão otimista do desempenho do modelo.

Além disso, na etapa de binarização existe interesse em avaliar a qualidade do
score da máscara antes da escolha de um threshold fixo.

## Motivo da escolha

A AUPRC foi escolhida porque é uma das métricas mais úteis quando a classe
positiva é rara. No caso deste projeto, os pixels do búfalo são poucos e o
fundo é enorme. A métrica mede quão bem o modelo consegue separar búfalo vs
fundo usando o score da máscara, sem exigir a definição prévia de um threshold
fixo.

## Consequências

- a avaliação fica mais alinhada ao cenário real de desbalanceamento entre
  búfalo e fundo;
- o score contínuo da máscara passa a ser aproveitado diretamente;
- comparações entre estratégias de binarização podem considerar a qualidade da
  ordenação dos pixels, e não apenas o resultado final após um corte arbitrário.
