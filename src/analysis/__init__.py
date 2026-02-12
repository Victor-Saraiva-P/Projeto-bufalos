"""
Módulo de análise de métricas de segmentação.

Este módulo fornece ferramentas para:
- Coletar e processar métricas de todos os modelos (MetricsCollector)
- Calcular rankings ponderados dos modelos (ModelRanker)
"""

from src.analysis.collector import MetricsCollector
from src.analysis.ranker import ModelRanker

__all__ = ["MetricsCollector", "ModelRanker"]
