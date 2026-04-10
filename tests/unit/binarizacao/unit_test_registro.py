import pytest

from src.binarizacao import (
    FixedThresholdHighBinarizationStrategy,
    GaussianOpeningLowBinarizationStrategy,
    instanciar_estrategia_binarizacao,
    instanciar_estrategias_binarizacao,
    listar_nomes_estrategias_binarizacao,
)


def test_listar_nomes_estrategias_binarizacao_inclui_gaussiana() -> None:
    assert listar_nomes_estrategias_binarizacao() == [
        "GaussianaOpeningAlta",
        "GaussianaOpeningBaixa",
        "HistereseClosingAlta",
        "HistereseClosingBaixa",
        "LimiarFixoAlta",
        "LimiarFixoBaixa",
        "OtsuOpeningAlta",
        "OtsuOpeningBaixa",
    ]


def test_instanciar_estrategia_binarizacao_resolve_nome_configurado() -> None:
    strategy = instanciar_estrategia_binarizacao("GaussianaOpeningBaixa")

    assert isinstance(strategy, GaussianOpeningLowBinarizationStrategy)
    assert strategy.nome_pasta == "GaussianaOpeningBaixa"


def test_instanciar_estrategias_binarizacao_preserva_ordem() -> None:
    strategies = instanciar_estrategias_binarizacao(
        ["GaussianaOpeningBaixa", "LimiarFixoAlta"]
    )

    assert [strategy.nome_pasta for strategy in strategies] == [
        "GaussianaOpeningBaixa",
        "LimiarFixoAlta",
    ]

    assert isinstance(strategies[1], FixedThresholdHighBinarizationStrategy)


def test_instanciar_estrategia_binarizacao_falha_para_nome_desconhecido() -> None:
    with pytest.raises(ValueError, match="Disponiveis"):
        instanciar_estrategia_binarizacao("Inexistente")
