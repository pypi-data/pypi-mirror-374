"""
业务能力层性能和压力测试
测试大规模并发、内存使用、响应时间、吞吐量等性能指标
"""

import pytest
import asyncio
import time
import psutil
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import statistics
import gc

from layers.business.teams.collaboration_manager import (
    CollaborationManager, CollaborationPattern, CollaborationRole, TeamMember
)
from layers.business.teams.team_engine import TeamManager
from layers.business.workflows.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowStep, WorkflowStepType
)
from layers.business.communication_manager import BusinessCommunicationManager

from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.response_times = []
        self.memory_snapshots = []
        self.cpu_snapshots = []
        self.success_count = 0
        self.failure_count = 0
        self.process = psutil.Process(os.getpid())
    
    def start_monitoring(self):
        """开始性能监控"""
        self.start_time = time.time()
        self.memory_snapshots = [self.process.memory_info().rss]
        self.cpu_snapshots = [self.process.cpu_percent()]
    
    def record_operation(self, start_time: float, end_time: float, success: bool):
        """记录操作性能"""
        response_time = end_time - start_time
        self.response_times.append(response_time)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # 记录内存和CPU快照
        self.memory_snapshots.append(self.process.memory_info().rss)
        self.cpu_snapshots.append(self.process.cpu_percent())
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.end_time = time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        total_time = self.end_time - self.start_time if self.end_time else 0
        total_operations = self.success_count + self.failure_count
        
        return {
            "total_time": total_time,
            "total_operations": total_operations,
            "success_rate": self.success_count / total_operations if total_operations > 0 else 0,
            "throughput": total_operations / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "avg": statistics.mean(self.response_times) if self.response_times else 0,
                "median": statistics.median(self.response_times) if self.response_times else 0,
                "p95": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else 0,
                "p99": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else 0
            },
            "memory": {
                "initial": self.memory_snapshots[0] if self.memory_snapshots else 0,
                "final": self.memory_snapshots[-1] if self.memory_snapshots else 0,
                "peak": max(self.memory_snapshots) if self.memory_snapshots else 0,
                "increase": (self.memory_snapshots[-1] - self.memory_snapshots[0]) if len(self.memory_snapshots) > 1 else 0
            },
            "cpu": {
                "avg": statistics.mean(self.cpu_snapshots) if self.cpu_snapshots else 0,
                "peak": max(self.cpu_snapshots) if self.cpu_snapshots else 0
            }
        }


