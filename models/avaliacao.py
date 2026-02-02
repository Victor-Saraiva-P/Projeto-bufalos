import os.path

from models.mascara import Mascara


class Avaliacao:
    nome_arquivo: str
    ground_truth: Mascara
    segmetacoes: list[Mascara]

    def __init__(
            self,
            nome_arquivo: str,
            mascaras_type: str,
            ground_truth_dir: str,
            segmetacoes_dir: str,
            segmetacoes_modelos: list[str],
    ):
        self.nome_arquivo = nome_arquivo

        ground_truth_path = os.path.join(ground_truth_dir, f"{nome_arquivo}{mascaras_type}")
        self.ground_truth = Mascara("ground-of-truth", ground_truth_path)

        self.segmetacoes = [
            Mascara(modelo, os.path.join(segmetacoes_dir, modelo, f"{nome_arquivo}{mascaras_type}")) for modelo in
            segmetacoes_modelos
        ]
