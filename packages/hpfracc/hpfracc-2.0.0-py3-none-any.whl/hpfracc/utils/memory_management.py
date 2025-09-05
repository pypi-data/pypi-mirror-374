"""
Memory management and optimization tools for fractional calculus computations.

This module provides tools for:
- Monitoring memory usage
- Caching frequently used computations
- Optimizing memory allocation
- Managing large-scale computations
"""

import numpy as np
import gc
import psutil
import time
from typing import Any, Callable, Dict, Optional
from functools import wraps


class MemoryManager:
    """Manager for monitoring and optimizing memory usage."""

    def __init__(self, memory_limit_gb: Optional[float] = None):
        """
        Initialize the memory manager.

        Args:
            memory_limit_gb: Memory limit in GB (optional)
        """
        self.memory_limit_gb = memory_limit_gb
        self.memory_history = []
        self.peak_memory = 0.0

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage information.

        Returns:
            Dictionary with memory usage information in GB
        """
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss": memory_info.rss / (1024**3),  # Resident Set Size in GB
            "vms": memory_info.vms / (1024**3),  # Virtual Memory Size in GB
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available / (1024**3),
            "total": psutil.virtual_memory().total / (1024**3),
        }

    def record_memory_usage(self) -> Dict[str, float]:
        """
        Record current memory usage and update history.

        Returns:
            Current memory usage information
        """
        usage = self.get_memory_usage()
        self.memory_history.append({"timestamp": time.time(), "usage": usage})

        # Update peak memory
        if usage["rss"] > self.peak_memory:
            self.peak_memory = usage["rss"]

        return usage

    def check_memory_limit(self) -> bool:
        """
        Check if current memory usage exceeds the limit.

        Returns:
            True if within limit, False if exceeded
        """
        if self.memory_limit_gb is None:
            return True

        current_usage = self.get_memory_usage()
        return current_usage["rss"] <= self.memory_limit_gb

    def force_garbage_collection(self) -> None:
        """Force garbage collection to free memory."""
        gc.collect()

    def optimize_memory_usage(self) -> Dict[str, float]:
        """
        Perform memory optimization.

        Returns:
            Memory usage before and after optimization
        """
        before = self.get_memory_usage()

        # Force garbage collection
        self.force_garbage_collection()

        # Clear numpy cache if available
        try:
            np.core._multiarray_umath._clear_floatstatus()
        except AttributeError:
            pass

        after = self.get_memory_usage()

        return {
            "before": before,
            "after": after,
            "freed": before["rss"] -
            after["rss"]}

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive memory usage summary.

        Returns:
            Memory usage summary
        """
        current = self.get_memory_usage()

        return {
            "current": current,
            "peak": self.peak_memory,
            "history_length": len(
                self.memory_history),
            "within_limit": self.check_memory_limit(),
            "available_percent": (
                current["available"] /
                current["total"]) *
            100,
        }


class CacheManager:
    """Manager for caching frequently used computations."""

    def __init__(self, max_size: int = 1000, max_memory_gb: float = 1.0):
        """
        Initialize the cache manager.

        Args:
            max_size: Maximum number of cached items
            max_memory_gb: Maximum memory usage for cache in GB
        """
        self.max_size = max_size
        self.max_memory_gb = max_memory_gb
        self.cache = {}
        self.access_count = {}
        self.size_estimates = {}
        self.memory_manager = MemoryManager()

    def _estimate_size(self, obj: Any) -> int:
        """Estimate the size of an object in bytes."""
        if isinstance(obj, np.ndarray):
            return obj.nbytes
        elif isinstance(obj, (list, tuple)):
            return sum(self._estimate_size(item) for item in obj)
        elif isinstance(obj, dict):
            return sum(self._estimate_size(v) for v in obj.values())
        else:
            return len(str(obj))

    def _get_cache_size_gb(self) -> float:
        """Get current cache size in GB."""
        total_bytes = sum(self.size_estimates.values())
        return total_bytes / (1024**3)

    def _evict_least_used(self) -> None:
        """Evict least frequently used items from cache."""
        if not self.cache:
            return

        # Sort by access count (ascending)
        sorted_items = sorted(self.access_count.items(), key=lambda x: x[1])

        # Remove items until we're under the limit
        while (
            len(self.cache) > self.max_size
            or self._get_cache_size_gb() > self.max_memory_gb
        ):
            if not sorted_items:
                break

            key, _ = sorted_items.pop(0)
            self._remove_from_cache(key)

    def _remove_from_cache(self, key: str) -> None:
        """Remove an item from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_count[key]
            del self.size_estimates[key]

    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Store an item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Estimate size
        size_bytes = self._estimate_size(value)

        # Check if adding this item would exceed limits
        if (len(self.cache) >= self.max_size or self._get_cache_size_gb() +
                size_bytes / (1024**3) > self.max_memory_gb):
            self._evict_least_used()

        # Add to cache
        self.cache[key] = value
        self.access_count[key] = 1
        self.size_estimates[key] = size_bytes

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.access_count.clear()
        self.size_estimates.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics
        """
        if not self.cache:
            return {
                "size": 0,
                "memory_gb": 0.0,
                "hit_rate": 0.0,
                "most_accessed": None,
            }

        total_accesses = sum(self.access_count.values())
        hit_rate = total_accesses / len(self.cache) if self.cache else 0

        most_accessed = max(self.access_count.items(), key=lambda x: x[1])[0]

        return {
            "size": len(self.cache),
            "memory_gb": self._get_cache_size_gb(),
            "hit_rate": hit_rate,
            "most_accessed": most_accessed,
            "max_size": self.max_size,
            "max_memory_gb": self.max_memory_gb,
        }


def optimize_memory_usage(func: Callable) -> Callable:
    """
    Decorator to optimize memory usage of a function.

    Args:
        func: Function to optimize

    Returns:
        Wrapped function with memory optimization
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        memory_manager = MemoryManager()

        # Record memory before
        before = memory_manager.record_memory_usage()

        try:
            result = func(*args, **kwargs)

            # Record memory after
            after = memory_manager.record_memory_usage()

            # Optimize if memory usage increased significantly
            if after["rss"] - before["rss"] > 0.1:  # More than 100MB increase
                memory_manager.optimize_memory_usage()

            return result

        except Exception as e:
            # Clean up on exception
            memory_manager.force_garbage_collection()
            raise e

    return wrapper


def clear_cache() -> None:
    """Clear all caches and perform garbage collection."""
    gc.collect()

    # Clear numpy cache if available
    try:
        np.core._multiarray_umath._clear_floatstatus()
    except AttributeError:
        pass


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage.

    Returns:
        Memory usage information
    """
    manager = MemoryManager()
    return manager.get_memory_usage()


# Global cache manager instance
_global_cache = CacheManager()


def get_global_cache() -> CacheManager:
    """Get the global cache manager instance."""
    return _global_cache


def cache_result(key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = _global_cache.get(key)
            if cached_result is not None:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)

            # Cache result
            _global_cache.set(key, result)

            return result

        return wrapper

    return decorator
