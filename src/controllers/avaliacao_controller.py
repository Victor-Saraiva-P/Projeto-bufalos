from __future__ import annotations

from collections.abc import Iterable
import time

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES
from src.io.mask_utils import (
    carregar_mask_array_avaliacao,
    carregar_score_mask_predita,
)
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasAvaliacao,
    imprimir_resumo_avaliacao,
    imprimir_status_avaliacao,
)
from src.models import Imagem, SegmentacaoBruta
from src.repositories import (
    GroundTruthBinarizadaRepository,
    ImagemRepository,
    SegmentacaoBinarizadaRepository,
    SegmentacaoBrutaRepository,
)
from src.services.avaliacao_service import AvaliacaoService


class AvaliacaoController:
    ESTRATEGIA_BINARIZACAO_PADRAO = GaussianOpeningBinarizationStrategy().nome_pasta

    def __init__(
        self,
        imagem_repository: ImagemRepository | None = None,
        ground_truth_binarizada_repository: GroundTruthBinarizadaRepository | None = None,
        segmentacao_binarizada_repository: SegmentacaoBinarizadaRepository | None = None,
        segmentacao_bruta_repository: SegmentacaoBrutaRepository | None = None,
        avaliacao_service: AvaliacaoService | None = None,
    ):
        self.path_resolver = PathResolver.from_config()
        self.estrategia_binarizacao = self.ESTRATEGIA_BINARIZACAO_PADRAO
        self.imagem_repository = (
            imagem_repository
            if imagem_repository is not None
            else ImagemRepository(self.path_resolver.sqlite_path)
        )
        sqlite_path = getattr(self.imagem_repository, "sqlite_path", self.path_resolver.sqlite_path)
        self.ground_truth_binarizada_repository = (
            ground_truth_binarizada_repository
            if ground_truth_binarizada_repository is not None
            else GroundTruthBinarizadaRepository(sqlite_path)
        )
        self.segmentacao_binarizada_repository = (
            segmentacao_binarizada_repository
            if segmentacao_binarizada_repository is not None
            else SegmentacaoBinarizadaRepository(sqlite_path)
        )
        self.segmentacao_bruta_repository = (
            segmentacao_bruta_repository
            if segmentacao_bruta_repository is not None
            else SegmentacaoBrutaRepository(sqlite_path)
        )
        self.avaliacao_service = (
            avaliacao_service if avaliacao_service is not None else AvaliacaoService()
        )

    def processar_imagem(
        self,
        imagem: Imagem,
    ) -> Imagem:
        nomes_modelo = list(MODELOS_PARA_AVALIACAO)
        ground_truth_mask = carregar_mask_array_avaliacao(
            imagem.nome_arquivo,
            "ground_truth",
            path_resolver=self.path_resolver,
        )
        imagem_avaliada = imagem
        for execucao in range(1, NUM_EXECUCOES + 1):
            mascaras_modelo = {
                nome_modelo: carregar_mask_array_avaliacao(
                    imagem.nome_arquivo,
                    nome_modelo,
                    path_resolver=self.path_resolver,
                    execucao=execucao,
                    nome_binarizacao=self.estrategia_binarizacao,
                )
                for nome_modelo in nomes_modelo
            }
            score_masks_modelo = {
                nome_modelo: carregar_score_mask_predita(
                    imagem.nome_arquivo,
                    nome_modelo,
                    execucao=execucao,
                    path_resolver=self.path_resolver,
                )
                for nome_modelo in nomes_modelo
            }

            imagem_avaliada = self.avaliacao_service.avaliar(
                imagem=imagem_avaliada,
                ground_truth_mask=ground_truth_mask,
                mascaras_modelo=mascaras_modelo,
                score_masks_modelo=score_masks_modelo,
                estrategia_binarizacao=self.estrategia_binarizacao,
                execucao=execucao,
            )
        ground_truth = imagem_avaliada.ground_truth_binarizada
        if ground_truth is not None:
            self.ground_truth_binarizada_repository.save(ground_truth)

        segmentacoes_binarizadas = [
            segmentacao_binarizada
            for segmentacao_bruta in imagem_avaliada.segmentacoes_brutas
            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
            if segmentacao_binarizada.estrategia_binarizacao == self.estrategia_binarizacao
        ]
        for segmentacao_bruta in imagem_avaliada.segmentacoes_brutas:
            self.segmentacao_bruta_repository.save(segmentacao_bruta)
        for segmentacao_binarizada in segmentacoes_binarizadas:
            self.segmentacao_binarizada_repository.save(segmentacao_binarizada)
        return imagem_avaliada

    def processar_imagens(
        self,
        imagens: Iterable[Imagem] | None = None,
    ) -> EstatisticasAvaliacao:
        linhas = list(imagens) if imagens is not None else self.imagem_repository.list()
        nomes_modelo = list(MODELOS_PARA_AVALIACAO)
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

    def _imagem_ja_avaliada(
        self,
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

        segmentacoes_brutas = {
            (segmentacao_bruta.nome_modelo, segmentacao_bruta.execucao): segmentacao_bruta
            for segmentacao_bruta in imagem.segmentacoes_brutas
        }
        for execucao in range(1, NUM_EXECUCOES + 1):
            for nome_modelo in nomes_modelo:
                segmentacao_bruta = segmentacoes_brutas.get((nome_modelo, execucao))
                if segmentacao_bruta is None:
                    return False
                if (
                    segmentacao_bruta.auprc <= SegmentacaoBruta.AUPRC_NAO_CALCULADA
                ):
                    return False
                segmentacao_binarizada_atual = next(
                    (
                        segmentacao_binarizada
                        for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
                        if (
                            segmentacao_binarizada.estrategia_binarizacao
                            == self.estrategia_binarizacao
                        )
                    ),
                    None,
                )
                if (
                    segmentacao_binarizada_atual is None
                    or segmentacao_binarizada_atual.area is None
                    or segmentacao_binarizada_atual.perimetro is None
                    or segmentacao_binarizada_atual.iou is None
                ):
                    return False

        return True
