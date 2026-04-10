from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBinarizadaTesteEstrategia
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBinarizadaTesteEstrategiaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBinarizadaTesteEstrategia]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBinarizadaTesteEstrategia))
            session.add_all(registros)
            session.commit()

    def list(self) -> list[AnaliseSegmentacaoBinarizadaTesteEstrategia]:
        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBinarizadaTesteEstrategia],
                session.scalars(
                    select(AnaliseSegmentacaoBinarizadaTesteEstrategia).order_by(
                        AnaliseSegmentacaoBinarizadaTesteEstrategia.metric_name,
                        AnaliseSegmentacaoBinarizadaTesteEstrategia.modelo_origem,
                        AnaliseSegmentacaoBinarizadaTesteEstrategia.comparison_scope,
                        AnaliseSegmentacaoBinarizadaTesteEstrategia.group_a,
                        AnaliseSegmentacaoBinarizadaTesteEstrategia.group_b,
                    )
                ).all(),
            )

