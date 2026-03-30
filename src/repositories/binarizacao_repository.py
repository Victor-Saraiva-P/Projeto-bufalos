from __future__ import annotations

from typing import cast

from sqlalchemy import select

from src.config import SQLITE_PATH
from src.models import Binarizacao
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class BinarizacaoRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(self, binarizacao: Binarizacao) -> Binarizacao:
        persistivel = Binarizacao(
            nome_arquivo=binarizacao.nome_arquivo,
            nome_modelo=binarizacao.nome_modelo,
            estrategia_binarizacao=binarizacao.estrategia_binarizacao,
            metrica_x=binarizacao.metrica_x,
            metrica_y=binarizacao.metrica_y,
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
    ) -> Binarizacao | None:
        with self.sessionmaker() as session:
            return session.get(
                Binarizacao,
                (nome_arquivo, nome_modelo, estrategia_binarizacao),
            )

    def list(
        self,
        nome_arquivo: str | None = None,
        nome_modelo: str | None = None,
    ) -> list[Binarizacao]:
        stmt = select(Binarizacao).order_by(
            Binarizacao.nome_arquivo,
            Binarizacao.nome_modelo,
            Binarizacao.estrategia_binarizacao,
        )
        if nome_arquivo is not None:
            stmt = stmt.where(Binarizacao.nome_arquivo == nome_arquivo)
        if nome_modelo is not None:
            stmt = stmt.where(Binarizacao.nome_modelo == nome_modelo)

        with self.sessionmaker() as session:
            return cast(list[Binarizacao], session.scalars(stmt).all())

    def delete(
        self,
        nome_arquivo: str,
        nome_modelo: str,
        estrategia_binarizacao: str,
    ) -> None:
        with self.sessionmaker() as session:
            registro = session.get(
                Binarizacao,
                (nome_arquivo, nome_modelo, estrategia_binarizacao),
            )
            if registro is None:
                return
            session.delete(registro)
            session.commit()
