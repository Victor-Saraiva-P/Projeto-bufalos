from __future__ import annotations

import pandas as pd

from src.analysis.bootstrap import build_bootstrap_confidence_intervals
from src.analysis.descriptive_stats import RAW_METRIC_CONFIGS, build_descriptive_stats
from src.analysis.stability import build_execution_stability
from src.analysis.statistical_tests import (
    GLOBAL_SCOPE,
    build_model_comparison_tests,
    build_model_tag_interactions,
    build_tag_impact_tests,
)
from src.models import (
    AnaliseSegmentacaoBrutaEstabilidade,
    AnaliseSegmentacaoBrutaInteracaoTagModelo,
    AnaliseSegmentacaoBrutaIntervaloConfianca,
    AnaliseSegmentacaoBrutaResumoExecucao,
    AnaliseSegmentacaoBrutaResumoModelo,
    AnaliseSegmentacaoBrutaResumoTag,
    AnaliseSegmentacaoBrutaTesteModelo,
    AnaliseSegmentacaoBrutaTesteTag,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaEstabilidadeRepository,
    AnaliseSegmentacaoBrutaInteracaoTagModeloRepository,
    AnaliseSegmentacaoBrutaIntervaloConfiancaRepository,
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
    AnaliseSegmentacaoBrutaTesteModeloRepository,
    AnaliseSegmentacaoBrutaTesteTagRepository,
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

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaResumoModeloRepository()
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
        repository if repository is not None else AnaliseSegmentacaoBrutaResumoExecucaoRepository()
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

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaResumoTagRepository()
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_bruta_estabilidade(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaEstabilidadeRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaEstabilidade]]:
    df_estabilidade = build_execution_stability(df_base=df_base)
    registros = [
        AnaliseSegmentacaoBrutaEstabilidade(
            nome_modelo=str(row["nome_modelo"]),
            metric_name=str(row["metric_name"]),
            count_execucoes=int(row["count_execucoes"]),
            mean_execucoes=float(row["mean_execucoes"]),
            std_execucoes=float(row["std_execucoes"]),
            cv_execucoes=float(row["cv_execucoes"]),
            amplitude_execucoes=float(row["amplitude_execucoes"]),
            melhor_execucao=int(row["melhor_execucao"]),
            pior_execucao=int(row["pior_execucao"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_estabilidade.to_dict(orient="records")
    ]

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaEstabilidadeRepository()
    repo.replace_all(registros)
    return df_estabilidade, registros


def build_and_persist_analysis_segmentacao_bruta_intervalo_confianca(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaIntervaloConfiancaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaIntervaloConfianca]]:
    df_intervalos = build_bootstrap_confidence_intervals(df_base=df_base)
    registros = [
        AnaliseSegmentacaoBrutaIntervaloConfianca(
            nome_modelo=str(row["modelo"]),
            metric_name=str(row["metric_name"]),
            statistic_name=str(row["statistic_name"]),
            count=int(row["count"]),
            estimate=float(row["estimate"]),
            ci_low=float(row["ci_low"]),
            ci_high=float(row["ci_high"]),
            confidence_level=float(row["confidence_level"]),
            n_resamples=int(row["n_resamples"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_intervalos.to_dict(orient="records")
    ]

    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBrutaIntervaloConfiancaRepository()
    )
    repo.replace_all(registros)
    return df_intervalos, registros


def build_and_persist_analysis_segmentacao_bruta_testes_modelo(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaTesteModeloRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaTesteModelo]]:
    df_testes = build_model_comparison_tests(df_base=df_base)
    registros = [
        AnaliseSegmentacaoBrutaTesteModelo(
            metric_name=str(row["metric_name"]),
            comparison_scope=str(row["comparison_scope"]),
            test_name=str(row["test_name"]),
            group_a=str(row["group_a"]),
            group_b=str(row["group_b"]),
            n_group_a=int(row["n_group_a"]),
            n_group_b=int(row["n_group_b"]),
            statistic=float(row["statistic"]),
            p_value=float(row["p_value"]),
            p_value_adjusted=float(row["p_value_adjusted"]),
            effect_size=(
                float(row["effect_size"]) if pd.notna(row["effect_size"]) else None
            ),
            effect_size_label=(
                str(row["effect_size_label"])
                if pd.notna(row["effect_size_label"])
                else None
            ),
            mean_group_a=float(row["mean_group_a"]),
            mean_group_b=float(row["mean_group_b"]),
            median_group_a=float(row["median_group_a"]),
            median_group_b=float(row["median_group_b"]),
            favored_group=(
                str(row["favored_group"]) if pd.notna(row["favored_group"]) else None
            ),
        )
        for row in df_testes.to_dict(orient="records")
    ]

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaTesteModeloRepository()
    repo.replace_all(registros)
    return df_testes, registros


def build_and_persist_analysis_segmentacao_bruta_testes_tag(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaTesteTagRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaTesteTag]]:
    df_testes = build_tag_impact_tests(df_base=df_base)
    registros = [
        AnaliseSegmentacaoBrutaTesteTag(
            metric_name=str(row["metric_name"]),
            tag_name=str(row["tag_name"]),
            comparison_scope=str(row["comparison_scope"]),
            nome_modelo=str(row["nome_modelo"]),
            test_name=str(row["test_name"]),
            n_group_a=int(row["n_group_a"]),
            n_group_b=int(row["n_group_b"]),
            statistic=float(row["statistic"]),
            p_value=float(row["p_value"]),
            p_value_adjusted=float(row["p_value_adjusted"]),
            effect_size=float(row["effect_size"]),
            effect_size_label=str(row["effect_size_label"]),
            mean_com_tag=float(row["mean_com_tag"]),
            mean_sem_tag=float(row["mean_sem_tag"]),
            median_com_tag=float(row["median_com_tag"]),
            median_sem_tag=float(row["median_sem_tag"]),
            delta_mean=float(row["delta_mean"]),
            delta_median=float(row["delta_median"]),
        )
        for row in df_testes.to_dict(orient="records")
    ]

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaTesteTagRepository()
    repo.replace_all(registros)
    return df_testes, registros


def build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaInteracaoTagModeloRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBrutaInteracaoTagModelo]]:
    df_interacoes = build_model_tag_interactions(df_base=df_base)
    registros = [
        AnaliseSegmentacaoBrutaInteracaoTagModelo(
            nome_modelo=str(row["nome_modelo"]),
            tag_name=str(row["tag_name"]),
            metric_name=str(row["metric_name"]),
            count_com_tag=int(row["count_com_tag"]),
            count_sem_tag=int(row["count_sem_tag"]),
            mean_com_tag=float(row["mean_com_tag"]),
            mean_sem_tag=float(row["mean_sem_tag"]),
            median_com_tag=float(row["median_com_tag"]),
            median_sem_tag=float(row["median_sem_tag"]),
            delta_mean=float(row["delta_mean"]),
            delta_median=float(row["delta_median"]),
            relative_delta_mean=float(row["relative_delta_mean"]),
            adjusted_delta_mean=float(row["adjusted_delta_mean"]),
            adjusted_delta_median=float(row["adjusted_delta_median"]),
            impact_direction=str(row["impact_direction"]),
            higher_is_better=bool(row["higher_is_better"]),
        )
        for row in df_interacoes.to_dict(orient="records")
    ]

    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBrutaInteracaoTagModeloRepository()
    )
    repo.replace_all(registros)
    return df_interacoes, registros


def _build_tag_analysis_base(df_base: pd.DataFrame) -> pd.DataFrame:
    tag_columns = [column for column in df_base.columns if column.startswith("tag_")]
    if not tag_columns:
        raise ValueError("DataFrame base não contém colunas de tag.")

    return df_base.melt(
        id_vars=[column for column in df_base.columns if column not in tag_columns],
        value_vars=tag_columns,
        var_name="tag_name",
        value_name="tag_value",
    )
