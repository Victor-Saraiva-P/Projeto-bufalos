import os
from dataclasses import dataclass

from PIL import Image

from src.segmentacao.logs import (
    imprimir_resumo_verificacao_png as imprimir_logs_verificacao_png,
)


@dataclass(frozen=True)
class ResumoVerificacaoPng:
    total_png: int
    arquivos_integros: int
    arquivos_removidos: int
    falhas_remocao: int


def verificar_e_limpar_pngs_corrompidos(
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
    _imprimir_resumo_verificacao_png(resumo)
    return resumo


def _imprimir_resumo_verificacao_png(resumo: ResumoVerificacaoPng) -> None:
    imprimir_logs_verificacao_png(
        total_png=resumo.total_png,
        arquivos_integros=resumo.arquivos_integros,
        arquivos_removidos=resumo.arquivos_removidos,
        falhas_remocao=resumo.falhas_remocao,
    )
