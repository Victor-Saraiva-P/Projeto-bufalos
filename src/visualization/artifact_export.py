from __future__ import annotations

from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd


def build_artifact_output_dir(
    generated_dir: str | Path,
    notebook_slug: str,
) -> Path:
    output_dir = Path(generated_dir) / notebook_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_artifact_stem(*parts: str) -> str:
    cleaned_parts = [_slugify(part) for part in parts if part and part.strip()]
    if not cleaned_parts:
        raise ValueError("Ao menos uma parte textual e obrigatoria para o nome do artefato.")
    return "_".join(cleaned_parts)


def export_figure_with_csv(
    output_dir: str | Path,
    stem: str,
    figure: plt.Figure,
    data: pd.DataFrame,
    dpi: int = 180,
) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    png_path = output_path / f"{stem}.png"
    csv_path = output_path / f"{stem}.csv"

    figure.savefig(png_path, dpi=dpi, bbox_inches="tight")
    data.to_csv(csv_path, index=False)
    return png_path, csv_path


def export_table_csv(
    output_dir: str | Path,
    stem: str,
    data: pd.DataFrame,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_path = output_path / f"{stem}.csv"
    data.to_csv(csv_path, index=False)
    return csv_path


def _slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("%", "pct")
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")
