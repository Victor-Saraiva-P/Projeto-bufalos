import os

from src.config import (
    GROUND_TRUTH_DIR,
    GROUND_TRUTH_BINARY,
    IMAGES_TYPE,
    IMAGES_DIR,
    REMBG_IMAGE_TYPE,
    PREDICTED_MASKS_DIR,
    PREDICTED_MASKS_BINARY,
)


def caminho_foto_original(nome_arquivo: str) -> str:
    return os.path.join(IMAGES_DIR, f"{nome_arquivo}{IMAGES_TYPE}")


def caminho_ground_truth(nome_arquivo: str) -> str:
    return os.path.join(GROUND_TRUTH_DIR, f"{nome_arquivo}{IMAGES_TYPE}")


def caminho_ground_truth_binaria(nome_arquivo: str) -> str:
    return os.path.join(GROUND_TRUTH_BINARY, f"{nome_arquivo}{REMBG_IMAGE_TYPE}")


def caminho_mascara_predita(nome_modelo: str, nome_arquivo: str) -> str:
    """Retorna caminho para máscara raw do modelo (gerada pelo notebook 01)."""
    return os.path.join(
        PREDICTED_MASKS_DIR,
        nome_modelo,
        f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
    )


def caminho_mascara_predita_binaria(nome_modelo: str, nome_arquivo: str) -> str:
    """Retorna caminho para máscara binarizada do modelo (gerada pelo notebook 02)."""
    return os.path.join(
        PREDICTED_MASKS_BINARY,
        nome_modelo,
        f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
    )
