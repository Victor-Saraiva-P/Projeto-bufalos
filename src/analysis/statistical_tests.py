from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, norm, rankdata

from src.analysis.descriptive_stats import MetricConfig, RAW_METRIC_CONFIGS


GLOBAL_SCOPE = "__global__"


def build_model_comparison_tests(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
) -> pd.DataFrame:
    _validate_base_columns(df_base, required_columns={"modelo"}, metric_configs=metric_configs)

    rows: list[dict[str, object]] = []
    model_names = sorted(df_base["modelo"].dropna().unique().tolist())
    if len(model_names) < 2:
        return pd.DataFrame(columns=_model_test_columns())

    for metric_config in metric_configs:
        values_by_model = {
            model_name: df_base.loc[df_base["modelo"] == model_name, metric_config.metric_name]
            .astype(float)
            .to_numpy()
            for model_name in model_names
        }
        non_empty_groups = [values for values in values_by_model.values() if len(values) > 0]
        if len(non_empty_groups) < 2:
            continue

        global_statistic, global_p = kruskal(*non_empty_groups)
        rows.append(
            {
                "metric_name": metric_config.metric_name,
                "comparison_scope": "global",
                "test_name": "kruskal_wallis",
                "group_a": "all_models",
                "group_b": "",
                "n_group_a": int(sum(len(values) for values in values_by_model.values())),
                "n_group_b": int(len(values_by_model)),
                "statistic": float(global_statistic),
                "p_value": float(global_p),
                "p_value_adjusted": float(global_p),
                "effect_size": None,
                "effect_size_label": None,
                "mean_group_a": float(df_base[metric_config.metric_name].mean()),
                "mean_group_b": float(df_base[metric_config.metric_name].mean()),
                "median_group_a": float(df_base[metric_config.metric_name].median()),
                "median_group_b": float(df_base[metric_config.metric_name].median()),
                "favored_group": None,
            }
        )

        pairwise_rows = _build_dunn_pairwise_rows(values_by_model, metric_config)
        rows.extend(pairwise_rows)

    return pd.DataFrame(rows, columns=_model_test_columns())


def build_tag_impact_tests(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
) -> pd.DataFrame:
    _validate_base_columns(df_base, required_columns={"modelo"}, metric_configs=metric_configs)
    tag_columns = [column for column in df_base.columns if column.startswith("tag_")]
    if not tag_columns:
        raise ValueError("DataFrame base não contém colunas de tag.")

    rows: list[dict[str, object]] = []
    for metric_config in metric_configs:
        metric_name = metric_config.metric_name
        for tag_name in tag_columns:
            global_row = _build_tag_test_row(
                df_scope=df_base,
                metric_name=metric_name,
                tag_name=tag_name,
                comparison_scope="global",
                nome_modelo=GLOBAL_SCOPE,
            )
            if global_row is not None:
                rows.append(global_row)

            per_model_rows: list[dict[str, object]] = []
            for model_name, model_df in df_base.groupby("modelo", dropna=False):
                row = _build_tag_test_row(
                    df_scope=model_df,
                    metric_name=metric_name,
                    tag_name=tag_name,
                    comparison_scope="por_modelo",
                    nome_modelo=str(model_name),
                )
                if row is not None:
                    per_model_rows.append(row)

            if per_model_rows:
                adjusted = holm_adjust([float(row["p_value"]) for row in per_model_rows])
                for row, adjusted_p in zip(per_model_rows, adjusted, strict=True):
                    row["p_value_adjusted"] = adjusted_p
                rows.extend(per_model_rows)

    return pd.DataFrame(rows, columns=_tag_test_columns())


