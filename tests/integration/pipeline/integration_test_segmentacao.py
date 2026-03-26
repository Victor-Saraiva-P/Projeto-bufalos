from pathlib import Path

import pytest
from PIL import Image

from mock_config import MockDataConfig
from src.io import indice_loader, path_utils
from src.io.indice_loader import carregar_indice
from src.segmentacao import executar_segmentacao


def test_executar_segmentacao_processa_modelo_e_gera_arquivo(
    mock_data_config: MockDataConfig,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida_modelo_dir = tmp_path / "predicted_masks"

    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.PREDICTED_MASKS_DIR",
        str(saida_modelo_dir),
    )
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
        str(saida_modelo_dir),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras._criar_sessao_segmentacao",
        lambda modelo, providers: {
            "modelo": modelo,
            "providers": providers,
        },
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_api_rembg",
        lambda: (
            object(),
            lambda *_args, **_kwargs: Image.new("L", (4, 4), color=255),
        ),
    )

    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    indice_loader.inicializar_indice_sqlite(
        indice_path=str(mock_data_config.indice_path),
        sqlite_path=sqlite_path,
    )
    linhas = carregar_indice(sqlite_path=sqlite_path)
    resumos = executar_segmentacao(
        indice_excel=linhas,
        modelos_para_avaliacao=mock_data_config.modelos_para_avaliacao,
    )

    nome_modelo = next(iter(mock_data_config.modelos_para_avaliacao))
    saidas_geradas = sorted((saida_modelo_dir / nome_modelo).glob("*.png"))

    assert len(linhas) == 5
    assert list(resumos) == [nome_modelo]
    assert resumos[nome_modelo].total == len(linhas)
    assert resumos[nome_modelo].processadas == len(linhas)
    assert resumos[nome_modelo].ok == len(linhas)
    assert resumos[nome_modelo].erro == 0
    assert resumos[nome_modelo].skip == 0
    assert len(saidas_geradas) == len(linhas)
