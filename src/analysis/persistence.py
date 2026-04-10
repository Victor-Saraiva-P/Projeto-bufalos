from __future__ import annotations

import pandas as pd

from src.analysis.bootstrap import build_bootstrap_confidence_intervals
from src.analysis.descriptive_stats import (
    MetricConfig,
    RAW_METRIC_CONFIGS,
    build_descriptive_stats,
)
from src.analysis.stability import build_execution_stability
from src.analysis.statistical_tests import (
    GLOBAL_SCOPE,
    build_model_comparison_tests,
    build_model_tag_interactions,
    build_tag_impact_tests,
)
from src.models import (
    AnaliseSegmentacaoBinarizadaEstabilidade,
    AnaliseSegmentacaoBinarizadaInteracaoTagEstrategia,
    AnaliseSegmentacaoBinarizadaIntervaloConfianca,
    AnaliseSegmentacaoBinarizadaResumoEstrategia,
    AnaliseSegmentacaoBinarizadaResumoExecucao,
    AnaliseSegmentacaoBinarizadaResumoModeloEstrategia,
    AnaliseSegmentacaoBinarizadaResumoTag,
    AnaliseSegmentacaoBinarizadaTesteEstrategia,
    AnaliseSegmentacaoBinarizadaTesteTagEstrategia,
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
    AnaliseSegmentacaoBinarizadaEstabilidadeRepository,
    AnaliseSegmentacaoBinarizadaInteracaoTagEstrategiaRepository,
    AnaliseSegmentacaoBinarizadaIntervaloConfiancaRepository,
    AnaliseSegmentacaoBinarizadaResumoEstrategiaRepository,
    AnaliseSegmentacaoBinarizadaResumoExecucaoRepository,
    AnaliseSegmentacaoBinarizadaResumoModeloEstrategiaRepository,
    AnaliseSegmentacaoBinarizadaResumoTagRepository,
    AnaliseSegmentacaoBinarizadaTesteEstrategiaRepository,
    AnaliseSegmentacaoBinarizadaTesteTagEstrategiaRepository,
    AnaliseSegmentacaoBrutaEstabilidadeRepository,
    AnaliseSegmentacaoBrutaInteracaoTagModeloRepository,
    AnaliseSegmentacaoBrutaIntervaloConfiancaRepository,
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
    AnaliseSegmentacaoBrutaTesteModeloRepository,
    AnaliseSegmentacaoBrutaTesteTagRepository,
)