def build_model_tag_interactions(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig] = RAW_METRIC_CONFIGS,
) -> pd.DataFrame:
    _validate_base_columns(df_base, required_columns={"modelo"}, metric_configs=metric_configs)
    tag_columns = [column for column in df_base.columns if column.startswith("tag_")]
    if not tag_columns:
        raise ValueError("DataFrame base não contém colunas de tag.")

    rows: list[dict[str, object]] = []
    for metric_config in metric_configs:
        metric_name = metric_config.metric_name
        for model_name, model_df in df_base.groupby("modelo", dropna=False):
            for tag_name in tag_columns:
                com_tag = model_df.loc[model_df[tag_name], metric_name].astype(float)
                sem_tag = model_df.loc[~model_df[tag_name], metric_name].astype(float)
                if com_tag.empty or sem_tag.empty:
                    continue

                delta_mean = float(com_tag.mean() - sem_tag.mean())
                delta_median = float(com_tag.median() - sem_tag.median())
                adjusted_delta_mean = (
                    delta_mean if metric_config.higher_is_better else -delta_mean
                )
                adjusted_delta_median = (
                    delta_median if metric_config.higher_is_better else -delta_median
                )
                relative_delta_mean = (
                    adjusted_delta_mean / abs(float(sem_tag.mean()))
                    if float(sem_tag.mean()) != 0.0
                    else 0.0
                )

                if adjusted_delta_mean < 0:
                    impact_direction = "piora"
                elif adjusted_delta_mean > 0:
                    impact_direction = "melhora"
                else:
                    impact_direction = "neutro"

                rows.append(
                    {
                        "nome_modelo": str(model_name),
                        "tag_name": tag_name,
                        "metric_name": metric_name,
                        "count_com_tag": int(len(com_tag)),
                        "count_sem_tag": int(len(sem_tag)),
                        "mean_com_tag": float(com_tag.mean()),
                        "mean_sem_tag": float(sem_tag.mean()),
                        "median_com_tag": float(com_tag.median()),
                        "median_sem_tag": float(sem_tag.median()),
                        "delta_mean": delta_mean,
                        "delta_median": delta_median,
                        "relative_delta_mean": relative_delta_mean,
                        "adjusted_delta_mean": adjusted_delta_mean,
                        "adjusted_delta_median": adjusted_delta_median,
                        "impact_direction": impact_direction,
                        "higher_is_better": metric_config.higher_is_better,
                    }
                )

    return pd.DataFrame(rows)


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    values = list(p_values)
    if not values:
        return []

    indexed = sorted(enumerate(values), key=lambda item: item[1])
    adjusted = [0.0] * len(values)
    running_max = 0.0
    total = len(values)

    for rank, (original_index, p_value) in enumerate(indexed):
        candidate = min(1.0, (total - rank) * p_value)
        running_max = max(running_max, candidate)
        adjusted[original_index] = running_max

    return adjusted


def cliffs_delta(values_a: Sequence[float], values_b: Sequence[float]) -> float:
    if not values_a or not values_b:
        raise ValueError("Cliff's Delta requer dois grupos não vazios.")

    greater = 0
    lower = 0
    for value_a in values_a:
        for value_b in values_b:
            if value_a > value_b:
                greater += 1
            elif value_a < value_b:
                lower += 1

    total_pairs = len(values_a) * len(values_b)
    return float((greater - lower) / total_pairs)


def cliffs_delta_label(delta: float) -> str:
    absolute_delta = abs(delta)
    if absolute_delta < 0.147:
        return "negligible"
    if absolute_delta < 0.33:
        return "small"
    if absolute_delta < 0.474:
        return "medium"
    return "large"


def _build_dunn_pairwise_rows(
    values_by_model: dict[str, np.ndarray],
    metric_config: MetricConfig,
) -> list[dict[str, object]]:
    model_names = sorted(values_by_model)
    all_values = np.concatenate([values_by_model[model_name] for model_name in model_names])
    all_groups = np.concatenate(
        [np.repeat(model_name, len(values_by_model[model_name])) for model_name in model_names]
    )
    ranks = rankdata(all_values, method="average")
    tie_correction = _calculate_tie_correction(all_values)
    n_total = len(all_values)

    raw_rows: list[dict[str, object]] = []
    raw_p_values: list[float] = []

    for group_a, group_b in combinations(model_names, 2):
        values_a = values_by_model[group_a]
        values_b = values_by_model[group_b]
        mean_rank_a = float(ranks[all_groups == group_a].mean())
        mean_rank_b = float(ranks[all_groups == group_b].mean())
        variance = (
            (n_total * (n_total + 1) / 12.0)
            * tie_correction
            * (1 / len(values_a) + 1 / len(values_b))
        )
        statistic = float((mean_rank_a - mean_rank_b) / np.sqrt(variance)) if variance > 0 else 0.0
        p_value = float(2 * (1 - norm.cdf(abs(statistic))))

        favored_group = _favor_group(
            group_a=group_a,
            group_b=group_b,
            mean_a=float(values_a.mean()),
            mean_b=float(values_b.mean()),
            higher_is_better=metric_config.higher_is_better,
        )
        delta = cliffs_delta(values_a.tolist(), values_b.tolist())

        raw_rows.append(
            {
                "metric_name": metric_config.metric_name,
                "comparison_scope": "pairwise",
                "test_name": "dunn_holm",
                "group_a": group_a,
                "group_b": group_b,
                "n_group_a": int(len(values_a)),
                "n_group_b": int(len(values_b)),
                "statistic": statistic,
                "p_value": p_value,
                "p_value_adjusted": p_value,
                "effect_size": delta,
                "effect_size_label": cliffs_delta_label(delta),
                "mean_group_a": float(values_a.mean()),
                "mean_group_b": float(values_b.mean()),
                "median_group_a": float(np.median(values_a)),
                "median_group_b": float(np.median(values_b)),
                "favored_group": favored_group,
            }
        )
        raw_p_values.append(p_value)

    adjusted = holm_adjust(raw_p_values)
    for row, adjusted_p in zip(raw_rows, adjusted, strict=True):
        row["p_value_adjusted"] = adjusted_p

    return raw_rows


