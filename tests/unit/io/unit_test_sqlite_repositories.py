from dataclasses import dataclass

from mock_config import MockDataConfig
from src.io.sqlite.repositories import AvaliacaoSQLiteRepository, IndiceSQLiteRepository


@dataclass
class _GroundTruthFake:
    area: float
    perimetro: float


@dataclass
class _ModeloFake:
    modelo: str
    area: float
    perimetro: float
    iou: float


@dataclass
class _AvaliacaoFake:
    nome_arquivo: str
    ground_truth: _GroundTruthFake
    modelos: dict[str, _ModeloFake]


def test_indice_sqlite_repository_sincroniza_do_excel(tmp_path) -> None:
    config = MockDataConfig()
    sqlite_path = str(tmp_path / "bufalos.sqlite3")

    repository = IndiceSQLiteRepository(sqlite_path)
    repository.sincronizar_do_excel(str(config.indice_path))
    linhas = repository.listar()

    assert len(linhas) == 5
    assert linhas[0].nome_arquivo == "1166_Calcula_506"


def test_avaliacao_sqlite_repository_salva_e_carrega_dataframe(tmp_path) -> None:
    config = MockDataConfig()
    sqlite_path = str(tmp_path / "bufalos.sqlite3")
    indice_repository = IndiceSQLiteRepository(sqlite_path)
    indice_repository.sincronizar_do_excel(str(config.indice_path))

    repository = AvaliacaoSQLiteRepository(sqlite_path)
    avaliacao = _AvaliacaoFake(
        nome_arquivo="1166_Calcula_506",
        ground_truth=_GroundTruthFake(area=10.0, perimetro=20.0),
        modelos={
            "u2netp": _ModeloFake(
                modelo="u2netp",
                area=9.0,
                perimetro=21.0,
                iou=0.8,
            )
        },
    )

    repository.salvar_avaliacao(avaliacao)
    df = repository.carregar_metricas_dataframe()

    assert len(df) == 1
    assert df.iloc[0]["nome_arquivo"] == "1166_Calcula_506"
    assert df.iloc[0]["modelo"] == "u2netp"
    assert df.iloc[0]["area_gt"] == 10.0
    assert df.iloc[0]["iou"] == 0.8
