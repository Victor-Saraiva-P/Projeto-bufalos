from src.config import INDICE_PATH
from src.io.indice_loader import carregar_indice_excel
from src.models import Binarizacao, GroundTruthBinarizada, Imagem, Segmentacao, Tag
from src.repositories import ImagemRepository
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


def test_imagem_repository_save_persiste_ground_truth_e_segmentacoes_com_cascade(
    tmp_path,
) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = ImagemRepository(sqlite_path)
    repository.replace_all(carregar_indice_excel(INDICE_PATH))

    imagem = repository.get("1166_Calcula_506")
    assert imagem is not None

    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo=imagem.nome_arquivo,
        area=10.0,
        perimetro=20.0,
    )
    imagem.segmentacoes = [
        Segmentacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo="u2netp",
            area=9.0,
            perimetro=21.0,
            iou=0.8,
        )
    ]

    repository.save(imagem)
    imagem_persistida = repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is not None
    assert imagem_persistida.ground_truth_binarizada.area == 10.0
    assert len(imagem_persistida.segmentacoes) == 1
    assert imagem_persistida.segmentacoes[0].nome_modelo == "u2netp"
    assert imagem_persistida.segmentacoes[0].iou == 0.8
    assert imagem_persistida.segmentacoes[0].binarizacoes == []


def test_imagem_repository_get_carrega_binarizacoes_aninhadas(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = ImagemRepository(sqlite_path)
    repository.replace_all(carregar_indice_excel(INDICE_PATH))

    imagem = repository.get("1166_Calcula_506")
    assert imagem is not None
    imagem.segmentacoes = [
        Segmentacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo="u2netp",
            binarizacoes=[
                Binarizacao(
                    nome_arquivo=imagem.nome_arquivo,
                    nome_modelo="u2netp",
                    estrategia_binarizacao="GaussianOpeningBinarizationStrategy",
                    metrica_x=1.0,
                    metrica_y=2.0,
                )
            ],
        ),
    ]
    repository.save(imagem)

    imagem_persistida = repository.get("1166_Calcula_506")

    assert imagem_persistida is not None
    assert [registro.nome_modelo for registro in imagem_persistida.segmentacoes] == ["u2netp"]
    assert imagem_persistida.segmentacoes[0].binarizacoes[0].estrategia_binarizacao == (
        "GaussianOpeningBinarizationStrategy"
    )
    assert imagem_persistida.segmentacoes[0].binarizacoes[0].metrica_x == 1.0


def test_imagem_repository_replace_all_recria_schema_e_remove_dados_derivados(tmp_path) -> None:
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    repository = ImagemRepository(sqlite_path)
    imagens = carregar_indice_excel(INDICE_PATH)
    repository.replace_all(imagens)

    imagem = repository.get("1166_Calcula_506")
    assert imagem is not None
    imagem.ground_truth_binarizada = GroundTruthBinarizada(
        nome_arquivo=imagem.nome_arquivo,
        area=3.0,
        perimetro=4.0,
    )
    imagem.segmentacoes = [
        Segmentacao(
            nome_arquivo=imagem.nome_arquivo,
            nome_modelo="u2netp",
            area=1.0,
            perimetro=2.0,
            iou=0.5,
        )
    ]
    repository.save(imagem)

    repository.replace_all(imagens)
    imagem_recarregada = repository.get("1166_Calcula_506")

    assert imagem_recarregada is not None
    assert imagem_recarregada.ground_truth_binarizada is None
    assert imagem_recarregada.segmentacoes == []
