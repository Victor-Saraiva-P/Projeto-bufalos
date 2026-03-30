from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.base import Base


class ImagemTag(Base):
    __tablename__ = "imagem_tag"

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        ForeignKey("imagem.nome_arquivo"),
        primary_key=True,
    )
    nome_tag: Mapped[str] = mapped_column(
        String,
        ForeignKey("tag.nome_tag"),
        primary_key=True,
    )
