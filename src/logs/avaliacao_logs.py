from dataclasses import dataclass, field
import time

from src.logs.logs_base import (
    EstatisticasLogGeral,
    formatar_duracao,
    formatar_nome_execucao,
)


@dataclass
class EstatisticasAvaliacao(EstatisticasLogGeral):
    tempo_calculo: float = 0.0
    inicio: float = field(default_factory=time.perf_counter)

    def registrar_ok_com_duracao(self, duracao_calculo: float) -> None:
        super().registrar_ok()
        self.tempo_calculo += duracao_calculo

    @property
    def tempo_execucao(self) -> float:
        return time.perf_counter() - self.inicio


def imprimir_status_avaliacao(
    identificador: str,
    nome_arquivo: str,
    stats: EstatisticasAvaliacao,
    execucao: int,
    estrategia_binarizacao: str | None = None,
) -> None:
    perc = (stats.processadas / stats.total * 100.0) if stats.total else 0.0
    tempo_execucao = stats.tempo_execucao
    taxa = (stats.processadas / tempo_execucao) if tempo_execucao > 0 else 0.0
    media = (stats.tempo_calculo / stats.ok) if stats.ok else 0.0
    restantes = max(0, stats.total - stats.processadas)
    eta = (restantes / taxa) if taxa > 0 else None

    contexto = [f"[AVALIACAO {formatar_nome_execucao(execucao)}]"]
    if estrategia_binarizacao is not None:
        contexto.append(estrategia_binarizacao)
    contexto.append(identificador)
    contexto.append(nome_arquivo)

    print(
        f"{' '.join(contexto)} | "
        f"processadas={stats.processadas}/{stats.total} ({perc:5.1f}%) | "
        f"ok={stats.ok} skip={stats.skip} erro={stats.erro} | "
        f"media={media:.2f}s/img | ETA {formatar_duracao(eta)}"
    )


def imprimir_resumo_avaliacao(stats: EstatisticasAvaliacao) -> None:
    tempo_execucao = stats.tempo_execucao
    taxa = (stats.processadas / tempo_execucao) if tempo_execucao > 0 else 0.0
    media = (stats.tempo_calculo / stats.ok) if stats.ok else 0.0

    print("[RESUMO AVALIACAO]")
    print(
        f"tempo_total={formatar_duracao(tempo_execucao)} | total={stats.total} | "
        f"ok={stats.ok} | skip={stats.skip} | erro={stats.erro}"
    )
    print(f"tempo_medio={media:.2f}s/img | throughput={taxa:.2f} img/s")
    print("-" * 100)


def imprimir_resumo_avaliacao_execucao(
    execucao: int,
    stats: EstatisticasAvaliacao,
    estrategia_binarizacao: str | None = None,
) -> None:
    tempo_execucao = stats.tempo_execucao
    taxa = (stats.processadas / tempo_execucao) if tempo_execucao > 0 else 0.0
    media = (stats.tempo_calculo / stats.ok) if stats.ok else 0.0

    titulo = f"[RESUMO AVALIACAO {formatar_nome_execucao(execucao)}]"
    if estrategia_binarizacao is not None:
        titulo = f"{titulo} {estrategia_binarizacao}"
    print(titulo)
    print(
        f"tempo_total={formatar_duracao(tempo_execucao)} | total={stats.total} | "
        f"ok={stats.ok} | skip={stats.skip} | erro={stats.erro}"
    )
    print(f"tempo_medio={media:.2f}s/img | throughput={taxa:.2f} img/s")
    print("-" * 100)
