"""
智能缓存系统
支持多级缓存、TTL过期、LRU策略、持久化和缓存预热
"""

import time
import json
import pickle
import hashlib
import threading
from typing import Dict, Any, Optional, Union, Callable, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict
import sqlite3


class CacheLevel(Enum):
    """缓存级别枚举"""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"  # 预留Redis支持


class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"        # 最近最少使用
    LFU = "lfu"        # 最少使用频率
    FIFO = "fifo"      # 先进先出
    TTL = "ttl"        # 基于时间


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size: int = 0
    
    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    @property
    def age(self) -> float:
        """获取条目年龄(秒)"""
        return time.time() - self.created_at


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: Optional[float] = None,
                 strategy: CacheStrategy = CacheStrategy.LRU):
        
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats(max_size=max_size)
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            entry = self._cache[key]
            
            # 检查过期
            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.size -= 1
                return None
            
            # 更新访问信息
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # LRU策略：移到末尾
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)
            
            self._stats.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            now = time.time()
            
            # 计算值大小（估算）
            try:
                size = len(pickle.dumps(value))
            except:
                size = 1
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=1,
                ttl=ttl or self.default_ttl,
                size=size
            )
            
            # 如果key已存在，更新统计
            if key in self._cache:
                self._stats.size -= 1
            
            # 添加到缓存
            self._cache[key] = entry
            self._stats.size += 1
            
            # 检查是否需要清理
            self._evict_if_needed()
            
            return True
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size -= 1
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._stats.size = 0
    
    def _evict_if_needed(self):
        """根据策略清理缓存"""
        while len(self._cache) > self.max_size:
            self._evict_one()
    
    def _evict_one(self):
        """清理一个缓存条目"""
        if not self._cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # 删除最少使用的（最前面的）
            key = next(iter(self._cache))
        elif self.strategy == CacheStrategy.LFU:
            # 删除访问频率最低的
            key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].access_count)
        elif self.strategy == CacheStrategy.FIFO:
            # 删除最早的
            key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].created_at)
        else:  # TTL
            # 删除最快过期的
            key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].created_at + (self._cache[k].ttl or float('inf')))
        
        del self._cache[key]
        self._stats.evictions += 1
        self._stats.size -= 1
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self._stats
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._stats.size -= 1
            
            return len(expired_keys)


