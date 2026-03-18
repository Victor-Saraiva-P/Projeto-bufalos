from __future__ import annotations

import os
import tkinter as tk
from dataclasses import dataclass

from openpyxl import load_workbook
from PIL import Image, ImageTk

from src.config import IMAGES_DIR, INDICE_PATH, TAGS_COL
from src.io.indice_loader import carregar_indice_excel
from src.io.path_utils import caminho_foto_original
from src.models.indice_linha import IndiceLinha


TAG_OPTIONS = [
    "multi_bufalos",
    "cortado",
    "angulo_extremo",
    "ocluido",
]
MAX_IMAGE_SIZE = (1100, 700)
BUTTON_DEFAULT_BG = "#d6d3d1"
BUTTON_SELECTED_BG = "#0f766e"
BUTTON_DEFAULT_FG = "#1c1917"
BUTTON_SELECTED_FG = "#f5f5f4"


@dataclass(frozen=True)
class PendingImage:
    row_number: int
    line_number: int
    indice_linha: IndiceLinha


def _resolve_image_path(nome_arquivo: str) -> str:
    caminho_padrao = caminho_foto_original(nome_arquivo)
    if os.path.exists(caminho_padrao):
        return caminho_padrao

    caminho_direto = os.path.join(IMAGES_DIR, nome_arquivo)
    if os.path.exists(caminho_direto):
        return caminho_direto

    raise FileNotFoundError(
        f"Imagem nao encontrada para '{nome_arquivo}'. "
        f"Tentativas: '{caminho_padrao}' e '{caminho_direto}'."
    )


def _is_pending(tags: list[str]) -> bool:
    return len(tags) == 0


class ExcelTagRepository:
    def __init__(self, indice_path: str = INDICE_PATH, tags_col: str = TAGS_COL):
        self.indice_path = indice_path
        self.tags_col = tags_col

    def get_next_pending(self) -> PendingImage | None:
        linhas = carregar_indice_excel()

        for idx, linha in enumerate(linhas, start=2):
            if _is_pending(linha.tags):
                return PendingImage(
                    row_number=idx,
                    line_number=idx - 1,
                    indice_linha=linha,
                )

        return None

    def save_tags(self, row_number: int, tags_value: str) -> None:
        workbook = load_workbook(self.indice_path)
        worksheet = workbook.active
        header_map = {
            str(cell.value).strip().lower(): cell.column
            for cell in worksheet[1]
            if cell.value is not None
        }
        tags_column = header_map.get(self.tags_col)

        if tags_column is None:
            tags_column = worksheet.max_column + 1
            worksheet.cell(row=1, column=tags_column, value=self.tags_col)

        worksheet.cell(row=row_number, column=tags_column, value=tags_value)
        workbook.save(self.indice_path)


class ManualTaggerApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Tag de imagens")
        self.master.geometry("1280x920")

        self.repository = ExcelTagRepository()
        self.selected_tags: set[str] = set()
        self.current_pending: PendingImage | None = None
        self.button_by_tag: dict[str, tk.Button] = {}
        self.tk_image: ImageTk.PhotoImage | None = None
        self.image_available = False

        self._build_layout()
        self._bind_keys()
        self._load_next_pending()

    def _build_layout(self) -> None:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        top_frame = tk.Frame(self.master, padx=16, pady=12)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            top_frame,
            text="Carregando...",
            anchor="w",
            justify="left",
            font=("Helvetica", 14, "bold"),
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        self.hint_label = tk.Label(
            top_frame,
            text="Selecione tags com os numeros e confirme com Enter.",
            anchor="w",
            justify="left",
            font=("Helvetica", 11),
        )
        self.hint_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        image_frame = tk.Frame(self.master, padx=16, pady=8)
        image_frame.grid(row=1, column=0, sticky="nsew")
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)

        self.image_label = tk.Label(
            image_frame,
            text="",
            bd=1,
            relief="solid",
            anchor="center",
        )
        self.image_label.grid(row=0, column=0, sticky="nsew")

        controls_frame = tk.Frame(self.master, padx=16, pady=16)
        controls_frame.grid(row=2, column=0, sticky="ew")
        controls_frame.columnconfigure(len(TAG_OPTIONS), weight=1)

        for idx, tag in enumerate(TAG_OPTIONS, start=1):
            button = tk.Button(
                controls_frame,
                text=f"{idx}. {tag}",
                width=18,
                padx=10,
                pady=14,
                command=lambda current_tag=tag: self.toggle_tag(current_tag),
            )
            button.grid(row=0, column=idx - 1, padx=6, pady=4, sticky="ew")
            self.button_by_tag[tag] = button

        self.finish_button = tk.Button(
            controls_frame,
            text="Enter. Finalizar",
            width=18,
            padx=10,
            pady=14,
            bg="#2563eb",
            fg="#eff6ff",
            activebackground="#1d4ed8",
            activeforeground="#eff6ff",
            command=self.finish_current_image,
        )
        self.finish_button.grid(
            row=0,
            column=len(TAG_OPTIONS),
            padx=(18, 6),
            pady=4,
            sticky="ew",
        )

        self._refresh_buttons()

    def _bind_keys(self) -> None:
        for idx, tag in enumerate(TAG_OPTIONS, start=1):
            self.master.bind(str(idx), lambda event, current_tag=tag: self.toggle_tag(current_tag))
        self.master.bind("<Return>", lambda event: self.finish_current_image())

    def _refresh_buttons(self) -> None:
        for tag, button in self.button_by_tag.items():
            is_selected = tag in self.selected_tags
            button.configure(
                bg=BUTTON_SELECTED_BG if is_selected else BUTTON_DEFAULT_BG,
                fg=BUTTON_SELECTED_FG if is_selected else BUTTON_DEFAULT_FG,
                activebackground=BUTTON_SELECTED_BG if is_selected else BUTTON_DEFAULT_BG,
                activeforeground=BUTTON_SELECTED_FG if is_selected else BUTTON_DEFAULT_FG,
                relief="sunken" if is_selected else "raised",
            )

    def toggle_tag(self, tag: str) -> None:
        if self.current_pending is None:
            return

        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.add(tag)

        self._refresh_buttons()

    def finish_current_image(self) -> None:
        if self.current_pending is None or not self.image_available:
            return

        tags_value = self._build_tags_value()
        self.repository.save_tags(self.current_pending.row_number, tags_value)
        self._load_next_pending()

    def _build_tags_value(self) -> str:
        selected = [tag for tag in TAG_OPTIONS if tag in self.selected_tags]
        if not selected:
            return "ok"

        return ", ".join(selected)

    def _load_next_pending(self) -> None:
        self.selected_tags.clear()
        self.image_available = False
        self._refresh_buttons()

        pending = self.repository.get_next_pending()
        self.current_pending = pending

        if pending is None:
            self.status_label.configure(text="Nao ha mais imagens para tag-acao.")
            self.hint_label.configure(text="Todas as linhas da coluna tags ja foram preenchidas.")
            self.image_label.configure(image="", text="Fila concluida.")
            self.finish_button.configure(state="disabled")
            return

        self.finish_button.configure(state="normal")
        linha = pending.indice_linha
        self.status_label.configure(
            text=(
                f"Linha {pending.line_number}: {linha.nome_arquivo} | "
                f"fazenda={linha.fazenda} | peso={linha.peso}"
            )
        )
        self.hint_label.configure(
            text="Enter sem selecao grava ok. Numeros alternam as tags."
        )

        try:
            image_path = _resolve_image_path(linha.nome_arquivo)
            self._display_image(image_path)
            self.finish_button.configure(state="normal")
        except FileNotFoundError as exc:
            self.tk_image = None
            self.finish_button.configure(state="disabled")
            self.image_label.configure(
                image="",
                text=str(exc),
                justify="center",
                wraplength=1000,
            )

    def _display_image(self, image_path: str) -> None:
        image = Image.open(image_path)
        image.thumbnail(MAX_IMAGE_SIZE)
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_available = True
        self.image_label.configure(image=self.tk_image, text="")


def main() -> None:
    root = tk.Tk()
    ManualTaggerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
