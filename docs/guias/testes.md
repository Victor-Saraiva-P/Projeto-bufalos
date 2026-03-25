# Suite de Testes

Este documento descreve a organizacao da pasta `tests/`.

## Objetivo

A suite automatizada existe para validar comportamento sem depender do dataset completo do projeto.

Principios da suite:

- usar um dataset reduzido e controlado;
- separar testes por tipo;
- manter os imports do pacote `src` via instalacao do projeto;
- evitar acoplamento desnecessario com caminhos do ambiente real.

## Estrutura atual

Estrutura principal:

```text
tests/
  config.toml
  conftest.py
  mock_config.py
  mock_data/
  mock_generated/
  fixtures/
  unit/
    analysis/
    io/
    logs/
    metrics/
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

- testes de `src.metrics` ficam em `tests/unit/metrics/`;
- testes de `src.models` ficam em `tests/unit/models/`;
- testes de `src.segmentacao` ficam em `tests/unit/segmentacao/`.

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

## Convencoes de import

`tests/` nao deve ser tratado como pacote instalado.

Por isso:

- evite imports com prefixo `tests.`;
- use imports locais da propria suite quando necessario;
- mantenha imports com prefixo `src.` para o codigo do projeto.

Exemplo correto:

```python
from mock_config import MockDataConfig
```

Exemplo a evitar:

```python
from tests.mock_config import MockDataConfig
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

- testar leitura do indice Excel;
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

A configuracao dedicada aos testes fica em `tests/config.toml`.

O arquivo `tests/mock_config.py` funciona como um loader fino para ler esse TOML e expor caminhos resolvidos.

Caminhos esperados:

- `mock_data_dir`
- `indice_path`
- `images_dir`
- `ground_truth_raw_dir`

Estrutura da configuracao:

```toml
[paths]
mock_data_dir = "mock_data"
indice_file = "Indice.xlsx"
images_dir = "images"
ground_truth_raw_dir = "ground_truth_raw"
lock_file = ".~lock.Indice.xlsx#"
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

O relatorio e gerado em `htmlcov/index.html`.

## Observacoes

- o dataset de teste usa `ground_truth_raw/`, nao `ground_truth/`;
- `.~lock.Indice.xlsx#` e arquivo temporario de editor e nao faz parte do dataset;
- `tests/unit/` tende a acompanhar `src/`, enquanto `tests/integration/` e orientado a fluxo;
- o CI rapido exclui os testes marcados como `e2e`; veja [`ci.md`](./ci.md).