def _build_tag_test_row(
    df_scope: pd.DataFrame,
    metric_name: str,
    tag_name: str,
    comparison_scope: str,
    nome_modelo: str,
) -> dict[str, object] | None:
    com_tag = df_scope.loc[df_scope[tag_name], metric_name].astype(float)
    sem_tag = df_scope.loc[~df_scope[tag_name], metric_name].astype(float)
    if com_tag.empty or sem_tag.empty:
        return None

    statistic, p_value = mannwhitneyu(com_tag.to_list(), sem_tag.to_list(), alternative="two-sided")
    effect_size = cliffs_delta(com_tag.to_list(), sem_tag.to_list())

    return {
        "metric_name": metric_name,
        "tag_name": tag_name,
        "comparison_scope": comparison_scope,
        "nome_modelo": nome_modelo,
        "test_name": "mann_whitney_u",
        "n_group_a": int(len(com_tag)),
        "n_group_b": int(len(sem_tag)),
        "statistic": float(statistic),
        "p_value": float(p_value),
        "p_value_adjusted": float(p_value),
        "effect_size": effect_size,
        "effect_size_label": cliffs_delta_label(effect_size),
        "mean_com_tag": float(com_tag.mean()),
        "mean_sem_tag": float(sem_tag.mean()),
        "median_com_tag": float(com_tag.median()),
        "median_sem_tag": float(sem_tag.median()),
        "delta_mean": float(com_tag.mean() - sem_tag.mean()),
        "delta_median": float(com_tag.median() - sem_tag.median()),
    }


def _calculate_tie_correction(values: np.ndarray) -> float:
    _, counts = np.unique(values, return_counts=True)
    if len(values) <= 1:
        return 1.0
    tie_sum = int(np.sum(counts**3 - counts))
    denominator = len(values) ** 3 - len(values)
    return 1.0 - (tie_sum / denominator) if denominator else 1.0


def _favor_group(
    group_a: str,
    group_b: str,
    mean_a: float,
    mean_b: float,
    higher_is_better: bool,
) -> str:
    if mean_a == mean_b:
        return "empate"
    if higher_is_better:
        return group_a if mean_a > mean_b else group_b
    return group_a if mean_a < mean_b else group_b


def _validate_base_columns(
    df_base: pd.DataFrame,
    required_columns: set[str],
    metric_configs: Sequence[MetricConfig],
) -> None:
    if df_base.empty:
        raise ValueError("DataFrame base está vazio.")

    missing_required = sorted(required_columns - set(df_base.columns))
    if missing_required:
        raise ValueError(
            "Colunas obrigatórias ausentes no DataFrame base: "
            + ", ".join(missing_required)
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


def _model_test_columns() -> list[str]:
    return [
        "metric_name",
        "comparison_scope",
        "test_name",
        "group_a",
        "group_b",
        "n_group_a",
        "n_group_b",
        "statistic",
        "p_value",
        "p_value_adjusted",
        "effect_size",
        "effect_size_label",
        "mean_group_a",
        "mean_group_b",
        "median_group_a",
        "median_group_b",
        "favored_group",
    ]


def _tag_test_columns() -> list[str]:
    return [
        "metric_name",
        "tag_name",
        "comparison_scope",
        "nome_modelo",
        "test_name",
        "n_group_a",
        "n_group_b",
        "statistic",
        "p_value",
        "p_value_adjusted",
        "effect_size",
        "effect_size_label",
        "mean_com_tag",
        "mean_sem_tag",
        "median_com_tag",
        "median_sem_tag",
        "delta_mean",
        "delta_median",
    ]
