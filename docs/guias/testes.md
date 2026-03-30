# Suite de Testes

Este documento descreve a organizacao da pasta `tests/`.

## Objetivo

A suite automatizada existe para validar comportamento sem depender do dataset completo do projeto.

Principios da suite:

- usar um dataset reduzido e controlado;
- desenvolver novas funcionalidades e correcoes usando TDD sempre que pratico;
- separar testes por tipo;
- manter os imports do pacote `src` via instalacao do projeto;
- evitar acoplamento desnecessario com caminhos do ambiente real.

## Abordagem de desenvolvimento

O projeto adota TDD (`Test-Driven Development`) como abordagem preferencial de implementacao.

Fluxo esperado:

1. escrever ou ajustar um teste que descreva o comportamento desejado;
2. executar o teste e confirmar a falha inicial;
3. implementar a menor mudanca necessaria para fazer o teste passar;
4. refatorar preservando a suite verde.

Essa diretriz vale tanto para novas funcionalidades quanto para correcoes de bug, desde que o comportamento seja testavel de forma automatizada.

## Estrutura atual

Estrutura principal:

```text
config.toml
config.test.toml
tests/
  conftest.py
  mock_data/
  mock_generated/
  fixtures/
  unit/
    analysis/
    binarizacao/
    io/
    logs/
    avaliacao/
    metricas/
    models/
    runtime/
    segmentacao/
    visualization/
  integration/
    analysis/
    io/
    pipeline/
  e2e/
```

## Organizacao por tipo

### `tests/unit/`

Contem testes isolados por modulo.

Regra:

- sempre que fizer sentido, a estrutura deve acompanhar a organizacao de `src/`.

Exemplos:

- testes de `src.metricas` e `src.metricas.segmentacao_binarizada` ficam em `tests/unit/metricas/`;
- testes de `src.models` ficam em `tests/unit/models/`;
- testes de `src.repositories` ficam em `tests/unit/io/` enquanto a suite nao ganhar uma pasta propria;
- testes de `src.controllers` e `src.services` devem acompanhar essas camadas em novas subpastas quando surgirem;
- testes de `src.binarizacao` ficam em `tests/unit/binarizacao/`;
- testes de `src.segmentacao` ficam em `tests/unit/segmentacao/`.

### `tests/integration/`

Contem cenarios que atravessam mais de um modulo ou dependem de arquivos reais do dataset reduzido.

Pastas atuais:

- `tests/integration/analysis/`
- `tests/integration/io/`
- `tests/integration/pipeline/`

### `tests/e2e/`

Reserva os testes ponta a ponta, normalmente mais caros e menos adequados para execucao em todas as iteracoes locais ou no CI rapido.

### `tests/fixtures/`

Contem helpers, builders e fixtures compartilhadas entre diferentes camadas da suite.

## Convencao de nomes dos arquivos

Os arquivos de teste devem comecar pelo tipo do teste.

Regra:

- testes unitarios usam o prefixo `unit_test_`;
- testes de integracao usam o prefixo `integration_test_`;
- testes end-to-end usam o prefixo `e2e_test_`.

Exemplos:

- `tests/unit/io/unit_test_path_utils.py`
- `tests/integration/pipeline/integration_test_segmentacao.py`
- `tests/e2e/e2e_test_segmentacao.py`

Essa convencao deve ser seguida em novos arquivos para manter o espelhamento da suite e evitar ambiguidade sobre o tipo do teste ja no nome do arquivo.

## Convencoes de import

`tests/` nao deve ser tratado como pacote instalado.

Por isso:

- evite imports com prefixo `tests.`;
- use imports locais da propria suite quando necessario;
- mantenha imports com prefixo `src.` para o codigo do projeto.

Exemplo preferido:

```python
from src.config import INDICE_PATH, MODELOS_PARA_AVALIACAO
```

## Dataset reduzido

O conjunto de apoio da suite fica em `tests/mock_data/`.

Ele replica apenas a estrutura minima necessaria para exercitar leitura de planilha, resolucao de caminhos e fluxos que dependem de nomes de arquivos reais.

Estrutura atual:

```text
tests/mock_data/
  Indice.xlsx
  images/
  ground_truth_raw/
```

Objetivos desse dataset:

- testar bootstrap do indice Excel para SQLite;
- testar leitura do indice a partir do SQLite;
- validar fluxos baseados em nomes de arquivo reais;
- permitir testes de integracao sem depender de `data/`.

## Artefatos gerados versionados

O conjunto `tests/mock_generated/` guarda artefatos intermediarios e finais ja gerados, versionados para uso em testes de integracao futuros.

Ele complementa `tests/mock_data/`:

- `mock_data` contem insumos brutos, como o indice e imagens de entrada;
- `mock_generated` contem saidas produzidas pelo pipeline, prontas para consumo por testes.

Estrutura atual:

```text
tests/mock_generated/
  ground_truth_binary/
  predicted_masks/
    u2netp/
  predicted_masks_binary/
    u2netp/
```

Objetivos desse conjunto:

- disponibilizar mascaras geradas estaveis para cenarios de integracao;
- evitar depender da execucao previa dos notebooks ou do `rembg` em testes futuros da avaliacao;
- permitir testes sobre artefatos binarios versionados.

## Configuracao da suite

A configuracao base do projeto fica em `config.toml`.

O override de teste fica em `config.test.toml`.

Durante a suite, `tests/conftest.py` define `BUFALOS_ENV=test` antes de qualquer import de `src.config`.

Com isso:

- `src/config.py` continua sendo o loader oficial;
- `config.toml` funciona como base;
- `config.test.toml` sobrescreve apenas o que muda para a suite, principalmente paths e subconjunto de modelos.

Exemplo enxuto de override:

```toml
[paths]
data_dir = "tests/mock_data"
generated_dir = "tests/generated"
images_dir = "tests/mock_data/images"
ground_truth_raw_dir = "tests/mock_data/ground_truth_raw"
predicted_masks_dir = "tests/generated/predicted_masks"
predicted_masks_binary_dir = "tests/generated/predicted_masks_binary"
ground_truth_binary_dir = "tests/generated/ground_truth_binary"
evaluation_dir = "tests/generated/evaluation"
indice_file = "tests/mock_data/Indice.xlsx"
sqlite_file = "tests/generated/bufalos-testes.sqlite3"

[models]
u2netp = "cpu"
```

## Fluxo local recomendado

Instalacao editavel:

```bash
pip install -e .
```

Execucao da suite:

```bash
pytest
```

Execucao rapida sem `e2e`:

```bash
pytest -m "not e2e"
```

## Coverage

Resumo no terminal:

```bash
pytest --cov=src --cov-report=term-missing
```

Relatorio HTML:

```bash
pytest --cov=src --cov-report=html
```

O relatorio fica em `htmlcov/`.
