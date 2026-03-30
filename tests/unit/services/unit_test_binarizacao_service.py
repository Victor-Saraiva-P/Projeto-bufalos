from pathlib import Path

import numpy as np
from PIL import Image

from src.models import Imagem
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


def test_garantir_ground_truth_binarizada_reaproveita_registro_existente() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    service = BinarizacaoService()

    primeiro = service.garantir_ground_truth_binarizada(imagem)
    segundo = service.garantir_ground_truth_binarizada(imagem)

    assert primeiro is segundo
    assert imagem.ground_truth_binarizada is primeiro


def test_garantir_binarizacao_cria_segmentacao_e_reaproveita_estrategia() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    strategy = FakeBinarizationStrategy()
    service = BinarizacaoService()

    primeira = service.garantir_binarizacao(imagem, "u2netp", strategy)
    segunda = service.garantir_binarizacao(imagem, "u2netp", strategy)

    assert primeira is segunda
    assert len(imagem.segmentacoes) == 1
    assert imagem.segmentacoes[0].nome_modelo == "u2netp"
    assert len(imagem.segmentacoes[0].binarizacoes) == 1
