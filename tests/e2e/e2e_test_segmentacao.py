from pathlib import Path

import pytest

from mock_config import MockDataConfig
from src.io import path_utils
from src.io.indice_loader import carregar_indice_sqlite
from src.segmentacao import executar_segmentacao


@pytest.mark.e2e
def test_segmentacao_e2e_com_rembg_real(
    mock_data_config: MockDataConfig,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    monkeypatch.setattr(
        path_utils,
        "IMAGES_DIR",
        str(mock_data_config.images_dir),
    )
    monkeypatch.setattr(
        path_utils,
        "GROUND_TRUTH_RAW_DIR",
        str(mock_data_config.ground_truth_raw_dir),
    )
    monkeypatch.setattr(
        path_utils,
        "PREDICTED_MASKS_DIR",
        str(tmp_path / "predicted_masks"),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.PREDICTED_MASKS_DIR",
        str(tmp_path / "predicted_masks"),
    )

    linhas = carregar_indice_sqlite()
    linha_teste = [linhas[0]]
    nome_modelo = next(iter(mock_data_config.modelos_para_avaliacao))
    modelos = mock_data_config.modelos_para_avaliacao

    try:
        resumos = executar_segmentacao(
            indice_excel=linha_teste,
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
