"""
Coletor de métricas de segmentação para avaliação de modelos.

Este módulo processa todas as imagens e modelos, calculando métricas
e persistindo resultados no SQLite do projeto.
"""

from typing import Optional

import pandas as pd
from tqdm.auto import tqdm

from src.controllers.avaliacao_controller import AvaliacaoController
from src.models import Imagem
from src.repositories import ImagemRepository


class MetricsCollector:
    """
    Coleta e processa métricas de segmentação para todos os modelos.

    Esta classe:
    - Itera sobre todas as imagens do índice persistido no SQLite
    - Para cada imagem, calcula métricas de cada segmentacao vs ground truth
    - Persiste resultados por imagem no SQLite
    - Materializa um DataFrame analítico a partir das entidades persistidas
    """

    def __init__(self, force_recalculate: bool = False):
        self.force_recalculate = force_recalculate
        self.df: Optional[pd.DataFrame] = None
        self.imagem_repository = ImagemRepository()
        self.avaliacao_controller = AvaliacaoController(
            imagem_repository=self.imagem_repository
        )

    def collect_all_metrics(self) -> pd.DataFrame:
        if not self.force_recalculate:
            sqlite_df = self._build_metrics_dataframe(self.imagem_repository.list())
            if not sqlite_df.empty:
                print("✓ Métricas carregadas do SQLite")
                self.df = sqlite_df
                return self.df

        print("Coletando métricas de todas as imagens...")
        indice = self.imagem_repository.list()
        modelos_com_erro = set()

        for imagem in tqdm(indice, desc="Processando imagens"):
            try:
                self._calculate_metrics_for_image(imagem, modelos_com_erro)
            except Exception as e:
                print(f"\n⚠ Erro ao processar {imagem.nome_arquivo}: {e}")
                continue

        self.df = self._build_metrics_dataframe(self.imagem_repository.list())

        if self.df.empty:
            raise ValueError("Nenhuma métrica foi coletada. Verifique as segmentações.")

        if modelos_com_erro:
            print(f"\n⚠ Modelos sem segmentações encontradas:")
            for modelo in sorted(modelos_com_erro):
                print(f"  - {modelo}")

        print(f"\n✓ Métricas coletadas: {len(self.df)} registros")
        print(f"  - Imagens processadas: {self.df['nome_arquivo'].nunique()}")
        print(f"  - Modelos com dados: {self.df['modelo'].nunique()}")

        return self.df

    def _calculate_metrics_for_image(self, imagem: Imagem, modelos_com_erro: set) -> None:
        imagem_avaliada = self.avaliacao_controller.processar_imagem(imagem)

        for segmentacao in imagem_avaliada.segmentacoes:
            if (
                segmentacao.area is None
                or segmentacao.perimetro is None
                or segmentacao.iou is None
            ):
                modelos_com_erro.add(segmentacao.nome_modelo)

    @staticmethod
    def _build_metrics_dataframe(imagens: list[Imagem]) -> pd.DataFrame:
        registros: list[dict[str, float | str]] = []

        for imagem in imagens:
            ground_truth = imagem.ground_truth_binarizada
            if ground_truth is None:
                continue

            area_gt = ground_truth.area
            perimetro_gt = ground_truth.perimetro
            if area_gt is None or perimetro_gt is None:
                continue

            for segmentacao in imagem.segmentacoes:
                area = segmentacao.area
                perimetro = segmentacao.perimetro
                iou = segmentacao.iou

                if area is None or perimetro is None or iou is None:
                    continue

                area_diff_abs = abs(area - area_gt)
                perimetro_diff_abs = abs(perimetro - perimetro_gt)
                area_similarity = 1.0 - (area_diff_abs / area_gt) if area_gt > 0 else 0.0
                perimetro_similarity = (
                    1.0 - (perimetro_diff_abs / perimetro_gt)
                    if perimetro_gt > 0
                    else 0.0
                )

                registros.append(
                    {
                        "nome_arquivo": imagem.nome_arquivo,
                        "modelo": segmentacao.nome_modelo,
                        "area": area,
                        "perimetro": perimetro,
                        "iou": iou,
                        "area_gt": area_gt,
                        "perimetro_gt": perimetro_gt,
                        "area_diff_abs": area_diff_abs,
                        "area_similarity": max(0.0, area_similarity),
                        "perimetro_diff_abs": perimetro_diff_abs,
                        "perimetro_similarity": max(0.0, perimetro_similarity),
                    }
                )

        return pd.DataFrame(registros)
