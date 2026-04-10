from __future__ import annotations

import pandas as pd

from src.analysis.descriptive_stats import RAW_METRIC_CONFIGS, build_descriptive_stats
from src.models import (
    AnaliseSegmentacaoBrutaResumoExecucao,
    AnaliseSegmentacaoBrutaResumoModelo,
    AnaliseSegmentacaoBrutaResumoTag,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
)

def build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaResumoModeloRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaResumoModelo]]:
    df_resumo = build_descriptive_stats(
        df_base=df_base,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo"],
    )

    registros = [
        AnaliseSegmentacaoBrutaResumoModelo(
            nome_modelo=str(row["modelo"]),
            metric_name=str(row["metric_name"]),
            count=int(row["count"]),
            mean=float(row["mean"]),
            median=float(row["median"]),
            std=float(row["std"]),
            min=float(row["min"]),
            max=float(row["max"]),
            q1=float(row["q1"]),
            q3=float(row["q3"]),
            iqr=float(row["iqr"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_resumo.to_dict(orient="records")
    ]

    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBrutaResumoModeloRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_bruta_resumo_execucao(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaResumoExecucaoRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaResumoExecucao]]:
    df_resumo = build_descriptive_stats(
        df_base=df_base,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo", "execucao"],
    )

    registros = [
        AnaliseSegmentacaoBrutaResumoExecucao(
            nome_modelo=str(row["modelo"]),
            execucao=int(row["execucao"]),
            metric_name=str(row["metric_name"]),
            count=int(row["count"]),
            mean=float(row["mean"]),
            median=float(row["median"]),
            std=float(row["std"]),
            min=float(row["min"]),
            max=float(row["max"]),
            q1=float(row["q1"]),
            q3=float(row["q3"]),
            iqr=float(row["iqr"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_resumo.to_dict(orient="records")
    ]

    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBrutaResumoExecucaoRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_bruta_resumo_tag(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaResumoTagRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaResumoTag]]:
    df_tag_base = _build_tag_analysis_base(df_base)
    df_resumo = build_descriptive_stats(
        df_base=df_tag_base,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo", "tag_name", "tag_value"],
    )

    registros = [
        AnaliseSegmentacaoBrutaResumoTag(
            nome_modelo=str(row["modelo"]),
            tag_name=str(row["tag_name"]),
            tag_value=bool(row["tag_value"]),
            metric_name=str(row["metric_name"]),
            count=int(row["count"]),
            mean=float(row["mean"]),
            median=float(row["median"]),
            std=float(row["std"]),
            min=float(row["min"]),
            max=float(row["max"]),
            q1=float(row["q1"]),
            q3=float(row["q3"]),
            iqr=float(row["iqr"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_resumo.to_dict(orient="records")
    ]

    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBrutaResumoTagRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def _build_tag_analysis_base(df_base: pd.DataFrame) -> pd.DataFrame:
    tag_columns = [column for column in df_base.columns if column.startswith("tag_")]
    if not tag_columns:
        raise ValueError("DataFrame base não contém colunas de tag.")

    return df_base.melt(
        id_vars=[
            column
            for column in df_base.columns
            if column not in tag_columns
        ],
        value_vars=tag_columns,
        var_name="tag_name",
        value_name="tag_value",
    )
