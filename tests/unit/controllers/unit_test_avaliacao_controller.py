import numpy as np
import pytest

from src.controllers.avaliacao_controller import (
    AvaliacaoController,
    MascaraBinarizadaNaoEncontradaError,
)
from src.io.path_resolver import PathResolver
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)
from src.services.avaliacao_service import (
    AvaliacaoExecucaoResultado,
    SegmentacaoBinarizadaResultado,
    SegmentacaoBrutaResultado,
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
                str,
                np.ndarray,
                dict[str, dict[str, np.ndarray]],
                dict[str, np.ndarray],
                int,
            ]
        ] = []

    def avaliar_execucao(
        self,
        nome_arquivo: str,
        ground_truth_mask: np.ndarray,
        mascaras_modelo_por_estrategia: dict[str, dict[str, np.ndarray]],
        score_masks_modelo: dict[str, np.ndarray],
        execucao: int,
    ) -> AvaliacaoExecucaoResultado:
        self.chamadas.append(
            (
                nome_arquivo,
                ground_truth_mask,
                mascaras_modelo_por_estrategia,
                score_masks_modelo,
                execucao,
            )
        )
        return AvaliacaoExecucaoResultado(
            nome_arquivo=nome_arquivo,
            execucao=execucao,
            ground_truth_area=10.0,
            ground_truth_perimetro=20.0,
            segmentacoes_brutas=(
                SegmentacaoBrutaResultado(
                    nome_arquivo=nome_arquivo,
                    nome_modelo="u2netp",
                    execucao=execucao,
                    auprc=0.9,
                    soft_dice=0.82,
                    brier_score=0.08,
                ),
            )
            ,
            segmentacoes_binarizadas=tuple(
                SegmentacaoBinarizadaResultado(
                    nome_arquivo=nome_arquivo,
                    nome_modelo="u2netp",
                    execucao=execucao,
                    estrategia_binarizacao=estrategia_binarizacao,
                    area=5.0,
                    perimetro=7.0,
                    iou=0.8,
                    precision=0.85,
                    recall=0.75,
                )
                for estrategia_binarizacao in mascaras_modelo_por_estrategia
            ),
        )

    def aplicar_resultado(
        self,
        imagem: Imagem,
        resultado: AvaliacaoExecucaoResultado,
    ) -> Imagem:
        imagem.ground_truth_binarizada = GroundTruthBinarizada(
            nome_arquivo=imagem.nome_arquivo,
            area=resultado.ground_truth_area,
            perimetro=resultado.ground_truth_perimetro,
        )
        for segmentacao_resultado in resultado.segmentacoes_brutas:
            segmentacao = next(
                (
                    existente
                    for existente in imagem.segmentacoes_brutas
                    if (
                        existente.nome_modelo == segmentacao_resultado.nome_modelo
                        and existente.execucao == segmentacao_resultado.execucao
                    )
                ),
                None,
            )
            if segmentacao is None:
                segmentacao = SegmentacaoBruta(
                    nome_arquivo=segmentacao_resultado.nome_arquivo,
                    nome_modelo=segmentacao_resultado.nome_modelo,
                    execucao=segmentacao_resultado.execucao,
                    auprc=segmentacao_resultado.auprc,
                    soft_dice=segmentacao_resultado.soft_dice,
                    brier_score=segmentacao_resultado.brier_score,
                )
                imagem.segmentacoes_brutas.append(segmentacao)
            else:
                segmentacao.auprc = segmentacao_resultado.auprc
                segmentacao.soft_dice = segmentacao_resultado.soft_dice
                segmentacao.brier_score = segmentacao_resultado.brier_score

        for binarizada_resultado in resultado.segmentacoes_binarizadas:
            segmentacao = next(
                existente
                for existente in imagem.segmentacoes_brutas
                if (
                    existente.nome_modelo == binarizada_resultado.nome_modelo
                    and existente.execucao == binarizada_resultado.execucao
                )
            )
            segmentacao.segmentacoes_binarizadas.append(
                SegmentacaoBinarizada(
                    nome_arquivo=binarizada_resultado.nome_arquivo,
                    nome_modelo=binarizada_resultado.nome_modelo,
                    execucao=binarizada_resultado.execucao,
                    estrategia_binarizacao=binarizada_resultado.estrategia_binarizacao,
                    area=binarizada_resultado.area,
                    perimetro=binarizada_resultado.perimetro,
                    iou=binarizada_resultado.iou,
                    precision=binarizada_resultado.precision,
                    recall=binarizada_resultado.recall,
                )
            )
        imagem.segmentacoes_brutas.sort(
            key=lambda existente: (existente.nome_modelo, existente.execucao)
        )
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
    monkeypatch.setattr("src.controllers.avaliacao_controller.NUM_EXECUCOES", 2)
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_mask_array_avaliacao",
        lambda nome_arquivo,
        nome_modelo,
        path_resolver,
        execucao=None,
        nome_binarizacao=None: (
            ground_truth_mask if nome_modelo == "ground_truth" else model_mask
        ),
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_score_mask_predita",
        lambda nome_arquivo, nome_modelo, execucao, path_resolver: score_mask,
    )
    controller = AvaliacaoController(
        imagem_repository=repository,
        ground_truth_binarizada_repository=ground_truth_repository,
        segmentacao_binarizada_repository=binarizacao_repository,
        segmentacao_bruta_repository=segmentacao_repository,
        avaliacao_service=service,
        estrategias_binarizacao=["GaussianaOpening", "LimiarFixo"],
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)
    model_mask = np.ones((2, 2), dtype=np.uint8)
    score_mask = np.full((2, 2), 127, dtype=np.float64)

    imagem_avaliada = controller.processar_imagem(imagem)

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert len(ground_truth_repository.salvos) == 1
    assert len(segmentacao_repository.salvos) == 2
    assert len(binarizacao_repository.salvos) == 4
    assert service.chamadas[0][0] == imagem.nome_arquivo
    assert np.array_equal(service.chamadas[0][1], ground_truth_mask)
    assert list(service.chamadas[0][2]) == ["GaussianaOpening", "LimiarFixo"]
    assert np.array_equal(service.chamadas[0][2]["GaussianaOpening"]["u2netp"], model_mask)
    assert list(service.chamadas[0][3]) == ["u2netp"]
    assert np.array_equal(service.chamadas[0][3]["u2netp"], score_mask)
    assert [chamada[4] for chamada in service.chamadas] == [1, 2]
    assert [segmentacao.execucao for segmentacao in imagem_avaliada.segmentacoes_brutas] == [
        1,
        2,
    ]
    assert all(
        segmentacao.soft_dice == 0.82 for segmentacao in imagem_avaliada.segmentacoes_brutas
    )
    assert {segmentacao.brier_score for segmentacao in imagem_avaliada.segmentacoes_brutas} == {
        0.08
    }
    assert all(
        {binarizada.estrategia_binarizacao for binarizada in segmentacao.segmentacoes_binarizadas}
        == {"GaussianaOpening", "LimiarFixo"}
        for segmentacao in imagem_avaliada.segmentacoes_brutas
    )


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
        execucao=1,
        auprc=0.9,
        soft_dice=0.83,
        brier_score=0.08,
    )
    segmentacao_skip.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=5.0,
            perimetro=7.0,
            iou=0.8,
            precision=0.85,
            recall=0.75,
        )
    )
    segmentacao_skip.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="LimiarFixo",
            area=5.2,
            perimetro=7.1,
            iou=0.78,
            precision=0.82,
            recall=0.73,
        )
    )
    segmentacao_skip_execucao_2 = SegmentacaoBruta(
        nome_arquivo="ja_avaliada",
        nome_modelo="u2netp",
        execucao=2,
        auprc=0.91,
        soft_dice=0.84,
        brier_score=0.07,
    )
    segmentacao_skip_execucao_2.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            execucao=2,
            estrategia_binarizacao="GaussianaOpening",
            area=5.0,
            perimetro=7.0,
            iou=0.81,
            precision=0.86,
            recall=0.76,
        )
    )
    segmentacao_skip_execucao_2.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            execucao=2,
            estrategia_binarizacao="LimiarFixo",
            area=5.1,
            perimetro=7.2,
            iou=0.79,
            precision=0.83,
            recall=0.74,
        )
    )
    imagem_skip.segmentacoes_brutas = [segmentacao_skip, segmentacao_skip_execucao_2]
    imagem_ok = Imagem(nome_arquivo="avaliar", fazenda="B", peso=2.0)
    repository.imagens = [imagem_skip, imagem_ok]
    processadas: list[str] = []

    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr("src.controllers.avaliacao_controller.NUM_EXECUCOES", 2)

    def fake_processar_imagem(
        imagem: Imagem,
        execucao: int | None = None,
        estrategias_binarizacao=None,
    ) -> Imagem:
        estrategia = estrategias_binarizacao[0] if estrategias_binarizacao is not None else "todas"
        processadas.append(f"{imagem.nome_arquivo}:{execucao}:{estrategia}")
        return imagem

    monkeypatch.setattr(controller, "processar_imagem", fake_processar_imagem)
    controller.estrategias_binarizacao = ["GaussianaOpening", "LimiarFixo"]

    stats = controller.processar_imagens()

    assert processadas == [
        "avaliar:1:GaussianaOpening",
        "avaliar:2:GaussianaOpening",
    ]
    assert stats.total == 4
    assert stats.ok == 2
    assert stats.skip == 2
    assert stats.erro == 0


