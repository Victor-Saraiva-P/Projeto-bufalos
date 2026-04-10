from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tomllib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["figure.max_open_warning"] = 0
import pytest
import numpy as np
import pandas as pd
from src.analysis import (
    MetricsCollector,
    build_and_persist_analysis_segmentacao_bruta_estabilidade,
    build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo,
    build_and_persist_analysis_segmentacao_bruta_intervalo_confianca,
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao,
    build_and_persist_analysis_segmentacao_bruta_resumo_modelo,
    build_and_persist_analysis_segmentacao_bruta_resumo_tag,
    build_and_persist_analysis_segmentacao_bruta_testes_modelo,
    build_and_persist_analysis_segmentacao_bruta_testes_tag,
)
from src.io.path_resolver import PathResolver
from src.controllers import (
    AvaliacaoController,
    BinarizacaoController,
    ImagemController,
    SegmentacaoController,
)
from src.repositories import (
    AnaliseSegmentacaoBrutaEstabilidadeRepository,
    AnaliseSegmentacaoBrutaInteracaoTagModeloRepository,
    AnaliseSegmentacaoBrutaIntervaloConfiancaRepository,
    AnaliseSegmentacaoBrutaResumoExecucaoRepository,
    AnaliseSegmentacaoBrutaResumoModeloRepository,
    AnaliseSegmentacaoBrutaResumoTagRepository,
    AnaliseSegmentacaoBrutaTesteModeloRepository,
    AnaliseSegmentacaoBrutaTesteTagRepository,
    ImagemRepository,
)
from src.visualization import (
    PdfReportSection,
    plot_metric_bars_with_ci_by_model,
    plot_metric_correlation_heatmap,
    plot_metric_by_execution_heatmap,
    plot_metric_distribution_by_model,
    plot_metric_scatter,
    plot_model_tag_interaction_heatmap,
    plot_pairwise_pvalue_heatmap,
    plot_simple_regression,
    plot_stability_heatmap,
    save_pdf_report,
)

E2E_CONFIG_PATH = "config.e2e.toml"
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class E2EContext:
    resolver: PathResolver
    modelos: dict[str, str]
    num_execucoes: int
    ground_truth_strategy: str
    segmentacao_strategies: list[str]


def _resolver_caminho(path_value: str) -> str:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((REPO_ROOT / path).resolve())


def _carregar_contexto_e2e() -> E2EContext:
    config_path = REPO_ROOT / E2E_CONFIG_PATH
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    paths = config["paths"]

    return E2EContext(
        resolver=PathResolver(
            data_dir=_resolver_caminho(paths["data_dir"]),
            generated_dir=_resolver_caminho(paths["generated_dir"]),
            images_dir=_resolver_caminho(paths["images_dir"]),
            ground_truth_brutos_dir=_resolver_caminho(paths["ground_truth_brutos_dir"]),
            segmentacoes_brutas_dir=_resolver_caminho(paths["segmentacoes_brutas_dir"]),
            segmentacoes_binarizadas_dir=_resolver_caminho(
                paths["segmentacoes_binarizadas_dir"]
            ),
            ground_truth_binarizada_dir=_resolver_caminho(
                paths["ground_truth_binarizada_dir"]
            ),
            evaluation_dir=_resolver_caminho(paths["evaluation_dir"]),
            indice_path=_resolver_caminho(paths["indice_file"]),
            sqlite_path=_resolver_caminho(paths["sqlite_file"]),
        ),
        modelos=dict(config["models"]),
        num_execucoes=config["execution"]["num_execucoes"],
        ground_truth_strategy=config["binarization"]["ground_truth_strategy"],
        segmentacao_strategies=list(config["binarization"]["segmentacao_strategies"]),
    )


def _limpar_saida_e2e(resolver: PathResolver) -> None:
    generated_dir = Path(resolver.generated_dir)
    shutil.rmtree(generated_dir, ignore_errors=True)
    generated_dir.mkdir(parents=True, exist_ok=True)


def _iterar_execucoes(num_execucoes: int) -> range:
    return range(1, num_execucoes + 1)


def _registros_para_dataframe(registros: list, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [{column: getattr(registro, column) for column in columns} for registro in registros],
        columns=columns,
    )


