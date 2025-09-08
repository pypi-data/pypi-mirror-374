from smooth_criminal.benchmark import benchmark_jam, detect_fastest_backend


def cube(x: int) -> int:
    return x ** 3


def test_benchmark_generates_metrics_for_all_backends():
    args = [1, 2, 3]
    result = benchmark_jam(cube, args, ["thread", "process", "async"])
    backends = {m["backend"] for m in result["metrics"]}
    assert backends == {"thread", "process", "async"}
    assert result["fastest"] in backends


def test_detect_fastest_backend_returns_valid_backend():
    best = detect_fastest_backend(cube, [1, 2, 3], ["thread", "process", "async"])
    assert best in {"thread", "process", "async"}
