import pytest
from smooth_criminal.core import dangerous

@dangerous
def heavy_math():
    total = 0
    for i in range(1, 5000):
        total += i ** 0.5
    return round(total, 2)

def test_dangerous_execution():
    result = heavy_math()
    expected = round(sum(i ** 0.5 for i in range(1, 5000)), 2)
    assert abs(result - expected) < 1e-6

def test_dangerous_exception():
    def fail(x):
        raise ValueError("boom")
    wrapped = dangerous(fail)
    with pytest.raises(ValueError):
        wrapped(1)
