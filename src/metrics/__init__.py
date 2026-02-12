"""
Módulo de cálculo de métricas para máscaras de segmentação.

Segue o padrão Strategy com interfaces ABC para garantir consistência.
Cada métrica é uma classe especializada com responsabilidade única.

Classes:
    Area: Calcula área (número de pixels ativos)
    Perimetro: Calcula perímetro (distância Euclidiana)
    IoU: Calcula Intersection over Union entre duas máscaras
"""

from src.metrics.area import Area
from src.metrics.perimetro import Perimetro
from src.metrics.iou import IoU

__all__ = ["Area", "Perimetro", "IoU"]
