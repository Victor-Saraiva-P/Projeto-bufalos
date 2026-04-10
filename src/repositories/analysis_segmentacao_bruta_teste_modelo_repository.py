from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaTesteModelo
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaTesteModeloRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaTesteModelo]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaTesteModelo))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        metric_name: str | None = None,
        comparison_scope: str | None = None,
        test_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaTesteModelo]:
        stmt = select(AnaliseSegmentacaoBrutaTesteModelo).order_by(
            AnaliseSegmentacaoBrutaTesteModelo.metric_name,
            AnaliseSegmentacaoBrutaTesteModelo.comparison_scope,
            AnaliseSegmentacaoBrutaTesteModelo.test_name,
            AnaliseSegmentacaoBrutaTesteModelo.group_a,
            AnaliseSegmentacaoBrutaTesteModelo.group_b,
        )
        if metric_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaTesteModelo.metric_name == metric_name)
        if comparison_scope is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaTesteModelo.comparison_scope == comparison_scope
            )
        if test_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaTesteModelo.test_name == test_name)

        with self.sessionmaker() as session:
            return cast(list[AnaliseSegmentacaoBrutaTesteModelo], session.scalars(stmt).all())
