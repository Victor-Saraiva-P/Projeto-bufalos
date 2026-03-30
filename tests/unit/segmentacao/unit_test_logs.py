import time

from src.logs import EstatisticasProcessamentoComEta, formatar_duracao


def test_estatisticas_processamento_atualiza_contadores() -> None:
    stats = EstatisticasProcessamentoComEta(total=3)

    stats.registrar_ok_com_duracao(0.5)
    stats.registrar_skip()
    stats.registrar_erro()

    assert stats.processadas == 3
    assert stats.ok == 1
    assert stats.skip == 1
    assert stats.erro == 1
    assert stats.tempo_inferencia == 0.5


def test_tempo_execucao_retorna_duracao_nao_negativa() -> None:
    stats = EstatisticasProcessamentoComEta(total=1)

    time.sleep(0.01)

    assert stats.tempo_execucao >= 0.0


def test_formatar_duracao_formata_minutos_e_segundos() -> None:
    assert formatar_duracao(None) == "--"
    assert formatar_duracao(5) == "5s"
    assert formatar_duracao(65) == "1m05s"
    assert formatar_duracao(3661) == "1h01m01s"
