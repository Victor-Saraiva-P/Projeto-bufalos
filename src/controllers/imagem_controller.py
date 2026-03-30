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
        sqlite_path: str | None = None,
        path_resolver: PathResolver | None = None,
        imagem_repository: ImagemRepository | None = None,
        imagem_service: ImagemService | None = None,
    ):
        self.path_resolver = (
            path_resolver if path_resolver is not None else PathResolver.from_config()
        )
        sqlite_path_resolvido = (
            sqlite_path if sqlite_path is not None else self.path_resolver.sqlite_path
        )
        self.imagem_repository = (
            imagem_repository
            if imagem_repository is not None
            else ImagemRepository(sqlite_path_resolvido)
        )
        self.imagem_service = (
            imagem_service if imagem_service is not None else ImagemService()
        )

    def sincronizar_indice_excel(self, indice_path: str | None = None) -> None:
        self.imagem_service.sincronizar_indice_excel(
            imagem_repository=self.imagem_repository,
            indice_path=indice_path or self.path_resolver.indice_path,
        )

    def verificar_pngs_corrompidos(
        self,
        diretorio_base: str | None = None,
        extensao_arquivo: str = REMBG_IMAGE_TYPE,
    ) -> ResumoVerificacaoPng:
        return self.imagem_service.verificar_pngs_corrompidos(
            diretorio_base=diretorio_base or self.path_resolver.generated_dir,
            extensao_arquivo=extensao_arquivo,
        )

    def verificar_segmentacoes(
        self,
        extensao_arquivo: str = REMBG_IMAGE_TYPE,
    ) -> ResumoVerificacaoPng:
        return self.verificar_pngs_corrompidos(
            diretorio_base=self.path_resolver.predicted_masks_dir,
            extensao_arquivo=extensao_arquivo,
        )
