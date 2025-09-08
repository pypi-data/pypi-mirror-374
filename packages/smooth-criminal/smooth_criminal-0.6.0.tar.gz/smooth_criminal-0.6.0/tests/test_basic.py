from smooth_criminal.core import smooth

@smooth
def test_sum():
    return sum([i for i in range(10000)])

def test_run():
    assert test_sum() == sum(range(10000))