class TestCollaborationManagerPerformance:
    """协作管理器性能测试"""
    
    @pytest.fixture
    def collaboration_manager(self):
        return CollaborationManager()
    
    @pytest.fixture
    def performance_agents(self):
        """创建性能测试用的Agent池"""
        agents = []
        for i in range(100):  # 100个Agent
            agent = Mock(spec=UniversalAgent)
            agent.agent_id = f"perf_agent_{i}"
            agent.name = f"Performance Agent {i}"
            agent.capabilities = [
                AgentCapability.TEXT_PROCESSING,
                AgentCapability.REASONING,
                AgentCapability.DATA_ANALYSIS
            ]
            
            async def mock_execute(task, processing_time=0.01 + (i % 10) * 0.001):
                await asyncio.sleep(processing_time)  # 模拟不同的处理时间
                return UniversalResult(
                    task_id=task.task_id,
                    status=ResultStatus.SUCCESS,
                    data={"processed": True, "agent_id": agent.agent_id},
                    metadata={"processing_time": processing_time}
                )
            
            agent.execute = mock_execute
            agents.append(agent)
        
        return agents

    @pytest.mark.asyncio
    async def test_large_team_collaboration_performance(self, collaboration_manager, performance_agents):
        """测试大团队协作性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 创建大团队（50个成员）
        team_id = "large_team_performance"
        large_team_agents = performance_agents[:50]
        
        members = [
            TeamMember(
                agent=agent,
                role=CollaborationRole.CONTRIBUTOR,
                capabilities=agent.capabilities,
                priority=i % 5
            )
            for i, agent in enumerate(large_team_agents)
        ]
        
        start_time = time.time()
        await collaboration_manager.create_team(team_id, members)
        end_time = time.time()
        
        metrics.record_operation(start_time, end_time, True)
        
        # 执行大规模并行协作
        task = UniversalTask(
            task_id="large_team_task",
            task_type=TaskType.ANALYSIS,
            description="Large team collaboration performance test",
            priority=TaskPriority.HIGH
        )
        
        start_time = time.time()
        result = await collaboration_manager.collaborate(
            team_id=team_id,
            task=task,
            pattern=CollaborationPattern.PARALLEL
        )
        end_time = time.time()
        
        metrics.record_operation(start_time, end_time, 
                                result.final_result.status == ResultStatus.SUCCESS)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.95  # 95%成功率
        assert performance_data["response_times"]["avg"] < 5.0  # 平均响应时间小于5秒
        assert performance_data["memory"]["increase"] < 100 * 1024 * 1024  # 内存增长小于100MB
        
        # 验证大团队协作结果
        assert len(result.individual_results) == 50
        assert result.final_result.status == ResultStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_concurrent_collaborations_performance(self, collaboration_manager, performance_agents):
        """测试并发协作性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 创建多个团队
        teams = []
        team_size = 5
        num_teams = 20
        
        for i in range(num_teams):
            team_id = f"concurrent_team_{i}"
            team_agents = performance_agents[i*team_size:(i+1)*team_size]
            
            members = [
                TeamMember(
                    agent=agent,
                    role=CollaborationRole.CONTRIBUTOR,
                    capabilities=agent.capabilities
                )
                for agent in team_agents
            ]
            
            await collaboration_manager.create_team(team_id, members)
            teams.append(team_id)
        
        # 并发执行协作任务
        collaboration_tasks = []
        
        for i, team_id in enumerate(teams):
            task = UniversalTask(
                task_id=f"concurrent_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Concurrent collaboration task {i}",
                priority=TaskPriority.MEDIUM
            )
            
            # 随机选择协作模式
            patterns = [
                CollaborationPattern.PARALLEL,
                CollaborationPattern.SEQUENTIAL,
                CollaborationPattern.EXPERT_CONSULTATION,
                CollaborationPattern.ROUND_ROBIN
            ]
            pattern = patterns[i % len(patterns)]
            
            coroutine = collaboration_manager.collaborate(
                team_id=team_id,
                task=task,
                pattern=pattern
            )
            collaboration_tasks.append((coroutine, time.time()))
        
        # 执行所有并发任务
        start_time = time.time()
        results = await asyncio.gather(*[task[0] for task in collaboration_tasks])
        end_time = time.time()
        
        # 记录每个任务的性能
        for i, result in enumerate(results):
            task_start_time = collaboration_tasks[i][1]
            success = result.final_result.status == ResultStatus.SUCCESS
            metrics.record_operation(task_start_time, end_time, success)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.90  # 90%成功率
        assert performance_data["response_times"]["p95"] < 10.0  # 95%的请求在10秒内完成
        assert performance_data["throughput"] >= 2.0  # 至少每秒处理2个协作任务
        
        # 验证并发协作结果
        success_count = sum(1 for result in results 
                           if result.final_result.status == ResultStatus.SUCCESS)
        assert success_count >= num_teams * 0.9

    @pytest.mark.asyncio
    async def test_collaboration_pattern_performance_comparison(self, collaboration_manager, performance_agents):
        """测试不同协作模式的性能对比"""
        team_id = "pattern_performance_team"
        team_agents = performance_agents[:10]
        
        members = [
            TeamMember(
                agent=agent,
                role=CollaborationRole.CONTRIBUTOR,
                capabilities=agent.capabilities
            )
            for agent in team_agents
        ]
        
        await collaboration_manager.create_team(team_id, members)
        
        # 测试不同协作模式的性能
        patterns_performance = {}
        
        patterns_to_test = [
            CollaborationPattern.SEQUENTIAL,
            CollaborationPattern.PARALLEL,
            CollaborationPattern.ROUND_ROBIN,
            CollaborationPattern.EXPERT_CONSULTATION,
            CollaborationPattern.CONSENSUS
        ]
        
        for pattern in patterns_to_test:
            pattern_metrics = PerformanceMetrics()
            pattern_metrics.start_monitoring()
            
            # 为每种模式执行多次测试
            for i in range(5):
                task = UniversalTask(
                    task_id=f"pattern_test_{pattern.value}_{i}",
                    task_type=TaskType.ANALYSIS,
                    description=f"Pattern performance test for {pattern.value}"
                )
                
                start_time = time.time()
                result = await collaboration_manager.collaborate(
                    team_id=team_id,
                    task=task,
                    pattern=pattern
                )
                end_time = time.time()
                
                success = result.final_result.status == ResultStatus.SUCCESS
                pattern_metrics.record_operation(start_time, end_time, success)
            
            pattern_metrics.stop_monitoring()
            patterns_performance[pattern.value] = pattern_metrics.get_metrics()
        
        # 分析性能差异
        for pattern_name, perf_data in patterns_performance.items():
            print(f"\n{pattern_name} Performance:")
            print(f"  Average Response Time: {perf_data['response_times']['avg']:.3f}s")
            print(f"  Success Rate: {perf_data['success_rate']:.2%}")
            print(f"  Throughput: {perf_data['throughput']:.2f} ops/sec")
        
        # 验证性能合理性
        for pattern_name, perf_data in patterns_performance.items():
            assert perf_data["success_rate"] >= 0.8  # 所有模式至少80%成功率
            
            # 并行模式应该最快
            if pattern_name == "parallel":
                assert perf_data["response_times"]["avg"] < 2.0
            
            # 顺序模式可能较慢但应该稳定
            if pattern_name == "sequential":
                assert perf_data["success_rate"] >= 0.95


