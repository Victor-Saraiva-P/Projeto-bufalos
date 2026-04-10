import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.visualization import (
    plot_metric_correlation_heatmap,
    plot_metric_scatter,
    plot_pairwise_pvalue_heatmap,
    plot_simple_regression,
    plot_stability_bars,
)


def test_plot_pairwise_pvalue_heatmap_gera_figura_sem_erro() -> None:
    df_testes_modelo = pd.DataFrame(
        [
            {
                "metric_name": "auprc",
                "comparison_scope": "pairwise",
                "group_a": "u2netp",
                "group_b": "isnet",
                "p_value_adjusted": 0.04,
            },
            {
                "metric_name": "auprc",
                "comparison_scope": "pairwise",
                "group_a": "u2netp",
                "group_b": "sam",
                "p_value_adjusted": 0.01,
            },
            {
                "metric_name": "auprc",
                "comparison_scope": "pairwise",
                "group_a": "isnet",
                "group_b": "sam",
                "p_value_adjusted": 0.20,
            },
        ]
    )

    fig, ax = plot_pairwise_pvalue_heatmap(df_testes_modelo, "auprc")

    assert ax.images
    plt.close(fig)


def test_plot_metric_scatter_gera_figura_sem_erro() -> None:
    df_base = pd.DataFrame(
        [
            {"modelo": "u2netp", "auprc": 0.9, "soft_dice": 0.8},
            {"modelo": "u2netp", "auprc": 0.85, "soft_dice": 0.78},
            {"modelo": "isnet", "auprc": 0.7, "soft_dice": 0.6},
        ]
    )

    fig, ax = plot_metric_scatter(df_base, "auprc", "soft_dice")

    assert ax.has_data()
    plt.close(fig)


def test_plot_metric_correlation_heatmap_gera_figura_sem_erro() -> None:
    df_base = pd.DataFrame(
        [
            {"auprc": 0.9, "soft_dice": 0.8, "brier_score": 0.1},
            {"auprc": 0.85, "soft_dice": 0.78, "brier_score": 0.11},
            {"auprc": 0.7, "soft_dice": 0.6, "brier_score": 0.2},
        ]
    )

    fig, ax = plot_metric_correlation_heatmap(
        df_base,
        ["auprc", "soft_dice", "brier_score"],
        "pearson",
    )

    assert ax.images
    plt.close(fig)


def test_plot_simple_regression_gera_figura_sem_erro() -> None:
    df_base = pd.DataFrame(
        [
            {"modelo": "u2netp", "num_tags_problema": 0, "soft_dice": 0.85},
            {"modelo": "u2netp", "num_tags_problema": 1, "soft_dice": 0.75},
            {"modelo": "isnet", "num_tags_problema": 2, "soft_dice": 0.55},
        ]
    )

    fig, ax = plot_simple_regression(df_base, "num_tags_problema", "soft_dice")

    assert ax.has_data()
    plt.close(fig)


def test_plot_stability_bars_gera_figura_sem_erro() -> None:
    df_estabilidade = pd.DataFrame(
        [
            {"nome_modelo": "u2netp", "metric_name": "auprc", "cv_execucoes": 0.00001},
            {"nome_modelo": "sam", "metric_name": "auprc", "cv_execucoes": 0.00005},
            {"nome_modelo": "isnet", "metric_name": "auprc", "cv_execucoes": 0.00002},
        ]
    )

    fig, ax = plot_stability_bars(df_estabilidade, "auprc")

    assert ax.has_data()
    assert len(ax.patches) == 3
    plt.close(fig)
