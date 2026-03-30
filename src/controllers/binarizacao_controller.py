from __future__ import annotations

from collections.abc import Iterable
import os

from src.binarizacao.estrategias import BinarizationStrategy
from src.config import (
    MODELOS_PARA_AVALIACAO,
)
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasBinarizacao,
    imprimir_resumo_binarizacao,
    imprimir_resumo_binarizacao_modelo,
    imprimir_status_binarizacao,
)
from src.models import Imagem
from src.repositories import ImagemRepository
from src.services.binarizacao_service import BinarizacaoService


class BinarizacaoController:
    def __init__(
        self,
        imagem_repository: ImagemRepository | None = None,
        binarizacao_service: BinarizacaoService | None = None,
    ):
        self.path_resolver = PathResolver.from_config()
        self.imagem_repository = (
            imagem_repository
            if imagem_repository is not None
            else ImagemRepository(self.path_resolver.sqlite_path)
        )
        self.binarizacao_service = (
            binarizacao_service
            if binarizacao_service is not None
            else BinarizacaoService()
        )

    def processar_ground_truth(
        self,
        strategy: BinarizationStrategy,
        imagens: Iterable[Imagem] | None = None,
    ) -> EstatisticasBinarizacao:
        linhas = (
            list(imagens)
            if imagens is not None
            else self.imagem_repository.list()
        )
        stats = EstatisticasBinarizacao(total=len(linhas))

        print("Convertendo Ground Truth para PNG binarizado")

        for idx, imagem in enumerate(linhas, start=1):
            resultado = self.binarizacao_service.processar_arquivo(
                caminho_entrada=self.path_resolver.caminho_ground_truth(imagem.nome_arquivo),
                caminho_saida=self.path_resolver.caminho_ground_truth_binaria(
                    imagem.nome_arquivo
                ),
                strategy=strategy,
            )
            stats.registrar_resultado(resultado)

            imprimir_status_binarizacao(
                etapa="ground_truth",
                identificador=f"{idx}/{len(linhas)}",
                stats=stats,
            )

        imprimir_resumo_binarizacao("ground_truth", stats)
        return stats

    def processar_segmentacoes(
        self,
        strategy: BinarizationStrategy,
        imagens: Iterable[Imagem] | None = None,
    ) -> dict[str, EstatisticasBinarizacao]:
        linhas = (
            list(imagens)
            if imagens is not None
            else self.imagem_repository.list()
        )
        modelos = dict(MODELOS_PARA_AVALIACAO)
        resumos: dict[str, EstatisticasBinarizacao] = {}

        print("Binarizando mascaras dos modelos")

        for nome_modelo in modelos:
            stats = EstatisticasBinarizacao(total=len(linhas))
            resumos[nome_modelo] = stats
            diretorio_modelo = self._diretorio_modelo(nome_modelo)

            if not os.path.isdir(diretorio_modelo):
                print(
                    "[AVISO BINARIZACAO] "
                    f"Diretorio de mascaras nao encontrado para o modelo "
                    f"{nome_modelo}: {diretorio_modelo}. Pulando modelo."
                )
                for _ in linhas:
                    stats.registrar_skip()
                imprimir_resumo_binarizacao_modelo(nome_modelo, stats)
                continue

            for idx, imagem in enumerate(linhas, start=1):
                resultado = self.binarizacao_service.processar_arquivo(
                    caminho_entrada=self.path_resolver.caminho_mascara_predita(
                        nome_modelo,
                        imagem.nome_arquivo,
                    ),
                    caminho_saida=self.path_resolver.caminho_mascara_predita_binaria(
                        nome_modelo,
                        imagem.nome_arquivo,
                    ),
                    strategy=strategy,
                )
                stats.registrar_resultado(resultado)

                imprimir_status_binarizacao(
                    etapa="modelo",
                    identificador=f"{nome_modelo} {idx}/{len(linhas)}",
                    stats=stats,
                )

            imprimir_resumo_binarizacao_modelo(nome_modelo, stats)

        return resumos

    def _diretorio_modelo(self, nome_modelo: str) -> str:
        return os.path.join(self.path_resolver.predicted_masks_dir, nome_modelo)

    def verificar_segmentacoes(
        self,
    ):
        from src.controllers.imagem_controller import ImagemController

        return ImagemController(imagem_repository=self.imagem_repository).verificar_segmentacoes()
