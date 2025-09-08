import subprocess
import sys
from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import get_execution_history

LOG_PATH = Path.home() / ".smooth_criminal_log.json"

@auto_boost()
def cli_suggest_target():
    return sum(i for i in range(1000))

def test_cli_suggest_command(monkeypatch):
    # Limpiar logs
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    # Ejecutar varias veces para generar historial
    for _ in range(3):
        cli_suggest_target()

    # Llamar a la CLI como si fuera por terminal
    result = subprocess.run(
        [sys.executable, "-m", "smooth_criminal.cli", "suggest", "cli_suggest_target"],
        capture_output=True,
        text=True
    )

    output = result.stdout
    assert "Suggestion for 'cli_suggest_target'" in output
    assert "@smooth" in output or "@jam" in output
