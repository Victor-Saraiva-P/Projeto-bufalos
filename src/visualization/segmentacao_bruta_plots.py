from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
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


def plot_metric_bars_with_ci_by_model(
    df_resumo_modelo: pd.DataFrame,
    df_intervalo_confianca: pd.DataFrame,
    metric_name: str,
    statistic_name: str = "mean",
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_resumo_modelo, "grafico com intervalo de confianca por modelo")
    _require_non_empty(
        df_intervalo_confianca, "grafico com intervalo de confianca por modelo"
    )
    _require_columns(
        df_resumo_modelo,
        {"nome_modelo", "metric_name", "mean", "higher_is_better"},
        "grafico com intervalo de confianca por modelo",
    )
    _require_columns(
        df_intervalo_confianca,
        {"nome_modelo", "metric_name", "statistic_name", "estimate", "ci_low", "ci_high"},
        "grafico com intervalo de confianca por modelo",
    )

    df_plot = df_intervalo_confianca.loc[
        (df_intervalo_confianca["metric_name"] == metric_name)
        & (df_intervalo_confianca["statistic_name"] == statistic_name)
    ].copy()
    _require_non_empty(
        df_plot, f"grafico com intervalo de confianca da metrica {metric_name}"
    )

    higher_is_better = bool(
        df_resumo_modelo.loc[df_resumo_modelo["metric_name"] == metric_name, "higher_is_better"].iloc[0]
    )
    df_plot = df_plot.sort_values("estimate", ascending=not higher_is_better)
    errors = np.vstack(
        [
            df_plot["estimate"].to_numpy() - df_plot["ci_low"].to_numpy(),
            df_plot["ci_high"].to_numpy() - df_plot["estimate"].to_numpy(),
        ]
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(
        df_plot["nome_modelo"],
        df_plot["estimate"],
        yerr=errors,
        capsize=4,
        color="#2A9D8F",
    )
    ax.set_title(f"{statistic_name.title()} com intervalo de confianca de {metric_name}")
    ax.set_xlabel("Modelo")
    ax.set_ylabel(statistic_name.title())
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig, ax


def plot_stability_heatmap(
    df_estabilidade: pd.DataFrame,
    metric_name: str,
    value_column: str = "cv_execucoes",
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_estabilidade, "heatmap de estabilidade")
    _require_columns(
        df_estabilidade,
        {"nome_modelo", "metric_name", value_column},
        "heatmap de estabilidade",
    )

    df_plot = df_estabilidade.loc[df_estabilidade["metric_name"] == metric_name].copy()
    _require_non_empty(df_plot, f"heatmap de estabilidade da metrica {metric_name}")

    matrix = np.expand_dims(df_plot.sort_values("nome_modelo")[value_column].to_numpy(), axis=1)
    labels = df_plot.sort_values("nome_modelo")["nome_modelo"].to_list()

    fig, ax = plt.subplots(figsize=(5, max(3, len(labels) * 0.45)))
    image = ax.imshow(matrix, aspect="auto", cmap="YlOrRd")
    ax.set_title(f"{value_column} por modelo em {metric_name}")
    ax.set_xlabel(value_column)
    ax.set_ylabel("Modelo")
    ax.set_xticks([0])
    ax.set_xticklabels([value_column])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    fig.colorbar(image, ax=ax, label=value_column)
    fig.tight_layout()
    return fig, ax


def plot_pairwise_pvalue_heatmap(
    df_testes_modelo: pd.DataFrame,
    metric_name: str,
    value_column: str = "p_value_adjusted",
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_testes_modelo, "heatmap de comparacao entre modelos")
    _require_columns(
        df_testes_modelo,
        {"metric_name", "comparison_scope", "group_a", "group_b", value_column},
        "heatmap de comparacao entre modelos",
    )

    df_plot = df_testes_modelo.loc[
        (df_testes_modelo["metric_name"] == metric_name)
        & (df_testes_modelo["comparison_scope"] == "pairwise")
    ].copy()
    _require_non_empty(
        df_plot, f"heatmap de comparacao entre modelos da metrica {metric_name}"
    )

    labels = sorted(set(df_plot["group_a"]) | set(df_plot["group_b"]))
    matrix = pd.DataFrame(np.nan, index=labels, columns=labels)
    for label in labels:
        matrix.loc[label, label] = 0.0

    for row in df_plot.to_dict(orient="records"):
        matrix.loc[str(row["group_a"]), str(row["group_b"])] = float(row[value_column])
        matrix.loc[str(row["group_b"]), str(row["group_a"])] = float(row[value_column])

    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(matrix.to_numpy(), cmap="magma_r")
    ax.set_title(f"{value_column} entre pares de modelos em {metric_name}")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    fig.colorbar(image, ax=ax, label=value_column)
    fig.tight_layout()
    return fig, ax


def plot_tag_effect_bars(
    df_testes_tag: pd.DataFrame,
    metric_name: str,
    tag_name: str,
    comparison_scope: str = "por_modelo",
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_testes_tag, "grafico de efeito por tag")
    _require_columns(
        df_testes_tag,
        {"metric_name", "tag_name", "comparison_scope", "nome_modelo", "effect_size"},
        "grafico de efeito por tag",
    )

    df_plot = df_testes_tag.loc[
        (df_testes_tag["metric_name"] == metric_name)
        & (df_testes_tag["tag_name"] == tag_name)
        & (df_testes_tag["comparison_scope"] == comparison_scope)
    ].copy()
    _require_non_empty(
        df_plot, f"grafico de efeito por tag {tag_name} na metrica {metric_name}"
    )
    df_plot = df_plot.sort_values("effect_size")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df_plot["nome_modelo"], df_plot["effect_size"], color="#E76F51")
    ax.axhline(0.0, color="#222222", linewidth=1)
    ax.set_title(f"Tamanho de efeito de {tag_name} em {metric_name}")
    ax.set_xlabel("Escopo")
    ax.set_ylabel("Cliff's Delta")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig, ax


