from abc import ABC, abstractmethod


class Metrica(ABC):
    nome: str
    nome_arquivo: str
    modelo: str | None

    def __init__(
        self,
        nome: str,
        nome_arquivo: str,
        modelo: str | None = None,
    ) -> None:
        self.nome = nome
        self.nome_arquivo = nome_arquivo
        self.modelo = modelo

    @abstractmethod
    def calcular(self) -> int | float:
        """
        Executa o cálculo da métrica e retorna o resultado.
        """
        pass
