import pytest
from smooth_criminal.core import bad

@bad(parallel=False)
def sum_sqrt(n):
    total = 0.0
    for i in range(1, n + 1):
        total += i ** 0.5
    return round(total, 2)

def test_bad_aggressive_optimization():
    result = sum_sqrt(1000)
    expected = round(sum(i ** 0.5 for i in range(1, 1001)), 2)
    assert abs(result - expected) < 1e-6

def test_bad_exception():
    def fail(x, y):
        raise ValueError("boom")
    wrapped = bad(parallel=False)(fail)
    with pytest.raises(ValueError):
        wrapped(1, 2)
