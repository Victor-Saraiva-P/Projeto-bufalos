from pathlib import Path
import shutil

from src.analysis.collector import MetricsCollector
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES
from src.repositories import (
    AnaliseSegmentacaoBrutaBaseRepository,
    ImagemRepository,
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


def test_metrics_collector_persiste_analise_segmentacao_bruta_base_no_sqlite(
    tmp_path: Path,
) -> None:
    sqlite_fixture = Path("tests/mock_generated/bufalos-avaliacao.sqlite3")
    sqlite_path = tmp_path / "bufalos-avaliacao.sqlite3"
    shutil.copy2(sqlite_fixture, sqlite_path)

    imagem_repository = ImagemRepository(str(sqlite_path))
    base_repository = AnaliseSegmentacaoBrutaBaseRepository(str(sqlite_path))
    collector = MetricsCollector(
        force_recalculate=False,
        imagem_repository=imagem_repository,
        avaliacao_controller=FalhaSeRecalcularAvaliacaoController(),
    )

    df = collector.persist_analysis_segmentacao_bruta_base(base_repository)
    registros = base_repository.list()

    assert len(registros) == len(df)
    assert {registro.nome_modelo for registro in registros} == set(MODELOS_PARA_AVALIACAO)
    assert {registro.execucao for registro in registros} == set(
        range(1, NUM_EXECUCOES + 1)
    )
    assert any(registro.grupo_dificuldade for registro in registros)
