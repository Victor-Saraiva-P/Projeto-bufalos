import numpy as np
from PIL import Image

from src.io.path_resolver import PathResolver


def carregar_mascara_cinza(image_path: str) -> np.ndarray:
    with Image.open(image_path) as img:
        return np.array(img.convert("L"), dtype=np.float64)


def carregar_mascara_binaria(image_path: str) -> np.ndarray:
    with Image.open(image_path) as img:
        arr = np.array(img.convert("L"))
    return (arr > 0).astype(np.uint8)


def carregar_mask_array_avaliacao(
    nome_arquivo: str,
    modelo: str,
    path_resolver: PathResolver | None = None,
    nome_binarizacao: str | None = None,
) -> np.ndarray:
    resolver = path_resolver or PathResolver.from_config()
    image_path = resolver.caminho_segmentacao_avaliacao(
        modelo,
        nome_arquivo,
        nome_binarizacao=nome_binarizacao,
    )
    return carregar_mascara_binaria(image_path)


def carregar_score_mask_predita(
    nome_arquivo: str,
    modelo: str,
    path_resolver: PathResolver | None = None,
) -> np.ndarray:
    resolver = path_resolver or PathResolver.from_config()
    image_path = resolver.caminho_segmentacao_bruta(modelo, nome_arquivo)
    return carregar_mascara_cinza(image_path)
