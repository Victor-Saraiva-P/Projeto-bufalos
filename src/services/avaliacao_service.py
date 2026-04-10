from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)
from src.metricas import AUPRC, BrierScore, SoftDice
from src.metricas.segmentacao_binarizada import Area, IoU, Perimetro, Precision, Recall


@dataclass(frozen=True)
class SegmentacaoBrutaResultado:
    nome_arquivo: str
    nome_modelo: str
    execucao: int
    auprc: float
    soft_dice: float
    brier_score: float


@dataclass(frozen=True)
class SegmentacaoBinarizadaResultado:
    nome_arquivo: str
    nome_modelo: str
    execucao: int
    estrategia_binarizacao: str
    area: float
    perimetro: float
    iou: float
    precision: float
    recall: float


@dataclass(frozen=True)
class AvaliacaoExecucaoResultado:
    nome_arquivo: str
    execucao: int
    ground_truth_area: float
    ground_truth_perimetro: float
    segmentacoes_brutas: tuple[SegmentacaoBrutaResultado, ...]
    segmentacoes_binarizadas: tuple[SegmentacaoBinarizadaResultado, ...]


class AvaliacaoService:
    def avaliar(
        self,
        imagem: Imagem,
        ground_truth_mask: np.ndarray,
        mascaras_modelo: dict[str, np.ndarray],
        score_masks_modelo: dict[str, np.ndarray],
        estrategia_binarizacao: str,
        execucao: int,
    ) -> Imagem:
        resultado = self.avaliar_execucao(
            nome_arquivo=imagem.nome_arquivo,
            ground_truth_mask=ground_truth_mask,
            mascaras_modelo_por_estrategia={estrategia_binarizacao: mascaras_modelo},
            score_masks_modelo=score_masks_modelo,
            execucao=execucao,
        )
        return self.aplicar_resultado(imagem, resultado)

    def avaliar_execucao(
        self,
        nome_arquivo: str,
        ground_truth_mask: np.ndarray,
        mascaras_modelo_por_estrategia: dict[str, dict[str, np.ndarray]],
        score_masks_modelo: dict[str, np.ndarray],
        execucao: int,
    ) -> AvaliacaoExecucaoResultado:
        area_ground_truth = Area(
            nome_arquivo=nome_arquivo,
            mask_array=ground_truth_mask,
            modelo="ground_truth",
        ).calcular()
        perimetro_ground_truth = Perimetro(
            nome_arquivo=nome_arquivo,
            mask_array=ground_truth_mask,
            modelo="ground_truth",
        ).calcular()

        metricas_brutas: list[SegmentacaoBrutaResultado] = []
        metricas_binarizadas: list[SegmentacaoBinarizadaResultado] = []

        for nome_modelo, score_mask_modelo in score_masks_modelo.items():
            score_mask_normalizado = self._normalizar_score_mask(score_mask_modelo)
            auprc = AUPRC(
                nome_arquivo=nome_arquivo,
                score_mask=score_mask_normalizado,
                ground_truth_mask=ground_truth_mask,
                modelo=nome_modelo,
            ).calcular()
            soft_dice = SoftDice(
                nome_arquivo=nome_arquivo,
                score_mask=score_mask_normalizado,
                ground_truth_mask=ground_truth_mask,
                modelo=nome_modelo,
            ).calcular()
            brier_score = BrierScore(
                nome_arquivo=nome_arquivo,
                score_mask=score_mask_normalizado,
                ground_truth_mask=ground_truth_mask,
                modelo=nome_modelo,
            ).calcular()
            metricas_brutas.append(
                SegmentacaoBrutaResultado(
                    nome_arquivo=nome_arquivo,
                    nome_modelo=nome_modelo,
                    execucao=execucao,
                    auprc=float(auprc),
                    soft_dice=float(soft_dice),
                    brier_score=float(brier_score),
                )
            )

            for estrategia_binarizacao, mascaras_modelo in mascaras_modelo_por_estrategia.items():
                mask_modelo = mascaras_modelo[nome_modelo]
                area = Area(
                    nome_arquivo=nome_arquivo,
                    mask_array=mask_modelo,
                    modelo=nome_modelo,
                ).calcular()
                perimetro = Perimetro(
                    nome_arquivo=nome_arquivo,
                    mask_array=mask_modelo,
                    modelo=nome_modelo,
                ).calcular()
                iou = IoU(
                    nome_arquivo=nome_arquivo,
                    mask_modelo=mask_modelo,
                    mask_ground_truth=ground_truth_mask,
                    modelo=nome_modelo,
                ).calcular()
                precision = Precision(
                    nome_arquivo=nome_arquivo,
                    mask_modelo=mask_modelo,
                    mask_ground_truth=ground_truth_mask,
                    modelo=nome_modelo,
                ).calcular()
                recall = Recall(
                    nome_arquivo=nome_arquivo,
                    mask_modelo=mask_modelo,
                    mask_ground_truth=ground_truth_mask,
                    modelo=nome_modelo,
                ).calcular()

                metricas_binarizadas.append(
                    SegmentacaoBinarizadaResultado(
                        nome_arquivo=nome_arquivo,
                        nome_modelo=nome_modelo,
                        execucao=execucao,
                        estrategia_binarizacao=estrategia_binarizacao,
                        area=float(area),
                        perimetro=float(perimetro),
                        iou=float(iou),
                        precision=float(precision),
                        recall=float(recall),
                    )
                )

        return AvaliacaoExecucaoResultado(
            nome_arquivo=nome_arquivo,
            execucao=execucao,
            ground_truth_area=float(area_ground_truth),
            ground_truth_perimetro=float(perimetro_ground_truth),
            segmentacoes_brutas=tuple(
                sorted(
                    metricas_brutas,
                    key=lambda item: (item.nome_modelo, item.execucao),
                )
            ),
            segmentacoes_binarizadas=tuple(
                sorted(
                    metricas_binarizadas,
                    key=lambda item: (
                        item.nome_modelo,
                        item.execucao,
                        item.estrategia_binarizacao,
                    ),
                )
            ),
        )

    def aplicar_resultado(
        self,
        imagem: Imagem,
        resultado: AvaliacaoExecucaoResultado,
    ) -> Imagem:
        imagem.ground_truth_binarizada = GroundTruthBinarizada(
            nome_arquivo=resultado.nome_arquivo,
            area=resultado.ground_truth_area,
            perimetro=resultado.ground_truth_perimetro,
        )

        segmentacoes_existentes = {
            (segmentacao.nome_modelo, segmentacao.execucao): segmentacao
            for segmentacao in imagem.segmentacoes_brutas
        }

        for segmentacao_resultado in resultado.segmentacoes_brutas:
            chave = (segmentacao_resultado.nome_modelo, segmentacao_resultado.execucao)
            segmentacao = segmentacoes_existentes.get(chave)
            if segmentacao is None:
                segmentacao = SegmentacaoBruta(
                    nome_arquivo=segmentacao_resultado.nome_arquivo,
                    nome_modelo=segmentacao_resultado.nome_modelo,
                    execucao=segmentacao_resultado.execucao,
                    auprc=SegmentacaoBruta.AUPRC_NAO_CALCULADA,
                    soft_dice=SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO,
                    brier_score=SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO,
                )
                segmentacoes_existentes[chave] = segmentacao

            segmentacao.auprc = segmentacao_resultado.auprc
            segmentacao.soft_dice = segmentacao_resultado.soft_dice
            segmentacao.brier_score = segmentacao_resultado.brier_score

        for binarizada_resultado in resultado.segmentacoes_binarizadas:
            chave = (binarizada_resultado.nome_modelo, binarizada_resultado.execucao)
            segmentacao = segmentacoes_existentes[chave]
            self._atualizar_segmentacao_binarizada(
                registro=segmentacao,
                estrategia_binarizacao=binarizada_resultado.estrategia_binarizacao,
                area=binarizada_resultado.area,
                perimetro=binarizada_resultado.perimetro,
                iou=binarizada_resultado.iou,
                precision=binarizada_resultado.precision,
                recall=binarizada_resultado.recall,
            )

        imagem.segmentacoes_brutas = sorted(
            segmentacoes_existentes.values(),
            key=lambda segmentacao: (segmentacao.nome_modelo, segmentacao.execucao),
        )
        return imagem

    @staticmethod
    def _atualizar_segmentacao_binarizada(
        registro: SegmentacaoBruta,
        estrategia_binarizacao: str,
        area: float,
        perimetro: float,
        iou: float,
        precision: float,
        recall: float,
    ) -> None:
        segmentacoes_binarizadas = {
            segmentacao_binarizada.estrategia_binarizacao: segmentacao_binarizada
            for segmentacao_binarizada in registro.segmentacoes_binarizadas
        }
        segmentacao_binarizada = segmentacoes_binarizadas.get(estrategia_binarizacao)
        if segmentacao_binarizada is None:
            segmentacao_binarizada = SegmentacaoBinarizada(
                nome_arquivo=registro.nome_arquivo,
                nome_modelo=registro.nome_modelo,
                execucao=registro.execucao,
                estrategia_binarizacao=estrategia_binarizacao,
                area=area,
                perimetro=perimetro,
                iou=iou,
                precision=precision,
                recall=recall,
            )
            registro.segmentacoes_binarizadas.append(segmentacao_binarizada)
            return

        segmentacao_binarizada.area = area
        segmentacao_binarizada.perimetro = perimetro
        segmentacao_binarizada.iou = iou
        segmentacao_binarizada.precision = precision
        segmentacao_binarizada.recall = recall

    @staticmethod
    def _normalizar_score_mask(score_mask: np.ndarray) -> np.ndarray:
        score_mask_array = np.asarray(score_mask, dtype=np.float64)
        if score_mask_array.size == 0:
            return score_mask_array

        if np.all((score_mask_array >= 0.0) & (score_mask_array <= 1.0)):
            return score_mask_array

        if np.all((score_mask_array >= 0.0) & (score_mask_array <= 255.0)):
            return score_mask_array / 255.0

        return score_mask_array
