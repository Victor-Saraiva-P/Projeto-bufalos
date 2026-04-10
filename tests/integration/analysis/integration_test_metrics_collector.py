from pathlib import Path
import shutil

from src.analysis.collector import MetricsCollector
from src.analysis import (
    build_and_persist_analysis_segmentacao_bruta_estabilidade,
    build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo,
    build_and_persist_analysis_segmentacao_bruta_intervalo_confianca,
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao,
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    build_and_persist_analysis_segmentacao_bruta_resumo_tag,
    build_and_persist_analysis_segmentacao_bruta_testes_modelo,
    build_and_persist_analysis_segmentacao_bruta_testes_tag,
)
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES
from src.repositories import (
    AnaliseSegmentacaoBrutaEstabilidadeRepository,
    AnaliseSegmentacaoBrutaInteracaoTagModeloRepository,
    AnaliseSegmentacaoBrutaIntervaloConfiancaRepository,
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    ImagemRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
    AnaliseSegmentacaoBrutaTesteModeloRepository,
    AnaliseSegmentacaoBrutaTesteTagRepository,
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
    estabilidade_repository = AnaliseSegmentacaoBrutaEstabilidadeRepository(str(sqlite_path))
    intervalo_repository = AnaliseSegmentacaoBrutaIntervaloConfiancaRepository(
        str(sqlite_path)
    )
    teste_modelo_repository = AnaliseSegmentacaoBrutaTesteModeloRepository(
        str(sqlite_path)
    )
    teste_tag_repository = AnaliseSegmentacaoBrutaTesteTagRepository(str(sqlite_path))
    interacao_repository = AnaliseSegmentacaoBrutaInteracaoTagModeloRepository(
        str(sqlite_path)
    )
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
    df_estabilidade, _ = build_and_persist_analysis_segmentacao_bruta_estabilidade(
        df_base=df,
        repository=estabilidade_repository,
    )
    df_intervalos, _ = build_and_persist_analysis_segmentacao_bruta_intervalo_confianca(
        df_base=df,
        repository=intervalo_repository,
    )
    df_testes_modelo, _ = build_and_persist_analysis_segmentacao_bruta_testes_modelo(
        df_base=df,
        repository=teste_modelo_repository,
    )
    df_testes_tag, _ = build_and_persist_analysis_segmentacao_bruta_testes_tag(
        df_base=df,
        repository=teste_tag_repository,
    )
    df_interacoes, _ = build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo(
        df_base=df,
        repository=interacao_repository,
    )

    registros_modelo = resumo_modelo_repository.list()
    registros_execucao = resumo_execucao_repository.list()
    registros_tag = resumo_tag_repository.list()
    registros_estabilidade = estabilidade_repository.list()
    registros_intervalos = intervalo_repository.list()
    registros_testes_modelo = teste_modelo_repository.list()
    registros_testes_tag = teste_tag_repository.list()
    registros_interacoes = interacao_repository.list()

    assert len(df_resumo_modelo) == len(registros_modelo)
    assert len(df_resumo_execucao) == len(registros_execucao)
    assert len(df_resumo_tag) == len(registros_tag)
    assert len(df_estabilidade) == len(registros_estabilidade)
    assert len(df_intervalos) == len(registros_intervalos)
    assert len(df_testes_modelo) == len(registros_testes_modelo)
    assert len(df_testes_tag) == len(registros_testes_tag)
    assert len(df_interacoes) == len(registros_interacoes)
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
    assert {registro.metric_name for registro in registros_estabilidade} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }
    assert {registro.statistic_name for registro in registros_intervalos} == {
        "mean",
        "median",
    }
    assert {registro.tag_name for registro in registros_testes_tag}
    assert {registro.tag_name for registro in registros_interacoes}
