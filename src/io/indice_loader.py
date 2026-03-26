from src.config import INDICE_DB_PATH
from src.io.indice_db import carregar_indice
from src.models.indice_linha import IndiceLinha


def carregar_indice_sqlite() -> list[IndiceLinha]:
    return carregar_indice(db_path=INDICE_DB_PATH)


def carregar_indice_excel() -> list[IndiceLinha]:
    return carregar_indice(db_path=INDICE_DB_PATH)
