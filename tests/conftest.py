from decimal import Decimal

import pytest

from mock_config import MockDataConfig
from src.config import INDICE_DB_PATH
from src.io.indice_db import inicializar_banco_indice
from src.models.indice_linha import IndiceLinha


@pytest.fixture(scope="session")
def mock_data_config() -> MockDataConfig:
    config = MockDataConfig()
    linhas = [
        IndiceLinha(
            nome_arquivo="493098e5-da4e-47dc-80cc-eddd2c703a24",
            fazenda="Manezinho",
            peso=Decimal("55"),
            tags=["ok"],
        ),
        IndiceLinha(
            nome_arquivo="e2b294f6-387c-49ce-8fd8-8e80e80cdc46",
            fazenda="Faco",
            peso=Decimal("188"),
            tags=["angulo_extremo", "baixo_contraste"],
        ),
        IndiceLinha(
            nome_arquivo="67_Laje-Nova_453",
            fazenda="Laje Nova",
            peso=Decimal("453"),
            tags=["ok"],
        ),
        IndiceLinha(
            nome_arquivo="1166_Calcula_506",
            fazenda="Calcula",
            peso=Decimal("506"),
            tags=["ok"],
        ),
        IndiceLinha(
            nome_arquivo="284_Mamucaba_350",
            fazenda="Mamucaba",
            peso=Decimal("350"),
            tags=["baixo_contraste"],
        ),
    ]
    inicializar_banco_indice(linhas, db_path=str(config.indice_path))
    inicializar_banco_indice(linhas, db_path=INDICE_DB_PATH)
    return config
