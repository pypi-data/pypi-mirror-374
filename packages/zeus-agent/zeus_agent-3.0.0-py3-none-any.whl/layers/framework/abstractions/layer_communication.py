"""
Layer Communication Protocol - 层间通信协议
实现8层架构间的统一通信机制，包含A2A (Agent-to-Agent) 协议支持
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union
from typing_extensions import Protocol

logger = logging.getLogger(__name__)


class LayerMessageType(Enum):
    """层间消息类型"""
    REQUEST = "request"           # 请求消息
    RESPONSE = "response"         # 响应消息
    EVENT = "event"              # 事件消息
    COMMAND = "command"          # 命令消息
    NOTIFICATION = "notification" # 通知消息
    

class LayerMessageStatus(Enum):
    """层间消息状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class LayerMessagePriority(Enum):
    """层间消息优先级"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class LayerMessage:
    """层间消息"""
    id: str
    type: LayerMessageType
    source: str
    target: str
    content: Dict[str, Any]
    status: LayerMessageStatus = LayerMessageStatus.PENDING
    priority: LayerMessagePriority = LayerMessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None


class LayerMessageHandler(ABC):
    """层间消息处理器"""
    
    @abstractmethod
    async def handle_message(self, message: LayerMessage) -> bool:
        """处理消息"""
        pass


class LayerMessageRouter:
    """层间消息路由器"""
    
    def __init__(self):
        self.handlers: Dict[str, LayerMessageHandler] = {}
    
    def register_handler(self, target: str, handler: LayerMessageHandler):
        """注册消息处理器"""
        self.handlers[target] = handler
    
    def unregister_handler(self, target: str):
        """注销消息处理器"""
        if target in self.handlers:
            del self.handlers[target]
    
    async def route_message(self, message: LayerMessage) -> bool:
        """路由消息"""
        handler = self.handlers.get(message.target)
        if handler:
            return await handler.handle_message(message)
        return False


class LayerMessageQueue:
    """层间消息队列"""
    
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.paused = False
        self.router = None
    
    def set_router(self, router: 'LayerMessageRouter'):
        """设置路由器"""
        self.router = router
    
    async def put(self, message: LayerMessage):
        """添加消息"""
        await self.queue.put(message)
    
    async def get(self) -> LayerMessage:
        """获取消息"""
        return await self.queue.get()
    
    def size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()
    
    def pause(self):
        """暂停消息处理"""
        self.paused = True
    
    async def resume(self):
        """恢复消息处理"""
        self.paused = False
        while not self.queue.empty():
            message = await self.queue.get()
            if self.router:
                await self.router.route_message(message)
    
    async def process_message(self, message: LayerMessage):
        """处理消息"""
        if self.router:
            await self.router.route_message(message)


class LayerMessageFilter:
    """层间消息过滤器"""
    
    def __init__(self):
        self.rules: List[Callable[[LayerMessage], bool]] = []
    
    def add_rule(self, rule: Callable[[LayerMessage], bool]):
        """添加过滤规则"""
        self.rules.append(rule)
    
    def remove_rule(self, rule: Callable[[LayerMessage], bool]):
        """移除过滤规则"""
        if rule in self.rules:
            self.rules.remove(rule)
    
    def filter_message(self, message: LayerMessage) -> bool:
        """过滤消息"""
        return all(rule(message) for rule in self.rules)


class LayerMessageTransformer:
    """层间消息转换器"""
    
    def __init__(self):
        self.transforms: List[Callable[[LayerMessage], LayerMessage]] = []
    
    def add_transform(self, transform: Callable[[LayerMessage], LayerMessage]):
        """添加转换规则"""
        self.transforms.append(transform)
    
    def remove_transform(self, transform: Callable[[LayerMessage], LayerMessage]):
        """移除转换规则"""
        if transform in self.transforms:
            self.transforms.remove(transform)
    
    def transform_message(self, message: LayerMessage) -> LayerMessage:
        """转换消息"""
        result = message
        for transform in self.transforms:
            result = transform(result)
        return result


class LayerMessageValidator:
    """层间消息验证器"""
    
    def __init__(self):
        self.rules: List[Callable[[LayerMessage], bool]] = []
    
    def add_rule(self, rule: Callable[[LayerMessage], bool]):
        """添加验证规则"""
        self.rules.append(rule)
    
    def remove_rule(self, rule: Callable[[LayerMessage], bool]):
        """移除验证规则"""
        if rule in self.rules:
            self.rules.remove(rule)
    
    def validate_message(self, message: LayerMessage) -> bool:
        """验证消息"""
        return all(rule(message) for rule in self.rules)


class LayerMessageLogger:
    """层间消息日志记录器"""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
    
    def log_message(self, message: LayerMessage):
        """记录消息"""
        log_entry = {
            "message_id": message.id,
            "type": message.type.value,
            "source": message.source,
            "target": message.target,
            "status": message.status.value,
            "priority": message.priority.value,
            "timestamp": message.timestamp.isoformat(),
            "metadata": message.metadata,
            "error": message.error
        }
        self.logs.append(log_entry)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """获取日志"""
        return self.logs


class LayerCommunicationManager:
    """层间通信管理器"""
    
    def __init__(self,
                 router: LayerMessageRouter,
                 queue: LayerMessageQueue,
                 filter: LayerMessageFilter,
                 transformer: LayerMessageTransformer,
                 validator: LayerMessageValidator,
                 logger: LayerMessageLogger):
        self.router = router
        self.queue = queue
        self.filter = filter
        self.transformer = transformer
        self.validator = validator
        self.logger = logger
        
        # 设置队列的路由器
        self.queue.set_router(self.router)
        
        # 性能指标
        self.total_messages = 0
        self.processed_messages = 0
        self.failed_messages = 0
        self.processing_times: List[float] = []
    
    async def send_message(self, message: LayerMessage):
        """发送消息"""
        start_time = datetime.now()
        self.total_messages += 1
        
        try:
            # 记录原始消息
            self.logger.log_message(message)
            
            # 验证消息
            if not self.validator.validate_message(message):
                message.status = LayerMessageStatus.ERROR
                message.error = {"message": "Message validation failed"}
                self.failed_messages += 1
                self.logger.log_message(message)
                return
            
            # 过滤消息
            if not self.filter.filter_message(message):
                return
            
            # 转换消息
            transformed_message = self.transformer.transform_message(message)
            
            # 添加到队列
            if self.queue.paused:
                await self.queue.put(transformed_message)
                return
            
            # 路由消息
            transformed_message.status = LayerMessageStatus.PROCESSING
            success = await self.router.route_message(transformed_message)
            
            # 更新状态
            if success:
                transformed_message.status = LayerMessageStatus.COMPLETED
                self.processed_messages += 1
            else:
                transformed_message.status = LayerMessageStatus.FAILED
                transformed_message.error = {"message": "Message routing failed"}
                self.failed_messages += 1
            
            # 记录日志
            self.logger.log_message(transformed_message)
            
            # 记录处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(processing_time)
            
        except Exception as e:
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            self.failed_messages += 1
            self.logger.log_message(message)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "total_messages": self.total_messages,
            "processed_messages": self.processed_messages,
            "failed_messages": self.failed_messages,
            "success_rate": self.processed_messages / self.total_messages if self.total_messages > 0 else 0,
            "average_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        } 