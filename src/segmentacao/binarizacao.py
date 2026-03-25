from collections.abc import Iterable, Mapping
import os
from PIL import Image

from src.io.path_utils import (
    caminho_ground_truth,
    caminho_ground_truth_binaria,
    caminho_mascara_predita,
    caminho_mascara_predita_binaria,
)
from src.models.indice_linha import IndiceLinha
from src.segmentacao.binarizacoes import BinarizationStrategy
from src.segmentacao.logging.logs_binarizacao import (
    EstatisticasBinarizacao,
    imprimir_resumo_binarizacao,
    imprimir_resumo_binarizacao_modelo,
    imprimir_status_binarizacao,
)


def processar_arquivo_binarizacao(
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


def _caminho_diretorio_mascara_predita_modelo(
    nome_modelo: str,
    linhas_indice: list[IndiceLinha],
) -> str:
    if linhas_indice:
        return os.path.dirname(
            caminho_mascara_predita(nome_modelo, linhas_indice[0].nome_arquivo),
        )

    return os.path.dirname(caminho_mascara_predita(nome_modelo, ""))


def binarizar_ground_truth(
    indice_excel: Iterable[IndiceLinha],
    strategy: BinarizationStrategy,
) -> EstatisticasBinarizacao:
    linhas_indice = list(indice_excel)
    stats = EstatisticasBinarizacao(total=len(linhas_indice))

    print("Convertendo Ground Truth para PNG binarizado")

    for idx, linha in enumerate(linhas_indice, start=1):
        resultado = processar_arquivo_binarizacao(
            caminho_entrada=caminho_ground_truth(linha.nome_arquivo),
            caminho_saida=caminho_ground_truth_binaria(linha.nome_arquivo),
            strategy=strategy,
        )
        stats.registrar_resultado(resultado)
        imprimir_status_binarizacao(
            etapa="ground_truth",
            identificador=f"{idx}/{len(linhas_indice)}",
            stats=stats,
        )

    imprimir_resumo_binarizacao("ground_truth", stats)
    return stats


def binarizar_mascaras_preditas(
    indice_excel: Iterable[IndiceLinha],
    modelos_para_avaliacao: Mapping[str, str],
    strategy: BinarizationStrategy,
) -> dict[str, EstatisticasBinarizacao]:
    linhas_indice = list(indice_excel)
    resumos: dict[str, EstatisticasBinarizacao] = {}

    print("Binarizando mascaras dos modelos")

    for nome_modelo in modelos_para_avaliacao:
        stats = EstatisticasBinarizacao(total=len(linhas_indice))
        resumos[nome_modelo] = stats
        diretorio_modelo = _caminho_diretorio_mascara_predita_modelo(
            nome_modelo,
            linhas_indice,
        )

        if not os.path.isdir(diretorio_modelo):
            print(
                "[AVISO BINARIZACAO] "
                f"Diretorio de mascaras nao encontrado para o modelo "
                f"{nome_modelo}: {diretorio_modelo}. Pulando modelo."
            )
            for _ in linhas_indice:
                stats.registrar_skip()
            imprimir_resumo_binarizacao_modelo(nome_modelo, stats)
            continue

        for idx, linha in enumerate(linhas_indice, start=1):
            resultado = processar_arquivo_binarizacao(
                caminho_entrada=caminho_mascara_predita(nome_modelo, linha.nome_arquivo),
                caminho_saida=caminho_mascara_predita_binaria(
                    nome_modelo,
                    linha.nome_arquivo,
                ),
                strategy=strategy,
            )
            stats.registrar_resultado(resultado)
            imprimir_status_binarizacao(
                etapa="modelo",
                identificador=f"{nome_modelo} {idx}/{len(linhas_indice)}",
                stats=stats,
            )

        imprimir_resumo_binarizacao_modelo(nome_modelo, stats)

    return resumos
