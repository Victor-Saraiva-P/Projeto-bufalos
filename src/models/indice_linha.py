from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class IndiceLinha:
    nome_arquivo: str
    fazenda: str
    peso: Decimal
