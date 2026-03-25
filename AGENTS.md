# Repository Guidelines

## Estrutura do Projeto e Organizacao dos Modulos

O codigo principal fica em `src/`. O pipeline de segmentacao esta em `src/segmentacao/`, incluindo orquestracao em lote, estrategias de binarizacao, verificacao de integridade e helpers de logging. A configuracao compartilhada fica em `src/config.py` e `src/config.toml`. A documentacao fica em `docs/`, com destaque para `docs/guias/` e `docs/decisoes-tecnicas/`. Os notebooks de apoio ficam em `notebooks/`. Os testes automatizados ficam em `tests/` e devem espelhar `src/` sempre que fizer sentido.

## Comandos de Build, Teste e Desenvolvimento

- `mise exec python@3.13 -- python -m venv .venv && source .venv/bin/activate`: cria e ativa um ambiente virtual local, conforme `docs/guias/guia-do-projeto.md`.
- `pip install -e .`: instala o projeto em modo editavel.
- `pytest`: executa toda a suite de testes.
- `pytest -m "not e2e"`: executa a suite rapida sem testes end-to-end.
- `pytest --cov=src --cov-report=term-missing`: executa os testes com coverage.

## Estilo de Codigo e Convencoes de Nomes

Use Python com indentacao de 4 espacos e imports explicitos. Prefira modulos pequenos e coesos, e mantenha notebooks finos, movendo logica reutilizavel para `src/`. Arquivos e funcoes usam `snake_case`; classes usam `PascalCase`. Em `src/segmentacao/logging/`, os modulos de logging devem comecar com `logs_`. Em `src/segmentacao/binarizacoes/`, abstracoes base devem usar nomes de dominio claros, como `binarizacao_base.py`.

Quando uma decisao tecnica impactar o pipeline, registre-a em `docs/decisoes-tecnicas/` e referencie no codigo com comentarios como:

```python
# Docs: decisoes-tecnicas/mascaras-do-rembg.md
```

## Diretrizes de Testes

O framework de testes e `pytest`. Os arquivos de teste devem comecar com a camada a que pertencem: `unit_test_`, `integration_test_` ou `e2e_test_`. Mantenha as pastas de teste alinhadas com `src/` quando pratico, por exemplo `tests/unit/segmentacao/` para `src/segmentacao/`. Use `tests/mock_data/` e `tests/mock_config.py` para cenarios deterministas, evitando dependencia dos dados reais do projeto.

## Diretrizes de Commit e Pull Request

O historico recente usa mensagens curtas no imperativo, como `Refatora pipeline de binarizacao e logging` e `Remove modulo legado de logs de segmentacao`. Siga esse padrao: um objetivo claro por commit, com descricao direta.

Pull requests devem resumir a mudanca de comportamento, listar os modulos afetados, mencionar atualizacoes de documentacao e incluir evidencia de teste (`pytest ...`). Se notebooks ou artefatos gerados forem alterados, explique o motivo.
