import numpy as np
from PIL import Image


class Mascara:
    modelo: str
    area: int

    def __init__(self, modelo: str, image_path: str):
        self.modelo = modelo
        self.area = self.calcular_area(image_path)

        # self._perimetro = self.calcular_perimetro()

    @staticmethod
    def calcular_area(image_path: str):
        with Image.open(image_path) as img:
            img_gray = img.convert("L")
            arr = np.array(img_gray)

        area = int((arr == 255).sum())

        return area

    # def calcular_perimetro(self, image_path: str):
    #     return 0
