import pytest
from smooth_criminal.core import beat_it

def fallback_add(x):
    return x + 1

@beat_it(fallback_func=fallback_add)
def faulty_add(x):
    return x + "💥"  # Provocará TypeError

@beat_it()
def good_add(a, b):
    return a + b

def test_beat_it_fallback():
    result = faulty_add(10)
    assert result == 11

def test_beat_it_normal():
    assert good_add(2, 3) == 5

def test_beat_it_no_fallback(failing_func):
    wrapped = beat_it()(failing_func)
    with pytest.raises(ValueError):
        wrapped()
