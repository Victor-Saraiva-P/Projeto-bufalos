from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import os
import time

from PIL import Image

from src.segmentacao.integracoes import obter_api_rembg


@dataclass(frozen=True)
class ResultadoSegmentacaoArquivo:
    status: str
    duracao_inferencia: float | None = None


class SegmentacaoService:
    @staticmethod
    def criar_sessao_segmentacao(nome_modelo: str, providers: list[str]):
        new_session, _ = obter_api_rembg()

        try:
            return new_session(nome_modelo, providers=providers)
        except Exception as erro:
            print(f" - Falha ao iniciar sessao com providers {providers}: {erro}")
            print(" - Recriando sessao em CPU...")
            return new_session(nome_modelo, providers=["CPUExecutionProvider"])

    @staticmethod
    def segmentar_arquivo(
            nome_arquivo: str,
        nome_modelo: str,
        original_path: str,
        mascara_path: str,
        output_path: str,
        rembg_session,
        remove_mask: Callable | None = None,
    ) -> ResultadoSegmentacaoArquivo:
        if not os.path.isfile(original_path):
            print(f"[ERRO ] Arquivo original nao encontrado: {original_path}")
            return ResultadoSegmentacaoArquivo(status="erro")

        if not os.path.isfile(mascara_path):
            print(f"[ERRO ] Arquivo de mascara nao encontrado: {mascara_path}")
            return ResultadoSegmentacaoArquivo(status="erro")

        if os.path.isfile(output_path):
            return ResultadoSegmentacaoArquivo(status="skip")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        remove = remove_mask or obter_api_rembg()[1]

        try:
            inicio_inferencia = time.perf_counter()
            with Image.open(original_path) as input_rembg:
                output_rembg = remove(
                    input_rembg,
                    only_mask=True,
                    session=rembg_session,
                )
            output_rembg.save(output_path)
        except Exception as erro:
            print(
                f"[ERRO ] Falha ao segmentar {nome_arquivo} "
                f"no modelo {nome_modelo}: {erro}"
            )
            return ResultadoSegmentacaoArquivo(status="erro")

        duracao_inferencia = time.perf_counter() - inicio_inferencia
        return ResultadoSegmentacaoArquivo(
            status="ok",
            duracao_inferencia=duracao_inferencia,
        )
