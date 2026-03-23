from decimal import Decimal

import pandas as pd
import pytest

from mock_config import MockDataConfig
from src.io import indice_loader
from src.models.indice_linha import IndiceLinha


def test_carregar_indice_excel_com_mock_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = MockDataConfig()
    monkeypatch.setattr(indice_loader, "INDICE_PATH", str(config.indice_path))

    indice_df = pd.read_excel(config.indice_path)
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

    assert list(indice_df.columns) == ["Nome do arquivo", "Fazenda", "Peso", "Tags"]
    assert len(indice_df) == 5
    assert linhas == linhas_esperadas


def test_carregar_indice_excel_falha_quando_faltam_colunas(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    indice_invalido = tmp_path / "Indice.xlsx"
    df = pd.DataFrame(
        {
            "nome do arquivo": ["bufalo_001"],
            "fazenda": ["Mamucaba"],
        }
    )
    df.to_excel(indice_invalido, index=False)

    monkeypatch.setattr(indice_loader, "INDICE_PATH", str(indice_invalido))

    with pytest.raises(
        ValueError,
        match="Alguma das colunas esperadas nao foi encontrada no arquivo Excel.",
    ):
        indice_loader.carregar_indice_excel()