class TestWorkflowEnginePerformance:
    """工作流引擎性能测试"""
    
    @pytest.fixture
    def workflow_engine(self):
        return WorkflowEngine()

    @pytest.mark.asyncio
    async def test_complex_workflow_performance(self, workflow_engine, performance_agents):
        """测试复杂工作流性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 注册Agent
        for agent in performance_agents[:20]:
            await workflow_engine.register_agent(agent)
        
        # 创建复杂工作流（多层依赖）
        complex_steps = []
        
        # 第一层：初始化步骤
        for i in range(3):
            step = WorkflowStep(
                step_id=f"init_{i}",
                name=f"Initialization {i}",
                step_type=WorkflowStepType.AGENT_TASK,
                config={"agent_id": f"perf_agent_{i}"},
                timeout=30
            )
            complex_steps.append(step)
        
        # 第二层：依赖第一层的步骤
        for i in range(5):
            step = WorkflowStep(
                step_id=f"process_{i}",
                name=f"Processing {i}",
                step_type=WorkflowStepType.AGENT_TASK,
                config={"agent_id": f"perf_agent_{i+3}"},
                dependencies=[f"init_{i%3}"],
                timeout=30
            )
            complex_steps.append(step)
        
        # 第三层：并行处理步骤
        parallel_step = WorkflowStep(
            step_id="parallel_processing",
            name="Parallel Processing",
            step_type=WorkflowStepType.PARALLEL,
            config={
                "parallel_steps": [
                    {
                        "step_id": f"parallel_{i}",
                        "step_type": "agent_task",
                        "config": {"agent_id": f"perf_agent_{i+8}"}
                    }
                    for i in range(6)
                ]
            },
            dependencies=[f"process_{i}" for i in range(5)],
            timeout=60
        )
        complex_steps.append(parallel_step)
        
        # 第四层：最终汇总
        final_step = WorkflowStep(
            step_id="finalization",
            name="Final Processing",
            step_type=WorkflowStepType.AGENT_TASK,
            config={"agent_id": "perf_agent_19"},
            dependencies=["parallel_processing"],
            timeout=30
        )
        complex_steps.append(final_step)
        
        complex_workflow = WorkflowDefinition(
            workflow_id="complex_performance_workflow",
            name="Complex Performance Workflow",
            steps=complex_steps,
            timeout=300
        )
        
        # 注册工作流
        start_time = time.time()
        await workflow_engine.register_workflow(complex_workflow)
        end_time = time.time()
        metrics.record_operation(start_time, end_time, True)
        
        # 执行复杂工作流
        task = UniversalTask(
            task_id="complex_performance_task",
            task_type=TaskType.WORKFLOW,
            description="Complex workflow performance test"
        )
        
        start_time = time.time()
        execution_id = await workflow_engine.start_workflow("complex_performance_workflow", task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=60)
        end_time = time.time()
        
        success = execution.status.value == "completed"
        metrics.record_operation(start_time, end_time, success)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.95
        assert performance_data["response_times"]["avg"] < 30.0  # 平均30秒内完成
        assert len(execution.step_executions) >= 10  # 至少执行了10个步骤

    @pytest.mark.asyncio
    async def test_concurrent_workflow_executions(self, workflow_engine, performance_agents):
        """测试并发工作流执行性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 注册Agent
        for agent in performance_agents[:50]:
            await workflow_engine.register_agent(agent)
        
        # 创建简单但资源密集的工作流
        intensive_workflow = WorkflowDefinition(
            workflow_id="intensive_workflow",
            name="Resource Intensive Workflow",
            steps=[
                WorkflowStep(
                    step_id="intensive_processing",
                    name="Intensive Processing",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {
                                "step_id": f"intensive_{i}",
                                "step_type": "agent_task",
                                "config": {"agent_id": f"perf_agent_{i}"}
                            }
                            for i in range(10)
                        ]
                    },
                    timeout=60
                )
            ],
            timeout=120
        )
        
        await workflow_engine.register_workflow(intensive_workflow)
        
        # 并发启动多个工作流
        num_concurrent = 20
        execution_tasks = []
        
        for i in range(num_concurrent):
            task = UniversalTask(
                task_id=f"concurrent_workflow_task_{i}",
                task_type=TaskType.WORKFLOW,
                description=f"Concurrent workflow execution {i}"
            )
            
            start_time = time.time()
            coroutine = workflow_engine.start_workflow("intensive_workflow", task)
            execution_tasks.append((coroutine, start_time))
        
        # 启动所有工作流
        execution_ids = []
        for coroutine, start_time in execution_tasks:
            execution_id = await coroutine
            execution_ids.append((execution_id, start_time))
        
        # 等待所有完成
        completion_tasks = []
        for execution_id, start_time in execution_ids:
            coroutine = workflow_engine.wait_for_completion(execution_id, timeout=30)
            completion_tasks.append((coroutine, start_time))
        
        # 收集结果
        for coroutine, start_time in completion_tasks:
            execution = await coroutine
            end_time = time.time()
            success = execution.status.value == "completed"
            metrics.record_operation(start_time, end_time, success)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.85  # 85%成功率
        assert performance_data["throughput"] >= 1.0  # 至少每秒1个工作流
        assert performance_data["response_times"]["p95"] < 25.0  # 95%在25秒内完成

    @pytest.mark.asyncio
    async def test_workflow_memory_scalability(self, workflow_engine, performance_agents):
        """测试工作流内存可扩展性"""
        initial_memory = psutil.Process().memory_info().rss
        
        # 注册Agent
        for agent in performance_agents[:30]:
            await workflow_engine.register_agent(agent)
        
        # 创建内存密集型工作流
        memory_steps = []
        for i in range(100):  # 100步工作流
            step = WorkflowStep(
                step_id=f"memory_step_{i}",
                name=f"Memory Step {i}",
                step_type=WorkflowStepType.AGENT_TASK,
                config={
                    "agent_id": f"perf_agent_{i % 30}",
                    "large_data": "x" * 1000  # 模拟大数据
                },
                dependencies=[f"memory_step_{i-1}"] if i > 0 else [],
                timeout=5
            )
            memory_steps.append(step)
        
        memory_workflow = WorkflowDefinition(
            workflow_id="memory_scalability_workflow",
            name="Memory Scalability Workflow",
            steps=memory_steps,
            timeout=600
        )
        
        await workflow_engine.register_workflow(memory_workflow)
        
        # 执行内存密集型工作流
        task = UniversalTask(
            task_id="memory_scalability_task",
            task_type=TaskType.WORKFLOW,
            description="Memory scalability test"
        )
        
        execution_id = await workflow_engine.start_workflow("memory_scalability_workflow", task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=120)
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存使用断言
        assert memory_increase < 500 * 1024 * 1024  # 内存增长小于500MB
        assert execution.status.value == "completed"
        
        # 强制垃圾回收
        gc.collect()
        
        # 检查内存是否有效释放
        post_gc_memory = psutil.Process().memory_info().rss
        memory_after_gc = post_gc_memory - initial_memory
        assert memory_after_gc < memory_increase * 0.8  # GC后内存应该减少


