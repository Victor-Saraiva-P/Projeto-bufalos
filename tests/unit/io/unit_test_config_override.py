import importlib
from pathlib import Path
import tomllib
import os

from src.config import (
    DATA_DIR,
    GENERATED_DIR,
    GROUND_TRUTH_BINARIZATION_STRATEGY,
    INDICE_PATH,
    MODELOS_PARA_AVALIACAO,
    NOME_COL,
    NUM_EXECUCOES,
    REMBG_IMAGE_TYPE,
    SEGMENTACAO_BINARIZATION_STRATEGIES,
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
    assert GROUND_TRUTH_BINARIZATION_STRATEGY == config_test["binarization"]["ground_truth_strategy"]
    assert SEGMENTACAO_BINARIZATION_STRATEGIES == config_test["binarization"]["segmentacao_strategies"]
    assert NOME_COL == "nome do arquivo"
    assert REMBG_IMAGE_TYPE == ".png"


def test_config_override_por_arquivo_carrega_config_e2e(monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    config_module = importlib.import_module("src.config")
    config_e2e = tomllib.loads((repo_root / "config.e2e.toml").read_text(encoding="utf-8"))
    override_original = os.environ.get("BUFALOS_CONFIG_PATH")

    try:
        monkeypatch.setenv("BUFALOS_CONFIG_PATH", "config.e2e.toml")
        recarregado = importlib.reload(config_module)

        assert Path(recarregado.GENERATED_DIR) == repo_root / "tests/e2e_generated"
        assert Path(recarregado.SQLITE_PATH) == repo_root / "tests/e2e_generated/bufalos-e2e.sqlite3"
        assert recarregado.MODELOS_PARA_AVALIACAO == config_e2e["models"]
        assert recarregado.NUM_EXECUCOES == config_e2e["execution"]["num_execucoes"]
        assert (
            recarregado.GROUND_TRUTH_BINARIZATION_STRATEGY
            == config_e2e["binarization"]["ground_truth_strategy"]
        )
        assert (
            recarregado.SEGMENTACAO_BINARIZATION_STRATEGIES
            == config_e2e["binarization"]["segmentacao_strategies"]
        )
    finally:
        monkeypatch.delenv("BUFALOS_CONFIG_PATH", raising=False)
        if override_original is not None:
            os.environ["BUFALOS_CONFIG_PATH"] = override_original
        importlib.reload(config_module)
