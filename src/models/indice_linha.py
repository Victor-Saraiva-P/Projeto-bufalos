from dataclasses import dataclass, field
from decimal import Decimal


def normalizar_tags(valor: object) -> list[str]:
    if valor is None:
        return []

    tags = str(valor).strip()
    if not tags or tags.lower() == "nan":
        return []

    return [tag.strip() for tag in tags.split(",") if tag.strip()]


@dataclass(frozen=True)
class IndiceLinha:
    nome_arquivo: str
    fazenda: str
    peso: Decimal
    tags: list[str] = field(default_factory=list)
