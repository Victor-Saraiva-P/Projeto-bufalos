from decimal import Decimal

from src.models.indice_linha import IndiceLinha, normalizar_tags


def test_indice_linha_inicializa_tags_vazio_por_padrao() -> None:
    linha = IndiceLinha(
        nome_arquivo="bufalo_001",
        fazenda="Mamucaba",
        peso=Decimal("350"),
    )

    assert linha.tags == []


def test_normalizar_tags_retorna_lista_vazia_para_valores_ausentes() -> None:
    assert normalizar_tags(None) == []
    assert normalizar_tags("") == []
    assert normalizar_tags("   ") == []
    assert normalizar_tags("nan") == []


def test_normalizar_tags_quebra_por_virgula_e_remove_espacos() -> None:
    assert normalizar_tags("ok, cortado, baixo_contraste") == [
        "ok",
        "cortado",
        "baixo_contraste",
    ]


def test_normalizar_tags_descarta_segmentos_vazios() -> None:
    assert normalizar_tags("ok, , cortado ,,") == ["ok", "cortado"]
