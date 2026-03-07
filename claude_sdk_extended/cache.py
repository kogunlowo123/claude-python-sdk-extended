"""Response caching for Claude API calls."""

from typing import Any, Dict, Optional
import hashlib
import json
import time


class ResponseCache:
    """Cache Claude API responses to reduce costs and latency."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _make_key(self, messages: Any, model: str, **kwargs) -> str:
        """Generate a cache key from request parameters."""
        key_data = json.dumps({"messages": messages, "model": model, **kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, messages: Any, model: str, **kwargs) -> Optional[Any]:
        """Get a cached response if available and not expired."""
        key = self._make_key(messages, model, **kwargs)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                self._hits += 1
                return entry["response"]
            else:
                del self._cache[key]
        self._misses += 1
        return None

    def set(self, messages: Any, model: str, response: Any, **kwargs) -> None:
        """Cache a response."""
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
        key = self._make_key(messages, model, **kwargs)
        self._cache[key] = {"response": response, "timestamp": time.time()}

    @property
    def hit_rate(self) -> float:
        """Get the cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
