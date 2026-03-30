import numpy as np

from src.controllers.avaliacao_controller import AvaliacaoController
from src.io.path_resolver import PathResolver
from src.models import GroundTruthBinarizada, Imagem, Segmentacao


class FakeImagemRepository:
    def __init__(self) -> None:
        self.salvos: list[Imagem] = []
        self.imagens: list[Imagem] = []

    def save(self, imagem: Imagem) -> Imagem:
        self.salvos.append(imagem)
        return imagem

    def list(self) -> list[Imagem]:
        return list(self.imagens)


class FakeAvaliacaoService:
    def __init__(self) -> None:
        self.chamadas: list[tuple[Imagem, np.ndarray, dict[str, np.ndarray]]] = []

    def avaliar(
        self,
        imagem: Imagem,
        ground_truth_mask: np.ndarray,
        mascaras_modelo: dict[str, np.ndarray],
    ) -> Imagem:
        self.chamadas.append((imagem, ground_truth_mask, mascaras_modelo))
        imagem.ground_truth_binarizada = GroundTruthBinarizada(
            nome_arquivo=imagem.nome_arquivo,
            area=10.0,
            perimetro=20.0,
        )
        imagem.segmentacoes = [
            Segmentacao(
                nome_arquivo=imagem.nome_arquivo,
                nome_modelo="u2netp",
                area=5.0,
                perimetro=7.0,
                iou=0.8,
            )
        ]
        return imagem


class FakePathResolver(PathResolver):
    pass


def test_processar_imagem_carrega_masks_e_persiste_resultado(monkeypatch) -> None:
    repository = FakeImagemRepository()
    service = FakeAvaliacaoService()
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_raw_dir="/gt/raw",
        predicted_masks_dir="/pred/raw",
        predicted_masks_binary_dir="/pred/bin",
        ground_truth_binary_dir="/gt/bin",
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
        lambda nome_arquivo, nome_modelo, path_resolver: (
            ground_truth_mask if nome_modelo == "ground_truth" else model_mask
        ),
    )
    controller = AvaliacaoController(
        imagem_repository=repository,
        avaliacao_service=service,
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)
    model_mask = np.ones((2, 2), dtype=np.uint8)

    imagem_avaliada = controller.processar_imagem(imagem)

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert len(repository.salvos) == 1
    assert service.chamadas[0][0] is imagem
    assert np.array_equal(service.chamadas[0][1], ground_truth_mask)
    assert list(service.chamadas[0][2]) == ["u2netp"]
    assert np.array_equal(service.chamadas[0][2]["u2netp"], model_mask)


def test_processar_imagens_registra_ok_e_skip(monkeypatch) -> None:
    repository = FakeImagemRepository()
    service = FakeAvaliacaoService()
    controller = AvaliacaoController(
        imagem_repository=repository,
        avaliacao_service=service,
    )
    imagem_skip = Imagem(nome_arquivo="ja_avaliada", fazenda="A", peso=1.0)
    imagem_skip.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="ja_avaliada",
        area=10.0,
        perimetro=20.0,
    )
    imagem_skip.segmentacoes = [
        Segmentacao(
            nome_arquivo="ja_avaliada",
            nome_modelo="u2netp",
            area=5.0,
            perimetro=7.0,
            iou=0.8,
        )
    ]
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
