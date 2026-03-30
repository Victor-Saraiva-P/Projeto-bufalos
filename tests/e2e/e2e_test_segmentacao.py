from pathlib import Path

import pytest

from src.config import MODELOS_PARA_AVALIACAO
from src.controllers import ImagemController, SegmentacaoController
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


@pytest.mark.e2e
def test_segmentacao_e2e_com_rembg_real(
    tmp_path: Path,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = PathResolver.from_config().with_overrides(
        predicted_masks_dir=str(tmp_path / "predicted_masks"),
        sqlite_path=str(tmp_path / "bufalos.sqlite3"),
    )

    ImagemController(path_resolver=resolver).sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    linha_teste = [linhas[0]]
    nome_modelo = next(iter(MODELOS_PARA_AVALIACAO))
    modelos = MODELOS_PARA_AVALIACAO

    try:
        resumos = SegmentacaoController(path_resolver=resolver).processar_imagens(
            imagens=linha_teste,
            modelos_para_avaliacao=modelos,
        )
    except Exception as erro:
        pytest.skip(f"Ambiente sem suporte para executar rembg real: {erro}")

    saida_esperada = (
        tmp_path / "predicted_masks" / nome_modelo / f"{linha_teste[0].nome_arquivo}.png"
    )

    assert saida_esperada.exists()
    assert resumos[nome_modelo].total == 1
    assert resumos[nome_modelo].processadas == 1
    assert resumos[nome_modelo].ok == 1
    assert resumos[nome_modelo].erro == 0
    assert resumos[nome_modelo].skip == 0