def plot_model_tag_interaction_heatmap(
    df_interacoes: pd.DataFrame,
    metric_name: str,
    value_column: str = "adjusted_delta_mean",
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_interacoes, "heatmap de interacao modelo x tag")
    _require_columns(
        df_interacoes,
        {"nome_modelo", "tag_name", "metric_name", value_column},
        "heatmap de interacao modelo x tag",
    )

    df_plot = df_interacoes.loc[df_interacoes["metric_name"] == metric_name].copy()
    _require_non_empty(
        df_plot, f"heatmap de interacao modelo x tag da metrica {metric_name}"
    )

    matrix = (
        df_plot.pivot(index="nome_modelo", columns="tag_name", values=value_column)
        .sort_index()
        .sort_index(axis=1)
        .fillna(0.0)
    )

    fig, ax = plt.subplots(figsize=(9, max(4, len(matrix.index) * 0.45)))
    image = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="coolwarm")
    ax.set_title(f"Interacao modelo x tag em {metric_name}")
    ax.set_xlabel("Tag")
    ax.set_ylabel("Modelo")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    fig.colorbar(image, ax=ax, label=value_column)
    fig.tight_layout()
    return fig, ax


def plot_metric_scatter(
    df_base: pd.DataFrame,
    x_metric: str,
    y_metric: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_base, "grafico bivariado entre metricas")
    _require_columns(
        df_base,
        {"modelo", x_metric, y_metric},
        "grafico bivariado entre metricas",
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    for model_name, model_df in df_base.groupby("modelo", dropna=False):
        ax.scatter(
            model_df[x_metric],
            model_df[y_metric],
            alpha=0.6,
            label=str(model_name),
            s=18,
        )

    ax.set_title(f"{y_metric} vs {x_metric}")
    ax.set_xlabel(x_metric)
    ax.set_ylabel(y_metric)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    return fig, ax


def plot_metric_correlation_heatmap(
    df_base: pd.DataFrame,
    metric_columns: list[str],
    method: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_base, "heatmap de correlacao")
    _require_columns(df_base, set(metric_columns), "heatmap de correlacao")

    correlation = df_base[metric_columns].corr(method=method)
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(correlation.to_numpy(), cmap="coolwarm", vmin=-1.0, vmax=1.0)
    ax.set_title(f"Correlacao {method.title()} entre metricas")
    ax.set_xticks(range(len(metric_columns)))
    ax.set_xticklabels(metric_columns, rotation=45, ha="right")
    ax.set_yticks(range(len(metric_columns)))
    ax.set_yticklabels(metric_columns)
    fig.colorbar(image, ax=ax, label="correlacao")
    fig.tight_layout()
    return fig, ax


def plot_simple_regression(
    df_base: pd.DataFrame,
    x_column: str,
    y_column: str,
) -> tuple[plt.Figure, plt.Axes]:
    _require_non_empty(df_base, "grafico de regressao simples")
    _require_columns(
        df_base,
        {"modelo", x_column, y_column},
        "grafico de regressao simples",
    )

    x_values = df_base[x_column].astype(float).to_numpy()
    y_values = df_base[y_column].astype(float).to_numpy()
    slope, intercept = np.polyfit(x_values, y_values, deg=1)
    fitted = slope * x_values + intercept
    residual = y_values - fitted
    total = y_values - y_values.mean()
    r_squared = 1.0 - float(np.sum(residual**2) / np.sum(total**2)) if np.sum(total**2) else 0.0

    fig, ax = plt.subplots(figsize=(7, 5))
    for model_name, model_df in df_base.groupby("modelo", dropna=False):
        ax.scatter(
            model_df[x_column],
            model_df[y_column],
            alpha=0.55,
            label=str(model_name),
            s=18,
        )

    x_line = np.linspace(x_values.min(), x_values.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color="#222222", linewidth=2)
    ax.set_title(f"Regressao simples: {y_column} ~ {x_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.legend(fontsize=8, ncol=2)
    ax.text(
        0.02,
        0.98,
        f"y = {slope:.4f}x + {intercept:.4f}\nR² = {r_squared:.4f}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "#bbbbbb"},
    )
    fig.tight_layout()
    return fig, ax
