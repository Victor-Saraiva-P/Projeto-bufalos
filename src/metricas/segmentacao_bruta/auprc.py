from __future__ import annotations

import numpy as np

from src.metricas.metrica_base import Metrica


class AUPRC(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        score_mask: np.ndarray,
        ground_truth_mask: np.ndarray,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="auprc", nome_arquivo=nome_arquivo, modelo=modelo)
        self._score_mask = np.asarray(score_mask, dtype=np.float64)
        self._ground_truth_mask = np.asarray(ground_truth_mask)
        self._validar_entradas()

    def calcular(self) -> float:
        scores = self._score_mask.reshape(-1)
        ground_truth = self._ground_truth_mask.astype(np.uint8, copy=False).reshape(-1)

        total_positivos = int(ground_truth.sum())
        if total_positivos == 0:
            return 0.0

        ordem_descendente = np.argsort(-scores, kind="mergesort")
        ground_truth_ordenado = ground_truth[ordem_descendente]
        scores_ordenados = scores[ordem_descendente]

        verdadeiros_positivos = np.cumsum(ground_truth_ordenado == 1)
        falsos_positivos = np.cumsum(ground_truth_ordenado == 0)

        indices_distintos = np.where(np.diff(scores_ordenados) != 0)[0]
        indices_threshold = np.r_[indices_distintos, len(scores_ordenados) - 1]

        verdadeiros_positivos = verdadeiros_positivos[indices_threshold]
        falsos_positivos = falsos_positivos[indices_threshold]

        precisao = verdadeiros_positivos / (verdadeiros_positivos + falsos_positivos)
        recall = verdadeiros_positivos / total_positivos

        recall_anterior = np.r_[0.0, recall[:-1]]
        return float(np.sum((recall - recall_anterior) * precisao))

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
