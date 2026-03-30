"""
Calculadora de IoU (Intersection over Union) para mascaras binarias.

Calcula a similaridade entre duas mascaras atraves da razao entre
intersecao e uniao.
"""

import numpy as np

from src.metricas.metrica_base import Metrica


class IoU(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        mask_modelo: np.ndarray,
        mask_ground_truth: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="iou", nome_arquivo=nome_arquivo, modelo=modelo)
        self._mask_modelo = mask_modelo
        self._mask_ground_truth = mask_ground_truth

    def calcular(self) -> float:
        """
        Calcula Intersection over Union entre duas mascaras.
        """
        intersection = np.logical_and(self._mask_modelo, self._mask_ground_truth).sum()
        union = np.logical_or(self._mask_modelo, self._mask_ground_truth).sum()

        if union == 0:
            return 0.0

        return float(intersection / union)
