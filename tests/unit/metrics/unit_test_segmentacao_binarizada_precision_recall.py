import math

import numpy as np

from src.metricas import Precision, Recall


def test_precision_calcula_true_positives_sobre_preditos_positivos() -> None:
    resultado = Precision(
        nome_arquivo="bufalo_001",
        mask_modelo=np.array([[1, 1], [0, 0]], dtype=np.uint8),
        mask_ground_truth=np.array([[1, 0], [1, 0]], dtype=np.uint8),
        modelo="u2netp",
    ).calcular()

    assert math.isclose(resultado, 0.5, rel_tol=1e-9)


def test_precision_retorna_zero_quando_nao_ha_preditos_positivos() -> None:
    resultado = Precision(
        nome_arquivo="bufalo_001",
        mask_modelo=np.zeros((2, 2), dtype=np.uint8),
        mask_ground_truth=np.array([[1, 0], [1, 0]], dtype=np.uint8),
    ).calcular()

    assert resultado == 0.0


def test_recall_calcula_true_positives_sobre_positivos_reais() -> None:
    resultado = Recall(
        nome_arquivo="bufalo_001",
        mask_modelo=np.array([[1, 0], [0, 0]], dtype=np.uint8),
        mask_ground_truth=np.array([[1, 0], [1, 0]], dtype=np.uint8),
        modelo="u2netp",
    ).calcular()

    assert math.isclose(resultado, 0.5, rel_tol=1e-9)


def test_recall_retorna_zero_quando_nao_ha_positivos_reais() -> None:
    resultado = Recall(
        nome_arquivo="bufalo_001",
        mask_modelo=np.array([[1, 0], [1, 0]], dtype=np.uint8),
        mask_ground_truth=np.zeros((2, 2), dtype=np.uint8),
    ).calcular()

    assert resultado == 0.0
