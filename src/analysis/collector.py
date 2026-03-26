"""
Coletor de métricas de segmentação para avaliação de modelos.

Este módulo processa todas as imagens e modelos, calculando métricas
e persistindo resultados no SQLite do projeto.
"""

import pandas as pd
from typing import Optional
from tqdm.auto import tqdm

from src.io.indice_loader import carregar_indice
from src.io.sqlite.repositories import AvaliacaoSQLiteRepository
from src.models.avaliacao import Avaliacao


class MetricsCollector:
    """
    Coleta e processa métricas de segmentação para todos os modelos.

    Esta classe:
    - Itera sobre todas as imagens do índice persistido no SQLite
    - Para cada imagem, calcula métricas de cada modelo vs ground truth
    - Persiste resultados por imagem no SQLite
    - Materializa um DataFrame analítico a partir do banco

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
        self.repository = AvaliacaoSQLiteRepository()

    def collect_all_metrics(self) -> pd.DataFrame:
        """
        Coleta métricas de todas as imagens e modelos.

        Tenta carregar do SQLite primeiro. Se não houver resultados ou
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
                - area_similarity: 1 - (|area - area_gt| / area_gt)
                - perimetro_diff_abs: |perimetro - perimetro_gt|
                - perimetro_similarity: 1 - (|perimetro - perimetro_gt| / perimetro_gt)
        """
        if not self.force_recalculate:
            sqlite_df = self.repository.carregar_metricas_dataframe()
            if not sqlite_df.empty:
                print("✓ Métricas carregadas do SQLite")
                self.df = sqlite_df
                return self.df

        # Processar todas as imagens
        print("Coletando métricas de todas as imagens...")
        indice = carregar_indice()
        modelos_com_erro = set()

        for linha in tqdm(indice, desc="Processando imagens"):
            try:
                self._calculate_metrics_for_image(linha.nome_arquivo, modelos_com_erro)
            except Exception as e:
                print(f"\n⚠ Erro ao processar {linha.nome_arquivo}: {e}")
                continue

        self.df = self.repository.carregar_metricas_dataframe()

        if self.df.empty:
            raise ValueError("Nenhuma métrica foi coletada. Verifique as segmentações.")

        # Mostrar resumo de modelos com problemas
        if modelos_com_erro:
            print(f"\n⚠ Modelos sem segmentações encontradas:")
            for modelo in sorted(modelos_com_erro):
                print(f"  - {modelo}")

        print(f"\n✓ Métricas coletadas: {len(self.df)} registros")
        print(f"  - Imagens processadas: {self.df['nome_arquivo'].nunique()}")
        print(f"  - Modelos com dados: {self.df['modelo'].nunique()}")

        return self.df

    def _calculate_metrics_for_image(self, nome_arquivo: str, modelos_com_erro: set) -> None:
        """
        Calcula métricas para uma imagem específica.

        Args:
            nome_arquivo: Nome do arquivo da imagem
            modelos_com_erro: Set para acumular modelos com problemas

        """
        avaliacao = Avaliacao(nome_arquivo)
        avaliacao.calcular_metricas()
        avaliacao.salvar()

        for modelo, modelo_avaliado in avaliacao.modelos.items():
            area = modelo_avaliado.area
            perimetro = modelo_avaliado.perimetro
            iou = modelo_avaliado.iou

            if area is None or perimetro is None or iou is None:
                modelos_com_erro.add(modelo)
