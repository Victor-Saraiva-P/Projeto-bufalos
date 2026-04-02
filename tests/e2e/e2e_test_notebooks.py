from pathlib import Path

import pytest
import numpy as np

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.config import MODELOS_PARA_AVALIACAO, NUM_EXECUCOES
from src.controllers import (
    AvaliacaoController,
    BinarizacaoController,
    ImagemController,
    SegmentacaoController,
)
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def _resolver_e2e(tmp_path: Path) -> PathResolver:
    e2e_generated_dir = tmp_path / "e2e_generated"

    return PathResolver.from_config().with_overrides(
        generated_dir=str(e2e_generated_dir),
        segmentacoes_brutas_dir=str(e2e_generated_dir / "segmentacoes_brutas"),
        segmentacoes_binarizadas_dir=str(
            e2e_generated_dir / "segmentacoes_binarizadas"
        ),
        ground_truth_binarizada_dir=str(e2e_generated_dir / "ground_truth_binarizada"),
        evaluation_dir=str(e2e_generated_dir / "evaluation"),
        sqlite_path=str(e2e_generated_dir / "bufalos-e2e.sqlite3"),
    )


def _modelos_e2e() -> dict[str, str]:
    return dict(MODELOS_PARA_AVALIACAO)


def _iterar_execucoes() -> range:
    return range(1, NUM_EXECUCOES + 1)


def _patch_ambiente_e2e(
    monkeypatch: pytest.MonkeyPatch,
    resolver: PathResolver,
    modelos: dict[str, str],
) -> None:
    monkeypatch.setattr(
        "src.controllers.imagem_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.PathResolver.from_config",
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
        "src.controllers.segmentacao_controller.MODELOS_PARA_AVALIACAO",
        modelos,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        modelos,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        modelos,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.CHAIN_APPROX_NONE",
        1,
        raising=False,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.findContours",
        _fake_find_contours,
        raising=False,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.arcLength",
        _fake_arc_length,
        raising=False,
    )


def _fake_find_contours(mask: np.ndarray, _mode: int, _method: int):
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return [], None

    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    contour = np.array(
        [
            [[x_min, y_min]],
            [[x_max, y_min]],
            [[x_max, y_max]],
            [[x_min, y_max]],
        ],
        dtype=np.int32,
    )
    return [contour], None


def _fake_arc_length(contour: np.ndarray, closed: bool = True) -> float:
    pontos = contour.reshape(-1, 2)
    if len(pontos) < 2:
        return 0.0

    deslocamentos = pontos[1:] - pontos[:-1]
    perimetro = float(np.linalg.norm(deslocamentos, axis=1).sum())
    if closed:
        perimetro += float(np.linalg.norm(pontos[0] - pontos[-1]))
    return perimetro


def _executar_fluxo_notebook_01() -> tuple[PathResolver, dict[str, str], list]:
    imagem_controller = ImagemController()
    imagem_controller.sincronizar_indice_excel()
    imagem_controller.verificar_pngs_corrompidos()

    segmentacao_controller = SegmentacaoController()
    linhas = segmentacao_controller.imagem_repository.list()
    try:
        segmentacao_controller.processar_imagens()
    except Exception as erro:
        pytest.skip(f"Ambiente sem suporte para executar rembg real: {erro}")

    return segmentacao_controller.path_resolver, _modelos_e2e(), linhas


def _executar_fluxo_notebook_02() -> tuple[PathResolver, dict[str, str], list]:
    resolver, modelos, linhas = _executar_fluxo_notebook_01()

    imagem_controller = ImagemController()
    imagem_controller.verificar_segmentacoes()

    strategy = GaussianOpeningBinarizationStrategy()
    binarizacao_controller = BinarizacaoController()
    binarizacao_controller.processar_ground_truth(strategy=strategy)
    binarizacao_controller.processar_segmentacoes(strategy=strategy)

    return resolver, modelos, linhas


