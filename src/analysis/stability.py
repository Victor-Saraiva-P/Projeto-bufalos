from __future__ import annotations

from typing import Sequence

import pandas as pd

from src.analysis.descriptive_stats import MetricConfig, RAW_METRIC_CONFIGS


def build_execution_stability(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
) -> pd.DataFrame:
    if df_base.empty:
        raise ValueError("DataFrame base está vazio.")
    required_columns = {"modelo", "execucao"}
    missing_columns = sorted(required_columns - set(df_base.columns))
    if missing_columns:
        raise ValueError(
            "Colunas obrigatórias ausentes no DataFrame base: "
            + ", ".join(missing_columns)
        )

    rows: list[dict[str, object]] = []
    for metric_config in metric_configs:
        if metric_config.metric_name not in df_base.columns:
            raise ValueError(
                f"Coluna de métrica ausente no DataFrame base: {metric_config.metric_name}"
            )

        per_execution = (
            df_base.groupby(["modelo", "execucao"], dropna=False)[metric_config.metric_name]
            .mean()
            .reset_index(name="execution_mean")
        )

        for model_name, model_df in per_execution.groupby("modelo", dropna=False):
            execution_means = model_df["execution_mean"].astype(float)
            mean_execucoes = float(execution_means.mean())
            std_execucoes = (
                float(execution_means.std(ddof=1)) if len(execution_means) > 1 else 0.0
            )
            cv_execucoes = (
                std_execucoes / abs(mean_execucoes) if mean_execucoes != 0.0 else 0.0
            )
            amplitude_execucoes = float(execution_means.max() - execution_means.min())

            ascending = not metric_config.higher_is_better
            ordered = model_df.sort_values("execution_mean", ascending=ascending)

            rows.append(
                {
                    "nome_modelo": str(model_name),
                    "metric_name": metric_config.metric_name,
                    "count_execucoes": int(model_df["execucao"].nunique()),
                    "mean_execucoes": mean_execucoes,
                    "std_execucoes": std_execucoes,
                    "cv_execucoes": cv_execucoes,
                    "amplitude_execucoes": amplitude_execucoes,
                    "melhor_execucao": int(ordered.iloc[0]["execucao"]),
                    "pior_execucao": int(ordered.iloc[-1]["execucao"]),
                    "higher_is_better": metric_config.higher_is_better,
                }
            )

    return pd.DataFrame(rows)
