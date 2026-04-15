import math

from src.metricas.metrica_base import Metrica


class PerimetroSimilarity(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        perimetro_modelo: float,
        perimetro_ground_truth: float,
        modelo: str | None = None,
    ) -> None:
        super().__init__(
            nome="perimetro_similarity",
            nome_arquivo=nome_arquivo,
            modelo=modelo,
        )
        self._perimetro_modelo = float(perimetro_modelo)
        self._perimetro_ground_truth = float(perimetro_ground_truth)

    def calcular(self) -> float:
        """
        Calcula uma similaridade de perimetro no intervalo [0, 1].

        A formula e baseada no erro relativo em relacao ao ground truth:
        similarity = max(0, 1 - |perimetro_modelo - perimetro_gt| / perimetro_gt)
        """
        if math.isclose(self._perimetro_ground_truth, 0.0):
            return 1.0 if math.isclose(self._perimetro_modelo, 0.0) else 0.0

        relative_error = abs(
            self._perimetro_modelo - self._perimetro_ground_truth
        ) / abs(self._perimetro_ground_truth)
        return float(max(0.0, 1.0 - relative_error))
