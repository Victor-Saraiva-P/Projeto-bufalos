"""
Coletor de métricas de segmentação para avaliação de modelos.

Este módulo processa todas as imagens e modelos, calculando métricas
e materializando uma base analítica de segmentação bruta a partir do SQLite.
"""

from typing import Optional

import pandas as pd
from tqdm.auto import tqdm

from src.config import SEGMENTACAO_BINARIZADA_ANALISE_EXECUCAO
from src.controllers.avaliacao_controller import (
    AvaliacaoController,
    MascaraBinarizadaNaoEncontradaError,
)
from src.models import Imagem, SegmentacaoBruta
from src.repositories import ImagemRepository

TAG_COLUMNS = (
    "ok",
    "multi_bufalos",
    "cortado",
    "angulo_extremo",
    "baixo_contraste",
    "ocluido",
)


def build_binarized_metrics_dataframe(
    imagens: list[Imagem],
    execucao_escolhida: int | None = None,
) -> pd.DataFrame:
    if execucao_escolhida is None:
        execucao_escolhida = SEGMENTACAO_BINARIZADA_ANALISE_EXECUCAO

    if execucao_escolhida < 1:
        raise ValueError("A execucao escolhida para analise binarizada deve ser >= 1.")

    registros: list[dict[str, float | str | bool | int]] = []

    for imagem in imagens:
        tags = sorted(dict.fromkeys(imagem.nomes_tags))
        tags_sem_ok = [tag for tag in tags if tag != "ok"]
        num_tags_problema = len(tags_sem_ok)

        if not tags:
            grupo_dificuldade = "nao_revisada"
        elif "ok" in tags and num_tags_problema == 0:
            grupo_dificuldade = "ok"
        elif num_tags_problema <= 1:
            grupo_dificuldade = "1_problema"
        else:
            grupo_dificuldade = "2_ou_mais_problemas"

        for segmentacao_bruta in imagem.segmentacoes_brutas:
            # Docs: docs/decisoes-tecnicas/analise-da-segmentacao-binarizada-por-execucao-fixa.md
            if segmentacao_bruta.execucao != execucao_escolhida:
                continue

            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas:
                if (
                    segmentacao_binarizada.iou is None
                    or segmentacao_binarizada.precision is None
                    or segmentacao_binarizada.recall is None
                ):
                    continue

                registro = {
                    "nome_arquivo": imagem.nome_arquivo,
                    "fazenda": imagem.fazenda,
                    "peso": imagem.peso,
                    "modelo": segmentacao_bruta.nome_modelo,
                    "execucao": segmentacao_bruta.execucao,
                    "estrategia_binarizacao": segmentacao_binarizada.estrategia_binarizacao,
                    "iou": float(segmentacao_binarizada.iou),
                    "precision": float(segmentacao_binarizada.precision),
                    "recall": float(segmentacao_binarizada.recall),
                    "area": float(segmentacao_binarizada.area),
                    "perimetro": float(segmentacao_binarizada.perimetro),
                    "tags": ",".join(tags),
                    "tags_sem_ok": ",".join(tags_sem_ok),
                    "num_tags_problema": num_tags_problema,
                    "tem_tag_problema": num_tags_problema > 0,
                    "grupo_dificuldade": grupo_dificuldade,
                }

                for tag_name in TAG_COLUMNS:
                    registro[f"tag_{tag_name}"] = tag_name in tags

                registros.append(registro)

    return pd.DataFrame(registros)


