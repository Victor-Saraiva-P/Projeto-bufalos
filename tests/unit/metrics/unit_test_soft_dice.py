import numpy as np
import pytest


def _soft_dice_class():
    try:
        from src.metricas.segmentacao_bruta.soft_dice import SoftDice
    except ImportError as exc:
        pytest.fail(
            "SoftDice ainda nao esta disponivel em "
            f"src.metricas.segmentacao_bruta.soft_dice: {exc}"
        )
    return SoftDice


def _criar_soft_dice(
    *,
    score_mask: list[list[float]] | np.ndarray,
    ground_truth_mask: list[list[int]] | np.ndarray,
):
    soft_dice_class = _soft_dice_class()
    return soft_dice_class(
        nome_arquivo="bufalo_001",
        score_mask=np.asarray(score_mask, dtype=np.float64),
        ground_truth_mask=np.asarray(ground_truth_mask),
        modelo="u2netp",
    )


def test_soft_dice_esta_disponivel_na_api_publica_de_metricas() -> None:
    try:
        from src.metricas import SoftDice
    except ImportError as exc:
        pytest.fail(f"SoftDice ainda nao foi exportado por src.metricas: {exc}")

    assert SoftDice.__name__ == "SoftDice"


def test_soft_dice_retorna_1_quando_score_e_ground_truth_coincidem() -> None:
    metrica = _criar_soft_dice(
        score_mask=[[1.0, 1.0], [0.0, 0.0]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )

    assert metrica.calcular() == pytest.approx(1.0)


def test_soft_dice_aplica_a_formula_da_sobreposicao_ponderada() -> None:
    metrica = _criar_soft_dice(
        score_mask=[[0.9, 0.6], [0.0, 0.0]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )

    esperado = (2 * (0.9 + 0.6)) / ((0.9 + 0.6) + 2.0)

    assert metrica.calcular() == pytest.approx(esperado)


def test_soft_dice_cai_quando_ha_vazamento_de_score_no_fundo() -> None:
    concentrado_no_bufalo = _criar_soft_dice(
        score_mask=[[0.9, 0.8], [0.0, 0.0]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )
    com_vazamento = _criar_soft_dice(
        score_mask=[[0.9, 0.8], [0.4, 0.3]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )

    assert com_vazamento.calcular() < concentrado_no_bufalo.calcular()


def test_soft_dice_cai_quando_o_modelo_cobre_apenas_parte_do_bufalo() -> None:
    cobertura_completa = _criar_soft_dice(
        score_mask=[[0.9, 0.8], [0.0, 0.0]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )
    cobertura_incompleta = _criar_soft_dice(
        score_mask=[[0.9, 0.0], [0.0, 0.0]],
        ground_truth_mask=[[1, 1], [0, 0]],
    )

    assert cobertura_incompleta.calcular() < cobertura_completa.calcular()


def test_soft_dice_rejeita_masks_com_shapes_diferentes() -> None:
    with pytest.raises(ValueError, match="mesmo shape"):
        _criar_soft_dice(
            score_mask=[[0.9, 0.8]],
            ground_truth_mask=[[1, 1], [0, 0]],
        )


def test_soft_dice_rejeita_masks_vazias() -> None:
    with pytest.raises(ValueError, match="nao podem ser vazios"):
        _criar_soft_dice(
            score_mask=np.array([], dtype=np.float64),
            ground_truth_mask=np.array([], dtype=np.uint8),
        )


def test_soft_dice_exige_ground_truth_binario() -> None:
    with pytest.raises(ValueError, match="binaria"):
        _criar_soft_dice(
            score_mask=[[0.9, 0.8], [0.0, 0.0]],
            ground_truth_mask=[[1, 2], [0, 0]],
        )


def test_soft_dice_exige_score_mask_no_intervalo_unitario() -> None:
    with pytest.raises(ValueError, match="0 e 1"):
        _criar_soft_dice(
            score_mask=[[1.2, 0.8], [0.0, -0.1]],
            ground_truth_mask=[[1, 1], [0, 0]],
        )
