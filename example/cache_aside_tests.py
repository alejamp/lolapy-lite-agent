import sys
import os
import time
from dotenv import dotenv_values     

from lolapy.assistant.stores import MemRedisCacheAside



config = {
    **dotenv_values("example/.env"),    # load development variables
    **os.environ,               # override loaded values with environment variables
}


def mock_db_query(i):
    time.sleep(0.250)
    return str(i)


if __name__ == "__main__":
    # Probar las funciones

    # Local
    # cache = MemRedisCacheAside('redis://localhost:6379/0', 'lola:cguru:push:')
    # Remote 
    cache = MemRedisCacheAside(config['REDIS_URL'], 'lola:cguru:push:')


    count = 20

    #---------------------------------------------------------------------------
    # test multiple sets with wait for redis
    print("Testing multiple sets, set_wait_for_redis(True)")
    cache.set_wait_for_redis(True)
    start = time.time()
    for i in range(count):
        cache.set(str(i), str(i))

    end = time.time()
    print(f"Time spent setting {count} keys: {end - start}")
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # test multiple sets with redis aside
    print("Testing multiple sets, set_wait_for_redis(False)")
    cache.set_wait_for_redis(False)
    start = time.time()
    for i in range(count):
        cache.set(str(i), str(i))

    end = time.time()
    print(f"Time spent setting {count} keys: {end - start}")
    #---------------------------------------------------------------------------  
      
    #---------------------------------------------------------------------------  
    print("Testing multiple gets with cache hits")
    start = time.time()
    for i in range(count):
        cache.get(str(i))

    end = time.time()
    print(f"Time spent getting {count} keys with cache hits: {end - start}")
    #---------------------------------------------------------------------------  

    #---------------------------------------------------------------------------      
    print("Testing multiple gets with cache misses")
    start = time.time()
    for i in range(count):
        cache.get(str(i + count))

    end = time.time()
    print(f"Time spent getting {count} keys with cache misses: {end - start}")
    #---------------------------------------------------------------------------  


    #---------------------------------------------------------------------------      
    print("Test clearing in-memory cache")
    cache.clear()

    print("Testing multiple gets with cache misses")
    start = time.time()
    for i in range(count):
        v = cache.get(str(i))
        if v is None:
            print(f"Cache miss for key: {i}")

    end = time.time()
    print(f"Time spent getting {count} keys with memory cache misses: {end - start}")
    #---------------------------------------------------------------------------  

    #---------------------------------------------------------------------------  
    print("Test clear cache, memory and redis")
    cache.clear()
    print("Cache Memory Cleared")
    cache.clear_redis()
    print("Cache Redis Cleared")

    print("Testing multiple gets with cache misses")
    start = time.time()
    for i in range(count):
        v = cache.get(str(i), callback=lambda: mock_db_query(i))
        print(f"Got key: {i} -> value: {v}")

    end = time.time()
    print(f"Time spent getting {count} keys with cache misses: {end - start}")
    #---------------------------------------------------------------------------  

    #---------------------------------------------------------------------------  
    print("Testing multiple gets with cache hits")
    start = time.time()
    for i in range(count):
        v = cache.get(str(i))

    end = time.time()
    print(f"Time spent getting {count} keys with cache hits: {end - start}")
    #---------------------------------------------------------------------------  