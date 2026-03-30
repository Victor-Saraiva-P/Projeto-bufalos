from pathlib import Path

import numpy as np
from PIL import Image

from src.services.binarizacao_service import BinarizacaoService


class FakeBinarizationStrategy:
    def __init__(self) -> None:
        self.calls = 0

    def binarizar(self, image: Image.Image) -> Image.Image:
        self.calls += 1
        return Image.new("L", image.size, color=255)


def test_processar_arquivo_usa_strategy_injetada(tmp_path: Path) -> None:
    entrada = tmp_path / "entrada.png"
    saida = tmp_path / "saida.png"
    strategy = FakeBinarizationStrategy()
    Image.new("L", (4, 4), color=0).save(entrada)

    resultado = BinarizacaoService().processar_arquivo(
        str(entrada),
        str(saida),
        strategy,
    )

    assert resultado == "ok"
    assert strategy.calls == 1
    assert saida.exists()
    assert np.all(np.array(Image.open(saida)) == 255)


def test_processar_arquivo_faz_skip_quando_saida_existe(tmp_path: Path) -> None:
    entrada = tmp_path / "entrada.png"
    saida = tmp_path / "saida.png"
    strategy = FakeBinarizationStrategy()
    Image.new("L", (4, 4), color=0).save(entrada)
    Image.new("L", (4, 4), color=0).save(saida)

    resultado = BinarizacaoService().processar_arquivo(
        str(entrada),
        str(saida),
        strategy,
    )

    assert resultado == "skip"
    assert strategy.calls == 0


def test_processar_arquivo_retorna_erro_quando_entrada_nao_existe(tmp_path: Path) -> None:
    strategy = FakeBinarizationStrategy()

    resultado = BinarizacaoService().processar_arquivo(
        str(tmp_path / "faltante.png"),
        str(tmp_path / "saida.png"),
        strategy,
    )

    assert resultado == "erro"
    assert strategy.calls == 0
