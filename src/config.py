from pathlib import Path
import tomllib


BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = Path(__file__).with_name("config.toml")

with _CONFIG_PATH.open("rb") as config_file:
    _CONFIG = tomllib.load(config_file)


def _resolver_caminho(base_dir: Path, *parts: str) -> str:
    return str(base_dir.joinpath(*parts))


_PATHS = _CONFIG["paths"]
_COLUMNS = _CONFIG["columns"]
_FILE_TYPES = _CONFIG["file_types"]
_BINARIZATION = _CONFIG["binarization"]
_EVALUATION = _CONFIG["evaluation"]

# Diretorios mais gerais
DATA_DIR = _resolver_caminho(BASE_DIR, _PATHS["data_dir"])
GENERATED_DIR = _resolver_caminho(BASE_DIR, _PATHS["generated_dir"])

# Diretorios especificos
IMAGES_DIR = _resolver_caminho(BASE_DIR, _PATHS["data_dir"], _PATHS["images_dir"])
GROUND_TRUTH_RAW_DIR = _resolver_caminho(
    BASE_DIR,
    _PATHS["data_dir"],
    _PATHS["ground_truth_raw_dir"],
)
PREDICTED_MASKS_DIR = _resolver_caminho(
    BASE_DIR,
    _PATHS["generated_dir"],
    _PATHS["predicted_masks_dir"],
)
PREDICTED_MASKS_BINARY = _resolver_caminho(
    BASE_DIR,
    _PATHS["generated_dir"],
    _PATHS["predicted_masks_binary_dir"],
)
GROUND_TRUTH_BINARY = _resolver_caminho(
    BASE_DIR,
    _PATHS["generated_dir"],
    _PATHS["ground_truth_binary_dir"],
)
EVALUATION_DIR = _resolver_caminho(
    BASE_DIR,
    _PATHS["generated_dir"],
    _PATHS["evaluation_dir"],
)

# Caminhos de arquivos
INDICE_PATH = _resolver_caminho(
    BASE_DIR,
    _PATHS["data_dir"],
    _PATHS["indice_file"],
)
METRICS_CACHE_PATH = _resolver_caminho(
    BASE_DIR,
    _PATHS["generated_dir"],
    _PATHS["evaluation_dir"],
    _EVALUATION["metrics_cache_file"],
)

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
