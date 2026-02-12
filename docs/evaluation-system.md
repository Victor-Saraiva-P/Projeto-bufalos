# Sistema de Avaliação de Modelos de Segmentação

Este documento descreve o sistema de avaliação completo implementado para análise dos modelos de remoção de fundo.

## 📋 Visão Geral

O sistema avalia modelos de segmentação através de 3 métricas principais:
- **IoU (Intersection over Union)**: similaridade entre máscaras
- **Diferença de Área**: precisão na área segmentada
- **Diferença de Perímetro**: precisão no contorno

## 🗂️ Estrutura de Arquivos

```
src/
├── analysis/
│   ├── __init__.py
│   ├── collector.py          # MetricsCollector: coleta métricas de todas imagens
│   └── ranker.py             # ModelRanker: ranking ponderado de modelos
│
├── visualization/
│   ├── __init__.py
│   ├── metric_plots.py       # Gráficos de análise (boxplot, scatter, heatmap)
│   └── image_grid.py         # Visualização de imagens (top/bottom casos)
│
└── config.py                 # Configurações (+ RANKING_WEIGHTS)

notebooks/
└── 03_avaliacao_das_segmentacoes.ipynb    # Notebook de análise completa

generated/
└── evaluation/
    └── metrics_cache.csv     # Cache de métricas (gerado automaticamente)
```

## 🚀 Como Usar

### 1. Executar Análise Completa

Abra o notebook `03_avaliacao_das_segmentacoes.ipynb` e execute todas as células:

```bash
jupyter notebook notebooks/03_avaliacao_das_segmentacoes.ipynb
```

O notebook irá:
1. Coletar métricas de todas as imagens e modelos
2. Gerar gráficos de análise por métrica
3. Mostrar top/bottom 5 resultados com imagens
4. Calcular ranking ponderado final

### 2. Uso Programático

#### Coletar Métricas

```python
from src.analysis import MetricsCollector

# Criar collector
collector = MetricsCollector(force_recalculate=False)

# Coletar métricas (usa cache se disponível)
df_metrics = collector.collect_all_metrics()

# DataFrame com colunas:
# - nome_arquivo, modelo
# - area, perimetro, iou
# - area_gt, perimetro_gt
# - area_diff_abs, area_diff_rel
# - perimetro_diff_abs, perimetro_diff_rel
```

#### Calcular Ranking

```python
from src.analysis import ModelRanker
from src.config import RANKING_WEIGHTS

# Criar ranker com pesos customizados (ou usa RANKING_WEIGHTS padrão)
ranker = ModelRanker(df_metrics, weights=RANKING_WEIGHTS)

# Calcular ranking
df_ranking = ranker.calculate_ranking()

# Top 5 modelos
top_5 = ranker.get_top_models(5)
```

#### Gerar Visualizações

```python
from src.visualization import (
    setup_plot_style,
    plot_iou_analysis,
    plot_ranking_analysis,
    get_top_bottom_iou,
    plot_image_grid,
)

# Configurar estilo
setup_plot_style()

# Gráficos de IoU
fig = plot_iou_analysis(df_metrics)

# Top/Bottom resultados
top_iou, bottom_iou = get_top_bottom_iou(df_metrics, n=5)

# Grid de imagens
fig = plot_image_grid(top_iou, "Top 5 - Maior IoU", "iou")
```

## ⚙️ Configuração

### Ajustar Pesos do Ranking

Edite `src/config.py` para modificar os pesos das métricas:

```python
RANKING_WEIGHTS = {
    "iou": 0.70,                    # IoU (peso maior = mais importante)
    "area_diff_rel": 0.15,          # Diferença de área relativa
    "perimetro_diff_rel": 0.15,     # Diferença de perímetro relativa
}
```

**Importante:** A soma dos pesos deve ser 1.0.

### Forçar Recálculo de Métricas

Por padrão, o sistema usa cache. Para recalcular:

```python
collector = MetricsCollector(force_recalculate=True)
df_metrics = collector.collect_all_metrics()
```

