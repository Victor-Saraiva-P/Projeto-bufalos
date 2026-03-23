from decimal import Decimal
from pathlib import Path

import pytest
from PIL import Image

from src.models.indice_linha import IndiceLinha
from src.segmentacao import executar_segmentacao


def test_executar_segmentacao_faz_fallback_para_cpu_quando_sessao_inicial_falha(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=Decimal("1"))
    original = tmp_path / "original.jpg"
    ground_truth = tmp_path / "ground_truth.jpg"
    output_dir = tmp_path / "predicted_masks"

    Image.new("RGB", (2, 2), color="white").save(original)
    Image.new("RGB", (2, 2), color="black").save(ground_truth)

    chamadas_sessao: list[tuple[str, list[str]]] = []

    def fake_new_session(nome_modelo: str, providers: list[str]):
        chamadas_sessao.append((nome_modelo, providers))
        if len(chamadas_sessao) == 1:
            raise RuntimeError("falha no provider primario")
        return {"modelo": nome_modelo, "providers": providers}

    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.PREDICTED_MASKS_DIR",
        str(output_dir),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_foto_original",
        lambda _: str(original),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_ground_truth",
        lambda _: str(ground_truth),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_mascara_predita",
        lambda modelo, _: str(output_dir / modelo / "bufalo_001.png"),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_resolvedor_providers",
        lambda: (lambda *_args: ["CUDAExecutionProvider"]),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_api_rembg",
        lambda: (
            fake_new_session,
            lambda *_args, **_kwargs: Image.new("L", (2, 2), color=255),
        ),
    )

    resumos = executar_segmentacao([linha], {"u2net": "gpu"})

    assert resumos["u2net"].ok == 1
    assert chamadas_sessao == [
        ("u2net", ["CUDAExecutionProvider"]),
        ("u2net", ["CPUExecutionProvider"]),
    ]


def test_executar_segmentacao_registra_skip_quando_saida_ja_existe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=Decimal("1"))
    original = tmp_path / "original.jpg"
    ground_truth = tmp_path / "ground_truth.jpg"
    output = tmp_path / "predicted_masks" / "u2net" / "bufalo_001.png"

    Image.new("RGB", (2, 2), color="white").save(original)
    Image.new("RGB", (2, 2), color="black").save(ground_truth)
    output.parent.mkdir(parents=True)
    output.write_text("ja existe")

    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.PREDICTED_MASKS_DIR",
        str(tmp_path / "predicted_masks"),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_foto_original",
        lambda _: str(original),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_ground_truth",
        lambda _: str(ground_truth),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_mascara_predita",
        lambda *_: str(output),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_resolvedor_providers",
        lambda: (lambda *_args: ["CPUExecutionProvider"]),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_api_rembg",
        lambda: (lambda *_args, **_kwargs: object(), object()),
    )

    resumos = executar_segmentacao([linha], {"u2net": "cpu"})

    assert resumos["u2net"].skip == 1
    assert resumos["u2net"].processadas == 1


def test_executar_segmentacao_salva_mascara_quando_inferencia_funciona(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=Decimal("1"))
    original = tmp_path / "original.jpg"
    ground_truth = tmp_path / "ground_truth.jpg"
    output_dir = tmp_path / "predicted_masks"
    output = output_dir / "u2net" / "bufalo_001.png"

    Image.new("RGB", (3, 3), color="white").save(original)
    Image.new("RGB", (3, 3), color="black").save(ground_truth)

    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.PREDICTED_MASKS_DIR",
        str(output_dir),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_foto_original",
        lambda _: str(original),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_ground_truth",
        lambda _: str(ground_truth),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.caminho_mascara_predita",
        lambda *_: str(output),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_resolvedor_providers",
        lambda: (lambda *_args: ["CPUExecutionProvider"]),
    )
    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras.obter_api_rembg",
        lambda: (
            lambda *_args, **_kwargs: object(),
            lambda *_args, **_kwargs: Image.new("L", (3, 3), color=255),
        ),
    )

    resumos = executar_segmentacao([linha], {"u2net": "cpu"})

    assert output.exists()
    assert resumos["u2net"].ok == 1
    assert resumos["u2net"].tempo_inferencia >= 0.0
