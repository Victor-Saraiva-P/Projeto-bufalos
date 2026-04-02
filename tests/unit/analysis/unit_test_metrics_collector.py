from src.analysis.collector import MetricsCollector
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
)


def test_build_metrics_dataframe_inclui_auprc() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
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
        ),
        SegmentacaoBinarizada(
            nome_arquivo="bufalo_001",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="LimiarFixo",
            area=88.0,
            perimetro=36.0,
            iou=0.76,
        )
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert list(df.columns) == [
        "nome_arquivo",
        "modelo",
        "execucao",
        "estrategia_binarizacao",
        "area",
        "perimetro",
        "iou",
        "auprc",
        "area_gt",
        "perimetro_gt",
        "area_diff_abs",
        "area_similarity",
        "perimetro_diff_abs",
        "perimetro_similarity",
    ]
    assert len(df) == 2
    assert set(df["estrategia_binarizacao"]) == {"GaussianaOpening", "LimiarFixo"}
    assert set(df["execucao"]) == {1}
    assert set(df["auprc"]) == {0.92}


def test_build_metrics_dataframe_descarta_segmentacao_sem_auprc_valida() -> None:
    imagem = Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo="bufalo_001",
        area=100.0,
        perimetro=40.0,
    )
    segmentacao = SegmentacaoBruta(
        nome_arquivo="bufalo_001",
        nome_modelo="u2netp",
        execucao=1,
        auprc=-1.0,
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
        )
    ]
    imagem.segmentacoes_brutas = [segmentacao]

    df = MetricsCollector._build_metrics_dataframe([imagem])

    assert df.empty
