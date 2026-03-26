from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class IndiceORM(Base):
    __tablename__ = "indice"

    nome_arquivo: Mapped[str] = mapped_column(String, primary_key=True)
    fazenda: Mapped[str] = mapped_column(String, nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[str | None] = mapped_column(String, nullable=True)

    avaliacao: Mapped["AvaliacaoImagemORM | None"] = relationship(
        back_populates="indice",
        cascade="all, delete-orphan",
        uselist=False,
    )


class AvaliacaoImagemORM(Base):
    __tablename__ = "avaliacao_imagem"

    nome_arquivo: Mapped[str] = mapped_column(
        ForeignKey("indice.nome_arquivo"),
        primary_key=True,
    )
    area_ground_truth: Mapped[float | None] = mapped_column(Float, nullable=True)
    perimetro_ground_truth: Mapped[float | None] = mapped_column(Float, nullable=True)

    indice: Mapped[IndiceORM] = relationship(back_populates="avaliacao")
    modelos: Mapped[list["AvaliacaoModeloORM"]] = relationship(
        back_populates="avaliacao",
        cascade="all, delete-orphan",
    )


class AvaliacaoModeloORM(Base):
    __tablename__ = "avaliacao_modelo"
    __table_args__ = (UniqueConstraint("nome_arquivo", "modelo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome_arquivo: Mapped[str] = mapped_column(
        ForeignKey("avaliacao_imagem.nome_arquivo"),
        nullable=False,
        index=True,
    )
    modelo: Mapped[str] = mapped_column(String, nullable=False)
    area: Mapped[float | None] = mapped_column(Float, nullable=True)
    perimetro: Mapped[float | None] = mapped_column(Float, nullable=True)
    iou: Mapped[float | None] = mapped_column(Float, nullable=True)

    avaliacao: Mapped[AvaliacaoImagemORM] = relationship(back_populates="modelos")
