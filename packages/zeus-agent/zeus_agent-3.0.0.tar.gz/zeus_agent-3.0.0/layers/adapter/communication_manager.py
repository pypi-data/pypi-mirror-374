"""
Adapter Layer Communication Manager - 适配器层通信管理器
集成层间通信协议，为适配器层提供通信能力
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
    LayerMessageHandler,
    LayerMessageRouter,
    LayerMessageQueue,
    LayerMessageFilter,
    LayerMessageTransformer,
    LayerMessageValidator,
    LayerMessageLogger
)

logger = logging.getLogger(__name__)


class AdapterCommunicationManager:
    """适配器层通信管理器"""
    
    def __init__(self):
        # 创建通信组件
        self.router = LayerMessageRouter()
        self.queue = LayerMessageQueue()
        self.filter = LayerMessageFilter()
        self.transformer = LayerMessageTransformer()
        self.validator = LayerMessageValidator()
        self.logger = LayerMessageLogger()
        
        # 创建通信管理器
        self.communicator = LayerCommunicationManager(
            router=self.router,
            queue=self.queue,
            filter=self.filter,
            transformer=self.transformer,
            validator=self.validator,
            logger=self.logger
        )
        
        self._register_handlers()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def _register_handlers(self):
        """注册适配器层的请求处理器"""
        self.communicator.router.register_handler("create_agent_instance", self._handle_create_agent_instance)
        self.communicator.router.register_handler("execute_task", self._handle_execute_task)
        self.communicator.router.register_handler("get_adapter_status", self._handle_get_adapter_status)
        self.communicator.router.register_handler("list_available_adapters", self._handle_list_available_adapters)
        self.communicator.router.register_handler("test_adapter_connection", self._handle_test_adapter_connection)
        self.communicator.router.register_handler("get_adapter_capabilities", self._handle_get_adapter_capabilities)
    
    async def _handle_create_agent_instance(self, message: LayerMessage) -> bool:
        """处理创建Agent实例请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        payload = message.content
        adapter_type = payload.get('adapter_type')
        agent_config = payload.get('agent_config', {})
        
        try:
            # 获取适配器注册表
            registry = AdapterRegistry()
            adapter = registry.get_adapter(adapter_type)
            
            if not adapter:
                message.status = LayerMessageStatus.ERROR
                message.error = {"message": f"Adapter not found: {adapter_type}"}
                return False
            
            # 创建Agent实例
            agent_instance = await adapter.create_agent(agent_config)
            agent_id = f"agent_{adapter_type}_{int(datetime.now().timestamp())}"
            
            self.logger.info(f"Agent instance created: {agent_id} using {adapter_type}")
            
            # 更新消息内容
            message.content.update({
                "agent_id": agent_id,
                "adapter_type": adapter_type,
                "status": "created"
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create agent instance: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def _handle_execute_task(self, message: LayerMessage) -> bool:
        """处理执行任务请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        payload = message.content
        adapter_type = payload.get('adapter_type')
        task_description = payload.get('task_description')
        task_parameters = payload.get('task_parameters', {})
        
        try:
            # 获取适配器
            registry = AdapterRegistry()
            adapter = registry.get_adapter(adapter_type)
            
            if not adapter:
                message.status = LayerMessageStatus.ERROR
                message.error = {"message": f"Adapter not found: {adapter_type}"}
                return False
            
            # 执行任务
            start_time = datetime.now()
            result = await adapter.execute_task(task_description, task_parameters)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Task executed via {adapter_type}: {task_description}")
            
            # 更新消息内容
            message.content.update({
                "task_id": f"task_{int(datetime.now().timestamp())}",
                "adapter_type": adapter_type,
                "result": result,
                "execution_time": execution_time,
                "status": "completed"
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute task via {adapter_type}: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def _handle_get_adapter_status(self, message: LayerMessage) -> bool:
        """处理获取适配器状态请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        payload = message.content
        adapter_type = payload.get('adapter_type')
        
        try:
            registry = AdapterRegistry()
            adapter = registry.get_adapter(adapter_type)
            
            if not adapter:
                message.content.update({
                    "status": "not_found",
                    "adapter_type": adapter_type
                })
                message.status = LayerMessageStatus.COMPLETED
                return True
            
            status = await adapter.get_status()
            message.content.update({
                "adapter_type": adapter_type,
                "status": status,
                "capabilities": adapter.get_capabilities(),
                "last_updated": datetime.now().isoformat()
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get adapter status for {adapter_type}: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def _handle_list_available_adapters(self, message: LayerMessage) -> bool:
        """处理列出可用适配器请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        try:
            registry = AdapterRegistry()
            adapters = registry.list_adapters()
            
            adapter_list = []
            for adapter_type, adapter in adapters.items():
                adapter_info = {
                    "adapter_type": adapter_type,
                    "status": await adapter.get_status(),
                    "capabilities": adapter.get_capabilities(),
                    "description": getattr(adapter, 'description', 'No description available')
                }
                adapter_list.append(adapter_info)
            
            message.content.update({
                "adapters": adapter_list,
                "total_count": len(adapter_list)
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to list available adapters: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def _handle_test_adapter_connection(self, message: LayerMessage) -> bool:
        """处理测试适配器连接请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        payload = message.content
        adapter_type = payload.get('adapter_type')
        
        try:
            registry = AdapterRegistry()
            adapter = registry.get_adapter(adapter_type)
            
            if not adapter:
                message.content.update({
                    "status": "not_found",
                    "adapter_type": adapter_type
                })
                message.status = LayerMessageStatus.COMPLETED
                return True
            
            # 测试连接
            connection_test = await adapter.test_connection()
            
            message.content.update({
                "adapter_type": adapter_type,
                "connection_status": connection_test.get('status', 'unknown'),
                "response_time": connection_test.get('response_time', 0),
                "error_message": connection_test.get('error', None)
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to test adapter connection for {adapter_type}: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def _handle_get_adapter_capabilities(self, message: LayerMessage) -> bool:
        """处理获取适配器能力请求"""
        from .registry.adapter_registry import AdapterRegistry
        
        payload = message.content
        adapter_type = payload.get('adapter_type')
        
        try:
            registry = AdapterRegistry()
            adapter = registry.get_adapter(adapter_type)
            
            if not adapter:
                message.content.update({
                    "capabilities": [],
                    "adapter_type": adapter_type
                })
                message.status = LayerMessageStatus.COMPLETED
                return True
            
            capabilities = adapter.get_capabilities()
            
            message.content.update({
                "adapter_type": adapter_type,
                "capabilities": capabilities,
                "capability_count": len(capabilities)
            })
            message.status = LayerMessageStatus.COMPLETED
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get adapter capabilities for {adapter_type}: {e}")
            message.status = LayerMessageStatus.ERROR
            message.error = {"message": str(e)}
            return False
    
    async def send_message(self, message: LayerMessage) -> bool:
        """发送消息"""
        return await self.communicator.send_message(message)
    
    def subscribe_to_events(self, event_type: str, handler: LayerMessageHandler) -> None:
        """订阅事件"""
        self.communicator.router.register_handler(event_type, handler)


# 全局适配器通信管理器实例
adapter_communication_manager = AdapterCommunicationManager() 