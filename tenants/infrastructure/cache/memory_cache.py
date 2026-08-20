# core/tenants/infrastructure/cache/memory_cache.py

class TenantCache:
    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value, ttl=None):
        self._cache[key] = value

    def delete(self, key):
        self._cache.pop(key, None)