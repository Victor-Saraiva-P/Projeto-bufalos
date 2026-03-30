from pathlib import Path

from src.config import (
    DATA_DIR,
    GENERATED_DIR,
    INDICE_PATH,
    MODELOS_PARA_AVALIACAO,
    NOME_COL,
    REMBG_IMAGE_TYPE,
    SQLITE_PATH,
)


def test_config_de_testes_aplica_override_e_herda_defaults() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    assert Path(DATA_DIR) == repo_root / "tests/mock_data"
    assert Path(GENERATED_DIR) == repo_root / "tests/generated"
    assert Path(INDICE_PATH) == repo_root / "tests/mock_data/Indice.xlsx"
    assert Path(SQLITE_PATH) == repo_root / "tests/generated/bufalos-testes.sqlite3"
    assert MODELOS_PARA_AVALIACAO == {"u2netp": "cpu"}
    assert NOME_COL == "nome do arquivo"
    assert REMBG_IMAGE_TYPE == ".png"
