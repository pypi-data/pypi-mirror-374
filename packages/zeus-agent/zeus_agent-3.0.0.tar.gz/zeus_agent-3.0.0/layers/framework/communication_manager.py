"""
Framework Abstraction Layer Communication Manager - 框架抽象层通信管理器
集成层间通信协议，为框架抽象层提供通信能力
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .abstractions.layer_communication import (
    LayerCommunicationManager,
    LayerRequest,
    LayerResponse,
    ExecutionContext,
    MessageType,
    LayerEventHandler
)

logger = logging.getLogger(__name__)


class FrameworkCommunicationManager:
    """框架抽象层通信管理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("framework")
        self._register_handlers()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def _register_handlers(self):
        """注册框架抽象层的请求处理器"""
        self.communicator.register_request_handler("get_agent_capabilities", self._handle_get_agent_capabilities)
        self.communicator.register_request_handler("create_agent", self._handle_create_agent)
        self.communicator.register_request_handler("create_team", self._handle_create_team)
        self.communicator.register_request_handler("execute_task", self._handle_execute_task)
        self.communicator.register_request_handler("get_agent_status", self._handle_get_agent_status)
        self.communicator.register_request_handler("list_agents", self._handle_list_agents)
        self.communicator.register_request_handler("get_team_status", self._handle_get_team_status)
    
    async def _handle_get_agent_capabilities(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理获取Agent能力请求"""
        from .abstractions.enhanced_factory import EnhancedAgentFactory
        
        agent_type = payload['parameters'].get('agent_type')
        
        try:
            factory = EnhancedAgentFactory()
            # 使用实际存在的方法
            capabilities = factory.get_capabilities_for_agent_type(agent_type)
            
            self.logger.info(f"Agent capabilities retrieved for type: {agent_type}")
            return {
                "agent_type": agent_type,
                "capabilities": capabilities,
                "capability_count": len(capabilities) if capabilities else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get agent capabilities for {agent_type}: {e}")
            # 返回默认能力列表
            default_capabilities = {
                "openai": ["conversation", "code_generation", "analysis"],
                "autogen": ["multi_agent_collaboration", "task_decomposition"],
                "custom": ["domain_specific", "custom_tools"]
            }
            capabilities = default_capabilities.get(agent_type, [])
            return {
                "agent_type": agent_type,
                "capabilities": capabilities,
                "capability_count": len(capabilities)
            }
    
    async def _handle_create_agent(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理创建Agent请求"""
        from .abstractions.enhanced_factory import EnhancedAgentFactory
        
        agent_config = payload['parameters']
        agent_type = agent_config.get('agent_type')
        agent_name = agent_config.get('name', f"Agent_{agent_type}")
        
        try:
            # 调用适配器层创建具体Agent实例
            adapter_request = LayerRequest(
                operation="create_agent_instance",
                parameters={
                    "adapter_type": agent_type,
                    "agent_config": agent_config
                }
            )
            
            response = await self.communicator.send_request(
                "adapter",
                adapter_request,
                context
            )
            
            if not response.success:
                raise Exception(f"Failed to create agent instance: {response.error}")
            
            # 创建框架抽象层的Agent对象
            factory = EnhancedAgentFactory()
            agent = factory.create_agent(agent_config)
            
            agent_id = response.data['agent_id']
            
            self.logger.info(f"Agent created: {agent_id} ({agent_name})")
            
            # 发布Agent创建事件
            await self.communicator.publish_event(
                "framework_agent_created",
                {
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "agent_type": agent_type,
                    "agent_config": agent_config
                },
                context
            )
            
            return {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "agent_type": agent_type,
                "status": "created",
                "framework_agent": str(agent)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            raise
    
    async def _handle_create_team(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理创建团队请求"""
        from .abstractions.enhanced_factory import EnhancedAgentFactory
        
        team_config = payload['parameters']
        team_name = team_config.get('name', 'Unnamed Team')
        
        try:
            factory = EnhancedAgentFactory()
            team = factory.create_team(team_config)
            
            team_id = f"team_{int(datetime.now().timestamp())}"
            
            self.logger.info(f"Team created: {team_id} ({team_name})")
            
            # 发布团队创建事件
            await self.communicator.publish_event(
                "framework_team_created",
                {
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_config": team_config,
                    "member_count": len(team_config.get('members', []))
                },
                context
            )
            
            return {
                "team_id": team_id,
                "team_name": team_name,
                "status": "created",
                "framework_team": str(team),
                "member_count": len(team_config.get('members', []))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create team: {e}")
            raise
    
    async def _handle_execute_task(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理执行任务请求"""
        from .abstractions.task import UniversalTask, TaskType
        from .abstractions.enhanced_agent import EnhancedUniversalAgent
        
        task_description = payload['parameters'].get('task_description')
        agent_id = payload['parameters'].get('agent_id')
        task_parameters = payload['parameters'].get('task_parameters', {})
        
        try:
            # 创建任务对象
            task = UniversalTask(
                task_id=f"task_{int(datetime.now().timestamp())}",
                description=task_description,
                task_type=TaskType.GENERAL,
                parameters=task_parameters
            )
            
            # 这里应该从Agent注册表中获取Agent实例
            # 暂时模拟Agent执行
            start_time = datetime.now()
            
            # 调用适配器层执行具体任务
            adapter_request = LayerRequest(
                operation="execute_task",
                parameters={
                    "adapter_type": "openai",  # 默认使用OpenAI适配器
                    "task_description": task_description,
                    "task_parameters": task_parameters
                }
            )
            
            response = await self.communicator.send_request(
                "adapter",
                adapter_request,
                context
            )
            
            if not response.success:
                raise Exception(f"Failed to execute task: {response.error}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Task executed by agent {agent_id}: {task_description}")
            
            # 发布任务执行完成事件
            await self.communicator.publish_event(
                "framework_task_executed",
                {
                    "task_id": task.task_id,
                    "agent_id": agent_id,
                    "task_description": task_description,
                    "execution_time": execution_time,
                    "result": response.data
                },
                context
            )
            
            return {
                "task_id": task.task_id,
                "agent_id": agent_id,
                "result": response.data,
                "execution_time": execution_time,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute task: {e}")
            raise
    
    async def _handle_get_agent_status(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理获取Agent状态请求"""
        agent_id = payload['parameters'].get('agent_id')
        
        try:
            # 这里应该从Agent注册表中获取Agent状态
            # 暂时返回模拟状态
            status = {
                "agent_id": agent_id,
                "status": "active",
                "last_activity": datetime.now().isoformat(),
                "task_count": 0,
                "capabilities": ["conversation", "task_execution"]
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get agent status for {agent_id}: {e}")
            raise
    
    async def _handle_list_agents(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理列出Agent请求"""
        try:
            # 这里应该从Agent注册表中获取所有Agent
            # 暂时返回模拟数据
            agents = [
                {
                    "agent_id": "agent_openai_001",
                    "agent_name": "OpenAI Assistant",
                    "agent_type": "openai",
                    "status": "active"
                },
                {
                    "agent_id": "agent_autogen_001",
                    "agent_name": "AutoGen Agent",
                    "agent_type": "autogen",
                    "status": "active"
                }
            ]
            
            return {
                "agents": agents,
                "total_count": len(agents)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list agents: {e}")
            raise
    
    async def _handle_get_team_status(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理获取团队状态请求"""
        team_id = payload['parameters'].get('team_id')
        
        try:
            # 这里应该从团队注册表中获取团队状态
            # 暂时返回模拟状态
            status = {
                "team_id": team_id,
                "status": "active",
                "member_count": 3,
                "current_task": None,
                "collaboration_pattern": "round_robin",
                "last_activity": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get team status for {team_id}: {e}")
            raise
    
    async def send_request_to_layer(self, target_layer: str, operation: str, parameters: Dict[str, Any], context: ExecutionContext) -> LayerResponse:
        """向其他层发送请求"""
        request = LayerRequest(operation=operation, parameters=parameters)
        return await self.communicator.send_request(target_layer, request, context)
    
    async def publish_framework_event(self, event_type: str, event_data: Dict[str, Any], context: ExecutionContext) -> None:
        """发布框架抽象层事件"""
        await self.communicator.publish_event(event_type, event_data, context)
    
    def subscribe_to_events(self, event_type: str, handler: LayerEventHandler) -> None:
        """订阅事件"""
        self.communicator.subscribe_to_events(event_type, handler)


# 全局框架抽象层通信管理器实例
framework_communication_manager = FrameworkCommunicationManager() 