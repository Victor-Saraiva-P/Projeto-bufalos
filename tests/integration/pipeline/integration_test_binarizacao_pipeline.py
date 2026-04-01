from pathlib import Path

import pytest

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.config import MODELOS_PARA_AVALIACAO
from src.controllers import BinarizacaoController, ImagemController
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def test_binarizacao_controller_processa_ground_truth_e_gera_pngs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida_ground_truth = tmp_path / "ground_truth_binarizada"
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
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

    ImagemController().sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    stats = BinarizacaoController().processar_ground_truth(
        GaussianOpeningBinarizationStrategy(),
        imagens=linhas,
    )
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    saidas_geradas = sorted(saida_ground_truth.glob("*.png"))

    assert len(linhas) == 5
    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)
    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is None


def test_binarizacao_controller_processa_segmentacoes_e_gera_pngs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada_modelos = Path("tests/mock_generated/segmentacoes_brutas")
    saida_modelos = tmp_path / "segmentacoes_binarizadas"
    strategy = GaussianOpeningBinarizationStrategy()
    nome_modelo = next(iter(MODELOS_PARA_AVALIACAO))
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
        segmentacoes_brutas_dir=str(entrada_modelos),
        segmentacoes_binarizadas_dir=str(saida_modelos),
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
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        {nome_modelo: MODELOS_PARA_AVALIACAO[nome_modelo]},
    )

    ImagemController().sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()

    resumos = BinarizacaoController().processar_segmentacoes(
        strategy,
        imagens=linhas,
    )
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    saidas_geradas = sorted((saida_modelos / strategy.nome_pasta / nome_modelo).glob("*.png"))
    stats = resumos[nome_modelo]

    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)
    assert imagem_persistida is not None
    assert imagem_persistida.segmentacoes_brutas == []
