"""
Calculadora de IoU (Intersection over Union) para máscaras binárias.

Implementa a interface MetricaComparativa para calcular a similaridade
entre duas máscaras através da razão entre interseção e união.
"""

from src.metrics.base import MetricaComparativa
import numpy as np


class IoU(MetricaComparativa):
    @staticmethod
    def calcular(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
        """
        Calcula Intersection over Union entre duas máscaras.

        Args:
            mask_a: Array numpy binário da primeira máscara (valores 0 ou 1)
            mask_b: Array numpy binário da segunda máscara (valores 0 ou 1)

        Returns:
            IoU score entre 0.0 e 1.0
            - 1.0 = máscaras idênticas (100% de sobreposição)
            - 0.0 = sem sobreposição ou ambas vazias

        Examples:
            >>> mask_a = np.array([[1, 1, 0], [1, 0, 0]])
            >>> mask_b = np.array([[1, 0, 0], [1, 1, 0]])
            >>> IoU.calcular(mask_a, mask_b)
            0.5
        """
        intersection = np.logical_and(mask_a, mask_b).sum()
        union = np.logical_or(mask_a, mask_b).sum()

        if union == 0:
            return 0.0

        return float(intersection / union)
