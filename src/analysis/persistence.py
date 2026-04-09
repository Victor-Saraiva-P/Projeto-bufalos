from __future__ import annotations

import pandas as pd

from src.analysis.descriptive_stats import RAW_METRIC_CONFIGS, build_descriptive_stats
from src.models import (
    AnaliseSegmentacaoBrutaBase,
    AnaliseSegmentacaoBrutaResumoModelo,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaBaseRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
)


def persist_analysis_segmentacao_bruta_base(
    df_base: pd.DataFrame,
    repository: AnaliseSegmentacaoBrutaBaseRepository | None = None,
) -> list[AnaliseSegmentacaoBrutaBase]:
    if df_base.empty:
        raise ValueError("DataFrame base está vazio.")

    registros = [
        AnaliseSegmentacaoBrutaBase(
            nome_arquivo=str(row["nome_arquivo"]),
            nome_modelo=str(row["modelo"]),
            execucao=int(row["execucao"]),
            fazenda=str(row["fazenda"]),
            peso=float(row["peso"]),
            auprc=float(row["auprc"]),
            soft_dice=float(row["soft_dice"]),
            brier_score=float(row["brier_score"]),
            tags=str(row["tags"]),
            tags_sem_ok=str(row["tags_sem_ok"]),
            num_tags_problema=int(row["num_tags_problema"]),
            tem_tag_problema=bool(row["tem_tag_problema"]),
            grupo_dificuldade=str(row["grupo_dificuldade"]),
            tag_ok=bool(row["tag_ok"]),
            tag_multi_bufalos=bool(row["tag_multi_bufalos"]),
            tag_cortado=bool(row["tag_cortado"]),
            tag_angulo_extremo=bool(row["tag_angulo_extremo"]),
            tag_baixo_contraste=bool(row["tag_baixo_contraste"]),
            tag_ocluido=bool(row["tag_ocluido"]),
        )
        for row in df_base.to_dict(orient="records")
    ]

    repo = repository if repository is not None else AnaliseSegmentacaoBrutaBaseRepository()
    repo.replace_all(registros)
    return registros


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