class DiskCache:
    """磁盘缓存实现"""
    
    def __init__(self, 
                 cache_dir: str = "cache",
                 max_size_mb: int = 100,
                 default_ttl: Optional[float] = None):
        
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite数据库用于存储元数据
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_database()
        
        self._lock = threading.RLock()
        self._stats = CacheStats()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    file_path TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    access_count INTEGER,
                    ttl REAL,
                    size INTEGER
                )
            """)
            conn.commit()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用MD5哈希避免文件名冲突
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT file_path, created_at, ttl FROM cache_entries WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if not row:
                    self._stats.misses += 1
                    return None
                
                file_path, created_at, ttl = row
                
                # 检查过期
                if ttl and time.time() - created_at > ttl:
                    self._delete_entry(key, file_path)
                    self._stats.misses += 1
                    return None
                
                # 读取文件
                try:
                    cache_file = Path(file_path)
                    if not cache_file.exists():
                        self._delete_entry(key)
                        self._stats.misses += 1
                        return None
                    
                    with open(cache_file, 'rb') as f:
                        value = pickle.load(f)
                    
                    # 更新访问信息
                    conn.execute(
                        "UPDATE cache_entries SET last_accessed = ?, access_count = access_count + 1 WHERE key = ?",
                        (time.time(), key)
                    )
                    conn.commit()
                    
                    self._stats.hits += 1
                    return value
                    
                except Exception as e:
                    print(f"磁盘缓存读取失败 {key}: {e}")
                    self._delete_entry(key, file_path)
                    self._stats.misses += 1
                    return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                file_path = self._get_file_path(key)
                
                # 序列化并写入文件
                with open(file_path, 'wb') as f:
                    pickle.dump(value, f)
                
                # 获取文件大小
                size = file_path.stat().st_size
                
                # 更新数据库
                now = time.time()
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO cache_entries "
                        "(key, file_path, created_at, last_accessed, access_count, ttl, size) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (key, str(file_path), now, now, 1, ttl or self.default_ttl, size)
                    )
                    conn.commit()
                
                # 检查磁盘空间
                self._cleanup_if_needed()
                
                return True
                
            except Exception as e:
                print(f"磁盘缓存写入失败 {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT file_path FROM cache_entries WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    self._delete_entry(key, row[0])
                    return True
                
                return False
    
    def _delete_entry(self, key: str, file_path: str = None):
        """删除缓存条目"""
        with sqlite3.connect(self.db_path) as conn:
            if file_path is None:
                cursor = conn.execute(
                    "SELECT file_path FROM cache_entries WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                if row:
                    file_path = row[0]
            
            # 删除文件
            if file_path:
                try:
                    Path(file_path).unlink(missing_ok=True)
                except Exception:
                    pass
            
            # 删除数据库记录
            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            conn.commit()
    
    def _cleanup_if_needed(self):
        """清理磁盘空间"""
        # 计算当前使用的磁盘空间
        total_size = 0
        for file_path in self.cache_dir.glob("*.cache"):
            try:
                total_size += file_path.stat().st_size
            except:
                continue
        
        if total_size > self.max_size_bytes:
            # 删除最旧的文件
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key, file_path, size FROM cache_entries ORDER BY last_accessed ASC"
                )
                
                for key, file_path, size in cursor:
                    self._delete_entry(key, file_path)
                    total_size -= size
                    
                    if total_size <= self.max_size_bytes * 0.8:  # 清理到80%
                        break
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        with self._lock:
            now = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key, file_path FROM cache_entries WHERE ttl IS NOT NULL AND created_at + ttl < ?",
                    (now,)
                )
                
                expired_entries = cursor.fetchall()
                
                for key, file_path in expired_entries:
                    self._delete_entry(key, file_path)
                
                return len(expired_entries)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取磁盘缓存统计"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), SUM(size) FROM cache_entries")
            count, total_size = cursor.fetchone()
            
            return {
                'entries': count or 0,
                'total_size_bytes': total_size or 0,
                'total_size_mb': (total_size or 0) / 1024 / 1024,
                'max_size_mb': self.max_size_bytes / 1024 / 1024,
                'hits': self._stats.hits,
                'misses': self._stats.misses,
                'hit_rate': self._stats.hit_rate
            }


class MultiLevelCache:
    """多级缓存管理器"""
    
    def __init__(self,
                 memory_config: Optional[Dict[str, Any]] = None,
                 disk_config: Optional[Dict[str, Any]] = None,
                 enable_memory: bool = True,
                 enable_disk: bool = True):
        
        self.caches = {}
        
        # 初始化内存缓存
        if enable_memory:
            memory_config = memory_config or {}
            self.caches[CacheLevel.MEMORY] = MemoryCache(**memory_config)
        
        # 初始化磁盘缓存
        if enable_disk:
            disk_config = disk_config or {}
            self.caches[CacheLevel.DISK] = DiskCache(**disk_config)
        
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """多级缓存获取"""
        with self._lock:
            # 按优先级检查各级缓存
            for level in [CacheLevel.MEMORY, CacheLevel.DISK]:
                if level in self.caches:
                    value = self.caches[level].get(key)
                    if value is not None:
                        # 将值提升到更高级别的缓存
                        self._promote_to_higher_levels(key, value, level)
                        return value
            
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, levels: Optional[List[CacheLevel]] = None):
        """多级缓存设置"""
        with self._lock:
            # 如果没有指定级别，写入所有可用级别
            if levels is None:
                levels = list(self.caches.keys())
            
            for level in levels:
                if level in self.caches:
                    self.caches[level].set(key, value, ttl)
    
    def delete(self, key: str):
        """从所有级别删除"""
        with self._lock:
            for cache in self.caches.values():
                cache.delete(key)
    
    def _promote_to_higher_levels(self, key: str, value: Any, current_level: CacheLevel):
        """将值提升到更高级别的缓存"""
        higher_levels = []
        
        if current_level == CacheLevel.DISK and CacheLevel.MEMORY in self.caches:
            higher_levels.append(CacheLevel.MEMORY)
        
        for level in higher_levels:
            self.caches[level].set(key, value)
    
    def cleanup_expired(self) -> Dict[CacheLevel, int]:
        """清理所有级别的过期条目"""
        results = {}
        for level, cache in self.caches.items():
            if hasattr(cache, 'cleanup_expired'):
                results[level] = cache.cleanup_expired()
        return results
    
    def get_stats(self) -> Dict[CacheLevel, Any]:
        """获取所有级别的统计信息"""
        stats = {}
        for level, cache in self.caches.items():
            stats[level] = cache.get_stats()
        return stats


# 全局缓存实例
_global_cache = None


def get_cache(**kwargs) -> MultiLevelCache:
    """获取全局缓存实例"""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = MultiLevelCache(**kwargs)
    
    return _global_cache


# 便捷函数
def cache_get(key: str) -> Optional[Any]:
    """获取缓存值"""
    return get_cache().get(key)


def cache_set(key: str, value: Any, ttl: Optional[float] = None):
    """设置缓存值"""
    get_cache().set(key, value, ttl)


def cache_delete(key: str):
    """删除缓存值"""
    get_cache().delete(key)


# 缓存装饰器
def cached(ttl: Optional[float] = None, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # 尝试从缓存获取
            result = cache_get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator 