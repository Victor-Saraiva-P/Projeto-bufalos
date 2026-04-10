from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.sqlite_base import Base

if TYPE_CHECKING:
    from src.models.segmentacao_model import SegmentacaoBruta


class SegmentacaoBinarizada(Base):
    __tablename__ = "segmentacao_binarizada"
    __table_args__ = (
        ForeignKeyConstraint(
            ["nome_arquivo", "nome_modelo", "execucao"],
            [
                "segmentacao_bruta.nome_arquivo",
                "segmentacao_bruta.nome_modelo",
                "segmentacao_bruta.execucao",
            ],
        ),
    )

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
        index=True,
    )
    nome_modelo: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
        index=True,
    )
    execucao: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )
    estrategia_binarizacao: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )
    area: Mapped[float] = mapped_column(Float, nullable=False)
    perimetro: Mapped[float] = mapped_column(Float, nullable=False)
    iou: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)

    segmentacao_bruta: Mapped["SegmentacaoBruta"] = relationship(
        "SegmentacaoBruta",
        back_populates="segmentacoes_binarizadas",
    )

    def __repr__(self) -> str:
        return (
            "SegmentacaoBinarizada("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"nome_modelo={self.nome_modelo!r}, "
            f"execucao={self.execucao!r}, "
            f"estrategia_binarizacao={self.estrategia_binarizacao!r}, "
            f"area={self.area!r}, "
            f"perimetro={self.perimetro!r}, "
            f"iou={self.iou!r}, "
            f"precision={self.precision!r}, "
            f"recall={self.recall!r})"
        )
