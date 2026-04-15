from __future__ import annotations

from typing import Mapping, Sequence

import pandas as pd

from src.analysis.descriptive_stats import MetricConfig


def select_top_models_for_final_validation(
    df_rankings: pd.DataFrame,
    *,
    scenario_key: str,
    top_n: int,
    model_column: str = "modelo",
) -> pd.DataFrame:
    if top_n < 1:
        raise ValueError("top_n deve ser >= 1.")
    _require_columns(
        df_rankings,
        {"scenario_key", "scenario_rank", model_column},
        "selecionar modelos finalistas",
    )

    df_selected = df_rankings.loc[df_rankings["scenario_key"] == scenario_key].copy()
    if df_selected.empty:
        raise ValueError(f"Nenhum ranking encontrado para o cenario {scenario_key}.")

    return (
        df_selected.sort_values(["scenario_rank", model_column])
        .head(top_n)
        .reset_index(drop=True)
    )


def select_best_strategies_for_models(
    df_rankings_within_model: pd.DataFrame,
    selected_models: Sequence[str],
    *,
    scenario_key: str,
    model_column: str = "modelo",
    strategy_column: str = "estrategia_binarizacao",
) -> pd.DataFrame:
    if not selected_models:
        raise ValueError("selected_models nao pode ser vazio.")
    _require_columns(
        df_rankings_within_model,
        {"scenario_key", "strategy_rank_within_model", model_column, strategy_column},
        "selecionar melhores estrategias",
    )

    df_selected = df_rankings_within_model.loc[
        (df_rankings_within_model["scenario_key"] == scenario_key)
        & (df_rankings_within_model[model_column].isin(selected_models))
        & (df_rankings_within_model["strategy_rank_within_model"] == 1)
    ].copy()
    if df_selected.empty:
        raise ValueError(
            f"Nenhuma melhor estrategia encontrada para o cenario {scenario_key}."
        )
    return df_selected.sort_values(model_column).reset_index(drop=True)


def build_threshold_decision_table(
    df_finalists: pd.DataFrame,
    metric_thresholds: Mapping[str, float],
    metric_configs: Sequence[MetricConfig],
    *,
    entity_column: str = "combo",
    acceptance_rule: str = "all_metrics",
) -> pd.DataFrame:
    _require_columns(df_finalists, {entity_column}, "avaliacao final por thresholds")
    if acceptance_rule != "all_metrics":
        raise ValueError(f"Regra de aceitacao nao suportada: {acceptance_rule}.")

    result = df_finalists.copy()
    evaluation_columns: list[str] = []
    failed_columns: list[str] = []

    for metric_config in metric_configs:
        metric_name = metric_config.metric_name
        if metric_name not in metric_thresholds:
            raise ValueError(f"Threshold ausente para a metrica {metric_name}.")
        if metric_name not in result.columns:
            raise ValueError(
                f"DataFrame de finalistas nao contem a metrica {metric_name}."
            )

        threshold_value = float(metric_thresholds[metric_name])
        result[f"{metric_name}_min"] = threshold_value
        if metric_config.higher_is_better:
            passed = result[metric_name] >= threshold_value
        else:
            passed = result[metric_name] <= threshold_value
        column_name = f"{metric_name}_ok"
        result[column_name] = passed
        evaluation_columns.append(column_name)

    result["metricas_reprovadas"] = result.apply(
        lambda row: ",".join(
            metric_config.metric_name
            for metric_config in metric_configs
            if not bool(row[f"{metric_config.metric_name}_ok"])
        ),
        axis=1,
    )
    result["aprovado"] = result[evaluation_columns].all(axis=1)
    return result


def build_finalist_base(
    df_base: pd.DataFrame,
    finalists: pd.DataFrame,
    *,
    model_column: str = "modelo",
    strategy_column: str = "estrategia_binarizacao",
) -> pd.DataFrame:
    _require_columns(
        finalists,
        {model_column, strategy_column},
        "montagem da base finalista",
    )
    _require_columns(
        df_base,
        {model_column, strategy_column},
        "montagem da base finalista",
    )

    finalist_keys = finalists[[model_column, strategy_column]].drop_duplicates()
    result = df_base.merge(
        finalist_keys,
        on=[model_column, strategy_column],
        how="inner",
    )
    if result.empty:
        raise ValueError("Nenhum registro encontrado para os finalistas selecionados.")
    return result.reset_index(drop=True)


def _require_columns(df: pd.DataFrame, required_columns: set[str], context: str) -> None:
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            f"DataFrame para {context} nao contem as colunas obrigatorias: {missing}."
        )
