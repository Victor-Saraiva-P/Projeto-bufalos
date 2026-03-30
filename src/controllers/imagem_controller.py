from __future__ import annotations

from src.config import (
    REMBG_IMAGE_TYPE,
)
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository
from src.services.imagem_service import ImagemService, ResumoVerificacaoPng


class ImagemController:
    def __init__(
        self,
        imagem_repository: ImagemRepository | None = None,
        imagem_service: ImagemService | None = None,
    ):
        self.path_resolver = PathResolver.from_config()
        self.imagem_repository = (
            imagem_repository
            if imagem_repository is not None
            else ImagemRepository(self.path_resolver.sqlite_path)
        )
        self.imagem_service = (
            imagem_service if imagem_service is not None else ImagemService()
        )

    def sincronizar_indice_excel(self) -> None:
        self.imagem_service.sincronizar_indice_excel(
            imagem_repository=self.imagem_repository,
            indice_path=self.path_resolver.indice_path,
        )

    def verificar_pngs_corrompidos(self) -> ResumoVerificacaoPng:
        return self.imagem_service.verificar_pngs_corrompidos(
            diretorio_base=self.path_resolver.generated_dir,
            extensao_arquivo=REMBG_IMAGE_TYPE,
        )

    def verificar_segmentacoes(self) -> ResumoVerificacaoPng:
        return self.imagem_service.verificar_pngs_corrompidos(
            diretorio_base=self.path_resolver.predicted_masks_raw_dir,
            extensao_arquivo=REMBG_IMAGE_TYPE,
        )
