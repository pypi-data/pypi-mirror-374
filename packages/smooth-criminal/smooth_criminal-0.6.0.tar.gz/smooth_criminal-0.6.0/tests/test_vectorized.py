import numpy as np
from smooth_criminal.core import vectorized


@vectorized(["float64(float64, float64)"])
def add(a, b):
    return a + b


def test_vectorized_basic():
    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    np.testing.assert_array_equal(add(a, b), np.array([4.0, 6.0]))


def test_vectorized_fallback():
    @vectorized(["float64(float64)"], target="badtarget")
    def inc(x):
        return x + 1

    arr = np.array([1.0, 2.0])
    np.testing.assert_array_equal(inc(arr), np.array([2.0, 3.0]))
