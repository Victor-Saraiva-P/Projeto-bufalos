from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import SQLITE_PATH
from src.models import (
    Imagem,
    Segmentacao,
    Tag,
)
from src.sqlite import (
    criar_sessionmaker_sqlite,
    criar_tabelas_sqlite,
    recriar_tabelas_sqlite,
)


class ImagemRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def replace_all(self, imagens: list[Imagem]) -> None:
        recriar_tabelas_sqlite(self.sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(self.sqlite_path)

        with self.sessionmaker() as session:
            tags_cache: dict[str, Tag] = {}
            for imagem in imagens:
                imagem_persistivel = Imagem(
                    nome_arquivo=imagem.nome_arquivo,
                    fazenda=imagem.fazenda,
                    peso=imagem.peso,
                )
                imagem_persistivel.tags = []

                for nome_tag in dict.fromkeys(imagem.nomes_tags):
                    tag = tags_cache.get(nome_tag)
                    if tag is None:
                        tag = session.get(Tag, nome_tag) or Tag(nome_tag=nome_tag)
                        tags_cache[nome_tag] = tag
                    imagem_persistivel.tags.append(tag)

                session.add(imagem_persistivel)

            session.commit()

    def save(self, imagem: Imagem) -> Imagem:
        with self.sessionmaker() as session:
            merged = session.merge(imagem)
            session.commit()
            return merged

    def get(self, nome_arquivo: str) -> Imagem | None:
        with self.sessionmaker() as session:
            return session.scalar(
                select(Imagem)
                .options(
                    selectinload(Imagem.tags),
                    selectinload(Imagem.ground_truth_binarizada),
                    selectinload(Imagem.segmentacoes).selectinload(
                        Segmentacao.binarizacoes
                    ),
                )
                .where(Imagem.nome_arquivo == nome_arquivo)
            )

    def list(self) -> list[Imagem]:
        with self.sessionmaker() as session:
            return cast(
                list[Imagem],
                session.scalars(
                    select(Imagem)
                    .options(
                        selectinload(Imagem.tags),
                        selectinload(Imagem.ground_truth_binarizada),
                        selectinload(Imagem.segmentacoes).selectinload(
                            Segmentacao.binarizacoes
                        ),
                    )
                    .order_by(Imagem.nome_arquivo)
                ).all(),
            )

    def delete(self, nome_arquivo: str) -> None:
        with self.sessionmaker() as session:
            imagem = session.get(Imagem, nome_arquivo)
            if imagem is None:
                return
            session.delete(imagem)
            session.commit()
