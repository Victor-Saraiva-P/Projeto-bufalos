from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBinarizadaInteracaoTagEstrategia(Base):
    __tablename__ = "analise_segmentacao_binarizada_interacao_tag_estrategia"

    estrategia_binarizacao: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    tag_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    count_com_tag: Mapped[int] = mapped_column(Integer, nullable=False)
    count_sem_tag: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_com_tag: Mapped[float] = mapped_column(Float, nullable=False)
    mean_sem_tag: Mapped[float] = mapped_column(Float, nullable=False)
    median_com_tag: Mapped[float] = mapped_column(Float, nullable=False)
    median_sem_tag: Mapped[float] = mapped_column(Float, nullable=False)
    delta_mean: Mapped[float] = mapped_column(Float, nullable=False)
    delta_median: Mapped[float] = mapped_column(Float, nullable=False)
    relative_delta_mean: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_delta_mean: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_delta_median: Mapped[float] = mapped_column(Float, nullable=False)
    impact_direction: Mapped[str] = mapped_column(String, nullable=False)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, nullable=False)
