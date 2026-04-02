from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.sqlite_base import Base

if TYPE_CHECKING:
    from src.models.binarizacao_model import SegmentacaoBinarizada
    from src.models.imagem_model import Imagem


class SegmentacaoBruta(Base):
    AUPRC_NAO_CALCULADA = -1.0

    __tablename__ = "segmentacao_bruta"

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        ForeignKey("imagem.nome_arquivo"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    execucao: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    auprc: Mapped[float] = mapped_column(Float, nullable=False)

    imagem: Mapped["Imagem"] = relationship("Imagem", back_populates="segmentacoes_brutas")
    segmentacoes_binarizadas: Mapped[list["SegmentacaoBinarizada"]] = relationship(
        "SegmentacaoBinarizada",
        back_populates="segmentacao_bruta",
        cascade="all, delete-orphan",
    )

    @property
    def binarizacoes(self) -> list["SegmentacaoBinarizada"]:
        return self.segmentacoes_binarizadas

    @binarizacoes.setter
    def binarizacoes(self, value: list["SegmentacaoBinarizada"]) -> None:
        self.segmentacoes_binarizadas = value

    def __repr__(self) -> str:
        return (
            "SegmentacaoBruta("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"nome_modelo={self.nome_modelo!r}, "
            f"execucao={self.execucao!r}, "
            f"auprc={self.auprc!r})"
        )
