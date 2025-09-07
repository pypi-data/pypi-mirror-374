"""
Team Tests
测试团队协作组件的功能
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any, List

from layers.framework.abstractions.team import (
    UniversalTeam,
    TeamConfig,
    TeamType,
    CommunicationPattern,
    RoundRobinTeam,
    SelectorTeam,
    SwarmTeam
)
from layers.framework.abstractions.cognitive_agent import (
    CognitiveUniversalAgent,
    AgentType,
    ModelConfig,
    ToolConfig,
    MemoryConfig,
    BehaviorConfig,
    AgentConfig
)
from layers.framework.abstractions.agent import AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext, TeamContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus, ResultMetadata


class TestAgent(CognitiveUniversalAgent):
    """测试用的Agent实现"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.type = config.type
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置Agent"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取Agent的schema"""
        return {
            "name": self.name,
            "description": "Test agent for unit testing",
            "version": "1.0.0",
            "capabilities": self.capabilities
        }
    
    async def execute(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务"""
        # 这个方法会被mock，所以这里不需要实现
        pass


@pytest.mark.asyncio
class TestUniversalTeam:
    """测试通用团队"""
    
    @pytest_asyncio.fixture
    async def team_config(self):
        """创建团队配置"""
        return TeamConfig(
            name="test_team",
            type=TeamType.COLLABORATIVE,
            communication_pattern=CommunicationPattern.ROUND_ROBIN,
            agents=[
                {
                    "name": "leader",
                    "type": AgentType.TASK_ORIENTED,
                    "description": "Team leader",
                    "capabilities": [
                        AgentCapability.CONVERSATION,
                        AgentCapability.REASONING
                    ]
                },
                {
                    "name": "coder",
                    "type": AgentType.CODING,
                    "description": "Code expert",
                    "capabilities": [
                        AgentCapability.CODE_GENERATION,
                        AgentCapability.CODE_EXECUTION
                    ]
                },
                {
                    "name": "researcher",
                    "type": AgentType.RESEARCH,
                    "description": "Research expert",
                    "capabilities": [
                        AgentCapability.WEB_SEARCH,
                        AgentCapability.REASONING
                    ]
                }
            ]
        )
    
    @pytest_asyncio.fixture
    async def team(self, team_config):
        """创建团队实例"""
        team = RoundRobinTeam(team_config)
        
        # 创建并添加Agent
        model_config = ModelConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        memory_config = MemoryConfig(
            enabled=True,
            max_memories=1000,
            memory_type="conversation"
        )
        behavior_config = BehaviorConfig(
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER",
            code_execution_config={}
        )
        
        for agent_config in team_config.agents:
            agent = TestAgent(AgentConfig(
                name=agent_config["name"],
                type=agent_config["type"],
                description=agent_config["description"],
                capabilities=agent_config["capabilities"],
                model=model_config,
                memory=memory_config,
                behavior=behavior_config,
                tools=[]
            ))
            agent.execute = AsyncMock()  # 模拟execute方法
            await team.add_agent(agent)
        
        return team
    
    async def test_team_initialization(self, team, team_config):
        """测试团队初始化"""
        assert team.config.name == team_config.name
        assert team.config.type == team_config.type
        assert team.config.communication_pattern == team_config.communication_pattern
        assert len(team.agents) == 3
        
        # 验证Agent配置
        leader = next((a for a in team.agents if a.name == "leader"), None)
        assert leader is not None
        assert leader.name == "leader"
        assert leader.type == AgentType.TASK_ORIENTED
        assert AgentCapability.CONVERSATION in leader.capabilities
        
        coder = next((a for a in team.agents if a.name == "coder"), None)
        assert coder is not None
        assert coder.name == "coder"
        assert coder.type == AgentType.CODING
        assert AgentCapability.CODE_GENERATION in coder.capabilities
        
        researcher = next((a for a in team.agents if a.name == "researcher"), None)
        assert researcher is not None
        assert researcher.name == "researcher"
        assert researcher.type == AgentType.RESEARCH
        assert AgentCapability.WEB_SEARCH in researcher.capabilities
    
    async def test_round_robin_execution(self, team):
        """测试轮询执行模式"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.9  # type: ignore
        
        for agent in team.agents:
            agent.execute.return_value = UniversalResult(
                content={"response": f"Response from {agent.name}"},
                status=ResultStatus.SUCCESS,
                result_type="conversation",
                metadata=metadata
            )
        
        # 创建任务
        task = UniversalTask(
            content="Solve this problem",
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = TeamContext(
            team_name="test_team",
            current_round=0,
            participants=[agent.name for agent in team.agents],
            conversation_history=[],
            shared_state={},
            timestamp=datetime.now()
        )
        
        # 执行任务
        results = []
        for _ in range(4):  # 执行4次，验证轮询
            result = await team.execute_task(task, context)
            results.append(result)
        
        # 验证轮询顺序
        assert "Response from leader" in results[0].content["response"]
        assert "Response from coder" in results[1].content["response"]
        assert "Response from researcher" in results[2].content["response"]
        assert "Response from leader" in results[3].content["response"]  # 回到第一个Agent
    
    async def test_selector_team(self, team_config):
        """测试选择器团队"""
        # 创建选择器团队
        team_config.type = TeamType.SELECTOR
        team_config.communication_pattern = CommunicationPattern.HIERARCHICAL
        team = SelectorTeam(team_config)
        
        # 创建并添加Agent
        model_config = ModelConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        memory_config = MemoryConfig(
            enabled=True,
            max_memories=1000,
            memory_type="conversation"
        )
        behavior_config = BehaviorConfig(
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER",
            code_execution_config={}
        )
        
        for agent_config in team_config.agents:
            agent = TestAgent(AgentConfig(
                name=agent_config["name"],
                type=agent_config["type"],
                description=agent_config["description"],
                capabilities=agent_config["capabilities"],
                model=model_config,
                memory=memory_config,
                behavior=behavior_config,
                tools=[]
            ))
            agent.execute = AsyncMock()  # 模拟execute方法
            await team.add_agent(agent)
        
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.9  # type: ignore
        
        for agent in team.agents:
            agent.execute.return_value = UniversalResult(
                content={"response": f"Response from {agent.name}"},
                status=ResultStatus.SUCCESS,
                result_type="conversation",
                metadata=metadata
            )
        
        # 创建任务
        tasks = [
            UniversalTask(
                content="Write a function",
                task_type=TaskType.CODE_GENERATION
            ),
            UniversalTask(
                content="Research ML algorithms",
                task_type=TaskType.WEB_SEARCH
            ),
            UniversalTask(
                content="Plan the project",
                task_type=TaskType.CONVERSATION
            )
        ]
        
        # 创建上下文
        context = TeamContext(
            team_name="test_team",
            current_round=0,
            participants=[agent.name for agent in team.agents],
            conversation_history=[],
            shared_state={},
            timestamp=datetime.now()
        )
        
        # 执行任务并验证选择的Agent
        for task in tasks:
            result = await team.execute_task(task, context)
            if task.task_type == TaskType.CODE_GENERATION:
                assert "Response from coder" in result.content["response"]
            elif task.task_type == TaskType.WEB_SEARCH:
                assert "Response from researcher" in result.content["response"]
            else:
                assert "Response from leader" in result.content["response"]
    
    async def test_swarm_team(self, team_config):
        """测试群体智能团队"""
        # 创建群体智能团队
        team_config.type = TeamType.SWARM
        team_config.communication_pattern = CommunicationPattern.PEER_TO_PEER
        team = SwarmTeam(team_config)
        
        # 创建并添加Agent
        model_config = ModelConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        memory_config = MemoryConfig(
            enabled=True,
            max_memories=1000,
            memory_type="conversation"
        )
        behavior_config = BehaviorConfig(
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER",
            code_execution_config={}
        )
        
        for agent_config in team_config.agents:
            agent = TestAgent(AgentConfig(
                name=agent_config["name"],
                type=agent_config["type"],
                description=agent_config["description"],
                capabilities=agent_config["capabilities"],
                model=model_config,
                memory=memory_config,
                behavior=behavior_config,
                tools=[]
            ))
            agent.execute = AsyncMock()  # 模拟execute方法
            await team.add_agent(agent)
        
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.9  # type: ignore
        
        for agent in team.agents:
            agent.execute.return_value = UniversalResult(
                content={"response": f"Response from {agent.name}"},
                status=ResultStatus.SUCCESS,
                result_type="conversation",
                metadata=metadata
            )
        
        # 创建任务
        task = UniversalTask(
            content="Complex problem solving",
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = TeamContext(
            team_name="test_team",
            current_round=0,
            participants=[agent.name for agent in team.agents],
            conversation_history=[],
            shared_state={},
            timestamp=datetime.now()
        )
        
        # 执行任务
        result = await team.execute_task(task, context)
        
        # 验证所有Agent都参与了执行
        assert result.is_successful()
        assert isinstance(result.content["responses"], list)
        assert len(result.content["responses"]) == 3
        assert any("Response from leader" in r for r in result.content["responses"])
        assert any("Response from coder" in r for r in result.content["responses"])
        assert any("Response from researcher" in r for r in result.content["responses"])
    
    async def test_error_handling(self, team):
        """测试错误处理"""
        # 模拟执行失败
        for agent in team.agents:
            agent.execute.return_value = UniversalResult(
                content={},
                status=ResultStatus.ERROR,
                result_type="conversation",
                error={"message": f"Error from {agent.name}"},
                metadata=ResultMetadata(framework_info={})
            )
        
        # 创建任务
        task = UniversalTask(
            content="Problem task",
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = TeamContext(
            team_name="test_team",
            current_round=0,
            participants=[agent.name for agent in team.agents],
            conversation_history=[],
            shared_state={},
            timestamp=datetime.now()
        )
        
        # 执行任务
        result = await team.execute_task(task, context)
        
        # 验证错误处理
        assert not result.is_successful()
        assert result.error is not None
        assert "Error from leader" in result.error.error_message  # 第一个Agent的错误
    
    async def test_team_metrics(self, team):
        """测试团队指标"""
        # 添加一些测试数据
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.9  # type: ignore
        
        for agent in team.agents:
            agent.execute.return_value = UniversalResult(
                content={"response": f"Response from {agent.name}"},
                status=ResultStatus.SUCCESS,
                result_type="conversation",
                metadata=metadata
            )
        
        # 创建任务
        task = UniversalTask(
            content="Test task",
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = TeamContext(
            team_name="test_team",
            current_round=0,
            participants=[agent.name for agent in team.agents],
            conversation_history=[],
            shared_state={},
            timestamp=datetime.now()
        )
        
        # 执行一些任务
        for i in range(3):
            context.current_round = i
            result = await team.execute_task(task, context)
            # 验证结果
            assert result.is_successful()
            assert result.content["response"].startswith("Response from")
        
        # 获取指标
        metrics = await team.get_team_status()
        
        # 验证指标
        assert metrics.type == TeamType.COLLABORATIVE
        assert metrics.agent_count == 3
        assert metrics.total_conversations == 3
        assert metrics.status == "completed" 