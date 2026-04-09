import pytest
from sqlalchemy.exc import IntegrityError

from src.config import INDICE_PATH
from src.io.indice_loader import carregar_indice_excel
from src.models import (
    AnaliseSegmentacaoBrutaBase,
    AnaliseSegmentacaoBrutaResumoModelo,
    GroundTruthBinarizada,
    Imagem,
    ImagemTag,
    SegmentacaoBinarizada,
    SegmentacaoBruta,
    Tag,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaBaseRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
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
            execucao=1,
            auprc=0.8,
            soft_dice=0.7,
            brier_score=0.07,
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert len(imagem_persistida.segmentacoes_brutas) == 1
    assert imagem_persistida.segmentacoes_brutas[0].nome_modelo == "u2netp"
    assert imagem_persistida.segmentacoes_brutas[0].execucao == 1
    assert imagem_persistida.segmentacoes_brutas[0].auprc == 0.8
    assert imagem_persistida.segmentacoes_brutas[0].soft_dice == 0.7
    assert imagem_persistida.segmentacoes_brutas[0].brier_score == 0.07
    assert segmentacao_repository.get("1166_Calcula_506", "u2netp", 1) is not None


def test_segmentacao_bruta_repository_distingue_execucoes_da_mesma_imagem(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            execucao=1,
            auprc=0.8,
            soft_dice=0.7,
            brier_score=0.07,
        )
    )
    segmentacao_repository.save(
        SegmentacaoBruta(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            execucao=2,
            auprc=0.9,
            soft_dice=0.75,
            brier_score=0.05,
        )
    )

    segmentacoes = segmentacao_repository.list(
        nome_arquivo="1166_Calcula_506",
        nome_modelo="u2netp",
    )

    assert [
        (
            segmentacao.execucao,
            segmentacao.auprc,
            segmentacao.soft_dice,
            segmentacao.brier_score,
        )
        for segmentacao in segmentacoes
    ] == [
        (1, 0.8, 0.7, 0.07),
        (2, 0.9, 0.75, 0.05),
    ]


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
            execucao=1,
            auprc=0.95,
            soft_dice=0.88,
            brier_score=0.03,
        )
    )
    binarizacao_repository.save(
        SegmentacaoBinarizada(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=9.0,
            perimetro=21.0,
            iou=0.8,
        )
    )

    segmentacao = segmentacao_repository.get("1166_Calcula_506", "u2netp", 1)

    assert segmentacao is not None
    assert len(segmentacao.segmentacoes_binarizadas) == 1
    assert (
        segmentacao.segmentacoes_binarizadas[0].estrategia_binarizacao
        == "GaussianaOpening"
    )
    assert segmentacao.segmentacoes_binarizadas[0].execucao == 1
    assert segmentacao.segmentacoes_binarizadas[0].area == 9.0
    assert (
        binarizacao_repository.get(
            "1166_Calcula_506",
            "u2netp",
            1,
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


def test_analise_segmentacao_bruta_base_repository_replace_all_persiste_registros(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaBaseRepository(sqlite_path)

    repository.replace_all(
        [
            AnaliseSegmentacaoBrutaBase(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                execucao=1,
                fazenda="Calcula",
                peso=506.0,
                auprc=0.91,
                soft_dice=0.83,
                brier_score=0.07,
                tags="baixo_contraste",
                tags_sem_ok="baixo_contraste",
                num_tags_problema=1,
                tem_tag_problema=True,
                grupo_dificuldade="1_problema",
                tag_ok=False,
                tag_multi_bufalos=False,
                tag_cortado=False,
                tag_angulo_extremo=False,
                tag_baixo_contraste=True,
                tag_ocluido=False,
            )
        ]
    )

    registros = repository.list()

    assert len(registros) == 1
    assert registros[0].nome_arquivo == "1166_Calcula_506"
    assert registros[0].nome_modelo == "u2netp"
    assert registros[0].execucao == 1
    assert registros[0].grupo_dificuldade == "1_problema"
    assert registros[0].tag_baixo_contraste is True


def test_analise_segmentacao_bruta_base_repository_replace_all_substitui_conteudo(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaBaseRepository(sqlite_path)

    repository.replace_all(
        [
            AnaliseSegmentacaoBrutaBase(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                execucao=1,
                fazenda="Calcula",
                peso=506.0,
                auprc=0.91,
                soft_dice=0.83,
                brier_score=0.07,
                tags="",
                tags_sem_ok="",
                num_tags_problema=0,
                tem_tag_problema=False,
                grupo_dificuldade="nao_revisada",
                tag_ok=False,
                tag_multi_bufalos=False,
                tag_cortado=False,
                tag_angulo_extremo=False,
                tag_baixo_contraste=False,
                tag_ocluido=False,
            )
        ]
    )
    repository.replace_all(
        [
            AnaliseSegmentacaoBrutaBase(
                nome_arquivo="67_Laje-Nova_453",
                nome_modelo="u2net",
                execucao=2,
                fazenda="Laje-Nova",
                peso=453.0,
                auprc=0.88,
                soft_dice=0.79,
                brier_score=0.09,
                tags="multi_bufalos",
                tags_sem_ok="multi_bufalos",
                num_tags_problema=1,
                tem_tag_problema=True,
                grupo_dificuldade="1_problema",
                tag_ok=False,
                tag_multi_bufalos=True,
                tag_cortado=False,
                tag_angulo_extremo=False,
                tag_baixo_contraste=False,
                tag_ocluido=False,
            )
        ]
    )

    registros = repository.list()

    assert len(registros) == 1
    assert registros[0].nome_arquivo == "67_Laje-Nova_453"
    assert registros[0].execucao == 2
    assert registros[0].tag_multi_bufalos is True


def test_analise_segmentacao_bruta_resumo_modelo_repository_replace_all_persiste_resumos(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = AnaliseSegmentacaoBrutaResumoModeloRepository(sqlite_path)

    repository.replace_all(
        [
            AnaliseSegmentacaoBrutaResumoModelo(
                nome_modelo="u2netp",
                metric_name="auprc",
                count=2,
                mean=0.8,
                median=0.8,
                std=0.1,
                min=0.7,
                max=0.9,
                q1=0.75,
                q3=0.85,
                iqr=0.10,
                higher_is_better=True,
            )
        ]
    )

    registros = repository.list()

    assert len(registros) == 1
    assert registros[0].nome_modelo == "u2netp"
    assert registros[0].metric_name == "auprc"
    assert registros[0].higher_is_better is True


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
            execucao=1,
            auprc=1.0,
            soft_dice=0.94,
            brier_score=0.0,
        )
    )
    binarizacao_repository.save(
        SegmentacaoBinarizada(
            nome_arquivo="1166_Calcula_506",
            nome_modelo="u2netp",
            execucao=1,
            estrategia_binarizacao="GaussianaOpening",
            area=9.0,
            perimetro=21.0,
            iou=0.8,
        )
    )

    imagem_persistida = imagem_repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert [
        (registro.nome_modelo, registro.execucao)
        for registro in imagem_persistida.segmentacoes_brutas
    ] == [("u2netp", 1)]
    assert (
        imagem_persistida.segmentacoes_brutas[0]
        .segmentacoes_binarizadas[0]
        .estrategia_binarizacao
        == "GaussianaOpening"
    )
    assert imagem_persistida.segmentacoes_brutas[0].auprc == 1.0
    assert imagem_persistida.segmentacoes_brutas[0].soft_dice == 0.94
    assert imagem_persistida.segmentacoes_brutas[0].brier_score == 0.0
    assert imagem_persistida.segmentacoes_brutas[0].segmentacoes_binarizadas[0].iou == 0.8


def test_modelos_metricos_exigem_metricas_nao_nulas_no_schema() -> None:
    assert not GroundTruthBinarizada.__table__.c.area.nullable
    assert not GroundTruthBinarizada.__table__.c.perimetro.nullable
    assert not SegmentacaoBruta.__table__.c.auprc.nullable
    assert not SegmentacaoBruta.__table__.c.soft_dice.nullable
    assert not SegmentacaoBruta.__table__.c.brier_score.nullable
    assert not SegmentacaoBinarizada.__table__.c.area.nullable
    assert not SegmentacaoBinarizada.__table__.c.perimetro.nullable
    assert not SegmentacaoBinarizada.__table__.c.iou.nullable
    assert "execucao" in SegmentacaoBruta.__table__.c
    assert "execucao" in SegmentacaoBinarizada.__table__.c


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
            execucao=1,
            auprc=0.7,
            soft_dice=0.65,
            brier_score=0.12,
        )
    )

    with pytest.raises(IntegrityError):
        segmentacao_binarizada_repository.save(
            SegmentacaoBinarizada(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                execucao=1,
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
                execucao=1,
                auprc=None,  # type: ignore[arg-type]
                soft_dice=0.6,
                brier_score=0.07,
            )
        )


def test_segmentacao_bruta_repository_rejeita_soft_dice_nulo(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    with pytest.raises(IntegrityError):
        segmentacao_repository.save(
            SegmentacaoBruta(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                execucao=1,
                auprc=0.8,
                soft_dice=None,  # type: ignore[arg-type]
                brier_score=0.07,
            )
        )


def test_segmentacao_bruta_repository_rejeita_brier_score_nulo(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    imagem_repository = ImagemRepository(sqlite_path)
    segmentacao_repository = SegmentacaoBrutaRepository(sqlite_path)
    imagem_repository.replace_all(carregar_indice_excel(INDICE_PATH))

    with pytest.raises(IntegrityError):
        segmentacao_repository.save(
            SegmentacaoBruta(
                nome_arquivo="1166_Calcula_506",
                nome_modelo="u2netp",
                execucao=1,
                auprc=0.8,
                soft_dice=0.6,
                brier_score=None,  # type: ignore[arg-type]
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
            execucao=1,
            auprc=0.5,
            soft_dice=0.45,
            brier_score=0.09,
        )
    )

    imagem_repository.replace_all(imagens)
    imagem_recarregada = imagem_repository.get("1166_Calcula_506")

    assert imagem_recarregada is not None
    assert imagem_recarregada.ground_truth_binarizada is None
    assert imagem_recarregada.segmentacoes_brutas == []
