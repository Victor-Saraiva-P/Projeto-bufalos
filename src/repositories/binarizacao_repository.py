from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import SQLITE_PATH
from src.models import SegmentacaoBinarizada
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class SegmentacaoBinarizadaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, binarizacao: SegmentacaoBinarizada) -> SegmentacaoBinarizada:
        persistivel = SegmentacaoBinarizada(
            nome_arquivo=binarizacao.nome_arquivo,
            nome_modelo=binarizacao.nome_modelo,
            estrategia_binarizacao=binarizacao.estrategia_binarizacao,
            area=binarizacao.area,
            perimetro=binarizacao.perimetro,
            iou=binarizacao.iou,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        estrategia_binarizacao: str,
    ) -> SegmentacaoBinarizada | None:
        with self.sessionmaker() as session:
            return session.scalar(
                select(SegmentacaoBinarizada)
                .options(selectinload(SegmentacaoBinarizada.segmentacao_bruta))
                .where(
                    SegmentacaoBinarizada.nome_arquivo == nome_arquivo,
                    SegmentacaoBinarizada.nome_modelo == nome_modelo,
                    SegmentacaoBinarizada.estrategia_binarizacao == estrategia_binarizacao,
                )
            )

    def list(
        self,
        nome_arquivo: str | None = None,
        nome_modelo: str | None = None,
    ) -> list[SegmentacaoBinarizada]:
        stmt = (
            select(SegmentacaoBinarizada)
            .options(selectinload(SegmentacaoBinarizada.segmentacao_bruta))
            .order_by(
                SegmentacaoBinarizada.nome_arquivo,
                SegmentacaoBinarizada.nome_modelo,
                SegmentacaoBinarizada.estrategia_binarizacao,
            )
        )
        if nome_arquivo is not None:
            stmt = stmt.where(SegmentacaoBinarizada.nome_arquivo == nome_arquivo)
        if nome_modelo is not None:
            stmt = stmt.where(SegmentacaoBinarizada.nome_modelo == nome_modelo)

        with self.sessionmaker() as session:
            return cast(list[SegmentacaoBinarizada], session.scalars(stmt).all())

    def delete(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        estrategia_binarizacao: str,
    ) -> None:
        with self.sessionmaker() as session:
            registro = session.get(
                SegmentacaoBinarizada,
                (nome_arquivo, nome_modelo, estrategia_binarizacao),
            )
            if registro is None:
                return
            session.delete(registro)
            session.commit()
