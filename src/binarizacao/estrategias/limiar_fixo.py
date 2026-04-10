from dataclasses import dataclass

import numpy as np
from PIL import Image

from src.binarizacao.binarizacao_base import gerar_nome_pasta_binarizacao


def _carregar_matriz_cinza(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("L"), dtype=np.float32)


@dataclass(frozen=True)
class FixedThresholdBinarizationStrategy:
    nome_base: str
    threshold: float

    @property
    def nome(self) -> str:
        return self.nome_base

    @property
    def nome_pasta(self) -> str:
        return gerar_nome_pasta_binarizacao(self.nome)

    def binarizar(self, image: Image.Image) -> Image.Image:
        matriz = _carregar_matriz_cinza(image)
        matriz_final = ((matriz > self.threshold) * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")


@dataclass(frozen=True)
class FixedThresholdLowBinarizationStrategy(FixedThresholdBinarizationStrategy):
    nome_base: str = "LimiarFixoBaixa"
    threshold: float = 88.0


@dataclass(frozen=True)
class FixedThresholdHighBinarizationStrategy(FixedThresholdBinarizationStrategy):
    nome_base: str = "LimiarFixoAlta"
    threshold: float = 176.0
