import numpy as np

from src.metricas.metrica_base import Metrica


class Precision(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        mask_modelo: np.ndarray,
        mask_ground_truth: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="precision", nome_arquivo=nome_arquivo, modelo=modelo)
        self._mask_modelo = mask_modelo
        self._mask_ground_truth = mask_ground_truth

    def calcular(self) -> float:
        true_positives = np.logical_and(self._mask_modelo, self._mask_ground_truth).sum()
        false_positives = np.logical_and(
            self._mask_modelo,
            np.logical_not(self._mask_ground_truth),
        ).sum()
        predicted_positives = true_positives + false_positives

        if predicted_positives == 0:
            return 0.0

        return float(true_positives / predicted_positives)
