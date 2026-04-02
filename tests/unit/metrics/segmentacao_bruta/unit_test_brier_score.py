import math

import numpy as np
import pytest

from src.metricas import BrierScore


def test_brier_score_retorna_zero_quando_probabilidade_e_perfeita() -> None:
    score_mask = np.array([[1.0, 1.0], [0.0, 0.0]], dtype=np.float64)
    ground_truth_mask = np.array([[1, 1], [0, 0]], dtype=np.uint8)

    resultado = BrierScore(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
        modelo="u2netp",
    ).calcular()

    assert resultado == 0.0


def test_brier_score_calcula_erro_quadratico_medio() -> None:
    score_mask = np.array([[0.9, 0.2], [0.8, 0.1]], dtype=np.float64)
    ground_truth_mask = np.array([[1, 0], [1, 0]], dtype=np.uint8)

    resultado = BrierScore(
        nome_arquivo="bufalo_001",
        score_mask=score_mask,
        ground_truth_mask=ground_truth_mask,
    ).calcular()

    assert math.isclose(resultado, 0.025, rel_tol=1e-9)


def test_brier_score_pune_excesso_de_confianca_no_fundo() -> None:
    ground_truth_mask = np.array([[1, 1], [0, 0]], dtype=np.uint8)

    resultado_cauteloso = BrierScore(
        nome_arquivo="bufalo_001",
        score_mask=np.array([[0.6, 0.6], [0.05, 0.05]], dtype=np.float64),
        ground_truth_mask=ground_truth_mask,
    ).calcular()
    resultado_excessivamente_confiante = BrierScore(
        nome_arquivo="bufalo_001",
        score_mask=np.array([[0.6, 0.6], [0.2, 0.2]], dtype=np.float64),
        ground_truth_mask=ground_truth_mask,
    ).calcular()

    assert resultado_cauteloso < resultado_excessivamente_confiante


def test_brier_score_rejeita_mascaras_com_shapes_diferentes() -> None:
    with pytest.raises(ValueError, match="mesmo shape"):
        BrierScore(
            nome_arquivo="bufalo_001",
            score_mask=np.ones((2, 2)),
            ground_truth_mask=np.ones((2, 3), dtype=np.uint8),
        )


def test_brier_score_rejeita_ground_truth_nao_binaria() -> None:
    with pytest.raises(ValueError, match="binaria"):
        BrierScore(
            nome_arquivo="bufalo_001",
            score_mask=np.ones((2, 2)),
            ground_truth_mask=np.array([[0, 1], [2, 0]], dtype=np.uint8),
        )


def test_brier_score_rejeita_mascaras_vazias() -> None:
    with pytest.raises(ValueError, match="nao podem ser vazios"):
        BrierScore(
            nome_arquivo="bufalo_001",
            score_mask=np.array([], dtype=np.float64),
            ground_truth_mask=np.array([], dtype=np.uint8),
        )


def test_brier_score_rejeita_scores_fora_da_faixa_probabilistica() -> None:
    with pytest.raises(ValueError, match="0 e 1"):
        BrierScore(
            nome_arquivo="bufalo_001",
            score_mask=np.array([[1.2, -0.1]], dtype=np.float64),
            ground_truth_mask=np.array([[1, 0]], dtype=np.uint8),
        )
