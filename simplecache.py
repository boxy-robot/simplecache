import time
import threading


_DEFAULT = object()  # differentiate between kwargs being passed explicitly as None


class Cache:
    def __init__(self, ttl=None, maxsize=None):
        if ttl and ttl < 0:
            raise ValueError("ttl must be greater than 0")

        if maxsize and maxsize < 0:
            raise ValueError("maxsize must be greater than 0")

        self.ttl = ttl or float('inf')
        self.maxsize = maxsize
        self.storage = {}
        self.lock = threading.Lock()

        # poor man's priority queue
        self.index = []  # (expires, key) pairs in desc order (popping is cheaper)

    def set(self, key, value, ttl=_DEFAULT):
        ttl = self.ttl if ttl is _DEFAULT else ttl
        ttl = float('inf') if ttl is None else ttl  # if None is passed as kwarg
        now = time.monotonic()
        expires = now + ttl

        # heap edgecase
        if key in self.storage:
            i = [node[1] for node in self.index].index(key)
            del self.index[i]
            del self.storage[key]

        with self.lock:
            self.storage[key] = (value, expires)
            self.index.append((expires, key))
            self.index.sort(reverse=True)  # put staler keys towards back

        self.prune()

    def get(self, key, default=_DEFAULT):
        self.prune()

        try:
            value, expires = self.storage[key]
        except KeyError:
            if default is _DEFAULT:
                raise
            return default

        return value

    def exists(self, key):
        self.prune()
        return key in self.storage

    def prune(self):
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
        with self.lock:
            self.storage = {}
            self.index = []

    def __iter__(self):
        self.prune()
        for _, key in self.index:
            value, expires = self.storage[key]
            yield key, value

