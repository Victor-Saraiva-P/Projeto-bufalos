from __future__ import annotations

import os
import sys
import tkinter as tk
from dataclasses import dataclass

if __package__ is None or __package__ == "":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

from PIL import Image, ImageTk

from src.config import IMAGES_DIR, INDICE_DB_PATH
from src.io.indice_db import atualizar_tags
from src.io.indice_loader import carregar_indice_sqlite
from src.io.path_utils import caminho_foto_original
from src.models.indice_linha import IndiceLinha


TAG_OPTIONS = [
    "multi_bufalos",
    "cortado",
    "angulo_extremo",
    "baixo_contraste",
    "ocluido",
]
MAX_IMAGE_SIZE = (1100, 700)
BUTTON_DEFAULT_BG = "#d6d3d1"
BUTTON_SELECTED_BG = "#0f766e"
BUTTON_DEFAULT_FG = "#1c1917"
BUTTON_SELECTED_FG = "#f5f5f4"


@dataclass(frozen=True)
class PendingImage:
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


def _sanitize_problem_tags(tags: list[str]) -> list[str]:
    sanitized: list[str] = []
    for tag in tags:
        normalized = tag.strip()
        if not normalized:
            continue
        if normalized == "ok":
            continue
        if normalized in sanitized:
            continue
        sanitized.append(normalized)
    return sanitized


class FocusedTagRepository:
    def __init__(self, focus_tag: str, indice_path: str = INDICE_DB_PATH):
        self.focus_tag = focus_tag
        self.indice_path = indice_path
        self.pending_images = self._build_pending_images()
        self.current_index = 0

    def _build_pending_images(self) -> list[PendingImage]:
        linhas = carregar_indice_sqlite()
        return [
            PendingImage(
                line_number=idx - 1,
                indice_linha=linha,
            )
            for idx, linha in enumerate(linhas, start=2)
            if self.focus_tag not in linha.tags
        ]

    def get_current_pending(self) -> PendingImage | None:
        if self.current_index >= len(self.pending_images):
            return None
        return self.pending_images[self.current_index]

    def save_current_and_advance(self, mark_focus_tag: bool) -> PendingImage | None:
        current_pending = self.get_current_pending()
        if current_pending is None:
            return None

        current_tags = current_pending.indice_linha.tags
        next_value = self._build_next_tags_value(current_tags, mark_focus_tag)

        atualizar_tags(
            nome_arquivo=current_pending.indice_linha.nome_arquivo,
            tags=next_value,
            db_path=self.indice_path,
        )
        self.current_index += 1
        return self.get_current_pending()

    def _build_next_tags_value(self, current_tags: list[str], mark_focus_tag: bool) -> str:
        if mark_focus_tag:
            problem_tags = _sanitize_problem_tags(current_tags)
            if self.focus_tag not in problem_tags:
                problem_tags.append(self.focus_tag)
            return ", ".join(problem_tags)

        if len(current_tags) == 0:
            return "ok"

        return ", ".join(current_tags)

    def close(self) -> None:
        return None


class FocusedTaggerApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Tag de imagens por foco")
        self.master.geometry("1280x920")
        self.master.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.selected_focus_tag: str | None = None
        self.pending_mark = False
        self.repository: FocusedTagRepository | None = None
        self.current_pending: PendingImage | None = None
        self.tk_image: ImageTk.PhotoImage | None = None
        self.image_available = False

        self.selector_button_by_tag: dict[str, tk.Button] = {}
        self.review_button: tk.Button | None = None
        self.finish_button: tk.Button | None = None
        self.exit_button: tk.Button | None = None

        self._build_layout()
        self._bind_keys()
        self._show_selector_screen()

    def _build_layout(self) -> None:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        top_frame = tk.Frame(self.master, padx=16, pady=12)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            top_frame,
            text="Escolha a tag para iniciar.",
            anchor="w",
            justify="left",
            font=("Helvetica", 14, "bold"),
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        self.hint_label = tk.Label(
            top_frame,
            text="Use os numeros para escolher a tag e Enter para confirmar.",
            anchor="w",
            justify="left",
            font=("Helvetica", 11),
        )
        self.hint_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.content_frame = tk.Frame(self.master, padx=16, pady=8)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        self.selector_frame = tk.Frame(self.content_frame)
        self.selector_frame.columnconfigure(0, weight=1)

        selector_buttons_frame = tk.Frame(self.selector_frame, padx=24, pady=24)
        selector_buttons_frame.grid(row=0, column=0, sticky="n")

        for idx, tag in enumerate(TAG_OPTIONS, start=1):
            button = tk.Button(
                selector_buttons_frame,
                text=f"{idx}. {tag}",
                width=28,
                padx=10,
                pady=16,
                command=lambda current_tag=tag: self.select_focus_tag(current_tag),
            )
            button.grid(row=idx - 1, column=0, padx=6, pady=6, sticky="ew")
            self.selector_button_by_tag[tag] = button

        self.selector_confirm_button = tk.Button(
            selector_buttons_frame,
            text="Enter. Confirmar tag",
            width=28,
            padx=10,
            pady=16,
            bg="#2563eb",
            fg="#eff6ff",
            activebackground="#1d4ed8",
            activeforeground="#eff6ff",
            command=self.confirm_focus_tag,
        )
        self.selector_confirm_button.grid(row=len(TAG_OPTIONS), column=0, padx=6, pady=(18, 6), sticky="ew")

        self.review_frame = tk.Frame(self.content_frame)
        self.review_frame.columnconfigure(0, weight=1)
        self.review_frame.rowconfigure(0, weight=1)

        self.image_label = tk.Label(
            self.review_frame,
            text="",
            bd=1,
            relief="solid",
            anchor="center",
        )
        self.image_label.grid(row=0, column=0, sticky="nsew")

        controls_frame = tk.Frame(self.master, padx=16, pady=16)
        controls_frame.grid(row=2, column=0, sticky="ew")
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=1)

        self.review_button = tk.Button(
            controls_frame,
            text="1. Tag",
            width=18,
            padx=10,
            pady=14,
            command=self.toggle_focus_mark,
        )
        self.review_button.grid(row=0, column=0, padx=6, pady=4, sticky="ew")

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
        self.finish_button.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        self.exit_button = tk.Button(
            controls_frame,
            text="Sair",
            width=12,
            padx=10,
            pady=14,
            bg="#57534e",
            fg="#fafaf9",
            activebackground="#44403c",
            activeforeground="#fafaf9",
            command=self.exit_app,
        )
        self.exit_button.grid(row=0, column=2, padx=6, pady=4, sticky="ew")

        self._refresh_selector_buttons()
        self._refresh_review_button()

    def _bind_keys(self) -> None:
        for idx, tag in enumerate(TAG_OPTIONS, start=1):
            self.master.bind(str(idx), lambda event, current_tag=tag: self._handle_numeric_key(current_tag))
        self.master.bind("<Return>", lambda event: self._handle_enter())

    def _handle_numeric_key(self, tag: str) -> None:
        if self.repository is None:
            self.select_focus_tag(tag)
            return

        if tag == self.selected_focus_tag:
            self.toggle_focus_mark()

    def _handle_enter(self) -> None:
        if self.repository is None:
            self.confirm_focus_tag()
            return

        self.finish_current_image()

    def _show_selector_screen(self) -> None:
        self.review_frame.grid_forget()
        self.selector_frame.grid(row=0, column=0, sticky="nsew")
        self.review_button.configure(state="disabled")
        self.finish_button.configure(state="disabled")

    def _show_review_screen(self) -> None:
        self.selector_frame.grid_forget()
        self.review_frame.grid(row=0, column=0, sticky="nsew")
        self.review_button.configure(state="normal")
        self.finish_button.configure(state="normal")

    def _refresh_selector_buttons(self) -> None:
        for tag, button in self.selector_button_by_tag.items():
            is_selected = tag == self.selected_focus_tag
            button.configure(
                bg=BUTTON_SELECTED_BG if is_selected else BUTTON_DEFAULT_BG,
                fg=BUTTON_SELECTED_FG if is_selected else BUTTON_DEFAULT_FG,
                activebackground=BUTTON_SELECTED_BG if is_selected else BUTTON_DEFAULT_BG,
                activeforeground=BUTTON_SELECTED_FG if is_selected else BUTTON_DEFAULT_FG,
                relief="sunken" if is_selected else "raised",
            )

    def _refresh_review_button(self) -> None:
        if self.review_button is None:
            return

        tag_label = self.selected_focus_tag or "Tag"
        self.review_button.configure(
            text=f"1. {tag_label}",
            bg=BUTTON_SELECTED_BG if self.pending_mark else BUTTON_DEFAULT_BG,
            fg=BUTTON_SELECTED_FG if self.pending_mark else BUTTON_DEFAULT_FG,
            activebackground=BUTTON_SELECTED_BG if self.pending_mark else BUTTON_DEFAULT_BG,
            activeforeground=BUTTON_SELECTED_FG if self.pending_mark else BUTTON_DEFAULT_FG,
            relief="sunken" if self.pending_mark else "raised",
        )

    def select_focus_tag(self, tag: str) -> None:
        if self.repository is not None:
            return

        self.selected_focus_tag = tag
        self._refresh_selector_buttons()

    def confirm_focus_tag(self) -> None:
        if self.repository is not None or self.selected_focus_tag is None:
            return

        self.repository = FocusedTagRepository(self.selected_focus_tag)
        self._refresh_review_button()
        self._show_review_screen()
        self._load_next_pending()

    def toggle_focus_mark(self) -> None:
        if self.current_pending is None or not self.image_available:
            return

        self.pending_mark = not self.pending_mark
        self._refresh_review_button()

    def finish_current_image(self) -> None:
        if self.repository is None or self.current_pending is None or not self.image_available:
            return

        self.current_pending = self.repository.save_current_and_advance(self.pending_mark)
        self._load_next_pending()

    def exit_app(self) -> None:
        if (
            self.repository is not None
            and self.current_pending is not None
            and self.image_available
            and self.pending_mark
        ):
            self.repository.save_current_and_advance(self.pending_mark)

        if self.repository is not None:
            self.repository.close()
        self.master.destroy()

    def _load_next_pending(self) -> None:
        self.pending_mark = False
        self.image_available = False
        self._refresh_review_button()

        if self.current_pending is None and self.repository is not None:
            self.current_pending = self.repository.get_current_pending()

        pending = self.current_pending

        if pending is None:
            self.status_label.configure(
                text=f"Nao ha mais imagens sem a tag {self.selected_focus_tag}."
            )
            self.hint_label.configure(
                text="Todas as linhas elegiveis para este foco ja foram revisadas."
            )
            self.image_label.configure(image="", text="Fila concluida.")
            self.finish_button.configure(state="disabled")
            self.review_button.configure(state="disabled")
            self.exit_button.configure(state="normal")
            return

        self.finish_button.configure(state="normal")
        self.review_button.configure(state="normal")

        linha = pending.indice_linha
        tags_text = ", ".join(linha.tags) if linha.tags else "sem tags"
        self.status_label.configure(
            text=(
                f"Linha {pending.line_number}: {linha.nome_arquivo} | "
                f"fazenda={linha.fazenda} | peso={linha.peso} | tags atuais={tags_text}"
            )
        )
        self.hint_label.configure(
            text=(
                f"Tecla 1 adiciona {self.selected_focus_tag}. "
                "Enter finaliza; sem selecao grava ok apenas se a celula estiver vazia."
            )
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
    FocusedTaggerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
