# CI

## Objetivo

O projeto possui um workflow inicial de GitHub Actions em `.github/workflows/ci.yml`.

Nesta fase, o CI instala os extras `test` e `e2e` e executa toda a suite de testes.
Tambem gera o relatorio HTML de coverage como artifact da execucao.

## Gatilhos

O workflow roda em:

- `pull_request`
- `workflow_dispatch`

## Ambiente

O job usa:

- `ubuntu-latest`
- Python 3.13

## Dependencias

O CI usa os extras `test` e `e2e` definidos no `pyproject.toml`.

O workflow instala o projeto com:

```bash
pip install .[test,e2e]
```

Esse caminho aproxima o ambiente do CI do mesmo ambiente usado localmente para rodar os testes.

## Execucao

O workflow executa:

- `pytest` para toda a suite, incluindo os testes marcados como `e2e`
- generation de `htmlcov/` com `pytest-cov`
- upload do relatorio HTML como artifact

## Artifact de coverage

Ao final da execucao, o workflow publica um artifact chamado `coverage-html`.

Para visualizar o relatorio:

1. abra a execucao do workflow no GitHub Actions
2. baixe o artifact `coverage-html`
3. extraia o arquivo baixado
4. abra `htmlcov/index.html` no navegador

## Arquivos relacionados

- `.github/workflows/ci.yml`
- `pyproject.toml`
- `tests/`
- `htmlcov/`
