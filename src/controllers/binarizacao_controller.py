from __future__ import annotations

from collections.abc import Iterable
import os

from src.binarizacao.binarizacao_base import BinarizationStrategy
from src.config import (
    MODELOS_PARA_AVALIACAO,
    NUM_EXECUCOES,
)
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasBinarizacao,
    imprimir_resumo_binarizacao,
    imprimir_resumo_binarizacao_execucao,
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
                caminho_entrada=self.path_resolver.caminho_ground_truth_bruta(
                    imagem.nome_arquivo
                ),
                caminho_saida=self.path_resolver.caminho_ground_truth_binarizada(
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
            stats = EstatisticasBinarizacao(total=len(linhas) * NUM_EXECUCOES)
            resumos[nome_modelo] = stats

            for execucao in range(1, NUM_EXECUCOES + 1):
                stats_execucao = EstatisticasBinarizacao(total=len(linhas))
                diretorio_modelo = self._diretorio_modelo(nome_modelo, execucao)

                if not os.path.isdir(diretorio_modelo):
                    print(
                        "[AVISO BINARIZACAO] "
                        f"Diretorio de mascaras nao encontrado para o modelo "
                        f"{nome_modelo} na execucao_{execucao}: {diretorio_modelo}. "
                        "Pulando execucao."
                    )
                    for _ in linhas:
                        stats.registrar_skip()
                        stats_execucao.registrar_skip()
                    continue

                for idx, imagem in enumerate(linhas, start=1):
                    resultado = self.binarizacao_service.processar_arquivo(
                        caminho_entrada=self.path_resolver.caminho_segmentacao_bruta(
                            nome_modelo,
                            imagem.nome_arquivo,
                            execucao=execucao,
                        ),
                        caminho_saida=self.path_resolver.caminho_segmentacao_binarizada(
                            nome_modelo,
                            imagem.nome_arquivo,
                            execucao=execucao,
                            nome_binarizacao=strategy.nome_pasta,
                        ),
                        strategy=strategy,
                    )
                    stats.registrar_resultado(resultado)
                    stats_execucao.registrar_resultado(resultado)

                    imprimir_status_binarizacao(
                        etapa="modelo",
                        identificador=f"{idx}/{len(linhas)}",
                        stats=stats_execucao,
                        nome_modelo=nome_modelo,
                        execucao=execucao,
                    )
                imprimir_resumo_binarizacao_execucao(
                    nome_modelo,
                    execucao,
                    stats_execucao,
                )
            imprimir_resumo_binarizacao_modelo(nome_modelo, stats)

        return resumos

    def _diretorio_modelo(self, nome_modelo: str, execucao: int) -> str:
        return os.path.join(
            self.path_resolver.segmentacoes_brutas_dir,
            self.path_resolver.nome_pasta_execucao(execucao),
            nome_modelo,
        )

    def verificar_segmentacoes(
        self,
    ):
        from src.controllers.imagem_controller import ImagemController

        return ImagemController(imagem_repository=self.imagem_repository).verificar_segmentacoes()