def test_processar_imagens_nao_considera_execucao_sem_soft_dice_como_avaliada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = FakeImagemRepository()
    service = FakeAvaliacaoService()
    controller = AvaliacaoController(
        imagem_repository=repository,
        ground_truth_binarizada_repository=FakeGroundTruthBinarizadaRepository(),
        segmentacao_binarizada_repository=FakeBinarizacaoRepository(),
        segmentacao_bruta_repository=FakeSegmentacaoRepository(),
        avaliacao_service=service,
    )
    imagem = Imagem(nome_arquivo="reavaliar", fazenda="A", peso=1.0)
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="reavaliar",
        area=10.0,
        perimetro=20.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="reavaliar",
        nome_modelo="u2netp",
        execucao=1,
        auprc=0.9,
        soft_dice=SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO,
        brier_score=0.08,
    )
    segmentacao.segmentacoes_binarizadas = [
        SegmentacaoBinarizada(
            nome_arquivo="reavaliar",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=5.0,
            perimetro=7.0,
            iou=0.8,
            precision=0.85,
            recall=0.75,
        ),
        SegmentacaoBinarizada(
            nome_arquivo="reavaliar",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="LimiarFixo",
            area=5.1,
            perimetro=7.1,
            iou=0.79,
            precision=0.82,
            recall=0.74,
        ),
    ]
    imagem.segmentacoes_brutas = [segmentacao]
    repository.imagens = [imagem]

    processadas: list[str] = []
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr("src.controllers.avaliacao_controller.NUM_EXECUCOES", 1)

    def fake_processar_imagem(
        imagem: Imagem,
        execucao: int | None = None,
        estrategias_binarizacao=None,
    ) -> Imagem:
        estrategia = estrategias_binarizacao[0] if estrategias_binarizacao is not None else "todas"
        processadas.append(f"{imagem.nome_arquivo}:{execucao}:{estrategia}")
        return imagem

    monkeypatch.setattr(controller, "processar_imagem", fake_processar_imagem)
    controller.estrategias_binarizacao = ["GaussianaOpening", "LimiarFixo"]

    stats = controller.processar_imagens()

    assert processadas == [
        "reavaliar:1:GaussianaOpening",
    ]
    assert stats.ok == 1
    assert stats.skip == 0


