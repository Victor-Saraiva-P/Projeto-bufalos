# Sistema de Avaliacao

Este documento resume como o projeto compara os modelos de segmentacao e onde cada etapa se encaixa no fluxo de analise.

## Objetivo

O sistema avalia cada modelo comparando a mascara prevista com a mascara de referencia.

As metricas principais sao:

- `iou`: mede sobreposicao entre previsao e ground truth;
- `area_diff_rel`: mede o erro relativo de area;
- `perimetro_diff_rel`: mede o erro relativo de contorno.

## Fluxo de avaliacao

O fluxo principal do projeto e:

1. gerar as segmentacoes previstas;
2. binarizar as mascaras previstas e as mascaras de referencia;
3. calcular metricas por imagem e por modelo;
4. materializar bases analiticas a partir do SQLite;
5. produzir visualizacoes para interpretacao dos resultados.

No projeto, a etapa de avaliacao e centralizada no notebook:

- `notebooks/03_calculo_das_avaliacoes.ipynb`

A reestruturacao analitica desta branch esta em transicao:

- o notebook `04_analise_das_avaliacoes.ipynb` antigo foi removido por estar orientado ao ranking final pos-binarizacao;
- o novo notebook 04 sera recriado para calculo estatistico da segmentacao bruta;
- o novo notebook 05 sera criado para visualizacao da segmentacao bruta;
- o plano detalhado esta em `PLANO_REESTRUTURACAO_NOTEBOOKS_04_05.md`.

## Componentes envolvidos

Arquivos relevantes:

- `src/controllers/segmentacao_controller.py`: processa a etapa de geracao de mascaras e grava os artefatos previstos no filesystem;
- `src/services/segmentacao_service.py`: executa a inferencia sem persistir entidades metricas parciais;
- `src/controllers/binarizacao_controller.py`: processa a etapa de binarizacao e grava os artefatos binarios no filesystem;
- `src/services/binarizacao_service.py`: executa a binarizacao sem criar entidades metricas incompletas;
- `src/analysis/collector.py`: coleta as metricas para todas as imagens e modelos;
- `src/visualization/image_grid.py`: monta grades visuais para comparar casos;
- `src/config.py`: define caminhos, modelos e estrategias usados pelo pipeline.

Saida gerada:

- `generated/bufalos.sqlite3`: banco SQLite usado como fonte de verdade da avaliacao.

Observacao importante:

- `SegmentacaoBruta`, `GroundTruthBinarizada` e `SegmentacaoBinarizada` representam resultados metricos completos; elas nao sao criadas nas etapas 01 e 02.
- `SegmentacaoBruta` persiste `auprc`, `soft_dice` e `brier_score`.
- `SegmentacaoBinarizada` persiste `area`, `perimetro` e `iou` por estrategia de binarizacao.

Metricas de segmentacao bruta com score continuo:

- `auprc`: mede separacao entre pixels de bufalo e fundo ao longo de varios limiares;
- `soft_dice`: mede cobertura ponderada pela massa de score em cima do ground truth;
- `brier_score`: mede erro probabilistico medio entre score previsto e ground truth binario.

## Como usar

### Via notebook

Abra e execute:

```bash
jupyter notebook notebooks/03_calculo_das_avaliacoes.ipynb
```

O notebook 03 permite:

- recalcular metricas;
- persistir os resultados incrementais no SQLite;
- acompanhar o progresso do processamento por imagem.

### Via codigo

Exemplo minimo para coletar metricas:

```python
from src.analysis import MetricsCollector

collector = MetricsCollector(force_recalculate=False)
df_metrics = collector.collect_all_metrics()
```

## Como interpretar as metricas

### `iou`

Formula:

```text
IoU = intersecao / uniao
```

Leitura:

- varia entre `0` e `1`;
- quanto maior, melhor.

### `area_diff_rel`

Formula:

```text
|area_modelo - area_gt| / area_gt
```

Leitura:

- valores menores sao melhores;
- ajuda a detectar excesso ou falta de area segmentada.

### `perimetro_diff_rel`

Formula:

```text
|perimetro_modelo - perimetro_gt| / perimetro_gt
```

Leitura:

- valores menores sao melhores;
- ajuda a medir a qualidade do contorno.

## Persistencia

Por padrao, a coleta usa o SQLite do projeto como fonte de verdade para as metricas.

Para forcar recalcucao:

```python
collector = MetricsCollector(force_recalculate=True)
df_metrics = collector.collect_all_metrics()
```

Isso sobrescreve os registros de avaliacao no banco:

- `generated/bufalos.sqlite3`

Arquitetura da persistencia:

- `src/models/` define as entidades persistidas (`Imagem`, `GroundTruthBinarizada`, `SegmentacaoBruta`, `SegmentacaoBinarizada`, `Tag`);
- `src/repositories/` encapsula o CRUD dessas entidades;
- `src/logs/` centraliza os logs compartilhados do pipeline;
- `src/controllers/avaliacao_controller.py` coordena o processamento de cada imagem;
- `src/services/avaliacao_service.py` calcula as metricas e preenche `SegmentacaoBruta`, `SegmentacaoBinarizada` e `GroundTruthBinarizada` antes da persistencia.

## Leitura dos resultados

Ao analisar os resultados, normalmente vale olhar:

- distribuicao das metricas por modelo;
- top `N` e bottom `N` por imagem;
- estabilidade entre execucoes;
- comportamento por tags de curadoria.

As tags de curadoria descritas em [`tags-de-imagem.md`](./tags-de-imagem.md) ajudam a entender por que certos grupos de imagem tendem a performar pior.
