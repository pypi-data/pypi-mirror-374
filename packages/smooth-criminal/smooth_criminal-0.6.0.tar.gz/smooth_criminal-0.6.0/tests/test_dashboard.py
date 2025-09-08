from smooth_criminal.core import auto_boost
from smooth_criminal.dashboard import render_dashboard
from smooth_criminal.memory import get_execution_history
from io import StringIO
from rich.console import Console
import sys

@auto_boost()
def dashboard_test_func():
    return sum(i for i in range(3000))

def test_render_dashboard_output(capsys):
    # Ejecutar la función varias veces para llenar historial
    for _ in range(3):
        dashboard_test_func()

    # Redirigir salida a buffer
    console = Console(file=StringIO())
    original_stdout = sys.stdout
    sys.stdout = console.file

    # Ejecutar dashboard
    render_dashboard()

    # Restaurar stdout y obtener contenido
    sys.stdout = original_stdout
    output = console.file.getvalue()

    # Verificamos que se imprimió la función
    assert "dashboard_test_func" in output
    assert "@smooth" in output or "@jam" in output
    assert "Avg Time" in output or "avg" in output.lower()
