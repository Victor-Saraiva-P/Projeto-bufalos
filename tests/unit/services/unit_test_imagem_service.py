from pathlib import Path
from unittest.mock import Mock

from PIL import Image
import pytest

from src.models import Imagem
from src.services.imagem_service import ImagemService


def test_sincronizar_indice_excel_carrega_do_loader_e_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imagens = [Imagem(nome_arquivo="bufalo_001", fazenda="A", peso=1.0)]
    repository = Mock()

    monkeypatch.setattr(
        "src.services.imagem_service.carregar_indice_excel",
        lambda indice_path: imagens,
    )

    ImagemService.sincronizar_indice_excel(repository, "/tmp/Indice.xlsx")

    repository.replace_all.assert_called_once_with(imagens)


def test_verificar_pngs_corrompidos_remove_arquivo_invalido(
    tmp_path: Path,
) -> None:
    valido = tmp_path / "valido.png"
    corrompido = tmp_path / "corrompido.png"
    ignorado = tmp_path / "ignorado.jpg"

    Image.new("L", (4, 4), color=255).save(valido)
    corrompido.write_text("nao e um png valido")
    ignorado.write_text("nao deve ser lido")

    resumo = ImagemService.verificar_pngs_corrompidos(str(tmp_path), ".png")

    assert resumo.total_png == 2
    assert resumo.arquivos_integros == 1
    assert resumo.arquivos_removidos == 1
    assert resumo.falhas_remocao == 0
    assert valido.exists()
    assert not corrompido.exists()
    assert ignorado.exists()


def test_verificar_pngs_corrompidos_aceita_extensao_case_insensitive(
    tmp_path: Path,
) -> None:
    arquivo_maiusculo = tmp_path / "mascara.PNG"
    Image.new("L", (2, 2), color=0).save(arquivo_maiusculo)

    resumo = ImagemService.verificar_pngs_corrompidos(str(tmp_path), ".png")

    assert resumo.total_png == 1
    assert resumo.arquivos_integros == 1
    assert resumo.arquivos_removidos == 0
    assert resumo.falhas_remocao == 0
