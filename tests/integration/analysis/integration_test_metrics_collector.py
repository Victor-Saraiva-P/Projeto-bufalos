from pathlib import Path
import shutil

from src.analysis.collector import MetricsCollector
from src.analysis import (
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao,
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    build_and_persist_analysis_segmentacao_bruta_resumo_tag,
)
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES
from src.repositories import (
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    ImagemRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
)


class FalhaSeRecalcularAvaliacaoController:
    def processar_imagem(self, *args, **kwargs):
        raise AssertionError("MetricsCollector nao deveria recalcular metricas nesse cenario.")


def test_metrics_collector_carrega_metricas_do_sqlite_versionado(tmp_path: Path) -> None:
    sqlite_fixture = Path("tests/mock_generated/bufalos-avaliacao.sqlite3")
    sqlite_path = tmp_path / "bufalos-avaliacao.sqlite3"
    shutil.copy2(sqlite_fixture, sqlite_path)

    imagem_repository = ImagemRepository(str(sqlite_path))
    collector = MetricsCollector(
        force_recalculate=False,
        imagem_repository=imagem_repository,
        avaliacao_controller=FalhaSeRecalcularAvaliacaoController(),
    )

    df = collector.collect_all_metrics()

    assert len(df) == (
        len(imagem_repository.list())
        * NUM_EXECUCOES
        * len(MODELOS_PARA_AVALIACAO)
    )
    assert set(df["modelo"]) == set(MODELOS_PARA_AVALIACAO)
    assert set(df["execucao"]) == set(range(1, NUM_EXECUCOES + 1))


def test_metrics_collector_persiste_resumos_analiticos_no_sqlite(
    tmp_path: Path,
) -> None:
    sqlite_fixture = Path("tests/mock_generated/bufalos-avaliacao.sqlite3")
    sqlite_path = tmp_path / "bufalos-avaliacao.sqlite3"
    shutil.copy2(sqlite_fixture, sqlite_path)

    imagem_repository = ImagemRepository(str(sqlite_path))
    resumo_modelo_repository = AnaliseSegmentacaoBrutaResumoModeloRepository(
        str(sqlite_path)
    )
    resumo_execucao_repository = AnaliseSegmentacaoBrutaResumoExecucaoRepository(
        str(sqlite_path)
    )
    resumo_tag_repository = AnaliseSegmentacaoBrutaResumoTagRepository(str(sqlite_path))
    collector = MetricsCollector(
        force_recalculate=False,
        imagem_repository=imagem_repository,
        avaliacao_controller=FalhaSeRecalcularAvaliacaoController(),
    )

    df = collector.collect_all_metrics()
    df_resumo_modelo, _ = build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
        df_base=df,
        repository=resumo_modelo_repository,
    )
    df_resumo_execucao, _ = build_and_persist_analysis_segmentacao_bruta_resumo_execucao(
        df_base=df,
        repository=resumo_execucao_repository,
    )
    df_resumo_tag, _ = build_and_persist_analysis_segmentacao_bruta_resumo_tag(
        df_base=df,
        repository=resumo_tag_repository,
    )

    registros_modelo = resumo_modelo_repository.list()
    registros_execucao = resumo_execucao_repository.list()
    registros_tag = resumo_tag_repository.list()

    assert len(df_resumo_modelo) == len(registros_modelo)
    assert len(df_resumo_execucao) == len(registros_execucao)
    assert len(df_resumo_tag) == len(registros_tag)
    assert {registro.nome_modelo for registro in registros_modelo} == set(
        MODELOS_PARA_AVALIACAO
    )
    assert {registro.execucao for registro in registros_execucao} == set(
        range(1, NUM_EXECUCOES + 1)
    )
    assert {registro.metric_name for registro in registros_tag} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }
