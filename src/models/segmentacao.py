from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.base import Base

if TYPE_CHECKING:
    from src.models.binarizacao import Binarizacao
    from src.models.imagem import Imagem


class Segmentacao(Base):
    __tablename__ = "segmentacao"

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        ForeignKey("imagem.nome_arquivo"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    area: Mapped[float] = mapped_column(Float, nullable=False)
    perimetro: Mapped[float] = mapped_column(Float, nullable=False)
    iou: Mapped[float] = mapped_column(Float, nullable=False)

    imagem: Mapped["Imagem"] = relationship("Imagem", back_populates="segmentacoes")
    binarizacoes: Mapped[list["Binarizacao"]] = relationship(
        "Binarizacao",
        back_populates="segmentacao",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            "Segmentacao("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"nome_modelo={self.nome_modelo!r}, "
            f"area={self.area!r}, "
            f"perimetro={self.perimetro!r}, "
            f"iou={self.iou!r})"
        )