class MetricsCollector:
    """
    Coleta e processa métricas de segmentação para todos os modelos.

    Esta classe:
    - Itera sobre todas as imagens do índice persistido no SQLite
    - Para cada imagem, calcula métricas da segmentacao bruta
    - Persiste resultados por imagem no SQLite
    - Materializa um DataFrame analítico por imagem + modelo + execucao
    """

    def __init__(
        self,
        force_recalculate: bool = False,
        imagem_repository: ImagemRepository | None = None,
        avaliacao_controller: AvaliacaoController | None = None,
    ):
        self.force_recalculate = force_recalculate
        self.df: Optional[pd.DataFrame] = None
        self.imagem_repository = (
            imagem_repository if imagem_repository is not None else ImagemRepository()
        )
        self.avaliacao_controller = (
            avaliacao_controller
            if avaliacao_controller is not None
            else AvaliacaoController(imagem_repository=self.imagem_repository)
        )

    def collect_all_metrics(self) -> pd.DataFrame:
        if not self.force_recalculate:
            sqlite_df = self._build_metrics_dataframe(self.imagem_repository.list())
            if not sqlite_df.empty:
                print("✓ Métricas carregadas do SQLite")
                self.df = sqlite_df
                return self.df

        print("Coletando métricas de todas as imagens...")
        indice = self.imagem_repository.list()
        modelos_com_erro = set()

        for imagem in tqdm(indice, desc="Processando imagens"):
            try:
                self._calculate_metrics_for_image(imagem, modelos_com_erro)
            except MascaraBinarizadaNaoEncontradaError:
                raise
            except Exception as e:
                print(f"\n⚠ Erro ao processar {imagem.nome_arquivo}: {e}")
                continue

        self.df = self._build_metrics_dataframe(self.imagem_repository.list())

        if self.df.empty:
            raise ValueError("Nenhuma métrica foi coletada. Verifique as segmentações.")

        if modelos_com_erro:
            print(f"\n⚠ Modelos sem segmentações encontradas:")
            for modelo in sorted(modelos_com_erro):
                print(f"  - {modelo}")

        print(f"\n✓ Métricas coletadas: {len(self.df)} registros")
        print(f"  - Imagens processadas: {self.df['nome_arquivo'].nunique()}")
        print(f"  - Modelos com dados: {self.df['modelo'].nunique()}")

        return self.df

    def _calculate_metrics_for_image(self, imagem: Imagem, modelos_com_erro: set) -> None:
        imagem_avaliada = self.avaliacao_controller.processar_imagem(imagem)

        for segmentacao_bruta in imagem_avaliada.segmentacoes_brutas:
            if (
                segmentacao_bruta.auprc <= SegmentacaoBruta.AUPRC_NAO_CALCULADA
                or segmentacao_bruta.soft_dice
                <= SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO
                or segmentacao_bruta.brier_score
                <= SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO
            ):
                modelos_com_erro.add(segmentacao_bruta.nome_modelo)
                continue

            if not segmentacao_bruta.segmentacoes_binarizadas:
                modelos_com_erro.add(segmentacao_bruta.nome_modelo)
                continue

            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas:
                if (
                    segmentacao_binarizada.area is None
                    or segmentacao_binarizada.perimetro is None
                    or segmentacao_binarizada.iou is None
                    or segmentacao_binarizada.precision is None
                    or segmentacao_binarizada.recall is None
                ):
                    modelos_com_erro.add(segmentacao_bruta.nome_modelo)
                    break

    @staticmethod
    def _build_metrics_dataframe(imagens: list[Imagem]) -> pd.DataFrame:
        registros: list[dict[str, float | str]] = []

        for imagem in imagens:
            tags = sorted(dict.fromkeys(imagem.nomes_tags))
            tags_sem_ok = [tag for tag in tags if tag != "ok"]
            num_tags_problema = len(tags_sem_ok)

            if not tags:
                grupo_dificuldade = "nao_revisada"
            elif "ok" in tags and num_tags_problema == 0:
                grupo_dificuldade = "ok"
            elif num_tags_problema <= 1:
                grupo_dificuldade = "1_problema"
            else:
                grupo_dificuldade = "2_ou_mais_problemas"

            for segmentacao_bruta in imagem.segmentacoes_brutas:
                if (
                    segmentacao_bruta.auprc <= SegmentacaoBruta.AUPRC_NAO_CALCULADA
                    or segmentacao_bruta.soft_dice
                    <= SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO
                    or segmentacao_bruta.brier_score
                    <= SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO
                ):
                    continue

                registro = {
                    "nome_arquivo": imagem.nome_arquivo,
                    "fazenda": imagem.fazenda,
                    "peso": imagem.peso,
                    "modelo": segmentacao_bruta.nome_modelo,
                    "execucao": segmentacao_bruta.execucao,
                    "auprc": segmentacao_bruta.auprc,
                    "soft_dice": segmentacao_bruta.soft_dice,
                    "brier_score": segmentacao_bruta.brier_score,
                    "tags": ",".join(tags),
                    "tags_sem_ok": ",".join(tags_sem_ok),
                    "num_tags_problema": num_tags_problema,
                    "tem_tag_problema": num_tags_problema > 0,
                    "grupo_dificuldade": grupo_dificuldade,
                }

                for tag_name in TAG_COLUMNS:
                    registro[f"tag_{tag_name}"] = tag_name in tags

                registros.append(registro)

        return pd.DataFrame(registros)
