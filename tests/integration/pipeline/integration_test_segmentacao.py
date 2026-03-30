from pathlib import Path

import pytest
from PIL import Image

from src.config import MODELOS_PARA_AVALIACAO
from src.controllers import ImagemController, SegmentacaoController
from src.io.path_resolver import PathResolver
from src.repositories import ImagemRepository


def test_segmentacao_controller_processa_modelo_e_gera_arquivo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida_modelo_dir = tmp_path / "predicted_masks"
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    resolver = PathResolver.from_config().with_overrides(
        predicted_masks_raw_dir=str(saida_modelo_dir),
        sqlite_path=sqlite_path,
    )
    monkeypatch.setattr(
        "src.services.segmentacao_service.obter_api_rembg",
        lambda: (
            lambda modelo, providers: {
                "modelo": modelo,
                "providers": providers,
            },
            lambda *_args, **_kwargs: Image.new("L", (4, 4), color=255),
        ),
    )

    monkeypatch.setattr(
        "src.controllers.imagem_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.PathResolver.from_config",
        lambda: resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.MODELOS_PARA_AVALIACAO",
        MODELOS_PARA_AVALIACAO,
    )

    ImagemController().sincronizar_indice_excel()
    linhas = ImagemRepository(resolver.sqlite_path).list()
    resumos = SegmentacaoController().processar_imagens(imagens=linhas)
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(linhas[0].nome_arquivo)

    nome_modelo = next(iter(MODELOS_PARA_AVALIACAO))
    saidas_geradas = sorted((saida_modelo_dir / nome_modelo).glob("*.png"))

    assert len(linhas) == 5
    assert list(resumos) == [nome_modelo]
    assert resumos[nome_modelo].total == len(linhas)
    assert resumos[nome_modelo].processadas == len(linhas)
    assert resumos[nome_modelo].ok == len(linhas)
    assert resumos[nome_modelo].erro == 0
    assert resumos[nome_modelo].skip == 0
    assert len(saidas_geradas) == len(linhas)
    assert imagem_persistida is not None
    assert imagem_persistida.segmentacoes == []
