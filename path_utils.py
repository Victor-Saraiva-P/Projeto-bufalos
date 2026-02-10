import os

from config import (
    GROUND_OF_TRUTH,
    GROUND_OF_TRUTH_OUTPUT,
    ORIGINAL_IMAGE_TYPE,
    ORIGINAL_PHOTOS_DIR,
    REMBG_IMAGE_TYPE,
    SEGMENTED_PHOTOS_DIR,
)


def caminho_foto_original(nome_arquivo: str) -> str:
    return os.path.join(ORIGINAL_PHOTOS_DIR, f"{nome_arquivo}{ORIGINAL_IMAGE_TYPE}")


def caminho_ground_truth(nome_arquivo: str) -> str:
    return os.path.join(GROUND_OF_TRUTH, f"{nome_arquivo}{ORIGINAL_IMAGE_TYPE}")


def caminho_ground_truth_output(nome_arquivo: str) -> str:
    return os.path.join(GROUND_OF_TRUTH_OUTPUT, f"{nome_arquivo}{REMBG_IMAGE_TYPE}")


def caminho_segmentada_modelo(nome_modelo: str, nome_arquivo: str) -> str:
    return os.path.join(
        SEGMENTED_PHOTOS_DIR,
        nome_modelo,
        f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
    )
