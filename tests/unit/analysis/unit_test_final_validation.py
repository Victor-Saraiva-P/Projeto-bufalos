import pandas as pd

from src.analysis import (
    BINARIZED_METRIC_CONFIGS,
    build_finalist_base,
    build_threshold_decision_table,
    select_best_strategies_for_models,
    select_top_models_for_final_validation,
)


def test_select_top_models_for_final_validation_filtra_por_cenario() -> None:
    df_rankings = pd.DataFrame(
        [
            {"scenario_key": "apenas_ok", "scenario_rank": 2, "modelo": "m2"},
            {"scenario_key": "apenas_ok", "scenario_rank": 1, "modelo": "m1"},
            {"scenario_key": "apenas_ok", "scenario_rank": 3, "modelo": "m3"},
            {"scenario_key": "dataset_completo", "scenario_rank": 1, "modelo": "mx"},
        ]
    )

    result = select_top_models_for_final_validation(
        df_rankings,
        scenario_key="apenas_ok",
        top_n=2,
    )

    assert result["modelo"].tolist() == ["m1", "m2"]


def test_select_best_strategies_for_models_pega_rank_1_por_modelo() -> None:
    df_rankings = pd.DataFrame(
        [
            {
                "scenario_key": "apenas_ok",
                "modelo": "m1",
                "estrategia_binarizacao": "e1",
                "strategy_rank_within_model": 1,
            },
            {
                "scenario_key": "apenas_ok",
                "modelo": "m1",
                "estrategia_binarizacao": "e2",
                "strategy_rank_within_model": 2,
            },
            {
                "scenario_key": "apenas_ok",
                "modelo": "m2",
                "estrategia_binarizacao": "e3",
                "strategy_rank_within_model": 1,
            },
        ]
    )

    result = select_best_strategies_for_models(
        df_rankings,
        ["m1", "m2"],
        scenario_key="apenas_ok",
    )

    assert result["estrategia_binarizacao"].tolist() == ["e1", "e3"]


def test_build_threshold_decision_table_aprova_somente_quando_todas_passam() -> None:
    df_finalists = pd.DataFrame(
        [
            {
                "combo": "m1|e1",
                "iou": 0.98,
                "precision": 0.991,
                "recall": 0.986,
                "area_similarity": 0.991,
                "perimetro_similarity": 0.961,
            },
            {
                "combo": "m2|e2",
                "iou": 0.969,
                "precision": 0.991,
                "recall": 0.986,
                "area_similarity": 0.991,
                "perimetro_similarity": 0.961,
            },
        ]
    )
    thresholds = {
        "iou": 0.97,
        "precision": 0.99,
        "recall": 0.985,
        "area_similarity": 0.99,
        "perimetro_similarity": 0.96,
    }

    result = build_threshold_decision_table(
        df_finalists,
        thresholds,
        BINARIZED_METRIC_CONFIGS,
    )

    assert result["aprovado"].tolist() == [True, False]
    assert result.loc[result["combo"] == "m2|e2", "metricas_reprovadas"].iloc[0] == "iou"


def test_build_finalist_base_filtra_combinacoes() -> None:
    df_base = pd.DataFrame(
        [
            {"modelo": "m1", "estrategia_binarizacao": "e1", "iou": 0.9},
            {"modelo": "m1", "estrategia_binarizacao": "e2", "iou": 0.8},
            {"modelo": "m2", "estrategia_binarizacao": "e3", "iou": 0.7},
        ]
    )
    finalists = pd.DataFrame(
        [
            {"modelo": "m1", "estrategia_binarizacao": "e1"},
            {"modelo": "m2", "estrategia_binarizacao": "e3"},
        ]
    )

    result = build_finalist_base(df_base, finalists)

    assert result[["modelo", "estrategia_binarizacao"]].to_dict("records") == [
        {"modelo": "m1", "estrategia_binarizacao": "e1"},
        {"modelo": "m2", "estrategia_binarizacao": "e3"},
    ]
