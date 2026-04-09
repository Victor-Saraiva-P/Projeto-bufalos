import numpy as np
from PIL import Image

from src.binarizacao.estrategias import GroundTruthGlobalThresholdBinarizationStrategy


def test_ground_truth_limiar_global_retorna_apenas_valores_binarios() -> None:
    strategy = GroundTruthGlobalThresholdBinarizationStrategy(threshold=127)
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


def test_ground_truth_limiar_global_converte_rgb_para_grayscale() -> None:
    strategy = GroundTruthGlobalThresholdBinarizationStrategy(threshold=127)
    image = Image.new("RGB", (3, 3), color=(255, 0, 0))

    result = strategy.binarizar(image)

    assert result.mode == "L"
    assert np.array(result).shape == (3, 3)
    assert np.all(np.array(result) == 0)


def test_ground_truth_limiar_global_preserva_pixel_isolado_sem_morfologia() -> None:
    strategy = GroundTruthGlobalThresholdBinarizationStrategy(threshold=127)
    matriz = np.zeros((5, 5), dtype=np.uint8)
    matriz[2, 2] = 255
    image = Image.fromarray(matriz, mode="L")

    result = strategy.binarizar(image)

    assert np.count_nonzero(np.array(result)) == 1


def test_ground_truth_limiar_global_expoe_nome_e_nome_pasta() -> None:
    strategy = GroundTruthGlobalThresholdBinarizationStrategy()

    assert strategy.nome == "GroundTruthLimiarGlobal"
    assert strategy.nome_pasta == "GroundTruthLimiarGlobal"
