import numpy as np
from PIL import Image

from src.io.path_utils import caminho_mascara_avaliacao


def carregar_mascara_binaria(image_path: str) -> np.ndarray:
    with Image.open(image_path) as img:
        arr = np.array(img.convert("L"))
    return (arr > 0).astype(np.uint8)


def carregar_mask_array_avaliacao(nome_arquivo: str, modelo: str) -> np.ndarray:
    image_path = caminho_mascara_avaliacao(modelo, nome_arquivo)
    return carregar_mascara_binaria(image_path)
