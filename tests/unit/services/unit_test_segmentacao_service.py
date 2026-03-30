from pathlib import Path

from PIL import Image
import pytest

from src.services.segmentacao_service import ResultadoSegmentacaoArquivo, SegmentacaoService


def test_criar_sessao_segmentacao_faz_fallback_para_cpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas: list[tuple[str, list[str]]] = []

    def fake_new_session(nome_modelo: str, providers: list[str]):
        chamadas.append((nome_modelo, providers))
        if providers != ["CPUExecutionProvider"]:
            raise RuntimeError("falha no provider primario")
        return {"modelo": nome_modelo, "providers": providers}

    monkeypatch.setattr(
        "src.services.segmentacao_service.obter_api_rembg",
        lambda: (fake_new_session, object()),
    )

    sessao = SegmentacaoService.criar_sessao_segmentacao(
        "u2net",
        ["CUDAExecutionProvider"],
    )

    assert sessao == {"modelo": "u2net", "providers": ["CPUExecutionProvider"]}
    assert chamadas == [
        ("u2net", ["CUDAExecutionProvider"]),
        ("u2net", ["CPUExecutionProvider"]),
    ]


def test_segmentar_arquivo_salva_mascara_quando_inferencia_funciona(
    tmp_path: Path,
) -> None:
    original = tmp_path / "original.jpg"
    mascara = tmp_path / "ground_truth.jpg"
    saida = tmp_path / "predicted_masks" / "u2net" / "bufalo_001.png"
    Image.new("RGB", (3, 3), color="white").save(original)
    Image.new("L", (3, 3), color=0).save(mascara)

    resultado = SegmentacaoService.segmentar_arquivo(
        nome_arquivo="bufalo_001",
        nome_modelo="u2net",
        original_path=str(original),
        mascara_path=str(mascara),
        output_path=str(saida),
        rembg_session=object(),
        remove_mask=lambda *_args, **_kwargs: Image.new("L", (3, 3), color=255),
    )

    assert resultado.status == "ok"
    assert resultado.duracao_inferencia is not None
    assert saida.exists()


def test_segmentar_arquivo_retorna_skip_quando_saida_ja_existe(
    tmp_path: Path,
) -> None:
    original = tmp_path / "original.jpg"
    mascara = tmp_path / "ground_truth.jpg"
    saida = tmp_path / "predicted_masks" / "u2net" / "bufalo_001.png"
    Image.new("RGB", (3, 3), color="white").save(original)
    Image.new("L", (3, 3), color=0).save(mascara)
    saida.parent.mkdir(parents=True)
    saida.write_text("ja existe")

    resultado = SegmentacaoService.segmentar_arquivo(
        nome_arquivo="bufalo_001",
        nome_modelo="u2net",
        original_path=str(original),
        mascara_path=str(mascara),
        output_path=str(saida),
        rembg_session=object(),
    )

    assert resultado == ResultadoSegmentacaoArquivo(status="skip")


def test_segmentar_arquivo_retorna_erro_quando_original_nao_existe(
    tmp_path: Path,
) -> None:
    resultado = SegmentacaoService.segmentar_arquivo(
        nome_arquivo="bufalo_001",
        nome_modelo="u2net",
        original_path=str(tmp_path / "inexistente.jpg"),
        mascara_path=str(tmp_path / "ground_truth.jpg"),
        output_path=str(tmp_path / "predicted_masks" / "u2net" / "bufalo_001.png"),
        rembg_session=object(),
    )

    assert resultado == ResultadoSegmentacaoArquivo(status="erro")
