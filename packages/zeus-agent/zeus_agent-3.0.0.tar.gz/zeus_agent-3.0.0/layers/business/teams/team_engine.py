"""
Team Manager
团队管理器，负责管理Agent团队协作
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class TeamManager:
    """
    团队管理器
    
    管理Agent团队的创建、配置和协作
    """
    
    def __init__(self):
        self.teams: Dict[str, Dict[str, Any]] = {}
    
    async def create_team(self, name: str, description: str = "", team_id: Optional[str] = None, 
                         agents: Optional[List[Any]] = None, team_config: Optional[Dict[str, Any]] = None) -> str:
        """创建新团队"""
        if team_id is None:
            team_id = str(uuid.uuid4())
        
        # 处理agents参数
        members = []
        if agents:
            members = [{"agent_id": agent.agent_id, "agent": agent} for agent in agents]
            
        # 处理team_config参数
        config = team_config or {}
            
        self.teams[team_id] = {
            "id": team_id,
            "name": name,
            "description": description,
            "created_at": datetime.now(),
            "status": "active",
            "members": members,
            "workflows": [],
            "config": config
        }
        return team_id
    
    async def execute_team_task(self, team_id: str, task: Any, optimization_strategy: str = "performance") -> Dict[str, Any]:
        """执行团队任务"""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
        
        team = self.teams[team_id]
        
        # 模拟团队任务执行
        import asyncio
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        # 返回执行结果
        return {
            "task_id": getattr(task, 'task_id', 'unknown'),
            "team_id": team_id,
            "team_name": team["name"],
            "status": "completed",
            "members_count": len(team["members"]),
            "optimization_strategy": optimization_strategy,
            "execution_time": 0.1,
            "result": "团队任务执行成功"
        }
    
    async def get_team_performance(self, team_id: str) -> Dict[str, Any]:
        """获取团队性能指标"""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
        
        team = self.teams[team_id]
        
        # 模拟性能分析
        import random
        performance_score = 0.7 + random.random() * 0.3  # 0.7-1.0
        
        return {
            "team_id": team_id,
            "team_name": team["name"],
            "members_count": len(team["members"]),
            "performance_score": performance_score,
            "overall_score": performance_score,
            "efficiency": performance_score * 0.9,
            "collaboration_efficiency": performance_score * 0.95,
            "collaboration_quality": performance_score * 1.1,
            "task_completion_rate": performance_score,
            "individual_scores": {
                member["agent_id"]: 0.7 + random.random() * 0.3 
                for member in team["members"] if "agent_id" in member
            },
            "recommendations": [
                "增强团队沟通协作",
                "优化任务分配策略",
                "提升技术技能培训"
            ]
        }
    
    async def get_collaboration_pattern_recommendations(self, team_id: str) -> Dict[str, Any]:
        """获取协作模式推荐"""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
        
        team = self.teams[team_id]
        
        # 模拟协作模式分析
        import random
        
        # 基于团队规模和特点推荐协作模式
        members_count = len(team["members"])
        
        if members_count <= 3:
            # 小团队推荐
            patterns = {
                "sequential": 0.9,
                "parallel": 0.8,
                "expert_consultation": 0.7,
                "peer_review": 0.6
            }
        elif members_count <= 6:
            # 中等团队推荐
            patterns = {
                "parallel": 0.9,
                "peer_review": 0.8,
                "expert_consultation": 0.7,
                "sequential": 0.6
            }
        else:
            # 大团队推荐
            patterns = {
                "hierarchical": 0.9,
                "parallel": 0.8,
                "peer_review": 0.7,
                "expert_consultation": 0.6
            }
        
        # 添加一些随机性
        for pattern in patterns:
            patterns[pattern] += (random.random() - 0.5) * 0.2
            patterns[pattern] = max(0.0, min(1.0, patterns[pattern]))
        
        # 按分数排序
        sorted_patterns = dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "team_id": team_id,
            "team_size": members_count,
            "pattern_rankings": sorted_patterns,
            "recommendation_reason": f"基于{members_count}人团队规模的最佳协作模式推荐",
            "confidence_score": 0.8 + random.random() * 0.2
        }
    
    async def get_optimization_suggestions(self, team_id: str) -> List[Dict[str, Any]]:
        """获取团队优化建议"""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
        
        # 返回优化建议
        return [
            {
                "category": "协作效率",
                "suggestion": "建议增加每日站会，提升团队沟通频率",
                "priority": "high",
                "impact": "提升20%协作效率"
            },
            {
                "category": "技能发展", 
                "suggestion": "为团队成员安排跨技能培训",
                "priority": "medium",
                "impact": "增强团队灵活性"
            },
            {
                "category": "工作流程",
                "suggestion": "优化代码审查流程，减少等待时间",
                "priority": "high", 
                "impact": "提升15%开发速度"
            }
        ]
    
    def add_member(self, team_id: str, agent_id: str, role: str = "member") -> bool:
        """添加团队成员"""
        if team_id in self.teams:
            self.teams[team_id]["members"].append({
                "agent_id": agent_id,
                "role": role,
                "joined_at": datetime.now()
            })
            return True
        return False
    
    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """获取团队信息"""
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[Dict[str, Any]]:
        """列出所有团队"""
        return list(self.teams.values())
