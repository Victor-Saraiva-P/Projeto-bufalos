from pathlib import Path

import pytest
from PIL import Image

from src.models.indice_linha import IndiceLinha
from src.segmentacao.geracao_mascaras import (
    _criar_sessao_segmentacao,
    _segmentar_linha,
)
from src.segmentacao.logs import EstatisticasProcessamento


def test_criar_sessao_segmentacao_faz_fallback_para_cpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas: list[tuple[str, list[str]]] = []

    def fake_new_session(nome_modelo: str, providers: list[str]):
        chamadas.append((nome_modelo, providers))
        if len(chamadas) == 1:
            raise RuntimeError("falha no provider primario")
        return {"modelo": nome_modelo, "providers": providers}

    monkeypatch.setattr(
        "src.segmentacao.geracao_mascaras._obter_api_rembg",
        lambda: (fake_new_session, object()),
    )

    sessao = _criar_sessao_segmentacao("u2net", ["CUDAExecutionProvider"])

    assert sessao == {
        "modelo": "u2net",
        "providers": ["CPUExecutionProvider"],
    }
    assert chamadas == [
        ("u2net", ["CUDAExecutionProvider"]),
        ("u2net", ["CPUExecutionProvider"]),
    ]


def test_segmentar_linha_registra_skip_quando_saida_ja_existe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=1)
    original = tmp_path / "original.jpg"
    ground_truth = tmp_path / "ground_truth.jpg"
    output = tmp_path / "saida.png"

    Image.new("RGB", (2, 2), color="white").save(original)
    Image.new("RGB", (2, 2), color="black").save(ground_truth)
    output.write_text("ja existe")

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

    stats_geral = EstatisticasProcessamento(total=1)
    stats_modelo = EstatisticasProcessamento(total=1)

    _segmentar_linha(linha, "u2net", object(), stats_geral, stats_modelo)

    assert stats_geral.skip == 1
    assert stats_modelo.skip == 1
    assert stats_geral.processadas == 1
    assert stats_modelo.processadas == 1


def test_segmentar_linha_salva_mascara_quando_inferencia_funciona(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    linha = IndiceLinha(nome_arquivo="bufalo_001", fazenda="A", peso=1)
    original = tmp_path / "original.jpg"
    ground_truth = tmp_path / "ground_truth.jpg"
    output = tmp_path / "saida.png"

    Image.new("RGB", (3, 3), color="white").save(original)
    Image.new("RGB", (3, 3), color="black").save(ground_truth)

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
        "src.segmentacao.geracao_mascaras._obter_api_rembg",
        lambda: (
            object(),
            lambda *_args, **_kwargs: Image.new("L", (3, 3), color=255),
        ),
    )

    stats_geral = EstatisticasProcessamento(total=1)
    stats_modelo = EstatisticasProcessamento(total=1)

    _segmentar_linha(linha, "u2net", object(), stats_geral, stats_modelo)

    assert output.exists()
    assert stats_geral.ok == 1
    assert stats_modelo.ok == 1
    assert stats_geral.tempo_inferencia >= 0.0
    assert stats_modelo.tempo_inferencia >= 0.0
