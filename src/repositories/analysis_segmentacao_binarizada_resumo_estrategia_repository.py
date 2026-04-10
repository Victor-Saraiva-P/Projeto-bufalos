from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBinarizadaResumoEstrategia
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBinarizadaResumoEstrategiaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBinarizadaResumoEstrategia]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBinarizadaResumoEstrategia))
            session.add_all(registros)
            session.commit()

    def list(self) -> list[AnaliseSegmentacaoBinarizadaResumoEstrategia]:
        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBinarizadaResumoEstrategia],
                session.scalars(
                    select(AnaliseSegmentacaoBinarizadaResumoEstrategia).order_by(
                        AnaliseSegmentacaoBinarizadaResumoEstrategia.estrategia_binarizacao,
                        AnaliseSegmentacaoBinarizadaResumoEstrategia.metric_name,
                    )
                ).all(),
            )

