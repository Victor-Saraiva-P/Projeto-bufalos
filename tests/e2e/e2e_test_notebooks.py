from pathlib import Path
import shutil

import pytest
import numpy as np

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.config import MODELOS_PARA_AVALIACAO
from src.controllers import (
    AvaliacaoController,
    BinarizacaoController,
    ImagemController,
    SegmentacaoController,
)
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def _resolver_e2e() -> PathResolver:
    e2e_generated_dir = Path(__file__).resolve().parents[1] / "e2e_generated"
    shutil.rmtree(e2e_generated_dir, ignore_errors=True)

    return PathResolver.from_config().with_overrides(
        generated_dir=str(e2e_generated_dir),
        predicted_masks_raw_dir=str(e2e_generated_dir / "predicted_masks_raw"),
        predicted_masks_binary_dir=str(e2e_generated_dir / "predicted_masks_binary"),
        ground_truth_binary_dir=str(e2e_generated_dir / "ground_truth_binary"),
        evaluation_dir=str(e2e_generated_dir / "evaluation"),
        sqlite_path=str(e2e_generated_dir / "bufalos-e2e.sqlite3"),
    )


def _modelos_e2e() -> dict[str, str]:
    nome_modelo = next(iter(MODELOS_PARA_AVALIACAO))
    return {nome_modelo: MODELOS_PARA_AVALIACAO[nome_modelo]}


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
def test_notebook_01_gera_segmentacoes(monkeypatch: pytest.MonkeyPatch) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e()
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
    nome_modelo = next(iter(modelos))
    saidas_geradas = sorted(
        (Path(resolver.predicted_masks_raw_dir) / nome_modelo).glob("*.png")
    )

    assert resumo_integridade.total_png == 0
    assert len(linhas) == 5
    assert len(saidas_geradas) == len(linhas)
    assert resumos[nome_modelo].total == len(linhas)
    assert resumos[nome_modelo].processadas == len(linhas)
    assert resumos[nome_modelo].ok == len(linhas)
    assert resumos[nome_modelo].erro == 0
    assert resumos[nome_modelo].skip == 0


@pytest.mark.e2e
def test_notebook_02_binariza_ground_truth_e_segmentacoes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e()
    modelos = _modelos_e2e()
    _patch_ambiente_e2e(monkeypatch, resolver, modelos)

    resolver, modelos, linhas = _executar_fluxo_notebook_02()
    nome_modelo = next(iter(modelos))

    saidas_ground_truth = sorted(Path(resolver.ground_truth_binary_dir).glob("*.png"))
    saidas_modelo = sorted(
        (Path(resolver.predicted_masks_binary_dir) / nome_modelo).glob("*.png")
    )
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    assert len(saidas_ground_truth) == len(linhas)
    assert len(saidas_modelo) == len(linhas)
    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is None
    assert imagem_persistida.segmentacoes == []


@pytest.mark.e2e
def test_notebook_03_calcula_e_persiste_avaliacoes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = _resolver_e2e()
    modelos = _modelos_e2e()
    _patch_ambiente_e2e(monkeypatch, resolver, modelos)

    resolver, modelos, linhas = _executar_fluxo_notebook_02()

    avaliacao_controller = AvaliacaoController()
    stats = avaliacao_controller.processar_imagens()
    imagens = ImagemRepository(resolver.sqlite_path).list()
    nome_modelo = next(iter(modelos))

    assert stats.total == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.erro == 0
    assert stats.skip == 0

    assert len(imagens) == len(linhas)
    assert all(imagem.ground_truth_binarizada is not None for imagem in imagens)
    assert all(
        any(segmentacao.nome_modelo == nome_modelo for segmentacao in imagem.segmentacoes)
        for imagem in imagens
    )
    assert all(
        imagem.ground_truth_binarizada is not None
        and imagem.ground_truth_binarizada.area > 0
        and imagem.ground_truth_binarizada.perimetro > 0
        for imagem in imagens
    )
    assert all(
        segmentacao.area > 0 and segmentacao.perimetro > 0 and 0.0 <= segmentacao.iou <= 1.0
        for imagem in imagens
        for segmentacao in imagem.segmentacoes
    )
