from __future__ import annotations

import os

from PIL import Image

from src.binarizacao.estrategias import BinarizationStrategy
class BinarizacaoService:
    def processar_arquivo(
        self,
        caminho_entrada: str,
        caminho_saida: str,
        strategy: BinarizationStrategy,
    ) -> str:
        if not os.path.isfile(caminho_entrada):
            print(f"ERRO: Mascara nao encontrada: {caminho_entrada}")
            return "erro"

        if os.path.isfile(caminho_saida):
            return "skip"

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

        try:
            with Image.open(caminho_entrada) as image:
                image_binarizada = strategy.binarizar(image)
                image_binarizada.save(caminho_saida, format="PNG")
        except Exception as erro:
            print(f"ERRO ao processar {caminho_entrada}: {erro}")
            return "erro"

        return "ok"
