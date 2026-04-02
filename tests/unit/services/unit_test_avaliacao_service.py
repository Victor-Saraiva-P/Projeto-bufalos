import numpy as np
import pytest

from src.models import Imagem, SegmentacaoBinarizada, SegmentacaoBruta
from src.services.avaliacao_service import AvaliacaoService


class FakeArea:
    def __init__(self, *, modelo: str, **_kwargs):
        self.modelo = modelo

    def calcular(self) -> float:
        return 100.0 if self.modelo == "ground_truth" else 40.0


class FakePerimetro:
    def __init__(self, *, modelo: str, **_kwargs):
        self.modelo = modelo

    def calcular(self) -> float:
        return 20.0 if self.modelo == "ground_truth" else 8.0


class FakeIoU:
    def __init__(self, *, modelo: str, **_kwargs):
        self.modelo = modelo

    def calcular(self) -> float:
        return 0.75 if self.modelo == "u2netp" else 0.5


class FakeAUPRC:
    def __init__(self, *, modelo: str, **_kwargs):
        self.modelo = modelo

    def calcular(self) -> float:
        return 0.9 if self.modelo == "u2netp" else 0.6


class FakeSoftDice:
    def __init__(self, *, modelo: str, **_kwargs):
        self.modelo = modelo

    def calcular(self) -> float:
        return 0.85 if self.modelo == "u2netp" else 0.55


def test_avaliar_preenche_ground_truth_e_reaproveita_segmentacoes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.avaliacao_service.Area", FakeArea)
    monkeypatch.setattr("src.services.avaliacao_service.Perimetro", FakePerimetro)
    monkeypatch.setattr("src.services.avaliacao_service.IoU", FakeIoU)
    monkeypatch.setattr("src.services.avaliacao_service.AUPRC", FakeAUPRC)
    monkeypatch.setattr("src.services.avaliacao_service.SoftDice", FakeSoftDice)

    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    existente = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=SegmentacaoBruta.AUPRC_NAO_CALCULADA,
        soft_dice=-1.0,
    )
    imagem.segmentacoes_brutas.append(existente)

    imagem_avaliada = AvaliacaoService().avaliar(
        imagem=imagem,
        ground_truth_mask=np.zeros((2, 2), dtype=np.uint8),
        mascaras_modelo={
            "u2netp": np.ones((2, 2), dtype=np.uint8),
            "modnet": np.ones((2, 2), dtype=np.uint8),
        },
        score_masks_modelo={
            "u2netp": np.full((2, 2), 0.8, dtype=np.float64),
            "modnet": np.full((2, 2), 0.4, dtype=np.float64),
        },
        estrategia_binarizacao="GaussianaOpening",
        execucao=1,
    )

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert imagem_avaliada.ground_truth_binarizada.area == 100.0
    assert imagem_avaliada.ground_truth_binarizada.perimetro == 20.0
    assert [
        (segmentacao_bruta.nome_modelo, segmentacao_bruta.execucao)
        for segmentacao_bruta in imagem_avaliada.segmentacoes_brutas
    ] == [
        ("modnet", 1),
        ("u2netp", 1),
    ]
    assert imagem_avaliada.segmentacoes_brutas[1] is existente
    assert existente.auprc == 0.9
    assert existente.soft_dice == 0.85
    assert len(existente.segmentacoes_binarizadas) == 1
    binarizada = existente.segmentacoes_binarizadas[0]
    assert isinstance(binarizada, SegmentacaoBinarizada)
    assert binarizada.execucao == 1
    assert binarizada.estrategia_binarizacao == "GaussianaOpening"
    assert binarizada.area == 40.0
    assert binarizada.perimetro == 8.0
    assert binarizada.iou == 0.75


def test_avaliar_separa_segmentacoes_da_mesma_imagem_por_execucao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.avaliacao_service.Area", FakeArea)
    monkeypatch.setattr("src.services.avaliacao_service.Perimetro", FakePerimetro)
    monkeypatch.setattr("src.services.avaliacao_service.IoU", FakeIoU)
    monkeypatch.setattr("src.services.avaliacao_service.AUPRC", FakeAUPRC)
    monkeypatch.setattr("src.services.avaliacao_service.SoftDice", FakeSoftDice)

    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    service = AvaliacaoService()
    parametros = {
        "imagem": imagem,
        "ground_truth_mask": np.zeros((2, 2), dtype=np.uint8),
        "mascaras_modelo": {"u2netp": np.ones((2, 2), dtype=np.uint8)},
        "score_masks_modelo": {"u2netp": np.full((2, 2), 0.8, dtype=np.float64)},
        "estrategia_binarizacao": "GaussianaOpening",
    }

    service.avaliar(**parametros, execucao=1)
    imagem_avaliada = service.avaliar(**parametros, execucao=2)

    assert [
        (segmentacao.nome_modelo, segmentacao.execucao)
        for segmentacao in imagem_avaliada.segmentacoes_brutas
    ] == [("u2netp", 1), ("u2netp", 2)]
    assert all(
        segmentacao.segmentacoes_binarizadas[0].execucao == segmentacao.execucao
        for segmentacao in imagem_avaliada.segmentacoes_brutas
    )


def test_avaliar_acumula_metricas_de_multiplas_binarizacoes_na_mesma_segmentacao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.avaliacao_service.Area", FakeArea)
    monkeypatch.setattr("src.services.avaliacao_service.Perimetro", FakePerimetro)
    monkeypatch.setattr("src.services.avaliacao_service.IoU", FakeIoU)
    monkeypatch.setattr("src.services.avaliacao_service.AUPRC", FakeAUPRC)
    monkeypatch.setattr("src.services.avaliacao_service.SoftDice", FakeSoftDice)

    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    service = AvaliacaoService()
    parametros = {
        "imagem": imagem,
        "ground_truth_mask": np.zeros((2, 2), dtype=np.uint8),
        "mascaras_modelo": {"u2netp": np.ones((2, 2), dtype=np.uint8)},
        "score_masks_modelo": {"u2netp": np.full((2, 2), 0.8, dtype=np.float64)},
    }

    service.avaliar(
        **parametros,
        estrategia_binarizacao="GaussianaOpening",
        execucao=1,
    )
    imagem_avaliada = service.avaliar(
        **parametros,
        estrategia_binarizacao="LimiarFixo",
        execucao=1,
    )

    assert len(imagem_avaliada.segmentacoes_brutas) == 1
    assert imagem_avaliada.segmentacoes_brutas[0].auprc == 0.9
    assert imagem_avaliada.segmentacoes_brutas[0].soft_dice == 0.85
    assert {
        segmentacao_binarizada.estrategia_binarizacao
        for segmentacao_binarizada in imagem_avaliada.segmentacoes_brutas[0].segmentacoes_binarizadas
    } == {"GaussianaOpening", "LimiarFixo"}
