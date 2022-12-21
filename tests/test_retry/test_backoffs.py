from typing import Any

import pytest

from hyx.retry import backoffs


@pytest.mark.parametrize("value", [
    0.5,
    1,
    2,
])
async def test__retry__const_backoff(value: float) -> None:
    backoff = backoffs.const(wait=value)

    actual_results = [
        await backoff.__anext__()
        for _ in range(5)
    ]

    for delay in actual_results:
        assert delay == value


@pytest.mark.parametrize("params,results", [
    ({"base": 2, "initial_delay": 1, "max_delay": None}, [1, 2, 4, 8, 16]),
    ({"base": 2, "initial_delay": 1, "max_delay": 8}, [1, 2, 4, 8, 8]),
])
async def test__retry__exponential_backoff(params: dict[str, Any], results: list[float]) -> None:
    backoff = backoffs.expo(**params)

    actual_results = [
        await backoff.__anext__()
        for _ in range(5)
    ]

    assert actual_results == results

    backoff = backoff.__aiter__()

    actual_results = [
        await backoff.__anext__()
        for _ in range(5)
    ]

    assert actual_results == results
