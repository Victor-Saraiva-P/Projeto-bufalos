from src.config import MODELOS_PARA_AVALIACAO
from src.models.mascara import Mascara
from src.models.mascara_segmentada import MascaraSegmentada


class Avaliacao:
    nome_arquivo: str
    ground_truth: Mascara
    segmentacoes: list[MascaraSegmentada]

    def __init__(self, nome_arquivo: str):
        self.nome_arquivo = nome_arquivo

        # Criar máscaras (SEM calcular métricas)
        self.ground_truth = Mascara("ground_truth", nome_arquivo)
        self.segmentacoes = [
            MascaraSegmentada(modelo, nome_arquivo, ground_truth=self.ground_truth)
            for modelo in MODELOS_PARA_AVALIACAO
        ]

    def calcular_metricas(self) -> None:
        # Calcular métricas do ground-truth
        self.ground_truth.calcular_metricas()

        # Calcular métricas das segmentações (área, perímetro, IoU)
        for seg in self.segmentacoes:
            seg.calcular_metricas()
