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

__all__ = [
    "MetricsCollector",
    "MetricConfig",
    "RAW_METRIC_CONFIGS",
    "build_descriptive_stats",
]
