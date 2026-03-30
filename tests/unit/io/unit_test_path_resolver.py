from src.config import (
    IMAGES_DIR,
    INDICE_PATH,
    PREDICTED_MASKS_BINARY,
    PREDICTED_MASKS_RAW_DIR,
    SQLITE_PATH,
)
from src.io.path_resolver import PathResolver


def test_from_config_expoe_paths_esperados() -> None:
    resolver = PathResolver.from_config()

    assert resolver.images_dir == IMAGES_DIR
    assert resolver.indice_path == INDICE_PATH
    assert resolver.predicted_masks_raw_dir == PREDICTED_MASKS_RAW_DIR
    assert resolver.sqlite_path == SQLITE_PATH


def test_with_overrides_retorna_novo_resolvedor_sem_alterar_original() -> None:
    resolver = PathResolver.from_config()

    atualizado = resolver.with_overrides(
        predicted_masks_binary_dir="/tmp/predicted_masks_binary",
        sqlite_path="/tmp/bufalos.sqlite3",
    )

    assert atualizado.predicted_masks_binary_dir == "/tmp/predicted_masks_binary"
    assert atualizado.sqlite_path == "/tmp/bufalos.sqlite3"
    assert resolver.predicted_masks_binary_dir == PREDICTED_MASKS_BINARY
    assert resolver.sqlite_path == SQLITE_PATH


def test_caminho_mascara_avaliacao_usa_ground_truth_para_modelo_especial() -> None:
    resolver = PathResolver.from_config().with_overrides(
        ground_truth_binary_dir="/tmp/gt",
        predicted_masks_binary_dir="/tmp/pred_bin",
    )

    assert resolver.caminho_mascara_avaliacao("ground_truth", "bufalo_001") == (
        "/tmp/gt/bufalo_001.png"
    )
    assert resolver.caminho_mascara_avaliacao("u2netp", "bufalo_001") == (
        "/tmp/pred_bin/u2netp/bufalo_001.png"
    )
