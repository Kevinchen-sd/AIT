from functools import lru_cache
def cached(maxsize: int = 32):
    return lru_cache(maxsize=maxsize)
