from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBrutaBase(Base):
    __tablename__ = "analise_segmentacao_bruta_base"

    nome_arquivo: Mapped[str] = mapped_column(
        String,
        ForeignKey("imagem.nome_arquivo"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    execucao: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    fazenda: Mapped[str] = mapped_column(String, nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    auprc: Mapped[float] = mapped_column(Float, nullable=False)
    soft_dice: Mapped[float] = mapped_column(Float, nullable=False)
    brier_score: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[str] = mapped_column(String, nullable=False, default="")
    tags_sem_ok: Mapped[str] = mapped_column(String, nullable=False, default="")
    num_tags_problema: Mapped[int] = mapped_column(Integer, nullable=False)
    tem_tag_problema: Mapped[bool] = mapped_column(Boolean, nullable=False)
    grupo_dificuldade: Mapped[str] = mapped_column(String, nullable=False)
    tag_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_multi_bufalos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_cortado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_angulo_extremo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_baixo_contraste: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_ocluido: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return (
            "AnaliseSegmentacaoBrutaBase("
            f"nome_arquivo={self.nome_arquivo!r}, "
            f"nome_modelo={self.nome_modelo!r}, "
            f"execucao={self.execucao!r})"
        )
