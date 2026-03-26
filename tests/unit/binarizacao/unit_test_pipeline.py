from decimal import Decimal
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from src.binarizacao import (
    binarizar_ground_truth,
    processar_arquivo_binarizacao,
)
from src.models.indice_linha import IndiceLinha


class FakeBinarizationStrategy:
    def __init__(self) -> None:
        self.calls = 0

    def binarizar(self, image: Image.Image) -> Image.Image:
        self.calls += 1
        return Image.new("L", image.size, color=255)


def test_processar_arquivo_binarizacao_usa_strategy_injetada(tmp_path: Path) -> None:
    entrada = tmp_path / "entrada.png"
    saida = tmp_path / "saida.png"
    strategy = FakeBinarizationStrategy()
    Image.new("L", (4, 4), color=0).save(entrada)

    resultado = processar_arquivo_binarizacao(str(entrada), str(saida), strategy)

    assert resultado == "ok"
    assert strategy.calls == 1
    assert saida.exists()
    assert np.all(np.array(Image.open(saida)) == 255)


def test_processar_arquivo_binarizacao_faz_skip_quando_saida_existe(
    tmp_path: Path,
) -> None:
    entrada = tmp_path / "entrada.png"
    saida = tmp_path / "saida.png"
    strategy = FakeBinarizationStrategy()
    Image.new("L", (4, 4), color=0).save(entrada)
    Image.new("L", (4, 4), color=0).save(saida)

    resultado = processar_arquivo_binarizacao(str(entrada), str(saida), strategy)

    assert resultado == "skip"
    assert strategy.calls == 0


def test_processar_arquivo_binarizacao_retorna_erro_quando_entrada_nao_existe(
    tmp_path: Path,
) -> None:
    strategy = FakeBinarizationStrategy()

    resultado = processar_arquivo_binarizacao(
        str(tmp_path / "faltante.png"),
        str(tmp_path / "saida.png"),
        strategy,
    )

    assert resultado == "erro"
    assert strategy.calls == 0


def test_binarizar_ground_truth_aceita_strategy_fake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada_dir = tmp_path / "ground_truth_raw"
    saida_dir = tmp_path / "ground_truth_binary"
    entrada_dir.mkdir()
    strategy = FakeBinarizationStrategy()
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=Decimal("1"))
    Image.new("L", (2, 2), color=0).save(entrada_dir / "bufalo_001.jpg")

    monkeypatch.setattr("src.io.path_utils.GROUND_TRUTH_RAW_DIR", str(entrada_dir))
    monkeypatch.setattr("src.io.path_utils.GROUND_TRUTH_BINARY", str(saida_dir))

    stats = binarizar_ground_truth([linha], strategy)

    assert stats.total == 1
    assert stats.processadas == 1
    assert stats.ok == 1
    assert stats.skip == 0
    assert stats.erro == 0
    assert strategy.calls == 1
    assert (saida_dir / "bufalo_001.png").exists()
