from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening
from skimage.filters import threshold_otsu

from src.binarizacao.binarizacao_base import gerar_nome_pasta_binarizacao


def _carregar_matriz_cinza_uint8(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("L"), dtype=np.uint8)


def _estrutura(kernel_size: int) -> np.ndarray:
    return np.ones((kernel_size, kernel_size), dtype=bool)


@dataclass(frozen=True)
class OtsuOpeningBinarizationStrategy:
    nome_base: str
    threshold_offset: float
    kernel_size: int

    @property
    def nome(self) -> str:
        return self.nome_base

    @property
    def nome_pasta(self) -> str:
        return gerar_nome_pasta_binarizacao(self.nome)

    def binarizar(self, image: Image.Image) -> Image.Image:
        matriz = _carregar_matriz_cinza_uint8(image)
        otsu_threshold = threshold_otsu(matriz)
        limiar = float(np.clip(otsu_threshold + self.threshold_offset, 0, 255))
        matriz_binaria = matriz > limiar
        matriz_opening = binary_opening(
            matriz_binaria,
            structure=_estrutura(self.kernel_size),
        )
        matriz_final = (matriz_opening * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")


@dataclass(frozen=True)
class OtsuOpeningLowBinarizationStrategy(OtsuOpeningBinarizationStrategy):
    nome_base: str = "OtsuOpeningBaixa"
    threshold_offset: float = -12.0
    kernel_size: int = 2


@dataclass(frozen=True)
class OtsuOpeningHighBinarizationStrategy(OtsuOpeningBinarizationStrategy):
    nome_base: str = "OtsuOpeningAlta"
    threshold_offset: float = 12.0
    kernel_size: int = 4
