from src.config import (
    IMAGES_DIR,
    INDICE_PATH,
    SEGMENTACOES_BINARIZADAS_DIR,
    SEGMENTACOES_BRUTAS_DIR,
    SQLITE_PATH,
)
from src.io.path_resolver import PathResolver


def test_from_config_expoe_paths_esperados() -> None:
    resolver = PathResolver.from_config()

    assert resolver.images_dir == IMAGES_DIR
    assert resolver.indice_path == INDICE_PATH
    assert resolver.segmentacoes_brutas_dir == SEGMENTACOES_BRUTAS_DIR
    assert resolver.sqlite_path == SQLITE_PATH


def test_with_overrides_retorna_novo_resolvedor_sem_alterar_original() -> None:
    resolver = PathResolver.from_config()

    atualizado = resolver.with_overrides(
        segmentacoes_binarizadas_dir="/tmp/segmentacoes_binarizadas",
        sqlite_path="/tmp/bufalos.sqlite3",
    )

    assert atualizado.segmentacoes_binarizadas_dir == "/tmp/segmentacoes_binarizadas"
    assert atualizado.sqlite_path == "/tmp/bufalos.sqlite3"
    assert resolver.segmentacoes_binarizadas_dir == SEGMENTACOES_BINARIZADAS_DIR
    assert resolver.sqlite_path == SQLITE_PATH


def test_caminho_segmentacao_avaliacao_usa_ground_truth_para_modelo_especial() -> None:
    resolver = PathResolver.from_config().with_overrides(
        ground_truth_binarizada_dir="/tmp/gt",
        segmentacoes_binarizadas_dir="/tmp/seg_bin",
    )

    assert resolver.caminho_segmentacao_avaliacao("ground_truth", "bufalo_001") == (
        "/tmp/gt/bufalo_001.png"
    )
    assert resolver.caminho_segmentacao_avaliacao(
        "u2netp",
        "bufalo_001",
        execucao=1,
    ) == (
        "/tmp/seg_bin/execucao_1/GaussianaOpening/u2netp/bufalo_001.png"
    )


def test_caminho_segmentacao_binarizada_aceita_nome_binarizacao_explicitamente() -> None:
    resolver = PathResolver.from_config().with_overrides(
        segmentacoes_binarizadas_dir="/tmp/seg_bin",
    )

    assert resolver.caminho_segmentacao_binarizada(
        "u2netp",
        "bufalo_001",
        execucao=1,
        nome_binarizacao="MinhaBinarizacao",
    ) == "/tmp/seg_bin/execucao_1/MinhaBinarizacao/u2netp/bufalo_001.png"


def test_caminho_segmentacao_bruta_inclui_execucao() -> None:
    resolver = PathResolver.from_config().with_overrides(
        segmentacoes_brutas_dir="/tmp/seg_brutas",
    )

    assert resolver.caminho_segmentacao_bruta("u2netp", "bufalo_001", execucao=2) == (
        "/tmp/seg_brutas/execucao_2/u2netp/bufalo_001.png"
    )
