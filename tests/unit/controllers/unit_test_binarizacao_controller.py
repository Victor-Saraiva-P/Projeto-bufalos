from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.binarizacao import GaussianOpeningLowBinarizationStrategy
from src.controllers.binarizacao_controller import BinarizacaoController
from src.io.path_resolver import PathResolver
from src.models import Imagem


class FakeImagemRepository:
    def __init__(self, imagens: list[Imagem]):
        self._imagens = imagens

    def list(self) -> list[Imagem]:
        return self._imagens


class FakePathResolver(PathResolver):
    pass


@dataclass(frozen=True)
class FakeNamedStrategy:
    nome: str

    @property
    def nome_pasta(self) -> str:
        return self.nome

    def binarizar(self, image):
        return image


@dataclass
class FakeBinarizacaoService:
    resultados: dict[str, str]

    def __post_init__(self) -> None:
        self.processados: list[str] = []

    def processar_arquivo(self, caminho_entrada: str, caminho_saida: str, strategy) -> str:
        self.processados.append(caminho_saida)
        return self.resultados[caminho_saida]

def test_processar_ground_truth_nao_persiste_registro_parcial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [
        Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0),
        Imagem(nome_arquivo="bufalo_002", fazenda="A", peso=2.0),
    ]
    repository = FakeImagemRepository(imagens)
    saidas = {
        "/gt/bin/bufalo_001.png": "ok",
        "/gt/bin/bufalo_002.png": "skip",
    }
    service = FakeBinarizacaoService(resultados=saidas)
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_brutos_dir="/gt/raw",
        segmentacoes_brutas_dir="/pred/raw",
        segmentacoes_binarizadas_dir="/pred/bin",
        ground_truth_binarizada_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    controller = BinarizacaoController(
        imagem_repository=repository,
        binarizacao_service=service,
    )

    stats = controller.processar_ground_truth(
        GaussianOpeningLowBinarizationStrategy(),
        imagens=imagens,
    )

    assert stats.ok == 1
    assert stats.skip == 1
    assert stats.erro == 0
    assert imagens[0].ground_truth_binarizada is None
    assert imagens[1].ground_truth_binarizada is None


def test_processar_segmentacoes_nao_persiste_binarizacoes_parciais(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)]
    repository = FakeImagemRepository(imagens)
    service = FakeBinarizacaoService(
        resultados={
            "/pred/bin/execucao_1/GaussianaOpeningBaixa/u2netp/bufalo_001.png": "ok",
            "/pred/bin/execucao_2/GaussianaOpeningBaixa/u2netp/bufalo_001.png": "ok",
        }
    )
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_brutos_dir="/gt/raw",
        segmentacoes_brutas_dir="/pred/raw",
        segmentacoes_binarizadas_dir="/pred/bin",
        ground_truth_binarizada_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.os.path.isdir",
        lambda _path: True,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr("src.controllers.binarizacao_controller.NUM_EXECUCOES", 2)
    controller = BinarizacaoController(
        imagem_repository=repository,
        binarizacao_service=service,
    )

    resumos = controller.processar_segmentacoes(
        GaussianOpeningLowBinarizationStrategy(),
        imagens=imagens,
    )

    stats = resumos["u2netp"]
    assert stats.total == 2
    assert stats.ok == 2
    assert stats.skip == 0
    assert stats.erro == 0
    assert service.processados == [
        "/pred/bin/execucao_1/GaussianaOpeningBaixa/u2netp/bufalo_001.png",
        "/pred/bin/execucao_2/GaussianaOpeningBaixa/u2netp/bufalo_001.png",
    ]
    assert imagens[0].segmentacoes_brutas == []


def test_processar_segmentacoes_configuradas_itera_todas_as_estrategias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)]
    repository = FakeImagemRepository(imagens)
    strategies = [
        FakeNamedStrategy("GaussianaOpeningBaixa"),
        FakeNamedStrategy("LimiarFixoAlta"),
    ]
    service = FakeBinarizacaoService(
        resultados={
            "/pred/bin/execucao_1/GaussianaOpeningBaixa/u2netp/bufalo_001.png": "ok",
            "/pred/bin/execucao_1/LimiarFixoAlta/u2netp/bufalo_001.png": "ok",
        }
    )
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_brutos_dir="/gt/raw",
        segmentacoes_brutas_dir="/pred/raw",
        segmentacoes_binarizadas_dir="/pred/bin",
        ground_truth_binarizada_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.os.path.isdir",
        lambda _path: True,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr("src.controllers.binarizacao_controller.NUM_EXECUCOES", 1)
    controller = BinarizacaoController(
        imagem_repository=repository,
        binarizacao_service=service,
        segmentacao_strategies=strategies,
    )

    resumos = controller.processar_segmentacoes_configuradas(imagens=imagens)

    assert set(resumos) == {"GaussianaOpeningBaixa", "LimiarFixoAlta"}
    assert all(
        resumos[nome]["u2netp"].ok == 1
        for nome in {"GaussianaOpeningBaixa", "LimiarFixoAlta"}
    )
    assert service.processados == [
        "/pred/bin/execucao_1/GaussianaOpeningBaixa/u2netp/bufalo_001.png",
        "/pred/bin/execucao_1/LimiarFixoAlta/u2netp/bufalo_001.png",
    ]
