import random

import pytest as pytest

from hyx.retry import jitters


@pytest.mark.parametrize(
    "delay,expected_delays",
    [
        (10.0, [6.3943, 0.2501, 2.7503, 2.2321, 7.3647]),
    ],
)
async def test__jitters__full(delay: float, expected_delays: list[str]) -> None:
    random.seed(42)

    actual_delays = [jitters.full(delay) for _ in range(len(expected_delays))]

    assert pytest.approx(actual_delays, rel=1e-4) == expected_delays


@pytest.mark.parametrize(
    "delay,expected_delays",
    [
        (15.0, [12.2957, 7.6876, 9.5627, 9.1741, 13.0235]),
    ],
)
async def test__jitters__equal(delay: float, expected_delays: list[str]) -> None:
    random.seed(42)

    actual_delays = [jitters.equal(delay) for _ in range(len(expected_delays))]

    assert pytest.approx(actual_delays, rel=1e-4) == expected_delays
