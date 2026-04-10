from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBrutaIntervaloConfianca(Base):
    __tablename__ = "analise_segmentacao_bruta_intervalo_confianca"

    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    statistic_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    estimate: Mapped[float] = mapped_column(Float, nullable=False)
    ci_low: Mapped[float] = mapped_column(Float, nullable=False)
    ci_high: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[float] = mapped_column(Float, nullable=False)
    n_resamples: Mapped[int] = mapped_column(Integer, nullable=False)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return (
            "AnaliseSegmentacaoBrutaIntervaloConfianca("
            f"nome_modelo={self.nome_modelo!r}, "
            f"metric_name={self.metric_name!r}, "
            f"statistic_name={self.statistic_name!r})"
        )
