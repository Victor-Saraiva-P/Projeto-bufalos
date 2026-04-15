from __future__ import annotations

import pandas as pd

from src.analysis import (
    BINARIZED_METRIC_CONFIGS,
    RAW_METRIC_CONFIGS,
    SCENARIO_APENAS_OK,
    SCENARIO_CENARIO_IDEAL,
    SCENARIO_DATASET_COMPLETO,
    build_analysis_scenarios,
    build_best_entities_by_scenario,
    build_focus_model_strategy_rankings,
    build_negative_tag_impact_overview,
    build_scenario_rankings,
    identify_negative_impact_tags,
)


def _build_raw_df_base() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for indice in range(8):
        tem_baixo_contraste = indice < 4
        tem_ocluido = indice in {4, 5}
        rows.append(
            {
                "nome_arquivo": f"img_{indice}",
                "modelo": "modelo_a",
                "execucao": 1,
                "auprc": 0.55 if tem_baixo_contraste else 0.91,
                "soft_dice": 0.50 if tem_baixo_contraste else 0.89,
                "brier_score": 0.42 if tem_baixo_contraste else 0.11,
                "grupo_dificuldade": "1_problema" if tem_baixo_contraste else "ok",
                "tag_ok": not tem_baixo_contraste,
                "tag_baixo_contraste": tem_baixo_contraste,
                "tag_ocluido": tem_ocluido,
            }
        )
        rows.append(
            {
                "nome_arquivo": f"img_{indice}",
                "modelo": "modelo_b",
                "execucao": 1,
                "auprc": 0.60 if tem_baixo_contraste else 0.86,
                "soft_dice": 0.56 if tem_baixo_contraste else 0.83,
                "brier_score": 0.35 if tem_baixo_contraste else 0.15,
                "grupo_dificuldade": "1_problema" if tem_baixo_contraste else "ok",
                "tag_ok": not tem_baixo_contraste,
                "tag_baixo_contraste": tem_baixo_contraste,
                "tag_ocluido": tem_ocluido,
            }
        )
    return pd.DataFrame(rows)


def _build_binarized_df_base() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for indice in range(6):
        tem_baixo_contraste = indice < 3
        tem_ocluido = indice == 3
        for estrategia, iou_base in (
            ("OtsuOpeningBaixa", 0.90),
            ("LimiarFixoAlta", 0.83),
        ):
            rows.append(
                {
                    "nome_arquivo": f"img_{indice}",
                    "modelo": "modelo_a",
                    "execucao": 1,
                    "estrategia_binarizacao": estrategia,
                    "iou": iou_base - (0.08 if tem_baixo_contraste else 0.0),
                    "precision": (0.92 if estrategia == "OtsuOpeningBaixa" else 0.95)
                    - (0.04 if tem_baixo_contraste else 0.0),
                    "recall": (0.94 if estrategia == "OtsuOpeningBaixa" else 0.84)
                    - (0.07 if tem_baixo_contraste else 0.0),
                    "area_similarity": (0.93 if estrategia == "OtsuOpeningBaixa" else 0.86)
                    - (0.08 if tem_baixo_contraste else 0.0),
                    "perimetro_similarity": (
                        0.89 if estrategia == "OtsuOpeningBaixa" else 0.85
                    )
                    - (0.03 if tem_baixo_contraste else 0.0),
                    "grupo_dificuldade": "1_problema" if tem_baixo_contraste else "ok",
                    "tag_ok": not tem_baixo_contraste,
                    "tag_baixo_contraste": tem_baixo_contraste,
                    "tag_ocluido": tem_ocluido,
                }
            )
    return pd.DataFrame(rows)


def test_build_negative_tag_impact_overview_marca_tags_negativas_significativas() -> None:
    df_base = _build_raw_df_base()

    result = build_negative_tag_impact_overview(df_base=df_base, metric_configs=RAW_METRIC_CONFIGS)

    assert not result.empty
    baixo_contraste = result.loc[result["tag_name"] == "tag_baixo_contraste"]
    assert (baixo_contraste["impacto_negativo_significativo"]).all()
    assert (baixo_contraste["impact_direction"] == "piora").all()

    ocluido = result.loc[result["tag_name"] == "tag_ocluido"]
    assert not ocluido.empty
    assert not ocluido["impacto_negativo_significativo"].any()


