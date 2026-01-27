# Critérios de Avaliação dos Modelos de Remoção de Fundo

> Este arquivo descreve de forma clara e padronizada como os critérios de avaliação dos modelos de remoção de fundo são definidos, calculados e interpretados.

## ROI association

A **Região de Interesse (ROI)**, neste projeto, corresponde à segmentação manual realizada pelos especialistas e armazenada em `dados/fotos segmentadas/`. Essa segmentação manual é considerada a representação mais fiel do contorno corporal do animal, servindo como **Ground Truth (GT)** para todas as avaliações.

A ROI (nosso GT) será então comparada com a segmentação prevista pelo modelo para calcular métricas de similaridade. A principal abordagem é:

**Dice Coefficient**: métrica oficial gravada no banco e usada para ranquear os modelos de forma geral. O Dice é escolhido porque ele é estável e sensível à similaridade global entre as máscaras, dando maior peso à interseção real entre a segmentação prevista e a ROI. Isso o torna ideal para avaliar formas orgânicas, como o contorno corporal dos búfalos, onde pequenas imperfeições nas bordas não devem penalizar excessivamente o modelo.

> **Obs.:** o código mantém o cálculo de IoU comentado para referências futuras. Caso surja a necessidade de desempate entre modelos com Dice muito próximos, o IoU poderá ser reativado/registrado como métrica complementar.
