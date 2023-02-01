simplecache
========

A simple in-memory cache python library that supports TTLs.

Basic usage:

    import simplecache
    cache = simplecache.Cache(ttl=5 * 60)
    cache.set('foo', 'bar')
    cache.get('foo')  # bar

A more real world example:

    import requests
    import simplecache
    cache = simplecache.Cache(ttl=5 * 60)
    data = requests.get('https://cat-fact.herokuapp.com/facts').json()
    cache.set('facts', data, ttl=10)
    ...
    cache.get('facts')


Features
--------

- Time to live
- Max size
- That's it

<!--
Installation
------------

Install by running:

    pip install simplecache
-->


Contribute
----------

- Issue Tracker: github.com/$project/$project/issues
- Source Code: github.com/$project/$project

Testing
-------

To run the test suite:

    docker compose run test

To run it interactively:

    docker compose run test bash
    pytest -s


Support
-------

If you are having issues, please open a github issue at: <insert here>.


License
-------

The project is licensed under the MIT license.
