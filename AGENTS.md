# Repository Guidelines

## Objetivo do projeto

Este repositório visa avaliar modelos de remoção de fundo em imagens utilizando a biblioteca `rembg`.

## Docs

> A pasta `docs/` contém arquivos .md para detalhar aspectos específicos do projeto. Consulte:

- `eval-types.md`: critérios de avaliação dos modelos.
- `docs/rembg/rembg-readme.md`: referência original do rembg cobrindo requisitos, instalação, subcomandos CLI, uso via
  docker e catálogo de modelos.
- `docs/rembg/rembg-usage.md`: exemplos práticos de uso da função `remove` (sessões, alpha matting, somente máscara, bg
  customizado) para scripts Python.

## Rembg

> A pasta `rembg/` contém o repositório oficial do rembg clonado para referência.

> Caso a pasta não exista, clone o repositório oficial do rembg usando o github cli:
> ```bash
> gh repo clone danielgatis/rembg
> ```