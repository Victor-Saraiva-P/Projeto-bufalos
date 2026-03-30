from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.sqlite_base import Base

if TYPE_CHECKING:
    from src.models.imagem_model import Imagem


class GroundTruthBinarizada(Base):
    __tablename__ = "ground_of_truth_binarizada"

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        ForeignKey("imagem.nome_arquivo"),
        primary_key=True,
    )
    area: Mapped[float] = mapped_column(Float, nullable=False)
    perimetro: Mapped[float] = mapped_column(Float, nullable=False)

    imagem: Mapped["Imagem"] = relationship("Imagem", back_populates="ground_truth_binarizada")

    def __repr__(self) -> str:
        return (
            "GroundTruthBinarizada("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"area={self.area!r}, "
            f"perimetro={self.perimetro!r})"
        )
