from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaIntervaloConfianca
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaIntervaloConfiancaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(
        self, registros: list[AnaliseSegmentacaoBrutaIntervaloConfianca]
    ) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaIntervaloConfianca))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        metric_name: str | None = None,
        statistic_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaIntervaloConfianca]:
        stmt = select(AnaliseSegmentacaoBrutaIntervaloConfianca).order_by(
            AnaliseSegmentacaoBrutaIntervaloConfianca.nome_modelo,
            AnaliseSegmentacaoBrutaIntervaloConfianca.metric_name,
            AnaliseSegmentacaoBrutaIntervaloConfianca.statistic_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaIntervaloConfianca.nome_modelo == nome_modelo
            )
        if metric_name is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaIntervaloConfianca.metric_name == metric_name
            )
        if statistic_name is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaIntervaloConfianca.statistic_name == statistic_name
            )

        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBrutaIntervaloConfianca],
                session.scalars(stmt).all(),
            )
