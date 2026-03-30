from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import SQLITE_PATH
from src.models import Tag
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class TagRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, tag: Tag) -> Tag:
        persistivel = Tag(nome_tag=tag.nome_tag)
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(self, nome_tag: str) -> Tag | None:
        with self.sessionmaker() as session:
            return session.scalar(
                select(Tag)
                .options(selectinload(Tag.imagens))
                .where(Tag.nome_tag == nome_tag)
            )

    def list(self) -> list[Tag]:
        with self.sessionmaker() as session:
            return cast(
                list[Tag],
                session.scalars(
                    select(Tag).options(selectinload(Tag.imagens)).order_by(Tag.nome_tag)
                ).all(),
            )

    def delete(self, nome_tag: str) -> None:
        with self.sessionmaker() as session:
            registro = session.get(Tag, nome_tag)
            if registro is None:
                return
            session.delete(registro)
            session.commit()
