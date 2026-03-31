from __future__ import annotations

import numpy as np

from src.binarizacao import AUPRC
from src.models import Binarizacao, GroundTruthBinarizada, Imagem, Segmentacao
from src.metricas.segmentacao_binarizada import Area, IoU, Perimetro


class AvaliacaoService:
    def avaliar(
        self,
        imagem: Imagem,
        ground_truth_mask: np.ndarray,
        mascaras_modelo: dict[str, np.ndarray],
        score_masks_modelo: dict[str, np.ndarray],
        estrategia_binarizacao: str,
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

        segmentacoes = {
            segmentacao.nome_modelo: segmentacao
            for segmentacao in imagem.segmentacoes
        }
        for nome_modelo, mask_modelo in mascaras_modelo.items():
            segmentacoes[nome_modelo] = self._avaliar_modelo(
                imagem.nome_arquivo,
                nome_modelo,
                ground_truth_mask,
                mask_modelo,
                score_masks_modelo[nome_modelo],
                estrategia_binarizacao,
                segmentacoes.get(nome_modelo),
            )

        imagem.segmentacoes = sorted(
            segmentacoes.values(),
            key=lambda segmentacao: segmentacao.nome_modelo,
        )
        return imagem

    def _avaliar_modelo(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        ground_truth_mask: np.ndarray,
        mask_modelo: np.ndarray,
        score_mask_modelo: np.ndarray,
        estrategia_binarizacao: str,
        segmentacao: Segmentacao | None = None,
    ) -> Segmentacao:
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

        registro = segmentacao or Segmentacao(
            nome_arquivo=nome_arquivo,
            nome_modelo=nome_modelo,
        )
        registro.area = float(area)
        registro.perimetro = float(perimetro)
        registro.iou = float(iou)
        self._atualizar_binarizacao(
            registro=registro,
            estrategia_binarizacao=estrategia_binarizacao,
            auprc=float(auprc),
        )
        return registro

    @staticmethod
    def _atualizar_binarizacao(
        registro: Segmentacao,
        estrategia_binarizacao: str,
        auprc: float,
    ) -> None:
        binarizacoes = {
            binarizacao.estrategia_binarizacao: binarizacao
            for binarizacao in registro.binarizacoes
        }
        binarizacao = binarizacoes.get(estrategia_binarizacao)
        if binarizacao is None:
            binarizacao = Binarizacao(
                nome_arquivo=registro.nome_arquivo,
                nome_modelo=registro.nome_modelo,
                estrategia_binarizacao=estrategia_binarizacao,
                metrica_x=auprc,
                metrica_y=Binarizacao.METRICA_NAO_CALCULADA,
            )
            registro.binarizacoes.append(binarizacao)
            return

        binarizacao.auprc = auprc
        binarizacao.metrica_y = Binarizacao.METRICA_NAO_CALCULADA
