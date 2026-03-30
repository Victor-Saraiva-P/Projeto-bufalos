from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.controllers.binarizacao_controller import BinarizacaoController
from src.io.path_resolver import PathResolver
from src.models import Binarizacao, GroundTruthBinarizada, Imagem, Segmentacao


class FakeImagemRepository:
    def __init__(self, imagens: list[Imagem]):
        self._imagens = imagens
        self.salvos: list[str] = []

    def list(self) -> list[Imagem]:
        return self._imagens

    def save(self, imagem: Imagem) -> Imagem:
        self.salvos.append(imagem.nome_arquivo)
        return imagem


class FakePathResolver(PathResolver):
    pass


@dataclass
class FakeBinarizacaoService:
    resultados: dict[str, str]

    def __post_init__(self) -> None:
        self.processados: list[str] = []

    def processar_arquivo(self, caminho_entrada: str, caminho_saida: str, strategy) -> str:
        self.processados.append(caminho_saida)
        return self.resultados[caminho_saida]

    @staticmethod
    def garantir_ground_truth_binarizada(imagem: Imagem) -> GroundTruthBinarizada:
        gt = GroundTruthBinarizada(
            nome_arquivo=imagem.nome_arquivo,
            area=None,
            perimetro=None,
        )
        imagem.ground_truth_binarizada = gt
        return gt

    @staticmethod
    def garantir_binarizacao(
        imagem: Imagem,
        nome_modelo: str,
        strategy,
    ) -> Binarizacao:
        segmentacao = Segmentacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo=nome_modelo,
        )
        imagem.segmentacoes.append(segmentacao)
        binarizacao = Binarizacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo=nome_modelo,
            estrategia_binarizacao=type(strategy).__name__,
            metrica_x=None,
            metrica_y=None,
        )
        segmentacao.binarizacoes.append(binarizacao)
        return binarizacao


def test_processar_ground_truth_persiste_quando_status_e_ok_ou_skip(
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
        ground_truth_raw_dir="/gt/raw",
        predicted_masks_dir="/pred/raw",
        predicted_masks_binary_dir="/pred/bin",
        ground_truth_binary_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    controller = BinarizacaoController(
        path_resolver=resolver,
        imagem_repository=repository,
        binarizacao_service=service,
    )

    stats = controller.processar_ground_truth(
        GaussianOpeningBinarizationStrategy(),
        imagens=imagens,
    )

    assert stats.ok == 1
    assert stats.skip == 1
    assert stats.erro == 0
    assert repository.salvos == ["bufalo_001", "bufalo_002"]
    assert imagens[0].ground_truth_binarizada is not None
    assert imagens[1].ground_truth_binarizada is not None


def test_processar_segmentacoes_persiste_binarizacoes_do_modelo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)]
    repository = FakeImagemRepository(imagens)
    service = FakeBinarizacaoService(resultados={"/pred/bin/u2netp/bufalo_001.png": "ok"})
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_raw_dir="/gt/raw",
        predicted_masks_dir="/pred/raw",
        predicted_masks_binary_dir="/pred/bin",
        ground_truth_binary_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/data/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    controller = BinarizacaoController(
        path_resolver=resolver,
        imagem_repository=repository,
        binarizacao_service=service,
    )

    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.os.path.isdir",
        lambda _path: True,
    )

    resumos = controller.processar_segmentacoes(
        GaussianOpeningBinarizationStrategy(),
        imagens=imagens,
        modelos_para_avaliacao={"u2netp": "cpu"},
    )

    stats = resumos["u2netp"]
    assert stats.ok == 1
    assert stats.skip == 0
    assert stats.erro == 0
    assert repository.salvos == ["bufalo_001"]
    assert imagens[0].segmentacoes[0].nome_modelo == "u2netp"
    assert imagens[0].segmentacoes[0].binarizacoes[0].estrategia_binarizacao == (
        "GaussianOpeningBinarizationStrategy"
    )
