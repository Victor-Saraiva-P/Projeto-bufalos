from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import SQLITE_PATH
from src.models import SegmentacaoBruta
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class SegmentacaoBrutaRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, segmentacao: SegmentacaoBruta) -> SegmentacaoBruta:
        persistivel = SegmentacaoBruta(
            nome_arquivo=segmentacao.nome_arquivo,
            nome_modelo=segmentacao.nome_modelo,
            execucao=segmentacao.execucao,
            auprc=segmentacao.auprc,
            brier_score=segmentacao.brier_score,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def get(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        execucao: int,
    ) -> SegmentacaoBruta | None:
        with self.sessionmaker() as session:
            return session.scalar(
                select(SegmentacaoBruta)
                .options(selectinload(SegmentacaoBruta.segmentacoes_binarizadas))
                .where(
                    SegmentacaoBruta.nome_arquivo == nome_arquivo,
                    SegmentacaoBruta.nome_modelo == nome_modelo,
                    SegmentacaoBruta.execucao == execucao,
                )
            )

    def list(
        self,
        nome_arquivo: str | None = None,
        nome_modelo: str | None = None,
        execucao: int | None = None,
    ) -> list[SegmentacaoBruta]:
        stmt = (
            select(SegmentacaoBruta)
            .options(selectinload(SegmentacaoBruta.segmentacoes_binarizadas))
            .order_by(
                SegmentacaoBruta.nome_arquivo,
                SegmentacaoBruta.nome_modelo,
                SegmentacaoBruta.execucao,
            )
        )
        if nome_arquivo is not None:
            stmt = stmt.where(SegmentacaoBruta.nome_arquivo == nome_arquivo)
        if nome_modelo is not None:
            stmt = stmt.where(SegmentacaoBruta.nome_modelo == nome_modelo)
        if execucao is not None:
            stmt = stmt.where(SegmentacaoBruta.execucao == execucao)

        with self.sessionmaker() as session:
            return cast(list[SegmentacaoBruta], session.scalars(stmt).all())

    def delete(self, nome_arquivo: str, nome_modelo: str, execucao: int) -> None:
        with self.sessionmaker() as session:
            registro = session.get(SegmentacaoBruta, (nome_arquivo, nome_modelo, execucao))
            if registro is None:
                return
            session.delete(registro)
            session.commit()
