import os
from pathlib import Path
import sys
import tomllib


BASE_DIR = Path(__file__).resolve().parent.parent
_BASE_CONFIG_PATH = BASE_DIR / "config.toml"
_TEST_CONFIG_PATH = BASE_DIR / "config.test.toml"
_CONFIG_OVERRIDE_ENV = "BUFALOS_CONFIG_PATH"
_CONFIG_ENV = "BUFALOS_ENV"


def _carregar_toml(config_path: Path) -> dict:
    with config_path.open("rb") as config_file:
        return tomllib.load(config_file)


def _merge_recursivo(base: dict, override: dict) -> dict:
    merged = dict(base)

    for key, value in override.items():
        if key == "models":
            merged[key] = value
            continue

        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_recursivo(merged[key], value)
            continue

        merged[key] = value

    return merged


def _carregar_config() -> dict:
    config = _carregar_toml(_BASE_CONFIG_PATH)
    override_path_raw = os.environ.get(_CONFIG_OVERRIDE_ENV)

    if override_path_raw:
        override_path = Path(override_path_raw).expanduser()
        if not override_path.is_absolute():
            override_path = (BASE_DIR / override_path).resolve()

        override = _carregar_toml(override_path)
        return _merge_recursivo(config, override)

    if _em_modo_teste() and _TEST_CONFIG_PATH.exists():
        override = _carregar_toml(_TEST_CONFIG_PATH)
        return _merge_recursivo(config, override)

    return config


def _em_modo_teste() -> bool:
    ambiente = os.environ.get(_CONFIG_ENV, "").strip().lower()

    if ambiente in {"test", "tests"}:
        return True

    return "pytest" in sys.modules


_CONFIG = _carregar_config()


def _resolver_caminho(path_value: str) -> str:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((BASE_DIR / path).resolve())


_PATHS = _CONFIG["paths"]
_COLUMNS = _CONFIG["columns"]
_FILE_TYPES = _CONFIG["file_types"]
_BINARIZATION = _CONFIG["binarization"]
_EVALUATION = _CONFIG["evaluation"]

# Diretorios mais gerais
DATA_DIR = _resolver_caminho(_PATHS["data_dir"])
GENERATED_DIR = _resolver_caminho(_PATHS["generated_dir"])

# Diretorios especificos
IMAGES_DIR = _resolver_caminho(_PATHS["images_dir"])
GROUND_TRUTH_RAW_DIR = _resolver_caminho(_PATHS["ground_truth_raw_dir"])
PREDICTED_MASKS_DIR = _resolver_caminho(_PATHS["predicted_masks_dir"])
PREDICTED_MASKS_BINARY = _resolver_caminho(_PATHS["predicted_masks_binary_dir"])
GROUND_TRUTH_BINARY = _resolver_caminho(_PATHS["ground_truth_binary_dir"])
EVALUATION_DIR = _resolver_caminho(_PATHS["evaluation_dir"])

# Caminhos de arquivos
INDICE_PATH = _resolver_caminho(_PATHS["indice_file"])
SQLITE_PATH = _resolver_caminho(_PATHS["sqlite_file"])

# Nomes das colunas do excel
NOME_COL = _COLUMNS["nome"]
FAZENDA_COL = _COLUMNS["fazenda"]
PESO_COL = _COLUMNS["peso"]
TAGS_COL = _COLUMNS["tags"]

# Configuracao do tipo de arquivo
IMAGES_TYPE = _FILE_TYPES["images"]
REMBG_IMAGE_TYPE = _FILE_TYPES["rembg"]

# Configuracao de binarizacao
BINARIZATION_SIGMA = _BINARIZATION["sigma"]
BINARIZATION_THRESHOLD = _BINARIZATION["threshold"]
BINARIZATION_KERNEL_SIZE = _BINARIZATION["kernel_size"]

# Deprecated - usar BINARIZATION_THRESHOLD
LIMIAR_BINARIZACAO = BINARIZATION_THRESHOLD

# Configuracoes declarativas
MODELOS_PARA_AVALIACAO = _CONFIG["models"]
RANKING_WEIGHTS = _EVALUATION["ranking_weights"]
