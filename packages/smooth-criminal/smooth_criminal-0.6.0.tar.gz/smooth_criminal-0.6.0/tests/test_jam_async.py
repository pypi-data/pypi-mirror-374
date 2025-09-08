import asyncio
import pytest
from smooth_criminal.core import jam


@jam(workers=2, backend="async")
async def square_async(x):
    await asyncio.sleep(0)
    return x * x


def test_jam_async_function(numbers):
    expected = [n * n for n in numbers]
    result = asyncio.run(square_async(numbers))
    assert sorted(result) == expected


@jam(workers=2, backend="async")
def square_sync(x):
    return x * x


def test_jam_async_with_sync_func(numbers):
    expected = [n * n for n in numbers]
    result = asyncio.run(square_sync(numbers))
    assert sorted(result) == expected
