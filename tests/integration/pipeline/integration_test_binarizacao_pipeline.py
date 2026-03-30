from pathlib import Path

import pytest
from PIL import Image

from src.binarizacao import GaussianOpeningBinarizationStrategy
from src.config import GROUND_TRUTH_RAW_DIR, MODELOS_PARA_AVALIACAO
from src.controllers import BinarizacaoController, ImagemController
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def test_binarizacao_controller_processa_ground_truth_e_gera_pngs(
    tmp_path: Path,
) -> None:
    saida_ground_truth = tmp_path / "ground_truth_binary"
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
        ground_truth_binary_dir=str(saida_ground_truth),
        sqlite_path=sqlite_path,
    )

    ImagemController(path_resolver=resolver).sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    stats = BinarizacaoController(path_resolver=resolver).processar_ground_truth(
        GaussianOpeningBinarizationStrategy(),
        imagens=linhas,
    )
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    saidas_geradas = sorted(saida_ground_truth.glob("*.png"))

    assert len(linhas) == 5
    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)
    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is not None


def test_binarizacao_controller_processa_segmentacoes_e_gera_pngs(
    tmp_path: Path,
) -> None:
    entrada_modelos = tmp_path / "predicted_masks"
    saida_modelos = tmp_path / "predicted_masks_binary"
    nome_modelo = next(iter(MODELOS_PARA_AVALIACAO))
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
        predicted_masks_dir=str(entrada_modelos),
        predicted_masks_binary_dir=str(saida_modelos),
        sqlite_path=sqlite_path,
    )

    ImagemController(path_resolver=resolver).sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    diretorio_modelo = entrada_modelos / nome_modelo
    diretorio_modelo.mkdir(parents=True)

    for linha in linhas:
        Image.open(
            Path(GROUND_TRUTH_RAW_DIR) / f"{linha.nome_arquivo}.jpg"
        ).save(diretorio_modelo / f"{linha.nome_arquivo}.png")

    resumos = BinarizacaoController(path_resolver=resolver).processar_segmentacoes(
        GaussianOpeningBinarizationStrategy(),
        imagens=linhas,
        modelos_para_avaliacao={nome_modelo: MODELOS_PARA_AVALIACAO[nome_modelo]},
    )
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    saidas_geradas = sorted((saida_modelos / nome_modelo).glob("*.png"))
    stats = resumos[nome_modelo]

    assert stats.total == len(linhas)
    assert stats.processadas == len(linhas)
    assert stats.ok == len(linhas)
    assert stats.skip == 0
    assert stats.erro == 0
    assert len(saidas_geradas) == len(linhas)
    assert imagem_persistida is not None
    assert [segmentacao.nome_modelo for segmentacao in imagem_persistida.segmentacoes] == [
        nome_modelo
    ]
    assert (
        imagem_persistida.segmentacoes[0].binarizacoes[0].estrategia_binarizacao
        == "GaussianOpeningBinarizationStrategy"
    )
