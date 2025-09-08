from smooth_criminal.memory import get_execution_history, build_summary, calcular_score
from smooth_criminal.flet_app.utils import formatear_tiempo

def test_refresh_logic(monkeypatch):
    # Simular historial con monkeypatch
    fake_history = [
        {"function": "foo", "duration": 0.001, "decorator": "@smooth"},
        {"function": "foo", "duration": 0.002, "decorator": "@smooth"},
        {"function": "bar", "duration": 0.01,  "decorator": "@jam"},
    ]

    monkeypatch.setattr("smooth_criminal.memory.get_execution_history", lambda: fake_history)

    # Procesar resumen
    resumen = build_summary(get_execution_history())

    # Verificaciones
    assert "foo" in resumen
    assert len(resumen["foo"]["durations"]) == 2
    assert resumen["foo"]["decorators"] == {"@smooth"}

    avg = sum(resumen["foo"]["durations"]) / len(resumen["foo"]["durations"])
    score = calcular_score(resumen["foo"]["durations"], resumen["foo"]["decorators"])
    assert formatear_tiempo(avg).endswith("s")
    assert 80 <= score <= 100
