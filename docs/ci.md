# CI

## Objetivo

O projeto possui um workflow inicial de GitHub Actions em `.github/workflows/ci.yml`.

Nesta fase, o CI instala o extra `test` e executa a suite de testes existente.
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

O CI usa o extra `test` definido no `pyproject.toml`.

O workflow instala o projeto com:

```bash
pip install .[test]
```

Esse caminho aproxima o ambiente do CI do mesmo ambiente usado localmente para rodar os testes.

## Execucao

O workflow executa:

- `pytest` para os testes atuais de `io`
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
- `tests/unit/io/`
- `tests/integration/io/`
- `htmlcov/`
