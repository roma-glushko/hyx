import sys
import time
from collections import OrderedDict
from typing import Any, Optional


def _now() -> float:
    return time.monotonic()


class CacheItem:
    """
    Cache Item
    """

    __slots__ = ("_key", "_value", "_next", "_prev")

    def __init__(
        self,
        key: Any = None,
        value: Any = None,
        next_: Optional["CacheItem"] = None,
        prev_: Optional["CacheItem"] = None,
    ) -> None:
        self._key = key
        self._value = value

        self._next = next_
        self._prev = prev_

    @classmethod
    def root(cls) -> "CacheItem":
        root_item = cls()

        root_item.next = root_item
        root_item.prev = root_item

        return root_item

    @property
    def key(self) -> Any:
        return self._key

    @property
    def value(self) -> Any:
        return self._value

    @property
    def next(self) -> "CacheItem":
        return self._next

    @next.setter
    def next(self, next_: Optional["CacheItem"]) -> None:
        self._next = next_

    @property
    def prev(self) -> "CacheItem":
        return self._prev

    @prev.setter
    def prev(self, prev_: Optional["CacheItem"]) -> None:
        self._prev = prev_

    def link(self, prev_: "CacheItem", next_: "CacheItem") -> None:
        """
        Insert the current item between prev and next items
        prev_ -> self -> next_
        """
        self.next = next_
        self.prev = prev_

        prev_.next = self
        next_.prev = self

    def unlink(self) -> None:
        next_item = self.next
        prev_item = self.prev

        prev_item.next = next_item
        next_item.prev = prev_item

    def __repr__(self):
        return "%s(key=%r, value=%r)" % (
            self.__class__.__name__,
            self._key,
            self._value,
        )


class LRUCache:
    """
    Cache with key's TTL and fixed storage size.
    If the storage size has exceeded, it removes least recently used (LRU) keys to clean some space for a new items.
    """

    __slots__ = ("_max_size", "_data", "_ttl_secs", "_ttls_root")

    class Item(CacheItem):
        """
        Cache Item
        """

        __slots__ = ("_expire_at",)

        def __init__(
            self,
            key: Any = None,
            value: Any = None,
            lifetime_secs: Optional[float] = None,
            next_: Optional["CacheItem"] = None,
            prev_: Optional["CacheItem"] = None,
        ) -> None:
            super().__init__(key, value, next_, prev_)

            self._expire_at = None

            if lifetime_secs is not None:
                self._expire_at = _now() + lifetime_secs

        @property
        def expire_at(self) -> float:
            return self._expire_at

        @property
        def expired(self) -> bool:
            return self._expire_at is not None and _now() >= self._expire_at

        def __repr__(self):
            return "%s(key=%r, value=%r, expire_at=%r)" % (
                self.__class__.__name__,
                self._key,
                self._value,
                self.expire_at,
            )

    def __init__(self, max_size: int = 1000, ttl_secs: Optional[float] = None) -> None:
        self._max_size = max_size
        self._data: OrderedDict[Any, LRUCache.Item] = OrderedDict()

        self._ttl_secs = ttl_secs
        self._ttls_root = LRUCache.Item.root()

    def __repr__(self):
        return "%s(maxsize=%r, currsize=%r)" % (
            self.__class__.__name__,
            self._max_size,
            len(self._data),
        )

    def __contains__(self, key: Any) -> Any:
        try:
            item = self._data[key]
        except KeyError:
            return False

        if item.expired:
            # expired items should not be found
            del self[key]
            return False

        return True

    def __getitem__(self, key: Any) -> Any:
        if key in self:
            return self._data[key].value

        raise KeyError

    def __setitem__(self, key: Any, value: Any, ttl_secs: Optional[float] = None) -> None:
        if len(self._data) >= self._max_size:
            self._evict()

        new_item = LRUCache.Item(key=key, value=value, lifetime_secs=ttl_secs or self._ttl_secs)

        self._data[key] = new_item

        self._data.move_to_end(key)
        self._add_ttl_item(new_item)

    def __delitem__(self, key: Any) -> None:
        try:
            item = self._data[key]

            item.unlink()
            del self._data[key]
        except KeyError:
            # Ignore missing keys
            return

    def __iter__(self) -> tuple[Any, Any]:
        for key, item in self._data.items():
            if item.expired:
                del self[key]
                continue

            yield key, item.value

    def __len__(self) -> int:
        self._evict_by_ttl()

        return len(self._data)

    def __sizeof__(self) -> int:
        sizeof = sys.getsizeof
        items = len(self)

        size = sizeof(self._ttl_secs) + sizeof(self._max_size)
        size += sizeof(self._ttls_root) * (items + 1)  # plus the root item
        size += sizeof(self._data)

        return size

    def set(self, key: Any, value: Any, ttl_secs: Optional[float] = None) -> None:
        self.__setitem__(key, value, ttl_secs=ttl_secs)

    def _add_ttl_item(self, new_item) -> None:
        root_item = self._ttls_root
        curr_item = root_item.next

        while curr_item is not root_item and (
            curr_item.expire_at is not None and new_item.expire_at > curr_item.expire_at
        ):
            # find a place to insert a new item
            curr_item = curr_item.next

        new_item.link(curr_item.prev, curr_item)

    def _evict_by_ttl(self) -> int:
        """
        Evict cache items based on their TTL.
        If TTL is None, the item is not going to be expired as time goes on.
        """
        evicted_keys: int = 0

        # TTL items should be evicted first
        root_item = self._ttls_root
        curr_item = root_item.next

        while curr_item is not root_item and curr_item.expired:
            evicted_item = curr_item
            curr_item = curr_item.next

            del self[evicted_item.key]

            evicted_keys += 1

        return evicted_keys

    def _evict(self) -> None:
        """
        Evict cache items based on their TTL and least recent usage
        """
        if self._evict_by_ttl():
            # we have cleaned at least one slot for the new item
            return

        # TTL has not cleared any slots, needs to find least recently used item
        _, item = self._data.popitem(last=False)
        item.unlink()
