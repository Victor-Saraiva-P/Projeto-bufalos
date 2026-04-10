from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaTesteTag
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaTesteTagRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaTesteTag]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaTesteTag))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        metric_name: str | None = None,
        tag_name: str | None = None,
        comparison_scope: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaTesteTag]:
        stmt = select(AnaliseSegmentacaoBrutaTesteTag).order_by(
            AnaliseSegmentacaoBrutaTesteTag.metric_name,
            AnaliseSegmentacaoBrutaTesteTag.tag_name,
            AnaliseSegmentacaoBrutaTesteTag.comparison_scope,
            AnaliseSegmentacaoBrutaTesteTag.nome_modelo,
        )
        if metric_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaTesteTag.metric_name == metric_name)
        if tag_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaTesteTag.tag_name == tag_name)
        if comparison_scope is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaTesteTag.comparison_scope == comparison_scope
            )

        with self.sessionmaker() as session:
            return cast(list[AnaliseSegmentacaoBrutaTesteTag], session.scalars(stmt).all())
