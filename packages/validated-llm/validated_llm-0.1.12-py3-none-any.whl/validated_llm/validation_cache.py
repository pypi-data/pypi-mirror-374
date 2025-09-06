"""
Performance optimization through intelligent caching of validation results.

This module provides caching mechanisms to avoid redundant validation operations,
especially useful for expensive validations like JSON schema or complex regex patterns.
"""

import gc
import hashlib
import time
import weakref
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, Optional, Union

from .base_validator import ValidationResult


@dataclass
class CacheEntry:
    """Single cache entry with validation result and metadata."""

    result: ValidationResult
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0

    def mark_accessed(self) -> None:
        """Mark this entry as recently accessed."""
        self.access_count += 1
        self.last_access = time.time()

    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if entry is expired based on TTL."""
        return time.time() - self.timestamp > ttl_seconds

    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.timestamp


class ValidationCache:
    """High-performance cache for validation results with intelligent eviction."""

    def __init__(self, max_size: int = 10000, ttl_seconds: float = 3600.0, max_memory_mb: float = 100.0, cleanup_interval: int = 100):  # 1 hour default
        """Initialize validation cache.

        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time-to-live for entries in seconds
            max_memory_mb: Maximum memory usage in MB
            cleanup_interval: Cleanup every N operations
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.cleanup_interval = cleanup_interval

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._operation_count = 0
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "cleanups": 0, "memory_pressure_evictions": 0}

        # Weak reference to enable cleanup when cache is deleted
        self._self_ref = weakref.ref(self, self._cleanup_callback)

    @staticmethod
    def _cleanup_callback(cache_ref: weakref.ref) -> None:
        """Callback for cleanup when cache is deleted."""
        pass

    def _generate_cache_key(self, validator_id: str, input_data: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a deterministic cache key for validation inputs."""
        # Include validator configuration and context in key
        key_data = {"validator": validator_id, "input": input_data, "context": context or {}}

        # Create hash of the key data
        key_string = f"{validator_id}:{input_data}"
        if context:
            key_string += f":{hash(frozenset(context.items()))}"

        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()[:32]

    def _estimate_size(self, result: ValidationResult) -> int:
        """Estimate memory size of validation result in bytes."""
        size = 0

        # Size of error messages
        if result.errors:
            size += sum(len(str(error)) for error in result.errors) * 2  # UTF-8 approximation
        if result.warnings:
            size += sum(len(str(warning)) for warning in result.warnings) * 2

        # Size of metadata
        if result.metadata:
            size += len(str(result.metadata)) * 2

        # Base object overhead
        size += 200  # Approximate object overhead

        return size

    def _should_cleanup(self) -> bool:
        """Check if cleanup should be performed."""
        self._operation_count += 1
        return self._operation_count % self.cleanup_interval == 0 or len(self._cache) > self.max_size or self._get_memory_usage() > self.max_memory_bytes

    def _get_memory_usage(self) -> int:
        """Estimate current memory usage of cache."""
        return sum(entry.size_bytes for entry in self._cache.values())

    def _cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        expired_keys = []
        current_time = time.time()

        for key, entry in self._cache.items():
            if current_time - entry.timestamp > self.ttl_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def _evict_lru_entries(self, target_count: int) -> int:
        """Evict least recently used entries."""
        if len(self._cache) <= target_count:
            return 0

        # Sort by last access time (oldest first)
        sorted_entries = sorted(self._cache.items(), key=lambda x: x[1].last_access)

        evicted = 0
        for key, _ in sorted_entries:
            if len(self._cache) <= target_count:
                break
            del self._cache[key]
            evicted += 1

        return evicted

    def _smart_eviction(self) -> int:
        """Perform intelligent cache eviction based on usage patterns."""
        evicted = 0

        # First, remove expired entries
        evicted += self._cleanup_expired()

        # If still over limit, use LRU eviction
        if len(self._cache) > self.max_size:
            target_size = int(self.max_size * 0.8)  # Clean to 80% capacity
            evicted += self._evict_lru_entries(target_size)

        # If memory pressure, evict based on size/access ratio
        if self._get_memory_usage() > self.max_memory_bytes:
            memory_evicted = self._evict_by_memory_efficiency()
            evicted += memory_evicted
            self._stats["memory_pressure_evictions"] += memory_evicted

        return evicted

    def _evict_by_memory_efficiency(self) -> int:
        """Evict entries with poor memory efficiency (large size, low access)."""
        entries_with_efficiency = []

        for key, entry in self._cache.items():
            # Calculate efficiency: access_count per byte
            efficiency = entry.access_count / max(entry.size_bytes, 1)
            entries_with_efficiency.append((key, entry, efficiency))

        # Sort by efficiency (least efficient first)
        entries_with_efficiency.sort(key=lambda x: x[2])

        evicted = 0
        target_memory = int(self.max_memory_bytes * 0.8)  # Clean to 80% memory

        for key, entry, efficiency in entries_with_efficiency:
            if self._get_memory_usage() <= target_memory:
                break
            del self._cache[key]
            evicted += 1

        return evicted

    def get(self, validator_id: str, input_data: str, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationResult]:
        """Retrieve cached validation result."""
        with self._lock:
            cache_key = self._generate_cache_key(validator_id, input_data, context)

            if cache_key not in self._cache:
                self._stats["misses"] += 1
                return None

            entry = self._cache[cache_key]

            # Check if expired
            if entry.is_expired(self.ttl_seconds):
                del self._cache[cache_key]
                self._stats["misses"] += 1
                return None

            # Mark as accessed and update stats
            entry.mark_accessed()
            self._stats["hits"] += 1

            return entry.result

    def put(self, validator_id: str, input_data: str, result: ValidationResult, context: Optional[Dict[str, Any]] = None) -> None:
        """Store validation result in cache."""
        with self._lock:
            cache_key = self._generate_cache_key(validator_id, input_data, context)

            # Estimate size of result
            size_bytes = self._estimate_size(result)

            # Create cache entry
            entry = CacheEntry(result=result, timestamp=time.time(), size_bytes=size_bytes)

            self._cache[cache_key] = entry

            # Perform cleanup if needed
            if self._should_cleanup():
                evicted = self._smart_eviction()
                self._stats["evictions"] += evicted
                self._stats["cleanups"] += 1

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats = {key: 0 for key in self._stats}

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_mb": self._get_memory_usage() / (1024 * 1024),
                "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                "hit_rate": hit_rate,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "cleanups": self._stats["cleanups"],
                "memory_pressure_evictions": self._stats["memory_pressure_evictions"],
                "avg_entry_size_bytes": self._get_memory_usage() / len(self._cache) if self._cache else 0,
            }

    def get_efficiency_report(self) -> Dict[str, Any]:
        """Get detailed cache efficiency analysis."""
        with self._lock:
            if not self._cache:
                return {"status": "empty_cache"}

            ages = [entry.age_seconds() for entry in self._cache.values()]
            access_counts = [entry.access_count for entry in self._cache.values()]
            sizes = [entry.size_bytes for entry in self._cache.values()]

            return {
                "entry_count": len(self._cache),
                "avg_age_seconds": sum(ages) / len(ages),
                "max_age_seconds": max(ages),
                "avg_access_count": sum(access_counts) / len(access_counts),
                "max_access_count": max(access_counts),
                "avg_size_bytes": sum(sizes) / len(sizes),
                "max_size_bytes": max(sizes),
                "total_memory_mb": sum(sizes) / (1024 * 1024),
            }


# Global cache instance for shared use
_global_cache: Optional[ValidationCache] = None


def get_global_cache() -> ValidationCache:
    """Get or create the global validation cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ValidationCache()
    return _global_cache


def configure_global_cache(max_size: int = 10000, ttl_seconds: float = 3600.0, max_memory_mb: float = 100.0, cleanup_interval: int = 100) -> ValidationCache:
    """Configure the global validation cache with custom settings."""
    global _global_cache
    _global_cache = ValidationCache(max_size=max_size, ttl_seconds=ttl_seconds, max_memory_mb=max_memory_mb, cleanup_interval=cleanup_interval)
    return _global_cache


def clear_global_cache() -> None:
    """Clear the global validation cache."""
    global _global_cache
    if _global_cache:
        _global_cache.clear()


def get_global_cache_stats() -> Dict[str, Any]:
    """Get statistics for the global validation cache."""
    return get_global_cache().get_stats()
