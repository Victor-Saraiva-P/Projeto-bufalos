import math

from src.metricas import AreaSimilarity, PerimetroSimilarity


def test_area_similarity_retorna_um_quando_areas_sao_iguais() -> None:
    resultado = AreaSimilarity(
        nome_arquivo="bufalo_001",
        area_modelo=100.0,
        area_ground_truth=100.0,
        modelo="u2netp",
    ).calcular()

    assert resultado == 1.0


def test_area_similarity_reduz_linearmente_com_erro_relativo() -> None:
    resultado = AreaSimilarity(
        nome_arquivo="bufalo_001",
        area_modelo=75.0,
        area_ground_truth=100.0,
        modelo="u2netp",
    ).calcular()

    assert math.isclose(resultado, 0.75, rel_tol=1e-9)


def test_area_similarity_piso_zero_quando_erro_relativo_supera_um() -> None:
    resultado = AreaSimilarity(
        nome_arquivo="bufalo_001",
        area_modelo=250.0,
        area_ground_truth=100.0,
        modelo="u2netp",
    ).calcular()

    assert resultado == 0.0


def test_perimetro_similarity_trata_ground_truth_zero() -> None:
    igual = PerimetroSimilarity(
        nome_arquivo="bufalo_001",
        perimetro_modelo=0.0,
        perimetro_ground_truth=0.0,
        modelo="u2netp",
    ).calcular()
    diferente = PerimetroSimilarity(
        nome_arquivo="bufalo_001",
        perimetro_modelo=10.0,
        perimetro_ground_truth=0.0,
        modelo="u2netp",
    ).calcular()

    assert igual == 1.0
    assert diferente == 0.0