@pytest.fixture
def e2e_context(monkeypatch: pytest.MonkeyPatch) -> E2EContext:
    override_original = os.environ.get("BUFALOS_CONFIG_PATH")

    try:
        os.environ["BUFALOS_CONFIG_PATH"] = E2E_CONFIG_PATH
        contexto = _carregar_contexto_e2e()
        _limpar_saida_e2e(contexto.resolver)
        _patch_ambiente_e2e(monkeypatch, contexto)
        yield contexto
    finally:
        if override_original is None:
            os.environ.pop("BUFALOS_CONFIG_PATH", None)
        else:
            os.environ["BUFALOS_CONFIG_PATH"] = override_original


def _patch_ambiente_e2e(
    monkeypatch: pytest.MonkeyPatch,
    contexto: E2EContext,
) -> None:
    monkeypatch.setattr(
        "src.controllers.imagem_controller.PathResolver.from_config",
        lambda: contexto.resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.PathResolver.from_config",
        lambda: contexto.resolver,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.PathResolver.from_config",
        lambda: contexto.resolver,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.PathResolver.from_config",
        lambda: contexto.resolver,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.MODELOS_PARA_AVALIACAO",
        contexto.modelos,
    )
    monkeypatch.setattr(
        "src.controllers.segmentacao_controller.NUM_EXECUCOES",
        contexto.num_execucoes,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.MODELOS_PARA_AVALIACAO",
        contexto.modelos,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.NUM_EXECUCOES",
        contexto.num_execucoes,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.GROUND_TRUTH_BINARIZATION_STRATEGY",
        contexto.ground_truth_strategy,
    )
    monkeypatch.setattr(
        "src.controllers.binarizacao_controller.SEGMENTACAO_BINARIZATION_STRATEGIES",
        contexto.segmentacao_strategies,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.MODELOS_PARA_AVALIACAO",
        contexto.modelos,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.NUM_EXECUCOES",
        contexto.num_execucoes,
    )
    monkeypatch.setattr(
        "src.controllers.avaliacao_controller.SEGMENTACAO_BINARIZATION_STRATEGIES",
        contexto.segmentacao_strategies,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.CHAIN_APPROX_NONE",
        1,
        raising=False,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.findContours",
        _fake_find_contours,
        raising=False,
    )
    monkeypatch.setattr(
        "src.metricas.segmentacao_binarizada.perimetro.cv2.arcLength",
        _fake_arc_length,
        raising=False,
    )


def _fake_find_contours(mask: np.ndarray, _mode: int, _method: int):
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return [], None

    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    contour = np.array(
        [
            [[x_min, y_min]],
            [[x_max, y_min]],
            [[x_max, y_max]],
            [[x_min, y_max]],
        ],
        dtype=np.int32,
    )
    return [contour], None


def _fake_arc_length(contour: np.ndarray, closed: bool = True) -> float:
    pontos = contour.reshape(-1, 2)
    if len(pontos) < 2:
        return 0.0

    deslocamentos = pontos[1:] - pontos[:-1]
    perimetro = float(np.linalg.norm(deslocamentos, axis=1).sum())
    if closed:
        perimetro += float(np.linalg.norm(pontos[0] - pontos[-1]))
    return perimetro


def _executar_fluxo_notebook_01(contexto: E2EContext) -> list:
    imagem_controller = ImagemController()
    imagem_controller.sincronizar_indice_excel()
    imagem_controller.verificar_pngs_corrompidos()

    segmentacao_controller = SegmentacaoController()
    linhas = segmentacao_controller.imagem_repository.list()
    try:
        segmentacao_controller.processar_imagens()
    except Exception as erro:
        pytest.skip(f"Ambiente sem suporte para executar rembg real: {erro}")

    return linhas


def _executar_fluxo_notebook_02(contexto: E2EContext) -> list:
    linhas = _executar_fluxo_notebook_01(contexto)

    imagem_controller = ImagemController()
    imagem_controller.verificar_segmentacoes()

    binarizacao_controller = BinarizacaoController()
    binarizacao_controller.processar_ground_truth_configurada()
    binarizacao_controller.processar_segmentacoes_configuradas()

    return linhas


