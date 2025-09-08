import json
import pytest
from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import get_execution_history

LOG_PATH = Path.home() / ".smooth_criminal_log.json"


@auto_boost()
def boosted_function():
    return sum(i for i in range(1000))


@auto_boost()
def square(x):
    return x * x


def fallback(_):
    return -1


@auto_boost(fallback=fallback)
def failing(x):
    raise ValueError("boom")


def test_auto_boost_memory_logs():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    boosted_function()
    assert LOG_PATH.exists()
    history = get_execution_history("boosted_function")
    assert len(history) > 0
    entry = history[-1]
    assert entry["function"] == "boosted_function"
    assert entry["decorator"] in ("@smooth", "@jam", "none")
    assert isinstance(entry["duration"], float)
    assert entry["duration"] > 0


def test_auto_boost_normal(numbers):
    result = square(numbers[:3])
    assert sorted(result) == [1, 4, 9]


def test_auto_boost_fallback(numbers):
    result = failing(numbers[:3])
    assert result == [-1, -1, -1]
