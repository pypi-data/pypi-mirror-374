from smooth_criminal.core import auto_boost
from smooth_criminal.memory import score_function, clear_execution_history

@auto_boost()
def score_test_func():
    return sum(i for i in range(1000))

def test_score_function_evaluation():
    # Limpiar historial antes
    clear_execution_history()

    # Generar registros
    for _ in range(5):
        score_test_func()

    # Obtener puntuación
    score, summary = score_function("score_test_func")

    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert "score_test_func" in summary
    assert "- Executions:" in summary
    assert "- Avg time:" in summary
    assert "- Decorators:" in summary
