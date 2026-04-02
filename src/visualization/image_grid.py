"""
Funções para visualização simplificada de imagens com segmentações.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from typing import Tuple
from matplotlib.figure import Figure

from src.io.path_resolver import PathResolver


_PATH_RESOLVER = PathResolver.from_config()


def plot_image_grid(
    df_subset: pd.DataFrame,
    df_all: pd.DataFrame,
    title: str,
    metric_name: str,
    max_images: int = 5,
) -> Figure:
    """
    Cria grid simplificado mostrando TODOS os modelos para cada imagem.

    Layout por linha:
    - Imagem Original | Ground Truth | Modelo1 | Modelo2 | ... | ModeloN

    Args:
        df_subset: DataFrame com top/bottom resultados (define quais imagens mostrar)
        df_all: DataFrame completo com TODAS as métricas
        title: Título do plot
        metric_name: Nome da métrica principal (iou, area_similarity, etc)
        max_images: Máximo de imagens a mostrar

    Returns:
        Figura matplotlib
    """
    # Pegar apenas as imagens únicas do subset (sem repetir)
    unique_images = df_subset["nome_arquivo"].unique()[:max_images]

    if len(unique_images) == 0:
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.text(0.5, 0.5, "Nenhum dado para exibir", ha="center", va="center")
        ax.axis("off")
        return fig

    # Pegar todos os modelos disponíveis
    all_models = sorted(df_all["modelo"].unique())
    n_models = len(all_models)

    # Colunas: Original + GT + todos os modelos
    n_cols = 2 + n_models
    n_rows = len(unique_images)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 2.5, n_rows * 2.5))
    fig.suptitle(title, fontsize=14, fontweight="bold")

    # Garantir que axes é 2D
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for row_idx, nome_arquivo in enumerate(unique_images):
        # Coluna 0: Imagem Original
        try:
            img_path = _PATH_RESOLVER.caminho_foto_original(nome_arquivo)
            img = Image.open(img_path)
            axes[row_idx, 0].imshow(img)
            axes[row_idx, 0].set_title(f"Original\n{nome_arquivo[:15]}...", fontsize=8)
        except Exception as e:
            axes[row_idx, 0].text(
                0.5, 0.5, "Erro", ha="center", va="center", fontsize=8
            )
            axes[row_idx, 0].set_title("Original (erro)", fontsize=8)
        axes[row_idx, 0].axis("off")

        # Coluna 1: Ground Truth
        try:
            gt_path = _PATH_RESOLVER.caminho_ground_truth_binarizada(nome_arquivo)
            gt_img = Image.open(gt_path).convert("L")
            axes[row_idx, 1].imshow(gt_img, cmap="gray")
            axes[row_idx, 1].set_title("GT", fontsize=8)
        except Exception as e:
            axes[row_idx, 1].text(
                0.5, 0.5, "Erro", ha="center", va="center", fontsize=8
            )
            axes[row_idx, 1].set_title("GT (erro)", fontsize=8)
        axes[row_idx, 1].axis("off")

        # Colunas 2+: Todos os modelos
        for model_idx, modelo in enumerate(all_models):
            col_idx = 2 + model_idx

            # Buscar métrica deste modelo para esta imagem
            model_data = df_all[
                (df_all["nome_arquivo"] == nome_arquivo) & (df_all["modelo"] == modelo)
            ]

            try:
                if model_data.empty:
                    axes[row_idx, col_idx].set_title(f"{modelo}\nN/A", fontsize=7)
                    axes[row_idx, col_idx].axis("off")
                    continue

                nome_binarizacao = (
                    str(model_data.iloc[0]["estrategia_binarizacao"])
                    if "estrategia_binarizacao" in model_data.columns
                    else ""
                )
                execucao = (
                    int(model_data.iloc[0]["execucao"])
                    if "execucao" in model_data.columns
                    else 1
                )
                seg_path = _PATH_RESOLVER.caminho_segmentacao_binarizada(
                    modelo,
                    nome_arquivo,
                    execucao=execucao,
                    nome_binarizacao=nome_binarizacao,
                )
                seg_img = Image.open(seg_path).convert("L")
                axes[row_idx, col_idx].imshow(seg_img, cmap="gray")

                row_data = model_data.iloc[0]

                # Função auxiliar para formatar métricas
                def format_metric(name, value):
                    if name == "iou":
                        return f"IoU: {value:.3f}"
                    elif name == "auprc":
                        return f"AUPRC: {value:.3f}"
                    elif name == "area_similarity":
                        return f"Área: {value * 100:.1f}%"
                    elif name == "perimetro_similarity":
                        return f"Per: {value * 100:.1f}%"
                    return f"{value:.2f}"

                # Montar string com métrica principal primeiro
                metrics_order = [metric_name]
                for m in ["iou", "auprc", "area_similarity", "perimetro_similarity"]:
                    if m != metric_name and m in row_data.index:
                        metrics_order.append(m)

                metric_lines = [
                    format_metric(m, row_data[m]) for m in metrics_order
                ]
                metric_str = "\n".join(metric_lines)

                axes[row_idx, col_idx].set_title(
                    f"{modelo}\n{metric_str}", fontsize=6
                )

            except Exception as e:
                axes[row_idx, col_idx].text(
                    0.5, 0.5, "Erro", ha="center", va="center", fontsize=7
                )
                axes[row_idx, col_idx].set_title(f"{modelo}\n(erro)", fontsize=7)
            axes[row_idx, col_idx].axis("off")

    plt.tight_layout()
    return fig


def plot_single_image_comparison(
    nome_arquivo: str,
    df_metrics: pd.DataFrame,
) -> Figure:
    """
    Compara todos os modelos para uma única imagem.

    Args:
        nome_arquivo: Nome da imagem
        df_metrics: DataFrame completo de métricas

    Returns:
        Figura matplotlib
    """
    # Filtrar dados desta imagem
    img_data = df_metrics[df_metrics["nome_arquivo"] == nome_arquivo].copy()

    if img_data.empty:
        raise ValueError(f"Imagem {nome_arquivo} não encontrada")

    # Ordenar por IoU decrescente
    img_data = img_data.sort_values(by="iou", ascending=False)

    n_modelos = len(img_data)

    # Layout: 2 linhas
    # Linha 1: Original + GT
    # Linha 2+: Cada modelo
    n_rows = 2 + ((n_modelos - 1) // 3)  # 3 modelos por linha
    n_cols = 3

    fig = plt.figure(figsize=(12, n_rows * 3))
    gs = fig.add_gridspec(n_rows, n_cols, hspace=0.3, wspace=0.3)

    fig.suptitle(
        f"Comparação de Modelos - {nome_arquivo}", fontsize=14, fontweight="bold"
    )

    # Original (canto superior esquerdo)
    ax_orig = fig.add_subplot(gs[0, 0])
    try:
        img_path = _PATH_RESOLVER.caminho_foto_original(nome_arquivo)
        img = Image.open(img_path)
        ax_orig.imshow(img)
        ax_orig.set_title("Original", fontsize=10)
    except:
        ax_orig.text(0.5, 0.5, "Erro", ha="center", va="center")
        ax_orig.set_title("Original (erro)", fontsize=10)
    ax_orig.axis("off")

    # Ground Truth (centro superior)
    ax_gt = fig.add_subplot(gs[0, 1])
    try:
        gt_path = _PATH_RESOLVER.caminho_ground_truth_binarizada(nome_arquivo)
        gt_img = Image.open(gt_path).convert("L")
        ax_gt.imshow(gt_img, cmap="gray")
        ax_gt.set_title("Ground Truth", fontsize=10)
    except:
        ax_gt.text(0.5, 0.5, "Erro GT", ha="center", va="center")
        ax_gt.set_title("GT (erro)", fontsize=10)
    ax_gt.axis("off")

    # Modelos (a partir da linha 1)
    for idx, (_, row) in enumerate(img_data.iterrows()):
        row_pos = 1 + (idx // n_cols)
        col_pos = idx % n_cols

        ax = fig.add_subplot(gs[row_pos, col_pos])

        try:
            nome_binarizacao = (
                str(row["estrategia_binarizacao"])
                if "estrategia_binarizacao" in row.index
                else None
            )
            execucao = int(row["execucao"]) if "execucao" in row.index else 1
            seg_path = _PATH_RESOLVER.caminho_segmentacao_binarizada(
                str(row["modelo"]),
                nome_arquivo,
                execucao=execucao,
                nome_binarizacao=nome_binarizacao,
            )
            seg_img = Image.open(seg_path).convert("L")
            ax.imshow(seg_img, cmap="gray")
            ax.set_title(f"{row['modelo']}\\nIoU: {row['iou']:.4f}", fontsize=9)
        except:
            ax.text(0.5, 0.5, "Erro", ha="center", va="center")
            ax.set_title(f"{row['modelo']} (erro)", fontsize=9)
        ax.axis("off")

    return fig
