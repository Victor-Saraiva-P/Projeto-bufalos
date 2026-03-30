import numpy as np

from src.controllers.avaliacao_controller import AvaliacaoController
from src.io.path_resolver import PathResolver
from src.models import GroundTruthBinarizada, Imagem, Segmentacao


class FakeImagemRepository:
    def __init__(self) -> None:
        self.salvos: list[Imagem] = []

    def save(self, imagem: Imagem) -> Imagem:
        self.salvos.append(imagem)
        return imagem


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
    controller = AvaliacaoController(
        path_resolver=resolver,
        imagem_repository=repository,
        avaliacao_service=service,
    )
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    ground_truth_mask = np.zeros((2, 2), dtype=np.uint8)
    model_mask = np.ones((2, 2), dtype=np.uint8)

    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.carregar_mask_array_avaliacao",
        lambda nome_arquivo, nome_modelo, path_resolver: (
            ground_truth_mask if nome_modelo == "ground_truth" else model_mask
        ),
    )

    imagem_avaliada = controller.processar_imagem(
        imagem,
        modelos_para_avaliacao=["u2netp"],
    )

    assert imagem_avaliada.ground_truth_binarizada is not None
    assert len(repository.salvos) == 1
    assert service.chamadas[0][0] is imagem
    assert np.array_equal(service.chamadas[0][1], ground_truth_mask)
    assert list(service.chamadas[0][2]) == ["u2netp"]
    assert np.array_equal(service.chamadas[0][2]["u2netp"], model_mask)
