from src.models.mascara import Mascara
from src.metrics.iou import IoU


class MascaraSegmentada(Mascara):
    ground_truth: Mascara
    iou: float | None

    def __init__(self, modelo: str, nome_arquivo: str, ground_truth: Mascara):
        super().__init__(modelo, nome_arquivo)
        self.ground_truth = ground_truth
        self.iou = None

    def calcular_metricas(self) -> None:
        # Calcular métricas básicas (área, perímetro)
        super().calcular_metricas()

        # Calcular IoU contra ground-truth
        self.iou = IoU.calcular(self.mask_array, self.ground_truth.mask_array)
