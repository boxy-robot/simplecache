import time

import simplecache

import pytest


class TestBasics:
    """Test core functionality."""

    def test_set(self):
        cache = simplecache.Cache()
        cache.set('pin', 1077)

        v, expires = cache.storage['pin']
        assert v == 1077

    def test_get(self):
        cache = simplecache.Cache()
        cache.set('pin', 1077)

        v = cache.get('pin')
        assert v == 1077

        v = cache.get('balance', 0.93)
        assert v == 0.93

    def test_expiration(self):
        cache = simplecache.Cache()
        cache.set('pin', 1077, ttl=.1)

        time.sleep(.1)
        with pytest.raises(KeyError, match=r"pin"):
            v = cache.get('pin')

    def test_exists(self):
        cache = simplecache.Cache()
        cache.set('pin', 1077)
        assert cache.exists('pin')
        assert not cache.exists('balance')

    def test_clear(self):
        cache = simplecache.Cache()
        cache.set('pin', 1077)
        cache.clear()
        assert len(cache.storage) == 0

    def test_iter(self):
        cache = simplecache.Cache()
        cache.set('captain', 'leela')
        cache.set('delivery-boy', 'fry')
        cache.set('cook', 'bender')

        d = dict(cache)
        assert d == {'captain': 'leela', 'delivery-boy': 'fry', 'cook': 'bender'}


class TestConstructor:
    def test_bad_ttl(self):
        with pytest.raises(ValueError, match=r"ttl must be greater than 0"):
            cache = simplecache.Cache(ttl=-1)

    def test_bad_maxsize(self):
        with pytest.raises(ValueError, match=r"maxsize must be greater than 0"):
            cache = simplecache.Cache(maxsize=-1)


class TestExpiration:
    def test_default_ttl(self):
        cache = simplecache.Cache(ttl=.1)
        cache.set('pin', 1077)
        v = cache.get('pin')
        assert v == 1077
        time.sleep(.1)
        with pytest.raises(KeyError, match=r"pin"):
            cache.get('pin')

        # make sure storage objects get cleared
        assert not cache.storage
        assert not cache.heap

    def test_per_key_ttl(self):
        cache = simplecache.Cache(ttl=.1)
        cache.set('pin', 1077, ttl=.2)  # set ttl explicitly

        time.sleep(.1)
        v = cache.get('pin')
        assert v == 1077

        time.sleep(.2)
        with pytest.raises(KeyError, match=r"pin"):
            cache.get('pin')

    def test_per_key_none(self):
        cache = simplecache.Cache(ttl=.1)
        cache.set('pin', 1077, ttl=None)
        time.sleep(.2)
        v = cache.get('pin')
        assert v == 1077

    def test_sorting(self):
        cache = simplecache.Cache(ttl=1)
        cache.set('captain', 'leela')
        cache.set('delivery-boy', 'fry')
        cache.set('pin', 1077, ttl=.1)  # insert in middle
        cache.set('cook', 'bender')
        time.sleep(.1)

        with pytest.raises(KeyError, match=r"pin"):
            cache.get('pin')

        assert cache.get('captain') == 'leela'


class TestMaxSize:
    def test_eviction(self):
        cache = simplecache.Cache(maxsize=1, ttl=1)
        cache.set('captain', 'leela')
        cache.set('delivery-boy', 'fry')
        cache.set('cook', 'bender')

        # most stale entry should get evicted first
        with pytest.raises(KeyError, match=r"captain"):
            cache.get('captain')
        with pytest.raises(KeyError, match=r"delivery-boy"):
            cache.get('delivery-boy')

        assert cache.get('cook') == 'bender'


class TestSetKeyAgain:
    def test_set_twice(self):
        cache = simplecache.Cache(ttl=60)
        cache.set('pin', 1077)
        cache.set('pin', 1077)
        assert len(cache.storage) == 1
        assert len(cache.heap) == 1

