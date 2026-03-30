# U2Net Cloth Seg

Este documento registra a decisao de nao usar o modelo `u2net_cloth_seg` na configuracao ativa do projeto.

## Implementacao relacionada

- `config.toml`

## Contexto

O plano de trabalho que serviu de base para o projeto menciona o `u2net_cloth_seg` como candidato a teste.

Durante a avaliacao com imagens de bufalos, o comportamento observado foi inconsistente com o objetivo do projeto:

- a mascara gerada tende a ficar quase toda preta ou muito conservadora;
- o contorno do animal fica incorreto ou artificialmente reduzido;
- a segmentacao final perde partes relevantes do corpo ou distorce as bordas.

## Decisao adotada

- nao incluir `u2net_cloth_seg` entre os modelos ativos em `config.toml`;
- manter o identificador apenas comentado, com referencia para esta documentacao.

## Motivo

O `u2net_cloth_seg` foi treinado para segmentacao de roupas em pessoas, e nao para segmentacao generica de objetos ou animais.

Por isso, ao receber imagens de bufalos, o modelo opera fora do dominio para o qual foi treinado e tende a falhar.

Na pratica, isso produz mascaras inadequadas para o pipeline de avaliacao do projeto e torna a comparacao com os demais modelos pouco util.
