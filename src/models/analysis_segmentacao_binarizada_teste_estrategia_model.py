from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBinarizadaTesteEstrategia(Base):
    __tablename__ = "analise_segmentacao_binarizada_teste_estrategia"

    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    modelo_origem: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    comparison_scope: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    test_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    group_a: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    group_b: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    n_group_a: Mapped[int] = mapped_column(Integer, nullable=False)
    n_group_b: Mapped[int] = mapped_column(Integer, nullable=False)
    statistic: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, nullable=False)
    p_value_adjusted: Mapped[float] = mapped_column(Float, nullable=False)
    effect_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    effect_size_label: Mapped[str | None] = mapped_column(String, nullable=True)
    mean_group_a: Mapped[float] = mapped_column(Float, nullable=False)
    mean_group_b: Mapped[float] = mapped_column(Float, nullable=False)
    median_group_a: Mapped[float] = mapped_column(Float, nullable=False)
    median_group_b: Mapped[float] = mapped_column(Float, nullable=False)
    favored_group: Mapped[str | None] = mapped_column(String, nullable=True)

