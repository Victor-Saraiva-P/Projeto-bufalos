"""
Sistema de ranking ponderado para modelos de segmentação.

Este módulo calcula scores finais para cada modelo baseado em múltiplas
métricas com pesos configuráveis.
"""

import pandas as pd
import numpy as np
from typing import Optional

from src.config import RANKING_WEIGHTS


class ModelRanker:
    """
    Calcula ranking de modelos usando média ponderada de métricas normalizadas.

    Esta classe:
    - Normaliza todas as métricas para escala 0-1
    - Aplica pesos configuráveis a cada métrica
    - Calcula score final por modelo
    - Gera ranking ordenado

    Attributes:
        metrics_df: DataFrame com métricas de todos os modelos
        weights: Dicionário com pesos de cada métrica
        ranking_df: DataFrame com ranking final (após calculate_ranking)
    """

    def __init__(self, metrics_df: pd.DataFrame, weights: Optional[dict] = None):
        """
        Inicializa o ranker de modelos.

        Args:
            metrics_df: DataFrame com métricas (output do MetricsCollector)
            weights: Dicionário com pesos customizados. Se None, usa RANKING_WEIGHTS do config
        """
        self.metrics_df = metrics_df.copy()
        self.weights = weights if weights is not None else RANKING_WEIGHTS
        self.ranking_df: Optional[pd.DataFrame] = None

        # Validar pesos
        self._validate_weights()

    def _validate_weights(self) -> None:
        """
        Valida configuração de pesos.

        Raises:
            ValueError: Se pesos não somam ~1.0 ou contêm métricas inválidas
        """
        expected_metrics = {"iou", "area_similarity", "perimetro_similarity"}
        provided_metrics = set(self.weights.keys())

        if expected_metrics != provided_metrics:
            raise ValueError(
                f"Pesos devem conter exatamente: {expected_metrics}. "
                f"Recebido: {provided_metrics}"
            )

        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=1e-6):
            raise ValueError(f"Pesos devem somar 1.0. Soma atual: {total_weight:.6f}")

    def calculate_ranking(self) -> pd.DataFrame:
        """
        Calcula ranking final dos modelos.

        Processo:
        1. Agrupa métricas por modelo (média)
        2. Normaliza cada métrica para 0-1
        3. Aplica pesos e calcula score final
        4. Ordena por score decrescente

        Returns:
            DataFrame com colunas:
                - modelo: nome do modelo
                - iou_mean: média do IoU
                - area_similarity_mean: média da similaridade de área
                - perimetro_similarity_mean: média da similaridade de perímetro
                - iou_norm: IoU normalizado (0-1)
                - area_similarity_norm: similaridade de área normalizada (0-1)
                - perimetro_similarity_norm: similaridade de perímetro normalizada (0-1)
                - score: score final ponderado (0-1, maior = melhor)
                - rank: posição no ranking (1 = melhor)
        """
        # 1. Calcular médias por modelo
        avg_metrics = (
            self.metrics_df.groupby("modelo")[
                ["iou", "area_similarity", "perimetro_similarity"]
            ]
            .mean()
            .reset_index()
        )

        # Renomear colunas para clareza
        avg_metrics.columns = [
            "modelo",
            "iou_mean",
            "area_similarity_mean",
            "perimetro_similarity_mean",
        ]

        # 2. Normalizar métricas
        normalized = self._normalize_metrics(avg_metrics)

        # 3. Calcular score final
        normalized["score"] = (
            (normalized["iou_norm"] * self.weights["iou"])
            + (normalized["area_similarity_norm"] * self.weights["area_similarity"])
            + (
                normalized["perimetro_similarity_norm"]
                * self.weights["perimetro_similarity"]
            )
        )

        # 4. Ordenar e adicionar ranking
        normalized = normalized.sort_values("score", ascending=False).reset_index(
            drop=True
        )
        normalized["rank"] = range(1, len(normalized) + 1)

        # Reordenar colunas
        column_order = [
            "rank",
            "modelo",
            "score",
            "iou_mean",
            "area_similarity_mean",
            "perimetro_similarity_mean",
            "iou_norm",
            "area_similarity_norm",
            "perimetro_similarity_norm",
        ]
        normalized = normalized[column_order]

        self.ranking_df = normalized
        return self.ranking_df

    def _normalize_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza métricas para escala 0-1.

        Regras:
        - IoU: já está em 0-1, usar direto (maior = melhor)
        - area_similarity: já está em 0-1, usar direto (maior = melhor)
        - perimetro_similarity: já está em 0-1, usar direto (maior = melhor)

        Args:
            df: DataFrame com médias das métricas

        Returns:
            DataFrame com colunas normalizadas adicionadas
        """
        df = df.copy()

        # IoU: já está normalizado (0-1), maior = melhor
        df["iou_norm"] = df["iou_mean"]

        # Similaridade de área: já está em 0-1, maior = melhor
        df["area_similarity_norm"] = df["area_similarity_mean"]

        # Similaridade de perímetro: já está em 0-1, maior = melhor
        df["perimetro_similarity_norm"] = df["perimetro_similarity_mean"]

        return df

    @staticmethod
    def _normalize_inverse(series: pd.Series) -> pd.Series:
        """
        Normaliza série usando min-max scaling invertido.

        Valores menores → scores maiores (mais próximos de 1.0)
        Valores maiores → scores menores (mais próximos de 0.0)

        Args:
            series: Série a ser normalizada

        Returns:
            Série normalizada (0-1, invertida)
        """
        min_val = series.min()
        max_val = series.max()

        # Se todos os valores são iguais, retornar 1.0 (perfeito)
        if max_val == min_val:
            return pd.Series([1.0] * len(series), index=series.index)

        # Min-max scaling invertido
        normalized = 1 - ((series - min_val) / (max_val - min_val))

        return normalized

    def get_top_models(self, n: int = 5) -> pd.DataFrame:
        """
        Retorna top N modelos do ranking.

        Args:
            n: Número de modelos a retornar

        Returns:
            DataFrame com top N modelos

        Raises:
            ValueError: Se calculate_ranking() ainda não foi chamado
        """
        if self.ranking_df is None:
            raise ValueError(
                "Ranking ainda não calculado. Execute calculate_ranking() primeiro."
            )

        return self.ranking_df.head(n)

    def get_model_statistics(self) -> pd.DataFrame:
        """
        Retorna estatísticas completas por modelo.

        Returns:
            DataFrame com count, mean, std, min, max por modelo para cada métrica

        Raises:
            ValueError: Se metrics_df está vazio
        """
        if self.metrics_df.empty:
            raise ValueError("DataFrame de métricas está vazio.")

        stats = self.metrics_df.groupby("modelo")[
            ["iou", "area_similarity", "perimetro_similarity"]
        ].agg(["count", "mean", "std", "min", "max"])

        return stats
