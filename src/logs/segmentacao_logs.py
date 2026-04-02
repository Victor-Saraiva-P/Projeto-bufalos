from dataclasses import dataclass, field
import time

from src.logs.logs_base import (
    EstatisticasLogGeral,
    formatar_duracao,
    formatar_nome_execucao,
)


@dataclass
class EstatisticasProcessamentoComEta(EstatisticasLogGeral):
    tempo_inferencia: float = 0.0
    inicio: float = field(default_factory=time.perf_counter)

    def registrar_ok_com_duracao(self, duracao_inferencia: float) -> None:
        super().registrar_ok()
        self.tempo_inferencia += duracao_inferencia

    @property
    def tempo_execucao(self) -> float:
        return time.perf_counter() - self.inicio


def imprimir_status(
    geral: EstatisticasProcessamentoComEta,
    modelo: EstatisticasProcessamentoComEta,
    execucao_stats: EstatisticasProcessamentoComEta,
    nome_modelo: str,
    execucao: int,
) -> None:
    tempo_geral_segundos = geral.tempo_execucao
    tempo_modelo_segundos = modelo.tempo_execucao
    processadas_geral = geral.processadas
    total_geral = geral.total

    perc_geral = (processadas_geral / total_geral * 100.0) if total_geral else 0.0
    taxa_geral = (
        (processadas_geral / tempo_geral_segundos) if tempo_geral_segundos > 0 else 0.0
    )

    processadas_modelo = modelo.processadas
    total_modelo = modelo.total
    perc_modelo = (processadas_modelo / total_modelo * 100.0) if total_modelo else 0.0
    media_modelo = (modelo.tempo_inferencia / modelo.ok) if modelo.ok else 0.0

    taxa_modelo = (
        (processadas_modelo / tempo_modelo_segundos)
        if tempo_modelo_segundos > 0
        else 0.0
    )
    restantes_modelo = max(0, total_modelo - processadas_modelo)
    eta_modelo = (restantes_modelo / taxa_modelo) if taxa_modelo > 0 else None
    processadas_execucao = execucao_stats.processadas
    total_execucao = execucao_stats.total
    perc_execucao = (
        (processadas_execucao / total_execucao * 100.0) if total_execucao else 0.0
    )
    media_execucao = (
        (execucao_stats.tempo_inferencia / execucao_stats.ok)
        if execucao_stats.ok
        else 0.0
    )
    tempo_execucao_segundos = execucao_stats.tempo_execucao
    taxa_execucao = (
        (processadas_execucao / tempo_execucao_segundos)
        if tempo_execucao_segundos > 0
        else 0.0
    )
    restantes_execucao = max(0, total_execucao - processadas_execucao)
    eta_execucao = (
        (restantes_execucao / taxa_execucao) if taxa_execucao > 0 else None
    )

    print(
        f"[GERAL ] {processadas_geral}/{total_geral} ({perc_geral:5.1f}%) | "
        f"ok={geral.ok} skip={geral.skip} erro={geral.erro} | "
        f"{taxa_geral:.2f} img/s"
    )
    print(
        f"[MODELO {nome_modelo}] {processadas_modelo}/{total_modelo} ({perc_modelo:5.1f}%) | "
        f"ok={modelo.ok} skip={modelo.skip} erro={modelo.erro} | "
        f"media={media_modelo:.2f}s/img | ETA {formatar_duracao(eta_modelo)}"
    )
    print(
        f"[EXECUCAO {nome_modelo} {formatar_nome_execucao(execucao)}] "
        f"{processadas_execucao}/{total_execucao} ({perc_execucao:5.1f}%) | "
        f"ok={execucao_stats.ok} skip={execucao_stats.skip} erro={execucao_stats.erro} | "
        f"media={media_execucao:.2f}s/img | ETA {formatar_duracao(eta_execucao)}"
    )
    print()


def imprimir_resumo_modelo(
    nome_modelo: str,
    stats_modelo: EstatisticasProcessamentoComEta,
) -> None:
    tempo_modelo = stats_modelo.tempo_execucao
    taxa_modelo = (
        (stats_modelo.processadas / tempo_modelo) if tempo_modelo > 0 else 0.0
    )
    media_modelo = (
        (stats_modelo.tempo_inferencia / stats_modelo.ok)
        if stats_modelo.ok
        else 0.0
    )

    print(f"[RESUMO MODELO {nome_modelo}]")
    print(
        f"tempo_total={formatar_duracao(tempo_modelo)} | total={stats_modelo.total} | "
        f"ok={stats_modelo.ok} | skip={stats_modelo.skip} | erro={stats_modelo.erro}"
    )
    print(f"tempo_medio={media_modelo:.2f}s/img | throughput={taxa_modelo:.2f} img/s")
    print("-" * 100)


def imprimir_resumo_execucao_modelo(
    nome_modelo: str,
    execucao: int,
    stats_execucao: EstatisticasProcessamentoComEta,
) -> None:
    tempo_execucao = stats_execucao.tempo_execucao
    taxa_execucao = (
        (stats_execucao.processadas / tempo_execucao) if tempo_execucao > 0 else 0.0
    )
    media_execucao = (
        (stats_execucao.tempo_inferencia / stats_execucao.ok)
        if stats_execucao.ok
        else 0.0
    )

    print(f"[RESUMO EXECUCAO {nome_modelo} {formatar_nome_execucao(execucao)}]")
    print(
        f"tempo_total={formatar_duracao(tempo_execucao)} | total={stats_execucao.total} | "
        f"ok={stats_execucao.ok} | skip={stats_execucao.skip} | erro={stats_execucao.erro}"
    )
    print(
        f"tempo_medio={media_execucao:.2f}s/img | throughput={taxa_execucao:.2f} img/s"
    )
    print("-" * 100)
