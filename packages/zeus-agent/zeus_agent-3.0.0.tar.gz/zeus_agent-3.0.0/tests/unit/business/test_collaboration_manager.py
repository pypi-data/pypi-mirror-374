"""
CollaborationManager单元测试
测试协作管理器的所有功能
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from layers.business.teams.collaboration_manager import (
    CollaborationManager, TeamMember, CollaborationRole, 
    CollaborationResult
)


class TestCollaborationManager:
    """测试CollaborationManager类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.manager = CollaborationManager()
        
        # 创建模拟的Agent和团队成员
        self.mock_agent1 = Mock()
        self.mock_agent1.agent_id = "agent_001"
        self.mock_agent1.name = "Test Agent 1"
        
        self.mock_agent2 = Mock()
        self.mock_agent2.agent_id = "agent_002"
        self.mock_agent2.name = "Test Agent 2"
        
        self.mock_agent3 = Mock()
        self.mock_agent3.agent_id = "agent_003"
        self.mock_agent3.name = "Test Agent 3"
        
        self.mock_member1 = TeamMember(
            agent=self.mock_agent1,
            role=CollaborationRole.EXPERT,
            capabilities=[]
        )
        
        self.mock_member2 = TeamMember(
            agent=self.mock_agent2,
            role=CollaborationRole.CONTRIBUTOR,
            capabilities=[]
        )
        
        self.mock_member3 = TeamMember(
            agent=self.mock_agent3,
            role=CollaborationRole.LEADER,
            capabilities=[]
        )
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.teams == {}
        assert self.manager.active_collaborations == {}
        assert self.manager.collaboration_history == []
    
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
    
    def test_remove_team_member(self):
        """测试移除团队成员"""
        # 先创建团队和成员
        team_id = "test_team"
        member_id = "agent_001"
        self.manager.teams[team_id] = {member_id: self.mock_member1}
        
        # 移除成员
        success = self.manager.remove_team_member(team_id, member_id)
        assert success is True
        assert member_id not in self.manager.teams[team_id]
    
    @pytest.mark.asyncio
    async def test_create_team_success(self):
        """测试成功创建团队"""
        team_id = "test_team_001"
        members = [self.mock_member1, self.mock_member2]
        
        success = await self.manager.create_team(team_id, members)
        assert success is True
        
        # 验证团队创建
        assert team_id in self.manager.teams
        team_members = self.manager.teams[team_id]
        assert len(team_members) == 2
        
        # 验证成员关系 - 使用agent_id作为key
        agent_ids = list(team_members.keys())
        assert "agent_001" in agent_ids
        assert "agent_002" in agent_ids
    
    @pytest.mark.asyncio
    async def test_create_team_without_members(self):
        """测试创建没有成员的团队"""
        team_id = "empty_team_001"
        success = await self.manager.create_team(team_id, [])
        
        assert success is True
        assert team_id in self.manager.teams
        
        team_members = self.manager.teams[team_id]
        assert len(team_members) == 0
    
    def test_create_team_duplicate_id(self):
        """测试创建重复ID的团队"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        
        # 创建第一个团队
        team_id = "duplicate_team"
        success1 = self.manager.create_team(team_id, [self.mock_member1])
        assert success1 is True
        
        # 创建相同ID的第二个团队应该失败
        success2 = self.manager.create_team(team_id, [self.mock_member1])
        assert success2 is False
    
    def test_add_member_to_team(self):
        """测试向团队添加成员"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队
        team_id = "add_member_team"
        self.manager.create_team(team_id, [self.mock_member1])
        
        # 添加新成员
        success = self.manager.add_member_to_team(team_id, self.mock_member2)
        assert success is True
        
        # 验证成员被添加
        team = self.manager.teams[team_id]
        assert len(team.members) == 2
        
        member_ids = [member.member_id for member in team.members]
        assert "member_001" in member_ids
        assert "member_002" in member_ids
    
    def test_add_member_to_nonexistent_team(self):
        """测试向不存在的团队添加成员"""
        self.manager.register_member(self.mock_member1)
        
        success = self.manager.add_member_to_team("non_existent_team", self.mock_member1)
        assert success is False
    
    def test_add_nonexistent_member_to_team(self):
        """测试向团队添加不存在的成员"""
        # 创建团队
        team_id = "test_team"
        self.manager.create_team(team_id, [])
        
        # 尝试添加未注册的成员
        unregistered_member = TeamMember(
            member_id="unregistered",
            name="Unregistered Member",
            email="unregistered@test.com",
            role=CollaborationRole.DEVELOPER
        )
        
        success = self.manager.add_member_to_team(team_id, unregistered_member)
        assert success is False
    
    def test_remove_member_from_team(self):
        """测试从团队移除成员"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队
        team_id = "remove_member_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        # 移除成员
        success = self.manager.remove_member_from_team(team_id, self.mock_member1.member_id)
        assert success is True
        
        # 验证成员被移除
        team = self.manager.teams[team_id]
        assert len(team.members) == 1
        assert team.members[0].member_id == "member_002"
    
    def test_remove_member_from_nonexistent_team(self):
        """测试从不存在团队移除成员"""
        success = self.manager.remove_member_from_team("non_existent_team", "member_001")
        assert success is False
    
    def test_remove_nonexistent_member_from_team(self):
        """测试从团队移除不存在的成员"""
        # 创建团队
        team_id = "test_team"
        self.manager.create_team(team_id, [])
        
        # 尝试移除不存在的成员
        success = self.manager.remove_member_from_team(team_id, "non_existent_member")
        assert success is False
    
    def test_get_team_members(self):
        """测试获取团队成员"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队
        team_id = "get_members_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        # 获取成员
        members = self.manager.get_team_members(team_id)
        assert len(members) == 2
        
        member_ids = [member.member_id for member in members]
        assert "member_001" in member_ids
        assert "member_002" in member_ids
    
    def test_get_team_members_nonexistent_team(self):
        """测试获取不存在团队的成员"""
        members = self.manager.get_team_members("non_existent_team")
        assert members == []
    
    def test_get_teams_by_member(self):
        """测试获取成员所在的团队"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建多个团队
        team1_id = "team_1"
        team2_id = "team_2"
        
        self.manager.create_team(team1_id, [self.mock_member1])
        self.manager.create_team(team2_id, [self.mock_member1, self.mock_member2])
        
        # 获取member1所在的团队
        teams = self.manager.get_teams_by_member(self.mock_member1.member_id)
        assert len(teams) == 2
        
        team_ids = [team.team_id for team in teams]
        assert "team_1" in team_ids
        assert "team_2" in team_ids
        
        # 获取member2所在的团队
        teams = self.manager.get_teams_by_member(self.mock_member2.member_id)
        assert len(teams) == 1
        assert teams[0].team_id == "team_2"
    
    def test_get_teams_by_nonexistent_member(self):
        """测试获取不存在成员所在的团队"""
        teams = self.manager.get_teams_by_member("non_existent_member")
        assert teams == []
    
    def test_create_collaboration(self):
        """测试创建协作"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队
        team_id = "collab_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        # 创建协作
        collaboration_id = "collab_001"
        collaboration_type = "code_review"
        participants = [self.mock_member1.member_id, self.mock_member2.member_id]
        
        success = self.manager.create_collaboration(
            collaboration_id,
            collaboration_type,
            participants,
            team_id
        )
        
        assert success is True
        assert collaboration_id in self.manager.collaborations
        
        collaboration = self.manager.collaborations[collaboration_id]
        assert collaboration.collaboration_id == collaboration_id
        assert collaboration.collaboration_type == collaboration_type
        assert collaboration.team_id == team_id
        assert len(collaboration.participants) == 2
    
    def test_create_collaboration_with_nonexistent_team(self):
        """测试创建不存在的团队协作"""
        self.manager.register_member(self.mock_member1)
        
        success = self.manager.create_collaboration(
            "collab_001",
            "code_review",
            [self.mock_member1.member_id],
            "non_existent_team"
        )
        
        assert success is False
    
    def test_create_collaboration_with_nonexistent_members(self):
        """测试创建包含不存在成员的协作"""
        # 创建团队
        team_id = "test_team"
        self.manager.create_team(team_id, [])
        
        success = self.manager.create_collaboration(
            "collab_001",
            "code_review",
            ["non_existent_member"],
            team_id
        )
        
        assert success is False
    
    def test_get_collaboration_result(self):
        """测试获取协作结果"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队和协作
        team_id = "result_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        collaboration_id = "result_collab"
        self.manager.create_collaboration(
            collaboration_id,
            "code_review",
            [self.mock_member1.member_id, self.mock_member2.member_id],
            team_id
        )
        
        # 获取协作结果
        result = self.manager.get_collaboration_result(collaboration_id)
        assert result is not None
        assert result.collaboration_id == collaboration_id
        assert result.team_id == team_id
    
    def test_get_collaboration_result_nonexistent(self):
        """测试获取不存在协作的结果"""
        result = self.manager.get_collaboration_result("non_existent_collab")
        assert result is None
    
    def test_list_teams(self):
        """测试列出所有团队"""
        # 创建多个团队
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        self.manager.create_team("team_1", [self.mock_member1])
        self.manager.create_team("team_2", [self.mock_member2])
        self.manager.create_team("team_3", [self.mock_member1, self.mock_member2])
        
        # 列出团队
        teams = self.manager.list_teams()
        assert len(teams) == 3
        
        team_ids = [team.team_id for team in teams]
        assert "team_1" in team_ids
        assert "team_2" in team_ids
        assert "team_3" in team_ids
    
    def test_list_teams_empty(self):
        """测试列出空的团队列表"""
        teams = self.manager.list_teams()
        assert teams == []
    
    def test_list_collaborations(self):
        """测试列出所有协作"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        
        # 创建团队和协作
        team_id = "list_collab_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2])
        
        self.manager.create_collaboration(
            "collab_1",
            "code_review",
            [self.mock_member1.member_id, self.mock_member2.member_id],
            team_id
        )
        
        self.manager.create_collaboration(
            "collab_2",
            "pair_programming",
            [self.mock_member1.member_id, self.mock_member2.member_id],
            team_id
        )
        
        # 列出协作
        collaborations = self.manager.list_collaborations()
        assert len(collaborations) == 2
        
        collab_ids = [collab.collaboration_id for collab in collaborations]
        assert "collab_1" in collab_ids
        assert "collab_2" in collab_ids
    
    def test_list_collaborations_empty(self):
        """测试列出空的协作列表"""
        collaborations = self.manager.list_collaborations()
        assert collaborations == []
    
    def test_team_member_roles(self):
        """测试团队成员角色"""
        # 先注册成员
        self.manager.register_member(self.mock_member1)
        self.manager.register_member(self.mock_member2)
        self.manager.register_member(self.mock_member3)
        
        # 创建团队
        team_id = "roles_team"
        self.manager.create_team(team_id, [self.mock_member1, self.mock_member2, self.mock_member3])
        
        # 验证角色
        team = self.manager.teams[team_id]
        
        developer = next(m for m in team.members if m.role == CollaborationRole.DEVELOPER)
        tester = next(m for m in team.members if m.role == CollaborationRole.TESTER)
        manager = next(m for m in team.members if m.role == CollaborationRole.PROJECT_MANAGER)
        
        assert developer.name == "Test Member 1"
        assert tester.name == "Test Member 2"
        assert manager.name == "Test Member 3"


if __name__ == "__main__":
    pytest.main([__file__]) 