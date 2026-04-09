"""
Módulo de visualização de métricas e resultados.

Este módulo fornece ferramentas para:
- Visualizar grids de imagens e comparações pontuais (image_grid)
"""

from src.visualization.image_grid import (
    plot_image_grid,
    plot_single_image_comparison,
)

__all__ = [
    "plot_image_grid",
    "plot_single_image_comparison",
]
