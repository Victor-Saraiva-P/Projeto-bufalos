from typing import Protocol

from PIL import Image


def gerar_nome_pasta_binarizacao(nome_binarizacao: str) -> str:
    return nome_binarizacao.strip()


class BinarizationStrategy(Protocol):
    @property
    def nome(self) -> str:
        """Nome da estratégia de binarização."""

    @property
    def nome_pasta(self) -> str:
        """Nome da pasta usada para persistir os artefatos desta binarização."""

    def binarizar(self, image: Image.Image) -> Image.Image:
        """Retorna a imagem binarizada em escala de cinza."""
