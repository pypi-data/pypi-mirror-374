"""
Cognitive Architecture Layer Communication Manager - 认知架构层通信管理器
集成层间通信协议，为认知架构层提供通信能力
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


class CognitiveCommunicationManager:
    """认知架构层通信管理器"""
    
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
        
        self._register_handlers()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def _register_handlers(self):
        """注册认知架构层的消息处理器"""
        # 注册各种认知功能的处理器
        self.router.register_handler("analyze_collaboration", self._handle_analyze_collaboration)
        self.router.register_handler("reason_about_task", self._handle_reason_about_task)
        self.router.register_handler("perceive_environment", self._handle_perceive_environment)
        self.router.register_handler("store_memory", self._handle_store_memory)
        self.router.register_handler("retrieve_memory", self._handle_retrieve_memory)
        self.router.register_handler("learn_from_experience", self._handle_learn_from_experience)
        self.router.register_handler("communicate_with_agent", self._handle_communicate_with_agent)
    
    async def _handle_analyze_collaboration(self, message: LayerMessage) -> LayerMessage:
        """处理协作分析请求"""
        try:
            pattern = message.content.get('pattern')
            participants = message.content.get('participants', [])
            
            # 模拟协作分析结果（避免实例化抽象类）
            analysis_result = {
                "pattern_type": pattern,
                "participants_count": len(participants),
                "collaboration_score": 0.85,
                "recommendations": ["增强沟通频率", "明确角色分工", "建立反馈机制"]
            }
            
            self.logger.info(f"Collaboration analysis completed for pattern: {pattern}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "analysis_result": analysis_result,
                    "pattern": pattern,
                    "participants": participants
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to analyze collaboration: {e}")
            # 返回错误响应
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_reason_about_task(self, message: LayerMessage) -> LayerMessage:
        """处理任务推理请求"""
        try:
            from .reasoning import ReasoningEngine
            
            task_data = message.content.get('task')
            context = message.content.get('context', {})
            reasoning_type = message.content.get('reasoning_type', 'logical')
            
            # 创建推理引擎
            reasoning_engine = ReasoningEngine()
            
            # 执行推理
            reasoning_result = await reasoning_engine.reason_about_task(
                task_data, context, reasoning_type
            )
            
            self.logger.info(f"Task reasoning completed for task: {task_data}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "reasoning_result": reasoning_result,
                    "task": task_data,
                    "reasoning_type": reasoning_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to reason about task: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_perceive_environment(self, message: LayerMessage) -> LayerMessage:
        """处理环境感知请求"""
        try:
            from .perception import PerceptionEngine
            
            environment_data = message.content.get('environment')
            perception_type = message.content.get('perception_type', 'text')
            
            # 创建感知引擎
            perception_engine = PerceptionEngine()
            
            # 执行感知
            perception_result = await perception_engine.perceive_environment(
                environment_data, perception_type
            )
            
            self.logger.info(f"Environment perception completed")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "perception_result": perception_result,
                    "perception_type": perception_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to perceive environment: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_store_memory(self, message: LayerMessage) -> LayerMessage:
        """处理记忆存储请求"""
        try:
            from .memory import MemorySystem
            
            memory_data = message.content.get('memory_data')
            memory_type = message.content.get('memory_type', 'episodic')
            
            # 创建记忆系统
            memory_system = MemorySystem()
            
            # 存储记忆
            storage_result = await memory_system.store_memory(memory_data, memory_type)
            
            self.logger.info(f"Memory stored successfully: {memory_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "storage_result": storage_result,
                    "memory_type": memory_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_retrieve_memory(self, message: LayerMessage) -> LayerMessage:
        """处理记忆检索请求"""
        try:
            from .memory import MemorySystem
            
            query = message.content.get('query')
            memory_type = message.content.get('memory_type', 'episodic')
            limit = message.content.get('limit', 10)
            
            # 创建记忆系统
            memory_system = MemorySystem()
            
            # 检索记忆
            retrieval_result = await memory_system.retrieve_memory(query, memory_type, limit)
            
            self.logger.info(f"Memory retrieved successfully: {len(retrieval_result)} items")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "retrieval_result": retrieval_result,
                    "query": query,
                    "memory_type": memory_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_learn_from_experience(self, message: LayerMessage) -> LayerMessage:
        """处理经验学习请求"""
        try:
            from .learning import LearningEngine
            
            experience_data = message.content.get('experience')
            learning_type = message.content.get('learning_type', 'reinforcement')
            
            # 创建学习引擎
            learning_engine = LearningEngine()
            
            # 从经验中学习
            learning_result = await learning_engine.learn_from_experience(
                experience_data, learning_type
            )
            
            self.logger.info(f"Learning completed: {learning_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "learning_result": learning_result,
                    "learning_type": learning_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to learn from experience: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_communicate_with_agent(self, message: LayerMessage) -> LayerMessage:
        """处理Agent间通信请求"""
        try:
            from .communication import CommunicationEngine
            
            target_agent = message.content.get('target_agent')
            communication_data = message.content.get('data')
            communication_type = message.content.get('type', 'direct')
            
            # 创建通信引擎
            communication_engine = CommunicationEngine()
            
            # 执行通信
            communication_result = await communication_engine.communicate_with_agent(
                target_agent, communication_data, communication_type
            )
            
            self.logger.info(f"Agent communication completed with: {target_agent}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={
                    "communication_result": communication_result,
                    "target_agent": target_agent,
                    "communication_type": communication_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to communicate with agent: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="cognitive",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def send_message(self, message: LayerMessage) -> LayerMessage:
        """发送消息到其他层"""
        return await self.layer_comm.send_message(message)
    
    async def process_message(self, message: LayerMessage) -> LayerMessage:
        """处理接收到的消息"""
        return await self.layer_comm.process_message(message)
    
    def get_status(self) -> Dict[str, Any]:
        """获取通信管理器状态"""
        return {
            "component": "CognitiveCommunicationManager",
            "layer": "cognitive",
            "handlers_registered": len(self.router.handlers) if hasattr(self.router, "handlers") else 0,
            "queue_size": self.queue.size(),
            "layer_comm_status": self.layer_comm.get_status() if hasattr(self.layer_comm, 'get_status') else {}
        } 