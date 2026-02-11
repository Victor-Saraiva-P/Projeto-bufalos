import numpy as np
from PIL import Image

from src.io.path_utils import caminho_ground_truth_output, caminho_segmentada_modelo


class Mascara:
    modelo: str
    area: int
    perimetro: int

    def __init__(self, modelo: str, nome_arquivo: str):
        self.modelo = modelo
        image_path = self.obter_caminho_mascara(modelo, nome_arquivo)

        self.area = self.calcular_area(image_path)
        self.perimetro = self.calcular_perimetro(image_path)

    @staticmethod
    def obter_caminho_mascara(modelo: str, nome_arquivo: str) -> str:
        if modelo == "ground-of-truth":
            return caminho_ground_truth_output(nome_arquivo)

        return caminho_segmentada_modelo(modelo, nome_arquivo)

    @staticmethod
    def calcular_area(image_path: str):
        with Image.open(image_path) as img:
            img_gray = img.convert("L")
            arr = np.array(img_gray)

        area = int((arr == 255).sum())

        return area

    @staticmethod
    def calcular_perimetro(image_path: str):
        with Image.open(image_path) as img:
            img_gray = img.convert("L")
            arr = np.array(img_gray)

        # Cria máscara binária (1 para pixels brancos, 0 para pretos)
        binary_mask = (arr > 0).astype(np.uint8)

        edges = 0
        h, w = binary_mask.shape

        # Para cada pixel branco, conta quantas arestas ele tem expostas
        for i in range(h):
            for j in range(w):
                if binary_mask[i, j] == 1:
                    # Borda esquerda
                    if j == 0 or binary_mask[i, j - 1] == 0:
                        edges += 1
                    # Borda direita
                    if j == w - 1 or binary_mask[i, j + 1] == 0:
                        edges += 1
                    # Borda superior
                    if i == 0 or binary_mask[i - 1, j] == 0:
                        edges += 1
                    # Borda inferior
                    if i == h - 1 or binary_mask[i + 1, j] == 0:
                        edges += 1

        return edges
