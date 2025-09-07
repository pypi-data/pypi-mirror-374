"""
A2A Integration Components
A2A协议与适配器的集成组件

提供A2A协议与各种适配器的集成功能，包括：
1. 集成管理器
2. 适配器桥接器
3. 消息路由器
"""

from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple, Type
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import uuid
from abc import ABC, abstractmethod

from .a2a_protocol import (
    A2AMessageType,
    A2ACapabilityType,
    A2AProtocolVersion,
    A2ACapability,
    A2AAgentProfile,
    A2AMessage,
    A2AProtocolHandler
)
from .task import TaskType, UniversalTask
from .result import ResultStatus, UniversalResult
from .context import UniversalContext
from ...adapter.base import BaseAdapter

logger = logging.getLogger(__name__)


class A2AAdapterBridge:
    """A2A协议与适配器的桥接器"""
    
    def __init__(self, adapter: BaseAdapter, protocol_handler: A2AProtocolHandler):
        self.adapter = adapter
        self.protocol_handler = protocol_handler
        self._capability_mapping = self._create_capability_mapping()
        self._task_type_mapping = self._create_task_type_mapping()
    
    def _create_capability_mapping(self) -> Dict[str, A2ACapabilityType]:
        """创建能力映射关系"""
        return {
            "text_processing": A2ACapabilityType.TEXT_PROCESSING,
            "code_generation": A2ACapabilityType.CODE_GENERATION,
            "data_analysis": A2ACapabilityType.DATA_ANALYSIS,
            "reasoning": A2ACapabilityType.REASONING,
            "planning": A2ACapabilityType.PLANNING,
            "task_coordination": A2ACapabilityType.TASK_COORDINATION,
            "workflow_management": A2ACapabilityType.WORKFLOW_MANAGEMENT,
            "team_leadership": A2ACapabilityType.TEAM_LEADERSHIP
        }
    
    def _create_task_type_mapping(self) -> Dict[A2AMessageType, TaskType]:
        """创建任务类型映射关系"""
        return {
            A2AMessageType.TASK_REQUEST: TaskType.CONVERSATION,
            A2AMessageType.COLLABORATION_INVITE: TaskType.TOOL_EXECUTION,
            A2AMessageType.WORK_ASSIGNMENT: TaskType.CODE_GENERATION
        }
    
    def is_ready(self) -> bool:
        """检查桥接器是否就绪"""
        return (self.adapter is not None and 
                self.protocol_handler is not None and 
                len(self._capability_mapping) > 0)
    
    def get_mapped_capabilities(self) -> List[A2ACapability]:
        """获取映射后的A2A能力列表"""
        capabilities = []
        adapter_info = self.adapter.get_info()
        
        for adapter_cap in adapter_info.capabilities:
            if adapter_cap in self._capability_mapping:
                cap_type = self._capability_mapping[adapter_cap]
                capabilities.append(A2ACapability(
                    capability_type=cap_type,
                    version="1.0",
                    description=f"Mapped from {adapter_cap}",
                    input_formats=["text", "json"],
                    output_formats=["text", "json"]
                ))
        
        return capabilities
    
    async def execute_task(self, message: A2AMessage) -> Optional[A2AMessage]:
        """执行任务并返回A2A消息"""
        try:
            # 映射任务类型
            task_type = self._task_type_mapping.get(
                message.message_type, 
                TaskType.CONVERSATION
            )
            
            # 创建通用任务
            task = UniversalTask(
                content=message.payload.get("content", ""),
                task_type=task_type,
                context=message.payload.get("parameters", {}),
                task_id=message.message_id
            )
            
            # 创建上下文
            context = UniversalContext({
                "sender_id": message.sender_id,
                "correlation_id": message.correlation_id
            })
            
            # 执行任务
            result = await self.adapter.execute_task(task, context)
            
            # 创建响应消息
            response = A2AMessage(
                message_id=str(uuid.uuid4()),
                protocol_version=message.protocol_version,
                message_type=A2AMessageType.TASK_RESPONSE,
                sender_id=self.protocol_handler.agent_profile.agent_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now(),
                correlation_id=message.message_id,
                payload={
                    "reply": result.content.get("reply", ""),
                    "status": "success" if result.status == ResultStatus.SUCCESS else "error",
                    "result_type": result.result_type.value if result.result_type else None
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute task: {e}")
            return self._create_error_response(message, str(e))
    
    def _create_error_response(self, original_message: A2AMessage, error: str) -> A2AMessage:
        """创建错误响应消息"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            protocol_version=original_message.protocol_version,
            message_type=A2AMessageType.ERROR_REPORT,
            sender_id=self.protocol_handler.agent_profile.agent_id,
            receiver_id=original_message.sender_id,
            timestamp=datetime.now(),
            correlation_id=original_message.message_id,
            payload={
                "error_type": "execution_error",
                "error_message": error,
                "original_message_id": original_message.message_id
            }
        )


class A2AMessageRouter:
    """A2A消息路由器"""
    
    def __init__(self):
        self.handlers: Dict[A2AMessageType, Callable] = {}
        self.routes: Dict[str, str] = {}  # agent_id -> endpoint
    
    def register_handler(self, message_type: A2AMessageType, handler: Callable):
        """注册消息处理器"""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type.value}")
    
    def register_route(self, agent_id: str, endpoint: str):
        """注册路由"""
        self.routes[agent_id] = endpoint
        logger.info(f"Registered route for agent {agent_id} -> {endpoint}")
    
    async def route_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """路由消息到对应的处理器"""
        try:
            handler = self.handlers.get(message.message_type)
            if handler:
                return await handler(message)
            
            logger.warning(f"No handler for message type: {message.message_type.value}")
            return None
                
        except Exception as e:
            logger.error(f"Failed to route message: {e}")
            return None
    
    def get_endpoint(self, agent_id: str) -> Optional[str]:
        """获取Agent的endpoint"""
        return self.routes.get(agent_id)


class A2AIntegrationManager:
    """A2A集成管理器"""
    
    def __init__(self):
        self.adapter_bridges: Dict[str, A2AAdapterBridge] = {}
        self.message_router: Optional[A2AMessageRouter] = None
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        self._health_status = True
        self._authorized_agents: Set[str] = set()
    
    def register_adapter_bridge(self, bridge: A2AAdapterBridge):
        """注册适配器桥接器"""
        agent_id = bridge.protocol_handler.agent_profile.agent_id
        self.adapter_bridges[agent_id] = bridge
        self._authorized_agents.add(agent_id)
        logger.info(f"Registered adapter bridge for agent: {agent_id}")
    
    def register_message_router(self, router: A2AMessageRouter):
        """注册消息路由器"""
        self.message_router = router
        logger.info("Registered message router")
    
    async def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理A2A消息"""
        try:
            # 验证消息
            validation_result = self._validate_message(message)
            if validation_result != "valid":
                return self._create_validation_error(message, validation_result)
            
            # 查找目标桥接器
            bridge = self.adapter_bridges.get(message.receiver_id)
            if not bridge:
                return self._create_routing_error(message)
            
            # 处理协作消息
            if message.message_type == A2AMessageType.COLLABORATION_INVITE:
                return await self._handle_collaboration(message)
            
            # 执行任务
            return await bridge.execute_task(message)
            
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
            return self._create_system_error(message, str(e))
    
    def _validate_message(self, message: A2AMessage) -> str:
        """验证消息，返回验证结果"""
        # 检查发送者授权
        if message.sender_id not in self._authorized_agents:
            return "unauthorized"
        
        # 检查接收者
        if not message.receiver_id:
            return "invalid_receiver"
        
        # 检查消息类型
        if not isinstance(message.message_type, A2AMessageType):
            return "invalid_type"
        
        # 检查签名（如果有）
        if message.signature and not self._verify_signature(message):
            return "integrity_error"
        
        return "valid"
    
    def _verify_signature(self, message: A2AMessage) -> bool:
        """验证消息签名"""
        # TODO: 实现签名验证
        return False  # 暂时返回False以触发安全检查
    
    async def _handle_collaboration(self, message: A2AMessage) -> A2AMessage:
        """处理协作消息"""
        try:
            collaboration_id = message.payload.get("collaboration_id", str(uuid.uuid4()))
            
            # 记录协作
            self.active_collaborations[collaboration_id] = {
                "status": "active",
                "created_at": datetime.now(),
                "participants": message.payload.get("participants", []),
                "type": message.payload.get("collaboration_type"),
                "data": message.payload
            }
            
            # 创建接受响应
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                protocol_version=message.protocol_version,
                message_type=A2AMessageType.COLLABORATION_ACCEPT,
                sender_id=message.receiver_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now(),
                correlation_id=message.message_id,
                payload={
                    "collaboration_id": collaboration_id,
                    "status": "accepted",
                    "capabilities": self.adapter_bridges[message.receiver_id]
                                  .get_mapped_capabilities()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle collaboration: {e}")
            return self._create_system_error(message, str(e))
    
    def get_active_collaboration(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """获取活动协作的信息"""
        return self.active_collaborations.get(collaboration_id)
    
    def is_healthy(self) -> bool:
        """检查系统健康状态"""
        return self._health_status
    
    def _create_validation_error(self, message: A2AMessage, error_type: str) -> A2AMessage:
        """创建验证错误响应"""
        error_messages = {
            "unauthorized": "Unauthorized sender",
            "invalid_receiver": "Invalid receiver",
            "invalid_type": "Invalid message type",
            "integrity_error": "Message integrity check failed"
        }
        
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            protocol_version=message.protocol_version,
            message_type=A2AMessageType.ERROR_REPORT,
            sender_id=next(iter(self.adapter_bridges.keys()), "system"),
            receiver_id=message.sender_id,
            timestamp=datetime.now(),
            correlation_id=message.message_id,
            payload={
                "error_type": error_type,
                "error_message": error_messages.get(error_type, "Validation error"),
                "original_message_id": message.message_id
            }
        )
    
    def _create_routing_error(self, message: A2AMessage) -> A2AMessage:
        """创建路由错误响应"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            protocol_version=message.protocol_version,
            message_type=A2AMessageType.ERROR_REPORT,
            sender_id=next(iter(self.adapter_bridges.keys()), "system"),
            receiver_id=message.sender_id,
            timestamp=datetime.now(),
            correlation_id=message.message_id,
            payload={
                "error_type": "routing_error",
                "error_message": f"No route to agent: {message.receiver_id}",
                "original_message_id": message.message_id
            }
        )
    
    def _create_system_error(self, message: A2AMessage, error: str) -> A2AMessage:
        """创建系统错误响应"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            protocol_version=message.protocol_version,
            message_type=A2AMessageType.ERROR_REPORT,
            sender_id=next(iter(self.adapter_bridges.keys()), "system"),
            receiver_id=message.sender_id,
            timestamp=datetime.now(),
            correlation_id=message.message_id,
            payload={
                "error_type": "system_error",
                "error_message": error,
                "original_message_id": message.message_id
            }
        ) 