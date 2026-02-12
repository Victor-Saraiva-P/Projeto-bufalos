from abc import ABC, abstractmethod
import numpy as np
from typing import Union


class MetricaSimples(ABC):
    @staticmethod
    @abstractmethod
    def calcular(mask_array: np.ndarray) -> Union[int, float]:
        """
        Calcula métrica a partir de uma máscara.

        Args:
            mask_array: Array numpy binário (valores 0 ou 1)

        Returns:
            Valor numérico da métrica (int ou float)
        """
        pass


class MetricaComparativa(ABC):
    @staticmethod
    @abstractmethod
    def calcular(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
        """
        Calcula métrica comparativa entre duas máscaras.

        Args:
            mask_a: Array numpy binário da primeira máscara
            mask_b: Array numpy binário da segunda máscara

        Returns:
            Valor da métrica (sempre float para métricas comparativas)
        """
        pass
