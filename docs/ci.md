# CI

## Objetivo

O projeto possui um workflow inicial de GitHub Actions em `.github/workflows/ci.yml`.

Nesta fase, o CI instala o extra `test` e executa a suite de testes existente.

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

## Arquivos relacionados

- `.github/workflows/ci.yml`
- `pyproject.toml`
- `tests/unit/io/`
- `tests/integration/io/`
