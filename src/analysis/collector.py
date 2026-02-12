"""
Coletor de métricas de segmentação para avaliação de modelos.

Este módulo processa todas as imagens e modelos, calculando métricas
e armazenando resultados em cache para análises posteriores.
"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Optional
from tqdm.auto import tqdm

from src.config import (
    MODELOS_PARA_AVALIACAO,
    EVALUATION_DIR,
    METRICS_CACHE_PATH,
)
from src.models.avaliacao import Avaliacao
from src.io.indice_loader import carregar_indice_excel


class MetricsCollector:
    """
    Coleta e processa métricas de segmentação para todos os modelos.

    Esta classe:
    - Itera sobre todas as imagens do índice
    - Para cada imagem, calcula métricas de cada modelo vs ground truth
    - Armazena resultados em DataFrame com cache em CSV
    - Calcula diferenças absolutas e relativas para área e perímetro

    Attributes:
        force_recalculate: Se True, ignora cache e recalcula tudo
        df: DataFrame com todas as métricas coletadas
    """

    def __init__(self, force_recalculate: bool = False):
        """
        Inicializa o coletor de métricas.

        Args:
            force_recalculate: Se True, recalcula todas as métricas mesmo com cache válido
        """
        self.force_recalculate = force_recalculate
        self.df: Optional[pd.DataFrame] = None

    def collect_all_metrics(self) -> pd.DataFrame:
        """
        Coleta métricas de todas as imagens e modelos.

        Tenta carregar do cache primeiro. Se não houver cache válido ou
        force_recalculate=True, processa todas as imagens.

        Returns:
            DataFrame com colunas:
                - nome_arquivo: nome da imagem
                - modelo: nome do modelo
                - area: área da segmentação (pixels)
                - perimetro: perímetro da segmentação
                - iou: Intersection over Union vs GT
                - area_gt: área do ground truth
                - perimetro_gt: perímetro do ground truth
                - area_diff_abs: |area - area_gt|
                - area_diff_rel: |area - area_gt| / area_gt
                - perimetro_diff_abs: |perimetro - perimetro_gt|
                - perimetro_diff_rel: |perimetro - perimetro_gt| / perimetro_gt
        """
        # Tentar carregar do cache
        if not self.force_recalculate:
            cached_df = self._load_cache()
            if cached_df is not None:
                print(f"✓ Métricas carregadas do cache: {METRICS_CACHE_PATH}")
                self.df = cached_df
                return self.df

        # Processar todas as imagens
        print("Coletando métricas de todas as imagens...")
        indice_excel = carregar_indice_excel()

        all_metrics = []
        modelos_com_erro = set()

        for linha in tqdm(indice_excel, desc="Processando imagens"):
            try:
                metrics = self._calculate_metrics_for_image(
                    linha.nome_arquivo, modelos_com_erro
                )
                all_metrics.extend(metrics)
            except Exception as e:
                print(f"\n⚠ Erro ao processar {linha.nome_arquivo}: {e}")
                continue

        if not all_metrics:
            raise ValueError("Nenhuma métrica foi coletada. Verifique as segmentações.")

        # Criar DataFrame
        self.df = pd.DataFrame(all_metrics)

        # Mostrar resumo de modelos com problemas
        if modelos_com_erro:
            print(f"\n⚠ Modelos sem segmentações encontradas:")
            for modelo in sorted(modelos_com_erro):
                print(f"  - {modelo}")

        # Salvar cache
        self._save_cache(self.df)

        print(f"\n✓ Métricas coletadas: {len(self.df)} registros")
        print(f"  - Imagens processadas: {self.df['nome_arquivo'].nunique()}")
        print(f"  - Modelos com dados: {self.df['modelo'].nunique()}")

        return self.df

    def _calculate_metrics_for_image(
        self, nome_arquivo: str, modelos_com_erro: set
    ) -> List[dict]:
        """
        Calcula métricas para uma imagem específica.

        Args:
            nome_arquivo: Nome do arquivo da imagem
            modelos_com_erro: Set para acumular modelos com problemas

        Returns:
            Lista de dicionários com métricas de cada modelo
        """
        # Criar avaliação e calcular métricas
        avaliacao = Avaliacao(nome_arquivo)
        avaliacao.calcular_metricas()

        # Extrair métricas do ground truth
        gt_area = avaliacao.ground_truth.area
        gt_perimetro = avaliacao.ground_truth.perimetro

        metrics_list = []

        # Processar cada modelo
        for segmentacao in avaliacao.segmentacoes:
            # Verificar se modelo tem dados válidos (métricas calculadas)
            if (
                segmentacao.area is None
                or segmentacao.perimetro is None
                or segmentacao.iou is None
            ):
                modelos_com_erro.add(segmentacao.modelo)
                continue

            # Garantir que gt também tem métricas válidas
            assert gt_area is not None, f"GT área None para {nome_arquivo}"
            assert gt_perimetro is not None, f"GT perímetro None para {nome_arquivo}"

            # Após as verificações acima, sabemos que os valores não são None
            # type: ignore é necessário pois o LSP não reconhece o narrowing
            area_diff_abs = abs(segmentacao.area - gt_area)  # type: ignore
            perimetro_diff_abs = abs(segmentacao.perimetro - gt_perimetro)  # type: ignore

            # Calcular diferenças relativas (percentuais)
            # Evitar divisão por zero
            area_diff_rel = area_diff_abs / gt_area if gt_area > 0 else 0.0  # type: ignore
            perimetro_diff_rel = (
                perimetro_diff_abs / gt_perimetro if gt_perimetro > 0 else 0.0  # type: ignore
            )

            metrics_list.append(
                {
                    "nome_arquivo": nome_arquivo,
                    "modelo": segmentacao.modelo,
                    "area": segmentacao.area,
                    "perimetro": segmentacao.perimetro,
                    "iou": segmentacao.iou,
                    "area_gt": gt_area,
                    "perimetro_gt": gt_perimetro,
                    "area_diff_abs": area_diff_abs,
                    "area_diff_rel": area_diff_rel,
                    "perimetro_diff_abs": perimetro_diff_abs,
                    "perimetro_diff_rel": perimetro_diff_rel,
                }
            )

        return metrics_list

    def _save_cache(self, df: pd.DataFrame) -> None:
        """
        Salva DataFrame em arquivo CSV de cache.

        Args:
            df: DataFrame a ser salvo
        """
        # Criar diretório se não existir
        os.makedirs(EVALUATION_DIR, exist_ok=True)

        # Salvar CSV
        df.to_csv(METRICS_CACHE_PATH, index=False)
        print(f"✓ Cache salvo em: {METRICS_CACHE_PATH}")

    def _load_cache(self) -> Optional[pd.DataFrame]:
        """
        Carrega DataFrame do arquivo de cache.

        Returns:
            DataFrame se cache existe e é válido, None caso contrário
        """
        cache_path = Path(METRICS_CACHE_PATH)

        if not cache_path.exists():
            print("Cache não encontrado. Processando todas as imagens...")
            return None

        try:
            df = pd.read_csv(METRICS_CACHE_PATH)

            # Validar colunas esperadas
            expected_cols = {
                "nome_arquivo",
                "modelo",
                "area",
                "perimetro",
                "iou",
                "area_gt",
                "perimetro_gt",
                "area_diff_abs",
                "area_diff_rel",
                "perimetro_diff_abs",
                "perimetro_diff_rel",
            }

            if not expected_cols.issubset(df.columns):
                print("Cache inválido (colunas incorretas). Recalculando...")
                return None

            return df

        except Exception as e:
            print(f"Erro ao carregar cache: {e}. Recalculando...")
            return None
