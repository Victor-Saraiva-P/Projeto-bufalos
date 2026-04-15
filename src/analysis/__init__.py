"""
Módulo de análise de métricas de segmentação.

Este módulo fornece ferramentas para:
- Coletar e processar métricas persistidas no SQLite (MetricsCollector)
- Calcular estatísticas descritivas genéricas por métrica
"""

from src.analysis.collector import MetricsCollector, build_binarized_metrics_dataframe
from src.analysis.bootstrap import build_bootstrap_confidence_intervals
from src.analysis.final_validation import (
    build_finalist_base,
    build_threshold_decision_table,
    select_best_strategies_for_models,
    select_top_models_for_final_validation,
)
from src.analysis.descriptive_stats import (
    MetricConfig,
    RAW_METRIC_CONFIGS,
    build_descriptive_stats,
)
from src.analysis.scenario_analysis import (
    SCENARIO_APENAS_OK,
    SCENARIO_CENARIO_IDEAL,
    SCENARIO_DATASET_COMPLETO,
    ScenarioSlice,
    build_analysis_scenarios,
    build_best_entities_by_scenario,
    build_focus_model_strategy_rankings,
    build_negative_tag_impact_overview,
    build_scenario_rankings,
    build_strategy_rankings_within_model_by_scenario,
    identify_negative_impact_tags,
)
from src.analysis.persistence import (
    BINARIZED_METRIC_CONFIGS,
    build_and_persist_analysis_segmentacao_binarizada_estabilidade,
    build_and_persist_analysis_segmentacao_binarizada_interacao_tag_estrategia,
    build_and_persist_analysis_segmentacao_binarizada_intervalo_confianca,
    build_and_persist_analysis_segmentacao_binarizada_resumo_estrategia,
    build_and_persist_analysis_segmentacao_binarizada_resumo_execucao,
    build_and_persist_analysis_segmentacao_binarizada_resumo_modelo_estrategia,
    build_and_persist_analysis_segmentacao_binarizada_resumo_tag,
    build_and_persist_analysis_segmentacao_binarizada_testes_estrategia,
    build_and_persist_analysis_segmentacao_binarizada_testes_tag_estrategia,
    build_and_persist_analysis_segmentacao_bruta_estabilidade,
    build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo,
    build_and_persist_analysis_segmentacao_bruta_intervalo_confianca,
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao,
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    build_and_persist_analysis_segmentacao_bruta_resumo_tag,
    build_and_persist_analysis_segmentacao_bruta_testes_modelo,
    build_and_persist_analysis_segmentacao_bruta_testes_tag,
)
from src.analysis.stability import build_execution_stability
from src.analysis.statistical_tests import (
    GLOBAL_SCOPE,
    build_model_comparison_tests,
    build_model_tag_interactions,
    build_tag_impact_tests,
    cliffs_delta,
    cliffs_delta_label,
    holm_adjust,
)

__all__ = [
    "MetricsCollector",
    "BINARIZED_METRIC_CONFIGS",
    "GLOBAL_SCOPE",
    "MetricConfig",
    "RAW_METRIC_CONFIGS",
    "SCENARIO_APENAS_OK",
    "SCENARIO_CENARIO_IDEAL",
    "SCENARIO_DATASET_COMPLETO",
    "ScenarioSlice",
    "build_binarized_metrics_dataframe",
    "build_analysis_scenarios",
    "build_best_entities_by_scenario",
    "build_bootstrap_confidence_intervals",
    "build_descriptive_stats",
    "build_execution_stability",
    "build_finalist_base",
    "build_focus_model_strategy_rankings",
    "build_model_comparison_tests",
    "build_model_tag_interactions",
    "build_negative_tag_impact_overview",
    "build_scenario_rankings",
    "build_threshold_decision_table",
    "build_strategy_rankings_within_model_by_scenario",
    "build_tag_impact_tests",
    "cliffs_delta",
    "cliffs_delta_label",
    "holm_adjust",
    "identify_negative_impact_tags",
    "select_best_strategies_for_models",
    "select_top_models_for_final_validation",
    "build_and_persist_analysis_segmentacao_binarizada_estabilidade",
    "build_and_persist_analysis_segmentacao_binarizada_interacao_tag_estrategia",
    "build_and_persist_analysis_segmentacao_binarizada_intervalo_confianca",
    "build_and_persist_analysis_segmentacao_binarizada_resumo_estrategia",
    "build_and_persist_analysis_segmentacao_binarizada_resumo_execucao",
    "build_and_persist_analysis_segmentacao_binarizada_resumo_modelo_estrategia",
    "build_and_persist_analysis_segmentacao_binarizada_resumo_tag",
    "build_and_persist_analysis_segmentacao_binarizada_testes_estrategia",
    "build_and_persist_analysis_segmentacao_binarizada_testes_tag_estrategia",
    "build_and_persist_analysis_segmentacao_bruta_estabilidade",
    "build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo",
    "build_and_persist_analysis_segmentacao_bruta_intervalo_confianca",
    "build_and_persist_analysis_segmentacao_bruta_resumo_execucao",
    "build_and_persist_analysis_segmentacao_bruta_resumo_modelo",
    "build_and_persist_analysis_segmentacao_bruta_resumo_tag",
    "build_and_persist_analysis_segmentacao_bruta_testes_modelo",
    "build_and_persist_analysis_segmentacao_bruta_testes_tag",
]
