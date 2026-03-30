"""
Métricas de avaliação para máscaras de segmentação.

Classes:
    Area: Calcula área (número de pixels ativos)
    Perimetro: Calcula perímetro (distância Euclidiana)
    IoU: Calcula Intersection over Union entre duas máscaras
"""

from src.avaliacao.metricas.area import Area
from src.avaliacao.metricas.iou import IoU
from src.avaliacao.metricas.perimetro import Perimetro

__all__ = ["Area", "Perimetro", "IoU"]
