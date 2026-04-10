from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaResumoModelo
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaResumoModeloRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(
        self, registro: AnaliseSegmentacaoBrutaResumoModelo
    ) -> AnaliseSegmentacaoBrutaResumoModelo:
        persistivel = AnaliseSegmentacaoBrutaResumoModelo(
            nome_modelo=registro.nome_modelo,
            metric_name=registro.metric_name,
            count=registro.count,
            mean=registro.mean,
            median=registro.median,
            std=registro.std,
            min=registro.min,
            max=registro.max,
            q1=registro.q1,
            q3=registro.q3,
            iqr=registro.iqr,
            higher_is_better=registro.higher_is_better,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaResumoModelo]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaResumoModelo))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        metric_name: str | None = None,
    ) -> list[AnaliseSegmentacaoBrutaResumoModelo]:
        stmt = select(AnaliseSegmentacaoBrutaResumoModelo).order_by(
            AnaliseSegmentacaoBrutaResumoModelo.nome_modelo,
            AnaliseSegmentacaoBrutaResumoModelo.metric_name,
        )
        if nome_modelo is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaResumoModelo.nome_modelo == nome_modelo
            )
        if metric_name is not None:
            stmt = stmt.where(
                AnaliseSegmentacaoBrutaResumoModelo.metric_name == metric_name
            )

        with self.sessionmaker() as session:
            return cast(
                list[AnaliseSegmentacaoBrutaResumoModelo],
                session.scalars(stmt).all(),
            )
