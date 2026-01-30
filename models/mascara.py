from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Mascara:
    area: int
    perimetro: int
