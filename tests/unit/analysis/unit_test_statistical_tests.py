import pandas as pd

from src.analysis import (
    build_bootstrap_confidence_intervals,
    build_execution_stability,
    build_model_comparison_tests,
    build_model_tag_interactions,
    build_tag_impact_tests,
    cliffs_delta,
    cliffs_delta_label,
    holm_adjust,
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
                "auprc": 0.91,
                "soft_dice": 0.87,
                "brier_score": 0.08,
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
                "auprc": 0.90,
                "soft_dice": 0.85,
                "brier_score": 0.09,
                "tag_ok": False,
                "tag_multi_bufalos": False,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": True,
                "tag_ocluido": False,
            },
            {
                "nome_arquivo": "a",
                "fazenda": "F1",
                "peso": 1.0,
                "modelo": "isnet",
                "execucao": 1,
                "auprc": 0.72,
                "soft_dice": 0.69,
                "brier_score": 0.21,
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
                "modelo": "isnet",
                "execucao": 2,
                "auprc": 0.70,
                "soft_dice": 0.66,
                "brier_score": 0.23,
                "tag_ok": False,
                "tag_multi_bufalos": False,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": True,
                "tag_ocluido": False,
            },
            {
                "nome_arquivo": "a",
                "fazenda": "F1",
                "peso": 1.0,
                "modelo": "briarmbg",
                "execucao": 1,
                "auprc": 0.52,
                "soft_dice": 0.48,
                "brier_score": 0.35,
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
                "modelo": "briarmbg",
                "execucao": 2,
                "auprc": 0.50,
                "soft_dice": 0.46,
                "brier_score": 0.38,
                "tag_ok": False,
                "tag_multi_bufalos": False,
                "tag_cortado": False,
                "tag_angulo_extremo": False,
                "tag_baixo_contraste": True,
                "tag_ocluido": False,
            },
        ]
    )


def test_holm_adjust_aplica_correcao_monotona() -> None:
    adjusted = holm_adjust([0.01, 0.03, 0.04])
    assert adjusted == [0.03, 0.06, 0.06]


def test_cliffs_delta_e_rotulo_refletem_diferenca_entre_grupos() -> None:
    delta = cliffs_delta([0.9, 0.8, 0.85], [0.1, 0.2, 0.15])
    assert delta > 0.9
    assert cliffs_delta_label(delta) == "large"


def test_build_bootstrap_confidence_intervals_gera_faixas_por_modelo() -> None:
    df = build_bootstrap_confidence_intervals(
        df_base=_build_df_base(),
        n_resamples=100,
        random_state=7,
    )

    assert set(df["statistic_name"]) == {"mean", "median"}
    assert set(df["metric_name"]) == {"auprc", "soft_dice", "brier_score"}
    assert all(df["ci_low"] <= df["estimate"])
    assert all(df["estimate"] <= df["ci_high"])


def test_build_execution_stability_gera_cv_e_execucoes_extremas() -> None:
    df = build_execution_stability(_build_df_base())

    assert len(df) == 9
    registro = df.loc[
        (df["nome_modelo"] == "u2netp") & (df["metric_name"] == "auprc")
    ].iloc[0]
    assert registro["count_execucoes"] == 2
    assert registro["melhor_execucao"] in {1, 2}
    assert registro["pior_execucao"] in {1, 2}
    assert registro["cv_execucoes"] >= 0.0


def test_build_model_comparison_tests_gera_global_e_pairwise() -> None:
    df = build_model_comparison_tests(_build_df_base())

    assert not df.empty
    assert {"global", "pairwise"} <= set(df["comparison_scope"])
    assert {"kruskal_wallis", "dunn_holm"} <= set(df["test_name"])
    assert set(df["metric_name"]) == {"auprc", "soft_dice", "brier_score"}


def test_build_tag_impact_tests_gera_global_e_por_modelo() -> None:
    df = build_tag_impact_tests(_build_df_base())

    assert not df.empty
    assert {"global", "por_modelo"} <= set(df["comparison_scope"])
    assert set(df["test_name"]) == {"mann_whitney_u"}
    assert "tag_multi_bufalos" in set(df["tag_name"])


def test_build_model_tag_interactions_gera_deltas_ajustados() -> None:
    df = build_model_tag_interactions(_build_df_base())

    assert not df.empty
    registro = df.loc[
        (df["nome_modelo"] == "u2netp")
        & (df["metric_name"] == "brier_score")
        & (df["tag_name"] == "tag_multi_bufalos")
    ].iloc[0]
    assert registro["impact_direction"] in {"piora", "melhora", "neutro"}
    assert registro["higher_is_better"] == False
