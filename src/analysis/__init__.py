"""
Módulo de análise de métricas de segmentação.

Este módulo fornece ferramentas para:
- Coletar e processar métricas persistidas no SQLite (MetricsCollector)
"""

from src.analysis.collector import MetricsCollector

__all__ = ["MetricsCollector"]
