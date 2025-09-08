from smooth_criminal.memory import calcular_score
from smooth_criminal.flet_app.utils import (
    formatear_tiempo,
    export_filename
)

def test_calcular_score_basic():
    durations = [0.001, 0.002, 0.0015]
    decorators = {"@smooth"}
    score = calcular_score(durations, decorators)
    assert isinstance(score, int)
    assert 80 <= score <= 100

def test_calcular_score_penalized():
    durations = [0.02, 0.03, 0.025]
    decorators = {"@none"}
    score = calcular_score(durations, decorators)
    assert score < 80

def test_formatear_tiempo():
    tiempo = 0.002345678
    formatted = formatear_tiempo(tiempo)
    assert formatted.endswith("s")
    assert formatted.startswith("0.002345")

def test_export_filename_format():
    name = export_filename()
    assert name.startswith("smooth_export_")
    assert name.endswith(".csv")
    assert len(name) > 20