class TestTeamManagerPerformance:
    """团队管理器性能测试"""
    
    @pytest.fixture
    def team_manager(self):
        return TeamManager()

    @pytest.mark.asyncio
    async def test_large_scale_team_management(self, team_manager, performance_agents):
        """测试大规模团队管理性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 创建100个团队，每个团队5-15个成员
        num_teams = 100
        teams_created = []
        
        for i in range(num_teams):
            team_id = f"large_scale_team_{i}"
            team_size = 5 + (i % 11)  # 5-15个成员
            team_agents = performance_agents[i*2:(i*2)+team_size]
            
            start_time = time.time()
            await team_manager.create_team(
                team_id=team_id,
                team_name=f"Large Scale Team {i}",
                agents=team_agents,
                team_config={"max_size": 20}
            )
            end_time = time.time()
            
            metrics.record_operation(start_time, end_time, True)
            teams_created.append(team_id)
        
        # 并发执行团队任务
        team_tasks = []
        for i, team_id in enumerate(teams_created[:50]):  # 选择50个团队
            task = UniversalTask(
                task_id=f"large_scale_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Large scale team task {i}"
            )
            
            coroutine = team_manager.execute_team_task(
                team_id, task, CollaborationPattern.PARALLEL
            )
            team_tasks.append((coroutine, time.time()))
        
        # 执行所有团队任务
        results = []
        for coroutine, start_time in team_tasks:
            result = await coroutine
            end_time = time.time()
            success = result.final_result.status == ResultStatus.SUCCESS
            metrics.record_operation(start_time, end_time, success)
            results.append(result)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.90
        assert performance_data["throughput"] >= 10.0  # 每秒至少10个操作
        assert len(teams_created) == num_teams
        
        success_results = sum(1 for result in results 
                             if result.final_result.status == ResultStatus.SUCCESS)
        assert success_results >= len(results) * 0.9

    @pytest.mark.asyncio
    async def test_team_optimization_performance(self, team_manager, performance_agents):
        """测试团队优化性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 创建需要优化的团队
        team_id = "optimization_performance_team"
        
        # 创建性能参差不齐的Agent
        mixed_agents = []
        for i, agent in enumerate(performance_agents[:20]):
            # 设置不同的性能分数
            agent.performance_score = 0.3 + (i % 5) * 0.15
            mixed_agents.append(agent)
        
        await team_manager.create_team(
            team_id=team_id,
            team_name="Optimization Performance Team",
            agents=mixed_agents
        )
        
        # 执行基准任务
        baseline_tasks = []
        for i in range(10):
            task = UniversalTask(
                task_id=f"baseline_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Baseline task {i}"
            )
            
            start_time = time.time()
            result = await team_manager.execute_team_task(
                team_id, task, CollaborationPattern.ROUND_ROBIN
            )
            end_time = time.time()
            
            success = result.final_result.status == ResultStatus.SUCCESS
            metrics.record_operation(start_time, end_time, success)
        
        # 执行团队优化
        start_time = time.time()
        optimization_suggestions = await team_manager.get_optimization_suggestions(team_id)
        end_time = time.time()
        metrics.record_operation(start_time, end_time, True)
        
        # 应用优化建议
        if optimization_suggestions.get("suggested_additions"):
            high_performance_agents = [agent for agent in performance_agents[20:25] 
                                     if not hasattr(agent, 'performance_score')]
            for agent in high_performance_agents:
                agent.performance_score = 0.9
            
            for agent in high_performance_agents[:2]:
                start_time = time.time()
                await team_manager.add_team_member(
                    team_id, agent, CollaborationRole.EXPERT
                )
                end_time = time.time()
                metrics.record_operation(start_time, end_time, True)
        
        # 执行优化后任务
        for i in range(10):
            task = UniversalTask(
                task_id=f"optimized_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Optimized task {i}"
            )
            
            start_time = time.time()
            result = await team_manager.execute_team_task(
                team_id, task, CollaborationPattern.EXPERT_CONSULTATION
            )
            end_time = time.time()
            
            success = result.final_result.status == ResultStatus.SUCCESS
            metrics.record_operation(start_time, end_time, success)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 性能断言
        assert performance_data["success_rate"] >= 0.85
        assert performance_data["response_times"]["avg"] < 5.0


