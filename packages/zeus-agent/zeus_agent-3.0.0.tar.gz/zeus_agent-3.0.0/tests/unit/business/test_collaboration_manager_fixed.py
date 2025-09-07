"""
CollaborationManager单元测试 - 修复版
测试协作管理器的实际功能接口
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from layers.business.teams.collaboration_manager import (
    CollaborationManager, TeamMember, CollaborationRole, 
    CollaborationResult, CollaborationPattern
)
from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType


class TestCollaborationManagerFixed:
    """测试CollaborationManager类的实际实现"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.manager = CollaborationManager()
        
        # 创建模拟的Agent
        self.mock_agent1 = Mock(spec=UniversalAgent)
        self.mock_agent1.agent_id = "agent_001"
        self.mock_agent1.name = "Test Agent 1"
        self.mock_agent1.get_capabilities.return_value = [AgentCapability.REASONING]
        
        self.mock_agent2 = Mock(spec=UniversalAgent)
        self.mock_agent2.agent_id = "agent_002"
        self.mock_agent2.name = "Test Agent 2"
        self.mock_agent2.get_capabilities.return_value = [AgentCapability.PLANNING]
        
        self.mock_agent3 = Mock(spec=UniversalAgent)
        self.mock_agent3.agent_id = "agent_003"
        self.mock_agent3.name = "Test Agent 3"
        self.mock_agent3.get_capabilities.return_value = [AgentCapability.CODE_GENERATION]
        
        # 创建团队成员
        self.mock_member1 = TeamMember(
            agent=self.mock_agent1,
            role=CollaborationRole.EXPERT,
            capabilities=[AgentCapability.REASONING]
        )
        
        self.mock_member2 = TeamMember(
            agent=self.mock_agent2,
            role=CollaborationRole.CONTRIBUTOR,
            capabilities=[AgentCapability.PLANNING]
        )
        
        self.mock_member3 = TeamMember(
            agent=self.mock_agent3,
            role=CollaborationRole.LEADER,
            capabilities=[AgentCapability.CODE_GENERATION]
        )
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.teams == {}
        assert self.manager.active_collaborations == {}
        assert self.manager.collaboration_history == []
        assert len(self.manager.pattern_handlers) == 8  # 8种协作模式
    
    @pytest.mark.asyncio
    async def test_create_team_with_members(self):
        """测试创建包含成员的团队"""
        team_id = "test_team_001"
        members = [self.mock_member1, self.mock_member2]
        
        success = await self.manager.create_team(team_id, members)
        assert success is True
        
        # 验证团队创建
        assert team_id in self.manager.teams
        team_members = self.manager.teams[team_id]
        assert len(team_members) == 2
        
        # 验证成员关系 - 使用agent_id作为key
        assert "agent_001" in team_members
        assert "agent_002" in team_members
        assert team_members["agent_001"] == self.mock_member1
        assert team_members["agent_002"] == self.mock_member2
    
    @pytest.mark.asyncio
    async def test_create_team_without_members(self):
        """测试创建空团队"""
        team_id = "empty_team"
        
        success = await self.manager.create_team(team_id, [])
        assert success is True
        
        assert team_id in self.manager.teams
        assert len(self.manager.teams[team_id]) == 0
    
    @pytest.mark.asyncio
    async def test_create_team_duplicate_id(self):
        """测试创建重复ID的团队"""
        team_id = "duplicate_team"
        
        # 第一次创建
        success1 = await self.manager.create_team(team_id, [])
        assert success1 is True
        
        # 第二次创建相同ID应该失败
        success2 = await self.manager.create_team(team_id, [])
        assert success2 is False
    
    @pytest.mark.asyncio
    async def test_add_team_member(self):
        """测试添加团队成员"""
        team_id = "test_team"
        member_id = "agent_001"
        
        success = await self.manager.add_team_member(
            team_id, member_id, self.mock_agent1, CollaborationRole.EXPERT
        )
        
        assert success is True
        assert team_id in self.manager.teams
        assert member_id in self.manager.teams[team_id]
        
        member = self.manager.teams[team_id][member_id]
        assert member.agent == self.mock_agent1
        assert member.role == CollaborationRole.EXPERT
    
    def test_remove_team_member_success(self):
        """测试成功移除团队成员"""
        team_id = "test_team"
        member_id = "agent_001"
        
        # 先添加团队和成员
        self.manager.teams[team_id] = {member_id: self.mock_member1}
        
        # 移除成员
        success = self.manager.remove_team_member(team_id, member_id)
        assert success is True
        assert member_id not in self.manager.teams[team_id]
    
    def test_remove_team_member_nonexistent(self):
        """测试移除不存在的团队成员"""
        success = self.manager.remove_team_member("nonexistent_team", "nonexistent_member")
        assert success is False
    
    def test_get_team_members(self):
        """测试获取团队成员"""
        team_id = "test_team"
        
        # 添加团队和成员
        self.manager.teams[team_id] = {
            "agent_001": self.mock_member1,
            "agent_002": self.mock_member2
        }
        
        members = self.manager.get_team_members(team_id)
        assert len(members) == 2
        assert "agent_001" in members
        assert "agent_002" in members
    
    def test_get_team_members_nonexistent(self):
        """测试获取不存在团队的成员"""
        members = self.manager.get_team_members("nonexistent_team")
        assert members == {}
    
    @pytest.mark.asyncio
    async def test_execute_collaboration_basic(self):
        """测试基础协作执行"""
        team_id = "test_team"
        
        # 创建团队和成员
        await self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        # 创建测试任务
        task = UniversalTask(content="Test collaborative task", task_type=TaskType.ANALYSIS)
        
        # Mock agent的execute方法
        self.mock_agent1.execute = AsyncMock(return_value=Mock(status="success"))
        self.mock_agent2.execute = AsyncMock(return_value=Mock(status="success"))
        
        # 执行协作
        result = await self.manager.execute_collaboration(
            team_id, task, CollaborationPattern.PARALLEL
        )
        
        assert isinstance(result, CollaborationResult)
        assert result.task_id is not None
        assert result.pattern == CollaborationPattern.PARALLEL
    
    @pytest.mark.asyncio
    async def test_execute_collaboration_nonexistent_team(self):
        """测试在不存在的团队上执行协作"""
        task = UniversalTask(content="Test task", task_type=TaskType.PLANNING)
        
        with pytest.raises(ValueError, match="Team nonexistent_team not found"):
            await self.manager.execute_collaboration(
                "nonexistent_team", task, CollaborationPattern.SEQUENTIAL
            )
    
    @pytest.mark.asyncio
    async def test_collaborate_alias_method(self):
        """测试collaborate方法（execute_collaboration的别名）"""
        team_id = "test_team"
        
        # 创建团队和成员
        await self.manager.create_team(team_id, [self.mock_member1])
        
        # 创建测试任务
        task = UniversalTask(content="Test task", task_type=TaskType.CUSTOM)
        
        # Mock agent的execute方法
        self.mock_agent1.execute = AsyncMock(return_value=Mock(status="success"))
        
        # 测试collaborate方法
        result = await self.manager.collaborate(team_id, task, CollaborationPattern.SEQUENTIAL)
        
        assert isinstance(result, CollaborationResult)
        assert result.pattern == CollaborationPattern.SEQUENTIAL
    
    def test_collaboration_patterns_registered(self):
        """测试所有协作模式都已注册"""
        expected_patterns = [
            CollaborationPattern.SEQUENTIAL,
            CollaborationPattern.PARALLEL,
            CollaborationPattern.ROUND_ROBIN,
            CollaborationPattern.EXPERT_CONSULTATION,
            CollaborationPattern.PEER_REVIEW,
            CollaborationPattern.DEBATE,
            CollaborationPattern.CONSENSUS,
            CollaborationPattern.HIERARCHICAL,
        ]
        
        for pattern in expected_patterns:
            assert pattern in self.manager.pattern_handlers
            assert callable(self.manager.pattern_handlers[pattern]) 