Isso irá:
- Processar todas as 387 imagens novamente
- Recalcular métricas de todos os modelos
- Atualizar o cache em `generated/evaluation/metrics_cache.csv`

## 📊 Métricas Explicadas

### IoU (Intersection over Union)

```
IoU = (Área de Interseção) / (Área de União)
```

- Valores entre 0 e 1
- **Maior é melhor**
- Mede sobreposição entre segmentação e ground truth

### Diferença Relativa de Área

```
diff_rel = |área_modelo - área_gt| / área_gt
```

- Valores entre 0 e ∞
- **Menor é melhor**
- Normalizada pelo tamanho da imagem (fair para diferentes resoluções)

### Diferença Relativa de Perímetro

```
diff_rel = |perímetro_modelo - perímetro_gt| / perímetro_gt
```

- Valores entre 0 e ∞
- **Menor é melhor**
- Mede precisão do contorno

## 🎨 Visualizações Disponíveis

### Por Métrica (IoU, Área, Perímetro)

1. **Boxplot**: distribuição por modelo
2. **Violin plot**: densidade da distribuição
3. **Barplot**: médias ordenadas
4. **Scatter plot**: previsto vs ground truth (área/perímetro)

### Ranking

1. **Barplot**: score final por modelo
2. **Stacked bar**: contribuição de cada métrica no score
3. **Heatmap**: correlação entre métricas

### Imagens

- **Grid de comparação**: Original + GT + todos os modelos
- **Top/Bottom N**: melhores e piores casos por métrica
- **Overlay colorido**: máscaras sobrepostas na imagem original

## 🔍 Análise de Resultados

### Top 5 / Bottom 5

Para cada métrica, o sistema identifica:
- **Top 5**: melhores resultados (maior IoU, menor diferença)
- **Bottom 5**: piores resultados (menor IoU, maior diferença)

Permite investigar:
- Por que certos modelos/imagens performam melhor/pior?
- Quais características das imagens influenciam a qualidade?
- Modelos têm vieses (ex: funcionam melhor em certos ângulos)?

### Ranking Ponderado

O score final é calculado como:

```python
score = (iou_norm × w_iou) + 
        (area_norm × w_area) + 
        (perim_norm × w_perim)
```

Onde:
- Todas as métricas são normalizadas para 0-1
- Diferenças são invertidas (menor = melhor)
- Pesos definem importância relativa

### Interpretação

- **Score > 0.9**: modelo excelente
- **Score 0.7-0.9**: modelo bom
- **Score 0.5-0.7**: modelo médio
- **Score < 0.5**: modelo fraco

## 📝 Workflow Recomendado

1. **Gerar segmentações** usando `01_geracao_mascaras_e_segmentacao.ipynb`
2. **Binarizar máscaras** usando `02_binarizacao_mascaras.ipynb`
3. **Avaliar modelos** usando `03_avaliacao_das_segmentacoes.ipynb`
4. **Analisar resultados**:
   - Verificar ranking final
   - Investigar top/bottom casos
   - Validar visualmente com imagens
5. **Ajustar pesos** se necessário e re-executar ranking
6. **Escolher melhor modelo** baseado no score final

## 🐛 Troubleshooting

### Cache corrompido

```python
import os
from src.config import METRICS_CACHE_PATH

# Deletar cache
if os.path.exists(METRICS_CACHE_PATH):
    os.remove(METRICS_CACHE_PATH)

# Recalcular
collector = MetricsCollector(force_recalculate=True)
df_metrics = collector.collect_all_metrics()
```

### Modelos faltando

Se modelos não aparecem no ranking:
- Verifique se segmentações existem em `generated/segmentada/binarized/`
- Execute notebook 01 para gerar segmentações faltantes
- Recalcule métricas com `force_recalculate=True`

### Erros de visualização

Certifique-se de que matplotlib e seaborn estão instalados:

```bash
pip install matplotlib seaborn
```

## 📚 Referências

- **IoU**: Métrica padrão para segmentação semântica
- **Área/Perímetro**: Métricas complementares para análise morfológica
- **Normalização**: Permite comparação justa entre imagens de diferentes tamanhos
