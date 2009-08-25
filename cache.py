"""
Small functional cache.
"""


def cached(func):
    """
    Cache the output of the function invocation.

    >>> @cached
    ... def cap(s): return s.upper()
    >>> cap('a')
    'A'
    >>> cap('b')
    'B'

    Show cache contents:

    >>> cap.cache()
    {('a',): 'A', ('b',): 'B'}

    Clear the cache:
    
    >>> cap.clear()
    >>> cap.cache()
    {}

    Due to the caching, we can not take key-value arguments:

    >>> cap(s='a')     # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: wrapper() got an unexpected keyword argument 's'
    """
    func._cache = {}

    def wrapper(*args):
        cache = func._cache
        try:
            return cache[args]
        except KeyError:
            result = func(*args)
            cache[args] = result
            return result

    def cache():
        return func._cache
    wrapper.cache = cache
    def clear():
        func._cache.clear()
    wrapper.clear = clear
    return wrapper


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim: sw=4:et:ai
