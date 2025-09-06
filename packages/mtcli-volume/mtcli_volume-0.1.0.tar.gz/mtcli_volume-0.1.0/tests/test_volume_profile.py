import pytest
from mtcli_volume.volume_profile import calcular_volume_profile, calcular_estatisticas


# Simula candles com preços de fechamento e volumes
@pytest.fixture
def dados_simulados():
    return [
        {"close": 100, "tick_volume": 120},
        {"close": 101, "tick_volume": 80},
        {"close": 100, "tick_volume": 100},
        {"close": 102, "tick_volume": 50},
        {"close": 101, "tick_volume": 90},
        {"close": 100, "tick_volume": 70},
    ]


def test_calculo_volume_profile(dados_simulados):
    profile = calcular_volume_profile(dados_simulados, step=1)
    assert isinstance(profile, dict)
    assert profile[100] == 290  # 120 + 100 + 70
    assert profile[101] == 170  # 80 + 90
    assert profile[102] == 50


def test_estatisticas_volume_profile(dados_simulados):
    profile = calcular_volume_profile(dados_simulados, step=1)
    stats = calcular_estatisticas(profile)

    assert "poc" in stats
    assert "area_valor" in stats
    assert "hvns" in stats
    assert "lvns" in stats

    assert stats["poc"] == 100
    assert isinstance(stats["hvns"], list)
    assert isinstance(stats["lvns"], list)
    assert stats["area_valor"][0] <= stats["poc"] <= stats["area_valor"][1]
