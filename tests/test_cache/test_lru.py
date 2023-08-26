import asyncio

from hyx.cache import LRUCache


async def test__cache_lru__as_map() -> None:
    cache = LRUCache(max_size=2, ttl_secs=None)

    cache["1"] = [1, 2, 3]

    assert "1" in cache
    assert len(cache) == 1
    assert cache["1"] == [1, 2, 3]

    cache["1"] = 1

    assert cache["1"] == 1

    del cache["1"]
    assert "1" not in cache
    assert len(cache) == 0


async def test__cache_lru__no_ttl_eviction() -> None:
    cache = LRUCache(max_size=2, ttl_secs=None)

    cache["1"] = 1
    cache["2"] = 2

    assert len(cache) == 2
    assert "1" in cache
    assert "2" in cache

    cache["3"] = 3

    assert len(cache) == 2
    assert "1" not in cache
    assert "3" in cache
    assert "3" in cache


async def test__cache_lru__iteration() -> None:
    cache = LRUCache(max_size=2, ttl_secs=None)

    cache["1"] = 1
    cache["2"] = 2

    assert [("1", 1), ("2", 2)] == list(cache)


async def test__cache_lru__instance_level_ttl_eviction() -> None:
    cache = LRUCache(max_size=3, ttl_secs=0.01)

    cache["1"] = 1
    cache["2"] = 2

    assert len(cache) == 2

    await asyncio.sleep(0.02)

    assert len(cache) == 0
    assert "1" not in cache
    assert "2" not in cache


async def test__cache_lru__mixed_ttl_eviction() -> None:
    cache = LRUCache(max_size=4, ttl_secs=0.01)

    cache["1"] = 1
    cache["2"] = 2
    cache.set("3", 3, ttl_secs=0.03)
    cache.set("4", 4, ttl_secs=0.04)

    assert len(cache) == 4

    await asyncio.sleep(0.02)

    assert len(cache) == 2
    assert "1" not in cache
    assert "2" not in cache

    await asyncio.sleep(0.010)
    assert len(cache) == 1
    assert "3" not in cache

    await asyncio.sleep(0.010)
    assert len(cache) == 0
    assert "4" not in cache


async def test__cache_lru__ttl_eviction_on_iter() -> None:
    cache = LRUCache(max_size=2, ttl_secs=0.01)

    cache["1"] = 1
    cache["2"] = 2

    assert len(cache) == 2
    assert list(cache) == [("1", 1), ("2", 2)]

    await asyncio.sleep(0.02)

    assert list(cache) == []


async def test__cache_lru__ttl_size_eviction() -> None:
    cache = LRUCache(max_size=2, ttl_secs=0.01)

    cache["1"] = 1
    cache["2"] = 2

    assert len(cache) == 2
    assert "1" in cache
    assert "2" in cache

    cache["3"] = 3

    assert len(cache) == 2
    assert "1" not in cache
    assert "2" in cache
    assert "3" in cache