def test_identify_negative_impact_tags_retorna_apenas_tags_negativas() -> None:
    df_base = _build_raw_df_base()

    result = identify_negative_impact_tags(df_base=df_base, metric_configs=RAW_METRIC_CONFIGS)

    assert result == ["tag_baixo_contraste"]


def test_build_analysis_scenarios_constroi_tres_recortes() -> None:
    df_base = _build_raw_df_base()

    result = build_analysis_scenarios(
        df_base=df_base,
        ideal_allowed_tags=["ocluido"],
    )

    assert [item.scenario_key for item in result] == [
        SCENARIO_DATASET_COMPLETO,
        SCENARIO_CENARIO_IDEAL,
        SCENARIO_APENAS_OK,
    ]
    assert len(result[0].df) == 16
    assert len(result[1].df) == 8
    assert len(result[2].df) == 8
    assert set(result[1].df["tag_ocluido"].unique()) == {False, True}
    assert set(result[1].df["tag_baixo_contraste"].unique()) == {False}


def test_build_scenario_rankings_gera_melhor_modelo_por_cenario() -> None:
    df_base = _build_raw_df_base()

    result = build_scenario_rankings(
        df_base=df_base,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo"],
        ideal_allowed_tags=["ocluido"],
        primary_metric="auprc",
    )

    assert not result.empty
    assert set(result["scenario_key"]).issubset(
        {
            SCENARIO_DATASET_COMPLETO,
            SCENARIO_CENARIO_IDEAL,
            SCENARIO_APENAS_OK,
        }
    )
    assert {
        SCENARIO_CENARIO_IDEAL,
        SCENARIO_APENAS_OK,
    }.issubset(set(result["scenario_key"]))
    dataset_best = result.loc[
        (result["scenario_key"] == SCENARIO_DATASET_COMPLETO)
        & (result["scenario_rank"] == 1),
        "modelo",
    ].item()
    ideal_best = result.loc[
        (result["scenario_key"] == SCENARIO_CENARIO_IDEAL)
        & (result["scenario_rank"] == 1),
        "modelo",
    ].item()

    assert dataset_best == "modelo_b"
    assert ideal_best == "modelo_a"


def test_build_best_entities_by_scenario_filtra_apenas_topo() -> None:
    df_base = _build_raw_df_base()

    result = build_best_entities_by_scenario(
        df_base=df_base,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo"],
        ideal_allowed_tags=["ocluido"],
        primary_metric="auprc",
    )

    assert len(result) == 3
    assert set(result["scenario_key"]) == {
        SCENARIO_DATASET_COMPLETO,
        SCENARIO_CENARIO_IDEAL,
        SCENARIO_APENAS_OK,
    }


def test_build_focus_model_strategy_rankings_restringe_ao_melhor_modelo_bruto() -> None:
    df_base_raw = _build_raw_df_base()
    melhores_modelos = build_best_entities_by_scenario(
        df_base=df_base_raw,
        metric_configs=RAW_METRIC_CONFIGS,
        group_by=["modelo"],
        ideal_allowed_tags=["ocluido"],
        primary_metric="auprc",
    )

    df_base_binarizada = _build_binarized_df_base()
    result = build_focus_model_strategy_rankings(
        df_base_binarizada=df_base_binarizada,
        best_models_by_scenario=melhores_modelos,
        metric_configs=BINARIZED_METRIC_CONFIGS,
        ideal_allowed_tags=["ocluido"],
        primary_metric="iou",
    )

    assert not result.empty
    assert set(result["scenario_key"]).issubset(
        {
            SCENARIO_DATASET_COMPLETO,
            SCENARIO_CENARIO_IDEAL,
            SCENARIO_APENAS_OK,
        }
    )
    assert {
        SCENARIO_CENARIO_IDEAL,
        SCENARIO_APENAS_OK,
    }.issubset(set(result["scenario_key"]))
    assert set(result["modelo_foco"]).issubset({"modelo_a", "modelo_b"})
    tops = result.loc[result["scenario_rank"] == 1, ["scenario_key", "estrategia_binarizacao"]]
    assert set(tops["estrategia_binarizacao"]) == {"OtsuOpeningBaixa"}
