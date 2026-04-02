from pathlib import Path
import tomllib

from src.config import (
    DATA_DIR,
    GENERATED_DIR,
    INDICE_PATH,
    MODELOS_PARA_AVALIACAO,
    NOME_COL,
    NUM_EXECUCOES,
    REMBG_IMAGE_TYPE,
    SQLITE_PATH,
)


def test_config_de_testes_aplica_override_e_herda_defaults() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    config_test = tomllib.loads((repo_root / "config.test.toml").read_text(encoding="utf-8"))

    assert Path(DATA_DIR) == repo_root / "tests/mock_data"
    assert Path(GENERATED_DIR) == repo_root / "tests/generated"
    assert Path(INDICE_PATH) == repo_root / "tests/mock_data/Indice.xlsx"
    assert Path(SQLITE_PATH) == repo_root / "tests/mock_generated/bufalos-testes.sqlite3"
    assert MODELOS_PARA_AVALIACAO == config_test["models"]
    assert NUM_EXECUCOES == config_test["execution"]["num_execucoes"]
    assert NOME_COL == "nome do arquivo"
    assert REMBG_IMAGE_TYPE == ".png"