class TestStressTests:
    """压力测试"""

    @pytest.mark.asyncio
    async def test_system_overload_handling(self, performance_agents):
        """测试系统过载处理"""
        # 创建所有组件
        collaboration_manager = CollaborationManager()
        team_manager = TeamManager()
        workflow_engine = WorkflowEngine()
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # 注册大量Agent
        for agent in performance_agents:
            await workflow_engine.register_agent(agent)
        
        # 创建过载场景：大量团队、工作流、协作任务
        overload_tasks = []
        
        # 1. 创建大量团队
        for i in range(50):
            team_id = f"overload_team_{i}"
            team_agents = performance_agents[i*2:(i*2)+5]
            
            members = [
                TeamMember(agent=agent, role=CollaborationRole.CONTRIBUTOR,
                          capabilities=agent.capabilities)
                for agent in team_agents
            ]
            
            task = collaboration_manager.create_team(team_id, members)
            overload_tasks.append(task)
        
        # 等待团队创建完成
        await asyncio.gather(*overload_tasks)
        
        # 2. 创建大量工作流
        for i in range(20):
            workflow = WorkflowDefinition(
                workflow_id=f"overload_workflow_{i}",
                name=f"Overload Workflow {i}",
                steps=[
                    WorkflowStep(
                        step_id="overload_step",
                        name="Overload Step",
                        step_type=WorkflowStepType.PARALLEL,
                        config={
                            "parallel_steps": [
                                {"step_id": f"sub_{j}", "step_type": "agent_task",
                                 "config": {"agent_id": f"perf_agent_{j}"}}
                                for j in range(10)
                            ]
                        },
                        timeout=30
                    )
                ]
            )
            await workflow_engine.register_workflow(workflow)
        
        # 3. 同时执行大量任务
        concurrent_tasks = []
        
        # 协作任务
        for i in range(100):
            team_id = f"overload_team_{i % 50}"
            task = UniversalTask(
                task_id=f"overload_collab_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Overload collaboration task {i}"
            )
            
            coroutine = collaboration_manager.collaborate(
                team_id, task, CollaborationPattern.PARALLEL
            )
            concurrent_tasks.append(coroutine)
        
        # 工作流任务
        for i in range(50):
            workflow_id = f"overload_workflow_{i % 20}"
            task = UniversalTask(
                task_id=f"overload_workflow_task_{i}",
                task_type=TaskType.WORKFLOW,
                description=f"Overload workflow task {i}"
            )
            
            async def execute_workflow(wf_id, wf_task):
                execution_id = await workflow_engine.start_workflow(wf_id, wf_task)
                return await workflow_engine.wait_for_completion(execution_id, timeout=60)
            
            coroutine = execute_workflow(workflow_id, task)
            concurrent_tasks.append(coroutine)
        
        # 执行所有任务并记录性能
        start_time = time.time()
        
        try:
            # 使用超时来避免无限等待
            results = await asyncio.wait_for(
                asyncio.gather(*concurrent_tasks, return_exceptions=True),
                timeout=120.0
            )
            
            end_time = time.time()
            
            # 统计成功和失败
            success_count = 0
            failure_count = 0
            
            for result in results:
                if isinstance(result, Exception):
                    failure_count += 1
                else:
                    if hasattr(result, 'final_result'):
                        # 协作结果
                        if result.final_result.status == ResultStatus.SUCCESS:
                            success_count += 1
                        else:
                            failure_count += 1
                    elif hasattr(result, 'status'):
                        # 工作流结果
                        if result.status.value == "completed":
                            success_count += 1
                        else:
                            failure_count += 1
                    else:
                        failure_count += 1
            
            metrics.record_operation(start_time, end_time, success_count > failure_count)
            
        except asyncio.TimeoutError:
            end_time = time.time()
            metrics.record_operation(start_time, end_time, False)
            success_count = 0
            failure_count = len(concurrent_tasks)
        
        metrics.stop_monitoring()
        performance_data = metrics.get_metrics()
        
        # 压力测试断言（更宽松的标准）
        total_tasks = len(concurrent_tasks)
        success_rate = success_count / total_tasks if total_tasks > 0 else 0
        
        # 在极端压力下，系统应该至少处理一部分任务
        assert success_rate >= 0.3  # 至少30%的任务成功
        assert performance_data["memory"]["increase"] < 1024 * 1024 * 1024  # 内存增长小于1GB
        
        print(f"Stress Test Results:")
        print(f"  Total Tasks: {total_tasks}")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Memory Increase: {performance_data['memory']['increase'] / 1024 / 1024:.1f}MB")
        print(f"  Peak CPU: {performance_data['cpu']['peak']:.1f}%")

    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self, performance_agents):
        """测试资源耗尽后的恢复能力"""
        collaboration_manager = CollaborationManager()
        
        # 创建资源耗尽场景
        team_id = "resource_exhaustion_team"
        members = [
            TeamMember(agent=agent, role=CollaborationRole.CONTRIBUTOR,
                      capabilities=agent.capabilities)
            for agent in performance_agents[:50]  # 大团队
        ]
        
        await collaboration_manager.create_team(team_id, members)
        
        # 第一阶段：资源耗尽
        exhaustion_tasks = []
        for i in range(200):  # 大量任务
            task = UniversalTask(
                task_id=f"exhaustion_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Resource exhaustion task {i}"
            )
            
            coroutine = collaboration_manager.collaborate(
                team_id, task, CollaborationPattern.PARALLEL
            )
            exhaustion_tasks.append(coroutine)
        
        # 尝试执行所有任务（预期会有部分失败）
        try:
            await asyncio.wait_for(
                asyncio.gather(*exhaustion_tasks, return_exceptions=True),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pass  # 预期的超时
        
        # 第二阶段：恢复测试
        await asyncio.sleep(2.0)  # 等待系统恢复
        
        # 执行少量任务验证恢复
        recovery_tasks = []
        for i in range(5):
            task = UniversalTask(
                task_id=f"recovery_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Recovery test task {i}"
            )
            
            coroutine = collaboration_manager.collaborate(
                team_id, task, CollaborationPattern.SEQUENTIAL
            )
            recovery_tasks.append(coroutine)
        
        # 恢复阶段应该成功
        recovery_results = await asyncio.gather(*recovery_tasks, return_exceptions=True)
        
        recovery_success_count = 0
        for result in recovery_results:
            if not isinstance(result, Exception) and \
               hasattr(result, 'final_result') and \
               result.final_result.status == ResultStatus.SUCCESS:
                recovery_success_count += 1
        
        # 恢复断言
        recovery_rate = recovery_success_count / len(recovery_tasks)
        assert recovery_rate >= 0.8  # 恢复后至少80%成功率
        
        print(f"Recovery Test Results:")
        print(f"  Recovery Success Rate: {recovery_rate:.2%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"]) 