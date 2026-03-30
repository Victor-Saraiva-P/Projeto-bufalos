from __future__ import annotations

import os

from PIL import Image

from src.binarizacao.estrategias import BinarizationStrategy
from src.models import Binarizacao, GroundTruthBinarizada, Imagem


class BinarizacaoService:
    def processar_arquivo(
        self,
        caminho_entrada: str,
        caminho_saida: str,
        strategy: BinarizationStrategy,
    ) -> str:
        if not os.path.isfile(caminho_entrada):
            print(f"ERRO: Mascara nao encontrada: {caminho_entrada}")
            return "erro"

        if os.path.isfile(caminho_saida):
            return "skip"

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

        try:
            with Image.open(caminho_entrada) as image:
                image_binarizada = strategy.binarizar(image)
                image_binarizada.save(caminho_saida, format="PNG")
        except Exception as erro:
            print(f"ERRO ao processar {caminho_entrada}: {erro}")
            return "erro"

        return "ok"

    def garantir_ground_truth_binarizada(self, imagem: Imagem) -> GroundTruthBinarizada:
        if imagem.ground_truth_binarizada is None:
            imagem.ground_truth_binarizada = GroundTruthBinarizada(
                nome_arquivo=imagem.nome_arquivo,
                area=None,
                perimetro=None,
            )
        return imagem.ground_truth_binarizada

    def garantir_binarizacao(
        self,
        imagem: Imagem,
        nome_modelo: str,
        strategy: BinarizationStrategy,
    ) -> Binarizacao:
        segmentacao = self._garantir_segmentacao(imagem, nome_modelo)
        estrategia_binarizacao = type(strategy).__name__

        for binarizacao in segmentacao.binarizacoes:
            if binarizacao.estrategia_binarizacao == estrategia_binarizacao:
                return binarizacao

        binarizacao = Binarizacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo=nome_modelo,
            estrategia_binarizacao=estrategia_binarizacao,
            metrica_x=None,
            metrica_y=None,
        )
        segmentacao.binarizacoes.append(binarizacao)
        return binarizacao

    @staticmethod
    def _garantir_segmentacao(imagem: Imagem, nome_modelo: str):
        for segmentacao in imagem.segmentacoes:
            if segmentacao.nome_modelo == nome_modelo:
                return segmentacao

        from src.models import Segmentacao

        segmentacao = Segmentacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo=nome_modelo,
        )
        imagem.segmentacoes.append(segmentacao)
        return segmentacao
