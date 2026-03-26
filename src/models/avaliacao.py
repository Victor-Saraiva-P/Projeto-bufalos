from dataclasses import dataclass

import numpy as np

from src.avaliacao.metricas import Area, IoU, Perimetro
from src.config import MODELOS_PARA_AVALIACAO
from src.io.mask_utils import carregar_mask_array_avaliacao
from src.io.sqlite.repositories import AvaliacaoSQLiteRepository


@dataclass
class GroundTruthAvaliado:
    nome_arquivo: str
    mask_array: np.ndarray
    area: int | float | None = None
    perimetro: float | None = None


@dataclass
class ModeloAvaliado:
    nome_arquivo: str
    modelo: str
    mask_array: np.ndarray
    area: int | float | None = None
    perimetro: float | None = None
    iou: float | None = None


class Avaliacao:
    nome_arquivo: str
    ground_truth: GroundTruthAvaliado
    modelos: dict[str, ModeloAvaliado]

    def __init__(self, nome_arquivo: str):
        self.nome_arquivo = nome_arquivo
        self.ground_truth = GroundTruthAvaliado(
            nome_arquivo=nome_arquivo,
            mask_array=carregar_mask_array_avaliacao(nome_arquivo, "ground_truth"),
        )
        self.modelos = {
            modelo: ModeloAvaliado(
                nome_arquivo=nome_arquivo,
                modelo=modelo,
                mask_array=carregar_mask_array_avaliacao(nome_arquivo, modelo),
            )
            for modelo in MODELOS_PARA_AVALIACAO
        }

    def calcular_metricas(self) -> None:
        self._calcular_areas()
        self._calcular_perimetros()
        self._calcular_ious()

    def _calcular_areas(self) -> None:
        self.ground_truth.area = Area(
            nome_arquivo=self.nome_arquivo,
            mask_array=self.ground_truth.mask_array,
            modelo="ground_truth",
        ).calcular()

        for modelo_avaliado in self.modelos.values():
            modelo_avaliado.area = Area(
                nome_arquivo=self.nome_arquivo,
                mask_array=modelo_avaliado.mask_array,
                modelo=modelo_avaliado.modelo,
            ).calcular()

    def _calcular_perimetros(self) -> None:
        self.ground_truth.perimetro = Perimetro(
            nome_arquivo=self.nome_arquivo,
            mask_array=self.ground_truth.mask_array,
            modelo="ground_truth",
        ).calcular()

        for modelo_avaliado in self.modelos.values():
            modelo_avaliado.perimetro = Perimetro(
                nome_arquivo=self.nome_arquivo,
                mask_array=modelo_avaliado.mask_array,
                modelo=modelo_avaliado.modelo,
            ).calcular()

    def _calcular_ious(self) -> None:
        for modelo_avaliado in self.modelos.values():
            modelo_avaliado.iou = IoU(
                nome_arquivo=self.nome_arquivo,
                mask_modelo=modelo_avaliado.mask_array,
                mask_ground_truth=self.ground_truth.mask_array,
                modelo=modelo_avaliado.modelo,
            ).calcular()

    def salvar(self) -> None:
        repository = AvaliacaoSQLiteRepository()
        repository.salvar_avaliacao(self)
