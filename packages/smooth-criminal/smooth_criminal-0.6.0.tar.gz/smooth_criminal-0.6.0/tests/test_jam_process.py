import pytest
from smooth_criminal.core import jam


@jam(workers=2, backend="process")
def square(x):
    return x * x


def test_jam_process_execution(numbers):
    expected = [n * n for n in numbers]
    result = square(numbers)
    assert sorted(result) == expected


def test_jam_process_worker_exception(numbers):
    @jam(workers=2, backend="process")
    def maybe_fail(x):
        if x == 3:
            raise ValueError("boom")
        return x * x

    result = maybe_fail(numbers[:3])
    assert sorted(result) == [1, 4]
