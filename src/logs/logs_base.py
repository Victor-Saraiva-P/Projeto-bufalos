from dataclasses import dataclass


@dataclass
class EstatisticasLogGeral:
    total: int
    processadas: int = 0
    ok: int = 0
    skip: int = 0
    erro: int = 0

    def registrar_ok(self) -> None:
        self.processadas += 1
        self.ok += 1

    def registrar_skip(self) -> None:
        self.processadas += 1
        self.skip += 1

    def registrar_erro(self) -> None:
        self.processadas += 1
        self.erro += 1

    def registrar_resultado(self, resultado: str) -> None:
        if resultado == "ok":
            self.registrar_ok()
            return

        if resultado == "skip":
            self.registrar_skip()
            return

        self.registrar_erro()


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


def formatar_nome_execucao(execucao: int) -> str:
    return f"execucao_{execucao}"
