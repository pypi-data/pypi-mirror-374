"""
智能日志系统
支持结构化日志、上下文追踪、Agent状态记录和性能监控
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from contextlib import contextmanager


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """日志分类枚举"""
    AGENT = "agent"
    ADAPTER = "adapter"
    TASK = "task"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER = "user"


@dataclass
class LogContext:
    """日志上下文信息"""
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    adapter_name: Optional[str] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class LogEntry:
    """结构化日志条目"""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    context: LogContext
    metadata: Dict[str, Any]
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "category": self.category.value,
            "message": self.message,
            "context": self.context.to_dict(),
            "metadata": self.metadata,
            "duration_ms": self.duration_ms
        }


class AgentLogger:
    """Agent智能日志记录器"""
    
    def __init__(self, 
                 name: str = "zeus",
                 log_file: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_structured: bool = True):
        
        self.name = name
        self.enable_structured = enable_structured
        self._context_stack = threading.local()
        
        # 创建Python标准logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清除现有handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 控制台输出
        if enable_console:
            console_handler = logging.StreamHandler()
            console_formatter = self._create_formatter(structured=False)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # 文件输出
        if log_file:
            from logging.handlers import RotatingFileHandler
            
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            file_formatter = self._create_formatter(structured=enable_structured)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # 性能统计
        self.performance_stats = {
            'total_logs': 0,
            'logs_by_level': {},
            'logs_by_category': {},
            'start_time': datetime.now()
        }
    
    def _create_formatter(self, structured: bool = True) -> logging.Formatter:
        """创建日志格式化器"""
        if structured:
            return StructuredFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def _get_context_stack(self) -> List[LogContext]:
        """获取当前线程的上下文栈"""
        if not hasattr(self._context_stack, 'stack'):
            self._context_stack.stack = []
        return self._context_stack.stack
    
    def _merge_context(self) -> LogContext:
        """合并上下文栈中的所有上下文"""
        stack = self._get_context_stack()
        if not stack:
            return LogContext()
        
        # 从底层到顶层合并上下文
        merged = LogContext()
        for context in stack:
            for field, value in asdict(context).items():
                if value is not None:
                    setattr(merged, field, value)
        
        return merged
    
    @contextmanager
    def context(self, **kwargs):
        """上下文管理器，用于设置日志上下文"""
        context = LogContext(**kwargs)
        stack = self._get_context_stack()
        stack.append(context)
        try:
            yield
        finally:
            stack.pop()
    
    @contextmanager
    def timer(self, message: str, category: LogCategory = LogCategory.PERFORMANCE, **kwargs):
        """计时上下文管理器"""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.info(
                message=f"{message} (耗时: {duration_ms:.2f}ms)",
                category=category,
                duration_ms=duration_ms,
                **kwargs
            )
    
    def _log(self, 
             level: LogLevel,
             message: str,
             category: LogCategory = LogCategory.SYSTEM,
             duration_ms: Optional[float] = None,
             **metadata):
        """内部日志记录方法"""
        
        # 合并上下文
        context = self._merge_context()
        
        # 创建日志条目
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            context=context,
            metadata=metadata,
            duration_ms=duration_ms
        )
        
        # 更新统计信息
        self.performance_stats['total_logs'] += 1
        self.performance_stats['logs_by_level'][level.value] = \
            self.performance_stats['logs_by_level'].get(level.value, 0) + 1
        self.performance_stats['logs_by_category'][category.value] = \
            self.performance_stats['logs_by_category'].get(category.value, 0) + 1
        
        # 输出日志
        if self.enable_structured:
            # 结构化日志输出
            log_data = entry.to_dict()
            self.logger.log(
                getattr(logging, level.value),
                json.dumps(log_data, ensure_ascii=False, default=str)
            )
        else:
            # 标准格式输出
            context_str = ""
            if context.agent_id:
                context_str += f"[Agent:{context.agent_id}]"
            if context.task_id:
                context_str += f"[Task:{context.task_id}]"
            if context.session_id:
                context_str += f"[Session:{context.session_id}]"
            
            full_message = f"{context_str} [{category.value.upper()}] {message}"
            if metadata:
                full_message += f" | {metadata}"
            
            self.logger.log(getattr(logging, level.value), full_message)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
        """调试日志"""
        self._log(LogLevel.DEBUG, message, category, **metadata)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
        """信息日志"""
        self._log(LogLevel.INFO, message, category, **metadata)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
        """警告日志"""
        self._log(LogLevel.WARNING, message, category, **metadata)
    
    def error(self, message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
        """错误日志"""
        self._log(LogLevel.ERROR, message, category, **metadata)
    
    def critical(self, message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
        """严重错误日志"""
        self._log(LogLevel.CRITICAL, message, category, **metadata)
    
    def agent_action(self, agent_id: str, action: str, **metadata):
        """记录Agent行为"""
        with self.context(agent_id=agent_id):
            self.info(f"Agent行为: {action}", LogCategory.AGENT, **metadata)
    
    def task_start(self, task_id: str, task_type: str, **metadata):
        """记录任务开始"""
        with self.context(task_id=task_id):
            self.info(f"任务开始: {task_type}", LogCategory.TASK, **metadata)
    
    def task_complete(self, task_id: str, result: str, duration_ms: float, **metadata):
        """记录任务完成"""
        with self.context(task_id=task_id):
            self.info(
                f"任务完成: {result}",
                LogCategory.TASK,
                duration_ms=duration_ms,
                **metadata
            )
    
    def adapter_call(self, adapter_name: str, method: str, **metadata):
        """记录适配器调用"""
        with self.context(adapter_name=adapter_name):
            self.info(f"适配器调用: {method}", LogCategory.ADAPTER, **metadata)
    
    def security_event(self, event_type: str, severity: str, **metadata):
        """记录安全事件"""
        level = LogLevel.WARNING if severity == 'medium' else LogLevel.ERROR
        self._log(level, f"安全事件: {event_type}", LogCategory.SECURITY, **metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        uptime = (datetime.now() - self.performance_stats['start_time']).total_seconds()
        return {
            **self.performance_stats,
            'uptime_seconds': uptime,
            'logs_per_second': self.performance_stats['total_logs'] / max(uptime, 1)
        }


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record):
        """格式化日志记录"""
        try:
            # 如果消息已经是JSON格式，直接返回
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # 如果不是JSON，创建结构化格式
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # 添加异常信息
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_entry, ensure_ascii=False, default=str)


# 全局日志实例
_global_logger = None


def get_logger(name: str = "zeus", **kwargs) -> AgentLogger:
    """获取全局日志实例"""
    global _global_logger
    
    if _global_logger is None:
        # 默认配置
        default_config = {
            'log_file': 'logs/zeus.log',
            'enable_console': True,
            'enable_structured': True
        }
        default_config.update(kwargs)
        
        _global_logger = AgentLogger(name, **default_config)
    
    return _global_logger


def configure_logging(config: Dict[str, Any]):
    """配置全局日志"""
    global _global_logger
    _global_logger = AgentLogger(**config)


# 便捷函数
def debug(message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
    """全局调试日志"""
    get_logger().debug(message, category, **metadata)


def info(message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
    """全局信息日志"""
    get_logger().info(message, category, **metadata)


def warning(message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
    """全局警告日志"""
    get_logger().warning(message, category, **metadata)


def error(message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
    """全局错误日志"""
    get_logger().error(message, category, **metadata)


def critical(message: str, category: LogCategory = LogCategory.SYSTEM, **metadata):
    """全局严重错误日志"""
    get_logger().critical(message, category, **metadata) 