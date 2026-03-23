import numpy as np
from PIL import Image

from src.segmentacao.binarizacoes import GaussianOpeningBinarizationStrategy


def test_gaussian_opening_strategy_retorna_apenas_valores_binarios() -> None:
    strategy = GaussianOpeningBinarizationStrategy(sigma=0.0, threshold=127, kernel_size=1)
    image = Image.fromarray(
        np.array(
            [
                [0, 120, 128],
                [255, 200, 10],
            ],
            dtype=np.uint8,
        ),
        mode="L",
    )

    result = strategy.binarizar(image)
    valores = set(np.unique(np.array(result)))

    assert result.mode == "L"
    assert valores <= {0, 255}
    assert valores == {0, 255}


def test_gaussian_opening_strategy_converte_rgb_para_grayscale() -> None:
    strategy = GaussianOpeningBinarizationStrategy(sigma=0.0, threshold=127, kernel_size=1)
    image = Image.new("RGB", (3, 3), color=(255, 0, 0))

    result = strategy.binarizar(image)

    assert result.mode == "L"
    assert np.array(result).shape == (3, 3)
    assert np.all(np.array(result) == 0)


def test_gaussian_opening_strategy_remove_ruido_com_opening() -> None:
    strategy = GaussianOpeningBinarizationStrategy(sigma=0.0, threshold=127, kernel_size=3)
    matriz = np.zeros((5, 5), dtype=np.uint8)
    matriz[2, 2] = 255
    image = Image.fromarray(matriz, mode="L")

    result = strategy.binarizar(image)

    assert np.count_nonzero(np.array(result)) == 0
