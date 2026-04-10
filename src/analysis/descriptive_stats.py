from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd


@dataclass(frozen=True)
class MetricConfig:
    metric_name: str
    higher_is_better: bool


RAW_METRIC_CONFIGS: tuple[MetricConfig, ...] = (
    MetricConfig(metric_name="auprc", higher_is_better=True),
    MetricConfig(metric_name="soft_dice", higher_is_better=True),
    MetricConfig(metric_name="brier_score", higher_is_better=False),
)


def build_descriptive_stats(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
    group_by: Sequence[str] = ("modelo",),
) -> pd.DataFrame:
    _validate_input_dataframe(df_base)
    _validate_group_by(df_base, group_by)
    _validate_metric_configs(df_base, metric_configs)

    result_frames: list[pd.DataFrame] = []

    for metric_config in metric_configs:
        result_frames.append(
            _build_metric_stats(
                df_base=df_base,
                metric_config=metric_config,
                group_by=group_by,
            )
        )

    result = pd.concat(result_frames, ignore_index=True)
    ordered_columns = [
        *group_by,
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
    return result[ordered_columns]


def _build_metric_stats(
    df_base: pd.DataFrame,
    metric_config: MetricConfig,
    group_by: Sequence[str],
) -> pd.DataFrame:
    metric_name = metric_config.metric_name
    grouped = df_base.groupby(list(group_by), dropna=False)[metric_name]
    stats = grouped.agg(
        count="count",
        mean="mean",
        median="median",
        std=lambda values: float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        min="min",
        max="max",
        q1=lambda values: float(values.quantile(0.25)),
        q3=lambda values: float(values.quantile(0.75)),
    ).reset_index()

    stats["iqr"] = stats["q3"] - stats["q1"]
    stats["metric_name"] = metric_name
    stats["higher_is_better"] = metric_config.higher_is_better

    return stats


def _validate_input_dataframe(df_base: pd.DataFrame) -> None:
    if df_base.empty:
        raise ValueError("DataFrame base está vazio.")


def _validate_group_by(df_base: pd.DataFrame, group_by: Sequence[str]) -> None:
    if not group_by:
        raise ValueError("group_by deve conter pelo menos uma coluna.")

    missing_columns = [column for column in group_by if column not in df_base.columns]
    if missing_columns:
        raise ValueError(
            "Colunas de agrupamento ausentes no DataFrame base: "
            + ", ".join(missing_columns)
        )


def _validate_metric_configs(
    df_base: pd.DataFrame, metric_configs: Sequence[MetricConfig]
) -> None:
    if not metric_configs:
        raise ValueError("metric_configs deve conter pelo menos uma métrica.")

    missing_metrics = [
        metric_config.metric_name
        for metric_config in metric_configs
        if metric_config.metric_name not in df_base.columns
    ]
    if missing_metrics:
        raise ValueError(
            "Colunas de métricas ausentes no DataFrame base: "
            + ", ".join(missing_metrics)
        )
