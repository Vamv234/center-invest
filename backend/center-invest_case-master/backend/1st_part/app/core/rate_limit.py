import time
from threading import Lock


class RateLimiter:
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self._lock = Lock()
        self._buckets: dict[str, tuple[int, float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            count, start = self._buckets.get(key, (0, now))
            if now - start >= 60:
                self._buckets[key] = (1, now)
                return True
            if count >= self.limit:
                return False
            self._buckets[key] = (count + 1, start)
            return True
