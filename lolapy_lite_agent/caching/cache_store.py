

class CacheStore:
    def get(self, key, callback=None):
        raise NotImplementedError()

    def set(self, key, value):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()
    
    def clear(self):
        raise NotImplementedError()
    
    def all(self):
        raise NotImplementedError()
