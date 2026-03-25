from typing import Protocol

from PIL import Image


class BinarizationStrategy(Protocol):
    def binarizar(self, image: Image.Image) -> Image.Image:
        """Retorna a imagem binarizada em escala de cinza."""
