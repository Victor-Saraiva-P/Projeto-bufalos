import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.visualization import plot_pairwise_pvalue_heatmap


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
