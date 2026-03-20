from dataclasses import dataclass, field
import time


@dataclass
class EstatisticasProcessamento:
    total: int
    processadas: int = 0
    ok: int = 0
    skip: int = 0
    erro: int = 0
    tempo_inferencia: float = 0.0
    inicio: float = field(default_factory=time.perf_counter)

    def registrar_ok(self, duracao_inferencia: float) -> None:
        self.processadas += 1
        self.ok += 1
        self.tempo_inferencia += duracao_inferencia

    def registrar_skip(self) -> None:
        self.processadas += 1
        self.skip += 1

    def registrar_erro(self) -> None:
        self.processadas += 1
        self.erro += 1

    @property
    def tempo_execucao(self) -> float:
        return time.perf_counter() - self.inicio


def formatar_duracao(segundos):
    if segundos is None:
        return "--"

    total = int(max(0, segundos))
    horas = total // 3600
    minutos = (total % 3600) // 60
    seg = total % 60

    if horas > 0:
        return f"{horas}h{minutos:02d}m{seg:02d}s"
    if minutos > 0:
        return f"{minutos}m{seg:02d}s"
    return f"{seg}s"


def imprimir_status(
    geral: EstatisticasProcessamento,
    modelo: EstatisticasProcessamento,
    nome_modelo: str,
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
    print()


def imprimir_resumo_modelo(
    nome_modelo: str,
    stats_modelo: EstatisticasProcessamento,
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


def imprimir_resumo_verificacao_png(
    total_png: int,
    arquivos_integros: int,
    arquivos_removidos: int,
    falhas_remocao: int,
) -> None:
    print("\nVerificacao de integridade concluida.")
    print(f" - Total de PNGs verificados: {total_png}")
    print(f" - Arquivos integros: {arquivos_integros}")
    print(f" - Arquivos removidos por corrupcao: {arquivos_removidos}")
    print(f" - Falhas ao remover: {falhas_remocao}")
