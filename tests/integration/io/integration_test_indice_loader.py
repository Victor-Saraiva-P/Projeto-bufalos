from decimal import Decimal

import pytest

from mock_config import MockDataConfig
from src.io import indice_loader
from src.io.indice_db import inicializar_banco_indice
from src.models.indice_linha import IndiceLinha


def test_carregar_indice_excel_com_mock_data(
    mock_data_config: MockDataConfig,
) -> None:
    linhas = indice_loader.carregar_indice_excel()
    linhas_esperadas = [
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

    assert mock_data_config.indice_path.exists()
    assert linhas == linhas_esperadas


def test_carregar_indice_excel_retorna_vazio_quando_banco_esta_vazio(
    tmp_path,
) -> None:
    indice_vazio = tmp_path / "indice.sqlite"
    inicializar_banco_indice([], db_path=str(indice_vazio))

    linhas = indice_loader.carregar_indice(db_path=str(indice_vazio))

    assert linhas == []
