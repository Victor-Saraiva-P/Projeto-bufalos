from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from src.analysis.descriptive_stats import MetricConfig, build_descriptive_stats
from src.analysis.statistical_tests import GLOBAL_SCOPE, build_tag_impact_tests


SCENARIO_DATASET_COMPLETO = "dataset_completo"
SCENARIO_CENARIO_IDEAL = "cenario_ideal"
SCENARIO_APENAS_OK = "apenas_ok"


@dataclass(frozen=True)
class ScenarioSlice:
    scenario_key: str
    scenario_label: str
    df: pd.DataFrame


def _normalize_tag_column_names(tag_names: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for tag_name in tag_names:
        if not tag_name:
            continue
        normalized_tag = str(tag_name).strip()
        if not normalized_tag:
            continue
        if not normalized_tag.startswith("tag_"):
            normalized_tag = f"tag_{normalized_tag}"
        normalized.append(normalized_tag)
    return sorted(dict.fromkeys(normalized))


def build_negative_tag_impact_overview(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    alpha: float = 0.05,
) -> pd.DataFrame:
    if df_base.empty:
        raise ValueError("DataFrame base esta vazio.")

    tag_tests = build_tag_impact_tests(df_base=df_base, metric_configs=metric_configs)
    if tag_tests.empty:
        return pd.DataFrame(
            columns=[
                "tag_name",
                "metric_name",
                "p_value_adjusted",
                "delta_mean",
                "adjusted_delta_mean",
                "impact_direction",
                "impact_is_significant",
                "impacto_negativo_significativo",
                "higher_is_better",
            ]
        )

    metric_direction = {
        metric_config.metric_name: metric_config.higher_is_better
        for metric_config in metric_configs
    }

    result = tag_tests.loc[tag_tests["comparison_scope"] == "global"].copy()
    if result.empty:
        return pd.DataFrame(
            columns=[
                "tag_name",
                "metric_name",
                "p_value_adjusted",
                "delta_mean",
                "adjusted_delta_mean",
                "impact_direction",
                "impact_is_significant",
                "impacto_negativo_significativo",
                "higher_is_better",
            ]
        )

    result["higher_is_better"] = result["metric_name"].map(metric_direction)
    result["adjusted_delta_mean"] = np.where(
        result["higher_is_better"],
        result["delta_mean"],
        -result["delta_mean"],
    )
    result["impact_direction"] = np.select(
        [
            result["adjusted_delta_mean"] < 0,
            result["adjusted_delta_mean"] > 0,
        ],
        [
            "piora",
            "melhora",
        ],
        default="neutro",
    )
    result["impact_is_significant"] = result["p_value_adjusted"] < alpha
    result["impacto_negativo_significativo"] = (
        result["impact_is_significant"] & (result["adjusted_delta_mean"] < 0)
    )
    return result[
        [
            "tag_name",
            "metric_name",
            "p_value_adjusted",
            "delta_mean",
            "adjusted_delta_mean",
            "impact_direction",
            "impact_is_significant",
            "impacto_negativo_significativo",
            "higher_is_better",
        ]
    ].sort_values(["tag_name", "metric_name"]).reset_index(drop=True)


def identify_negative_impact_tags(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    alpha: float = 0.05,
) -> list[str]:
    overview = build_negative_tag_impact_overview(
        df_base=df_base,
        metric_configs=metric_configs,
        alpha=alpha,
    )
    if overview.empty:
        return []

    return sorted(
        overview.loc[overview["impacto_negativo_significativo"], "tag_name"].unique().tolist()
    )


def build_analysis_scenarios(
    df_base: pd.DataFrame,
    ideal_allowed_tags: Sequence[str],
) -> list[ScenarioSlice]:
    if df_base.empty:
        raise ValueError("DataFrame base esta vazio.")

    scenario_frames: list[ScenarioSlice] = [
        ScenarioSlice(
            scenario_key=SCENARIO_DATASET_COMPLETO,
            scenario_label="Dataset completo",
            df=df_base.copy(),
        )
    ]

    problem_tag_columns = sorted(
        column_name
        for column_name in df_base.columns
        if column_name.startswith("tag_") and column_name != "tag_ok"
    )
    allowed_tag_columns = _normalize_tag_column_names(ideal_allowed_tags)
    if allowed_tag_columns:
        missing = [
            tag_name for tag_name in allowed_tag_columns if tag_name not in problem_tag_columns
        ]
        if missing:
            raise ValueError(
                "Tags permitidas do cenario ideal ausentes no DataFrame base: "
                + ", ".join(sorted(missing))
            )
    disallowed_tag_columns = [
        column_name
        for column_name in problem_tag_columns
        if column_name not in set(allowed_tag_columns)
    ]
    if disallowed_tag_columns:
        # Docs: docs/avaliacao/objetivos-das-analises-estatisticas.md
        # O cenario ideal e um recorte declarativo: ele remove apenas as tags
        # de problema que nao foram explicitamente permitidas para esta analise.
        ideal_mask = ~df_base[disallowed_tag_columns].fillna(False).any(axis=1)
        ideal_df = df_base.loc[ideal_mask].copy()
    else:
        ideal_df = df_base.copy()

    scenario_frames.append(
        ScenarioSlice(
            scenario_key=SCENARIO_CENARIO_IDEAL,
            scenario_label="Cenario ideal",
            df=ideal_df,
        )
    )

    if "grupo_dificuldade" in df_base.columns:
        ok_df = df_base.loc[df_base["grupo_dificuldade"] == "ok"].copy()
    elif "tag_ok" in df_base.columns:
        ok_df = df_base.loc[df_base["tag_ok"]].copy()
    else:
        raise ValueError(
            "DataFrame base precisa de grupo_dificuldade ou tag_ok para o cenario apenas_ok."
        )

    scenario_frames.append(
        ScenarioSlice(
            scenario_key=SCENARIO_APENAS_OK,
            scenario_label="Apenas imagens ok",
            df=ok_df,
        )
    )

    return scenario_frames


def build_scenario_rankings(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    group_by: Sequence[str],
    ideal_allowed_tags: Sequence[str],
    primary_metric: str | None = None,
) -> pd.DataFrame:
    if not group_by:
        raise ValueError("group_by deve conter pelo menos uma coluna.")

    primary_metric = primary_metric or metric_configs[0].metric_name
    primary_config = next(
        (metric_config for metric_config in metric_configs if metric_config.metric_name == primary_metric),
        None,
    )
    if primary_config is None:
        raise ValueError(f"Metrica primaria desconhecida: {primary_metric}.")

    rows: list[dict[str, object]] = []
    for scenario in build_analysis_scenarios(
        df_base=df_base,
        ideal_allowed_tags=ideal_allowed_tags,
    ):
        if scenario.df.empty:
            continue

        stats = build_descriptive_stats(
            df_base=scenario.df,
            metric_configs=metric_configs,
            group_by=group_by,
        )
        if stats.empty:
            continue

        rank_parts: list[pd.DataFrame] = []
        mean_parts: list[pd.DataFrame] = []

        for metric_config in metric_configs:
            metric_stats = stats.loc[stats["metric_name"] == metric_config.metric_name].copy()
            metric_stats["metric_rank"] = metric_stats["mean"].rank(
                method="min",
                ascending=not metric_config.higher_is_better,
            )
            rank_parts.append(
                metric_stats[list(group_by) + ["metric_rank"]].rename(
                    columns={"metric_rank": f"rank_{metric_config.metric_name}"}
                )
            )
            mean_parts.append(
                metric_stats[list(group_by) + ["mean"]].rename(
                    columns={"mean": metric_config.metric_name}
                )
            )

        ranking = mean_parts[0]
        for part in mean_parts[1:]:
            ranking = ranking.merge(part, on=list(group_by), how="inner")
        for part in rank_parts:
            ranking = ranking.merge(part, on=list(group_by), how="inner")

        rank_columns = [f"rank_{metric_config.metric_name}" for metric_config in metric_configs]
        ranking["mean_rank"] = ranking[rank_columns].mean(axis=1)
        ranking["wins"] = (ranking[rank_columns] == 1).sum(axis=1)
        ranking["scenario_key"] = scenario.scenario_key
        ranking["scenario_label"] = scenario.scenario_label
        ranking["count_registros"] = len(scenario.df)
        ranking["count_imagens"] = int(scenario.df["nome_arquivo"].nunique())
        ranking = ranking.sort_values(
            by=[
                "mean_rank",
                "wins",
                primary_metric,
            ],
            ascending=[True, False, not primary_config.higher_is_better],
        ).reset_index(drop=True)
        ranking["scenario_rank"] = ranking.index + 1

        rows.extend(ranking.to_dict(orient="records"))

    return pd.DataFrame(rows)


def build_best_entities_by_scenario(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    group_by: Sequence[str],
    ideal_allowed_tags: Sequence[str],
    primary_metric: str | None = None,
) -> pd.DataFrame:
    rankings = build_scenario_rankings(
        df_base=df_base,
        metric_configs=metric_configs,
        group_by=group_by,
        ideal_allowed_tags=ideal_allowed_tags,
        primary_metric=primary_metric,
    )
    if rankings.empty:
        return rankings
    return rankings.loc[rankings["scenario_rank"] == 1].reset_index(drop=True)


def build_strategy_rankings_within_model_by_scenario(
    df_base: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    ideal_allowed_tags: Sequence[str],
    *,
    model_column: str = "modelo",
    strategy_column: str = "estrategia_binarizacao",
    primary_metric: str | None = None,
) -> pd.DataFrame:
    if model_column not in df_base.columns:
        raise ValueError(f"Coluna de modelo ausente no DataFrame base: {model_column}.")
    if strategy_column not in df_base.columns:
        raise ValueError(
            f"Coluna de estrategia ausente no DataFrame base: {strategy_column}."
        )

    primary_metric = primary_metric or metric_configs[0].metric_name
    primary_config = next(
        (
            metric_config
            for metric_config in metric_configs
            if metric_config.metric_name == primary_metric
        ),
        None,
    )
    if primary_config is None:
        raise ValueError(f"Metrica primaria desconhecida: {primary_metric}.")
    rows: list[pd.DataFrame] = []

    for scenario in build_analysis_scenarios(
        df_base=df_base,
        ideal_allowed_tags=ideal_allowed_tags,
    ):
        if scenario.df.empty:
            continue

        for model_name, df_model in scenario.df.groupby(model_column):
            stats = build_descriptive_stats(
                df_base=df_model.copy(),
                metric_configs=metric_configs,
                group_by=[strategy_column],
            )
            if stats.empty:
                continue

            rank_parts: list[pd.DataFrame] = []
            mean_parts: list[pd.DataFrame] = []

            for metric_config in metric_configs:
                metric_stats = stats.loc[
                    stats["metric_name"] == metric_config.metric_name
                ].copy()
                metric_stats["metric_rank"] = metric_stats["mean"].rank(
                    method="min",
                    ascending=not metric_config.higher_is_better,
                )
                rank_parts.append(
                    metric_stats[[strategy_column, "metric_rank"]].rename(
                        columns={"metric_rank": f"rank_{metric_config.metric_name}"}
                    )
                )
                mean_parts.append(
                    metric_stats[[strategy_column, "mean"]].rename(
                        columns={"mean": metric_config.metric_name}
                    )
                )

            rankings = mean_parts[0]
            for part in mean_parts[1:]:
                rankings = rankings.merge(part, on=[strategy_column], how="inner")
            for part in rank_parts:
                rankings = rankings.merge(part, on=[strategy_column], how="inner")

            rank_columns = [
                f"rank_{metric_config.metric_name}" for metric_config in metric_configs
            ]
            rankings["mean_rank"] = rankings[rank_columns].mean(axis=1)
            rankings["wins"] = (rankings[rank_columns] == 1).sum(axis=1)
            rankings = rankings.sort_values(
                by=["mean_rank", "wins", primary_metric],
                ascending=[True, False, not primary_config.higher_is_better],
            ).reset_index(drop=True)
            rankings["strategy_rank_within_model"] = rankings.index + 1
            rankings["scenario_key"] = scenario.scenario_key
            rankings["scenario_label"] = scenario.scenario_label
            rankings[model_column] = model_name
            rankings["count_registros"] = len(df_model)
            rankings["count_imagens"] = int(df_model["nome_arquivo"].nunique())
            rankings["count_registros_modelo"] = len(df_model)
            rankings["count_imagens_modelo"] = int(df_model["nome_arquivo"].nunique())
            rows.append(rankings)

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def build_focus_model_strategy_rankings(
    df_base_binarizada: pd.DataFrame,
    best_models_by_scenario: pd.DataFrame,
    metric_configs: Sequence[MetricConfig],
    ideal_allowed_tags: Sequence[str],
    primary_metric: str | None = None,
) -> pd.DataFrame:
    if "modelo" not in best_models_by_scenario.columns:
        raise ValueError("best_models_by_scenario precisa conter a coluna modelo.")

    scenario_frames = build_analysis_scenarios(
        df_base=df_base_binarizada,
        ideal_allowed_tags=ideal_allowed_tags,
    )
    scenario_map = {scenario.scenario_key: scenario for scenario in scenario_frames}
    rows: list[pd.DataFrame] = []

    for best_row in best_models_by_scenario.to_dict(orient="records"):
        scenario_key = str(best_row["scenario_key"])
        best_model = str(best_row["modelo"])
        scenario = scenario_map.get(scenario_key)
        if scenario is None or scenario.df.empty:
            continue

        focus_df = scenario.df.loc[scenario.df["modelo"] == best_model].copy()
        if focus_df.empty:
            continue

        rankings = build_scenario_rankings(
            df_base=focus_df,
            metric_configs=metric_configs,
            group_by=["estrategia_binarizacao"],
            ideal_allowed_tags=[],
            primary_metric=primary_metric,
        )
        if rankings.empty:
            continue

        rankings["modelo_foco"] = best_model
        rankings["scenario_key"] = scenario_key
        rankings["scenario_label"] = str(best_row["scenario_label"])
        rankings["count_registros"] = len(focus_df)
        rankings["count_imagens"] = int(focus_df["nome_arquivo"].nunique())
        rows.append(rankings)

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)
