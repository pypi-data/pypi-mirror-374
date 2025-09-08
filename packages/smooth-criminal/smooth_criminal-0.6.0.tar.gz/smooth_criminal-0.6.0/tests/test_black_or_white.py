import numpy as np
import pytest
from smooth_criminal.core import black_or_white

@black_or_white(mode="light")
def double_array(arr):
    return arr * 2

@black_or_white(mode="precise")
def triple_array(arr):
    return arr * 3

def test_black_or_white_light_mode(simple_array):
    result = double_array(simple_array)
    assert result.dtype == np.float32

def test_black_or_white_precise_mode(simple_array):
    result = triple_array(simple_array.astype(np.float32))
    assert result.dtype == np.float64

def test_black_or_white_exception(simple_array, failing_func):
    wrapped = black_or_white()(failing_func)
    with pytest.raises(ValueError):
        wrapped(simple_array)
