from __future__ import annotations

from dataclasses import dataclass

from src.controllers.imagem_controller import ImagemController
from src.io.path_resolver import PathResolver
from src.services.imagem_service import ResumoVerificacaoPng


@dataclass
class FakeImagemService:
    def __post_init__(self) -> None:
        self.sincronizacoes: list[tuple[object, str]] = []
        self.verificacoes: list[tuple[str, str]] = []

    def sincronizar_indice_excel(self, imagem_repository, indice_path: str) -> None:
        self.sincronizacoes.append((imagem_repository, indice_path))

    def verificar_pngs_corrompidos(
        self,
        diretorio_base: str,
        extensao_arquivo: str,
    ) -> ResumoVerificacaoPng:
        self.verificacoes.append((diretorio_base, extensao_arquivo))
        return ResumoVerificacaoPng(
            total_png=1,
            arquivos_integros=1,
            arquivos_removidos=0,
            falhas_remocao=0,
        )


class FakePathResolver(PathResolver):
    pass


def test_imagem_controller_delega_sincronizacao_para_service() -> None:
    repository = object()
    service = FakeImagemService()
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
    controller = ImagemController(
        path_resolver=resolver,
        imagem_repository=repository,
        imagem_service=service,
    )

    controller.sincronizar_indice_excel("/tmp/Indice.xlsx")

    assert service.sincronizacoes == [(repository, "/tmp/Indice.xlsx")]


def test_imagem_controller_verifica_segmentacoes_usando_diretorio_padrao(monkeypatch) -> None:
    service = FakeImagemService()
    resolver = FakePathResolver(
        data_dir="/data",
        generated_dir="/generated",
        images_dir="/orig",
        ground_truth_raw_dir="/gt/raw",
        predicted_masks_dir="/tmp/predicted_masks",
        predicted_masks_binary_dir="/pred/bin",
        ground_truth_binary_dir="/gt/bin",
        evaluation_dir="/eval",
        indice_path="/tmp/Indice.xlsx",
        sqlite_path="/tmp/bufalos.sqlite3",
    )
    controller = ImagemController(
        path_resolver=resolver,
        imagem_repository=object(),
        imagem_service=service,
    )

    resumo = controller.verificar_segmentacoes(extensao_arquivo=".png")

    assert resumo.total_png == 1
    assert service.verificacoes == [("/tmp/predicted_masks", ".png")]
