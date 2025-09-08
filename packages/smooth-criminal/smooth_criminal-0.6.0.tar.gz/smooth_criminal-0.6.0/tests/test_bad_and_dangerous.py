from pathlib import Path

import pytest

from smooth_criminal import bad_and_dangerous
from smooth_criminal.memory import get_execution_history

LOG_PATH = Path.home() / ".smooth_criminal_log.json"


def test_bad_and_dangerous_execution_and_log():
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    @bad_and_dangerous(parallel=False)
    def compute(n):
        total = 0.0
        for i in range(1, n + 1):
            total += i ** 0.5
        return round(total, 2)

    result = compute(100)
    expected = round(sum(i ** 0.5 for i in range(1, 101)), 2)
    assert abs(result - expected) < 1e-6

    history = get_execution_history("compute")
    assert history
    assert history[-1]["decorator"] == "@bad_and_dangerous"


def test_bad_and_dangerous_profiling(monkeypatch):
    called = {"profile": 0, "log": 0}

    def fake_profile(func, args=(), kwargs=None, repeat=5, parallel=False):
        called["profile"] += 1
        return {"mean": 0.01, "best": 0.01, "std_dev": 0.0, "runs": [0.01]}

    def fake_log(**kwargs):
        called["log"] += 1

    monkeypatch.setattr("smooth_criminal.core.profile_it", fake_profile)
    monkeypatch.setattr("smooth_criminal.core.log_execution_stats", fake_log)

    @bad_and_dangerous(parallel=False)
    def add(a, b):
        return a + b

    add(1, 2)
    assert called["profile"] == 1
    assert called["log"] == 1


def test_bad_and_dangerous_fallback():
    def fb(_):
        return -1

    @bad_and_dangerous(fallback=fb, parallel=False)
    def boom(x):
        raise ValueError("boom")

    assert boom(1) == -1
