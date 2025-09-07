"""
智能缓存系统模块
支持多级缓存、TTL过期、LRU策略、持久化和缓存预热
"""

from .cache_manager import (
    MultiLevelCache, MemoryCache, DiskCache, CacheLevel, CacheStrategy,
    CacheEntry, CacheStats, get_cache, cache_get, cache_set, cache_delete, cached
)

__all__ = [
    'MultiLevelCache', 'MemoryCache', 'DiskCache', 'CacheLevel', 'CacheStrategy',
    'CacheEntry', 'CacheStats', 'get_cache', 'cache_get', 'cache_set', 'cache_delete', 'cached'
]

__version__ = "1.0.0"
__author__ = "Infrastructure Team" 