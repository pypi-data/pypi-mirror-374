import os
from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import suggest_boost

LOG_PATH = Path.home() / ".smooth_criminal_log.json"

@auto_boost()
def test_func_to_suggest():
    return sum(i for i in range(500))

def test_suggest_boost_recommendation():
    # Limpiar log antes del test si existe
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    # Ejecutar varias veces para generar datos
    for _ in range(3):
        test_func_to_suggest()

    # Obtener sugerencia
    suggestion = suggest_boost("test_func_to_suggest")

    # Validar que sugiere algo coherente
    assert "use" in suggestion
    assert "@smooth" in suggestion or "@jam" in suggestion
