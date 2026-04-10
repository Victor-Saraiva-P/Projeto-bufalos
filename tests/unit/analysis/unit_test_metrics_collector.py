from src.analysis.collector import MetricsCollector
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
    Tag,
)


def test_build_metrics_dataframe_inclui_metricas_brutas() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.tags = []
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=0.92,
        soft_dice=0.81,
        brier_score=0.08,
    )
    segmentacao.segmentacoes_binarizadas = [
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=90.0,
            perimetro=38.0,
            iou=0.8,
            precision=0.82,
            recall=0.78,
        ),
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="LimiarFixo",
            area=88.0,
            perimetro=36.0,
            iou=0.76,
            precision=0.8,
            recall=0.74,
        ),
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert list(df.columns) == [
        "nome_arquivo",
        "fazenda",
        "peso",
        "modelo",
        "execucao",
        "auprc",
        "soft_dice",
        "brier_score",
        "tags",
        "tags_sem_ok",
        "num_tags_problema",
        "tem_tag_problema",
        "grupo_dificuldade",
        "tag_ok",
        "tag_multi_bufalos",
        "tag_cortado",
        "tag_angulo_extremo",
        "tag_baixo_contraste",
        "tag_ocluido",
    ]
    assert len(df) == 1
    assert set(df["execucao"]) == {1}
    assert set(df["auprc"]) == {0.92}
    assert set(df["brier_score"]) == {0.08}
    assert set(df["soft_dice"]) == {0.81}
    assert df.iloc[0]["tags"] == ""
    assert df.iloc[0]["tags_sem_ok"] == ""
    assert df.iloc[0]["num_tags_problema"] == 0
    assert df.iloc[0]["tem_tag_problema"] == False
    assert df.iloc[0]["grupo_dificuldade"] == "nao_revisada"


def test_build_metrics_dataframe_inclui_flags_de_tags() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.tags = [Tag(nome_tag="multi_bufalos"), Tag(nome_tag="baixo_contraste")]
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    imagem.segmentacoes_brutas = [
        SegmentacaoBruta(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            auprc=0.92,
            soft_dice=0.81,
            brier_score=0.08,
        )
    ]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert df.iloc[0]["tags"] == "baixo_contraste,multi_bufalos"
    assert df.iloc[0]["tags_sem_ok"] == "baixo_contraste,multi_bufalos"
    assert df.iloc[0]["num_tags_problema"] == 2
    assert df.iloc[0]["tem_tag_problema"] == True
    assert df.iloc[0]["grupo_dificuldade"] == "2_ou_mais_problemas"
    assert df.iloc[0]["tag_multi_bufalos"] == True
    assert df.iloc[0]["tag_baixo_contraste"] == True
    assert df.iloc[0]["tag_ok"] == False
    assert df.iloc[0]["tag_cortado"] == False


def test_build_metrics_dataframe_descarta_segmentacao_sem_auprc_valido() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.tags = []
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=SegmentacaoBruta.AUPRC_NAO_CALCULADA,
        soft_dice=0.81,
        brier_score=0.08,
    )
    segmentacao.segmentacoes_binarizadas = [
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=90.0,
            perimetro=38.0,
            iou=0.8,
            precision=0.82,
            recall=0.78,
        )
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert df.empty


def test_build_metrics_dataframe_descarta_segmentacao_sem_soft_dice_valido() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.tags = []
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=0.92,
        soft_dice=SegmentacaoBruta.SOFT_DICE_NAO_CALCULADO,
        brier_score=0.08,
    )
    segmentacao.segmentacoes_binarizadas = [
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=90.0,
            perimetro=38.0,
            iou=0.8,
            precision=0.82,
            recall=0.78,
        )
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert df.empty


def test_build_metrics_dataframe_descarta_segmentacao_sem_brier_score_valido() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.tags = []
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=0.92,
        soft_dice=0.81,
        brier_score=SegmentacaoBruta.BRIER_SCORE_NAO_CALCULADO,
    )
    segmentacao.segmentacoes_binarizadas = [
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=90.0,
            perimetro=38.0,
            iou=0.8,
            precision=0.82,
            recall=0.78,
        )
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert df.empty
