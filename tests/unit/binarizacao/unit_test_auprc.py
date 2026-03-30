import math

import numpy as np
import pytest

from src.binarizacao import AUPRC


def test_auprc_retorna_1_quando_separacao_e_perfeita() -> None:
    score_mask = np.array([[0.95, 0.80], [0.20, 0.05]])
    ground_truth_mask = np.array([[1, 1], [0, 0]], dtype=np.uint8)

    resultado = AUPRC(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
        modelo="u2netp",
    ).calcular()

    assert resultado == 1.0


def test_auprc_usa_media_de_precisao_quando_scores_sao_iguais() -> None:
    score_mask = np.full((2, 2), 0.5)
    ground_truth_mask = np.array([[1, 0], [1, 0]], dtype=np.uint8)

    resultado = AUPRC(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
    ).calcular()

    assert resultado == 0.5


def test_auprc_calcula_valor_intermediario_com_ordenacao_imperfeita() -> None:
    score_mask = np.array([[0.9, 0.8], [0.7, 0.1]])
    ground_truth_mask = np.array([[1, 0], [1, 0]], dtype=np.uint8)

    resultado = AUPRC(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
    ).calcular()

    assert math.isclose(resultado, 5 / 6, rel_tol=1e-9)


def test_auprc_retorna_zero_quando_nao_ha_pixels_positivos() -> None:
    score_mask = np.array([[0.9, 0.2], [0.4, 0.1]])
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)

    resultado = AUPRC(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
    ).calcular()

    assert resultado == 0.0


def test_auprc_rejeita_mascaras_com_shapes_diferentes() -> None:
    with pytest.raises(ValueError, match="mesmo shape"):
        AUPRC(
            nome_arquivo="bufalo_001",
            score_mask=np.ones((2, 2)),
            ground_truth_mask=np.ones((2, 3), dtype=np.uint8),
        )


def test_auprc_rejeita_ground_truth_nao_binaria() -> None:
    with pytest.raises(ValueError, match="binaria"):
        AUPRC(
            nome_arquivo="bufalo_001",
            score_mask=np.ones((2, 2)),
            ground_truth_mask=np.array([[0, 1], [2, 0]], dtype=np.uint8),
        )


def test_auprc_rejeita_mascaras_vazias() -> None:
    with pytest.raises(ValueError, match="nao podem ser vazios"):
        AUPRC(
            nome_arquivo="bufalo_001",
            score_mask=np.array([], dtype=np.float64),
            ground_truth_mask=np.array([], dtype=np.uint8),
        )
