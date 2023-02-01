simplecache
========

A simple in-memory cache python library that supports TTLs.

Basic usage:

    import simplecache
    cache = simplecache.Cache(ttl=60)
    cache.set('foo', 'bar')
    cache.get('foo')  # bar

Expiration of keys:
    cache = simplecache.Cache(ttl=1)
    cache.set('foo', 'bar')
    time.sleep(1)
    cache.get('foo')  # KeyError: 'foo'

Per-key TTL:
    cache = simplecache.Cache(ttl=60)
    cache.set('foo', 'bar', ttl=300)

Default return values:
    cache = simplecache.Cache(ttl=60)
    cache.get('foo', 'default')

Max size:
    cache = simplecache.Cache(maxsize=3)
    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    cache.set('d', 4)
    cache  # {'b': 2, 'c': 3, 'd': 4}

A more real world example:

    import logging
    import requests
    import simplecache

    cache = simplecache.Cache(ttl=60)

    def get_cat_facts():
        try:
            data = cache.get('cat-facts')
        except KeyError:
            logging.info("fetching cat facts...")
            data = requests.get('https://cat-fact.herokuapp.com/facts').json()
            cache.set('cat-facts', data)

        return data

    def main():
        get_cat_facts()  # call repeatedly


Features
--------

- Time to live
- Max size


Installation
------------

Install by running:

    pip install git+https://github.com/boxy-robot/simplecache.git


Testing
-------

To run the test suite:

    docker compose run test

To run it interactively:

    docker compose run test bash
    pytest -s



License
-------

The project is licensed under the MIT license.
