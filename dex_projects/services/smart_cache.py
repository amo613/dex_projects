# services/smart_cache.py
import logging

logger = logging.getLogger("SmartCache")

class SmartCache:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self._cache = {}

    def add(self, key: str, value, priority: int = 0) -> None:
        if len(self._cache) >= self.max_size:
            first_key = next(iter(self._cache))
            logger.debug("Cache voll. Entferne: %s", first_key)
            del self._cache[first_key]
        self._cache[key] = value
        logger.debug("Cache hinzugefügt: %s -> %s", key, value)

    def get(self, key: str):
        return self._cache.get(key)

    def get_all(self):
        return self._cache.copy()
