import pytest

from hyx.bulkhead import bulkhead


async def test__bulkhead__validate__positive_nonzero_limits() -> None:
    with pytest.raises(ValueError):
        bulkhead(max_capacity=0, max_concurrency=2)

    with pytest.raises(ValueError):
        bulkhead(max_capacity=3, max_concurrency=0)

    with pytest.raises(ValueError):
        bulkhead(max_capacity=0, max_concurrency=0)

    with pytest.raises(ValueError):
        bulkhead(max_capacity=-1, max_concurrency=2)

    with pytest.raises(ValueError):
        bulkhead(max_capacity=3, max_concurrency=-1)


async def test__bulkhead__validate__capacity_is_greater_than_concurrency() -> None:
    with pytest.raises(ValueError):
        bulkhead(max_capacity=10, max_concurrency=100)
