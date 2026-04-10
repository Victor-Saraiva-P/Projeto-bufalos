import pandas as pd

from src.analysis import (
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao,
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    build_and_persist_analysis_segmentacao_bruta_resumo_tag,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
)


def _build_df_base() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "nome_arquivo": "a",
                "fazenda": "F1",
                "peso": 1.0,
                "modelo": "u2netp",
                "execucao": 1,
                "auprc": 0.9,
                "soft_dice": 0.8,
                "brier_score": 0.1,
                "tags": "multi_bufalos",
                "tags_sem_ok": "multi_bufalos",
                "num_tags_problema": 1,
                "tem_tag_problema": True,
                "grupo_dificuldade": "1_problema",
                "tag_ok": False,
                "tag_multi_bufalos": True,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": False,
                "tag_ocluido": False,
            },
            {
                "nome_arquivo": "b",
                "fazenda": "F1",
                "peso": 2.0,
                "modelo": "u2netp",
                "execucao": 2,
                "auprc": 0.7,
                "soft_dice": 0.6,
                "brier_score": 0.2,
                "tags": "",
                "tags_sem_ok": "",
                "num_tags_problema": 0,
                "tem_tag_problema": False,
                "grupo_dificuldade": "nao_revisada",
                "tag_ok": False,
                "tag_multi_bufalos": False,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": False,
                "tag_ocluido": False,
            },
        ]
    )


def test_build_and_persist_analysis_segmentacao_bruta_resumo_modelo_grava_resumo(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaResumoModeloRepository(sqlite_path)

    df_resumo, registros = build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
        df_base=_build_df_base(),
        repository=repository,
    )

    assert len(df_resumo) == 3
    assert len(registros) == 3
    persistidos = repository.list(nome_modelo="u2netp")
    assert len(persistidos) == 3
    auprc = next(registro for registro in persistidos if registro.metric_name == "auprc")
    assert auprc.mean == 0.8
    assert auprc.higher_is_better is True


def test_build_and_persist_analysis_segmentacao_bruta_resumo_execucao_grava_resumo(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaResumoExecucaoRepository(sqlite_path)

    df_resumo, registros = build_and_persist_analysis_segmentacao_bruta_resumo_execucao(
        df_base=_build_df_base(),
        repository=repository,
    )

    assert len(df_resumo) == 6
    assert len(registros) == 6
    persistidos = repository.list(nome_modelo="u2netp", execucao=1)
    assert len(persistidos) == 3


def test_build_and_persist_analysis_segmentacao_bruta_resumo_tag_grava_resumo(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaResumoTagRepository(sqlite_path)

    df_resumo, registros = build_and_persist_analysis_segmentacao_bruta_resumo_tag(
        df_base=_build_df_base(),
        repository=repository,
    )

    assert len(df_resumo) == 21
    assert len(registros) == 21
    persistidos = repository.list(
        nome_modelo="u2netp",
        tag_name="tag_multi_bufalos",
        tag_value=True,
    )
    assert len(persistidos) == 3
