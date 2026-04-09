import pandas as pd

from src.analysis import (
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    persist_analysis_segmentacao_bruta_base,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaBaseRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
)


def test_persist_analysis_segmentacao_bruta_base_grava_dataframe_no_sqlite(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaBaseRepository(sqlite_path)
    df_base = pd.DataFrame(
        [
            {
                "nome_arquivo": "1166_Calcula_506",
                "fazenda": "Calcula",
                "peso": 506.0,
                "modelo": "u2netp",
                "execucao": 1,
                "auprc": 0.91,
                "soft_dice": 0.83,
                "brier_score": 0.07,
                "tags": "baixo_contraste",
                "tags_sem_ok": "baixo_contraste",
                "num_tags_problema": 1,
                "tem_tag_problema": True,
                "grupo_dificuldade": "1_problema",
                "tag_ok": False,
                "tag_multi_bufalos": False,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": True,
                "tag_ocluido": False,
            }
        ]
    )

    persist_analysis_segmentacao_bruta_base(df_base, repository)
    registros = repository.list()

    assert len(registros) == 1
    assert registros[0].nome_modelo == "u2netp"
    assert registros[0].tag_baixo_contraste is True


def test_build_and_persist_analysis_segmentacao_bruta_resumo_modelo_grava_resumo(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaResumoModeloRepository(sqlite_path)
    df_base = pd.DataFrame(
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

    df_resumo, registros = build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
        df_base=df_base,
        repository=repository,
    )

    assert len(df_resumo) == 3
    assert len(registros) == 3
    persistidos = repository.list(nome_modelo="u2netp")
    assert len(persistidos) == 3
    auprc = next(registro for registro in persistidos if registro.metric_name == "auprc")
    assert auprc.mean == 0.8
    assert auprc.higher_is_better is True
