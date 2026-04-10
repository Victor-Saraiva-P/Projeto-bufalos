"""
Módulo de visualização de métricas e resultados.

Este módulo fornece ferramentas para:
- Visualizar grids de imagens e comparações pontuais (image_grid)
- Visualizar resumos e distribuições da segmentação bruta
"""

from src.visualization.image_grid import (
    plot_image_grid,
    plot_single_image_comparison,
)
from src.visualization.pdf_report import PdfReportSection, save_pdf_report
from src.visualization.segmentacao_bruta_plots import (
    plot_metric_bars_with_ci_by_model,
    plot_metric_bars_by_model,
    plot_metric_correlation_heatmap,
    plot_metric_by_execution_heatmap,
    plot_metric_distribution_by_model,
    plot_metric_distribution_by_tag,
    plot_metric_scatter,
    plot_model_tag_interaction_heatmap,
    plot_pairwise_pvalue_heatmap,
    plot_simple_regression,
    plot_stability_heatmap,
    plot_tag_effect_bars,
    plot_metric_tag_comparison,
)

__all__ = [
    "plot_image_grid",
    "plot_single_image_comparison",
    "PdfReportSection",
    "save_pdf_report",
    "plot_metric_bars_with_ci_by_model",
    "plot_metric_bars_by_model",
    "plot_metric_correlation_heatmap",
    "plot_metric_by_execution_heatmap",
    "plot_metric_distribution_by_model",
    "plot_metric_distribution_by_tag",
    "plot_metric_scatter",
    "plot_model_tag_interaction_heatmap",
    "plot_pairwise_pvalue_heatmap",
    "plot_simple_regression",
    "plot_stability_heatmap",
    "plot_tag_effect_bars",
    "plot_metric_tag_comparison",
]
