from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBinarizadaResumoExecucao(Base):
    __tablename__ = "analise_segmentacao_binarizada_resumo_execucao"

    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    estrategia_binarizacao: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    execucao: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    mean: Mapped[float] = mapped_column(Float, nullable=False)
    median: Mapped[float] = mapped_column(Float, nullable=False)
    std: Mapped[float] = mapped_column(Float, nullable=False)
    min: Mapped[float] = mapped_column(Float, nullable=False)
    max: Mapped[float] = mapped_column(Float, nullable=False)
    q1: Mapped[float] = mapped_column(Float, nullable=False)
    q3: Mapped[float] = mapped_column(Float, nullable=False)
    iqr: Mapped[float] = mapped_column(Float, nullable=False)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, nullable=False)

