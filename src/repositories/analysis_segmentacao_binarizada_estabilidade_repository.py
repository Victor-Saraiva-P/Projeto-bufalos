from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBinarizadaEstabilidade
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBinarizadaEstabilidadeRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBinarizadaEstabilidade]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBinarizadaEstabilidade))
            session.add_all(registros)
            session.commit()

    def list(self) -> list[AnaliseSegmentacaoBinarizadaEstabilidade]:
        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBinarizadaEstabilidade],
                session.scalars(
                    select(AnaliseSegmentacaoBinarizadaEstabilidade).order_by(
                        AnaliseSegmentacaoBinarizadaEstabilidade.nome_modelo,
                        AnaliseSegmentacaoBinarizadaEstabilidade.estrategia_binarizacao,
                        AnaliseSegmentacaoBinarizadaEstabilidade.metric_name,
                    )
                ).all(),
            )

