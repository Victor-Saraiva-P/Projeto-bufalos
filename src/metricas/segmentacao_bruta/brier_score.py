from __future__ import annotations

import numpy as np

from src.metricas.metrica_base import Metrica


class BrierScore(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        score_mask: np.ndarray,
        ground_truth_mask: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="brier_score", nome_arquivo=nome_arquivo, modelo=modelo)
        self._score_mask = np.asarray(score_mask, dtype=np.float64)
        self._ground_truth_mask = np.asarray(ground_truth_mask)
        self._validar_entradas()

    def calcular(self) -> float:
        scores = self._score_mask.reshape(-1)
        ground_truth = self._ground_truth_mask.astype(np.float64, copy=False).reshape(-1)
        return float(np.mean((scores - ground_truth) ** 2))

    def _validar_entradas(self) -> None:
        if self._score_mask.shape != self._ground_truth_mask.shape:
            raise ValueError(
                "score_mask e ground_truth_mask precisam ter o mesmo shape."
            )

        if self._score_mask.size == 0:
            raise ValueError("score_mask e ground_truth_mask nao podem ser vazios.")

        valores_gt = np.unique(self._ground_truth_mask)
        if not np.all(np.isin(valores_gt, (0, 1, False, True))):
            raise ValueError("ground_truth_mask precisa ser binaria.")

        if np.any((self._score_mask < 0.0) | (self._score_mask > 1.0)):
            raise ValueError("score_mask precisa conter valores entre 0 e 1.")
