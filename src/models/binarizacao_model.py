from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.sqlite.sqlite_base import Base

if TYPE_CHECKING:
    from src.models.segmentacao_model import Segmentacao


class Binarizacao(Base):
    METRICA_NAO_CALCULADA = -1.0

    __tablename__ = "binarizacao"
    __table_args__ = (
        ForeignKeyConstraint(
            ["nome_arquivo", "nome_modelo"],
            ["segmentacao.nome_arquivo", "segmentacao.nome_modelo"],
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
    estrategia_binarizacao: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )
    metrica_x: Mapped[float] = mapped_column(Float, nullable=False)
    metrica_y: Mapped[float] = mapped_column(Float, nullable=False)

    segmentacao: Mapped["Segmentacao"] = relationship(
        "Segmentacao",
        back_populates="binarizacoes",
    )

    @property
    def auprc(self) -> float:
        return float(self.metrica_x)

    @auprc.setter
    def auprc(self, value: float) -> None:
        self.metrica_x = value

    def __repr__(self) -> str:
        return (
            "Binarizacao("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"nome_modelo={self.nome_modelo!r}, "
            f"estrategia_binarizacao={self.estrategia_binarizacao!r}, "
            f"metrica_x={self.metrica_x!r}, "
            f"metrica_y={self.metrica_y!r})"
        )
