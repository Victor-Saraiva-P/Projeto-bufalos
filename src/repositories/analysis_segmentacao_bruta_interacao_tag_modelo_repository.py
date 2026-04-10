from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaInteracaoTagModelo
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaInteracaoTagModeloRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(
        self, registros: list[AnaliseSegmentacaoBrutaInteracaoTagModelo]
    ) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaInteracaoTagModelo))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        tag_name: str | None = None,
        metric_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaInteracaoTagModelo]:
        stmt = select(AnaliseSegmentacaoBrutaInteracaoTagModelo).order_by(
            AnaliseSegmentacaoBrutaInteracaoTagModelo.nome_modelo,
            AnaliseSegmentacaoBrutaInteracaoTagModelo.tag_name,
            AnaliseSegmentacaoBrutaInteracaoTagModelo.metric_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaInteracaoTagModelo.nome_modelo == nome_modelo
            )
        if tag_name is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaInteracaoTagModelo.tag_name == tag_name)
        if metric_name is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaInteracaoTagModelo.metric_name == metric_name
            )

        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBrutaInteracaoTagModelo],
                session.scalars(stmt).all(),
            )
