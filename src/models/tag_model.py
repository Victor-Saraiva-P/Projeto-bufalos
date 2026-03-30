from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.sqlite_base import Base

if TYPE_CHECKING:
    from src.models.imagem_model import Imagem


def normalizar_tags(valor: object) -> list[str]:
    if valor is None:
        return []

    tags = str(valor).strip()
    if not tags or tags.lower() == "nan":
        return []

    return [tag.strip() for tag in tags.split(",") if tag.strip()]


class Tag(Base):
    __tablename__ = "tag"

    nome_tag: Mapped[str] = mapped_column(String, primary_key=True)
    imagens: Mapped[list["Imagem"]] = relationship(
        "Imagem",
        secondary="imagem_tag",
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"Tag(nome_tag={self.nome_tag!r})"
