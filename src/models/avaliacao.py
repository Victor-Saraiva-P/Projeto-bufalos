from src.config import MODELOS_PARA_AVALIACAO
from src.models.mascara import Mascara


class Avaliacao:
    nome_arquivo: str
    ground_truth: Mascara
    segmentacoes: list[Mascara]

    def __init__(
        self,
        nome_arquivo: str,
    ):
        self.nome_arquivo = nome_arquivo

        self.ground_truth = Mascara("ground-of-truth", nome_arquivo)

        self.segmentacoes = [
            Mascara(modelo, nome_arquivo) for modelo in MODELOS_PARA_AVALIACAO
        ]
