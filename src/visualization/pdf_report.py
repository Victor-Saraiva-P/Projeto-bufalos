from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


@dataclass(frozen=True)
class PdfReportSection:
    heading: str
    body: str
    figures: list[plt.Figure] = field(default_factory=list)


def save_pdf_report(
    output_path: str | Path,
    sections: list[PdfReportSection],
    report_title: str,
) -> Path:
    if not sections:
        raise ValueError("O relatorio PDF precisa conter ao menos uma secao.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(output) as pdf:
        _save_cover_page(pdf, report_title)

        for section in sections:
            if section.figures:
                for figure in section.figures:
                    page = _build_section_figure_page(section.heading, section.body, figure)
                    pdf.savefig(page, bbox_inches="tight")
                    plt.close(page)
            else:
                page = _build_text_only_page(section.heading, section.body)
                pdf.savefig(page, bbox_inches="tight")
                plt.close(page)

    return output


def _save_cover_page(pdf: PdfPages, report_title: str) -> None:
    figure = plt.figure(figsize=(8.27, 11.69))
    axis = figure.add_axes([0, 0, 1, 1])
    axis.axis("off")
    axis.text(
        0.5,
        0.72,
        report_title,
        ha="center",
        va="center",
        fontsize=24,
        fontweight="bold",
        wrap=True,
    )
    axis.text(
        0.5,
        0.58,
        "Relatorio visual gerado pelo notebook 05 da segmentacao bruta.",
        ha="center",
        va="center",
        fontsize=12,
        wrap=True,
    )
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _build_text_only_page(heading: str, body: str) -> plt.Figure:
    figure = plt.figure(figsize=(8.27, 11.69))
    axis = figure.add_axes([0.08, 0.08, 0.84, 0.84])
    axis.axis("off")
    axis.text(0.0, 1.0, heading, ha="left", va="top", fontsize=18, fontweight="bold")
    axis.text(
        0.0,
        0.92,
        _wrap_body(body),
        ha="left",
        va="top",
        fontsize=11,
        linespacing=1.5,
        wrap=True,
    )
    return figure


def _build_section_figure_page(
    heading: str,
    body: str,
    source_figure: plt.Figure,
) -> plt.Figure:
    buffer = BytesIO()
    source_figure.savefig(buffer, format="png", dpi=180, bbox_inches="tight")
    buffer.seek(0)
    image = plt.imread(buffer)

    page = plt.figure(figsize=(8.27, 11.69))
    text_axis = page.add_axes([0.08, 0.74, 0.84, 0.18])
    text_axis.axis("off")
    text_axis.text(0.0, 1.0, heading, ha="left", va="top", fontsize=18, fontweight="bold")
    text_axis.text(
        0.0,
        0.72,
        _wrap_body(body),
        ha="left",
        va="top",
        fontsize=11,
        linespacing=1.5,
        wrap=True,
    )

    image_axis = page.add_axes([0.08, 0.08, 0.84, 0.6])
    image_axis.imshow(image)
    image_axis.axis("off")
    return page


def _wrap_body(body: str, line_width: int = 95) -> str:
    paragraphs = [paragraph.strip() for paragraph in body.split("\n") if paragraph.strip()]
    return "\n\n".join(textwrap.fill(paragraph, width=line_width) for paragraph in paragraphs)
