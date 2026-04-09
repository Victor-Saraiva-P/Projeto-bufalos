import pytest

from src.binarizacao import (
    GaussianOpeningBinarizationStrategy,
    GroundTruthGlobalThresholdBinarizationStrategy,
    instanciar_estrategia_ground_truth_binarizacao,
    instanciar_estrategia_segmentacao_binarizacao,
    instanciar_estrategias_segmentacao_binarizacao,
    listar_nomes_estrategias_ground_truth_binarizacao,
    listar_nomes_estrategias_segmentacao_binarizacao,
)


def test_listar_nomes_estrategias_ground_truth_inclui_limiar_global() -> None:
    assert listar_nomes_estrategias_ground_truth_binarizacao() == [
        "GroundTruthLimiarGlobal"
    ]


def test_listar_nomes_estrategias_segmentacao_inclui_gaussiana() -> None:
    assert listar_nomes_estrategias_segmentacao_binarizacao() == ["GaussianaOpening"]


def test_instanciar_estrategia_ground_truth_resolve_nome_configurado() -> None:
    strategy = instanciar_estrategia_ground_truth_binarizacao("GroundTruthLimiarGlobal")

    assert isinstance(strategy, GroundTruthGlobalThresholdBinarizationStrategy)
    assert strategy.nome_pasta == "GroundTruthLimiarGlobal"


def test_instanciar_estrategia_segmentacao_resolve_nome_configurado() -> None:
    strategy = instanciar_estrategia_segmentacao_binarizacao("GaussianaOpening")

    assert isinstance(strategy, GaussianOpeningBinarizationStrategy)
    assert strategy.nome_pasta == "GaussianaOpening"


def test_instanciar_estrategias_segmentacao_preserva_ordem() -> None:
    strategies = instanciar_estrategias_segmentacao_binarizacao(
        ["GaussianaOpening", "GaussianaOpening"]
    )

    assert [strategy.nome_pasta for strategy in strategies] == [
        "GaussianaOpening",
        "GaussianaOpening",
    ]


def test_instanciar_estrategia_ground_truth_falha_para_nome_desconhecido() -> None:
    with pytest.raises(ValueError, match="ground truth"):
        instanciar_estrategia_ground_truth_binarizacao("Inexistente")


def test_instanciar_estrategia_segmentacao_falha_para_nome_desconhecido() -> None:
    with pytest.raises(ValueError, match="segmentacao"):
        instanciar_estrategia_segmentacao_binarizacao("GroundTruthLimiarGlobal")


def test_instanciar_estrategia_binarizacao_falha_listando_disponiveis() -> None:
    with pytest.raises(ValueError, match="Disponiveis"):
        instanciar_estrategia_segmentacao_binarizacao("Inexistente")
