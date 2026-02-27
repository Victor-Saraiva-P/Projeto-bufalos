import os


# Diretorio base do projeto (diretorio pai de src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretorios mais gerais
DATA_DIR = os.path.join(BASE_DIR, "data")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

# Diretorios especificos
IMAGES_DIR = os.path.join(DATA_DIR, "images")
GROUND_TRUTH_DIR = os.path.join(DATA_DIR, "ground_truth")

PREDICTED_MASKS_DIR = os.path.join(GENERATED_DIR, "predicted_masks")
PREDICTED_MASKS_BINARY = os.path.join(GENERATED_DIR, "predicted_masks_binary")

GROUND_TRUTH_BINARY = os.path.join(GENERATED_DIR, "ground_truth_binary")

# Caminhos de arquivos
INDICE_PATH = os.path.join(DATA_DIR, "Indice.xlsx")

# Nomes das colunas do excel
NOME_COL = "nome do arquivo"
FAZENDA_COL = "fazenda"
PESO_COL = "peso"

# Configuracao do tipo de arquivo
IMAGES_TYPE = ".jpg"
REMBG_IMAGE_TYPE = ".png"

# Configuracao de binarizacao
# Metodo: Gaussian Blur + Morphological Opening
# 1. Gaussian Blur: suaviza artefatos de compressao JPG
# 2. Threshold: separa foreground (>127) de background (<=127)
# 3. Morphological Opening: erosao seguida de dilatacao - remove pixels isolados e suaviza bordas
BINARIZATION_SIGMA = 1.0  # Intensidade do blur gaussiano
BINARIZATION_THRESHOLD = 127  # Limiar de binarizacao (0-255)
BINARIZATION_KERNEL_SIZE = 3  # Tamanho do elemento estruturante para opening

# Deprecated - usar BINARIZATION_THRESHOLD
LIMIAR_BINARIZACAO = 127

# Modelos para avaliacao (modelo: provider)
# provider: "gpu" = usa GPU se disponivel, senao CPU | "cpu" = sempre CPU
MODELOS_PARA_AVALIACAO = {
    "u2net": "gpu",
    "u2netp": "gpu",
    "u2net_human_seg": "gpu",
    # "u2net_cloth_seg": "gpu",  # especifico para roupas e altera resolucao da imagem
    "silueta": "gpu",
    "isnet-general-use": "gpu",
    "isnet-anime": "gpu",
    "sam": "gpu",
    "birefnet-general": "cpu",
    "birefnet-general-lite": "cpu",
    "birefnet-portrait": "cpu",
    "birefnet-dis": "cpu",
    "birefnet-hrsod": "cpu",
    "birefnet-cod": "cpu",
    "birefnet-massive": "cpu",
}

# ==============================================================================
# EVALUATION SYSTEM CONFIGURATION
# ==============================================================================

# Diretorio de avaliacao
EVALUATION_DIR = os.path.join(GENERATED_DIR, "evaluation")

# Cache de metricas
METRICS_CACHE_PATH = os.path.join(EVALUATION_DIR, "metrics_cache.csv")

# Pesos para ranking (devem somar 1.0)
RANKING_WEIGHTS = {
    "iou": 0.34,  # 40% - Sobreposicao (Intersection over Union)
    "area_similarity": 0.33,  # 30% - Similaridade de area
    "perimetro_similarity": 0.33,  # 30% - Similaridade de perimetro
}
