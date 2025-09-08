import numpy as np
from smooth_criminal.core import guvectorized


@guvectorized(["void(float64[:], float64[:], float64[:])"], "(n),(n)->(n)")
def add_vec(a, b, res):
    for i in range(a.shape[0]):
        res[i] = a[i] + b[i]


def test_guvectorized_basic():
    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    np.testing.assert_array_equal(add_vec(a, b), np.array([4.0, 6.0]))


def test_guvectorized_fallback():
    @guvectorized(["void(float64[:], float64[:], float64[:])"], "(n),(n)->(n)", target="badtarget")
    def add_bad(a, b, res):
        for i in range(a.shape[0]):
            res[i] = a[i] + b[i]

    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    out = np.empty_like(a)
    result = add_bad(a, b, out)
    assert result is None
    np.testing.assert_array_equal(out, np.array([4.0, 6.0]))
