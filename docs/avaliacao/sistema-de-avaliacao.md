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

- `notebooks/03_avaliacao_das_segmentacoes.ipynb`

## Componentes envolvidos

Arquivos relevantes:

- `src/analysis/collector.py`: coleta as metricas para todas as imagens e modelos;
- `src/analysis/ranker.py`: transforma as metricas agregadas em ranking;
- `src/visualization/metric_plots.py`: gera graficos para inspecao das metricas;
- `src/visualization/image_grid.py`: monta grades visuais para comparar casos;
- `src/config.py`: define caminhos e pesos usados no ranking.

Saida gerada:

- `generated/evaluation/metrics_cache.csv`: cache das metricas calculadas.

## Como usar

### Via notebook

Abra e execute:

```bash
jupyter notebook notebooks/03_avaliacao_das_segmentacoes.ipynb
```

O notebook permite:

- recalcular metricas;
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

## Recalculo e cache

Por padrao, a coleta usa cache para evitar recomputar tudo a cada execucao.

Para forcar recalcucao:

```python
collector = MetricsCollector(force_recalculate=True)
df_metrics = collector.collect_all_metrics()
```

Isso atualiza o arquivo:

- `generated/evaluation/metrics_cache.csv`

## Leitura dos resultados

Ao analisar os resultados, normalmente vale olhar:

- distribuicao das metricas por modelo;
- top `N` e bottom `N` por imagem;
- consistencia entre score agregado e inspecao visual.

As tags de curadoria descritas em [`tags-de-imagem.md`](./tags-de-imagem.md) ajudam a entender por que certos grupos de imagem tendem a performar pior.
