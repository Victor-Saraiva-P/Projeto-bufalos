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
4. agregar resultados;
5. produzir visualizacoes e ranking.

No projeto, a etapa de avaliacao e centralizada no notebook:

- `notebooks/03_calculo_das_avaliacoes.ipynb`

A analise exploratoria e o ranking ficam no notebook:

- `notebooks/04_analise_das_avaliacoes.ipynb`

## Componentes envolvidos

Arquivos relevantes:

- `src/controllers/segmentacao_controller.py`: processa a etapa de geracao de mascaras e grava os artefatos previstos no filesystem;
- `src/services/segmentacao_service.py`: executa a inferencia sem persistir entidades metricas parciais;
- `src/controllers/binarizacao_controller.py`: processa a etapa de binarizacao e grava os artefatos binarios no filesystem;
- `src/services/binarizacao_service.py`: executa a binarizacao sem criar entidades metricas incompletas;
- `src/analysis/collector.py`: coleta as metricas para todas as imagens e modelos;
- `src/analysis/ranker.py`: transforma as metricas agregadas em ranking;
- `src/visualization/metric_plots.py`: gera graficos para inspecao das metricas;
- `src/visualization/image_grid.py`: monta grades visuais para comparar casos;
- `src/config.py`: define caminhos e pesos usados no ranking.

Saida gerada:

- `generated/bufalos.sqlite3`: banco SQLite usado como fonte de verdade da avaliacao.

Observacao importante:

- `SegmentacaoBruta`, `GroundTruthBinarizada` e `SegmentacaoBinarizada` representam resultados metricos completos; elas nao sao criadas nas etapas 01 e 02.
- `SegmentacaoBruta` persiste a metrica `auprc`.
- `SegmentacaoBinarizada` persiste `area`, `perimetro` e `iou` por estrategia de binarizacao.

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

Depois, use o notebook 04 para:

- inspecionar distribuicoes por modelo;
- ver os melhores e piores casos;
- comparar o ranking final.

### Via codigo

Exemplo minimo para coletar metricas:

```python
from src.analysis import MetricsCollector

collector = MetricsCollector(force_recalculate=False)
df_metrics = collector.collect_all_metrics()
```

Exemplo minimo para gerar ranking:

```python
from src.analysis import ModelRanker
from src.config import RANKING_WEIGHTS

ranker = ModelRanker(df_metrics, weights=RANKING_WEIGHTS)
df_ranking = ranker.calculate_ranking()
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

## Ranking ponderado

O ranking final combina as metricas com pesos definidos em `src/config.py`.

Configuracao esperada:

```python
RANKING_WEIGHTS = {
    "iou": 0.70,
    "area_diff_rel": 0.15,
    "perimetro_diff_rel": 0.15,
}
```

Regra importante:

- a soma dos pesos deve ser `1.0`.

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
- consistencia entre score agregado e inspecao visual.

As tags de curadoria descritas em [`tags-de-imagem.md`](./tags-de-imagem.md) ajudam a entender por que certos grupos de imagem tendem a performar pior.
