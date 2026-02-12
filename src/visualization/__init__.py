"""
Módulo de visualização de métricas e resultados.

Este módulo fornece ferramentas para:
- Gerar gráficos de análise de métricas (metric_plots)
- Visualizar grids de imagens com top/bottom resultados (image_grid)
"""

from src.visualization.metric_plots import (
    setup_plot_style,
    plot_iou_analysis,
    plot_area_analysis,
    plot_perimetro_analysis,
    plot_ranking_analysis,
    get_top_bottom_iou,
    get_top_bottom_area,
    get_top_bottom_perimetro,
)

from src.visualization.image_grid import (
    plot_image_grid,
    plot_single_image_comparison,
)

__all__ = [
    "setup_plot_style",
    "plot_iou_analysis",
    "plot_area_analysis",
    "plot_perimetro_analysis",
    "plot_ranking_analysis",
    "get_top_bottom_iou",
    "get_top_bottom_area",
    "get_top_bottom_perimetro",
    "plot_image_grid",
    "plot_single_image_comparison",
]
