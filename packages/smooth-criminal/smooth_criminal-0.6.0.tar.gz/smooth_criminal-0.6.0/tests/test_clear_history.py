from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import (
    get_execution_history,
    clear_execution_history,
    LOG_PATH
)

@auto_boost()
def test_clear_target():
    return sum(i for i in range(1000))

def test_clear_execution_history():
    # Ejecutar varias veces para crear historial
    for _ in range(2):
        test_clear_target()

    # Verificar que hay historial
    assert LOG_PATH.exists()
    assert len(get_execution_history("test_clear_target")) > 0

    # Borrar historial
    result = clear_execution_history()
    assert result is True
    assert not LOG_PATH.exists()

    # Verificar que la lectura devuelve vacío
    assert get_execution_history() == []