def test_execucao_estrategia_ja_avaliada_exige_brier_score_valido() -> None:
    controller = AvaliacaoController(
        imagem_repository=FakeImagemRepository(),
        ground_truth_binarizada_repository=FakeGroundTruthBinarizadaRepository(),
        segmentacao_binarizada_repository=FakeBinarizacaoRepository(),
        segmentacao_bruta_repository=FakeSegmentacaoRepository(),
        avaliacao_service=FakeAvaliacaoService(),
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=10.0,
        perimetro=20.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=0.9,
        soft_dice=0.82,
        brier_score=SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO,
    )
    segmentacao.segmentacoes_binarizadas.append(
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=5.0,
            perimetro=7.0,
            iou=0.8,
            precision=0.85,
            recall=0.75,
        )
    )
    imagem.segmentacoes_brutas = [segmentacao]

    resultado = controller._execucao_estrategia_ja_avaliada(
        imagem=imagem,
        nomes_modelo=["u2netp"],
        execucao=1,
        estrategia_binarizacao="GaussianaOpening",
    )

    assert resultado is False


def test_processar_imagem_falha_quando_estrategia_configurada_nao_tem_saida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = FakeImagemRepository()
    controller = AvaliacaoController(
        imagem_repository=repository,
        ground_truth_binarizada_repository=FakeGroundTruthBinarizadaRepository(),
        segmentacao_binarizada_repository=FakeBinarizacaoRepository(),
        segmentacao_bruta_repository=FakeSegmentacaoRepository(),
        avaliacao_service=FakeAvaliacaoService(),
        estrategias_binarizacao=["GaussianaOpening", "LimiarFixo"],
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)
    model_mask = np.ones((2, 2), dtype=np.uint8)
    score_mask = np.full((2, 2), 127, dtype=np.float64)

    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        {"u2netp": "cpu"},
    )
    monkeypatch.setattr("src.controllers.avaliacao_controller.NUM_EXECUCOES", 1)

    def fake_carregar_mask_array_avaliacao(
        nome_arquivo,
        nome_modelo,
        path_resolver,
        execucao=None,
        nome_binarizacao=None,
    ):
        if nome_modelo == "ground_truth":
            return ground_truth_mask
        if nome_binarizacao == "LimiarFixo":
            raise FileNotFoundError(nome_binarizacao)
        return model_mask

    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_mask_array_avaliacao",
        fake_carregar_mask_array_avaliacao,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_score_mask_predita",
        lambda nome_arquivo, nome_modelo, execucao, path_resolver: score_mask,
    )

    with pytest.raises(MascaraBinarizadaNaoEncontradaError, match="LimiarFixo"):
        controller.processar_imagem(imagem)
