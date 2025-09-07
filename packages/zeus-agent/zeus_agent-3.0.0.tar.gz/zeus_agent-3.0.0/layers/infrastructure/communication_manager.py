"""
Infrastructure Layer Communication Manager - 基础设施层通信管理器
集成层间通信协议，为基础设施层提供通信能力
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from ..framework.abstractions.layer_communication import (
    LayerCommunicationManager,
    LayerMessage,
    LayerMessageType,
    LayerMessageStatus,
    LayerMessagePriority,
    LayerMessageHandler,
    LayerMessageRouter,
    LayerMessageQueue,
    LayerMessageFilter,
    LayerMessageTransformer,
    LayerMessageValidator,
    LayerMessageLogger
)

logger = logging.getLogger(__name__)


class InfrastructureCommunicationManager:
    """基础设施层通信管理器"""
    
    def __init__(self):
        # 创建层间通信组件
        self.router = LayerMessageRouter()
        self.queue = LayerMessageQueue()
        self.filter = LayerMessageFilter()
        self.transformer = LayerMessageTransformer()
        self.validator = LayerMessageValidator()
        self.message_logger = LayerMessageLogger()
        
        # 设置队列的路由器
        self.queue.set_router(self.router)
        
        # 创建层间通信管理器
        self.layer_comm = LayerCommunicationManager(
            router=self.router,
            queue=self.queue,
            filter=self.filter,
            transformer=self.transformer,
            validator=self.validator,
            logger=self.message_logger
        )
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def send_message(self, message: LayerMessage) -> LayerMessage:
        """发送消息到其他层"""
        return await self.layer_comm.send_message(message)
    
    async def process_message(self, message: LayerMessage) -> LayerMessage:
        """处理接收到的消息"""
        return await self.layer_comm.process_message(message)
    
    def get_status(self) -> Dict[str, Any]:
        """获取通信管理器状态"""
        return {
            "component": "InfrastructureCommunicationManager",
            "layer": "infrastructure",
            "handlers_registered": len(self.router.handlers) if hasattr(self.router, "handlers") else 0 if hasattr(self.router, 'handlers') else 0,
            "queue_size": self.queue.size(),
            "layer_comm_status": self.layer_comm.get_status() if hasattr(self.layer_comm, 'get_status') else {}
        } 