from __future__ import annotations

from collections.abc import Iterable
import time

from src.config import MODELOS_PARA_AVALIACAO
from src.io.mask_utils import carregar_mask_array_avaliacao
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasAvaliacao,
    imprimir_resumo_avaliacao,
    imprimir_status_avaliacao,
)
from src.models import Imagem
from src.repositories import ImagemRepository
from src.services.avaliacao_service import AvaliacaoService


class AvaliacaoController:
    def __init__(
        self,
        sqlite_path: str | None = None,
        path_resolver: PathResolver | None = None,
        imagem_repository: ImagemRepository | None = None,
        avaliacao_service: AvaliacaoService | None = None,
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
        self.avaliacao_service = (
            avaliacao_service if avaliacao_service is not None else AvaliacaoService()
        )

    def processar_imagem(
        self,
        imagem: Imagem,
        modelos_para_avaliacao: Iterable[str] | None = None,
    ) -> Imagem:
        nomes_modelo = list(modelos_para_avaliacao or MODELOS_PARA_AVALIACAO)
        ground_truth_mask = carregar_mask_array_avaliacao(
            imagem.nome_arquivo,
            "ground_truth",
            path_resolver=self.path_resolver,
        )
        mascaras_modelo = {
            nome_modelo: carregar_mask_array_avaliacao(
                imagem.nome_arquivo,
                nome_modelo,
                path_resolver=self.path_resolver,
            )
            for nome_modelo in nomes_modelo
        }

        imagem_avaliada = self.avaliacao_service.avaliar(
            imagem=imagem,
            ground_truth_mask=ground_truth_mask,
            mascaras_modelo=mascaras_modelo,
        )
        return self.imagem_repository.save(imagem_avaliada)

    def processar_imagens(
        self,
        imagens: Iterable[Imagem] | None = None,
        modelos_para_avaliacao: Iterable[str] | None = None,
    ) -> EstatisticasAvaliacao:
        linhas = list(imagens) if imagens is not None else self.imagem_repository.list()
        nomes_modelo = list(modelos_para_avaliacao or MODELOS_PARA_AVALIACAO)
        stats = EstatisticasAvaliacao(total=len(linhas))

        print("Calculando metricas de avaliacao")

        for idx, imagem in enumerate(linhas, start=1):
            identificador = f"{idx}/{len(linhas)}"

            if self._imagem_ja_avaliada(imagem, nomes_modelo):
                stats.registrar_skip()
                imprimir_status_avaliacao(identificador, imagem.nome_arquivo, stats)
                continue

            inicio = time.perf_counter()
            try:
                self.processar_imagem(
                    imagem=imagem,
                    modelos_para_avaliacao=nomes_modelo,
                )
            except Exception as exc:
                stats.registrar_erro()
                print(
                    "[ERRO AVALIACAO] "
                    f"Falha ao avaliar {imagem.nome_arquivo}: {exc}"
                )
            else:
                stats.registrar_ok_com_duracao(time.perf_counter() - inicio)

            imprimir_status_avaliacao(identificador, imagem.nome_arquivo, stats)

        imprimir_resumo_avaliacao(stats)
        return stats

    @staticmethod
    def _imagem_ja_avaliada(
        imagem: Imagem,
        nomes_modelo: list[str],
    ) -> bool:
        ground_truth = imagem.ground_truth_binarizada
        if (
            ground_truth is None
            or ground_truth.area is None
            or ground_truth.perimetro is None
        ):
            return False

        segmentacoes = {
            segmentacao.nome_modelo: segmentacao
            for segmentacao in imagem.segmentacoes
        }
        for nome_modelo in nomes_modelo:
            segmentacao = segmentacoes.get(nome_modelo)
            if segmentacao is None:
                return False
            if (
                segmentacao.area is None
                or segmentacao.perimetro is None
                or segmentacao.iou is None
            ):
                return False

        return True
