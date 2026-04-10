from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBinarizadaResumoExecucao
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBinarizadaResumoExecucaoRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBinarizadaResumoExecucao]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBinarizadaResumoExecucao))
            session.add_all(registros)
            session.commit()

    def list(self) -> list[AnaliseSegmentacaoBinarizadaResumoExecucao]:
        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBinarizadaResumoExecucao],
                session.scalars(
                    select(AnaliseSegmentacaoBinarizadaResumoExecucao).order_by(
                        AnaliseSegmentacaoBinarizadaResumoExecucao.nome_modelo,
                        AnaliseSegmentacaoBinarizadaResumoExecucao.estrategia_binarizacao,
                        AnaliseSegmentacaoBinarizadaResumoExecucao.execucao,
                        AnaliseSegmentacaoBinarizadaResumoExecucao.metric_name,
                    )
                ).all(),
            )

