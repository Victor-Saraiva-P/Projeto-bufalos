from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.controllers.segmentacao_controller import SegmentacaoController
from src.io.path_resolver import PathResolver
from src.logs import EstatisticasProcessamentoComEta
from src.models import Imagem
from src.services.segmentacao_service import ResultadoSegmentacaoArquivo


class FakeImagemRepository:
    def __init__(self, imagens: list[Imagem]):
        self._imagens = imagens

    def list(self) -> list[Imagem]:
        return self._imagens


class FakePathResolver(PathResolver):
    pass


@dataclass
class FakeSegmentacaoService:
    resultados: dict[str, ResultadoSegmentacaoArquivo]

    def __post_init__(self) -> None:
        self.sessoes: list[tuple[str, list[str]]] = []
        self.chamadas: list[tuple[str, str]] = []

    def criar_sessao_segmentacao(self, nome_modelo: str, providers: list[str]):
        self.sessoes.append((nome_modelo, providers))
        return {"modelo": nome_modelo}

    def segmentar_arquivo(
        self,
        *,
        nome_arquivo: str,
        nome_modelo: str,
        original_path: str,
        mascara_path: str,
        output_path: str,
        rembg_session,
    ) -> ResultadoSegmentacaoArquivo:
        self.chamadas.append((nome_arquivo, nome_modelo))
        return self.resultados[nome_arquivo]

def test_processar_imagens_nao_persiste_segmentacoes_parciais(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [
        Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0),
        Imagem(nome_arquivo="bufalo_002", fazenda="A", peso=2.0),
        Imagem(nome_arquivo="bufalo_003", fazenda="A", peso=3.0),
    ]
    repository = FakeImagemRepository(imagens)
    service = FakeSegmentacaoService(
        resultados={
            "bufalo_001": ResultadoSegmentacaoArquivo(status="ok", duracao_inferencia=0.3),
            "bufalo_002": ResultadoSegmentacaoArquivo(status="skip"),
            "bufalo_003": ResultadoSegmentacaoArquivo(status="erro"),
        }
    )
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_raw_dir="/gt",
        predicted_masks_raw_dir="/pred",
        predicted_masks_binary_dir="/pred_bin",
        ground_truth_binary_dir="/gt_bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.obter_resolvedor_providers",
        lambda: (lambda *_args: ["CPUExecutionProvider"]),
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2net": "cpu"},
    )
    controller = SegmentacaoController(
        imagem_repository=repository,
        segmentacao_service=service,
    )

    resumos = controller.processar_imagens(imagens=imagens)

    assert isinstance(resumos["u2net"], EstatisticasProcessamentoComEta)
    assert resumos["u2net"].ok == 1
    assert resumos["u2net"].skip == 1
    assert resumos["u2net"].erro == 1
    assert service.sessoes == [("u2net", ["CPUExecutionProvider"])]
    assert imagens[0].segmentacoes == []
    assert imagens[1].segmentacoes == []
    assert imagens[2].segmentacoes == []


def test_processar_imagens_busca_imagens_no_repositorio_quando_nao_recebe_lista(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)]
    repository = FakeImagemRepository(imagens)
    service = FakeSegmentacaoService(
        resultados={"bufalo_001": ResultadoSegmentacaoArquivo(status="erro")}
    )
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_raw_dir="/gt",
        predicted_masks_raw_dir="/pred",
        predicted_masks_binary_dir="/pred_bin",
        ground_truth_binary_dir="/gt_bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.obter_resolvedor_providers",
        lambda: (lambda *_args: ["CPUExecutionProvider"]),
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2net": "cpu"},
    )
    controller = SegmentacaoController(
        imagem_repository=repository,
        segmentacao_service=service,
    )

    resumos = controller.processar_imagens()

    assert resumos["u2net"].erro == 1
