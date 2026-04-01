import pytest
from sqlalchemy.exc import IntegrityError

from src.config import INDICE_PATH
from src.io.indice_loader import carregar_indice_excel
from src.models import (
    GroundTruthBinarizada,
    Imagem,
    ImagemTag,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
    Tag,
)
from src.repositories import (
    GroundTruthBinarizadaRepository,
    ImagemRepository,
    ImagemTagRepository,
    SegmentacaoBinarizadaRepository,
    SegmentacaoBrutaRepository,
    TagRepository,
)
from src.sqlite import criar_sessionmaker_sqlite


def test_imagem_repository_replace_all_persiste_imagens_e_tags(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")

    repository = ImagemRepository(sqlite_path)
    repository.replace_all(carregar_indice_excel(INDICE_PATH))
    imagens = repository.list()

    assert len(imagens) == 5
    assert imagens[0].nome_arquivo == "1166_Calcula_506"
    assert imagens[-1].nomes_tags == ["angulo_extremo", "baixo_contraste"]

    sessionmaker = criar_sessionmaker_sqlite(sqlite_path)
    with sessionmaker() as session:
        assert session.query(Imagem).count() == 5
        assert session.query(Tag).count() == 3


def test_ground_truth_repository_save_persiste_ground_truth(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    ground_truth_repository = GroundTruthBinarizadaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    ground_truth_repository.save(
        GroundTruthBinarizada(
            nome_arquivo="1166_Calcula_506",
            area=10.0,
            perimetro=20.0,
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is not None
    assert imagem_persistida.ground_truth_binarizada.area == 10.0
    assert ground_truth_repository.get("1166_Calcula_506") is not None


def test_segmentacao_bruta_repository_save_persiste_segmentacao_bruta(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            auprc=0.8,
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert len(imagem_persistida.segmentacoes_brutas) == 1
    assert imagem_persistida.segmentacoes_brutas[0].nome_modelo == "u2netp"
    assert imagem_persistida.segmentacoes_brutas[0].auprc == 0.8
    assert segmentacao_repository.get("1166_Calcula_506", "u2netp") is not None


def test_segmentacao_binarizada_repository_save_persiste_relacao(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    binarizacao_repository = SegmentacaoBinarizadaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            auprc=0.95,
        )
    )
    binarizacao_repository.save(
        SegmentacaoBinarizada(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            estrategia_binarizacao="GaussianaOpening",
            area=9.0,
            perimetro=21.0,
            iou=0.8,
        )
    )

    segmentacao = segmentacao_repository.get("1166_Calcula_506", "u2netp")

    assert segmentacao is not None
    assert len(segmentacao.segmentacoes_binarizadas) == 1
    assert (
        segmentacao.segmentacoes_binarizadas[0].estrategia_binarizacao
        == "GaussianaOpening"
    )
    assert segmentacao.segmentacoes_binarizadas[0].area == 9.0
    assert (
        binarizacao_repository.get(
            "1166_Calcula_506",
            "u2netp",
            "GaussianaOpening",
        )
        is not None
    )


def test_tag_repositories_persistem_tag_e_associacao(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    tag_repository = TagRepository(sqlite_path)
    imagem_tag_repository = ImagemTagRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    tag_repository.save(Tag(nome_tag="nova_tag"))
    imagem_tag_repository.save(
        ImagemTag(
            nome_arquivo="1166_Calcula_506",
            nome_tag="nova_tag",
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert "nova_tag" in imagem_persistida.nomes_tags
    assert tag_repository.get("nova_tag") is not None
    assert imagem_tag_repository.get("1166_Calcula_506", "nova_tag") is not None


def test_imagem_repository_get_carrega_binarizacoes_aninhadas(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    binarizacao_repository = SegmentacaoBinarizadaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            auprc=1.0,
        )
    )
    binarizacao_repository.save(
        SegmentacaoBinarizada(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            estrategia_binarizacao="GaussianaOpening",
            area=9.0,
            perimetro=21.0,
            iou=0.8,
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert [
        registro.nome_modelo for registro in imagem_persistida.segmentacoes_brutas
    ] == ["u2netp"]
    assert (
        imagem_persistida.segmentacoes_brutas[0]
        .segmentacoes_binarizadas[0]
        .estrategia_binarizacao
        == "GaussianaOpening"
    )
    assert (
        imagem_persistida.segmentacoes_brutas[0].auprc
        == 1.0
    )
    assert (
        imagem_persistida.segmentacoes_brutas[0]
        .segmentacoes_binarizadas[0]
        .iou
        == 0.8
    )


def test_modelos_metricos_exigem_metricas_nao_nulas_no_schema() -> None:
    assert not GroundTruthBinarizada.__table__.c.area.nullable
    assert not GroundTruthBinarizada.__table__.c.perimetro.nullable
    assert not SegmentacaoBruta.__table__.c.auprc.nullable
    assert not SegmentacaoBinarizada.__table__.c.area.nullable
    assert not SegmentacaoBinarizada.__table__.c.perimetro.nullable
    assert not SegmentacaoBinarizada.__table__.c.iou.nullable
    assert "metrica_x" not in SegmentacaoBruta.__table__.c
    assert "metrica_y" not in SegmentacaoBruta.__table__.c


def test_segmentacao_binarizada_repository_rejeita_segmentacao_parcial(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_bruta_repository = SegmentacaoBrutaRepository(sqlite_path)
    segmentacao_binarizada_repository = SegmentacaoBinarizadaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))
    segmentacao_bruta_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            auprc=0.7,
        )
    )

    with pytest.raises(IntegrityError):
        segmentacao_binarizada_repository.save(
            SegmentacaoBinarizada(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                estrategia_binarizacao="GaussianaOpening",
                area=1.0,
                perimetro=2.0,
                iou=None,  # type: ignore[arg-type]
            )
        )


def test_segmentacao_bruta_repository_rejeita_auprc_nula(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    with pytest.raises(IntegrityError):
        segmentacao_repository.save(
            SegmentacaoBruta(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                auprc=None,  # type: ignore[arg-type]
            )
        )


def test_imagem_repository_replace_all_recria_schema_e_remove_dados_derivados(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    ground_truth_repository = GroundTruthBinarizadaRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagens = carregar_indice_excel(INDICE_PATH)
    imagem_repository.replace_all(imagens)

    ground_truth_repository.save(
        GroundTruthBinarizada(
            nome_arquivo="1166_Calcula_506",
            area=3.0,
            perimetro=4.0,
        )
    )
    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            auprc=0.5,
        )
    )

    imagem_repository.replace_all(imagens)
    imagem_recarregada = imagem_repository.get("1166_Calcula_506")

    assert imagem_recarregada is not None
    assert imagem_recarregada.ground_truth_binarizada is None
    assert imagem_recarregada.segmentacoes_brutas == []
