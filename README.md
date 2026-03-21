# Projeto Bufalos

Este repositorio contem o projeto de avaliacao de modelos de remocao de fundo em imagens de bufalos.

## Quick Start

Pre-requisitos:

- Python 3.13 recomendado;
- o projeto requer Python `>= 3.12` e `< 3.14`;
- `tkinter` disponivel no Python para rodar os anotadores manuais;
- Jupyter instalado no ambiente para executar os notebooks;
- GPU NVIDIA com CUDA e opcional.

Na raiz do projeto:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Para executar localmente:

```bash
jupyter notebook
```

Depois, rode os notebooks principais nesta ordem:

1. `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`
2. `notebooks/02_binarizacao_mascaras.ipynb`
3. `notebooks/03_avaliacao_das_segmentacoes.ipynb`

Para executar a suite automatizada:

```bash
pytest
```

## Guia rapido

Se voce quer:

- entender como preparar o ambiente e rodar o projeto: veja `docs/guias/guia-do-projeto.md`;
- entender a suite automatizada: veja `docs/guias/testes.md`;
- entender o CI: veja `docs/guias/ci.md`;
- entender o sistema de avaliacao: veja `docs/avaliacao/sistema-de-avaliacao.md`;
- consultar as tags de curadoria: veja `docs/avaliacao/tags-de-imagem.md`;
- consultar decisoes tecnicas do pipeline: veja `docs/decisoes-tecnicas/`.
- consultar material de referencia do `rembg`: veja `docs/referencia/rembg/`.

## Onde encontrar cada coisa

- `src/`: codigo principal do projeto;
- `tests/`: suite automatizada;
- `notebooks/`: fluxo exploratorio e analitico;
- `docs/`: documentacao organizada por tema;
- `data/`: dados de entrada esperados pelo pipeline;
- `generated/`: artefatos gerados durante segmentacao, binarizacao e avaliacao.

## Estrutura da documentacao

```text
docs/
  guias/
    guia-do-projeto.md
    testes.md
    ci.md
  avaliacao/
    sistema-de-avaliacao.md
    tags-de-imagem.md
  decisoes-tecnicas/
    mascaras-do-rembg.md
    formato-das-mascaras.md
  referencia/
    rembg/
      leia-me-do-rembg.md
      uso-do-rembg.md
```

## Fluxo de leitura recomendado

1. comece por `docs/guias/guia-do-projeto.md`;
2. use `docs/avaliacao/sistema-de-avaliacao.md` para entender o pipeline de avaliacao;
3. consulte `docs/avaliacao/tags-de-imagem.md` ao revisar ou interpretar imagens;
4. use `docs/guias/testes.md` e `docs/guias/ci.md` ao mexer na suite.
