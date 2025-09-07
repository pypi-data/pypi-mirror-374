"""
智能日志系统模块
提供结构化日志、上下文追踪和Agent状态记录
"""

from .logger import (
    AgentLogger, LogLevel, LogCategory, LogContext, LogEntry,
    get_logger, configure_logging, debug, info, warning, error, critical
)

__all__ = [
    'AgentLogger', 'LogLevel', 'LogCategory', 'LogContext', 'LogEntry',
    'get_logger', 'configure_logging', 'debug', 'info', 'warning', 'error', 'critical'
]

__version__ = "1.0.0"
__author__ = "Infrastructure Team" 