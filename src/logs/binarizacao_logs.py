from src.logs.logs_base import EstatisticasLogGeral, formatar_nome_execucao


class EstatisticasBinarizacao(EstatisticasLogGeral):
    pass


def imprimir_status_binarizacao(
    etapa: str,
    stats: EstatisticasBinarizacao,
    identificador: str | None = None,
    nome_modelo: str | None = None,
    execucao: int | None = None,
    estrategia_binarizacao: str | None = None,
) -> None:
    contexto = [f"[BINARIZACAO {etapa}]"]
    if estrategia_binarizacao is not None:
        contexto.append(estrategia_binarizacao)
    if nome_modelo is not None:
        contexto.append(nome_modelo)
    if execucao is not None:
        contexto.append(formatar_nome_execucao(execucao))
    if identificador is not None:
        contexto.append(identificador)
    print(
        f"{' '.join(contexto)} | "
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
    estrategia_binarizacao: str | None = None,
) -> None:
    nome_lote = f"modelo {nome_modelo}"
    if estrategia_binarizacao is not None:
        nome_lote = f"{nome_lote} {estrategia_binarizacao}"
    imprimir_resumo_binarizacao(nome_lote, stats)


def imprimir_resumo_binarizacao_execucao(
    nome_modelo: str,
    execucao: int,
    stats: EstatisticasBinarizacao,
    estrategia_binarizacao: str | None = None,
) -> None:
    nome_lote = f"modelo {nome_modelo}"
    if estrategia_binarizacao is not None:
        nome_lote = f"{nome_lote} {estrategia_binarizacao}"
    imprimir_resumo_binarizacao(
        f"{nome_lote} {formatar_nome_execucao(execucao)}",
        stats,
    )
