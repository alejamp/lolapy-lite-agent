
import threading
import cachetools
from line_profiler import profile
from .cache_store import CacheStore


class MemoryCache(CacheStore):
    def __init__(self, key_prefix, memory_maxsize=1000):
        self.cache = cachetools.LRUCache(maxsize=memory_maxsize)

    @profile
    def get(self, key, callback=None):
        data = self.cache.get(key)
        if data is not None:
            return data
        
        if callback:
            data = callback()
            if data is not None:
                self.set(key, data)
                return data

        return None

    @profile
    def set(self, key, value):
        self.cache[key] = value

    @profile
    def delete(self, key):
        self.cache.pop(key, None)
    
    @profile
    def delete_redis(self, key):
        self.redis_client.delete(self.key_prefix + key)

    @profile
    def clear(self):
        self.cache.clear()

    @profile
    def clear_redis(self):
        # delete all keys with the prefix
        keys = self.redis_client.keys(self.key_prefix + '*')
        if keys:
            self.redis_client.delete(*keys)
        
    @profile
    def all(self):
        return self.cache.items()