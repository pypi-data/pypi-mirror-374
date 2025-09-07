"""
基础设施层 - Infrastructure Layer
为整个Agent开发中心提供基础设施支持：日志、配置、缓存、安全、性能监控
"""

# 日志系统
from .logging.logger import (
    AgentLogger, LogLevel, LogCategory, LogContext, LogEntry,
    get_logger, configure_logging, debug, info, warning, error, critical
)

# 配置管理
from .config.config_manager import (
    ConfigManager, ConfigSchema, ConfigFormat, ConfigSource,
    get_config_manager, get_config, set_config, generate_encryption_key,
    DEEPSEEK_SCHEMA, LOGGING_SCHEMA
)

# 缓存系统
from .cache.cache_manager import (
    MultiLevelCache, MemoryCache, DiskCache, CacheLevel, CacheStrategy,
    CacheEntry, CacheStats, get_cache, cache_get, cache_set, cache_delete, cached
)

# 层间通信管理器
from .communication_manager import (
    InfrastructureCommunicationManager
)

__all__ = [
    # 日志系统
    'AgentLogger', 'LogLevel', 'LogCategory', 'LogContext', 'LogEntry',
    'get_logger', 'configure_logging', 'debug', 'info', 'warning', 'error', 'critical',
    
    # 配置管理
    'ConfigManager', 'ConfigSchema', 'ConfigFormat', 'ConfigSource',
    'get_config_manager', 'get_config', 'set_config', 'generate_encryption_key',
    'DEEPSEEK_SCHEMA', 'LOGGING_SCHEMA',
    
    # 缓存系统
    'MultiLevelCache', 'MemoryCache', 'DiskCache', 'CacheLevel', 'CacheStrategy',
    'CacheEntry', 'CacheStats', 'get_cache', 'cache_get', 'cache_set', 'cache_delete', 'cached',
    
    # 层间通信管理器
    'InfrastructureCommunicationManager'
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Infrastructure Team" 