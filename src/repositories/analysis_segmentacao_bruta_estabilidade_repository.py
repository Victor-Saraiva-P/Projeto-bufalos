from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaEstabilidade
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaEstabilidadeRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaEstabilidade]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaEstabilidade))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        metric_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaEstabilidade]:
        stmt = select(AnaliseSegmentacaoBrutaEstabilidade).order_by(
            AnaliseSegmentacaoBrutaEstabilidade.nome_modelo,
            AnaliseSegmentacaoBrutaEstabilidade.metric_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaEstabilidade.nome_modelo == nome_modelo)
        if metric_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaEstabilidade.metric_name == metric_name)

        with self.sessionmaker() as session:
            return cast(list[AnaliseSegmentacaoBrutaEstabilidade], session.scalars(stmt).all())
