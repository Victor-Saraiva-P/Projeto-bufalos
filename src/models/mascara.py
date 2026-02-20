import numpy as np
from PIL import Image

from src.io.path_utils import (
    caminho_ground_truth_binaria,
    caminho_mascara_predita,
)
from src.metrics.area import Area
from src.metrics.perimetro import Perimetro


class Mascara:
    modelo: str
    nome_arquivo: str
    mask_array: np.ndarray
    area: int | None
    perimetro: float | None

    def __init__(self, modelo: str, nome_arquivo: str):
        self.modelo = modelo
        self.nome_arquivo = nome_arquivo

        # Inicializar métricas como None
        self.area = None
        self.perimetro = None

        # APENAS carregar máscara (SEM calcular métricas)
        image_path = self.obter_caminho_mascara(modelo, nome_arquivo)
        self.mask_array = self._carregar_mascara_binaria(image_path)

    def calcular_metricas(self) -> None:
        self.area = Area.calcular(self.mask_array)
        self.perimetro = Perimetro.calcular(self.mask_array)

    @staticmethod
    def obter_caminho_mascara(modelo: str, nome_arquivo: str) -> str:
        if modelo == "ground_truth":
            return caminho_ground_truth_binaria(nome_arquivo)

        return caminho_mascara_predita(modelo, nome_arquivo)

    @staticmethod
    def _carregar_mascara_binaria(image_path: str) -> np.ndarray:
        with Image.open(image_path) as img:
            arr = np.array(img.convert("L"))
        return (arr > 0).astype(np.uint8)
