from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening, gaussian_filter

from src.config import (
    BINARIZATION_KERNEL_SIZE,
    BINARIZATION_SIGMA,
    BINARIZATION_THRESHOLD,
)


@dataclass(frozen=True)
class GaussianOpeningBinarizationStrategy:
    sigma: float = BINARIZATION_SIGMA
    threshold: float = BINARIZATION_THRESHOLD
    kernel_size: int = BINARIZATION_KERNEL_SIZE

    def binarizar(self, image: Image.Image) -> Image.Image:
        image_gray = image.convert("L")
        matriz = np.array(image_gray, dtype=np.float32)
        matriz_blur = gaussian_filter(matriz, sigma=self.sigma)
        matriz_binaria = matriz_blur > self.threshold
        estrutura = np.ones((self.kernel_size, self.kernel_size), dtype=bool)
        matriz_opening = binary_opening(matriz_binaria, structure=estrutura)
        matriz_final = (matriz_opening * 255).astype(np.uint8)
        return Image.fromarray(matriz_final, mode="L")
