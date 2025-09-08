import logging
import pytest
from smooth_criminal.core import thriller


@thriller
def simple_loop():
    total = 0
    for i in range(1000):
        total += i
    return total


def test_thriller_runs():
    result = simple_loop()
    assert result == sum(range(1000))


def test_thriller_exception(failing_func):
    wrapped = thriller(failing_func)
    with pytest.raises(ValueError):
        wrapped()


def test_thriller_improvement_message(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    from smooth_criminal import core

    history = [{"duration": 10.0, "decorator": "@thriller"}]

    def fake_get_history(name):
        return history

    def fake_log_stats(func_name, input_type, decorator_used, duration):
        history.append({"duration": duration, "decorator": decorator_used})

    monkeypatch.setattr(core.memory, "get_execution_history", fake_get_history)
    monkeypatch.setattr(core.memory, "log_execution_stats", fake_log_stats)

    core._THRILLER_ANNOUNCED.clear()

    @thriller
    def fast_func():
        return 42

    fast_func()
    fast_func()

    msgs = [m for m in caplog.messages if "THRILLED the benchmarks" in m]
    assert len(msgs) == 1

