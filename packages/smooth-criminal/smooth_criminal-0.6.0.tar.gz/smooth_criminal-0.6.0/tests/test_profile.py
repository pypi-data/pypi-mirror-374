from smooth_criminal.core import profile_it

def dummy_func():
    total = 0
    for i in range(10000):
        total += i
    return total

def test_profile_it_metrics():
    stats = profile_it(dummy_func, repeat=5)

    assert isinstance(stats, dict)
    assert "mean" in stats
    assert "best" in stats
    assert "std_dev" in stats
    assert "runs" in stats
    assert len(stats["runs"]) == 5
    assert all(isinstance(t, float) and t > 0 for t in stats["runs"])
