import numpy as np
from PIL import Image

from src.binarizacao.estrategias import (
    FixedThresholdLowBinarizationStrategy,
    GaussianOpeningBinarizationStrategy,
    GaussianOpeningHighBinarizationStrategy,
    GaussianOpeningLowBinarizationStrategy,
    HysteresisClosingLowBinarizationStrategy,
    OtsuOpeningLowBinarizationStrategy,
)


def test_gaussian_opening_strategy_retorna_apenas_valores_binarios() -> None:
    strategy = GaussianOpeningBinarizationStrategy(
        nome_base="TesteGaussiana",
        sigma=0.0,
        threshold=127,
        kernel_size=1,
    )
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
    strategy = GaussianOpeningBinarizationStrategy(
        nome_base="TesteGaussiana",
        sigma=0.0,
        threshold=127,
        kernel_size=1,
    )
    image = Image.new("RGB", (3, 3), color=(255, 0, 0))

    result = strategy.binarizar(image)

    assert result.mode == "L"
    assert np.array(result).shape == (3, 3)
    assert np.all(np.array(result) == 0)


def test_gaussian_opening_strategy_remove_ruido_com_opening() -> None:
    strategy = GaussianOpeningBinarizationStrategy(
        nome_base="TesteGaussiana",
        sigma=0.0,
        threshold=127,
        kernel_size=3,
    )
    matriz = np.zeros((5, 5), dtype=np.uint8)
    matriz[2, 2] = 255
    image = Image.fromarray(matriz, mode="L")

    result = strategy.binarizar(image)

    assert np.count_nonzero(np.array(result)) == 0


def test_variantes_gaussianas_expoem_nome_e_nome_pasta() -> None:
    strategy_baixa = GaussianOpeningLowBinarizationStrategy()
    strategy_alta = GaussianOpeningHighBinarizationStrategy()

    assert strategy_baixa.nome == "GaussianaOpeningBaixa"
    assert strategy_baixa.nome_pasta == "GaussianaOpeningBaixa"
    assert strategy_alta.nome == "GaussianaOpeningAlta"
    assert strategy_alta.nome_pasta == "GaussianaOpeningAlta"


def test_limiar_fixo_baixa_retorna_apenas_valores_binarios() -> None:
    strategy = FixedThresholdLowBinarizationStrategy()
    image = Image.fromarray(
        np.array([[0, 95, 97], [255, 120, 10]], dtype=np.uint8),
        mode="L",
    )

    result = strategy.binarizar(image)

    assert set(np.unique(np.array(result))) == {0, 255}


def test_otsu_opening_baixa_remove_ruido_isolado() -> None:
    strategy = OtsuOpeningLowBinarizationStrategy()
    matriz = np.zeros((5, 5), dtype=np.uint8)
    matriz[2, 2] = 255
    image = Image.fromarray(matriz, mode="L")

    result = strategy.binarizar(image)

    assert np.count_nonzero(np.array(result)) == 0


def test_histerese_closing_baixa_retorna_imagem_binaria() -> None:
    strategy = HysteresisClosingLowBinarizationStrategy()
    image = Image.fromarray(
        np.array(
            [
                [0, 0, 0, 0],
                [0, 130, 170, 0],
                [0, 100, 150, 0],
                [0, 0, 0, 0],
            ],
            dtype=np.uint8,
        ),
        mode="L",
    )

    result = strategy.binarizar(image)

    assert result.mode == "L"
    assert set(np.unique(np.array(result))) <= {0, 255}
