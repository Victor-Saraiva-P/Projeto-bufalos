# Choices

Esse documento descreve as escolhas feitas no desenvolvimento deste projeto.

## Sobre os parâmetros do remove do rembg

A função `remove` do rembg tem vários parâmetros que influenciam o resultado da remoção de fundo. Aqui estão algumas escolhas importantes:

- `only_mask=True` → 256 valores diferentes (escala de cinza completa)
- `post_process_mask=True` → 2 valores apenas (0 e 255)

O parâmetro `post_process_mask=True` é a escolha que produz uma máscara binária (0 e 255), o que é o necessário para poder fazer as comparações com a máscara manual.

## Sobre o formato da saída da máscara binária

A saída da máscara binária está como PNG, por ser um formato sem perda de qualidade (lossless). Isso é importante para manter a integridade dos dados da máscara.