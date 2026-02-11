from decimal import Decimal

import pandas as pd

from src.config import FAZENDA_COL, INDICE_PATH, NOME_COL, PESO_COL
from src.models.indice_linha import IndiceLinha


def carregar_indice_excel() -> list[IndiceLinha]:
    indice_df = pd.read_excel(INDICE_PATH)
    colunas = {c.strip().lower(): c for c in indice_df.columns}

    nome_col = colunas.get(NOME_COL)
    fazenda_col = colunas.get(FAZENDA_COL)
    peso_col = colunas.get(PESO_COL)

    if not nome_col or not fazenda_col or not peso_col:
        raise ValueError(
            "Alguma das colunas esperadas nao foi encontrada no arquivo Excel."
        )

    return [
        IndiceLinha(
            nome_arquivo=str(row[nome_col]),
            fazenda=str(row[fazenda_col]),
            peso=Decimal(str(row[peso_col])),
        )
        for _, row in indice_df.iterrows()
    ]
