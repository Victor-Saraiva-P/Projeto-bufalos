import os


# Diretorio base do projeto (diretorio deste arquivo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretorios mais gerais
DATA_DIR = os.path.join(BASE_DIR, "data")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

# Diretorios especificos
ORIGINAL_PHOTOS_DIR = os.path.join(DATA_DIR, "Original")
GROUND_OF_TRUTH = os.path.join(DATA_DIR, "Ground-of-truth")

SEGMENTED_PHOTOS_DIR = os.path.join(GENERATED_DIR, "Segmentada")
GROUND_OF_TRUTH_OUTPUT = os.path.join(GENERATED_DIR, "Ground-of-truth")

# Caminhos de arquivos
INDICE_PATH = os.path.join(DATA_DIR, "Indice.xlsx")

# Nomes das colunas do excel
NOME_COL = "nome do arquivo"
FAZENDA_COL = "fazenda"
PESO_COL = "peso"

# Configuracao do tipo de arquivo
ORIGINAL_IMAGE_TYPE = ".jpg"
REMBG_IMAGE_TYPE = ".png"

# Configuracao de binarizacao
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
    "birefnet-general-lite": "gpu",
    "birefnet-portrait": "gpu",
    "birefnet-dis": "gpu",
    "birefnet-hrsod": "gpu",
    "birefnet-cod": "gpu",
    "birefnet-massive": "cpu",
}
