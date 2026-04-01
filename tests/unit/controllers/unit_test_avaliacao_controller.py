import numpy as np

from src.controllers.avaliacao_controller import AvaliacaoController
from src.io.path_resolver import PathResolver
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)


class FakeImagemRepository:
    def __init__(self) -> None:
        self.imagens: list[Imagem] = []

    def list(self) -> list[Imagem]:
        return list(self.imagens)


class FakeGroundTruthBinarizadaRepository:
    def __init__(self) -> None:
        self.salvos: list[GroundTruthBinarizada] = []

    def save(self, ground_truth_binarizada: GroundTruthBinarizada) -> GroundTruthBinarizada:
        self.salvos.append(ground_truth_binarizada)
        return ground_truth_binarizada


class FakeSegmentacaoRepository:
    def __init__(self) -> None:
        self.salvos: list[SegmentacaoBruta] = []

    def save(self, segmentacao: SegmentacaoBruta) -> SegmentacaoBruta:
        self.salvos.append(segmentacao)
        return segmentacao


class FakeBinarizacaoRepository:
    def __init__(self) -> None:
        self.salvos: list[SegmentacaoBinarizada] = []

    def save(
        self,
        binarizacao: SegmentacaoBinarizada,
    ) -> SegmentacaoBinarizada:
        self.salvos.append(binarizacao)
        return binarizacao


class FakeAvaliacaoService:
    def __init__(self) -> None:
        self.chamadas: list[
            tuple[
                Imagem,
                np.ndarray,
                dict[str, np.ndarray],
                dict[str, np.ndarray],
                str,
            ]
        ] = []

    def avaliar(
        self,
        imagem: Imagem,
        ground_truth_mask: np.ndarray,
        mascaras_modelo: dict[str, np.ndarray],
        score_masks_modelo: dict[str, np.ndarray],
        estrategia_binarizacao: str,
    ) -> Imagem:
        self.chamadas.append(
            (
                imagem,
                ground_truth_mask,
                mascaras_modelo,
                score_masks_modelo,
                estrategia_binarizacao,
            )
        )
        imagem.ground_truth_binarizada = GroundTruthBinarizada(
            nome_arquivo=imagem.nome_arquivo,
            area=10.0,
            perimetro=20.0,
        )
        segmentacao = SegmentacaoBruta(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo="u2netp",
            auprc=0.9,
        )
        segmentacao.segmentacoes_binarizadas.append(
            SegmentacaoBinarizada(
                nome_arquivo=imagem.nome_arquivo,
                nome_modelo="u2netp",
                estrategia_binarizacao=estrategia_binarizacao,
                area=5.0,
                perimetro=7.0,
                iou=0.8,
            )
        )
        imagem.segmentacoes_brutas = [
            segmentacao
        ]
        return imagem


class FakePathResolver(PathResolver):
    pass


def test_processar_imagem_carrega_masks_e_persiste_resultado(monkeypatch) -> None:
    repository = FakeImagemRepository()
    ground_truth_repository = FakeGroundTruthBinarizadaRepository()
    binarizacao_repository = FakeBinarizacaoRepository()
    segmentacao_repository = FakeSegmentacaoRepository()
    service = FakeAvaliacaoService()
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_brutos_dir="/gt/raw",
        segmentacoes_brutas_dir="/pred/raw",
        segmentacoes_binarizadas_dir="/pred/bin",
        ground_truth_binarizada_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/tmp/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_mask_array_avaliacao",
        lambda nome_arquivo, nome_modelo, path_resolver, nome_binarizacao=None: (
            ground_truth_mask if nome_modelo == "ground_truth" else model_mask
        ),
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_score_mask_predita",
        lambda nome_arquivo, nome_modelo, path_resolver: score_mask,
    )
    controller = AvaliacaoController(
        imagem_repository=repository,
        ground_truth_binarizada_repository=ground_truth_repository,
        segmentacao_binarizada_repository=binarizacao_repository,
        segmentacao_bruta_repository=segmentacao_repository,
        avaliacao_service=service,
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)
    model_mask = np.ones((2, 2), dtype=np.uint8)
    score_mask = np.full((2, 2), 127, dtype=np.float64)

    imagem_avaliada = controller.processar_imagem(imagem)

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert len(ground_truth_repository.salvos) == 1
    assert len(segmentacao_repository.salvos) == 1
    assert len(binarizacao_repository.salvos) == 1
    assert service.chamadas[0][0] is imagem
    assert np.array_equal(service.chamadas[0][1], ground_truth_mask)
    assert list(service.chamadas[0][2]) == ["u2netp"]
    assert np.array_equal(service.chamadas[0][2]["u2netp"], model_mask)
    assert list(service.chamadas[0][3]) == ["u2netp"]
    assert np.array_equal(service.chamadas[0][3]["u2netp"], score_mask)
    assert service.chamadas[0][4] == "GaussianaOpening"


def test_processar_imagens_registra_ok_e_skip(monkeypatch) -> None:
    repository = FakeImagemRepository()
    service = FakeAvaliacaoService()
    controller = AvaliacaoController(
        imagem_repository=repository,
        ground_truth_binarizada_repository=FakeGroundTruthBinarizadaRepository(),
        segmentacao_binarizada_repository=FakeBinarizacaoRepository(),
        segmentacao_bruta_repository=FakeSegmentacaoRepository(),
        avaliacao_service=service,
    )
    imagem_skip = Imagem(nome_arquivo="ja_avaliada", fazenda="A", peso=1.0)
    imagem_skip.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="ja_avaliada",
        area=10.0,
        perimetro=20.0,
    )
    segmentacao_skip = SegmentacaoBruta(
        nome_arquivo="ja_avaliada",
        nome_modelo="u2netp",
        auprc=0.9,
    )
    segmentacao_skip.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            estrategia_binarizacao="GaussianaOpening",
            area=5.0,
            perimetro=7.0,
            iou=0.8,
        )
    )
    imagem_skip.segmentacoes_brutas = [segmentacao_skip]
    imagem_ok = Imagem(nome_arquivo="avaliar", fazenda="B", peso=2.0)
    repository.imagens = [imagem_skip, imagem_ok]
    processadas: list[str] = []

    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )

    def fake_processar_imagem(
        imagem: Imagem,
    ) -> Imagem:
        processadas.append(imagem.nome_arquivo)
        return imagem

    monkeypatch.setattr(controller, "processar_imagem", fake_processar_imagem)

    stats = controller.processar_imagens()

    assert processadas == ["avaliar"]
    assert stats.total == 2
    assert stats.ok == 1
    assert stats.skip == 1
    assert stats.erro == 0
