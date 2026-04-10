from __future__ import annotations

from collections.abc import Iterable

from src.binarizacao.binarizacao_base import BinarizationStrategy
from src.binarizacao.estrategias import (
    FixedThresholdHighBinarizationStrategy,
    FixedThresholdLowBinarizationStrategy,
    GaussianOpeningHighBinarizationStrategy,
    GaussianOpeningLowBinarizationStrategy,
    GroundTruthGlobalThresholdBinarizationStrategy,
    HysteresisClosingHighBinarizationStrategy,
    HysteresisClosingLowBinarizationStrategy,
    OtsuOpeningHighBinarizationStrategy,
    OtsuOpeningLowBinarizationStrategy,
)


_GROUND_TRUTH_STRATEGY_FACTORIES = {
    "GroundTruthLimiarGlobal": GroundTruthGlobalThresholdBinarizationStrategy,
}

_SEGMENTACAO_STRATEGY_FACTORIES = {
    "GaussianaOpeningAlta": GaussianOpeningHighBinarizationStrategy,
    "GaussianaOpeningBaixa": GaussianOpeningLowBinarizationStrategy,
    "HistereseClosingAlta": HysteresisClosingHighBinarizationStrategy,
    "HistereseClosingBaixa": HysteresisClosingLowBinarizationStrategy,
    "LimiarFixoAlta": FixedThresholdHighBinarizationStrategy,
    "LimiarFixoBaixa": FixedThresholdLowBinarizationStrategy,
    "OtsuOpeningAlta": OtsuOpeningHighBinarizationStrategy,
    "OtsuOpeningBaixa": OtsuOpeningLowBinarizationStrategy,
}


def _listar_nomes(factories: dict[str, type[BinarizationStrategy]]) -> list[str]:
    return sorted(factories)


def _instanciar_estrategia(
    nome: str,
    factories: dict[str, type[BinarizationStrategy]],
    contexto: str,
) -> BinarizationStrategy:
    factory = factories.get(nome)
    if factory is None:
        disponiveis = ", ".join(_listar_nomes(factories))
        raise ValueError(
            f"Estrategia de binarizacao desconhecida para {contexto}: "
            f"{nome}. Disponiveis: {disponiveis}."
        )
    return factory()


def listar_nomes_estrategias_ground_truth_binarizacao() -> list[str]:
    return _listar_nomes(_GROUND_TRUTH_STRATEGY_FACTORIES)


def listar_nomes_estrategias_segmentacao_binarizacao() -> list[str]:
    return _listar_nomes(_SEGMENTACAO_STRATEGY_FACTORIES)


def instanciar_estrategia_ground_truth_binarizacao(nome: str) -> BinarizationStrategy:
    return _instanciar_estrategia(
        nome,
        _GROUND_TRUTH_STRATEGY_FACTORIES,
        contexto="ground truth",
    )


def instanciar_estrategia_segmentacao_binarizacao(nome: str) -> BinarizationStrategy:
    return _instanciar_estrategia(
        nome,
        _SEGMENTACAO_STRATEGY_FACTORIES,
        contexto="segmentacao",
    )


def instanciar_estrategias_segmentacao_binarizacao(
    nomes: Iterable[str],
) -> list[BinarizationStrategy]:
    return [instanciar_estrategia_segmentacao_binarizacao(nome) for nome in nomes]
