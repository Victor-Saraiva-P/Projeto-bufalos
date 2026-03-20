# Suite de Testes

## Objetivo

A pasta `testes/tests/` concentra a infraestrutura da suite automatizada do projeto.
Ela usa um dataset reduzido para validar comportamento sem depender do volume completo de `data/`.
O pacote `src` deve ser resolvido pela instalacao editavel do projeto, e nao por insercoes manuais em `sys.path`.
A organizacao da suite deve separar os testes por tipo, e nao usar um espelho unico de `testes/src/`.

Estrutura base esperada:

```text
testes/tests/
  config.toml
  conftest.py
  mock_config.py
  mock_data/
  fixtures/
  unit/
    analysis/
    io/
    logs/
    metrics/
    models/
    runtime/
    visualization/
  integration/
    analysis/
    io/
    pipeline/
```

## Organizacao da suite

### Testes unitarios

`testes/tests/unit/` deve espelhar a estrutura de `testes/src/`.

Exemplos:

- testes para `src.metrics` ficam em `testes/tests/unit/metrics/`
- testes para `src.models` ficam em `testes/tests/unit/models/`
- testes para `src.io` ficam em `testes/tests/unit/io/`

### Testes de integracao

`testes/tests/integration/` deve agrupar cenarios que atravessam mais de um modulo, usam arquivos reais do dataset reduzido ou validam fluxos completos.

Por enquanto, a estrutura base fica em:

- `testes/tests/integration/analysis/`
- `testes/tests/integration/io/`
- `testes/tests/integration/pipeline/`

### Fixtures compartilhadas

`testes/tests/fixtures/` fica reservado para builders, helpers e fixtures reutilizaveis entre `unit/` e `integration/`.

## Dataset reduzido

O conjunto de teste fica em `testes/tests/mock_data/` e replica a estrutura essencial do dataset real com poucos arquivos.

Estrutura atual:

```text
testes/tests/mock_data/
  Indice.xlsx
  images/
    1166_Calcula_506.jpg
    284_Mamucaba_350.jpg
    493098e5-da4e-47dc-80cc-eddd2c703a24.jpg
    67_Laje-Nova_453.jpg
    e2b294f6-387c-49ce-8fd8-8e80e80cdc46.jpg
  ground_truth_raw/
    1166_Calcula_506.jpg
    284_Mamucaba_350.jpg
    493098e5-da4e-47dc-80cc-eddd2c703a24.jpg
    67_Laje-Nova_453.jpg
    e2b294f6-387c-49ce-8fd8-8e80e80cdc46.jpg
```

Esse diretório serve para:

- testar leitura do índice Excel com um conjunto pequeno;
- validar fluxos que dependem de nomes de arquivos reais;
- preparar futuros testes, principalmente de integracao, sem usar o dataset completo.

## Configuracao fake da suite

A configuracao declarativa exclusiva da suite fica em `testes/tests/config.toml`.

O arquivo `testes/tests/mock_config.py` continua existindo apenas como loader fino para ler esse TOML e expor caminhos resolvidos para os testes.

Ela expõe caminhos dedicados para os testes:

- `mock_data_dir`
- `indice_path`
- `images_dir`
- `ground_truth_raw_dir`

O objetivo é evitar dependência direta dos caminhos definidos em `src/config.py`, que representam a estrutura de execução do sistema completo.

Estrutura do arquivo:

```toml
[paths]
mock_data_dir = "mock_data"
indice_file = "Indice.xlsx"
images_dir = "images"
ground_truth_raw_dir = "ground_truth_raw"
lock_file = ".~lock.Indice.xlsx#"
```

## Observacoes

- O diretório de teste usa `ground_truth_raw/`, não `ground_truth/`.
- O arquivo `.~lock.Indice.xlsx#` é temporário, gerado por editor de planilha, e não faz parte do dataset de teste.
- `testes/tests/unit/` espelha `testes/src/`; `testes/tests/integration/` nao precisa espelhar `src/`.
- O fluxo esperado para desenvolvimento local e execucao da suite e:

```bash
pip install -e .[test]
pytest
```
