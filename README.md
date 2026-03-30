# Projeto Bufalos

Este repositorio contem o projeto de avaliacao de modelos de remocao de fundo em imagens de bufalos.

## Quick Start

Pre-requisitos:

- Python 3.13 recomendado;
- o projeto requer Python `>= 3.12` e `< 3.14`;
- `tkinter` disponivel no Python para rodar os anotadores manuais;
- Jupyter instalado no ambiente para executar os notebooks;
- GPU NVIDIA com CUDA é opcional.

Na raiz do projeto, a opcao recomendada e usar `mise`:

```bash
mise exec python@3.13 -- python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Se voce nao tiver `mise`, pode usar diretamente:

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
3. `notebooks/03_calculo_das_avaliacoes.ipynb`
4. `notebooks/04_analise_das_avaliacoes.ipynb`

Observacoes sobre persistencia:

- o notebook 01 inicializa o SQLite em `generated/` a partir do `data/Indice.xlsx`;
- depois disso, o SQLite guarda o indice e os resultados completos de avaliacao;
- o progresso de segmentacao e binarizacao e inferido pelos arquivos gerados em `generated/`;
- o Excel continua sendo usado apenas no processo de tagging.
- os notebooks 01 e 02 executam o pipeline por meio de controllers em `src/controllers/`.
- nessa arquitetura, controllers podem ler `src/config.py`; services recebem caminhos, modelos e estrategias ja resolvidos por parametro.

Para executar a suite automatizada:

```bash
pytest
```

Comandos uteis:

```bash
pytest -m "not e2e"
pytest --cov=src --cov-report=term-missing
```

## Guia Rapido

Se voce quer:

- entender como preparar o ambiente e rodar o projeto: veja `docs/guias/guia-do-projeto.md`;
- entender a politica de sincronizacao entre `README.md`, `docs/` e `AGENTS.md`: veja `docs/guias/documentacao-do-repositorio.md`;
- entender a suite automatizada: veja `docs/guias/testes.md`;
- entender o CI: veja `docs/guias/ci.md`;
- entender o sistema de avaliacao: veja `docs/avaliacao/sistema-de-avaliacao.md`;
- entender a metrica AUPRC usada na binarizacao: veja `docs/metricas/auprc.md`;
- consultar as tags de curadoria: veja `docs/avaliacao/tags-de-imagem.md`;
- consultar decisoes tecnicas do pipeline: veja `docs/decisoes-tecnicas/`;
- consultar material de referencia do `rembg`: veja `docs/referencia/rembg/`.

## Onde Encontrar Cada Coisa

- `src/`: codigo principal do projeto;
- `src/models/`: entidades persistidas do dominio (`Imagem`, `Segmentacao`, `Binarizacao`, `Tag`, etc.);
- `src/repositories/`: CRUD e consultas baseadas nas entidades;
- `src/sqlite/`: infraestrutura de sessao, `Base` e configuracao do SQLite;
- `src/controllers/` e `src/services/`: orquestracao e casos de uso da aplicacao;
- `src/segmentacao/`: fachadas da etapa de segmentacao; a logica principal fica em `controllers/services`;
- `src/binarizacao/`: fachadas da etapa de binarizacao; a logica principal fica em `controllers/services`;
- `src/logs/`: logs compartilhados de segmentacao, binarizacao e integridade;
- `src/tagging/`: anotadores manuais de curadoria;
- `tests/`: suite automatizada, incluindo `mock_data/` para insumos reduzidos e `mock_generated/` para artefatos gerados versionados;
- `notebooks/`: fluxo exploratorio e analitico;
- `docs/`: documentacao organizada por tema;
- `data/`: dados de entrada esperados pelo pipeline; o `Indice.xlsx` permanece como insumo do tagging e bootstrap inicial;
- `generated/`: artefatos gerados durante segmentacao, binarizacao e avaliacao, incluindo o SQLite do projeto.

## Estrutura Da Documentacao

```text
docs/
  guias/
    guia-do-projeto.md
    documentacao-do-repositorio.md
    testes.md
    ci.md
  avaliacao/
    sistema-de-avaliacao.md
    tags-de-imagem.md
  metricas/
    auprc.md
  decisoes-tecnicas/
    escolha-da-metrica-auprc.md
    mascaras-do-rembg.md
    formato-das-mascaras.md
    u2net-cloth-seg.md
  referencia/
    rembg/
      leia-me-do-rembg.md
      uso-do-rembg.md
```

## Fluxo De Leitura Recomendado

1. comece por `docs/guias/guia-do-projeto.md`;
2. leia `docs/guias/documentacao-do-repositorio.md` para entender a regra de sincronizacao documental;
3. use `docs/avaliacao/sistema-de-avaliacao.md` para entender o pipeline de avaliacao;
4. use `docs/metricas/auprc.md` e `docs/decisoes-tecnicas/escolha-da-metrica-auprc.md` ao mexer na avaliacao de binarizacao;
5. consulte `docs/avaliacao/tags-de-imagem.md` ao revisar ou interpretar imagens;
6. use `docs/guias/testes.md` e `docs/guias/ci.md` ao mexer na suite;
7. consulte `AGENTS.md` quando precisar do contexto consolidado em um unico arquivo.
