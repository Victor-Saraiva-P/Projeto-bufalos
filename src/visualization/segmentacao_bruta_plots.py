from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def _require_non_empty(df: pd.DataFrame, context: str) -> None:
    if df.empty:
        raise ValueError(f"DataFrame vazio para {context}.")


def _require_columns(df: pd.DataFrame, required_columns: set[str], context: str) -> None:
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            f"DataFrame para {context} nao contem as colunas obrigatorias: {missing}."
        )


def plot_metric_bars_by_model(
    df_resumo_modelo: pd.DataFrame,
    metric_name: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_resumo_modelo, "grafico por modelo")
    _require_columns(
        df_resumo_modelo,
        {"nome_modelo", "metric_name", "mean", "higher_is_better"},
        "grafico por modelo",
    )

    df_plot = df_resumo_modelo.loc[
        df_resumo_modelo["metric_name"] == metric_name
    ].copy()
    _require_non_empty(df_plot, f"grafico por modelo da metrica {metric_name}")

    ascending = not bool(df_plot["higher_is_better"].iloc[0])
    df_plot = df_plot.sort_values("mean", ascending=ascending)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df_plot["nome_modelo"], df_plot["mean"], color="#8CB369")
    ax.set_title(f"Media de {metric_name} por modelo")
    ax.set_xlabel("Modelo")
    ax.set_ylabel("Media")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig, ax


def plot_metric_by_execution_heatmap(
    df_resumo_execucao: pd.DataFrame,
    metric_name: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_resumo_execucao, "heatmap por execucao")
    _require_columns(
        df_resumo_execucao,
        {"nome_modelo", "execucao", "metric_name", "mean"},
        "heatmap por execucao",
    )

    df_plot = df_resumo_execucao.loc[
        df_resumo_execucao["metric_name"] == metric_name
    ].copy()
    _require_non_empty(df_plot, f"heatmap por execucao da metrica {metric_name}")

    pivot = (
        df_plot.pivot(index="nome_modelo", columns="execucao", values="mean")
        .sort_index()
        .sort_index(axis=1)
    )

    fig, ax = plt.subplots(figsize=(8, max(3, len(pivot) * 0.6)))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="YlGn")
    ax.set_title(f"Media de {metric_name} por modelo e execucao")
    ax.set_xlabel("Execucao")
    ax.set_ylabel("Modelo")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    fig.colorbar(image, ax=ax, label="Media")
    fig.tight_layout()
    return fig, ax


def plot_metric_tag_comparison(
    df_resumo_tag: pd.DataFrame,
    metric_name: str,
    tag_name: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_resumo_tag, "comparacao por tag")
    _require_columns(
        df_resumo_tag,
        {"nome_modelo", "tag_name", "tag_value", "metric_name", "mean"},
        "comparacao por tag",
    )

    df_plot = df_resumo_tag.loc[
        (df_resumo_tag["metric_name"] == metric_name)
        & (df_resumo_tag["tag_name"] == tag_name)
    ].copy()
    _require_non_empty(
        df_plot, f"comparacao da metrica {metric_name} para a tag {tag_name}"
    )

    pivot = (
        df_plot.pivot(index="nome_modelo", columns="tag_value", values="mean")
        .rename(columns={False: "sem_tag", True: "com_tag"})
        .fillna(0.0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    positions = range(len(pivot.index))
    width = 0.35
    ax.bar(
        [position - width / 2 for position in positions],
        pivot.get("sem_tag", pd.Series([0.0] * len(pivot), index=pivot.index)),
        width=width,
        label="Sem tag",
        color="#4C956C",
    )
    ax.bar(
        [position + width / 2 for position in positions],
        pivot.get("com_tag", pd.Series([0.0] * len(pivot), index=pivot.index)),
        width=width,
        label="Com tag",
        color="#BC4B51",
    )
    ax.set_title(f"Impacto de {tag_name} em {metric_name}")
    ax.set_xlabel("Modelo")
    ax.set_ylabel("Media")
    ax.set_xticks(list(positions))
    ax.set_xticklabels(pivot.index, rotation=45)
    ax.legend()
    fig.tight_layout()
    return fig, ax


def plot_metric_distribution_by_model(
    df_base: pd.DataFrame,
    metric_name: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_base, "distribuicao por modelo")
    _require_columns(df_base, {"modelo", metric_name}, "distribuicao por modelo")

    grouped = df_base.groupby("modelo")[metric_name]
    labels = []
    values = []
    for model_name, series in grouped:
        labels.append(model_name)
        values.append(series.to_list())

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.boxplot(values, tick_labels=labels)
    ax.set_title(f"Distribuicao de {metric_name} por modelo")
    ax.set_xlabel("Modelo")
    ax.set_ylabel(metric_name)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig, ax


def plot_metric_distribution_by_tag(
    df_base: pd.DataFrame,
    metric_name: str,
    tag_name: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_base, "distribuicao por tag")
    _require_columns(df_base, {metric_name, tag_name}, "distribuicao por tag")

    false_values = df_base.loc[~df_base[tag_name], metric_name].to_list()
    true_values = df_base.loc[df_base[tag_name], metric_name].to_list()
    if not false_values and not true_values:
        raise ValueError(
            f"Nenhum dado encontrado para distribuicao da metrica {metric_name} com {tag_name}."
        )

    values = []
    labels = []
    if false_values:
        values.append(false_values)
        labels.append("sem_tag")
    if true_values:
        values.append(true_values)
        labels.append("com_tag")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(values, tick_labels=labels)
    ax.set_title(f"Distribuicao de {metric_name} por {tag_name}")
    ax.set_xlabel("Grupo")
    ax.set_ylabel(metric_name)
    fig.tight_layout()
    return fig, ax
