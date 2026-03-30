from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import SQLITE_PATH
from src.models import Segmentacao
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class SegmentacaoRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, segmentacao: Segmentacao) -> Segmentacao:
        persistivel = Segmentacao(
            nome_arquivo=segmentacao.nome_arquivo,
            nome_modelo=segmentacao.nome_modelo,
            area=segmentacao.area,
            perimetro=segmentacao.perimetro,
            iou=segmentacao.iou,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(self, nome_arquivo: str, nome_modelo: str) -> Segmentacao | None:
        with self.sessionmaker() as session:
            return session.scalar(
                select(Segmentacao)
                .options(selectinload(Segmentacao.binarizacoes))
                .where(
                    Segmentacao.nome_arquivo == nome_arquivo,
                    Segmentacao.nome_modelo == nome_modelo,
                )
            )

    def list(self, nome_arquivo: str | None = None) -> list[Segmentacao]:
        stmt = (
            select(Segmentacao)
            .options(selectinload(Segmentacao.binarizacoes))
            .order_by(Segmentacao.nome_arquivo, Segmentacao.nome_modelo)
        )
        if nome_arquivo is not None:
            stmt = stmt.where(Segmentacao.nome_arquivo == nome_arquivo)

        with self.sessionmaker() as session:
            return cast(list[Segmentacao], session.scalars(stmt).all())

    def delete(self, nome_arquivo: str, nome_modelo: str) -> None:
        with self.sessionmaker() as session:
            registro = session.get(Segmentacao, (nome_arquivo, nome_modelo))
            if registro is None:
                return
            session.delete(registro)
            session.commit()
