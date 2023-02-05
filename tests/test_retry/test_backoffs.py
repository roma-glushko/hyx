import random
from typing import Any

import pytest

from hyx.retry import backoffs


@pytest.mark.parametrize(
    "value",
    [
        0.5,
        1.0,
        2.0,
    ],
)
async def test__retry__const_backoff(value: float) -> None:
    backoff = backoffs.const(delay_secs=value)

    actual_results = [next(backoff) for _ in range(5)]

    for delay in actual_results:
        assert delay == value


@pytest.mark.parametrize(
    "interval,expected_sequence",
    [
        ((1.0, 2.0, 5.0, 10.0), [1.0, 2.0, 5.0, 10.0]),
        ((1.0, 2.0, 5.0), [1.0, 2.0, 5.0, 1.0, 2.0, 5.0, 1.0, 2.0, 5.0]),
    ],
)
async def test__retry__interval_backoff(interval: list[float], expected_sequence: list[float]) -> None:
    backoff = backoffs.interval(delay_secs=interval)

    actual_results = [next(backoff) for _ in range(len(expected_sequence))]

    assert actual_results == expected_sequence


@pytest.mark.parametrize(
    "params,results",
    [
        ({"base": 2, "min_delay_secs": 1, "max_delay_secs": None}, [1, 2, 4, 8, 16]),
        ({"base": 2, "min_delay_secs": 1, "max_delay_secs": 8}, [1, 2, 4, 8, 8]),
    ],
)
async def test__retry__exponential_backoff(params: dict[str, Any], results: list[float]) -> None:
    backoff = backoffs.expo(**params)

    actual_results = [next(backoff) for _ in range(5)]

    assert actual_results == results

    backoff = iter(backoff)

    actual_results = [next(backoff) for _ in range(5)]

    assert actual_results == results


@pytest.mark.parametrize(
    "args,expected_delays",
    [
        ({"min_delay_secs": 1.0, "additive_secs": 1.0, "max_delay_secs": None}, [1.0, 2.0, 3.0, 4.0]),
        ({"min_delay_secs": 1.0, "additive_secs": 4.0, "max_delay_secs": None}, [1.0, 5.0, 9.0, 13.0]),
        ({"min_delay_secs": 1.0, "additive_secs": 4.0, "max_delay_secs": 9.0}, [1.0, 5.0, 9.0, 9.0]),
    ],
)
async def test__retry__linear_backoff(args: dict[str, Any], expected_delays: list[str]) -> None:
    backoff = backoffs.linear(**args)

    actual_delays = [next(backoff) for _ in range(len(expected_delays))]

    assert actual_delays == expected_delays


@pytest.mark.parametrize(
    "args,expected_delays",
    [
        ({"min_delay_secs": 1.0, "factor_secs": 1.0, "max_delay_secs": None}, [1.0, 2.0, 3.0, 5.0, 8.0]),
        ({"min_delay_secs": 2.0, "factor_secs": 1.0, "max_delay_secs": None}, [2.0, 3.0, 5.0, 8.0, 13.0]),
        ({"min_delay_secs": 3.0, "factor_secs": 2.0, "max_delay_secs": 10.0}, [3.0, 5.0, 8.0, 10.0, 10.0]),
    ],
)
async def test__retry__fibonacci_backoff(args: dict[str, Any], expected_delays: list[str]) -> None:
    backoff = backoffs.fibo(**args)

    actual_delays = [next(backoff) for _ in range(len(expected_delays))]

    assert actual_delays == expected_delays


@pytest.mark.parametrize(
    "args,expected_delays",
    [
        ({"min_delay_secs": 1.0, "base": 2.0, "max_delay_secs": None}, [1.6394, 1.0570, 1.3064, 1.36, 2.2667]),
        ({"min_delay_secs": 2.0, "base": 10.0, "max_delay_secs": None}, [13.5097, 5.3289, 16.1058, 37.5036]),
    ],
)
async def test__retry__decorrexp_backoff(args: dict[str, Any], expected_delays: list[str]) -> None:
    random.seed(42)
    backoff = backoffs.decorrexp(**args)

    actual_delays = [next(backoff) for _ in range(len(expected_delays))]

    assert pytest.approx(actual_delays, rel=1e-4) == expected_delays


@pytest.mark.parametrize(
    "args,expected_delays",
    [
        ({"median_delay_secs": 10.0, "max_delay_secs": None}, [10.2537, 3.7838, 20.3690, 32.1965, 123.7448]),
        ({"median_delay_secs": 10.0, "max_delay_secs": 30.0}, [10.2537, 3.7838, 20.3690, 30.0, 30.0]),
    ],
)
async def test__retry__softexp_backoff(args: dict[str, Any], expected_delays: list[str]) -> None:
    random.seed(42)
    backoff = backoffs.softexp(**args)

    actual_delays = [next(backoff) for _ in range(len(expected_delays))]

    assert pytest.approx(actual_delays, rel=1e-4) == expected_delays
