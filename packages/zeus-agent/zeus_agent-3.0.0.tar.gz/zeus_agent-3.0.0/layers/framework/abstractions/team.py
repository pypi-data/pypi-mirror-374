"""
Team Collaboration Abstraction - 团队协作抽象
支持AutoGen的团队协作功能：RoundRobin、Selector、Swarm等模式
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .agent import UniversalAgent, AgentCapability
from .task import UniversalTask, TaskType
from .context import UniversalContext, TeamContext
from .result import UniversalResult, ResultStatus, ResultType, ResultMetadata, ErrorInfo


class TeamType(Enum):
    """团队类型枚举"""
    ROUND_ROBIN = "round_robin"
    SELECTOR = "selector"
    SWARM = "swarm"
    SEQUENTIAL = "sequential"
    COLLABORATIVE = "collaborative"


class CommunicationPattern(Enum):
    """通信模式枚举"""
    BROADCAST = "broadcast"  # 广播模式
    HIERARCHICAL = "hierarchical"  # 层次模式
    PEER_TO_PEER = "peer_to_peer"  # 点对点模式
    ROUND_ROBIN = "round_robin"  # 轮询模式


@dataclass
class TeamConfig:
    """团队配置"""
    name: str
    type: TeamType
    agents: List[Dict[str, Any]]  # Agent配置列表
    workflow: Dict[str, Any] = field(default_factory=dict)
    communication_pattern: CommunicationPattern = CommunicationPattern.ROUND_ROBIN
    termination_conditions: List[Dict[str, Any]] = field(default_factory=list)
    max_rounds: int = 10
    timeout: int = 300  # 秒


@dataclass
class TeamStatus:
    """团队状态"""
    name: str
    type: TeamType
    agent_count: int
    current_round: int
    total_conversations: int
    last_activity: Optional[datetime] = None
    status: str = "idle"  # idle, busy, completed, error


@dataclass
class TerminationCondition:
    """终止条件"""
    type: str  # max_rounds, consensus, timeout, manual
    value: Any
    description: str = ""


class UniversalTeam(ABC):
    """
    通用团队抽象
    
    支持AutoGen的团队协作功能：
    - 多Agent协作
    - 不同的通信模式
    - 工作流管理
    - 状态跟踪
    """
    
    def __init__(self, config: TeamConfig):
        self.config = config
        self.agents = []
        self.status = "idle"
        self.conversation_history = []
        self.current_round = 0
        self.start_time = None
    
    @abstractmethod
    async def execute_task(self, task: UniversalTask, context: Optional[TeamContext] = None) -> UniversalResult:
        """
        执行团队任务
        
        Args:
            task: 任务描述
            context: 团队上下文
            
        Returns:
            TeamResult: 团队执行结果
        """
        pass
    
    @abstractmethod
    async def add_agent(self, agent: UniversalAgent) -> None:
        """
        添加Agent到团队
        
        Args:
            agent: 要添加的Agent
        """
        pass
    
    @abstractmethod
    async def remove_agent(self, agent_name: str) -> None:
        """
        从团队移除Agent
        
        Args:
            agent_name: Agent名称
        """
        pass
    
    @abstractmethod
    async def get_team_status(self) -> TeamStatus:
        """
        获取团队状态
        
        Returns:
            TeamStatus: 团队状态
        """
        pass
    
    async def initialize_agents(self, agent_factory) -> None:
        """
        初始化团队中的Agent
        
        Args:
            agent_factory: Agent工厂
        """
        for agent_config in self.config.agents:
            agent = await agent_factory.create_agent(agent_config)
            await self.add_agent(agent)
    
    def _create_team_context(self, task: str) -> TeamContext:
        """创建团队上下文"""
        return TeamContext(
            team_name=self.config.name,
            current_round=self.current_round,
            participants=[agent.name for agent in self.agents],
            conversation_history=self.conversation_history.copy(),
            shared_state={},
            timestamp=datetime.now()
        )
    
    def _update_team_status(self, status: str) -> None:
        """更新团队状态"""
        self.status = status
        if status == "busy" and self.start_time is None:
            self.start_time = datetime.now()
    
    def _record_conversation(self, speaker: str, message: str, round_num: int) -> None:
        """记录对话"""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "round": round_num,
            "timestamp": datetime.now().isoformat()
        })
    
    def _check_termination_conditions(self, context: TeamContext) -> bool:
        """检查终止条件"""
        for condition in self.config.termination_conditions:
            condition_type = condition.get("type")
            
            if condition_type == "max_rounds":
                if context.current_round >= condition.get("value", self.config.max_rounds):
                    return True
            elif condition_type == "timeout":
                if self.start_time and (datetime.now() - self.start_time).seconds > condition.get("value", self.config.timeout):
                    return True
            elif condition_type == "consensus":
                # 检查是否达成共识
                pass
            elif condition_type == "manual":
                # 手动终止
                pass
        
        return False
    
    def _create_execution_context(self, task: UniversalTask, context: TeamContext, agent_name: str) -> Dict[str, Any]:
        """创建执行上下文"""
        return {
            "team_name": self.config.name,
            "current_agent": agent_name,
            "current_round": context.current_round,
            "total_agents": len(self.agents),
            "conversation_history": context.conversation_history,
            "shared_state": context.shared_state,
            "task_type": task.task_type.value,
            "task_content": task.content,
            "timestamp": datetime.now().isoformat()
        }


class RoundRobinTeam(UniversalTeam):
    """轮询团队实现"""
    
    def __init__(self, config: TeamConfig):
        super().__init__(config)
        self.current_agent_index = 0
        self.total_rounds = 0
    
    async def execute_task(self, task: UniversalTask, context: Optional[TeamContext] = None) -> UniversalResult:
        """执行轮询团队任务"""
        if context is None:
            context = self._create_team_context(task.content)
        
        self._update_team_status("busy")
        start_time = datetime.now()
        
        try:
            current_message = task.content
            final_response = ""
            error_info = None
            
            for round_num in range(self.config.max_rounds):
                context.current_round = round_num
                self.current_round = round_num
                
                # 选择当前Agent
                current_agent = self.agents[self.current_agent_index]
                
                # 创建执行上下文
                exec_context = UniversalContext(self._create_execution_context(task, context, current_agent.name))
                
                # 执行任务
                result = await current_agent.execute(task, exec_context)
                
                if result.is_successful():
                    response = result.content.get("response", "")
                    final_response = response
                    
                    # 记录对话
                    self._record_conversation(current_agent.name, response, round_num)
                    
                    # 更新消息
                    current_message = response
                    
                    # 移动到下一个Agent
                    self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
                    
                    # 检查终止条件
                    if self._check_termination_conditions(context):
                        break
                else:
                    # 处理错误
                    error_msg = result.error.get("message", "Unknown error") if result.error else "Unknown error"
                    final_response = f"Error from {current_agent.name}: {error_msg}"
                    error_info = ErrorInfo(
                        error_type="agent_error",
                        error_message=error_msg
                    )
                    break
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("completed")
            self.total_rounds += 1
            
            return UniversalResult(
                content={"response": final_response},
                status=ResultStatus.SUCCESS if not final_response.startswith("Error") else ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={
                        "team_type": self.config.type.value,
                        "communication_pattern": self.config.communication_pattern.value
                    }
                ),
                error=error_info
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("error")
            
            return UniversalResult(
                content={},
                status=ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={"error": str(e)}
                ),
                error=ErrorInfo(
                    error_type="execution_error",
                    error_message=str(e)
                )
            )
    
    async def add_agent(self, agent: UniversalAgent) -> None:
        """添加Agent"""
        self.agents.append(agent)
    
    async def remove_agent(self, agent_name: str) -> None:
        """移除Agent"""
        self.agents = [agent for agent in self.agents if agent.name != agent_name]
        # 调整当前索引
        if self.current_agent_index >= len(self.agents):
            self.current_agent_index = 0
    
    async def get_team_status(self) -> TeamStatus:
        """获取团队状态"""
        return TeamStatus(
            name=self.config.name,
            type=self.config.type,
            agent_count=len(self.agents),
            current_round=self.current_round,
            total_conversations=self.total_rounds,
            last_activity=datetime.now() if self.conversation_history else None,
            status=self.status
        )


class SelectorTeam(UniversalTeam):
    """选择器团队实现"""
    
    def __init__(self, config: TeamConfig):
        super().__init__(config)
        self.selector_agent = None  # 负责选择Agent的智能体
        self.total_rounds = 0
    
    async def execute_task(self, task: UniversalTask, context: Optional[TeamContext] = None) -> UniversalResult:
        """执行选择器团队任务"""
        if context is None:
            context = self._create_team_context(task.content)
        
        self._update_team_status("busy")
        start_time = datetime.now()
        
        try:
            current_message = task.content
            final_response = ""
            selected_agents = []
            error_info = None
            
            for round_num in range(self.config.max_rounds):
                context.current_round = round_num
                self.current_round = round_num
                
                # 使用选择器Agent选择最合适的Agent
                selected_agent = await self._select_best_agent(task, context)
                if selected_agent:
                    selected_agents.append(selected_agent.name)
                    
                    # 创建执行上下文
                    exec_context = UniversalContext(self._create_execution_context(task, context, selected_agent.name))
                    
                    # 执行任务
                    result = await selected_agent.execute(task, exec_context)
                    
                    if result.is_successful():
                        response = result.content.get("response", "")
                        final_response = response
                        
                        # 记录对话
                        self._record_conversation(selected_agent.name, response, round_num)
                        
                        # 更新消息
                        current_message = response
                        
                        # 检查终止条件
                        if self._check_termination_conditions(context):
                            break
                    else:
                        error_msg = result.error.get("message", "Unknown error") if result.error else "Unknown error"
                        final_response = f"Error from {selected_agent.name}: {error_msg}"
                        error_info = ErrorInfo(
                            error_type="agent_error",
                            error_message=error_msg
                        )
                        break
                else:
                    final_response = "No suitable agent found for the task"
                    error_info = ErrorInfo(
                        error_type="selection_error",
                        error_message="No suitable agent found for the task"
                    )
                    break
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("completed")
            self.total_rounds += 1
            
            return UniversalResult(
                content={"response": final_response},
                status=ResultStatus.SUCCESS if not final_response.startswith(("Error", "No suitable")) else ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={
                        "team_type": self.config.type.value,
                        "communication_pattern": self.config.communication_pattern.value,
                        "selected_agents": selected_agents
                    }
                ),
                error=error_info
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("error")
            
            return UniversalResult(
                content={},
                status=ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={"error": str(e)}
                ),
                error=ErrorInfo(
                    error_type="execution_error",
                    error_message=str(e)
                )
            )
    
    async def _select_best_agent(self, task: UniversalTask, context: TeamContext) -> Optional[UniversalAgent]:
        """选择最合适的Agent"""
        if not self.agents:
            return None
        
        # 根据任务类型选择Agent
        task_type = task.task_type
        
        for agent in self.agents:
            # 检查Agent的能力是否匹配任务
            if task_type == TaskType.CODE_GENERATION and AgentCapability.CODE_GENERATION in agent.capabilities:
                return agent
            elif task_type == TaskType.WEB_SEARCH and AgentCapability.WEB_SEARCH in agent.capabilities:
                return agent
            elif task_type == TaskType.CONVERSATION and AgentCapability.CONVERSATION in agent.capabilities:
                return agent
        
        # 默认返回第一个Agent
        return self.agents[0] if self.agents else None
    
    async def add_agent(self, agent: UniversalAgent) -> None:
        """添加Agent"""
        self.agents.append(agent)
    
    async def remove_agent(self, agent_name: str) -> None:
        """移除Agent"""
        self.agents = [agent for agent in self.agents if agent.name != agent_name]
    
    async def get_team_status(self) -> TeamStatus:
        """获取团队状态"""
        return TeamStatus(
            name=self.config.name,
            type=self.config.type,
            agent_count=len(self.agents),
            current_round=self.current_round,
            total_conversations=self.total_rounds,
            last_activity=datetime.now() if self.conversation_history else None,
            status=self.status
        )


class SwarmTeam(UniversalTeam):
    """群体智能团队实现"""
    
    def __init__(self, config: TeamConfig):
        super().__init__(config)
        self.parallel_execution = True
        self.total_rounds = 0
    
    async def execute_task(self, task: UniversalTask, context: Optional[TeamContext] = None) -> UniversalResult:
        """执行群体智能团队任务"""
        if context is None:
            context = self._create_team_context(task.content)
        
        self._update_team_status("busy")
        start_time = datetime.now()
        
        try:
            # 并行执行所有Agent
            tasks = []
            for agent in self.agents:
                exec_context = UniversalContext(self._create_execution_context(task, context, agent.name))
                tasks.append(agent.execute(task, exec_context))
            
            # 等待所有Agent完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 收集和整合结果
            responses = []
            successful_agents = []
            error_info = None
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_msg = str(result)
                    responses.append(f"Error from {self.agents[i].name}: {error_msg}")
                    if error_info is None:
                        error_info = ErrorInfo(
                            error_type="execution_error",
                            error_message=error_msg
                        )
                else:
                    if result.is_successful():
                        response = result.content.get("response", "")
                        responses.append(f"{self.agents[i].name}: {response}")
                        successful_agents.append(self.agents[i].name)
                        self._record_conversation(self.agents[i].name, response, 0)
                    else:
                        error_msg = result.error.get("message", "Unknown error") if result.error else "Unknown error"
                        responses.append(f"Error from {self.agents[i].name}: {error_msg}")
                        if error_info is None:
                            error_info = ErrorInfo(
                                error_type="agent_error",
                                error_message=error_msg
                            )
            
            # 整合最终响应
            final_response = "\n\n".join(responses)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("completed")
            self.total_rounds += 1
            
            return UniversalResult(
                content={
                    "response": final_response,
                    "responses": responses
                },
                status=ResultStatus.SUCCESS if len(successful_agents) > 0 else ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={
                        "team_type": self.config.type.value,
                        "communication_pattern": self.config.communication_pattern.value,
                        "parallel_execution": True,
                        "successful_agents": successful_agents
                    }
                ),
                error=error_info
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_team_status("error")
            
            return UniversalResult(
                content={},
                status=ResultStatus.ERROR,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    execution_time=execution_time,
                    framework_info={"error": str(e)}
                ),
                error=ErrorInfo(
                    error_type="execution_error",
                    error_message=str(e)
                )
            )
    
    async def add_agent(self, agent: UniversalAgent) -> None:
        """添加Agent"""
        self.agents.append(agent)
    
    async def remove_agent(self, agent_name: str) -> None:
        """移除Agent"""
        self.agents = [agent for agent in self.agents if agent.name != agent_name]
    
    async def get_team_status(self) -> TeamStatus:
        """获取团队状态"""
        return TeamStatus(
            name=self.config.name,
            type=self.config.type,
            agent_count=len(self.agents),
            current_round=self.current_round,
            total_conversations=self.total_rounds,
            last_activity=datetime.now() if self.conversation_history else None,
            status=self.status
        ) 