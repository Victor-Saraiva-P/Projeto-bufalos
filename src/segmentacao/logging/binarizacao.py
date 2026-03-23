from src.segmentacao.logging.shared import EstatisticasLogGeral


class EstatisticasBinarizacao(EstatisticasLogGeral):
    pass


def imprimir_status_binarizacao(
    etapa: str,
    identificador: str,
    stats: EstatisticasBinarizacao,
) -> None:
    print(
        f"[BINARIZACAO {etapa}] {identificador} | "
        f"processadas={stats.processadas}/{stats.total} | "
        f"ok={stats.ok} skip={stats.skip} erro={stats.erro}"
    )


def imprimir_resumo_binarizacao(
    nome_lote: str,
    stats: EstatisticasBinarizacao,
) -> None:
    print(f"[RESUMO BINARIZACAO {nome_lote}]")
    print(
        f"total={stats.total} | processadas={stats.processadas} | "
        f"ok={stats.ok} | skip={stats.skip} | erro={stats.erro}"
    )
    print("-" * 100)


def imprimir_resumo_binarizacao_modelo(
    nome_modelo: str,
    stats: EstatisticasBinarizacao,
) -> None:
    imprimir_resumo_binarizacao(f"modelo {nome_modelo}", stats)
