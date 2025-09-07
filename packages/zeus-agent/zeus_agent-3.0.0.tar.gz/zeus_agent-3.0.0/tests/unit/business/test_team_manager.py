"""
业务能力层 - 团队管理器测试
测试团队创建、成员管理、协作指标和团队优化
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from layers.business.teams.team_engine import TeamManager
from layers.business.teams.collaboration_manager import (
    CollaborationManager, CollaborationPattern, CollaborationRole, TeamMember
)
from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class TestTeamManager:
    """团队管理器基础功能测试"""
    
    @pytest.fixture
    def team_manager(self):
        """创建团队管理器实例"""
        return TeamManager()
    
    @pytest.fixture
    def mock_agents(self):
        """创建模拟Agent列表"""
        agents = []
        roles = ["leader", "developer", "tester", "designer", "analyst"]
        capabilities_map = {
            "leader": [AgentCapability.PROJECT_MANAGEMENT, AgentCapability.REASONING],
            "developer": [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING],
            "tester": [AgentCapability.TESTING, AgentCapability.QUALITY_ASSURANCE],
            "designer": [AgentCapability.UI_UX_DESIGN, AgentCapability.VISUALIZATION],
            "analyst": [AgentCapability.DATA_ANALYSIS, AgentCapability.REASONING]
        }
        
        for i, role in enumerate(roles):
            agent = Mock(spec=UniversalAgent)
            agent.agent_id = f"{role}_agent_{i}"
            agent.name = f"{role.title()} Agent {i}"
            agent.role = role
            agent.capabilities = capabilities_map[role]
            agent.performance_score = 0.8 + (i * 0.05)
            agent.availability = True
            
            async def mock_execute(task, agent_id=agent.agent_id, score=agent.performance_score):
                await asyncio.sleep(0.1)
                return UniversalResult(
                    task_id=task.task_id,
                    status=ResultStatus.SUCCESS,
                    data={"processed": True, "quality": score},
                    metadata={"agent_id": agent_id, "performance": score}
                )
            
            agent.execute = mock_execute
            agents.append(agent)
        
        return agents
    
    @pytest.fixture
    def collaboration_manager(self):
        """创建协作管理器实例"""
        return CollaborationManager()

    def test_team_manager_initialization(self, team_manager):
        """测试团队管理器初始化"""
        assert isinstance(team_manager.teams, dict)
        assert isinstance(team_manager.team_metrics, dict)
        assert isinstance(team_manager.performance_history, list)
        assert team_manager.collaboration_manager is not None

    @pytest.mark.asyncio
    async def test_create_team_basic(self, team_manager, mock_agents):
        """测试基础团队创建"""
        team_id = "dev_team_001"
        team_name = "Development Team Alpha"
        
        # 选择团队成员
        team_agents = mock_agents[:3]  # 领导者、开发者、测试者
        
        result = await team_manager.create_team(
            team_id=team_id,
            team_name=team_name,
            agents=team_agents,
            team_config={
                "max_size": 5,
                "collaboration_pattern": CollaborationPattern.HIERARCHICAL,
                "performance_threshold": 0.7
            }
        )
        
        assert result is True
        assert team_id in team_manager.teams
        
        team = team_manager.teams[team_id]
        assert team["name"] == team_name
        assert len(team["members"]) == 3
        assert team["config"]["max_size"] == 5
        
        # 验证团队角色分配
        leader_found = False
        for member in team["members"]:
            if member.role == CollaborationRole.LEADER:
                leader_found = True
                break
        assert leader_found

    @pytest.mark.asyncio
    async def test_add_team_member(self, team_manager, mock_agents):
        """测试添加团队成员"""
        team_id = "expandable_team"
        
        # 创建初始团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Expandable Team",
            agents=mock_agents[:2],
            team_config={"max_size": 5}
        )
        
        # 添加新成员
        new_member = mock_agents[2]
        result = await team_manager.add_team_member(
            team_id=team_id,
            agent=new_member,
            role=CollaborationRole.EXPERT
        )
        
        assert result is True
        
        team = team_manager.teams[team_id]
        assert len(team["members"]) == 3
        
        # 验证新成员已添加
        new_member_found = False
        for member in team["members"]:
            if member.agent.agent_id == new_member.agent_id:
                assert member.role == CollaborationRole.EXPERT
                new_member_found = True
                break
        assert new_member_found

    @pytest.mark.asyncio
    async def test_remove_team_member(self, team_manager, mock_agents):
        """测试移除团队成员"""
        team_id = "shrinkable_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Shrinkable Team",
            agents=mock_agents[:4],
            team_config={"min_size": 2}
        )
        
        # 移除成员
        member_to_remove = mock_agents[3].agent_id
        result = await team_manager.remove_team_member(team_id, member_to_remove)
        
        assert result is True
        
        team = team_manager.teams[team_id]
        assert len(team["members"]) == 3
        
        # 验证成员已移除
        for member in team["members"]:
            assert member.agent.agent_id != member_to_remove

    @pytest.mark.asyncio
    async def test_team_size_limits(self, team_manager, mock_agents):
        """测试团队大小限制"""
        team_id = "limited_team"
        
        # 创建有大小限制的团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Limited Team",
            agents=mock_agents[:2],
            team_config={"max_size": 3, "min_size": 2}
        )
        
        # 尝试添加成员到最大限制
        result = await team_manager.add_team_member(
            team_id, mock_agents[2], CollaborationRole.CONTRIBUTOR
        )
        assert result is True  # 应该成功，达到最大大小
        
        # 尝试超过最大限制
        result = await team_manager.add_team_member(
            team_id, mock_agents[3], CollaborationRole.CONTRIBUTOR
        )
        assert result is False  # 应该失败，超过最大大小
        
        # 尝试移除到最小限制以下
        team = team_manager.teams[team_id]
        members = list(team["members"])
        
        # 移除一个成员，应该成功
        result = await team_manager.remove_team_member(team_id, members[0].agent.agent_id)
        assert result is True
        
        # 再移除一个成员，应该失败（低于最小限制）
        remaining_members = list(team_manager.teams[team_id]["members"])
        result = await team_manager.remove_team_member(team_id, remaining_members[0].agent.agent_id)
        assert result is False


class TestTeamPerformanceTracking:
    """团队性能跟踪测试"""
    
    @pytest.fixture
    def team_manager(self):
        return TeamManager()
    
    @pytest.mark.asyncio
    async def test_team_performance_calculation(self, team_manager, mock_agents):
        """测试团队性能计算"""
        team_id = "performance_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Performance Team",
            agents=mock_agents[:3]
        )
        
        # 模拟团队协作任务
        task = UniversalTask(
            task_id="performance_task",
            task_type=TaskType.ANALYSIS,
            description="Performance analysis task"
        )
        
        # 执行协作任务
        result = await team_manager.execute_team_task(
            team_id=team_id,
            task=task,
            pattern=CollaborationPattern.PARALLEL
        )
        
        assert result.final_result.status == ResultStatus.SUCCESS
        
        # 检查性能指标
        performance = await team_manager.get_team_performance(team_id)
        
        assert "overall_score" in performance
        assert "individual_scores" in performance
        assert "collaboration_efficiency" in performance
        assert "task_completion_rate" in performance
        
        assert 0 <= performance["overall_score"] <= 1
        assert len(performance["individual_scores"]) == 3

    @pytest.mark.asyncio
    async def test_performance_history_tracking(self, team_manager, mock_agents):
        """测试性能历史跟踪"""
        team_id = "history_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="History Team",
            agents=mock_agents[:2]
        )
        
        # 执行多个任务
        for i in range(5):
            task = UniversalTask(
                task_id=f"history_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Historical task {i}"
            )
            
            await team_manager.execute_team_task(
                team_id=team_id,
                task=task,
                pattern=CollaborationPattern.SEQUENTIAL
            )
        
        # 获取性能历史
        history = await team_manager.get_performance_history(team_id)
        
        assert len(history) == 5
        
        for record in history:
            assert "timestamp" in record
            assert "performance_score" in record
            assert "task_id" in record
            assert "collaboration_metrics" in record

    @pytest.mark.asyncio
    async def test_performance_trend_analysis(self, team_manager, mock_agents):
        """测试性能趋势分析"""
        team_id = "trend_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Trend Team",
            agents=mock_agents[:3]
        )
        
        # 模拟性能变化的任务执行
        performance_scores = [0.6, 0.7, 0.75, 0.8, 0.85]  # 上升趋势
        
        for i, target_score in enumerate(performance_scores):
            # 调整Agent性能以模拟趋势
            for agent in mock_agents[:3]:
                agent.performance_score = target_score
            
            task = UniversalTask(
                task_id=f"trend_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Trend task {i}"
            )
            
            await team_manager.execute_team_task(
                team_id=team_id,
                task=task,
                pattern=CollaborationPattern.PARALLEL
            )
        
        # 分析性能趋势
        trend = await team_manager.analyze_performance_trend(team_id)
        
        assert "trend_direction" in trend
        assert "trend_strength" in trend
        assert "prediction" in trend
        
        assert trend["trend_direction"] == "improving"  # 应该检测到改善趋势
        assert trend["trend_strength"] > 0.5  # 趋势应该比较明显


class TestTeamOptimization:
    """团队优化测试"""
    
    @pytest.fixture
    def team_manager(self):
        return TeamManager()
    
    @pytest.mark.asyncio
    async def test_team_composition_optimization(self, team_manager, mock_agents):
        """测试团队组成优化"""
        team_id = "optimization_team"
        
        # 创建初始团队（性能不佳）
        low_performance_agents = mock_agents[:2]
        for agent in low_performance_agents:
            agent.performance_score = 0.5  # 较低的性能分数
        
        await team_manager.create_team(
            team_id=team_id,
            team_name="Optimization Team",
            agents=low_performance_agents
        )
        
        # 执行几个任务以建立基线性能
        for i in range(3):
            task = UniversalTask(
                task_id=f"baseline_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Baseline task {i}"
            )
            await team_manager.execute_team_task(team_id, task, CollaborationPattern.PARALLEL)
        
        # 获取优化建议
        optimization_suggestions = await team_manager.get_optimization_suggestions(team_id)
        
        assert "suggested_additions" in optimization_suggestions
        assert "suggested_removals" in optimization_suggestions
        assert "role_adjustments" in optimization_suggestions
        assert "performance_impact" in optimization_suggestions
        
        # 应用优化建议
        if optimization_suggestions["suggested_additions"]:
            # 添加高性能Agent
            high_performance_agent = mock_agents[4]  # 分析师，通常性能较高
            high_performance_agent.performance_score = 0.9
            
            result = await team_manager.add_team_member(
                team_id, high_performance_agent, CollaborationRole.EXPERT
            )
            assert result is True
        
        # 验证优化效果
        post_optimization_performance = await team_manager.get_team_performance(team_id)
        
        # 执行优化后的任务
        task = UniversalTask(
            task_id="post_optimization_task",
            task_type=TaskType.ANALYSIS,
            description="Post-optimization task"
        )
        await team_manager.execute_team_task(team_id, task, CollaborationPattern.PARALLEL)
        
        final_performance = await team_manager.get_team_performance(team_id)
        
        # 性能应该有所提升
        assert final_performance["overall_score"] > 0.6

    @pytest.mark.asyncio
    async def test_role_optimization(self, team_manager, mock_agents):
        """测试角色优化"""
        team_id = "role_optimization_team"
        
        # 创建角色分配不当的团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Role Optimization Team",
            agents=mock_agents[:3]
        )
        
        # 手动设置不合适的角色
        team = team_manager.teams[team_id]
        for member in team["members"]:
            if member.agent.role == "developer":
                member.role = CollaborationRole.LEADER  # 开发者做领导可能不合适
            elif member.agent.role == "leader":
                member.role = CollaborationRole.CONTRIBUTOR  # 领导者做贡献者
        
        # 执行任务以观察性能
        for i in range(3):
            task = UniversalTask(
                task_id=f"role_task_{i}",
                task_type=TaskType.PROJECT_MANAGEMENT,
                description=f"Role task {i}"
            )
            await team_manager.execute_team_task(team_id, task, CollaborationPattern.HIERARCHICAL)
        
        # 获取角色优化建议
        role_suggestions = await team_manager.suggest_role_optimization(team_id)
        
        assert "role_changes" in role_suggestions
        assert "expected_improvement" in role_suggestions
        
        # 应用角色优化
        await team_manager.apply_role_optimization(team_id, role_suggestions["role_changes"])
        
        # 验证角色已调整
        optimized_team = team_manager.teams[team_id]
        leader_count = sum(1 for member in optimized_team["members"] 
                          if member.role == CollaborationRole.LEADER)
        assert leader_count == 1  # 应该只有一个领导者

    @pytest.mark.asyncio
    async def test_workload_balancing(self, team_manager, mock_agents):
        """测试工作负载平衡"""
        team_id = "workload_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Workload Team",
            agents=mock_agents[:4]
        )
        
        # 模拟不平衡的工作负载
        tasks = []
        for i in range(10):
            task = UniversalTask(
                task_id=f"workload_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Workload task {i}",
                priority=TaskPriority.MEDIUM
            )
            tasks.append(task)
        
        # 执行任务并跟踪负载分布
        for task in tasks:
            await team_manager.execute_team_task(
                team_id, task, CollaborationPattern.ROUND_ROBIN
            )
        
        # 分析工作负载分布
        workload_analysis = await team_manager.analyze_workload_distribution(team_id)
        
        assert "member_workloads" in workload_analysis
        assert "balance_score" in workload_analysis
        assert "recommendations" in workload_analysis
        
        # 验证负载分布相对均匀
        workloads = list(workload_analysis["member_workloads"].values())
        max_workload = max(workloads)
        min_workload = min(workloads)
        
        # 负载差异不应该太大
        assert (max_workload - min_workload) / max_workload < 0.5


class TestTeamCollaborationPatterns:
    """团队协作模式测试"""
    
    @pytest.fixture
    def team_manager(self):
        return TeamManager()
    
    @pytest.mark.asyncio
    async def test_pattern_effectiveness_analysis(self, team_manager, mock_agents):
        """测试协作模式有效性分析"""
        team_id = "pattern_analysis_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Pattern Analysis Team",
            agents=mock_agents[:4]
        )
        
        # 测试不同的协作模式
        patterns_to_test = [
            CollaborationPattern.SEQUENTIAL,
            CollaborationPattern.PARALLEL,
            CollaborationPattern.EXPERT_CONSULTATION,
            CollaborationPattern.CONSENSUS
        ]
        
        pattern_results = {}
        
        for pattern in patterns_to_test:
            # 为每种模式执行多个任务
            pattern_performance = []
            
            for i in range(3):
                task = UniversalTask(
                    task_id=f"pattern_task_{pattern.value}_{i}",
                    task_type=TaskType.ANALYSIS,
                    description=f"Pattern test task for {pattern.value}"
                )
                
                result = await team_manager.execute_team_task(team_id, task, pattern)
                
                # 计算性能指标
                performance_score = result.collaboration_metrics.get("quality_score", 0.5)
                execution_time = result.collaboration_metrics.get("execution_time", 1.0)
                efficiency = performance_score / execution_time
                
                pattern_performance.append({
                    "performance": performance_score,
                    "efficiency": efficiency,
                    "consensus": result.consensus_score
                })
            
            # 计算模式平均性能
            avg_performance = sum(p["performance"] for p in pattern_performance) / len(pattern_performance)
            avg_efficiency = sum(p["efficiency"] for p in pattern_performance) / len(pattern_performance)
            avg_consensus = sum(p["consensus"] for p in pattern_performance) / len(pattern_performance)
            
            pattern_results[pattern] = {
                "average_performance": avg_performance,
                "average_efficiency": avg_efficiency,
                "average_consensus": avg_consensus
            }
        
        # 分析最佳模式
        best_pattern = max(pattern_results.items(), 
                          key=lambda x: x[1]["average_performance"])
        
        assert best_pattern is not None
        assert best_pattern[1]["average_performance"] > 0
        
        # 获取团队协作模式建议
        pattern_recommendations = await team_manager.get_collaboration_pattern_recommendations(team_id)
        
        assert "recommended_patterns" in pattern_recommendations
        assert "pattern_rankings" in pattern_recommendations
        assert "context_specific_suggestions" in pattern_recommendations

    @pytest.mark.asyncio
    async def test_adaptive_pattern_selection(self, team_manager, mock_agents):
        """测试自适应协作模式选择"""
        team_id = "adaptive_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Adaptive Team",
            agents=mock_agents
        )
        
        # 不同类型的任务
        task_types = [
            (TaskType.ANALYSIS, "Complex data analysis requiring expertise"),
            (TaskType.CREATIVE, "Creative brainstorming session"),
            (TaskType.DECISION_MAKING, "Strategic decision requiring consensus"),
            (TaskType.PROBLEM_SOLVING, "Technical problem solving")
        ]
        
        for task_type, description in task_types:
            task = UniversalTask(
                task_id=f"adaptive_task_{task_type.value}",
                task_type=task_type,
                description=description
            )
            
            # 让团队管理器自动选择最佳协作模式
            recommended_pattern = await team_manager.recommend_collaboration_pattern(
                team_id, task
            )
            
            assert recommended_pattern is not None
            assert isinstance(recommended_pattern, CollaborationPattern)
            
            # 执行任务使用推荐的模式
            result = await team_manager.execute_team_task(
                team_id, task, recommended_pattern
            )
            
            assert result.final_result.status == ResultStatus.SUCCESS
            
            # 验证模式选择的合理性
            if task_type == TaskType.ANALYSIS:
                # 分析任务通常适合专家会诊
                assert recommended_pattern in [
                    CollaborationPattern.EXPERT_CONSULTATION,
                    CollaborationPattern.PARALLEL
                ]
            elif task_type == TaskType.DECISION_MAKING:
                # 决策任务通常适合共识模式
                assert recommended_pattern in [
                    CollaborationPattern.CONSENSUS,
                    CollaborationPattern.DEBATE
                ]


class TestTeamMetrics:
    """团队指标测试"""
    
    @pytest.fixture
    def team_manager(self):
        return TeamManager()
    
    @pytest.mark.asyncio
    async def test_comprehensive_team_metrics(self, team_manager, mock_agents):
        """测试综合团队指标"""
        team_id = "metrics_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Metrics Team",
            agents=mock_agents[:3]
        )
        
        # 执行一系列任务
        for i in range(10):
            task = UniversalTask(
                task_id=f"metrics_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Metrics task {i}",
                priority=TaskPriority.MEDIUM
            )
            
            pattern = CollaborationPattern.PARALLEL if i % 2 == 0 else CollaborationPattern.SEQUENTIAL
            await team_manager.execute_team_task(team_id, task, pattern)
        
        # 获取综合指标
        comprehensive_metrics = await team_manager.get_comprehensive_metrics(team_id)
        
        # 验证指标完整性
        expected_metrics = [
            "team_performance", "collaboration_efficiency", "member_satisfaction",
            "task_completion_rate", "average_response_time", "quality_score",
            "innovation_index", "adaptability_score", "communication_effectiveness",
            "conflict_resolution_rate"
        ]
        
        for metric in expected_metrics:
            assert metric in comprehensive_metrics
            assert isinstance(comprehensive_metrics[metric], (int, float))
            assert 0 <= comprehensive_metrics[metric] <= 1

    @pytest.mark.asyncio
    async def test_team_health_assessment(self, team_manager, mock_agents):
        """测试团队健康评估"""
        team_id = "health_team"
        
        # 创建团队
        await team_manager.create_team(
            team_id=team_id,
            team_name="Health Team",
            agents=mock_agents[:4]
        )
        
        # 模拟一段时间的团队活动
        for week in range(4):
            for day in range(5):  # 工作日
                task = UniversalTask(
                    task_id=f"health_task_w{week}_d{day}",
                    task_type=TaskType.ANALYSIS,
                    description=f"Daily task week {week} day {day}"
                )
                
                # 模拟不同的成功率
                success_rate = 0.9 - (week * 0.1)  # 逐渐下降的成功率
                for agent in mock_agents[:4]:
                    agent.performance_score = max(0.3, success_rate)
                
                await team_manager.execute_team_task(
                    team_id, task, CollaborationPattern.ROUND_ROBIN
                )
        
        # 进行团队健康评估
        health_assessment = await team_manager.assess_team_health(team_id)
        
        assert "overall_health_score" in health_assessment
        assert "health_indicators" in health_assessment
        assert "risk_factors" in health_assessment
        assert "recommendations" in health_assessment
        
        # 验证健康指标
        health_indicators = health_assessment["health_indicators"]
        expected_indicators = [
            "performance_trend", "member_engagement", "collaboration_quality",
            "workload_balance", "skill_diversity", "communication_health"
        ]
        
        for indicator in expected_indicators:
            assert indicator in health_indicators
        
        # 由于模拟了性能下降，应该检测到风险
        assert len(health_assessment["risk_factors"]) > 0
        assert len(health_assessment["recommendations"]) > 0

    def test_team_comparison_metrics(self, team_manager, mock_agents):
        """测试团队比较指标"""
        # 创建两个不同的团队
        team_configs = [
            {
                "team_id": "team_a",
                "name": "Team Alpha",
                "agents": mock_agents[:3],
                "performance_modifier": 1.0
            },
            {
                "team_id": "team_b", 
                "name": "Team Beta",
                "agents": mock_agents[2:5],
                "performance_modifier": 0.8
            }
        ]
        
        # 异步创建团队和执行任务
        async def setup_and_run_team(config):
            # 调整Agent性能
            for agent in config["agents"]:
                agent.performance_score *= config["performance_modifier"]
            
            await team_manager.create_team(
                team_id=config["team_id"],
                team_name=config["name"],
                agents=config["agents"]
            )
            
            # 执行相同的任务集
            for i in range(5):
                task = UniversalTask(
                    task_id=f"comparison_task_{config['team_id']}_{i}",
                    task_type=TaskType.ANALYSIS,
                    description=f"Comparison task {i}"
                )
                
                await team_manager.execute_team_task(
                    config["team_id"], task, CollaborationPattern.PARALLEL
                )
        
        # 运行设置（在实际测试中需要使用asyncio.run或在async函数中运行）
        # 这里我们模拟已经运行完成的状态
        
        # 比较团队性能
        comparison = team_manager.compare_teams(["team_a", "team_b"])
        
        assert "team_rankings" in comparison
        assert "performance_comparison" in comparison
        assert "strength_analysis" in comparison
        assert "improvement_suggestions" in comparison
        
        # 验证排名
        rankings = comparison["team_rankings"]
        assert len(rankings) == 2
        assert rankings[0]["team_id"] in ["team_a", "team_b"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 