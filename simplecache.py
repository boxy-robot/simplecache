import heapq
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
        self.heap = []  # (expires, key)
        self.lock = threading.Lock()

    def set(self, key, value, ttl=_DEFAULT):
        ttl = self.ttl if ttl is _DEFAULT else ttl
        ttl = float('inf') if ttl is None else ttl  # if None is passed as kwarg
        now = time.monotonic()
        expires = now + ttl

        # prevent duplicates in heap
        with self.lock:
            if key in self.storage:
                # find the index for key in the heap
                i = [node[1] for node in self.heap].index(key)
                del self.heap[i]
                heapq.heapify(self.heap)
                del self.storage[key]

            self.storage[key] = (value, expires)
            heapitem = (expires, key)
            heapq.heappush(self.heap, heapitem)

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
        while self.heap:
            expires, key = self.heap[0]
            expired = now > expires
            maxsize = self.maxsize or float('inf')
            oversized = len(self.storage) > maxsize
            if expired or oversized:
                with self.lock:
                    del self.storage[key]
                    heapq.heappop(self.heap)
            else:
                break

    def clear(self):
        with self.lock:
            self.storage = {}
            self.heap = []

    def __iter__(self):
        self.prune()
        for _, key in self.heap:
            value, expires = self.storage[key]
            yield key, value

