import numpy as np
import pytest

from src.models import Imagem, Segmentacao
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


def test_avaliar_preenche_ground_truth_e_reaproveita_segmentacoes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.avaliacao_service.Area", FakeArea)
    monkeypatch.setattr("src.services.avaliacao_service.Perimetro", FakePerimetro)
    monkeypatch.setattr("src.services.avaliacao_service.IoU", FakeIoU)

    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    existente = Segmentacao(nome_arquivo="bufalo_001", nome_modelo="u2netp")
    imagem.segmentacoes.append(existente)

    imagem_avaliada = AvaliacaoService().avaliar(
        imagem=imagem,
        ground_truth_mask=np.zeros((2, 2), dtype=np.uint8),
        mascaras_modelo={
            "u2netp": np.ones((2, 2), dtype=np.uint8),
            "modnet": np.ones((2, 2), dtype=np.uint8),
        },
    )

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert imagem_avaliada.ground_truth_binarizada.area == 100.0
    assert imagem_avaliada.ground_truth_binarizada.perimetro == 20.0
    assert [segmentacao.nome_modelo for segmentacao in imagem_avaliada.segmentacoes] == [
        "modnet",
        "u2netp",
    ]
    assert imagem_avaliada.segmentacoes[1] is existente
    assert existente.area == 40.0
    assert existente.perimetro == 8.0
    assert existente.iou == 0.75
