from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.base import Base

if TYPE_CHECKING:
    from src.models.segmentacao import Segmentacao
    from src.models.ground_truth_binarizada import GroundTruthBinarizada
    from src.models.tag import Tag


class Imagem(Base):
    __tablename__ = "imagem"

    nome_arquivo: Mapped[str] = mapped_column(String, primary_key=True)
    fazenda: Mapped[str] = mapped_column(String, nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)

    ground_truth_binarizada: Mapped["GroundTruthBinarizada | None"] = relationship(
        "GroundTruthBinarizada",
        back_populates="imagem",
        cascade="all, delete-orphan",
        uselist=False,
    )
    segmentacoes: Mapped[list["Segmentacao"]] = relationship(
        "Segmentacao",
        back_populates="imagem",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="imagem_tag",
        back_populates="imagens",
    )

    @property
    def nomes_tags(self) -> list[str]:
        return sorted(tag.nome_tag for tag in self.tags)

    def __repr__(self) -> str:
        return (
            "Imagem("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"fazenda={self.fazenda!r}, "
            f"peso={self.peso!r})"
        )
