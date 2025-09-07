"""
AutoGen适配器 - 简化版本
与ADC 8层架构和A2A协议集成的AutoGen框架适配器

这个版本专注于核心功能，与现有的BaseAdapter接口兼容
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# AutoGen导入
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("AutoGen not available. Install with: pip install pyautogen")

# ADC架构导入
from ...framework.abstractions.task import UniversalTask, TaskType
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult
# A2A协议相关导入已移除，专注于核心AutoGen功能
from ..base import BaseAdapter, AdapterCapability, AdapterError, AdapterInitializationError

logger = logging.getLogger(__name__)


class AutoGenAgent:
    """AutoGen Agent包装器"""
    
    def __init__(self, agent_id: str, autogen_agent, adapter):
        self.agent_id = agent_id
        self.autogen_agent = autogen_agent
        self.adapter = adapter
    
    async def execute_task(self, task: str) -> str:
        """执行任务"""
        try:
            if hasattr(self.autogen_agent, 'generate_reply'):
                messages = [{"content": task, "role": "user"}]
                reply = await asyncio.to_thread(
                    self.autogen_agent.generate_reply,
                    messages=messages
                )
                return str(reply)
            else:
                return f"Agent {self.agent_id} received task: {task}"
        except Exception as e:
            logger.error(f"Error executing task in agent {self.agent_id}: {e}")
            return f"Error: {str(e)}"


class AutoGenTeam:
    """AutoGen团队包装器"""
    
    def __init__(self, team_id: str, agents: List[AutoGenAgent]):
        self.team_id = team_id
        self.agents = {agent.agent_id: agent for agent in agents}
        self.group_chat = None
        self.group_chat_manager = None
        
        # 创建GroupChat
        if len(agents) >= 2:
            autogen_agents = [agent.autogen_agent for agent in agents]
            self.group_chat = GroupChat(
                agents=autogen_agents,
                messages=[],
                max_round=10
            )
            self.group_chat_manager = GroupChatManager(
                groupchat=self.group_chat,
                name="GroupChatManager"
            )
    
    async def execute_collaboration(self, initial_message: str) -> Dict[str, Any]:
        """执行团队协作"""
        try:
            if not self.group_chat_manager:
                return {
                    "team_id": self.team_id,
                    "status": "error",
                    "error": "GroupChat not available"
                }
            
            # 选择第一个agent作为发起者
            first_agent = list(self.agents.values())[0].autogen_agent
            
            # 启动对话
            chat_result = await asyncio.to_thread(
                first_agent.initiate_chat,
                self.group_chat_manager,
                message=initial_message,
                max_turns=5
            )
            
            return {
                "team_id": self.team_id,
                "status": "completed",
                "participants": list(self.agents.keys()),
                "messages": len(self.group_chat.messages) if self.group_chat else 0,
                "chat_result": str(chat_result)
            }
            
        except Exception as e:
            logger.error(f"Error in team collaboration: {e}")
            return {
                "team_id": self.team_id,
                "status": "error", 
                "error": str(e)
            }


class AutoGenAdapterSimple(BaseAdapter):
    """
    AutoGen适配器 - 简化版本
    
    与BaseAdapter接口兼容，支持基本的AutoGen功能和A2A协议集成
    """
    
    def __init__(self, name: str = "autogen_simple"):
        super().__init__(name)
        
        if not AUTOGEN_AVAILABLE:
            raise AdapterInitializationError("AutoGen is not available. Please install: pip install pyautogen")
        
        self.agents: Dict[str, AutoGenAgent] = {}
        self.teams: Dict[str, AutoGenTeam] = {}
        self.llm_configs: Dict[str, Dict[str, Any]] = {}
        
        # A2A功能已移除，专注于核心AutoGen功能
        
        logger.info("AutoGen simple adapter initialized")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化适配器"""
        try:
            self.config = config
            
            # 配置默认LLM
            default_llm = config.get('default_llm', {})
            if default_llm:
                self.llm_configs['default'] = default_llm
            
            self.is_initialized = True
            self.status = self.status.READY
            self.metadata.last_initialized = datetime.now()
            self.metadata.initialization_count += 1
            
            logger.info(f"AutoGen adapter {self.name} initialized successfully")
            
        except Exception as e:
            self.status = self.status.ERROR
            logger.error(f"Failed to initialize AutoGen adapter: {e}")
            raise AdapterInitializationError(f"Initialization failed: {str(e)}")
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """创建Agent"""
        try:
            agent_id = agent_config.get('agent_id', f"agent_{len(self.agents)}")
            agent_type = agent_config.get('type', 'assistant')
            name = agent_config.get('name', agent_id)
            
            if agent_type == 'assistant':
                system_message = agent_config.get('system_message', 'You are a helpful assistant.')
                llm_config = agent_config.get('llm_config', self.llm_configs.get('default', {}))
                
                autogen_agent = AssistantAgent(
                    name=name,
                    system_message=system_message,
                    llm_config=llm_config
                )
                
            elif agent_type == 'user_proxy':
                autogen_agent = UserProxyAgent(
                    name=name,
                    human_input_mode="NEVER",
                    max_consecutive_auto_reply=10,
                    code_execution_config=agent_config.get('code_execution_config', {})
                )
                
            else:
                raise ValueError(f"Unsupported agent type: {agent_type}")
            
            # 包装Agent
            agent_wrapper = AutoGenAgent(agent_id, autogen_agent, self)
            self.agents[agent_id] = agent_wrapper
            
            self.metadata.successful_operations += 1
            logger.info(f"Created AutoGen agent: {agent_id} ({agent_type})")
            return agent_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create agent: {e}")
            raise AdapterExecutionError(f"Agent creation failed: {str(e)}")
    
    async def create_team(self, team_config: Dict[str, Any]) -> str:
        """创建团队"""
        try:
            team_id = team_config.get('team_id', f"team_{len(self.teams)}")
            agent_ids = team_config.get('agent_ids', [])
            
            # 获取agents
            team_agents = []
            for agent_id in agent_ids:
                if agent_id in self.agents:
                    team_agents.append(self.agents[agent_id])
                else:
                    logger.warning(f"Agent {agent_id} not found for team {team_id}")
            
            if len(team_agents) < 2:
                raise ValueError("Team requires at least 2 agents")
            
            # 创建团队
            team = AutoGenTeam(team_id, team_agents)
            self.teams[team_id] = team
            
            self.metadata.successful_operations += 1
            logger.info(f"Created AutoGen team: {team_id} with {len(team_agents)} agents")
            return team_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create team: {e}")
            raise AdapterExecutionError(f"Team creation failed: {str(e)}")
    
    def get_capabilities(self) -> List[AdapterCapability]:
        """获取适配器能力"""
        return [
            AdapterCapability.CONVERSATION,
            AdapterCapability.CODE_GENERATION,
            AdapterCapability.CODE_EXECUTION,
            AdapterCapability.TEAM_COLLABORATION
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            status = {
                "adapter_name": self.name,
                "status": self.status.value,
                "initialized": self.is_initialized,
                "autogen_available": AUTOGEN_AVAILABLE,
                "agents_count": len(self.agents),
                "teams_count": len(self.teams),
                "success_rate": self.metadata.success_rate,
                "timestamp": datetime.now().isoformat()
            }
            
            # 测试基本功能
            if AUTOGEN_AVAILABLE and self.is_initialized:
                status["health"] = "healthy"
            else:
                status["health"] = "unhealthy"
                status["issues"] = []
                if not AUTOGEN_AVAILABLE:
                    status["issues"].append("AutoGen not available")
                if not self.is_initialized:
                    status["issues"].append("Not initialized")
            
            return status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "adapter_name": self.name,
                "health": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务"""
        try:
            if not self.is_ready():
                raise AdapterError("Adapter not ready")
            
            task_type = task.task_type
            task_content = task.content
            
            if task_type == TaskType.CHAT:
                return await self._execute_chat_task(task_content, context)
            elif task_type == TaskType.CODE_GENERATION:
                return await self._execute_code_task(task_content, context)
            elif task_type == TaskType.COLLABORATION:
                return await self._execute_collaboration_task(task_content, context)
            else:
                return await self._execute_generic_task(task_content, context)
                
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Task execution failed: {e}")
            return UniversalResult(
                success=False,
                data={},
                error=str(e),
                metadata={"adapter": self.name, "task_type": task.task_type.name}
            )
    
    async def _execute_chat_task(self, task_content: str, context: UniversalContext) -> UniversalResult:
        """执行聊天任务"""
        if not self.agents:
            raise AdapterError("No agents available")
        
        # 选择第一个可用agent
        agent = list(self.agents.values())[0]
        result = await agent.execute_task(task_content)
        
        self.metadata.successful_operations += 1
        return UniversalResult(
            success=True,
            data={
                "reply": result,
                "agent_id": agent.agent_id,
                "agent_type": "autogen_agent"
            },
            metadata={"adapter": self.name, "task_type": "chat"}
        )
    
    async def _execute_code_task(self, task_content: str, context: UniversalContext) -> UniversalResult:
        """执行代码任务"""
        # 查找UserProxyAgent
        code_agent = None
        for agent in self.agents.values():
            if isinstance(agent.autogen_agent, UserProxyAgent):
                code_agent = agent
                break
        
        if not code_agent:
            raise AdapterError("No UserProxyAgent available for code execution")
        
        result = await code_agent.execute_task(f"Code task: {task_content}")
        
        self.metadata.successful_operations += 1
        return UniversalResult(
            success=True,
            data={
                "code_result": result,
                "agent_id": code_agent.agent_id
            },
            metadata={"adapter": self.name, "task_type": "code"}
        )
    
    async def _execute_collaboration_task(self, task_content: str, context: UniversalContext) -> UniversalResult:
        """执行协作任务"""
        if not self.teams:
            raise AdapterError("No teams available for collaboration")
        
        # 选择第一个可用团队
        team = list(self.teams.values())[0]
        result = await team.execute_collaboration(task_content)
        
        self.metadata.successful_operations += 1
        return UniversalResult(
            success=True,
            data=result,
            metadata={"adapter": self.name, "task_type": "collaboration"}
        )
    
    async def _execute_generic_task(self, task_content: str, context: UniversalContext) -> UniversalResult:
        """执行通用任务"""
        if not self.agents:
            raise AdapterError("No agents available")
        
        # 选择第一个可用agent
        agent = list(self.agents.values())[0]
        result = await agent.execute_task(task_content)
        
        self.metadata.successful_operations += 1
        return UniversalResult(
            success=True,
            data={
                "result": result,
                "agent_id": agent.agent_id
            },
            metadata={"adapter": self.name, "task_type": "generic"}
        )
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """获取Agent状态"""
        if agent_id not in self.agents:
            return {"status": "not_found"}
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "agent_type": type(agent.autogen_agent).__name__,
            "a2a_profile": agent.a2a_profile.to_dict(),
            "status": "active"
        }
    
    def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """获取团队状态"""
        if team_id not in self.teams:
            return {"status": "not_found"}
        
        team = self.teams[team_id]
        return {
            "team_id": team_id,
            "agents": list(team.agents.keys()),
            "agent_count": len(team.agents),
            "has_group_chat": team.group_chat is not None,
            "status": "active"
        } 