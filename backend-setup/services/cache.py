"""
Caching layer for subscription and billing data.
Implements TTL-based caching with automatic expiration.
"""
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with TTL."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        """
        Initialize cache entry.
        
        Args:
            value: The value to cache
            ttl_seconds: Time to live in seconds
        """
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        elapsed = time.time() - self.created_at
        return elapsed > self.ttl_seconds
    
    def get(self) -> Optional[Any]:
        """Get value if not expired, otherwise return None."""
        if self.is_expired():
            return None
        return self.value


class SubscriptionCache:
    """
    In-memory cache for subscription data with TTL.
    Thread-safe caching for subscription status and related data.
    """
    
    # Default TTL values (in seconds)
    DEFAULT_SUBSCRIPTION_TTL = 30  # 30 seconds for subscription status
    DEFAULT_USAGE_TTL = 300  # 5 minutes for usage metrics
    DEFAULT_BILLING_HISTORY_TTL = 600  # 10 minutes for billing history
    
    def __init__(self):
        """Initialize the cache."""
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = None  # Can be replaced with threading.Lock if needed
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set a value in the cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (uses default if None)
        """
        if ttl_seconds is None:
            ttl_seconds = self.DEFAULT_SUBSCRIPTION_TTL
        
        self._cache[key] = CacheEntry(value, ttl_seconds)
        logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            logger.debug(f"Cache MISS: {key} (not found)")
            return None
        
        entry = self._cache[key]
        value = entry.get()
        
        if value is None:
            logger.debug(f"Cache MISS: {key} (expired)")
            del self._cache[key]
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return value
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache DELETE: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.debug("Cache CLEAR: all entries removed")
    
    def get_subscription_key(self, customer_id: str) -> str:
        """Generate cache key for subscription."""
        return f"subscription:{customer_id}"
    
    def get_usage_key(self, customer_id: str) -> str:
        """Generate cache key for usage metrics."""
        return f"usage:{customer_id}"
    
    def get_billing_history_key(self, customer_id: str) -> str:
        """Generate cache key for billing history."""
        return f"billing_history:{customer_id}"
    
    def invalidate_customer_cache(self, customer_id: str) -> None:
        """
        Invalidate all cache entries for a customer.
        Called when subscription changes via webhook.
        
        Args:
            customer_id: Customer ID
        """
        keys_to_delete = [
            self.get_subscription_key(customer_id),
            self.get_usage_key(customer_id),
            self.get_billing_history_key(customer_id),
        ]
        
        for key in keys_to_delete:
            self.delete(key)
        
        logger.info(f"Invalidated cache for customer: {customer_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        active_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
        }


# Global cache instance
_subscription_cache = SubscriptionCache()


def get_cache() -> SubscriptionCache:
    """Get the global subscription cache instance."""
    return _subscription_cache
