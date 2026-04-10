from __future__ import annotations

from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import time

from src.config import (
    EVALUATION_PARALLELISM_BATCH_SIZE,
    EVALUATION_PARALLELISM_ENABLED,
    EVALUATION_PARALLELISM_EXECUTOR,
    EVALUATION_PARALLELISM_MAX_WORKERS,
    MODELOS_PARA_AVALIACAO,
    NUM_EXECUCOES,
    SEGMENTACAO_BINARIZATION_STRATEGIES,
)
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
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)
from src.repositories import (
    GroundTruthBinarizadaRepository,
    ImagemRepository,
    SegmentacaoBinarizadaRepository,
    SegmentacaoBrutaRepository,
)
from src.services.avaliacao_service import (
    AvaliacaoExecucaoResultado,
    AvaliacaoService,
)


class MascaraBinarizadaNaoEncontradaError(FileNotFoundError):
    pass


@dataclass(frozen=True)
class AvaliacaoExecucaoTask:
    nome_arquivo: str
    execucao: int
    nomes_modelo: tuple[str, ...]
    estrategias_binarizacao: tuple[str, ...]
    path_resolver: PathResolver


def _carregar_segmentacao_binarizada_worker(
    *,
    nome_arquivo: str,
    nome_modelo: str,
    execucao: int,
    estrategia_binarizacao: str,
    path_resolver: PathResolver,
):
    try:
        return carregar_mask_array_avaliacao(
            nome_arquivo,
            nome_modelo,
            path_resolver=path_resolver,
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


def _avaliar_execucao_task(task: AvaliacaoExecucaoTask) -> AvaliacaoExecucaoResultado:
    ground_truth_mask = carregar_mask_array_avaliacao(
        task.nome_arquivo,
        "ground_truth",
        path_resolver=task.path_resolver,
    )
    score_masks_modelo = {
        nome_modelo: carregar_score_mask_predita(
            task.nome_arquivo,
            nome_modelo,
            execucao=task.execucao,
            path_resolver=task.path_resolver,
        )
        for nome_modelo in task.nomes_modelo
    }
    mascaras_modelo_por_estrategia = {
        estrategia_binarizacao: {
            nome_modelo: _carregar_segmentacao_binarizada_worker(
                nome_arquivo=task.nome_arquivo,
                nome_modelo=nome_modelo,
                execucao=task.execucao,
                estrategia_binarizacao=estrategia_binarizacao,
                path_resolver=task.path_resolver,
            )
            for nome_modelo in task.nomes_modelo
        }
        for estrategia_binarizacao in task.estrategias_binarizacao
    }
    return AvaliacaoService().avaliar_execucao(
        nome_arquivo=task.nome_arquivo,
        ground_truth_mask=ground_truth_mask,
        mascaras_modelo_por_estrategia=mascaras_modelo_por_estrategia,
        score_masks_modelo=score_masks_modelo,
        execucao=task.execucao,
    )


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
        self.parallelism_enabled = EVALUATION_PARALLELISM_ENABLED
        self.parallelism_executor = EVALUATION_PARALLELISM_EXECUTOR
        self.parallelism_max_workers = max(1, EVALUATION_PARALLELISM_MAX_WORKERS)
        self.parallelism_batch_size = max(1, EVALUATION_PARALLELISM_BATCH_SIZE)

    def processar_imagem(
        self,
        imagem: Imagem,
        execucao: int | None = None,
        estrategias_binarizacao: Sequence[str] | None = None,
    ) -> Imagem:
        nomes_modelo = tuple(MODELOS_PARA_AVALIACAO)
        estrategias = tuple(
            dict.fromkeys(
                estrategias_binarizacao
                if estrategias_binarizacao is not None
                else self.estrategias_binarizacao
            )
        )
        imagem_avaliada = imagem
        execucoes = [execucao] if execucao is not None else range(1, NUM_EXECUCOES + 1)

        for execucao_atual in execucoes:
            resultado = self._avaliar_execucao_local(
                nome_arquivo=imagem.nome_arquivo,
                nomes_modelo=nomes_modelo,
                execucao=execucao_atual,
                estrategias_binarizacao=estrategias,
            )
            imagem_avaliada = self.avaliacao_service.aplicar_resultado(
                imagem_avaliada,
                resultado,
            )
            self._persistir_resultado_execucao(resultado)

        return imagem_avaliada

    def processar_imagens(
        self,
        imagens: Iterable[Imagem] | None = None,
    ) -> EstatisticasAvaliacao:
        linhas = list(imagens) if imagens is not None else self.imagem_repository.list()
        nomes_modelo = list(MODELOS_PARA_AVALIACAO)
        stats = EstatisticasAvaliacao(total=len(linhas) * NUM_EXECUCOES)

        print("Calculando metricas de avaliacao")
        print(
            "Configuracao de concorrencia: "
            f"enabled={self.parallelism_enabled} | "
            f"executor={self.parallelism_executor} | "
            f"max_workers={self.parallelism_max_workers} | "
            f"batch_size={self.parallelism_batch_size}"
        )

        tarefas_por_execucao: dict[int, list[Imagem]] = {
            execucao: [] for execucao in range(1, NUM_EXECUCOES + 1)
        }
        for execucao in range(1, NUM_EXECUCOES + 1):
            for imagem in linhas:
                if self._execucao_ja_avaliada(imagem, nomes_modelo, execucao):
                    stats.registrar_skip()
                    continue
                tarefas_por_execucao[execucao].append(imagem)

        if self._usar_process_pool():
            self._processar_imagens_em_paralelo(
                tarefas_por_execucao=tarefas_por_execucao,
                stats=stats,
                nomes_modelo=tuple(nomes_modelo),
            )
        else:
            self._processar_imagens_em_serie(
                tarefas_por_execucao=tarefas_por_execucao,
                stats=stats,
            )

        imprimir_resumo_avaliacao(stats)
        return stats

    def _processar_imagens_em_serie(
        self,
        *,
        tarefas_por_execucao: dict[int, list[Imagem]],
        stats: EstatisticasAvaliacao,
    ) -> None:
        for execucao in range(1, NUM_EXECUCOES + 1):
            imagens_execucao = tarefas_por_execucao[execucao]
            stats_execucao = EstatisticasAvaliacao(total=len(imagens_execucao))
            for idx, imagem in enumerate(imagens_execucao, start=1):
                identificador = f"{idx}/{len(imagens_execucao)}"
                inicio = time.perf_counter()
                try:
                    self.processar_imagem(
                        imagem=imagem,
                        execucao=execucao,
                        estrategias_binarizacao=self.estrategias_binarizacao,
                    )
                except Exception as exc:
                    stats.registrar_erro()
                    stats_execucao.registrar_erro()
                    print(
                        "[ERRO AVALIACAO] "
                        f"Falha ao avaliar {imagem.nome_arquivo} na execucao_{execucao}: {exc}"
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
                )

            imprimir_resumo_avaliacao_execucao(execucao, stats_execucao)

    def _processar_imagens_em_paralelo(
        self,
        *,
        tarefas_por_execucao: dict[int, list[Imagem]],
        stats: EstatisticasAvaliacao,
        nomes_modelo: tuple[str, ...],
    ) -> None:
        for execucao in range(1, NUM_EXECUCOES + 1):
            imagens_execucao = tarefas_por_execucao[execucao]
            stats_execucao = EstatisticasAvaliacao(total=len(imagens_execucao))
            if not imagens_execucao:
                imprimir_resumo_avaliacao_execucao(execucao, stats_execucao)
                continue

            tasks = [
                AvaliacaoExecucaoTask(
                    nome_arquivo=imagem.nome_arquivo,
                    execucao=execucao,
                    nomes_modelo=nomes_modelo,
                    estrategias_binarizacao=tuple(self.estrategias_binarizacao),
                    path_resolver=self.path_resolver,
                )
                for imagem in imagens_execucao
            ]

            future_to_task: dict[object, AvaliacaoExecucaoTask] = {}
            with ProcessPoolExecutor(max_workers=self.parallelism_max_workers) as executor:
                concluidas = 0
                for inicio_lote in range(0, len(tasks), self.parallelism_batch_size):
                    lote = tasks[inicio_lote : inicio_lote + self.parallelism_batch_size]
                    future_to_task.clear()
                    for task in lote:
                        future = executor.submit(_avaliar_execucao_task, task)
                        future_to_task[future] = task

                    for future in as_completed(future_to_task):
                        concluidas += 1
                        task = future_to_task[future]
                        identificador = f"{concluidas}/{len(tasks)}"
                        inicio = time.perf_counter()
                        try:
                            resultado = future.result()
                            self._persistir_resultado_execucao(resultado)
                        except Exception as exc:
                            stats.registrar_erro()
                            stats_execucao.registrar_erro()
                            print(
                                "[ERRO AVALIACAO] "
                                f"Falha ao avaliar {task.nome_arquivo} na execucao_{execucao}: {exc}"
                            )
                            if isinstance(exc, MascaraBinarizadaNaoEncontradaError):
                                raise
                        else:
                            duracao = time.perf_counter() - inicio
                            stats.registrar_ok_com_duracao(duracao)
                            stats_execucao.registrar_ok_com_duracao(duracao)

                        imprimir_status_avaliacao(
                            identificador,
                            task.nome_arquivo,
                            stats_execucao,
                            execucao,
                        )

            imprimir_resumo_avaliacao_execucao(execucao, stats_execucao)

    def _avaliar_execucao_local(
        self,
        *,
        nome_arquivo: str,
        nomes_modelo: Sequence[str],
        execucao: int,
        estrategias_binarizacao: Sequence[str],
    ) -> AvaliacaoExecucaoResultado:
        ground_truth_mask = carregar_mask_array_avaliacao(
            nome_arquivo,
            "ground_truth",
            path_resolver=self.path_resolver,
        )
        score_masks_modelo = {
            nome_modelo: carregar_score_mask_predita(
                nome_arquivo,
                nome_modelo,
                execucao=execucao,
                path_resolver=self.path_resolver,
            )
            for nome_modelo in nomes_modelo
        }
        mascaras_modelo_por_estrategia = {
            estrategia_binarizacao: {
                nome_modelo: _carregar_segmentacao_binarizada_worker(
                    nome_arquivo=nome_arquivo,
                    nome_modelo=nome_modelo,
                    execucao=execucao,
                    estrategia_binarizacao=estrategia_binarizacao,
                    path_resolver=self.path_resolver,
                )
                for nome_modelo in nomes_modelo
            }
            for estrategia_binarizacao in estrategias_binarizacao
        }
        return self.avaliacao_service.avaliar_execucao(
            nome_arquivo=nome_arquivo,
            ground_truth_mask=ground_truth_mask,
            mascaras_modelo_por_estrategia=mascaras_modelo_por_estrategia,
            score_masks_modelo=score_masks_modelo,
            execucao=execucao,
        )

    def _persistir_resultado_execucao(
        self,
        resultado: AvaliacaoExecucaoResultado,
    ) -> None:
        if not self._suporta_persistencia_em_lote():
            ground_truth = GroundTruthBinarizada(
                nome_arquivo=resultado.nome_arquivo,
                area=resultado.ground_truth_area,
                perimetro=resultado.ground_truth_perimetro,
            )
            self.ground_truth_binarizada_repository.save(ground_truth)
            for segmentacao in resultado.segmentacoes_brutas:
                self.segmentacao_bruta_repository.save(
                    SegmentacaoBruta(
                        nome_arquivo=segmentacao.nome_arquivo,
                        nome_modelo=segmentacao.nome_modelo,
                        execucao=segmentacao.execucao,
                        auprc=segmentacao.auprc,
                        soft_dice=segmentacao.soft_dice,
                        brier_score=segmentacao.brier_score,
                    )
                )
            for binarizacao in resultado.segmentacoes_binarizadas:
                self.segmentacao_binarizada_repository.save(
                    SegmentacaoBinarizada(
                        nome_arquivo=binarizacao.nome_arquivo,
                        nome_modelo=binarizacao.nome_modelo,
                        execucao=binarizacao.execucao,
                        estrategia_binarizacao=binarizacao.estrategia_binarizacao,
                        area=binarizacao.area,
                        perimetro=binarizacao.perimetro,
                        iou=binarizacao.iou,
                        precision=binarizacao.precision,
                        recall=binarizacao.recall,
                    )
                )
            return

        sessionmaker = self.ground_truth_binarizada_repository.sessionmaker
        with sessionmaker() as session:
            session.merge(
                GroundTruthBinarizada(
                    nome_arquivo=resultado.nome_arquivo,
                    area=resultado.ground_truth_area,
                    perimetro=resultado.ground_truth_perimetro,
                )
            )
            for segmentacao in resultado.segmentacoes_brutas:
                session.merge(
                    SegmentacaoBruta(
                        nome_arquivo=segmentacao.nome_arquivo,
                        nome_modelo=segmentacao.nome_modelo,
                        execucao=segmentacao.execucao,
                        auprc=segmentacao.auprc,
                        soft_dice=segmentacao.soft_dice,
                        brier_score=segmentacao.brier_score,
                    )
                )
            for binarizacao in resultado.segmentacoes_binarizadas:
                session.merge(
                    SegmentacaoBinarizada(
                        nome_arquivo=binarizacao.nome_arquivo,
                        nome_modelo=binarizacao.nome_modelo,
                        execucao=binarizacao.execucao,
                        estrategia_binarizacao=binarizacao.estrategia_binarizacao,
                        area=binarizacao.area,
                        perimetro=binarizacao.perimetro,
                        iou=binarizacao.iou,
                        precision=binarizacao.precision,
                        recall=binarizacao.recall,
                    )
                )
            session.commit()

    def _suporta_persistencia_em_lote(self) -> bool:
        return all(
            hasattr(repository, "sessionmaker")
            for repository in (
                self.ground_truth_binarizada_repository,
                self.segmentacao_bruta_repository,
                self.segmentacao_binarizada_repository,
            )
        )

    def _usar_process_pool(self) -> bool:
        return (
            self.parallelism_enabled
            and self.parallelism_executor == "process"
            and self.parallelism_max_workers > 1
        )

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
            if segmentacao_bruta.soft_dice <= SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO:
                return False
            if (
                segmentacao_bruta.brier_score
                <= SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO
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
                or segmentacao_binarizada_atual.precision is None
                or segmentacao_binarizada_atual.recall is None
            ):
                return False

        return True
