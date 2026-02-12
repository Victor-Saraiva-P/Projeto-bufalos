import os

from src.config import (
    GROUND_OF_TRUTH,
    GROUND_OF_TRUTH_OUTPUT,
    ORIGINAL_IMAGE_TYPE,
    ORIGINAL_PHOTOS_DIR,
    REMBG_IMAGE_TYPE,
    SEGMENTED_PHOTOS_DIR,
    SEGMENTED_RAW_DIR,
    SEGMENTED_BINARIZED_DIR,
)


def caminho_foto_original(nome_arquivo: str) -> str:
    return os.path.join(ORIGINAL_PHOTOS_DIR, f"{nome_arquivo}{ORIGINAL_IMAGE_TYPE}")


def caminho_ground_truth(nome_arquivo: str) -> str:
    return os.path.join(GROUND_OF_TRUTH, f"{nome_arquivo}{ORIGINAL_IMAGE_TYPE}")


def caminho_ground_truth_output(nome_arquivo: str) -> str:
    return os.path.join(GROUND_OF_TRUTH_OUTPUT, f"{nome_arquivo}{REMBG_IMAGE_TYPE}")


def caminho_segmentada_raw_modelo(nome_modelo: str, nome_arquivo: str) -> str:
    """Retorna caminho para máscara raw do modelo (gerada pelo notebook 01)."""
    return os.path.join(
        SEGMENTED_RAW_DIR,
        nome_modelo,
        f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
    )


def caminho_segmentada_binarizada_modelo(nome_modelo: str, nome_arquivo: str) -> str:
    """Retorna caminho para máscara binarizada do modelo (gerada pelo notebook 02)."""
    return os.path.join(
        SEGMENTED_BINARIZED_DIR,
        nome_modelo,
        f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
    )


def caminho_segmentada_modelo(nome_modelo: str, nome_arquivo: str) -> str:
    """Retorna caminho para máscara binarizada do modelo (usado para avaliação).

    NOTA: Esta função aponta para máscaras binarizadas, que são o produto final
    usado na avaliação (notebook 03). Para máscaras raw, use caminho_segmentada_raw_modelo().
    """
    return caminho_segmentada_binarizada_modelo(nome_modelo, nome_arquivo)