@pytest.mark.e2e
def test_notebook_01_gera_segmentacoes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e(tmp_path)
    modelos = _modelos_e2e()
    _patch_ambiente_e2e(monkeypatch, resolver, modelos)

    imagem_controller = ImagemController()
    imagem_controller.sincronizar_indice_excel()
    resumo_integridade = imagem_controller.verificar_pngs_corrompidos()

    segmentacao_controller = SegmentacaoController()
    try:
        resumos = segmentacao_controller.processar_imagens()
    except Exception as erro:
        pytest.skip(f"Ambiente sem suporte para executar rembg real: {erro}")
    linhas = ImagemRepository(resolver.sqlite_path).list()
    saidas_por_modelo_execucao = {
        (nome_modelo, execucao): sorted(
            (
                Path(resolver.segmentacoes_brutas_dir)
                / f"execucao_{execucao}"
                / nome_modelo
            ).glob("*.png")
        )
        for nome_modelo in modelos
        for execucao in _iterar_execucoes()
    }

    assert resumo_integridade.total_png == 0
    assert len(linhas) == 5
    assert set(resumos) == set(modelos)
    for nome_modelo in modelos:
        assert resumos[nome_modelo].total == len(linhas) * NUM_EXECUCOES
        assert resumos[nome_modelo].processadas == len(linhas) * NUM_EXECUCOES
        assert resumos[nome_modelo].ok == len(linhas) * NUM_EXECUCOES
        assert resumos[nome_modelo].erro == 0
        assert resumos[nome_modelo].skip == 0
    assert all(
        len(saidas) == len(linhas) for saidas in saidas_por_modelo_execucao.values()
    )


@pytest.mark.e2e
def test_notebook_02_binariza_ground_truth_e_segmentacoes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e(tmp_path)
    modelos = _modelos_e2e()
    _patch_ambiente_e2e(monkeypatch, resolver, modelos)

    resolver, modelos, linhas = _executar_fluxo_notebook_02()
    strategy = GaussianOpeningBinarizationStrategy()

    saidas_ground_truth = sorted(Path(resolver.ground_truth_binarizada_dir).glob("*.png"))
    saidas_por_modelo_execucao = {
        (nome_modelo, execucao): sorted(
            (
                Path(resolver.segmentacoes_binarizadas_dir)
                / f"execucao_{execucao}"
                / strategy.nome_pasta
                / nome_modelo
            ).glob("*.png")
        )
        for nome_modelo in modelos
        for execucao in _iterar_execucoes()
    }
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    assert len(saidas_ground_truth) == len(linhas)
    assert all(
        len(saidas) == len(linhas) for saidas in saidas_por_modelo_execucao.values()
    )
    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is None
    assert imagem_persistida.segmentacoes_brutas == []


@pytest.mark.e2e
def test_notebook_03_calcula_e_persiste_avaliacoes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e(tmp_path)
    modelos = _modelos_e2e()
    _patch_ambiente_e2e(monkeypatch, resolver, modelos)

    resolver, modelos, linhas = _executar_fluxo_notebook_02()

    avaliacao_controller = AvaliacaoController()
    stats = avaliacao_controller.processar_imagens()
    imagens = ImagemRepository(resolver.sqlite_path).list()
    pares_esperados = {
        (nome_modelo, execucao)
        for nome_modelo in modelos
        for execucao in _iterar_execucoes()
    }

    assert stats.total == len(linhas) * len(_iterar_execucoes())
    assert stats.ok == len(linhas) * len(_iterar_execucoes())
    assert stats.erro == 0
    assert stats.skip == 0

    assert len(imagens) == len(linhas)
    assert all(imagem.ground_truth_binarizada is not None for imagem in imagens)
    assert all(
        {
            (segmentacao_bruta.nome_modelo, segmentacao_bruta.execucao)
            for segmentacao_bruta in imagem.segmentacoes_brutas
        }
        == pares_esperados
        for imagem in imagens
    )
    assert all(
        imagem.ground_truth_binarizada is not None
        and imagem.ground_truth_binarizada.area > 0
        and imagem.ground_truth_binarizada.perimetro > 0
        for imagem in imagens
    )
    assert all(
        segmentacao_binarizada.area > 0
        and segmentacao_binarizada.perimetro > 0
        and 0.0 <= segmentacao_binarizada.iou <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
        for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
    )
    assert all(
        0.0 <= segmentacao_bruta.auprc <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )
    assert all(
        any(
            segmentacao_binarizada.estrategia_binarizacao
            == AvaliacaoController.ESTRATEGIA_BINARIZACAO_PADRAO
            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
        )
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )
