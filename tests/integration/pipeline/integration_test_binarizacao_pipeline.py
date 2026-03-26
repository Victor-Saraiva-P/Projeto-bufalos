from pathlib import Path

import pytest
from PIL import Image

from mock_config import MockDataConfig
from src.binarizacao import (
    GaussianOpeningBinarizationStrategy,
    binarizar_ground_truth,
    binarizar_mascaras_preditas,
)
from src.io import path_utils
from src.io.indice_loader import carregar_indice_sqlite


def test_binarizar_ground_truth_processa_indice_e_gera_pngs(
    mock_data_config: MockDataConfig,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida_ground_truth = tmp_path / "ground_truth_binary"

    monkeypatch.setattr(
        path_utils,
        "GROUND_TRUTH_RAW_DIR",
        str(mock_data_config.ground_truth_raw_dir),
    )
    monkeypatch.setattr(
        path_utils,
        "GROUND_TRUTH_BINARY",
        str(saida_ground_truth),
    )

    linhas = carregar_indice_sqlite()
    stats = binarizar_ground_truth(linhas, GaussianOpeningBinarizationStrategy())

    saidas_geradas = sorted(saida_ground_truth.glob("*.png"))

    assert len(linhas) == 5
    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)


def test_binarizar_mascaras_preditas_processa_modelo_e_gera_pngs(
    mock_data_config: MockDataConfig,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada_modelos = tmp_path / "predicted_masks"
    saida_modelos = tmp_path / "predicted_masks_binary"
    nome_modelo = next(iter(mock_data_config.modelos_para_avaliacao))

    monkeypatch.setattr(
        path_utils,
        "PREDICTED_MASKS_DIR",
        str(entrada_modelos),
    )
    monkeypatch.setattr(
        path_utils,
        "PREDICTED_MASKS_BINARY",
        str(saida_modelos),
    )

    linhas = carregar_indice_sqlite()
    diretorio_modelo = entrada_modelos / nome_modelo
    diretorio_modelo.mkdir(parents=True)

    for linha in linhas:
        Image.open(
            mock_data_config.ground_truth_raw_dir / f"{linha.nome_arquivo}.jpg"
        ).save(diretorio_modelo / f"{linha.nome_arquivo}.png")

    resumos = binarizar_mascaras_preditas(
        linhas,
        {nome_modelo: mock_data_config.modelos_para_avaliacao[nome_modelo]},
        GaussianOpeningBinarizationStrategy(),
    )

    saidas_geradas = sorted((saida_modelos / nome_modelo).glob("*.png"))
    stats = resumos[nome_modelo]

    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)
