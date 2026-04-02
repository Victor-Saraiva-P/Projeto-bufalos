from __future__ import annotations

from collections.abc import Iterable

from src.binarizacao.binarizacao_base import BinarizationStrategy
from src.binarizacao.estrategias import GaussianOpeningBinarizationStrategy


_STRATEGY_FACTORIES = {
    "GaussianaOpening": GaussianOpeningBinarizationStrategy,
}


def listar_nomes_estrategias_binarizacao() -> list[str]:
    return sorted(_STRATEGY_FACTORIES)


def instanciar_estrategia_binarizacao(nome: str) -> BinarizationStrategy:
    factory = _STRATEGY_FACTORIES.get(nome)
    if factory is None:
        disponiveis = ", ".join(listar_nomes_estrategias_binarizacao())
        raise ValueError(
            "Estrategia de binarizacao desconhecida: "
            f"{nome}. Disponiveis: {disponiveis}."
        )
    return factory()


def instanciar_estrategias_binarizacao(
    nomes: Iterable[str],
) -> list[BinarizationStrategy]:
    return [instanciar_estrategia_binarizacao(nome) for nome in nomes]
