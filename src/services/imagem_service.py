from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image

from src.io.indice_loader import carregar_indice_excel
from src.logs import imprimir_resumo_verificacao_png
from src.repositories import ImagemRepository


@dataclass(frozen=True)
class ResumoVerificacaoPng:
    total_png: int
    arquivos_integros: int
    arquivos_removidos: int
    falhas_remocao: int


class ImagemService:
    @staticmethod
    def sincronizar_indice_excel(
            imagem_repository: ImagemRepository,
        indice_path: str,
    ) -> None:
        imagens = carregar_indice_excel(indice_path)
        imagem_repository.replace_all(imagens)

    @staticmethod
    def verificar_pngs_corrompidos(
            diretorio_base: str,
        extensao_arquivo: str,
    ) -> ResumoVerificacaoPng:
        total_png = 0
        arquivos_integros = 0
        arquivos_removidos = 0
        falhas_remocao = 0
        extensao_normalizada = extensao_arquivo.lower()

        for raiz, _, arquivos in os.walk(diretorio_base):
            for nome_arquivo in arquivos:
                if not nome_arquivo.lower().endswith(extensao_normalizada):
                    continue

                total_png += 1
                caminho_arquivo = os.path.join(raiz, nome_arquivo)

                try:
                    with Image.open(caminho_arquivo) as img:
                        img.verify()

                    with Image.open(caminho_arquivo) as img:
                        img.load()

                    arquivos_integros += 1
                except Exception as erro:
                    print(f"Corrompido detectado: {caminho_arquivo}")
                    print(f" - Erro: {erro}")

                    try:
                        os.remove(caminho_arquivo)
                        arquivos_removidos += 1
                        print(" - Arquivo removido com sucesso.")
                    except OSError as erro_remocao:
                        falhas_remocao += 1
                        print(f" - Falha ao remover arquivo: {erro_remocao}")

        resumo = ResumoVerificacaoPng(
            total_png=total_png,
            arquivos_integros=arquivos_integros,
            arquivos_removidos=arquivos_removidos,
            falhas_remocao=falhas_remocao,
        )
        imprimir_resumo_verificacao_png(resumo)
        return resumo
