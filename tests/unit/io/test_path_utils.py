from src.config import (
    GROUND_TRUTH_BINARY,
    GROUND_TRUTH_DIR,
    IMAGES_DIR,
    IMAGES_TYPE,
    PREDICTED_MASKS_BINARY,
    PREDICTED_MASKS_DIR,
    REMBG_IMAGE_TYPE,
)
from src.io.path_utils import (
    caminho_foto_original,
    caminho_ground_truth,
    caminho_ground_truth_binaria,
    caminho_mascara_predita,
    caminho_mascara_predita_binaria,
)


def test_caminho_foto_original_monta_path_esperado() -> None:
    nome_arquivo = "bufalo_001"

    assert caminho_foto_original(nome_arquivo) == (
        f"{IMAGES_DIR}/{nome_arquivo}{IMAGES_TYPE}"
    )


def test_caminho_ground_truth_monta_path_esperado() -> None:
    nome_arquivo = "bufalo_001"

    assert caminho_ground_truth(nome_arquivo) == (
        f"{GROUND_TRUTH_DIR}/{nome_arquivo}{IMAGES_TYPE}"
    )


def test_caminho_ground_truth_binaria_monta_path_esperado() -> None:
    nome_arquivo = "bufalo_001"

    assert caminho_ground_truth_binaria(nome_arquivo) == (
        f"{GROUND_TRUTH_BINARY}/{nome_arquivo}{REMBG_IMAGE_TYPE}"
    )


def test_caminho_mascara_predita_monta_path_esperado() -> None:
    nome_modelo = "u2net"
    nome_arquivo = "bufalo_001"

    assert caminho_mascara_predita(nome_modelo, nome_arquivo) == (
        f"{PREDICTED_MASKS_DIR}/{nome_modelo}/{nome_arquivo}{REMBG_IMAGE_TYPE}"
    )


def test_caminho_mascara_predita_binaria_monta_path_esperado() -> None:
    nome_modelo = "u2net"
    nome_arquivo = "bufalo_001"

    assert caminho_mascara_predita_binaria(nome_modelo, nome_arquivo) == (
        f"{PREDICTED_MASKS_BINARY}/{nome_modelo}/{nome_arquivo}{REMBG_IMAGE_TYPE}"
    )
