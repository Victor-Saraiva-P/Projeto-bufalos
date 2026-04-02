from __future__ import annotations

from collections.abc import Iterable, Sequence
import time

from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES, SEGMENTACAO_BINARIZATION_STRATEGIES
from src.io.mask_utils import (
    carregar_mask_array_avaliacao,
    carregar_score_mask_predita,
)
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasAvaliacao,
    imprimir_resumo_avaliacao,
    imprimir_resumo_avaliacao_execucao,
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


class MascaraBinarizadaNaoEncontradaError(FileNotFoundError):
    pass


class AvaliacaoController:
    def __init__(
        self,
        imagem_repository: ImagemRepository | None = None,
        ground_truth_binarizada_repository: GroundTruthBinarizadaRepository | None = None,
        segmentacao_binarizada_repository: SegmentacaoBinarizadaRepository | None = None,
        segmentacao_bruta_repository: SegmentacaoBrutaRepository | None = None,
        avaliacao_service: AvaliacaoService | None = None,
        estrategias_binarizacao: Sequence[str] | None = None,
    ):
        self.path_resolver = PathResolver.from_config()
        self.estrategias_binarizacao = list(
            dict.fromkeys(
                estrategias_binarizacao
                if estrategias_binarizacao is not None
                else SEGMENTACAO_BINARIZATION_STRATEGIES
            )
        )
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
        execucao: int | None = None,
        estrategias_binarizacao: Sequence[str] | None = None,
    ) -> Imagem:
        nomes_modelo = list(MODELOS_PARA_AVALIACAO)
        estrategias = list(
            dict.fromkeys(
                estrategias_binarizacao
                if estrategias_binarizacao is not None
                else self.estrategias_binarizacao
            )
        )
        ground_truth_mask = carregar_mask_array_avaliacao(
            imagem.nome_arquivo,
            "ground_truth",
            path_resolver=self.path_resolver,
        )
        imagem_avaliada = imagem
        execucoes = [execucao] if execucao is not None else range(1, NUM_EXECUCOES + 1)
        for execucao_atual in execucoes:
            score_masks_modelo = {
                nome_modelo: carregar_score_mask_predita(
                    imagem.nome_arquivo,
                    nome_modelo,
                    execucao=execucao_atual,
                    path_resolver=self.path_resolver,
                )
                for nome_modelo in nomes_modelo
            }

            for estrategia_binarizacao in estrategias:
                mascaras_modelo = {
                    nome_modelo: self._carregar_segmentacao_binarizada(
                        nome_arquivo=imagem.nome_arquivo,
                        nome_modelo=nome_modelo,
                        execucao=execucao_atual,
                        estrategia_binarizacao=estrategia_binarizacao,
                    )
                    for nome_modelo in nomes_modelo
                }

                imagem_avaliada = self.avaliacao_service.avaliar(
                    imagem=imagem_avaliada,
                    ground_truth_mask=ground_truth_mask,
                    mascaras_modelo=mascaras_modelo,
                    score_masks_modelo=score_masks_modelo,
                    estrategia_binarizacao=estrategia_binarizacao,
                    execucao=execucao_atual,
                )
        ground_truth = imagem_avaliada.ground_truth_binarizada
        if ground_truth is not None:
            self.ground_truth_binarizada_repository.save(ground_truth)

        segmentacoes_binarizadas = [
            segmentacao_binarizada
            for segmentacao_bruta in imagem_avaliada.segmentacoes_brutas
            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
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
        stats = EstatisticasAvaliacao(
            total=len(linhas) * NUM_EXECUCOES * len(self.estrategias_binarizacao)
        )

        print("Calculando metricas de avaliacao")

        for estrategia_binarizacao in self.estrategias_binarizacao:
            print(
                "Calculando metricas de avaliacao para a estrategia "
                f"{estrategia_binarizacao}"
            )
            for execucao in range(1, NUM_EXECUCOES + 1):
                stats_execucao = EstatisticasAvaliacao(total=len(linhas))
                for idx, imagem in enumerate(linhas, start=1):
                    identificador = f"{idx}/{len(linhas)}"

                    if self._execucao_estrategia_ja_avaliada(
                        imagem,
                        nomes_modelo,
                        execucao,
                        estrategia_binarizacao,
                    ):
                        stats.registrar_skip()
                        stats_execucao.registrar_skip()
                        imprimir_status_avaliacao(
                            identificador,
                            imagem.nome_arquivo,
                            stats_execucao,
                            execucao,
                            estrategia_binarizacao=estrategia_binarizacao,
                        )
                        continue

                    inicio = time.perf_counter()
                    try:
                        self.processar_imagem(
                            imagem=imagem,
                            execucao=execucao,
                            estrategias_binarizacao=[estrategia_binarizacao],
                        )
                    except Exception as exc:
                        stats.registrar_erro()
                        stats_execucao.registrar_erro()
                        print(
                            "[ERRO AVALIACAO] "
                            f"Falha ao avaliar {imagem.nome_arquivo} na execucao_{execucao} "
                            f"com a estrategia {estrategia_binarizacao}: {exc}"
                        )
                        if isinstance(exc, MascaraBinarizadaNaoEncontradaError):
                            raise
                    else:
                        duracao = time.perf_counter() - inicio
                        stats.registrar_ok_com_duracao(duracao)
                        stats_execucao.registrar_ok_com_duracao(duracao)

                    imprimir_status_avaliacao(
                        identificador,
                        imagem.nome_arquivo,
                        stats_execucao,
                        execucao,
                        estrategia_binarizacao=estrategia_binarizacao,
                    )
                imprimir_resumo_avaliacao_execucao(
                    execucao,
                    stats_execucao,
                    estrategia_binarizacao=estrategia_binarizacao,
                )

        imprimir_resumo_avaliacao(stats)
        return stats

    def _imagem_ja_avaliada(
        self,
        imagem: Imagem,
        nomes_modelo: list[str],
    ) -> bool:
        for execucao in range(1, NUM_EXECUCOES + 1):
            if not self._execucao_ja_avaliada(imagem, nomes_modelo, execucao):
                return False
        return True

    def _execucao_ja_avaliada(
        self,
        imagem: Imagem,
        nomes_modelo: list[str],
        execucao: int,
    ) -> bool:
        for estrategia_binarizacao in self.estrategias_binarizacao:
            if not self._execucao_estrategia_ja_avaliada(
                imagem,
                nomes_modelo,
                execucao,
                estrategia_binarizacao,
            ):
                return False
        return True

    def _execucao_estrategia_ja_avaliada(
        self,
        imagem: Imagem,
        nomes_modelo: list[str],
        execucao: int,
        estrategia_binarizacao: str,
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
        for nome_modelo in nomes_modelo:
            segmentacao_bruta = segmentacoes_brutas.get((nome_modelo, execucao))
            if segmentacao_bruta is None:
                return False
            if segmentacao_bruta.auprc <= SegmentacaoBruta.AUPRC_NAO_CALCULADA:
                return False
            if (
                segmentacao_bruta.soft_dice
                <= SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO
            ):
                return False
            segmentacao_binarizada_atual = next(
                (
                    segmentacao_binarizada
                    for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
                    if (
                        segmentacao_binarizada.estrategia_binarizacao
                        == estrategia_binarizacao
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

    def _carregar_segmentacao_binarizada(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        execucao: int,
        estrategia_binarizacao: str,
    ):
        try:
            return carregar_mask_array_avaliacao(
                nome_arquivo,
                nome_modelo,
                path_resolver=self.path_resolver,
                execucao=execucao,
                nome_binarizacao=estrategia_binarizacao,
            )
        except FileNotFoundError as exc:
            raise MascaraBinarizadaNaoEncontradaError(
                "Mascara binarizada nao encontrada para "
                f"imagem={nome_arquivo}, modelo={nome_modelo}, "
                f"execucao={execucao}, estrategia={estrategia_binarizacao}. "
                "Rode a etapa de binarizacao para essa estrategia antes da avaliacao."
            ) from exc