BINARIZED_METRIC_CONFIGS = (
    MetricConfig(metric_name="iou", higher_is_better=True),
    MetricConfig(metric_name="precision", higher_is_better=True),
    MetricConfig(metric_name="recall", higher_is_better=True),
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


def build_and_persist_analysis_segmentacao_binarizada_resumo_estrategia(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaResumoEstrategiaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaResumoEstrategia]]:
    df_resumo = build_descriptive_stats(
        df_base=df_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        group_by=["estrategia_binarizacao"],
    )
    registros = [
        AnaliseSegmentacaoBinarizadaResumoEstrategia(
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        else AnaliseSegmentacaoBinarizadaResumoEstrategiaRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_binarizada_resumo_modelo_estrategia(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaResumoModeloEstrategiaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaResumoModeloEstrategia]]:
    df_resumo = build_descriptive_stats(
        df_base=df_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        group_by=["modelo", "estrategia_binarizacao"],
    )
    registros = [
        AnaliseSegmentacaoBinarizadaResumoModeloEstrategia(
            nome_modelo=str(row["modelo"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        else AnaliseSegmentacaoBinarizadaResumoModeloEstrategiaRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_binarizada_resumo_execucao(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaResumoExecucaoRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaResumoExecucao]]:
    df_resumo = build_descriptive_stats(
        df_base=df_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        group_by=["modelo", "estrategia_binarizacao", "execucao"],
    )
    registros = [
        AnaliseSegmentacaoBinarizadaResumoExecucao(
            nome_modelo=str(row["modelo"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        else AnaliseSegmentacaoBinarizadaResumoExecucaoRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_binarizada_resumo_tag(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaResumoTagRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaResumoTag]]:
    df_tag_base = _build_tag_analysis_base(df_base)
    df_resumo = build_descriptive_stats(
        df_base=df_tag_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        group_by=["modelo", "estrategia_binarizacao", "tag_name", "tag_value"],
    )
    registros = [
        AnaliseSegmentacaoBinarizadaResumoTag(
            nome_modelo=str(row["modelo"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        repository if repository is not None else AnaliseSegmentacaoBinarizadaResumoTagRepository()
    )
    repo.replace_all(registros)
    return df_resumo, registros


def build_and_persist_analysis_segmentacao_binarizada_estabilidade(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaEstabilidadeRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaEstabilidade]]:
    df_estabilidade = _build_execution_stability_modelo_estrategia(df_base)
    registros = [
        AnaliseSegmentacaoBinarizadaEstabilidade(
            nome_modelo=str(row["modelo"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
    repo = (
        repository if repository is not None else AnaliseSegmentacaoBinarizadaEstabilidadeRepository()
    )
    repo.replace_all(registros)
    return df_estabilidade, registros


def build_and_persist_analysis_segmentacao_binarizada_intervalo_confianca(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaIntervaloConfiancaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaIntervaloConfianca]]:
    df_intervalos = build_bootstrap_confidence_intervals(
        df_base=df_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        group_by=["modelo", "estrategia_binarizacao"],
    )
    registros = [
        AnaliseSegmentacaoBinarizadaIntervaloConfianca(
            nome_modelo=str(row["modelo"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        else AnaliseSegmentacaoBinarizadaIntervaloConfiancaRepository()
    )
    repo.replace_all(registros)
    return df_intervalos, registros


def build_and_persist_analysis_segmentacao_binarizada_testes_estrategia(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaTesteEstrategiaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaTesteEstrategia]]:
    df_testes = _build_strategy_comparison_tests(df_base)
    registros = [
        AnaliseSegmentacaoBinarizadaTesteEstrategia(
            metric_name=str(row["metric_name"]),
            modelo_origem=str(row["modelo_origem"]),
            comparison_scope=str(row["comparison_scope"]),
            test_name=str(row["test_name"]),
            group_a=str(row["group_a"]),
            group_b=str(row["group_b"]),
            n_group_a=int(row["n_group_a"]),
            n_group_b=int(row["n_group_b"]),
            statistic=float(row["statistic"]),
            p_value=float(row["p_value"]),
            p_value_adjusted=float(row["p_value_adjusted"]),
            effect_size=float(row["effect_size"]) if pd.notna(row["effect_size"]) else None,
            effect_size_label=(
                str(row["effect_size_label"]) if pd.notna(row["effect_size_label"]) else None
            ),
            mean_group_a=float(row["mean_group_a"]),
            mean_group_b=float(row["mean_group_b"]),
            median_group_a=float(row["median_group_a"]),
            median_group_b=float(row["median_group_b"]),
            favored_group=str(row["favored_group"]) if pd.notna(row["favored_group"]) else None,
        )
        for row in df_testes.to_dict(orient="records")
    ]
    repo = (
        repository if repository is not None else AnaliseSegmentacaoBinarizadaTesteEstrategiaRepository()
    )
    repo.replace_all(registros)
    return df_testes, registros


def build_and_persist_analysis_segmentacao_binarizada_testes_tag_estrategia(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaTesteTagEstrategiaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaTesteTagEstrategia]]:
    df_testes = _build_tag_impact_tests_by_strategy(df_base)
    registros = [
        AnaliseSegmentacaoBinarizadaTesteTagEstrategia(
            metric_name=str(row["metric_name"]),
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
            tag_name=str(row["tag_name"]),
            comparison_scope=str(row["comparison_scope"]),
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
    repo = (
        repository
        if repository is not None
        else AnaliseSegmentacaoBinarizadaTesteTagEstrategiaRepository()
    )
    repo.replace_all(registros)
    return df_testes, registros


def build_and_persist_analysis_segmentacao_binarizada_interacao_tag_estrategia(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBinarizadaInteracaoTagEstrategiaRepository | None = None,
) -> tuple[pd.DataFrame, list[AnaliseSegmentacaoBinarizadaInteracaoTagEstrategia]]:
    df_interacoes = _build_tag_interactions_by_strategy(df_base)
    registros = [
        AnaliseSegmentacaoBinarizadaInteracaoTagEstrategia(
            estrategia_binarizacao=str(row["estrategia_binarizacao"]),
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
        else AnaliseSegmentacaoBinarizadaInteracaoTagEstrategiaRepository()
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


def _build_execution_stability_modelo_estrategia(df_base: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for metric_config in BINARIZED_METRIC_CONFIGS:
        per_execution = (
            df_base.groupby(["modelo", "estrategia_binarizacao", "execucao"], dropna=False)[
                metric_config.metric_name
            ]
            .mean()
            .reset_index(name="execution_mean")
        )
        for (model_name, strategy_name), group_df in per_execution.groupby(
            ["modelo", "estrategia_binarizacao"], dropna=False
        ):
            execution_means = group_df["execution_mean"].astype(float)
            mean_execucoes = float(execution_means.mean())
            std_execucoes = (
                float(execution_means.std(ddof=1)) if len(execution_means) > 1 else 0.0
            )
            cv_execucoes = (
                std_execucoes / abs(mean_execucoes) if mean_execucoes != 0.0 else 0.0
            )
            amplitude_execucoes = float(execution_means.max() - execution_means.min())
            ascending = not metric_config.higher_is_better
            ordered = group_df.sort_values("execution_mean", ascending=ascending)
            rows.append(
                {
                    "modelo": str(model_name),
                    "estrategia_binarizacao": str(strategy_name),
                    "metric_name": metric_config.metric_name,
                    "count_execucoes": int(group_df["execucao"].nunique()),
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


def _build_strategy_comparison_tests(df_base: pd.DataFrame) -> pd.DataFrame:
    strategy_base = df_base.copy()
    strategy_base["modelo_origem"] = strategy_base["modelo"]
    strategy_base["modelo"] = strategy_base["estrategia_binarizacao"]
    frames: list[pd.DataFrame] = []

    global_tests = build_model_comparison_tests(
        df_base=strategy_base.drop(columns=["modelo_origem"]),
        metric_configs=BINARIZED_METRIC_CONFIGS,
    )
    if not global_tests.empty:
        global_tests["modelo_origem"] = GLOBAL_SCOPE
        frames.append(global_tests)

    for model_name, model_df in strategy_base.groupby("modelo_origem", dropna=False):
        model_tests = build_model_comparison_tests(
            df_base=model_df.drop(columns=["modelo_origem"]),
            metric_configs=BINARIZED_METRIC_CONFIGS,
        )
        if model_tests.empty:
            continue
        model_tests["modelo_origem"] = str(model_name)
        frames.append(model_tests)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _build_tag_impact_tests_by_strategy(df_base: pd.DataFrame) -> pd.DataFrame:
    strategy_base = df_base.copy()
    strategy_base["modelo"] = strategy_base["estrategia_binarizacao"]
    result = build_tag_impact_tests(
        df_base=strategy_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
    )
    if result.empty:
        return result
    return result.rename(columns={"nome_modelo": "estrategia_binarizacao"})


def _build_tag_interactions_by_strategy(df_base: pd.DataFrame) -> pd.DataFrame:
    strategy_base = df_base.copy()
    strategy_base["modelo"] = strategy_base["estrategia_binarizacao"]
    result = build_model_tag_interactions(
        df_base=strategy_base,
        metric_configs=BINARIZED_METRIC_CONFIGS,
    )
    if result.empty:
        return result
    return result.rename(columns={"nome_modelo": "estrategia_binarizacao"})
