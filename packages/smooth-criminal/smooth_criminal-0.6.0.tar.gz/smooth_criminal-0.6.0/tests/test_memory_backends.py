import importlib

import pytest


@pytest.mark.parametrize("backend", ["json", "sqlite", "tinydb"])
def test_storage_backends(monkeypatch, tmp_path, backend):
    """Verifica operaciones básicas para cada backend disponible."""

    monkeypatch.setenv("SMOOTH_CRIMINAL_STORAGE", backend)
    import smooth_criminal.memory as memory
    importlib.reload(memory)

    # Limpiar cualquier rastro previo
    if memory.LOG_PATH.exists():
        memory._BACKEND.clear_execution_history()

    # Registrar una ejecución
    memory.log_execution_stats("demo", int, "@smooth", 0.001)
    history = memory.get_execution_history("demo")
    assert history and history[0]["function"] == "demo"

    # Exportar historial
    csv_file = tmp_path / "hist.csv"
    assert memory.export_execution_history(csv_file)
    assert csv_file.exists()

    # Calcular puntuación
    score, summary = memory.score_function("demo")
    assert score is not None and "Function: demo" in summary

    # Limpiar y comprobar
    assert memory._BACKEND.clear_execution_history()
    assert not memory.LOG_PATH.exists()

    # Restaurar backend por defecto para no afectar a otras pruebas
    monkeypatch.delenv("SMOOTH_CRIMINAL_STORAGE", raising=False)
    importlib.reload(memory)

