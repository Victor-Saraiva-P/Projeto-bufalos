from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaResumoTag
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaResumoTagRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaResumoTag]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaResumoTag))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        tag_name: str | None = None,
        tag_value: bool | None = None,
        metric_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaResumoTag]:
        stmt = select(AnaliseSegmentacaoBrutaResumoTag).order_by(
            AnaliseSegmentacaoBrutaResumoTag.nome_modelo,
            AnaliseSegmentacaoBrutaResumoTag.tag_name,
            AnaliseSegmentacaoBrutaResumoTag.tag_value,
            AnaliseSegmentacaoBrutaResumoTag.metric_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaResumoTag.nome_modelo == nome_modelo)
        if tag_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaResumoTag.tag_name == tag_name)
        if tag_value is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaResumoTag.tag_value == tag_value)
        if metric_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaResumoTag.metric_name == metric_name)

        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBrutaResumoTag],
                session.scalars(stmt).all(),
            )
