import sys
from collections import OrderedDict
from typing import Final

from hyx.cache import LRUCache

MAX_SIZE: Final[int] = 1_000_000

# Key and Value are 28b
# 10 - X MiB
# 100 - 0.012 MiB (0.000 MiB)
# 200 - X MiB (0.000 MiB)
# 500 - 0.047 MiB (0.020 MiB)
# 10_000 - 1.684 MiB (0.016 MiB)
# 100_000 - 19.719 MiB (9.352 MiB, 15.566 MiB)
# 200_000 - 43.473 MiB (19.375 MiB, 31.746 MiB)
# 500_000 - 104.777 MiB (38.320 MiB, 70.387 MiB)
# 1_000_000 - 213.629 MiB (79.402 MiB, 141.383 MiB)
# Overhead: ~(140b + 2 * K_SIZE + V_SIZE) per item

plain_dict = {}
ordered_dict = OrderedDict()

cache = LRUCache(max_size=MAX_SIZE)
sample_cache_item = LRUCache.Item(key=MAX_SIZE, value=MAX_SIZE)

print(f"Key and Value Size: {sys.getsizeof(MAX_SIZE)}b")
print(f"Dict Size: {sys.getsizeof({0: MAX_SIZE})}b")
print(f"LRUCache.Item Size: {sys.getsizeof(sample_cache_item)}b")


def create_dict_reference() -> None:
    for idx in range(MAX_SIZE):
        plain_dict[idx] = idx


def create_ord_dict_reference() -> None:
    for idx in range(MAX_SIZE):
        ordered_dict[idx] = idx


# @profile
def stress_lru_cache() -> None:
    for idx in range(MAX_SIZE):
        cache[idx] = idx


if __name__ == "__main__":
    # create_dict_reference()
    # create_ord_dict_reference()
    stress_lru_cache()
    print(f"LRUCache Size: {sys.getsizeof(cache)}b")