@pytest.mark.e2e
def test_notebook_01_gera_segmentacoes(
    e2e_context: E2EContext,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = e2e_context.resolver
    modelos = e2e_context.modelos

    imagem_controller = ImagemController()
    imagem_controller.sincronizar_indice_excel()
    resumo_integridade = imagem_controller.verificar_pngs_corrompidos()

    segmentacao_controller = SegmentacaoController()
    try:
        resumos = segmentacao_controller.processar_imagens()
    except Exception as erro:
        pytest.skip(f"Ambiente sem suporte para executar rembg real: {erro}")
    linhas = ImagemRepository(resolver.sqlite_path).list()
    saidas_por_modelo_execucao = {
        (nome_modelo, execucao): sorted(
            (
                Path(resolver.segmentacoes_brutas_dir)
                / f"execucao_{execucao}"
                / nome_modelo
            ).glob("*.png")
        )
        for nome_modelo in modelos
        for execucao in _iterar_execucoes(e2e_context.num_execucoes)
    }

    assert resumo_integridade.total_png == 0
    assert len(linhas) == 5
    assert set(resumos) == set(modelos)
    for nome_modelo in modelos:
        assert resumos[nome_modelo].total == len(linhas) * e2e_context.num_execucoes
        assert resumos[nome_modelo].processadas == len(linhas) * e2e_context.num_execucoes
        assert resumos[nome_modelo].ok == len(linhas) * e2e_context.num_execucoes
        assert resumos[nome_modelo].erro == 0
        assert resumos[nome_modelo].skip == 0
    assert all(
        len(saidas) == len(linhas) for saidas in saidas_por_modelo_execucao.values()
    )


@pytest.mark.e2e
def test_notebook_02_binariza_ground_truth_e_segmentacoes(
    e2e_context: E2EContext,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = e2e_context.resolver
    modelos = e2e_context.modelos
    linhas = _executar_fluxo_notebook_02(e2e_context)

    saidas_ground_truth = sorted(Path(resolver.ground_truth_binarizada_dir).glob("*.png"))
    saidas_por_modelo_execucao = {
        (estrategia, nome_modelo, execucao): sorted(
            (
                Path(resolver.segmentacoes_binarizadas_dir)
                / f"execucao_{execucao}"
                / estrategia
                / nome_modelo
            ).glob("*.png")
        )
        for estrategia in e2e_context.segmentacao_strategies
        for nome_modelo in modelos
        for execucao in _iterar_execucoes(e2e_context.num_execucoes)
    }
    imagem_persistida = ImagemRepository(resolver.sqlite_path).get(
        linhas[0].nome_arquivo
    )

    assert len(saidas_ground_truth) == len(linhas)
    assert all(
        len(saidas) == len(linhas) for saidas in saidas_por_modelo_execucao.values()
    )
    assert imagem_persistida is not None
    assert imagem_persistida.ground_truth_binarizada is None
    assert imagem_persistida.segmentacoes_brutas == []


@pytest.mark.e2e
def test_notebook_03_calcula_e_persiste_avaliacoes(
    e2e_context: E2EContext,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = e2e_context.resolver
    modelos = e2e_context.modelos
    linhas = _executar_fluxo_notebook_02(e2e_context)

    avaliacao_controller = AvaliacaoController()
    stats = avaliacao_controller.processar_imagens()
    imagens = ImagemRepository(resolver.sqlite_path).list()
    pares_esperados = {
        (nome_modelo, execucao)
        for nome_modelo in modelos
        for execucao in _iterar_execucoes(e2e_context.num_execucoes)
    }

    assert stats.total == (
        len(linhas) * len(_iterar_execucoes(e2e_context.num_execucoes))
    )
    assert stats.ok == (
        len(linhas) * len(_iterar_execucoes(e2e_context.num_execucoes))
    )
    assert stats.erro == 0
    assert stats.skip == 0

    assert len(imagens) == len(linhas)
    assert all(imagem.ground_truth_binarizada is not None for imagem in imagens)
    assert all(
        {
            (segmentacao_bruta.nome_modelo, segmentacao_bruta.execucao)
            for segmentacao_bruta in imagem.segmentacoes_brutas
        }
        == pares_esperados
        for imagem in imagens
    )
    assert all(
        imagem.ground_truth_binarizada is not None
        and imagem.ground_truth_binarizada.area > 0
        and imagem.ground_truth_binarizada.perimetro > 0
        for imagem in imagens
    )
    assert all(
        segmentacao_binarizada.area > 0
        and segmentacao_binarizada.perimetro > 0
        and 0.0 <= segmentacao_binarizada.iou <= 1.0
        and 0.0 <= segmentacao_binarizada.precision <= 1.0
        and 0.0 <= segmentacao_binarizada.recall <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
        for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
    )
    assert all(
        0.0 <= segmentacao_bruta.auprc <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )
    assert all(
        0.0 <= segmentacao_bruta.soft_dice <= 1.0
        and 0.0 <= segmentacao_bruta.brier_score <= 1.0
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )
    assert all(
        {
            segmentacao_binarizada.estrategia_binarizacao
            for segmentacao_binarizada in segmentacao_bruta.segmentacoes_binarizadas
        }
        == set(e2e_context.segmentacao_strategies)
        for imagem in imagens
        for segmentacao_bruta in imagem.segmentacoes_brutas
    )


@pytest.mark.e2e
def test_notebook_04_persiste_camadas_estatisticas_da_segmentacao_bruta(
    e2e_context: E2EContext,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = e2e_context.resolver
    modelos = e2e_context.modelos
    linhas = _executar_fluxo_notebook_02(e2e_context)

    AvaliacaoController().processar_imagens()

    collector = MetricsCollector(
        force_recalculate=False,
        imagem_repository=ImagemRepository(resolver.sqlite_path),
    )
    resumo_modelo_repository = AnaliseSegmentacaoBrutaResumoModeloRepository(
        resolver.sqlite_path
    )
    resumo_execucao_repository = AnaliseSegmentacaoBrutaResumoExecucaoRepository(
        resolver.sqlite_path
    )
    resumo_tag_repository = AnaliseSegmentacaoBrutaResumoTagRepository(
        resolver.sqlite_path
    )
    estabilidade_repository = AnaliseSegmentacaoBrutaEstabilidadeRepository(
        resolver.sqlite_path
    )
    intervalo_repository = AnaliseSegmentacaoBrutaIntervaloConfiancaRepository(
        resolver.sqlite_path
    )
    teste_modelo_repository = AnaliseSegmentacaoBrutaTesteModeloRepository(
        resolver.sqlite_path
    )
    teste_tag_repository = AnaliseSegmentacaoBrutaTesteTagRepository(
        resolver.sqlite_path
    )
    interacao_repository = AnaliseSegmentacaoBrutaInteracaoTagModeloRepository(
        resolver.sqlite_path
    )

    df_base = collector.collect_all_metrics()
    df_resumo_modelo, _ = build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
        df_base=df_base,
        repository=resumo_modelo_repository,
    )
    df_resumo_execucao, _ = build_and_persist_analysis_segmentacao_bruta_resumo_execucao(
        df_base=df_base,
        repository=resumo_execucao_repository,
    )
    df_resumo_tag, _ = build_and_persist_analysis_segmentacao_bruta_resumo_tag(
        df_base=df_base,
        repository=resumo_tag_repository,
    )
    df_estabilidade, _ = build_and_persist_analysis_segmentacao_bruta_estabilidade(
        df_base=df_base,
        repository=estabilidade_repository,
    )
    df_intervalos, _ = build_and_persist_analysis_segmentacao_bruta_intervalo_confianca(
        df_base=df_base,
        repository=intervalo_repository,
    )
    df_testes_modelo, _ = build_and_persist_analysis_segmentacao_bruta_testes_modelo(
        df_base=df_base,
        repository=teste_modelo_repository,
    )
    df_testes_tag, _ = build_and_persist_analysis_segmentacao_bruta_testes_tag(
        df_base=df_base,
        repository=teste_tag_repository,
    )
    df_interacoes, _ = build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo(
        df_base=df_base,
        repository=interacao_repository,
    )

    resumo_modelo_registros = resumo_modelo_repository.list()
    resumo_execucao_registros = resumo_execucao_repository.list()
    resumo_tag_registros = resumo_tag_repository.list()
    estabilidade_registros = estabilidade_repository.list()
    intervalo_registros = intervalo_repository.list()
    testes_modelo_registros = teste_modelo_repository.list()
    testes_tag_registros = teste_tag_repository.list()
    interacoes_registros = interacao_repository.list()

    assert len(df_base) == len(linhas) * e2e_context.num_execucoes * len(modelos)

    assert len(df_resumo_modelo) == len(modelos) * 3
    assert len(resumo_modelo_registros) == len(df_resumo_modelo)
    assert {registro.nome_modelo for registro in resumo_modelo_registros} == set(modelos)
    assert {registro.metric_name for registro in resumo_modelo_registros} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }

    assert len(df_resumo_execucao) == len(modelos) * e2e_context.num_execucoes * 3
    assert len(resumo_execucao_registros) == len(df_resumo_execucao)
    assert {registro.execucao for registro in resumo_execucao_registros} == set(
        _iterar_execucoes(e2e_context.num_execucoes)
    )

    assert len(resumo_tag_registros) == len(df_resumo_tag)
    assert {registro.tag_name for registro in resumo_tag_registros} == {
        "tag_ok",
        "tag_multi_bufalos",
        "tag_cortado",
        "tag_angulo_extremo",
        "tag_baixo_contraste",
        "tag_ocluido",
    }
    assert {registro.metric_name for registro in resumo_tag_registros} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }
    assert {registro.tag_value for registro in resumo_tag_registros} == {False, True}

    assert len(estabilidade_registros) == len(df_estabilidade)
    assert {registro.metric_name for registro in estabilidade_registros} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }

    assert len(intervalo_registros) == len(df_intervalos)
    assert {registro.statistic_name for registro in intervalo_registros} == {
        "mean",
        "median",
    }

    assert len(testes_modelo_registros) == len(df_testes_modelo)
    assert df_testes_modelo.empty

    assert len(testes_tag_registros) == len(df_testes_tag)
    assert testes_tag_registros
    assert {registro.metric_name for registro in testes_tag_registros} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }

    assert len(interacoes_registros) == len(df_interacoes)
    assert interacoes_registros
    assert {registro.metric_name for registro in interacoes_registros} == {
        "auprc",
        "soft_dice",
        "brier_score",
    }


