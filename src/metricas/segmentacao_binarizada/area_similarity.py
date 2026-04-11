import math

from src.metricas.metrica_base import Metrica


class AreaSimilarity(Metrica):
    def __init__(
        self,
        nome_arquivo: str,
        area_modelo: float,
        area_ground_truth: float,
        modelo: str | None = None,
    ) -> None:
        super().__init__(nome="area_similarity", nome_arquivo=nome_arquivo, modelo=modelo)
        self._area_modelo = float(area_modelo)
        self._area_ground_truth = float(area_ground_truth)

    def calcular(self) -> float:
        """
        Calcula uma similaridade de area no intervalo [0, 1].

        A formula e baseada no erro relativo em relacao ao ground truth:
        similarity = max(0, 1 - |area_modelo - area_gt| / area_gt)
        """
        if math.isclose(self._area_ground_truth, 0.0):
            return 1.0 if math.isclose(self._area_modelo, 0.0) else 0.0

        relative_error = abs(self._area_modelo - self._area_ground_truth) / abs(
            self._area_ground_truth
        )
        return float(max(0.0, 1.0 - relative_error))
