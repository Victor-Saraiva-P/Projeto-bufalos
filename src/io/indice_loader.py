import pandas as pd

from src.config import FAZENDA_COL, INDICE_PATH, NOME_COL, PESO_COL, TAGS_COL
from src.models import Imagem, Tag, normalizar_tags


def carregar_indice_excel(indice_path: str = INDICE_PATH) -> list[Imagem]:
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

    imagens: list[Imagem] = []
    for _, row in indice_df.iterrows():
        imagem = Imagem(
            nome_arquivo=str(row[nome_col]),
            fazenda=str(row[fazenda_col]),
            peso=float(row[peso_col]),
        )
        tags = normalizar_tags(row[tags_col]) if tags_col else []
        imagem.tags = [
            Tag(nome_tag=nome_tag)
            for nome_tag in tags
        ]
        imagens.append(imagem)

    return imagens
