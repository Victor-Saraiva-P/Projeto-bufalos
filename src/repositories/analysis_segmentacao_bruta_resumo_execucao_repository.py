from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaResumoExecucao
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaResumoExecucaoRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaResumoExecucao]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaResumoExecucao))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        execucao: int | None = None,
        metric_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaResumoExecucao]:
        stmt = select(AnaliseSegmentacaoBrutaResumoExecucao).order_by(
            AnaliseSegmentacaoBrutaResumoExecucao.nome_modelo,
            AnaliseSegmentacaoBrutaResumoExecucao.execucao,
            AnaliseSegmentacaoBrutaResumoExecucao.metric_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaResumoExecucao.nome_modelo == nome_modelo
            )
        if execucao is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaResumoExecucao.execucao == execucao)
        if metric_name is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaResumoExecucao.metric_name == metric_name
            )

        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBrutaResumoExecucao],
                session.scalars(stmt).all(),
            )
