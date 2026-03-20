# CI

## Objetivo

O projeto possui um workflow inicial de GitHub Actions em `.github/workflows/ci.yml`.

Nesta fase, o CI valida a infraestrutura minima do projeto sem depender ainda de testes reais em `pytest`.

## Gatilhos

O workflow roda em:

- `pull_request`
- `workflow_dispatch`

## Ambiente

O job usa:

- `ubuntu-latest`
- Python 3.13

## Dependencias

O CI usa um conjunto reduzido de dependencias definido em `requirements-ci.txt`.

Depois disso, o projeto e instalado em modo editavel com:

```bash
pip install . --no-deps
```

Esse caminho existe para manter o workflow mais leve e estavel do que o ambiente local completo, sem depender de instalacao editavel no runner.

## Smoke checks

O workflow executa validacoes minimas para garantir que a infraestrutura principal esta integra:

- import de `src.config`
- import de `src.metrics.iou`
- leitura de `tests/config.toml`
- carga de `tests/mock_config.py`
- acesso ao dataset reduzido em `tests/mock_data/`

## Arquivos relacionados

- `.github/workflows/ci.yml`
- `requirements-ci.txt`
- `tests/config.toml`
- `tests/mock_config.py`
- `tests/mock_data/`
