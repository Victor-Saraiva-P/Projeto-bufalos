from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening, gaussian_filter

from src.binarizacao.binarizacao_base import gerar_nome_pasta_binarizacao


def _carregar_matriz_cinza(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("L"), dtype=np.float32)


def _estrutura(kernel_size: int) -> np.ndarray:
    return np.ones((kernel_size, kernel_size), dtype=bool)


@dataclass(frozen=True)
class GaussianOpeningBinarizationStrategy:
    nome_base: str
    sigma: float
    threshold: float
    kernel_size: int

    @property
    def nome(self) -> str:
        return self.nome_base

    @property
    def nome_pasta(self) -> str:
        return gerar_nome_pasta_binarizacao(self.nome)

    def binarizar(self, image: Image.Image) -> Image.Image:
        matriz = _carregar_matriz_cinza(image)
        matriz_blur = gaussian_filter(matriz, sigma=self.sigma)
        matriz_binaria = matriz_blur > self.threshold
        matriz_opening = binary_opening(
            matriz_binaria,
            structure=_estrutura(self.kernel_size),
        )
        matriz_final = (matriz_opening * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")


@dataclass(frozen=True)
class GaussianOpeningLowBinarizationStrategy(GaussianOpeningBinarizationStrategy):
    nome_base: str = "GaussianaOpeningBaixa"
    sigma: float = 0.4
    threshold: float = 104.0
    kernel_size: int = 2


@dataclass(frozen=True)
class GaussianOpeningHighBinarizationStrategy(GaussianOpeningBinarizationStrategy):
    nome_base: str = "GaussianaOpeningAlta"
    sigma: float = 1.6
    threshold: float = 152.0
    kernel_size: int = 4
