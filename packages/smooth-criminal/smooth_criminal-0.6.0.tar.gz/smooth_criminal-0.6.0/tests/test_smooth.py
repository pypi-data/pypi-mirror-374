import pytest
from smooth_criminal.core import smooth


@smooth
def square_numbers(n):
    return [i * i for i in range(n)]


def test_smooth_basic():
    result = square_numbers(5)
    assert result == [0, 1, 4, 9, 16]


def test_smooth_exception(failing_func):
    wrapped = smooth(failing_func)
    with pytest.raises(ValueError):
        wrapped()

