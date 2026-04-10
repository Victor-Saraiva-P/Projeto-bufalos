import math

import pandas as pd
import pytest

from src.analysis import MetricConfig, build_descriptive_stats


def test_build_descriptive_stats_retorna_formato_longo_por_grupo_e_metrica() -> None:
    df_base = pd.DataFrame(
        [
            {
                "modelo": "u2netp",
                "execucao": 1,
                "tag_multi_bufalos": False,
                "auprc": 0.90,
                "soft_dice": 0.80,
                "brier_score": 0.10,
            },
            {
                "modelo": "u2netp",
                "execucao": 1,
                "tag_multi_bufalos": False,
                "auprc": 0.70,
                "soft_dice": 0.60,
                "brier_score": 0.20,
            },
            {
                "modelo": "u2net",
                "execucao": 1,
                "tag_multi_bufalos": True,
                "auprc": 0.50,
                "soft_dice": 0.40,
                "brier_score": 0.30,
            },
        ]
    )

    stats = build_descriptive_stats(
        df_base=df_base,
        metric_configs=[
            MetricConfig(metric_name="auprc", higher_is_better=True),
            MetricConfig(metric_name="brier_score", higher_is_better=False),
        ],
        group_by=["modelo", "execucao", "tag_multi_bufalos"],
    )

    assert list(stats.columns) == [
        "modelo",
        "execucao",
        "tag_multi_bufalos",
        "metric_name",
        "count",
        "mean",
        "median",
        "std",
        "min",
        "max",
        "q1",
        "q3",
        "iqr",
        "higher_is_better",
    ]
    assert len(stats) == 4

    auprc_u2netp = stats[
        (stats["modelo"] == "u2netp") & (stats["metric_name"] == "auprc")
    ].iloc[0]
    assert auprc_u2netp["count"] == 2
    assert auprc_u2netp["mean"] == pytest.approx(0.80)
    assert auprc_u2netp["median"] == pytest.approx(0.80)
    assert auprc_u2netp["std"] == pytest.approx(math.sqrt(0.02))
    assert auprc_u2netp["min"] == pytest.approx(0.70)
    assert auprc_u2netp["max"] == pytest.approx(0.90)
    assert auprc_u2netp["q1"] == pytest.approx(0.75)
    assert auprc_u2netp["q3"] == pytest.approx(0.85)
    assert auprc_u2netp["iqr"] == pytest.approx(0.10)
    assert auprc_u2netp["higher_is_better"] == True

    brier_u2net = stats[
        (stats["modelo"] == "u2net") & (stats["metric_name"] == "brier_score")
    ].iloc[0]
    assert brier_u2net["count"] == 1
    assert brier_u2net["mean"] == pytest.approx(0.30)
    assert brier_u2net["median"] == pytest.approx(0.30)
    assert brier_u2net["std"] == pytest.approx(0.0)
    assert brier_u2net["q1"] == pytest.approx(0.30)
    assert brier_u2net["q3"] == pytest.approx(0.30)
    assert brier_u2net["iqr"] == pytest.approx(0.0)
    assert brier_u2net["higher_is_better"] == False


def test_build_descriptive_stats_falha_quando_dataframe_esta_vazio() -> None:
    with pytest.raises(ValueError, match="DataFrame base está vazio"):
        build_descriptive_stats(
            df_base=pd.DataFrame(),
            metric_configs=[MetricConfig(metric_name="auprc", higher_is_better=True)],
            group_by=["modelo"],
        )


def test_build_descriptive_stats_falha_quando_coluna_de_agrupamento_nao_existe() -> None:
    df_base = pd.DataFrame([{"modelo": "u2netp", "auprc": 0.9}])

    with pytest.raises(ValueError, match="Colunas de agrupamento ausentes"):
        build_descriptive_stats(
            df_base=df_base,
            metric_configs=[MetricConfig(metric_name="auprc", higher_is_better=True)],
            group_by=["execucao"],
        )


def test_build_descriptive_stats_falha_quando_coluna_de_metrica_nao_existe() -> None:
    df_base = pd.DataFrame([{"modelo": "u2netp", "execucao": 1, "auprc": 0.9}])

    with pytest.raises(ValueError, match="Colunas de métricas ausentes"):
        build_descriptive_stats(
            df_base=df_base,
            metric_configs=[
                MetricConfig(metric_name="soft_dice", higher_is_better=True)
            ],
            group_by=["modelo"],
        )
