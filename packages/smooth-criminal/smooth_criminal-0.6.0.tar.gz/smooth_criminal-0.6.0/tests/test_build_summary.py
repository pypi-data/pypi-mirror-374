import pytest
from smooth_criminal.memory import build_summary


def test_build_summary_basic():
    logs = [
        {"function": "foo", "duration": 0.1, "decorator": "@smooth"},
        {"function": "foo", "duration": 0.2, "decorator": "@smooth"},
        {"function": "bar", "duration": 0.3, "decorator": "@jam"},
    ]
    summary = build_summary(logs)
    assert set(summary.keys()) == {"foo", "bar"}
    assert summary["foo"]["decorators"] == {"@smooth"}
    assert summary["bar"]["durations"] == [0.3]


def test_build_summary_empty():
    assert build_summary([]) == {}
