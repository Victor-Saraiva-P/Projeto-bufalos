import cv2
import numpy as np

from src.metricas.metrica import Metrica


class Perimetro(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        mask_array: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="perimetro", nome_arquivo=nome_arquivo, modelo=modelo)
        self._mask_array = mask_array

    def calcular(self) -> float:
        """
        Calcula perímetro da máscara usando distância Euclidiana.
        """
        contours, _ = cv2.findContours(
            self._mask_array,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_NONE,
        )

        if len(contours) == 0:
            return 0.0

        perimetro_total = sum(cv2.arcLength(cnt, closed=True) for cnt in contours)
        return float(perimetro_total)
