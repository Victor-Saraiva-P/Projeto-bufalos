import os
from collections.abc import Iterable, Mapping
import time

from PIL import Image

from src.config import PREDICTED_MASKS_DIR
from src.io.path_utils import (
    caminho_foto_original,
    caminho_ground_truth,
    caminho_mascara_predita,
)
from src.segmentacao.integracoes import (
    obter_api_rembg,
    obter_resolvedor_providers,
)
from src.segmentacao.logging.logs_segmentacao import (
    EstatisticasProcessamentoComEta,
    imprimir_resumo_modelo,
    imprimir_status,
)
from src.models.indice_linha import IndiceLinha


def executar_segmentacao(
    indice_excel: Iterable[IndiceLinha],
    modelos_para_avaliacao: Mapping[str, str],
) -> dict[str, EstatisticasProcessamentoComEta]:
    linhas_indice = list(indice_excel)
    total_previsto = len(modelos_para_avaliacao) * len(linhas_indice)
    stats_geral = EstatisticasProcessamentoComEta(total=total_previsto)
    resumos_modelo: dict[str, EstatisticasProcessamentoComEta] = {}
    resolver_providers = obter_resolvedor_providers()

    for nome_modelo, provider_config in modelos_para_avaliacao.items():
        providers = resolver_providers(provider_config, nome_modelo)
        print(f"Iniciando modelo: {nome_modelo} (provider: {provider_config})")

        stats_modelo = EstatisticasProcessamentoComEta(total=len(linhas_indice))
        resumos_modelo[nome_modelo] = stats_modelo

        rembg_session = _criar_sessao_segmentacao(nome_modelo, providers)
        output_dir = os.path.join(PREDICTED_MASKS_DIR, nome_modelo)
        os.makedirs(output_dir, exist_ok=True)

        for linha in linhas_indice:
            _segmentar_linha(
                linha=linha,
                nome_modelo=nome_modelo,
                rembg_session=rembg_session,
                stats_geral=stats_geral,
                stats_modelo=stats_modelo,
            )

        imprimir_resumo_modelo(nome_modelo, stats_modelo)

    return resumos_modelo


def _criar_sessao_segmentacao(nome_modelo: str, providers: list[str]):
    new_session, _ = obter_api_rembg()

    try:
        return new_session(nome_modelo, providers=providers)
    except Exception as erro:
        print(f" - Falha ao iniciar sessao com providers {providers}: {erro}")
        print(" - Recriando sessao em CPU...")
        return new_session(nome_modelo, providers=["CPUExecutionProvider"])


def _segmentar_linha(
    linha: IndiceLinha,
    nome_modelo: str,
    rembg_session,
    stats_geral: EstatisticasProcessamentoComEta,
    stats_modelo: EstatisticasProcessamentoComEta,
) -> None:
    original_path = caminho_foto_original(linha.nome_arquivo)
    mascara_path = caminho_ground_truth(linha.nome_arquivo)
    output_path = caminho_mascara_predita(nome_modelo, linha.nome_arquivo)

    if not os.path.isfile(original_path):
        print(f"[ERRO ] Arquivo original nao encontrado: {original_path}")
        stats_geral.registrar_erro()
        stats_modelo.registrar_erro()
        _imprimir_progresso(stats_geral, stats_modelo, nome_modelo)
        return

    if not os.path.isfile(mascara_path):
        print(f"[ERRO ] Arquivo de mascara nao encontrado: {mascara_path}")
        stats_geral.registrar_erro()
        stats_modelo.registrar_erro()
        _imprimir_progresso(stats_geral, stats_modelo, nome_modelo)
        return

    if os.path.isfile(output_path):
        stats_geral.registrar_skip()
        stats_modelo.registrar_skip()
        _imprimir_progresso(stats_geral, stats_modelo, nome_modelo)
        return

    try:
        _, remove = obter_api_rembg()
        inicio_inferencia = time.perf_counter()
        with Image.open(original_path) as input_rembg:
            # Docs: decisoes-tecnicas/mascaras-do-rembg.md
            output_rembg = remove(
                input_rembg,
                only_mask=True,
                session=rembg_session,
            )
        output_rembg.save(output_path)

        duracao_inferencia = time.perf_counter() - inicio_inferencia
        stats_geral.registrar_ok_com_duracao(duracao_inferencia)
        stats_modelo.registrar_ok_com_duracao(duracao_inferencia)
    except Exception as erro:
        print(
            f"[ERRO ] Falha ao segmentar {linha.nome_arquivo} "
            f"no modelo {nome_modelo}: {erro}"
        )
        stats_geral.registrar_erro()
        stats_modelo.registrar_erro()

    _imprimir_progresso(stats_geral, stats_modelo, nome_modelo)


def _imprimir_progresso(
    stats_geral: EstatisticasProcessamentoComEta,
    stats_modelo: EstatisticasProcessamentoComEta,
    nome_modelo: str,
) -> None:
    imprimir_status(stats_geral, stats_modelo, nome_modelo)
