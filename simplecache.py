"""An in-memory cache supporting a TTL and max size.

The TTL can be set at the object level or per key.

Example:

    import simplecache
    cache = simplecache.Cache(ttl=60)  # in seconds
    cache.set('foo', 1)
    cache.get('foo')  # 1

    # Per key ttl
    cache.set('bar', 2, expires=300)

    # Don't expire
    cache.set('baz', 3, expires=None)

    # Exired keys
    time.sleep(60)
    cache.get('foo')  # KeyError

    # Default return values
    cache.get('foo', 1)

    # Max Size
    cache = simplecache.Cache(maxsize=3)
    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    cache.set('d', 4)
    cache  # {'b': 2, 'c': 3, 'd': 4}
"""
import time
import threading


_DEFAULT = object()  # differentiate between kwargs being passed explicitly as None


class Cache:
    """In-memory cache supporting a TTL and max size."""

    def __init__(self, ttl=None, maxsize=None):
        """
        Args:
            ttl (float, optional): Time to keep values cached (in seconds). If
                None, values will be cached indefinitely.
            maxsize (int, optional): Max number of entries to allow into cache.
                If None, cache can grow indefinitely.
        """
        if ttl and ttl < 0:
            raise ValueError("ttl must be greater than 0")

        if maxsize and maxsize < 0:
            raise ValueError("maxsize must be greater than 0")

        self.ttl = ttl or float('inf')
        self.maxsize = maxsize
        self.storage = {}  # {key: (value, timestamp)}
        self.lock = threading.Lock()

        # poor man's heap
        self.index = []  # (expires, key) pairs in desc order (popping is cheaper)

    def set(self, key, value, ttl=_DEFAULT):
        """Add a value to the cache.

        Args:
            key (str): Key to store the value under.
            value (any): Value to cache.
            ttl (float, optional): Seconds to cache the value.
        """
        ttl = self.ttl if ttl is _DEFAULT else ttl
        ttl = float('inf') if ttl is None else ttl  # if None is passed as kwarg
        now = time.monotonic()
        expires = now + ttl

        with self.lock:
            # prevent duplicates in heap
            if key in self.storage:
                i = [node[1] for node in self.index].index(key)  # not great for large lists
                del self.index[i]
                del self.storage[key]

            self.storage[key] = (value, expires)
            self.index.append((expires, key))
            self.index.sort(reverse=True)  # put staler keys towards back

        self.prune()

    def get(self, key, default=_DEFAULT):
        """Retrieve a value from the cache.

        Args:
            key (str): Key of the value to retrieve.
            default (any, optional): Value to return instead if the key isn't
                found or is expired.

        Returns:
            any: The cached value for the given key.
        """
        self.prune()

        try:
            value, expires = self.storage[key]
        except KeyError:
            if default is _DEFAULT:
                raise
            return default

        return value

    def exists(self, key):
        """Return whether the given key exists.

        Args:
            key (str): Key of the cached value to check.

        Returns:
            bool: Whether the key is in the cache.
        """
        self.prune()
        return key in self.storage

    def prune(self):
        """Remove stale items from the cache."""
        now = time.monotonic()
        while self.index:
            expires, key = self.index[-1]
            expired = now > expires
            maxsize = self.maxsize or float('inf')
            oversized = len(self.storage) > maxsize
            if expired or oversized:
                with self.lock:
                    del self.storage[key]
                    self.index.pop()
            else:
                break

    def clear(self):
        """Empty the cache."""
        with self.lock:
            self.storage = {}
            self.index = []

    def __iter__(self):
        self.prune()
        for _, key in self.index:
            value, expires = self.storage[key]
            yield key, value

    def __repr__(self):
        if len(self.storage) <= 3:
            return str({k: v[0] for k, v in self.storage.items()})

        else:
            sample = {}
            for i in range(3):
                k = self.index[i][1]  # (timestamp, key)
                sample[k] = self.storage[k][0]
            return str(sample).rstrip('}') + ', ...}'
