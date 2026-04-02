from pathlib import Path

import pytest

from src.analysis.collector import MetricsCollector
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES, SEGMENTACAO_BINARIZATION_STRATEGIES
from src.controllers import AvaliacaoController, BinarizacaoController, ImagemController
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def test_avaliacao_controller_processa_pipeline_e_persiste_soft_dice(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada_modelos = Path("tests/mock_generated/segmentacoes_brutas")
    saida_modelos = tmp_path / "segmentacoes_binarizadas"
    saida_ground_truth = tmp_path / "ground_truth_binarizada"
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
        segmentacoes_brutas_dir=str(entrada_modelos),
        segmentacoes_binarizadas_dir=str(saida_modelos),
        ground_truth_binarizada_dir=str(saida_ground_truth),
        sqlite_path=sqlite_path,
    )

    monkeypatch.setattr(
        "src.controllers.imagem_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        MODELOS_PARA_AVALIACAO,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        MODELOS_PARA_AVALIACAO,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.NUM_EXECUCOES",
        NUM_EXECUCOES,
    )

    ImagemController().sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    BinarizacaoController().processar_ground_truth_configurada(imagens=linhas)
    BinarizacaoController().processar_segmentacoes_configuradas(imagens=linhas)

    stats = AvaliacaoController().processar_imagens(imagens=linhas)
    imagens = ImagemRepository(resolver.sqlite_path).list()
    df = MetricsCollector._build_metrics_dataframe(imagens)

    assert stats.total == len(linhas) * NUM_EXECUCOES * len(SEGMENTACAO_BINARIZATION_STRATEGIES)
    assert stats.ok == len(linhas) * NUM_EXECUCOES * len(SEGMENTACAO_BINARIZATION_STRATEGIES)
    assert stats.erro == 0
    assert stats.skip == 0
    assert all(imagem.ground_truth_binarizada is not None for imagem in imagens)
    assert all(
        0.0 <= segmentacao_bruta.auprc <= 1.0
        and 0.0 <= segmentacao_bruta.soft_dice <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )
    assert "soft_dice" in df.columns
    assert set(df["soft_dice"].between(0.0, 1.0)) == {True}
