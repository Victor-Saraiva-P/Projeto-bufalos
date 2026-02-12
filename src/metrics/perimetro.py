from src.metrics.base import MetricaSimples
import numpy as np
import cv2


class Perimetro(MetricaSimples):

    @staticmethod
    def calcular(mask_array: np.ndarray) -> float:
        """
        Calcula perímetro da máscara usando distância Euclidiana.

        Args:
            mask_array: Array numpy binário (valores 0 ou 1)

        Returns:
            Perímetro em pixels (distância Euclidiana)
            Retorna 0.0 se não houver contornos na máscara

        Examples:
            >>> mask = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
            >>> perimetro = Perimetro.calcular(mask)
            >>> perimetro > 0
            True
        """
        # Encontra contornos externos
        contours, _ = cv2.findContours(
            mask_array,
            cv2.RETR_EXTERNAL,  # Apenas contorno externo
            cv2.CHAIN_APPROX_NONE,  # Todos os pontos (sem aproximação)
        )

        if len(contours) == 0:
            return 0.0

        # Soma perímetro de todos os contornos
        perimetro_total = sum(cv2.arcLength(cnt, closed=True) for cnt in contours)

        return float(perimetro_total)
