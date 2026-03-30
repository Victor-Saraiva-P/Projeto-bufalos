from __future__ import annotations

from typing import cast

from sqlalchemy import select

from src.config import SQLITE_PATH
from src.models import GroundTruthBinarizada
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class GroundTruthBinarizadaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, ground_truth_binarizada: GroundTruthBinarizada) -> GroundTruthBinarizada:
        persistivel = GroundTruthBinarizada(
            nome_arquivo=ground_truth_binarizada.nome_arquivo,
            area=ground_truth_binarizada.area,
            perimetro=ground_truth_binarizada.perimetro,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(self, nome_arquivo: str) -> GroundTruthBinarizada | None:
        with self.sessionmaker() as session:
            return session.get(GroundTruthBinarizada, nome_arquivo)

    def list(self) -> list[GroundTruthBinarizada]:
        with self.sessionmaker() as session:
            return cast(
                list[GroundTruthBinarizada],
                session.scalars(
                    select(GroundTruthBinarizada).order_by(GroundTruthBinarizada.nome_arquivo)
                ).all(),
            )

    def delete(self, nome_arquivo: str) -> None:
        with self.sessionmaker() as session:
            registro = session.get(GroundTruthBinarizada, nome_arquivo)
            if registro is None:
                return
            session.delete(registro)
            session.commit()