@pytest.mark.e2e
def test_notebook_05_gera_visualizacoes_da_segmentacao_bruta(
    e2e_context: E2EContext,
) -> None:
    try:
        import rembg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("rembg nao esta instalado no ambiente.")

    resolver = e2e_context.resolver
    _executar_fluxo_notebook_02(e2e_context)
    AvaliacaoController().processar_imagens()

    collector = MetricsCollector(
        force_recalculate=False,
        imagem_repository=ImagemRepository(resolver.sqlite_path),
    )
    df_base = collector.collect_all_metrics()

    resumo_modelo_repository = AnaliseSegmentacaoBrutaResumoModeloRepository(
        resolver.sqlite_path
    )
    resumo_execucao_repository = AnaliseSegmentacaoBrutaResumoExecucaoRepository(
        resolver.sqlite_path
    )
    resumo_tag_repository = AnaliseSegmentacaoBrutaResumoTagRepository(
        resolver.sqlite_path
    )
    estabilidade_repository = AnaliseSegmentacaoBrutaEstabilidadeRepository(
        resolver.sqlite_path
    )
    intervalo_repository = AnaliseSegmentacaoBrutaIntervaloConfiancaRepository(
        resolver.sqlite_path
    )
    teste_modelo_repository = AnaliseSegmentacaoBrutaTesteModeloRepository(
        resolver.sqlite_path
    )
    teste_tag_repository = AnaliseSegmentacaoBrutaTesteTagRepository(
        resolver.sqlite_path
    )
    interacao_repository = AnaliseSegmentacaoBrutaInteracaoTagModeloRepository(
        resolver.sqlite_path
    )

    build_and_persist_analysis_segmentacao_bruta_resumo_modelo(
        df_base=df_base,
        repository=resumo_modelo_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_resumo_execucao(
        df_base=df_base,
        repository=resumo_execucao_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_resumo_tag(
        df_base=df_base,
        repository=resumo_tag_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_estabilidade(
        df_base=df_base,
        repository=estabilidade_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_intervalo_confianca(
        df_base=df_base,
        repository=intervalo_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_testes_modelo(
        df_base=df_base,
        repository=teste_modelo_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_testes_tag(
        df_base=df_base,
        repository=teste_tag_repository,
    )
    build_and_persist_analysis_segmentacao_bruta_interacao_tag_modelo(
        df_base=df_base,
        repository=interacao_repository,
    )

    df_resumo_modelo = _registros_para_dataframe(
        resumo_modelo_repository.list(),
        [
            "nome_modelo",
            "metric_name",
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "q1",
            "q3",
            "iqr",
            "higher_is_better",
        ],
    )
    df_resumo_execucao = _registros_para_dataframe(
        resumo_execucao_repository.list(),
        [
            "nome_modelo",
            "execucao",
            "metric_name",
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "q1",
            "q3",
            "iqr",
            "higher_is_better",
        ],
    )
    df_resumo_tag = _registros_para_dataframe(
        resumo_tag_repository.list(),
        [
            "nome_modelo",
            "tag_name",
            "tag_value",
            "metric_name",
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "q1",
            "q3",
            "iqr",
            "higher_is_better",
        ],
    )
    df_estabilidade = _registros_para_dataframe(
        estabilidade_repository.list(),
        [
            "nome_modelo",
            "metric_name",
            "count_execucoes",
            "mean_execucoes",
            "std_execucoes",
            "cv_execucoes",
            "amplitude_execucoes",
            "melhor_execucao",
            "pior_execucao",
            "higher_is_better",
        ],
    )
    df_intervalo_confianca = _registros_para_dataframe(
        intervalo_repository.list(),
        [
            "nome_modelo",
            "metric_name",
            "statistic_name",
            "count",
            "estimate",
            "ci_low",
            "ci_high",
            "confidence_level",
            "n_resamples",
            "higher_is_better",
        ],
    )
    df_testes_modelo = _registros_para_dataframe(
        teste_modelo_repository.list(),
        [
            "metric_name",
            "comparison_scope",
            "test_name",
            "group_a",
            "group_b",
            "n_group_a",
            "n_group_b",
            "statistic",
            "p_value",
            "p_value_adjusted",
            "effect_size",
            "effect_size_label",
            "mean_group_a",
            "mean_group_b",
            "median_group_a",
            "median_group_b",
            "favored_group",
        ],
    )
    df_testes_tag = _registros_para_dataframe(
        teste_tag_repository.list(),
        [
            "metric_name",
            "tag_name",
            "comparison_scope",
            "nome_modelo",
            "test_name",
            "n_group_a",
            "n_group_b",
            "statistic",
            "p_value",
            "p_value_adjusted",
            "effect_size",
            "effect_size_label",
            "mean_com_tag",
            "mean_sem_tag",
            "median_com_tag",
            "median_sem_tag",
            "delta_mean",
            "delta_median",
        ],
    )
    df_interacoes = _registros_para_dataframe(
        interacao_repository.list(),
        [
            "nome_modelo",
            "tag_name",
            "metric_name",
            "count_com_tag",
            "count_sem_tag",
            "mean_com_tag",
            "mean_sem_tag",
            "median_com_tag",
            "median_sem_tag",
            "delta_mean",
            "delta_median",
            "relative_delta_mean",
            "adjusted_delta_mean",
            "adjusted_delta_median",
            "impact_direction",
            "higher_is_better",
        ],
    )

    assert not df_base.empty
    assert not df_resumo_modelo.empty
    assert not df_intervalo_confianca.empty
    assert not df_interacoes.empty

    metric_names = ["auprc", "soft_dice", "brier_score"]
    metric_pairs = [("auprc", "soft_dice"), ("auprc", "brier_score"), ("soft_dice", "brier_score")]
    regression_metrics = ["soft_dice", "brier_score"]
    interaction_metrics = ["auprc", "soft_dice", "brier_score"]

    generated_figures = 0
    figures_univariada = []
    figures_distribuicao = []
    figures_correlacao = []
    figures_regressao = []
    figures_interacoes = []

    for metric_name in metric_names:
        fig, ax = plot_metric_bars_with_ci_by_model(
            df_resumo_modelo, df_intervalo_confianca, metric_name
        )
        assert ax.has_data()
        figures_univariada.append(fig)
        generated_figures += 1

        fig, ax = plot_metric_distribution_by_model(df_base, metric_name)
        assert ax.has_data()
        figures_distribuicao.append(fig)
        generated_figures += 1

    for x_metric, y_metric in metric_pairs:
        fig, ax = plot_metric_scatter(df_base, x_metric, y_metric)
        assert ax.has_data()
        figures_correlacao.append(fig)
        generated_figures += 1

    for method in ["pearson", "spearman"]:
        fig, ax = plot_metric_correlation_heatmap(df_base, metric_names, method)
        assert ax.images
        figures_correlacao.append(fig)
        generated_figures += 1

    for metric_name in regression_metrics:
        fig, ax = plot_simple_regression(df_base, "num_tags_problema", metric_name)
        assert ax.has_data()
        figures_regressao.append(fig)
        generated_figures += 1

    for metric_name in interaction_metrics:
        fig, ax = plot_model_tag_interaction_heatmap(df_interacoes, metric_name)
        assert ax.images
        figures_interacoes.append(fig)
        generated_figures += 1

    expected_figures = (
        len(metric_names)
        + len(metric_names)
        + len(metric_pairs)
        + 2
        + len(regression_metrics)
        + len(interaction_metrics)
    )
    assert generated_figures == expected_figures

    pdf_path = Path(resolver.generated_dir) / "05_visualizacao_segmentacao_bruta.pdf"
    saved_pdf_path = save_pdf_report(
        output_path=pdf_path,
        report_title="05 - Visualizacao da Segmentacao Bruta",
        sections=[
            PdfReportSection(
                heading="Carregamento das tabelas analiticas e da base linha a linha",
                body=(
                    "A visualizacao agora usa apenas o que e mais util para leitura do projeto: "
                    "resumos por modelo, intervalos de confianca, interacoes com dificuldade e a base linha a linha para correlacao e regressao."
                ),
            ),
            PdfReportSection(
                heading="Estatistica descritiva univariada",
                body=(
                    "Este bloco resume cada metrica por modelo usando estimativa central e intervalo de confianca, "
                    "o que torna a comparacao mais informativa do que olhar apenas medias isoladas."
                ),
                figures=figures_univariada,
            ),
            PdfReportSection(
                heading="Distribuicoes por modelo",
                body=(
                    "Os boxplots mostram densidade, centralidade e dispersao diretamente na base linha a linha, "
                    "complementando os intervalos de confianca com a forma da distribuicao."
                ),
                figures=figures_distribuicao,
            ),
            PdfReportSection(
                heading="Analise bivariada e correlacao",
                body=(
                    "Aqui avaliamos se as metricas contam historias complementares ou redundantes, "
                    "usando graficos bivariados e matrizes de correlacao de Pearson e Spearman."
                ),
                figures=figures_correlacao,
            ),
            PdfReportSection(
                heading="Regressao simples",
                body=(
                    "A regressao simples usa num_tags_problema como proxy de dificuldade "
                    "para medir a tendencia de degradacao das metricas mais interpretaveis para a segmentacao bruta."
                ),
                figures=figures_regressao,
            ),
            PdfReportSection(
                heading="Interacao entre modelo e dificuldade",
                body=(
                    "Para manter o relatorio sucinto, este bloco mostra as tres metricas brutas principais "
                    "para enxergar queda de qualidade com dificuldade: auprc, soft_dice e brier_score."
                ),
                figures=figures_interacoes,
            ),
            PdfReportSection(
                heading="Leitura inicial",
                body=(
                    "O notebook 05 agora prioriza menos paineis e mais leitura analitica: "
                    "univariada com intervalo de confianca, distribuicao, associacao entre metricas, "
                    "correlacao, regressao simples e relacao entre modelo e dificuldade."
                ),
            ),
        ],
    )

    assert saved_pdf_path == pdf_path
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0

    for figure in (
        figures_univariada
        + figures_distribuicao
        + figures_correlacao
        + figures_regressao
        + figures_interacoes
    ):
        plt.close(figure)
