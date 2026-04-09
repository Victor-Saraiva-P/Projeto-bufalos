from dataclasses import dataclass

import numpy as np
from PIL import Image

from src.binarizacao.binarizacao_base import gerar_nome_pasta_binarizacao
from src.config import BINARIZATION_THRESHOLD


@dataclass(frozen=True)
class GroundTruthGlobalThresholdBinarizationStrategy:
    threshold: float = BINARIZATION_THRESHOLD

    @property
    def nome(self) -> str:
        return "GroundTruthLimiarGlobal"

    @property
    def nome_pasta(self) -> str:
        return gerar_nome_pasta_binarizacao(self.nome)

    def binarizar(self, image: Image.Image) -> Image.Image:
        image_gray = image.convert("L")
        matriz = np.array(image_gray, dtype=np.float32)
        matriz_binaria = matriz > self.threshold
        matriz_final = (matriz_binaria * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")
