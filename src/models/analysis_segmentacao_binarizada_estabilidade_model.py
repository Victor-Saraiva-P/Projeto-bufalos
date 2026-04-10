from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBinarizadaEstabilidade(Base):
    __tablename__ = "analise_segmentacao_binarizada_estabilidade"

    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    estrategia_binarizacao: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    count_execucoes: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_execucoes: Mapped[float] = mapped_column(Float, nullable=False)
    std_execucoes: Mapped[float] = mapped_column(Float, nullable=False)
    cv_execucoes: Mapped[float] = mapped_column(Float, nullable=False)
    amplitude_execucoes: Mapped[float] = mapped_column(Float, nullable=False)
    melhor_execucao: Mapped[int] = mapped_column(Integer, nullable=False)
    pior_execucao: Mapped[int] = mapped_column(Integer, nullable=False)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, nullable=False)

