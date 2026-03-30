import pandas as pd
import pytest

from src.config import INDICE_PATH, SQLITE_PATH
from src.controllers import ImagemController
from src.io import indice_loader
from src.repositories import ImagemRepository


def test_carregar_indice_excel_retorna_imagens_com_tags() -> None:
    linhas = indice_loader.carregar_indice_excel(INDICE_PATH)

    assert [linha.nome_arquivo for linha in linhas] == [
        "493098e5-da4e-47dc-80cc-eddd2c703a24",
        "e2b294f6-387c-49ce-8fd8-8e80e80cdc46",
        "67_Laje-Nova_453",
        "1166_Calcula_506",
        "284_Mamucaba_350",
    ]
    assert [linha.nomes_tags for linha in linhas] == [
        ["ok"],
        ["angulo_extremo", "baixo_contraste"],
        ["ok"],
        ["ok"],
        ["baixo_contraste"],
    ]


def test_imagem_controller_sincroniza_excel_para_sqlite() -> None:
    sqlite_path = SQLITE_PATH

    ImagemController().sincronizar_indice_excel()
    linhas = ImagemRepository(sqlite_path).list()
    assert [linha.nome_arquivo for linha in linhas] == [
        "1166_Calcula_506",
        "284_Mamucaba_350",
        "493098e5-da4e-47dc-80cc-eddd2c703a24",
        "67_Laje-Nova_453",
        "e2b294f6-387c-49ce-8fd8-8e80e80cdc46",
    ]
    assert [linha.fazenda for linha in linhas] == [
        "Calcula",
        "Mamucaba",
        "Manezinho",
        "Laje Nova",
        "Faco",
    ]
    assert [linha.peso for linha in linhas] == [506.0, 350.0, 55.0, 453.0, 188.0]
    assert [linha.nomes_tags for linha in linhas] == [
        ["ok"],
        ["baixo_contraste"],
        ["ok"],
        ["ok"],
        ["angulo_extremo", "baixo_contraste"],
    ]


def test_imagem_controller_falha_quando_faltam_colunas_no_excel(
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

    from src.io.path_resolver import PathResolver

    resolver = PathResolver.from_config().with_overrides(
        indice_path=str(indice_invalido),
        sqlite_path=str(tmp_path / "bufalos.sqlite3"),
    )
    monkeypatch.setattr(
        "src.controllers.imagem_controller.PathResolver.from_config",
        lambda: resolver,
    )

    with pytest.raises(
        ValueError,
        match="Alguma das colunas esperadas nao foi encontrada no arquivo Excel.",
    ):
        ImagemController().sincronizar_indice_excel()
