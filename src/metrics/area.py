from src.metrics.base import MetricaSimples
import numpy as np


class Area(MetricaSimples):

    @staticmethod
    def calcular(mask_array: np.ndarray) -> int:
        """
        Calcula área da máscara (número de pixels ativos).

        Args:
            mask_array: Array numpy binário (valores 0 ou 1)

        Returns:
            Área em pixels (número de pixels com valor 1)

        Examples:
            >>> mask = np.array([[1, 1, 0], [1, 0, 0]])
            >>> Area.calcular(mask)
            3
        """
        return int((mask_array == 1).sum())
