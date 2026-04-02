from __future__ import annotations

import numpy as np

from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)
from src.metricas import AUPRC
from src.metricas.segmentacao_binarizada import Area, IoU, Perimetro


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
        area_ground_truth = Area(
            nome_arquivo=imagem.nome_arquivo,
            mask_array=ground_truth_mask,
            modelo="ground_truth",
        ).calcular()
        perimetro_ground_truth = Perimetro(
            nome_arquivo=imagem.nome_arquivo,
            mask_array=ground_truth_mask,
            modelo="ground_truth",
        ).calcular()

        imagem.ground_truth_binarizada = GroundTruthBinarizada(
            nome_arquivo=imagem.nome_arquivo,
            area=float(area_ground_truth),
            perimetro=float(perimetro_ground_truth),
        )

        segmentacoes_brutas = {
            (segmentacao.nome_modelo, segmentacao.execucao): segmentacao
            for segmentacao in imagem.segmentacoes_brutas
        }
        for nome_modelo, mask_modelo in mascaras_modelo.items():
            chave = (nome_modelo, execucao)
            segmentacoes_brutas[chave] = self._avaliar_modelo(
                imagem.nome_arquivo,
                nome_modelo,
                execucao,
                ground_truth_mask,
                mask_modelo,
                score_masks_modelo[nome_modelo],
                estrategia_binarizacao,
                segmentacoes_brutas.get(chave),
            )

        imagem.segmentacoes_brutas = sorted(
            segmentacoes_brutas.values(),
            key=lambda segmentacao: (segmentacao.nome_modelo, segmentacao.execucao),
        )
        return imagem

    def _avaliar_modelo(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        execucao: int,
        ground_truth_mask: np.ndarray,
        mask_modelo: np.ndarray,
        score_mask_modelo: np.ndarray,
        estrategia_binarizacao: str,
        segmentacao_bruta: SegmentacaoBruta | None = None,
    ) -> SegmentacaoBruta:
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
        auprc = AUPRC(
            nome_arquivo=nome_arquivo,
            score_mask=score_mask_modelo,
            ground_truth_mask=ground_truth_mask,
            modelo=nome_modelo,
        ).calcular()

        registro = segmentacao_bruta or SegmentacaoBruta(
            nome_arquivo=nome_arquivo,
            nome_modelo=nome_modelo,
            execucao=execucao,
            auprc=SegmentacaoBruta.AUPRC_NAO_CALCULADA,
        )
        registro.auprc = float(auprc)
        self._atualizar_segmentacao_binarizada(
            registro=registro,
            estrategia_binarizacao=estrategia_binarizacao,
            area=float(area),
            perimetro=float(perimetro),
            iou=float(iou),
        )
        return registro

    @staticmethod
    def _atualizar_segmentacao_binarizada(
        registro: SegmentacaoBruta,
        estrategia_binarizacao: str,
        area: float,
        perimetro: float,
        iou: float,
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
            )
            registro.segmentacoes_binarizadas.append(segmentacao_binarizada)
            return

        segmentacao_binarizada.area = area
        segmentacao_binarizada.perimetro = perimetro
        segmentacao_binarizada.iou = iou
