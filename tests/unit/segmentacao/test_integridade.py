from pathlib import Path

from PIL import Image

from src.segmentacao.integridade import verificar_e_limpar_pngs_corrompidos


def test_verificar_e_limpar_pngs_corrompidos_remove_arquivo_invalido(
    tmp_path: Path,
) -> None:
    valido = tmp_path / "valido.png"
    corrompido = tmp_path / "corrompido.png"
    ignorado = tmp_path / "ignorado.jpg"

    Image.new("L", (4, 4), color=255).save(valido)
    corrompido.write_text("nao e um png valido")
    ignorado.write_text("nao deve ser lido")

    resumo = verificar_e_limpar_pngs_corrompidos(str(tmp_path), ".png")

    assert resumo.total_png == 2
    assert resumo.arquivos_integros == 1
    assert resumo.arquivos_removidos == 1
    assert resumo.falhas_remocao == 0
    assert valido.exists()
    assert not corrompido.exists()
    assert ignorado.exists()


def test_verificar_e_limpar_pngs_corrompidos_aceita_extensao_case_insensitive(
    tmp_path: Path,
) -> None:
    arquivo_maiusculo = tmp_path / "mascara.PNG"
    Image.new("L", (2, 2), color=0).save(arquivo_maiusculo)

    resumo = verificar_e_limpar_pngs_corrompidos(str(tmp_path), ".png")

    assert resumo.total_png == 1
    assert resumo.arquivos_integros == 1
    assert resumo.arquivos_removidos == 0
    assert resumo.falhas_remocao == 0
