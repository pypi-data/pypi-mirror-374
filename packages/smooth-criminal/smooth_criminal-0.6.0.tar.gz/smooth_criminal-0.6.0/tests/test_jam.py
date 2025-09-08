import pytest
from smooth_criminal.core import jam


@jam(workers=3, backend="thread")
def square(x):
    return x * x


def test_jam_parallel_execution(numbers):
    expected = [n * n for n in numbers]
    result = square(numbers)
    assert sorted(result) == expected


def test_jam_worker_exception(numbers):
    @jam(workers=2, backend="thread")
    def maybe_fail(x):
        if x == 3:
            raise ValueError("boom")
        return x * x

    result = maybe_fail(numbers[:3])
    assert sorted(result) == [1, 4]  # 3 falla y se omite

