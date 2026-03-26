from src.io.indice_db import carregar_indice
from src.models.indice_linha import IndiceLinha


def carregar_indice_sqlite() -> list[IndiceLinha]:
    return carregar_indice()


def carregar_indice_excel() -> list[IndiceLinha]:
    return carregar_indice()
