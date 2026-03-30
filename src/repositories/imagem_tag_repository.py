from __future__ import annotations

from typing import cast

from sqlalchemy import select

from src.config import SQLITE_PATH
from src.models import ImagemTag
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class ImagemTagRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, imagem_tag: ImagemTag) -> ImagemTag:
        persistivel = ImagemTag(
            nome_arquivo=imagem_tag.nome_arquivo,
            nome_tag=imagem_tag.nome_tag,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(self, nome_arquivo: str, nome_tag: str) -> ImagemTag | None:
        with self.sessionmaker() as session:
            return session.get(ImagemTag, (nome_arquivo, nome_tag))

    def list(self, nome_arquivo: str | None = None) -> list[ImagemTag]:
        stmt = select(ImagemTag).order_by(ImagemTag.nome_arquivo, ImagemTag.nome_tag)
        if nome_arquivo is not None:
            stmt = stmt.where(ImagemTag.nome_arquivo == nome_arquivo)

        with self.sessionmaker() as session:
            return cast(list[ImagemTag], session.scalars(stmt).all())

    def delete(self, nome_arquivo: str, nome_tag: str) -> None:
        with self.sessionmaker() as session:
            registro = session.get(ImagemTag, (nome_arquivo, nome_tag))
            if registro is None:
                return
            session.delete(registro)
            session.commit()
