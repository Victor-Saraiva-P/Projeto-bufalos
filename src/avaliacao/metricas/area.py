import numpy as np

from src.metricas.metrica import Metrica


class Area(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        mask_array: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="area", nome_arquivo=nome_arquivo, modelo=modelo)
        self._mask_array = mask_array

    def calcular(self) -> int:
        """
        Calcula área da máscara (número de pixels ativos).
        """
        return int((self._mask_array == 1).sum())
