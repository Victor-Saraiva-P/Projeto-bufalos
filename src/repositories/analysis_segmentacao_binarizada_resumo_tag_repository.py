from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBinarizadaResumoTag
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBinarizadaResumoTagRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, registros: list[AnaliseSegmentacaoBinarizadaResumoTag]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBinarizadaResumoTag))
            session.add_all(registros)
            session.commit()

    def list(self) -> list[AnaliseSegmentacaoBinarizadaResumoTag]:
        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBinarizadaResumoTag],
                session.scalars(
                    select(AnaliseSegmentacaoBinarizadaResumoTag).order_by(
                        AnaliseSegmentacaoBinarizadaResumoTag.nome_modelo,
                        AnaliseSegmentacaoBinarizadaResumoTag.estrategia_binarizacao,
                        AnaliseSegmentacaoBinarizadaResumoTag.tag_name,
                        AnaliseSegmentacaoBinarizadaResumoTag.tag_value,
                        AnaliseSegmentacaoBinarizadaResumoTag.metric_name,
                    )
                ).all(),
            )

