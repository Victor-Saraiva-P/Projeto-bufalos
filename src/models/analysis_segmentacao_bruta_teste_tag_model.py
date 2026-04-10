from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.sqlite.sqlite_base import Base


class AnaliseSegmentacaoBrutaTesteTag(Base):
    __tablename__ = "analise_segmentacao_bruta_teste_tag"

    metric_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    tag_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    comparison_scope: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    nome_modelo: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    test_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    n_group_a: Mapped[int] = mapped_column(Integer, nullable=False)
    n_group_b: Mapped[int] = mapped_column(Integer, nullable=False)
    statistic: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, nullable=False)
    p_value_adjusted: Mapped[float] = mapped_column(Float, nullable=False)
    effect_size: Mapped[float] = mapped_column(Float, nullable=False)
    effect_size_label: Mapped[str] = mapped_column(String, nullable=False)
    mean_com_tag: Mapped[float] = mapped_column(Float, nullable=False)
    mean_sem_tag: Mapped[float] = mapped_column(Float, nullable=False)
    median_com_tag: Mapped[float] = mapped_column(Float, nullable=False)
    median_sem_tag: Mapped[float] = mapped_column(Float, nullable=False)
    delta_mean: Mapped[float] = mapped_column(Float, nullable=False)
    delta_median: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        return (
            "AnaliseSegmentacaoBrutaTesteTag("
            f"metric_name={self.metric_name!r}, "
            f"tag_name={self.tag_name!r}, "
            f"comparison_scope={self.comparison_scope!r}, "
            f"nome_modelo={self.nome_modelo!r})"
        )
