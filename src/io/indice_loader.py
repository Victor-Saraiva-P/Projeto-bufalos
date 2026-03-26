from decimal import Decimal

import pandas as pd

from src.config import FAZENDA_COL, INDICE_PATH, NOME_COL, PESO_COL, TAGS_COL, SQLITE_PATH
from src.io.sqlite.repositories import IndiceSQLiteRepository
from src.models.indice_linha import IndiceLinha, normalizar_tags


def carregar_indice_excel(indice_path: str = INDICE_PATH) -> list[IndiceLinha]:
    indice_df = pd.read_excel(indice_path)
    colunas = {c.strip().lower(): c for c in indice_df.columns}

    nome_col = colunas.get(NOME_COL)
    fazenda_col = colunas.get(FAZENDA_COL)
    peso_col = colunas.get(PESO_COL)
    tags_col = colunas.get(TAGS_COL)

    if not nome_col or not fazenda_col or not peso_col:
        raise ValueError(
            "Alguma das colunas esperadas nao foi encontrada no arquivo Excel."
        )

    return [
        IndiceLinha(
            nome_arquivo=str(row[nome_col]),
            fazenda=str(row[fazenda_col]),
            peso=Decimal(str(row[peso_col])),
            tags=normalizar_tags(row[tags_col]) if tags_col else [],
        )
        for _, row in indice_df.iterrows()
    ]


def inicializar_indice_sqlite(
    indice_path: str = INDICE_PATH,
    sqlite_path: str = SQLITE_PATH,
) -> None:
    repository = IndiceSQLiteRepository(sqlite_path)
    repository.sincronizar_do_excel(indice_path)


def carregar_indice(sqlite_path: str = SQLITE_PATH) -> list[IndiceLinha]:
    repository = IndiceSQLiteRepository(sqlite_path)
    return repository.listar()
