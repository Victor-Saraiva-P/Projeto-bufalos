import numpy as np
import cv2
from PIL import Image

from src.io.path_utils import caminho_ground_truth_output, caminho_segmentada_modelo


class Mascara:
    modelo: str
    area: int
    perimetro: float

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
    def calcular_area(image_path: str) -> int:
        """
        Calcula área da máscara (número de pixels brancos).

        Args:
            image_path: Caminho para imagem PNG binária

        Returns:
            Área em pixels
        """
        with Image.open(image_path) as img:
            img_gray = img.convert("L")
            arr = np.array(img_gray)

        area = int((arr == 255).sum())
        return area

    @staticmethod
    def calcular_perimetro(image_path: str) -> float:
        """
        Calcula perímetro usando distância Euclidiana (método CORRETO).

        Usa cv2.findContours + cv2.arcLength para calcular o perímetro real.
        Diagonais contam como √2 ≈ 1.414 (matematicamente correto).

        JUSTIFICATIVA (Notebook 03 - análise em 387 imagens, 4 métodos):
          • Método Manhattan superestima perímetro em ~20%
          • Erro amplifica para ~44% na estimativa de peso (Fórmula de Schaeffer)
          • Euclidiano simula corretamente medição com fita métrica
          • Erro é INVARIANTE ao método de binarização

        Análise completa em:
          notebooks/03_analise_perimetro_manhattan_vs_euclidiano.ipynb

        Args:
            image_path: Caminho para imagem PNG binária

        Returns:
            Perímetro em pixels (distância Euclidiana)
        """
        with Image.open(image_path) as img:
            arr = np.array(img.convert("L"))

        binary_mask = (arr > 0).astype(np.uint8)

        # Encontra contornos externos
        contours, _ = cv2.findContours(
            binary_mask,
            cv2.RETR_EXTERNAL,  # Apenas contorno externo
            cv2.CHAIN_APPROX_NONE,  # Todos os pontos (sem aproximação)
        )

        if len(contours) == 0:
            return 0.0

        # Pega o maior contorno (se houver múltiplos, soma todos)
        perimetro_total = sum(cv2.arcLength(cnt, closed=True) for cnt in contours)

        return float(perimetro_total)
