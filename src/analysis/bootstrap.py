from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd

from src.analysis.descriptive_stats import MetricConfig, RAW_METRIC_CONFIGS


BOOTSTRAP_STATISTICS = ("mean", "median")


def build_bootstrap_confidence_intervals(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
    group_by: Sequence[str] = ("modelo",),
    n_resamples: int = 1000,
    random_state: int = 42,
    confidence_level: float = 0.95,
) -> pd.DataFrame:
    _validate_bootstrap_params(df_base, metric_configs, group_by, n_resamples, confidence_level)

    rng = np.random.default_rng(random_state)
    alpha = 1.0 - confidence_level
    rows: list[dict[str, object]] = []

    grouped = df_base.groupby(list(group_by), dropna=False)
    for group_key, group_df in grouped:
        normalized_key = _normalize_group_key(group_key, group_by)

        for metric_config in metric_configs:
            values = group_df[metric_config.metric_name].astype(float).to_numpy()
            resampled = rng.choice(values, size=(n_resamples, len(values)), replace=True)

            for statistic_name in BOOTSTRAP_STATISTICS:
                if statistic_name == "mean":
                    estimate = float(values.mean())
                    distribution = resampled.mean(axis=1)
                else:
                    estimate = float(np.median(values))
                    distribution = np.median(resampled, axis=1)

                rows.append(
                    {
                        **normalized_key,
                        "metric_name": metric_config.metric_name,
                        "statistic_name": statistic_name,
                        "count": int(len(values)),
                        "estimate": estimate,
                        "ci_low": float(np.quantile(distribution, alpha / 2)),
                        "ci_high": float(np.quantile(distribution, 1 - alpha / 2)),
                        "confidence_level": float(confidence_level),
                        "n_resamples": int(n_resamples),
                        "higher_is_better": metric_config.higher_is_better,
                    }
                )

    return pd.DataFrame(rows)


def _normalize_group_key(group_key: object, group_by: Sequence[str]) -> dict[str, object]:
    if len(group_by) == 1:
        return {group_by[0]: group_key}
    return dict(zip(group_by, group_key, strict=True))


def _validate_bootstrap_params(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    group_by: Sequence[str],
    n_resamples: int,
    confidence_level: float,
) -> None:
    if df_base.empty:
        raise ValueError("DataFrame base está vazio.")
    if not metric_configs:
        raise ValueError("metric_configs deve conter pelo menos uma métrica.")
    if not group_by:
        raise ValueError("group_by deve conter pelo menos uma coluna.")
    if n_resamples <= 0:
        raise ValueError("n_resamples deve ser maior que zero.")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level deve estar entre 0 e 1.")

    missing_group_columns = [column for column in group_by if column not in df_base.columns]
    if missing_group_columns:
        raise ValueError(
            "Colunas de agrupamento ausentes no DataFrame base: "
            + ", ".join(missing_group_columns)
        )

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
