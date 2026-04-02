import pytest

from src.binarizacao import (
    GaussianOpeningBinarizationStrategy,
    instanciar_estrategia_binarizacao,
    instanciar_estrategias_binarizacao,
    listar_nomes_estrategias_binarizacao,
)


def test_listar_nomes_estrategias_binarizacao_inclui_gaussiana() -> None:
    assert listar_nomes_estrategias_binarizacao() == ["GaussianaOpening"]


def test_instanciar_estrategia_binarizacao_resolve_nome_configurado() -> None:
    strategy = instanciar_estrategia_binarizacao("GaussianaOpening")

    assert isinstance(strategy, GaussianOpeningBinarizationStrategy)
    assert strategy.nome_pasta == "GaussianaOpening"


def test_instanciar_estrategias_binarizacao_preserva_ordem() -> None:
    strategies = instanciar_estrategias_binarizacao(
        ["GaussianaOpening", "GaussianaOpening"]
    )

    assert [strategy.nome_pasta for strategy in strategies] == [
        "GaussianaOpening",
        "GaussianaOpening",
    ]


def test_instanciar_estrategia_binarizacao_falha_para_nome_desconhecido() -> None:
    with pytest.raises(ValueError, match="Disponiveis"):
        instanciar_estrategia_binarizacao("Inexistente")
