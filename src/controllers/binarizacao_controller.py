from __future__ import annotations

from collections.abc import Iterable, Sequence
import os

from src.binarizacao.binarizacao_base import BinarizationStrategy
from src.binarizacao.registro import (
    instanciar_estrategia_ground_truth_binarizacao,
    instanciar_estrategias_segmentacao_binarizacao,
)
from src.config import (
    GROUND_TRUTH_BINARIZATION_STRATEGY,
    MODELOS_PARA_AVALIACAO,
    NUM_EXECUCOES,
    SEGMENTACAO_BINARIZATION_STRATEGIES,
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
        ground_truth_strategy: BinarizationStrategy | None = None,
        segmentacao_strategies: Sequence[BinarizationStrategy] | None = None,
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
        self.ground_truth_strategy = (
            ground_truth_strategy
            if ground_truth_strategy is not None
            else instanciar_estrategia_ground_truth_binarizacao(
                GROUND_TRUTH_BINARIZATION_STRATEGY
            )
        )
        self.segmentacao_strategies = (
            list(segmentacao_strategies)
            if segmentacao_strategies is not None
            else instanciar_estrategias_segmentacao_binarizacao(
                SEGMENTACAO_BINARIZATION_STRATEGIES
            )
        )

    def processar_ground_truth(
        self,
        strategy: BinarizationStrategy | None = None,
        imagens: Iterable[Imagem] | None = None,
    ) -> EstatisticasBinarizacao:
        strategy = strategy or self.ground_truth_strategy
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
                estrategia_binarizacao=strategy.nome_pasta,
            )

        imprimir_resumo_binarizacao(f"ground_truth {strategy.nome_pasta}", stats)
        return stats

    def processar_ground_truth_configurada(
        self,
        imagens: Iterable[Imagem] | None = None,
    ) -> EstatisticasBinarizacao:
        return self.processar_ground_truth(
            strategy=self.ground_truth_strategy,
            imagens=imagens,
        )

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

        print(
            "Binarizando mascaras dos modelos com a estrategia "
            f"{strategy.nome_pasta}"
        )

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
                        estrategia_binarizacao=strategy.nome_pasta,
                    )
                imprimir_resumo_binarizacao_execucao(
                    nome_modelo,
                    execucao,
                    stats_execucao,
                    estrategia_binarizacao=strategy.nome_pasta,
                )
            imprimir_resumo_binarizacao_modelo(
                nome_modelo,
                stats,
                estrategia_binarizacao=strategy.nome_pasta,
            )

        return resumos

    def processar_segmentacoes_configuradas(
        self,
        imagens: Iterable[Imagem] | None = None,
    ) -> dict[str, dict[str, EstatisticasBinarizacao]]:
        return {
            strategy.nome_pasta: self.processar_segmentacoes(
                strategy=strategy,
                imagens=imagens,
            )
            for strategy in self.segmentacao_strategies
        }

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
