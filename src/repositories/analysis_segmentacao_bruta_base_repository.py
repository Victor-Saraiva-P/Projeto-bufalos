from __future__ import annotations

from typing import cast

from sqlalchemy import delete, select

from src.config import SQLITE_PATH
from src.models import AnaliseSegmentacaoBrutaBase
from src.sqlite import criar_sessionmaker_sqlite, criar_tabelas_sqlite


class AnaliseSegmentacaoBrutaBaseRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def save(
        self, registro: AnaliseSegmentacaoBrutaBase
    ) -> AnaliseSegmentacaoBrutaBase:
        persistivel = AnaliseSegmentacaoBrutaBase(
            nome_arquivo=registro.nome_arquivo,
            nome_modelo=registro.nome_modelo,
            execucao=registro.execucao,
            fazenda=registro.fazenda,
            peso=registro.peso,
            auprc=registro.auprc,
            soft_dice=registro.soft_dice,
            brier_score=registro.brier_score,
            tags=registro.tags,
            tags_sem_ok=registro.tags_sem_ok,
            num_tags_problema=registro.num_tags_problema,
            tem_tag_problema=registro.tem_tag_problema,
            grupo_dificuldade=registro.grupo_dificuldade,
            tag_ok=registro.tag_ok,
            tag_multi_bufalos=registro.tag_multi_bufalos,
            tag_cortado=registro.tag_cortado,
            tag_angulo_extremo=registro.tag_angulo_extremo,
            tag_baixo_contraste=registro.tag_baixo_contraste,
            tag_ocluido=registro.tag_ocluido,
        )
        with self.sessionmaker() as session:
            merged = session.merge(persistivel)
            session.commit()
            return merged

    def replace_all(self, registros: list[AnaliseSegmentacaoBrutaBase]) -> None:
        with self.sessionmaker() as session:
            session.execute(delete(AnaliseSegmentacaoBrutaBase))
            session.add_all(registros)
            session.commit()

    def list(
        self,
        nome_modelo: str | None = None,
        execucao: int | None = None,
    ) -> list[AnaliseSegmentacaoBrutaBase]:
        stmt = select(AnaliseSegmentacaoBrutaBase).order_by(
            AnaliseSegmentacaoBrutaBase.nome_arquivo,
            AnaliseSegmentacaoBrutaBase.nome_modelo,
            AnaliseSegmentacaoBrutaBase.execucao,
        )
        if nome_modelo is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaBase.nome_modelo == nome_modelo)
        if execucao is not None:
            stmt = stmt.where(AnaliseSegmentacaoBrutaBase.execucao == execucao)

        with self.sessionmaker() as session:
            return cast(list[AnaliseSegmentacaoBrutaBase], session.scalars(stmt).all())
