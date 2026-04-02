from pathlib import Path

import numpy as np
from PIL import Image

from src.io.mask_utils import carregar_score_mask_predita
from src.io.path_resolver import PathResolver


def test_carregar_score_mask_predita_normaliza_mascara_8bit_para_probabilidade(
    tmp_path: Path,
) -> None:
    resolver = _criar_path_resolver(tmp_path)
    caminho = Path(resolver.caminho_segmentacao_bruta("u2netp", "bufalo_001", execucao=1))
    caminho.parent.mkdir(parents=True, exist_ok=True)

    Image.fromarray(
        np.array([[255, 128], [64, 0]], dtype=np.uint8),
        mode="L",
    ).save(caminho)

    score_mask = carregar_score_mask_predita(
        "bufalo_001",
        "u2netp",
        execucao=1,
        path_resolver=resolver,
    )

    esperado = np.array([[1.0, 128 / 255], [64 / 255, 0.0]], dtype=np.float64)
    assert score_mask.dtype == np.float64
    assert np.allclose(score_mask, esperado)


def test_carregar_score_mask_predita_normaliza_mascara_escura_sem_confundir_com_probabilidade(
    tmp_path: Path,
) -> None:
    resolver = _criar_path_resolver(tmp_path)
    caminho = Path(resolver.caminho_segmentacao_bruta("u2netp", "bufalo_001", execucao=1))
    caminho.parent.mkdir(parents=True, exist_ok=True)

    Image.fromarray(
        np.array([[1, 0], [0, 1]], dtype=np.uint8),
        mode="L",
    ).save(caminho)

    score_mask = carregar_score_mask_predita(
        "bufalo_001",
        "u2netp",
        execucao=1,
        path_resolver=resolver,
    )

    esperado = np.array([[1 / 255, 0.0], [0.0, 1 / 255]], dtype=np.float64)
    assert np.allclose(score_mask, esperado)


def _criar_path_resolver(tmp_path: Path) -> PathResolver:
    base_dir = tmp_path / "dados"
    return PathResolver.from_config().with_overrides(
        data_dir=str(base_dir),
        generated_dir=str(base_dir / "generated"),
        images_dir=str(base_dir / "images"),
        ground_truth_brutos_dir=str(base_dir / "ground_truth_brutos"),
        segmentacoes_brutas_dir=str(base_dir / "segmentacoes_brutas"),
        segmentacoes_binarizadas_dir=str(base_dir / "segmentacoes_binarizadas"),
        ground_truth_binarizada_dir=str(base_dir / "ground_truth_binarizada"),
        evaluation_dir=str(base_dir / "evaluation"),
        indice_path=str(base_dir / "indice.csv"),
        sqlite_path=str(base_dir / "bufalos.sqlite3"),
    )
