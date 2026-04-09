"""
Módulo de análise de métricas de segmentação.

Este módulo fornece ferramentas para:
- Coletar e processar métricas persistidas no SQLite (MetricsCollector)
- Calcular estatísticas descritivas genéricas por métrica
"""

from src.analysis.collector import MetricsCollector
from src.analysis.descriptive_stats import (
    MetricConfig,
    RAW_METRIC_CONFIGS,
    build_descriptive_stats,
)
from src.analysis.persistence import persist_analysis_segmentacao_bruta_base
from src.analysis.persistence import (
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
)

__all__ = [
    "MetricsCollector",
    "MetricConfig",
    "RAW_METRIC_CONFIGS",
    "build_descriptive_stats",
    "build_and_persist_analysis_segmentacao_bruta_resumo_modelo",
    "persist_analysis_segmentacao_bruta_base",
]
