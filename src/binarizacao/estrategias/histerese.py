from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing
from skimage.filters import apply_hysteresis_threshold

from src.binarizacao.binarizacao_base import gerar_nome_pasta_binarizacao


def _carregar_matriz_cinza(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("L"), dtype=np.float32)


def _estrutura(kernel_size: int) -> np.ndarray:
    return np.ones((kernel_size, kernel_size), dtype=bool)


@dataclass(frozen=True)
class HysteresisClosingBinarizationStrategy:
    nome_base: str
    low_threshold: float
    high_threshold: float
    kernel_size: int

    @property
    def nome(self) -> str:
        return self.nome_base

    @property
    def nome_pasta(self) -> str:
        return gerar_nome_pasta_binarizacao(self.nome)

    def binarizar(self, image: Image.Image) -> Image.Image:
        matriz = _carregar_matriz_cinza(image)
        matriz_histerese = apply_hysteresis_threshold(
            matriz,
            low=self.low_threshold,
            high=self.high_threshold,
        )
        matriz_closing = binary_closing(
            matriz_histerese,
            structure=_estrutura(self.kernel_size),
        )
        matriz_final = (matriz_closing * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")


@dataclass(frozen=True)
class HysteresisClosingLowBinarizationStrategy(HysteresisClosingBinarizationStrategy):
    nome_base: str = "HistereseClosingBaixa"
    low_threshold: float = 64.0
    high_threshold: float = 144.0
    kernel_size: int = 2


@dataclass(frozen=True)
class HysteresisClosingHighBinarizationStrategy(HysteresisClosingBinarizationStrategy):
    nome_base: str = "HistereseClosingAlta"
    low_threshold: float = 112.0
    high_threshold: float = 192.0
    kernel_size: int = 4
