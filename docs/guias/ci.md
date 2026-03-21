# CI

Este documento descreve o que o workflow de integracao continua valida hoje em `.github/workflows/ci.yml`.

## Objetivo

O CI existe para verificar rapidamente se o projeto instala corretamente e se a suite automatizada principal continua passando.

Nesta configuracao atual, o workflow:

- instala o projeto com as dependencias de teste;
- executa `pytest` sem os testes marcados como `e2e`;
- gera o relatorio HTML de coverage;
- publica o coverage como artifact.

## Gatilhos

O workflow roda em:

- `pull_request`
- `workflow_dispatch`

## Ambiente usado

- sistema: `ubuntu-latest`
- Python: `3.13`

## Instalacao no CI

O job instala o projeto com:

```bash
python -m pip install .[test]
```

Isso garante que o ambiente do CI tenha tanto as dependencias do projeto quanto as dependencias necessarias para rodar a suite.

## Comando executado

O workflow roda:

```bash
python -m pytest -q -m "not e2e" --cov=src --cov-report=html
```

Efeitos desse comando:

- exclui os testes marcados como `e2e`;
- mede coverage do pacote `src`;
- gera o relatorio HTML em `htmlcov/`.

## Artifact publicado

Ao final da execucao, o CI publica um artifact chamado `coverage-html`.

Para inspecionar o coverage:

1. abra a execucao do workflow no GitHub Actions;
2. baixe o artifact `coverage-html`;
3. extraia o arquivo;
4. abra `htmlcov/index.html`.

## Arquivos relacionados

- `.github/workflows/ci.yml`
- `pyproject.toml`
- `tests/`
- `htmlcov/`
