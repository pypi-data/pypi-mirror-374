import os
import tempfile
import matplotlib.pyplot as plt
from smooth_criminal.memory import get_execution_history
from smooth_criminal.core import auto_boost


@auto_boost()
def func_to_graph():
    return sum(i for i in range(1000))

def test_graph_generation():
    # Ejecutar varias veces para crear historial
    for _ in range(5):
        func_to_graph()

    history = get_execution_history()
    func_name = "func_to_graph"
    times = [entry["duration"] for entry in history if entry["function"] == func_name]

    assert len(times) >= 3, "No hay suficientes datos para graficar."

    # Generar gráfico y guardarlo temporalmente
    fig, ax = plt.subplots()
    ax.plot(times, marker='o')
    ax.set_title(f"Historial de tiempos: {func_name}")
    ax.set_xlabel("Ejecución")
    ax.set_ylabel("Duración (s)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name)
        path = tmp.name

    plt.close(fig)

    # Verificar que el archivo existe y tiene tamaño
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

    # Limpieza
    os.remove(path)
