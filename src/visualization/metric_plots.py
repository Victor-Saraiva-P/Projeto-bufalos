"""
Funções SIMPLIFICADAS para visualização de métricas.

Foco em clareza e legibilidade.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
from matplotlib.figure import Figure


def setup_plot_style() -> None:
    """Configura estilo simples e limpo dos plots."""
    sns.set_style("whitegrid")
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 10


def plot_iou_analysis(df: pd.DataFrame, figsize: Tuple[int, int] = (10, 6)) -> Figure:
    """
    Análise SIMPLIFICADA de IoU.

    1 gráfico: Barplot com IoU médio por modelo (ordenado)
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle("Análise de IoU", fontsize=14, fontweight="bold")

    # Calcular médias
    means = df.groupby("modelo")["iou"].mean().sort_values(ascending=False)

    # Barplot horizontal
    means.plot(kind="barh", ax=ax, color="steelblue", edgecolor="black")
    ax.set_title("IoU Médio por Modelo", fontsize=12)
    ax.set_xlabel("IoU Médio", fontsize=11)
    ax.set_ylabel("")
    ax.set_xlim(0, 1.0)
    ax.grid(axis="x", alpha=0.3)

    # Adicionar valores
    for i, v in enumerate(means.values):
        ax.text(v + 0.02, i, f"{v:.3f}", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    return fig


def plot_area_analysis(df: pd.DataFrame, figsize: Tuple[int, int] = (10, 6)) -> Figure:
    """
    Análise SIMPLIFICADA de Área.

    1 gráfico: Barplot com diferença média por modelo (ordenado)
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle("Análise de Área (Diferença Relativa)", fontsize=14, fontweight="bold")

    # Calcular médias (ordenar por menor diferença = melhor)
    means = df.groupby("modelo")["area_diff_rel"].mean().sort_values()

    # Barplot horizontal
    (means * 100).plot(kind="barh", ax=ax, color="lightcoral", edgecolor="black")
    ax.set_title("Diferença Média de Área por Modelo", fontsize=12)
    ax.set_xlabel("Diferença Relativa (%)", fontsize=11)
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.3)

    # Adicionar valores
    for i, v in enumerate(means.values):
        ax.text(
            v * 100 + 1,
            i,
            f"{v * 100:.1f}%",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    return fig


def plot_perimetro_analysis(
    df: pd.DataFrame, figsize: Tuple[int, int] = (10, 6)
) -> Figure:
    """
    Análise SIMPLIFICADA de Perímetro.

    1 gráfico: Barplot com diferença média por modelo (ordenado)
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(
        "Análise de Perímetro (Diferença Relativa)", fontsize=14, fontweight="bold"
    )

    # Calcular médias (ordenar por menor diferença = melhor)
    means = df.groupby("modelo")["perimetro_diff_rel"].mean().sort_values()

    # Barplot horizontal
    (means * 100).plot(kind="barh", ax=ax, color="lightgreen", edgecolor="black")
    ax.set_title("Diferença Média de Perímetro por Modelo", fontsize=12)
    ax.set_xlabel("Diferença Relativa (%)", fontsize=11)
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.3)

    # Adicionar valores
    for i, v in enumerate(means.values):
        ax.text(
            v * 100 + 1,
            i,
            f"{v * 100:.1f}%",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    return fig


def plot_ranking_analysis(
    ranking_df: pd.DataFrame, figsize: Tuple[int, int] = (12, 6)
) -> Figure:
    """
    Visualização SIMPLIFICADA do ranking.

    1 gráfico grande: barplot com scores finais
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle("Ranking Final dos Modelos", fontsize=14, fontweight="bold")

    # Ordenar por score (menor rank = melhor)
    ranking_sorted = ranking_df.sort_values("score", ascending=False)

    # Barplot horizontal
    bars = ax.barh(
        ranking_sorted["modelo"],
        ranking_sorted["score"],
        color="steelblue",
        edgecolor="black",
    )

    # Destacar o melhor em verde
    bars[0].set_color("green")
    bars[0].set_alpha(0.7)

    ax.set_xlabel("Score Final (0-1, maior = melhor)", fontsize=11)
    ax.set_ylabel("")
    ax.set_xlim(0, 1.0)
    ax.set_title(
        "Score ponderado baseado em IoU, Área e Perímetro", fontsize=10, style="italic"
    )

    # Adicionar valores e ranks
    for i, (idx, row) in enumerate(ranking_sorted.iterrows()):
        score_text = f"#{int(row['rank'])} - {row['score']:.4f}"
        ax.text(
            row["score"] + 0.02,
            i,
            score_text,
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    # Grid para facilitar leitura
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig


def get_top_bottom_iou(
    df: pd.DataFrame, n: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna top N e bottom N por IoU.

    Para top N (melhores): inclui também o pior resultado para cada imagem
    Para bottom N (piores): inclui também o melhor resultado para cada imagem
    """
    sorted_df = df.sort_values("iou", ascending=False)

    # Top N - pegar melhores + pior de cada imagem
    top_results = sorted_df.head(n).copy()
    top_images = top_results["nome_arquivo"].unique()
    for img in top_images:
        worst_for_img = (
            df[df["nome_arquivo"] == img].sort_values("iou", ascending=True).iloc[0]
        )
        if worst_for_img.name not in top_results.index:
            top_results = pd.concat([top_results, pd.DataFrame([worst_for_img])])

    # Bottom N - pegar piores + melhor de cada imagem
    bottom_results = sorted_df.tail(n).copy()
    bottom_images = bottom_results["nome_arquivo"].unique()
    for img in bottom_images:
        best_for_img = (
            df[df["nome_arquivo"] == img].sort_values("iou", ascending=False).iloc[0]
        )
        if best_for_img.name not in bottom_results.index:
            bottom_results = pd.concat([bottom_results, pd.DataFrame([best_for_img])])

    return top_results, bottom_results


def get_top_bottom_area(
    df: pd.DataFrame, n: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna top N (menor dif) e bottom N (maior dif) para área.

    Para top N (melhores): inclui também o pior resultado para cada imagem
    Para bottom N (piores): inclui também o melhor resultado para cada imagem
    """
    sorted_df = df.sort_values("area_diff_rel", ascending=True)

    # Top N - pegar melhores (menor diferença) + pior de cada imagem
    top_results = sorted_df.head(n).copy()
    top_images = top_results["nome_arquivo"].unique()
    for img in top_images:
        worst_for_img = (
            df[df["nome_arquivo"] == img]
            .sort_values("area_diff_rel", ascending=False)
            .iloc[0]
        )
        if worst_for_img.name not in top_results.index:
            top_results = pd.concat([top_results, pd.DataFrame([worst_for_img])])

    # Bottom N - pegar piores (maior diferença) + melhor de cada imagem
    bottom_results = sorted_df.tail(n).copy()
    bottom_images = bottom_results["nome_arquivo"].unique()
    for img in bottom_images:
        best_for_img = (
            df[df["nome_arquivo"] == img]
            .sort_values("area_diff_rel", ascending=True)
            .iloc[0]
        )
        if best_for_img.name not in bottom_results.index:
            bottom_results = pd.concat([bottom_results, pd.DataFrame([best_for_img])])

    return top_results, bottom_results


def get_top_bottom_perimetro(
    df: pd.DataFrame, n: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna top N (menor dif) e bottom N (maior dif) para perímetro.

    Para top N (melhores): inclui também o pior resultado para cada imagem
    Para bottom N (piores): inclui também o melhor resultado para cada imagem
    """
    sorted_df = df.sort_values("perimetro_diff_rel", ascending=True)

    # Top N - pegar melhores (menor diferença) + pior de cada imagem
    top_results = sorted_df.head(n).copy()
    top_images = top_results["nome_arquivo"].unique()
    for img in top_images:
        worst_for_img = (
            df[df["nome_arquivo"] == img]
            .sort_values("perimetro_diff_rel", ascending=False)
            .iloc[0]
        )
        if worst_for_img.name not in top_results.index:
            top_results = pd.concat([top_results, pd.DataFrame([worst_for_img])])

    # Bottom N - pegar piores (maior diferença) + melhor de cada imagem
    bottom_results = sorted_df.tail(n).copy()
    bottom_images = bottom_results["nome_arquivo"].unique()
    for img in bottom_images:
        best_for_img = (
            df[df["nome_arquivo"] == img]
            .sort_values("perimetro_diff_rel", ascending=True)
            .iloc[0]
        )
        if best_for_img.name not in bottom_results.index:
            bottom_results = pd.concat([bottom_results, pd.DataFrame([best_for_img])])

    return top_results, bottom_results
