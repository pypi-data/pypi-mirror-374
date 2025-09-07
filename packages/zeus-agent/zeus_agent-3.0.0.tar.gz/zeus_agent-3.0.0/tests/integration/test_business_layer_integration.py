"""
业务能力层集成测试
测试业务能力层各组件间的协同工作以及与其他层的集成
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from layers.business.teams.collaboration_manager import (
    CollaborationManager, CollaborationPattern, CollaborationRole, TeamMember
)
from layers.business.teams.team_engine import TeamManager
from layers.business.workflows.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowStep, WorkflowStepType
)
from layers.business.project import ProjectManager
from layers.business.communication_manager import BusinessCommunicationManager

from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class TestBusinessLayerIntegration:
    """业务能力层内部集成测试"""
    
    @pytest.fixture
    def business_components(self):
        """创建业务能力层所有组件"""
        return {
            "collaboration_manager": CollaborationManager(),
            "team_manager": TeamManager(),
            "workflow_engine": WorkflowEngine(),
            "project_manager": ProjectManager(),
            "communication_manager": BusinessCommunicationManager()
        }
    
    @pytest.fixture
    def mock_agents(self):
        """创建完整的模拟Agent团队"""
        agents = []
        roles_and_capabilities = [
            ("project_manager", [AgentCapability.PROJECT_MANAGEMENT, AgentCapability.REASONING]),
            ("architect", [AgentCapability.ARCHITECTURE_DESIGN, AgentCapability.REASONING]),
            ("developer_1", [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING]),
            ("developer_2", [AgentCapability.CODE_GENERATION, AgentCapability.TESTING]),
            ("tester", [AgentCapability.TESTING, AgentCapability.QUALITY_ASSURANCE]),
            ("designer", [AgentCapability.UI_UX_DESIGN, AgentCapability.VISUALIZATION]),
            ("analyst", [AgentCapability.DATA_ANALYSIS, AgentCapability.REASONING])
        ]
        
        for role, capabilities in roles_and_capabilities:
            agent = Mock(spec=UniversalAgent)
            agent.agent_id = f"{role}_agent"
            agent.name = f"{role.replace('_', ' ').title()} Agent"
            agent.role = role
            agent.capabilities = capabilities
            agent.performance_score = 0.8
            agent.availability = True
            
            async def mock_execute(task, agent_role=role):
                await asyncio.sleep(0.1)  # 模拟处理时间
                
                # 根据角色返回不同类型的结果
                if "manager" in agent_role:
                    result_data = {"plan": "Project plan created", "timeline": "2 weeks"}
                elif "developer" in agent_role:
                    result_data = {"code": "Implementation completed", "tests": "Unit tests passed"}
                elif "tester" in agent_role:
                    result_data = {"test_results": "All tests passed", "coverage": "95%"}
                elif "designer" in agent_role:
                    result_data = {"design": "UI mockups created", "prototype": "Interactive prototype"}
                else:
                    result_data = {"analysis": "Analysis completed", "insights": ["insight1", "insight2"]}
                
                return UniversalResult(
                    task_id=task.task_id,
                    status=ResultStatus.SUCCESS,
                    data=result_data,
                    metadata={"agent_id": agent.agent_id, "role": agent_role}
                )
            
            agent.execute = mock_execute
            agents.append(agent)
        
        return agents

    @pytest.mark.asyncio
    async def test_team_workflow_integration(self, business_components, mock_agents):
        """测试团队管理与工作流引擎的集成"""
        team_manager = business_components["team_manager"]
        workflow_engine = business_components["workflow_engine"]
        collaboration_manager = business_components["collaboration_manager"]
        
        # 1. 创建开发团队
        team_id = "dev_team_integration"
        dev_agents = mock_agents[:5]  # PM, 架构师, 2个开发者, 测试者
        
        await team_manager.create_team(
            team_id=team_id,
            team_name="Development Team",
            agents=dev_agents,
            team_config={
                "collaboration_pattern": CollaborationPattern.HIERARCHICAL,
                "max_size": 10
            }
        )
        
        # 2. 注册Agent到工作流引擎
        for agent in dev_agents:
            await workflow_engine.register_agent(agent)
        
        # 3. 定义软件开发工作流
        dev_workflow = WorkflowDefinition(
            workflow_id="software_dev_workflow",
            name="Software Development Workflow",
            steps=[
                WorkflowStep(
                    step_id="planning",
                    name="Project Planning",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "project_manager_agent"},
                    timeout=60
                ),
                WorkflowStep(
                    step_id="architecture",
                    name="Architecture Design",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "architect_agent"},
                    dependencies=["planning"],
                    timeout=60
                ),
                WorkflowStep(
                    step_id="development",
                    name="Parallel Development",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {
                                "step_id": "dev_1",
                                "step_type": "agent_task",
                                "config": {"agent_id": "developer_1_agent"}
                            },
                            {
                                "step_id": "dev_2",
                                "step_type": "agent_task", 
                                "config": {"agent_id": "developer_2_agent"}
                            }
                        ]
                    },
                    dependencies=["architecture"],
                    timeout=120
                ),
                WorkflowStep(
                    step_id="testing",
                    name="Quality Assurance",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "tester_agent"},
                    dependencies=["development"],
                    timeout=60
                )
            ],
            timeout=300
        )
        
        # 4. 注册工作流
        await workflow_engine.register_workflow(dev_workflow)
        
        # 5. 创建项目任务
        project_task = UniversalTask(
            task_id="integration_project",
            task_type=TaskType.PROJECT,
            description="Develop new feature with team workflow integration",
            priority=TaskPriority.HIGH,
            context=UniversalContext(
                session_id="integration_session",
                data={
                    "feature_requirements": "User authentication system",
                    "deadline": "2024-02-01",
                    "team_id": team_id
                }
            )
        )
        
        # 6. 执行工作流
        execution_id = await workflow_engine.start_workflow("software_dev_workflow", project_task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=30)
        
        # 7. 验证集成结果
        assert execution.status.value == "completed"
        assert len(execution.step_executions) == 4
        
        # 验证每个步骤都成功完成
        for step_id in ["planning", "architecture", "development", "testing"]:
            if step_id in execution.step_executions:
                step_execution = execution.step_executions[step_id]
                assert step_execution.status.value == "completed"
        
        # 8. 验证团队性能指标
        team_performance = await team_manager.get_team_performance(team_id)
        assert team_performance["overall_score"] > 0.5

    @pytest.mark.asyncio
    async def test_collaboration_workflow_integration(self, business_components, mock_agents):
        """测试协作管理与工作流的深度集成"""
        collaboration_manager = business_components["collaboration_manager"]
        workflow_engine = business_components["workflow_engine"]
        
        # 1. 创建协作团队
        team_id = "collaboration_integration_team"
        collab_agents = mock_agents[2:6]  # 开发者、测试者、设计师、分析师
        
        members = [
            TeamMember(agent=collab_agents[0], role=CollaborationRole.LEADER,
                      capabilities=collab_agents[0].capabilities),
            TeamMember(agent=collab_agents[1], role=CollaborationRole.EXPERT,
                      capabilities=collab_agents[1].capabilities),
            TeamMember(agent=collab_agents[2], role=CollaborationRole.CONTRIBUTOR,
                      capabilities=collab_agents[2].capabilities),
            TeamMember(agent=collab_agents[3], role=CollaborationRole.REVIEWER,
                      capabilities=collab_agents[3].capabilities)
        ]
        
        await collaboration_manager.create_team(team_id, members)
        
        # 2. 注册Agent到工作流引擎
        for agent in collab_agents:
            await workflow_engine.register_agent(agent)
        
        # 3. 定义协作工作流（包含多种协作模式）
        collaboration_workflow = WorkflowDefinition(
            workflow_id="collaboration_workflow",
            name="Multi-Pattern Collaboration Workflow",
            steps=[
                WorkflowStep(
                    step_id="brainstorm",
                    name="Parallel Brainstorming",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "collaboration_pattern": "parallel",
                        "team_id": team_id,
                        "parallel_steps": [
                            {"step_id": "idea_1", "step_type": "agent_task", 
                             "config": {"agent_id": "developer_1_agent"}},
                            {"step_id": "idea_2", "step_type": "agent_task",
                             "config": {"agent_id": "designer_agent"}},
                            {"step_id": "idea_3", "step_type": "agent_task",
                             "config": {"agent_id": "analyst_agent"}}
                        ]
                    },
                    timeout=90
                ),
                WorkflowStep(
                    step_id="expert_review",
                    name="Expert Consultation",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "collaboration_pattern": "expert_consultation",
                        "team_id": team_id,
                        "agent_id": "tester_agent"
                    },
                    dependencies=["brainstorm"],
                    timeout=60
                ),
                WorkflowStep(
                    step_id="consensus_decision",
                    name="Consensus Building",
                    step_type=WorkflowStepType.CONDITION,
                    config={
                        "collaboration_pattern": "consensus",
                        "team_id": team_id,
                        "condition": "consensus_score >= 0.8"
                    },
                    dependencies=["expert_review"],
                    timeout=60
                )
            ],
            timeout=300
        )
        
        await workflow_engine.register_workflow(collaboration_workflow)
        
        # 4. 执行协作工作流
        collab_task = UniversalTask(
            task_id="collaboration_integration_task",
            task_type=TaskType.COLLABORATION,
            description="Multi-pattern collaboration integration test",
            priority=TaskPriority.MEDIUM
        )
        
        execution_id = await workflow_engine.start_workflow("collaboration_workflow", collab_task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=30)
        
        # 5. 验证协作工作流结果
        assert execution.status.value == "completed"
        
        # 验证协作历史记录
        collab_history = collaboration_manager.collaboration_history
        assert len(collab_history) > 0

    @pytest.mark.asyncio
    async def test_project_team_workflow_integration(self, business_components, mock_agents):
        """测试项目管理、团队管理和工作流的三方集成"""
        project_manager = business_components["project_manager"]
        team_manager = business_components["team_manager"]
        workflow_engine = business_components["workflow_engine"]
        
        # 1. 创建项目
        project_config = {
            "project_id": "integration_project_001",
            "name": "Full Stack Integration Project",
            "description": "Complete integration test project",
            "timeline": {
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30)
            },
            "requirements": {
                "features": ["authentication", "dashboard", "reporting"],
                "quality_standards": {"test_coverage": 90, "performance": "sub_2s"}
            }
        }
        
        project = await project_manager.create_project(project_config)
        
        # 2. 为项目分配团队
        project_team_id = f"team_{project_config['project_id']}"
        project_agents = mock_agents  # 使用全部Agent
        
        await team_manager.create_team(
            team_id=project_team_id,
            team_name=f"Team for {project_config['name']}",
            agents=project_agents,
            team_config={
                "project_id": project_config["project_id"],
                "collaboration_pattern": CollaborationPattern.HIERARCHICAL
            }
        )
        
        # 3. 将团队分配给项目
        await project_manager.assign_team(project_config["project_id"], project_team_id)
        
        # 4. 注册项目Agent到工作流引擎
        for agent in project_agents:
            await workflow_engine.register_agent(agent)
        
        # 5. 定义项目工作流
        project_workflow = WorkflowDefinition(
            workflow_id="full_project_workflow",
            name="Complete Project Workflow",
            steps=[
                # 项目启动阶段
                WorkflowStep(
                    step_id="project_kickoff",
                    name="Project Kickoff",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "project_manager_agent"},
                    timeout=30
                ),
                # 需求分析阶段
                WorkflowStep(
                    step_id="requirements_analysis",
                    name="Requirements Analysis",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {"step_id": "business_analysis", "step_type": "agent_task",
                             "config": {"agent_id": "analyst_agent"}},
                            {"step_id": "technical_analysis", "step_type": "agent_task",
                             "config": {"agent_id": "architect_agent"}}
                        ]
                    },
                    dependencies=["project_kickoff"],
                    timeout=60
                ),
                # 设计阶段
                WorkflowStep(
                    step_id="design_phase",
                    name="Design Phase",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {"step_id": "ui_design", "step_type": "agent_task",
                             "config": {"agent_id": "designer_agent"}},
                            {"step_id": "architecture_design", "step_type": "agent_task",
                             "config": {"agent_id": "architect_agent"}}
                        ]
                    },
                    dependencies=["requirements_analysis"],
                    timeout=90
                ),
                # 开发阶段
                WorkflowStep(
                    step_id="development_phase",
                    name="Development Phase",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {"step_id": "frontend_dev", "step_type": "agent_task",
                             "config": {"agent_id": "developer_1_agent"}},
                            {"step_id": "backend_dev", "step_type": "agent_task",
                             "config": {"agent_id": "developer_2_agent"}}
                        ]
                    },
                    dependencies=["design_phase"],
                    timeout=120
                ),
                # 测试阶段
                WorkflowStep(
                    step_id="testing_phase",
                    name="Testing Phase",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "tester_agent"},
                    dependencies=["development_phase"],
                    timeout=60
                ),
                # 项目收尾
                WorkflowStep(
                    step_id="project_closure",
                    name="Project Closure",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "project_manager_agent"},
                    dependencies=["testing_phase"],
                    timeout=30
                )
            ],
            timeout=600
        )
        
        await workflow_engine.register_workflow(project_workflow)
        
        # 6. 启动项目工作流
        project_task = UniversalTask(
            task_id="full_project_task",
            task_type=TaskType.PROJECT,
            description="Execute complete project workflow",
            priority=TaskPriority.HIGH,
            context=UniversalContext(
                session_id="project_session",
                data={
                    "project_id": project_config["project_id"],
                    "team_id": project_team_id,
                    "requirements": project_config["requirements"]
                }
            )
        )
        
        execution_id = await workflow_engine.start_workflow("full_project_workflow", project_task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=60)
        
        # 7. 验证项目执行结果
        assert execution.status.value == "completed"
        assert len(execution.step_executions) == 6
        
        # 验证项目状态更新
        project_status = await project_manager.get_project_status(project_config["project_id"])
        assert project_status["status"] in ["in_progress", "completed"]
        
        # 验证团队性能
        team_performance = await team_manager.get_team_performance(project_team_id)
        assert team_performance["overall_score"] > 0.6
        
        # 验证工作流执行质量
        workflow_stats = workflow_engine.get_workflow_statistics("full_project_workflow")
        assert workflow_stats["success_rate"] > 0.8


class TestCrossLayerIntegration:
    """跨层集成测试"""
    
    @pytest.fixture
    def business_components(self):
        return {
            "collaboration_manager": CollaborationManager(),
            "team_manager": TeamManager(),
            "workflow_engine": WorkflowEngine(),
            "communication_manager": BusinessCommunicationManager()
        }
    
    @pytest.fixture
    def mock_framework_layer(self):
        """模拟框架抽象层"""
        framework_mock = Mock()
        
        # 模拟Agent工厂
        framework_mock.agent_factory.create_agent = AsyncMock()
        framework_mock.agent_factory.get_available_agents = AsyncMock(return_value=[])
        
        # 模拟上下文管理
        framework_mock.context_manager.create_context = AsyncMock()
        framework_mock.context_manager.update_context = AsyncMock()
        
        return framework_mock
    
    @pytest.fixture
    def mock_cognitive_layer(self):
        """模拟认知架构层"""
        cognitive_mock = Mock()
        
        # 模拟认知Agent
        cognitive_mock.cognitive_agent.process_task = AsyncMock()
        cognitive_mock.memory_system.store_experience = AsyncMock()
        cognitive_mock.learning_module.update_knowledge = AsyncMock()
        
        return cognitive_mock

    @pytest.mark.asyncio
    async def test_business_framework_integration(self, business_components, mock_framework_layer, mock_agents):
        """测试业务能力层与框架抽象层的集成"""
        communication_manager = business_components["communication_manager"]
        team_manager = business_components["team_manager"]
        
        # 1. 设置跨层通信
        await communication_manager.register_layer_connection("framework", mock_framework_layer)
        
        # 2. 创建团队
        team_id = "framework_integration_team"
        await team_manager.create_team(
            team_id=team_id,
            team_name="Framework Integration Team",
            agents=mock_agents[:3]
        )
        
        # 3. 请求框架层创建专门的Agent
        agent_request = {
            "agent_type": "specialized_analyst",
            "capabilities": [AgentCapability.DATA_ANALYSIS, AgentCapability.REASONING],
            "performance_requirements": {"min_score": 0.8}
        }
        
        # 模拟框架层响应
        specialized_agent = Mock(spec=UniversalAgent)
        specialized_agent.agent_id = "specialized_analyst_001"
        specialized_agent.capabilities = agent_request["capabilities"]
        mock_framework_layer.agent_factory.create_agent.return_value = specialized_agent
        
        # 4. 通过层间通信请求Agent
        response = await communication_manager.send_layer_request(
            target_layer="framework",
            request_type="create_agent",
            data=agent_request
        )
        
        # 5. 验证跨层通信
        mock_framework_layer.agent_factory.create_agent.assert_called_once()
        assert response is not None
        
        # 6. 将新Agent添加到团队
        await team_manager.add_team_member(
            team_id, specialized_agent, CollaborationRole.EXPERT
        )
        
        # 验证团队更新
        team = team_manager.teams[team_id]
        assert len(team["members"]) == 4

    @pytest.mark.asyncio
    async def test_business_cognitive_integration(self, business_components, mock_cognitive_layer, mock_agents):
        """测试业务能力层与认知架构层的集成"""
        communication_manager = business_components["communication_manager"]
        collaboration_manager = business_components["collaboration_manager"]
        
        # 1. 设置与认知层的连接
        await communication_manager.register_layer_connection("cognitive", mock_cognitive_layer)
        
        # 2. 创建协作团队
        team_id = "cognitive_integration_team"
        members = [
            TeamMember(agent=mock_agents[0], role=CollaborationRole.LEADER,
                      capabilities=mock_agents[0].capabilities),
            TeamMember(agent=mock_agents[1], role=CollaborationRole.EXPERT,
                      capabilities=mock_agents[1].capabilities)
        ]
        
        await collaboration_manager.create_team(team_id, members)
        
        # 3. 执行需要认知增强的协作任务
        cognitive_task = UniversalTask(
            task_id="cognitive_enhanced_task",
            task_type=TaskType.COMPLEX_REASONING,
            description="Complex problem requiring cognitive enhancement",
            priority=TaskPriority.HIGH,
            context=UniversalContext(
                session_id="cognitive_session",
                data={
                    "complexity_level": "high",
                    "requires_learning": True,
                    "memory_intensive": True
                }
            )
        )
        
        # 4. 模拟认知层处理
        mock_cognitive_layer.cognitive_agent.process_task.return_value = UniversalResult(
            task_id=cognitive_task.task_id,
            status=ResultStatus.SUCCESS,
            data={
                "cognitive_analysis": "Deep analysis completed",
                "insights": ["insight1", "insight2", "insight3"],
                "confidence": 0.92
            },
            metadata={"cognitive_processing": True, "learning_applied": True}
        )
        
        # 5. 执行协作（集成认知处理）
        result = await collaboration_manager.collaborate(
            team_id=team_id,
            task=cognitive_task,
            pattern=CollaborationPattern.EXPERT_CONSULTATION,
            config={"cognitive_enhancement": True}
        )
        
        # 6. 验证认知集成
        assert result.final_result.status == ResultStatus.SUCCESS
        
        # 验证认知层调用
        mock_cognitive_layer.cognitive_agent.process_task.assert_called()
        mock_cognitive_layer.memory_system.store_experience.assert_called()

    @pytest.mark.asyncio
    async def test_end_to_end_integration(self, business_components, mock_framework_layer, mock_cognitive_layer, mock_agents):
        """测试端到端集成"""
        # 获取所有业务组件
        team_manager = business_components["team_manager"]
        workflow_engine = business_components["workflow_engine"]
        communication_manager = business_components["communication_manager"]
        
        # 1. 设置所有层间连接
        await communication_manager.register_layer_connection("framework", mock_framework_layer)
        await communication_manager.register_layer_connection("cognitive", mock_cognitive_layer)
        
        # 2. 创建端到端项目
        e2e_team_id = "e2e_integration_team"
        await team_manager.create_team(
            team_id=e2e_team_id,
            team_name="End-to-End Integration Team",
            agents=mock_agents,
            team_config={
                "enable_cognitive_enhancement": True,
                "framework_integration": True
            }
        )
        
        # 3. 注册Agent到工作流引擎
        for agent in mock_agents:
            await workflow_engine.register_agent(agent)
        
        # 4. 定义端到端工作流
        e2e_workflow = WorkflowDefinition(
            workflow_id="e2e_integration_workflow",
            name="End-to-End Integration Workflow",
            steps=[
                # 请求框架层创建专门Agent
                WorkflowStep(
                    step_id="request_specialized_agent",
                    name="Request Specialized Agent",
                    step_type=WorkflowStepType.SCRIPT,
                    config={
                        "script": "request_framework_agent('data_scientist')",
                        "layer_integration": True
                    },
                    timeout=30
                ),
                # 认知增强的分析阶段
                WorkflowStep(
                    step_id="cognitive_analysis",
                    name="Cognitive Enhanced Analysis",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "analyst_agent",
                        "cognitive_enhancement": True
                    },
                    dependencies=["request_specialized_agent"],
                    timeout=60
                ),
                # 团队协作阶段
                WorkflowStep(
                    step_id="team_collaboration",
                    name="Team Collaboration",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "team_id": e2e_team_id,
                        "collaboration_pattern": "expert_consultation",
                        "parallel_steps": [
                            {"step_id": "dev_work", "step_type": "agent_task",
                             "config": {"agent_id": "developer_1_agent"}},
                            {"step_id": "design_work", "step_type": "agent_task",
                             "config": {"agent_id": "designer_agent"}}
                        ]
                    },
                    dependencies=["cognitive_analysis"],
                    timeout=90
                ),
                # 最终整合
                WorkflowStep(
                    step_id="final_integration",
                    name="Final Integration",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "project_manager_agent",
                        "integrate_all_results": True
                    },
                    dependencies=["team_collaboration"],
                    timeout=30
                )
            ],
            timeout=300
        )
        
        await workflow_engine.register_workflow(e2e_workflow)
        
        # 5. 执行端到端工作流
        e2e_task = UniversalTask(
            task_id="e2e_integration_task",
            task_type=TaskType.COMPLEX_PROJECT,
            description="Complete end-to-end integration test",
            priority=TaskPriority.CRITICAL,
            context=UniversalContext(
                session_id="e2e_session",
                data={
                    "integration_scope": "full_stack",
                    "quality_requirements": "enterprise_grade",
                    "team_id": e2e_team_id
                }
            )
        )
        
        # 模拟各层响应
        mock_framework_layer.agent_factory.create_agent.return_value = mock_agents[-1]
        mock_cognitive_layer.cognitive_agent.process_task.return_value = UniversalResult(
            task_id=e2e_task.task_id,
            status=ResultStatus.SUCCESS,
            data={"enhanced_analysis": "Complete cognitive analysis"},
            metadata={"cognitive_processing": True}
        )
        
        execution_id = await workflow_engine.start_workflow("e2e_integration_workflow", e2e_task)
        execution = await workflow_engine.wait_for_completion(execution_id, timeout=60)
        
        # 6. 验证端到端集成
        assert execution.status.value == "completed"
        
        # 验证各层都被调用
        mock_framework_layer.agent_factory.create_agent.assert_called()
        mock_cognitive_layer.cognitive_agent.process_task.assert_called()
        
        # 验证团队性能
        final_performance = await team_manager.get_team_performance(e2e_team_id)
        assert final_performance["overall_score"] > 0.7
        
        # 验证工作流完整性
        assert len(execution.step_executions) == 4
        for step_execution in execution.step_executions.values():
            assert step_execution.status.value in ["completed", "skipped"]


class TestBusinessLayerPerformance:
    """业务能力层性能测试"""
    
    @pytest.fixture
    def business_components(self):
        return {
            "collaboration_manager": CollaborationManager(),
            "team_manager": TeamManager(),
            "workflow_engine": WorkflowEngine()
        }

    @pytest.mark.asyncio
    async def test_high_concurrency_collaboration(self, business_components, mock_agents):
        """测试高并发协作性能"""
        collaboration_manager = business_components["collaboration_manager"]
        
        # 创建多个团队
        teams = []
        for i in range(5):
            team_id = f"concurrent_team_{i}"
            members = [
                TeamMember(agent=mock_agents[j % len(mock_agents)], 
                          role=CollaborationRole.CONTRIBUTOR,
                          capabilities=mock_agents[j % len(mock_agents)].capabilities)
                for j in range(3)
            ]
            await collaboration_manager.create_team(team_id, members)
            teams.append(team_id)
        
        # 并发执行协作任务
        tasks = []
        for i in range(20):  # 20个并发任务
            task = UniversalTask(
                task_id=f"concurrent_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Concurrent analysis task {i}"
            )
            
            team_id = teams[i % len(teams)]
            coroutine = collaboration_manager.collaborate(
                team_id=team_id,
                task=task,
                pattern=CollaborationPattern.PARALLEL
            )
            tasks.append(coroutine)
        
        # 等待所有任务完成
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # 验证性能
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 10.0  # 应该在10秒内完成
        
        # 验证所有任务都成功
        success_count = sum(1 for result in results 
                           if result.final_result.status == ResultStatus.SUCCESS)
        assert success_count >= 18  # 至少90%成功率

    @pytest.mark.asyncio
    async def test_workflow_scalability(self, business_components, mock_agents):
        """测试工作流可扩展性"""
        workflow_engine = business_components["workflow_engine"]
        
        # 注册Agent
        for agent in mock_agents:
            await workflow_engine.register_agent(agent)
        
        # 创建可扩展工作流
        scalable_workflow = WorkflowDefinition(
            workflow_id="scalable_workflow",
            name="Scalable Workflow",
            steps=[
                WorkflowStep(
                    step_id=f"step_{i}",
                    name=f"Step {i}",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": mock_agents[i % len(mock_agents)].agent_id},
                    dependencies=[f"step_{i-1}"] if i > 0 else []
                )
                for i in range(10)  # 10步工作流
            ]
        )
        
        await workflow_engine.register_workflow(scalable_workflow)
        
        # 并发执行多个工作流实例
        execution_tasks = []
        for i in range(10):
            task = UniversalTask(
                task_id=f"scalable_task_{i}",
                task_type=TaskType.WORKFLOW,
                description=f"Scalable workflow execution {i}"
            )
            
            coroutine = workflow_engine.start_workflow("scalable_workflow", task)
            execution_tasks.append(coroutine)
        
        # 启动所有工作流
        execution_ids = await asyncio.gather(*execution_tasks)
        
        # 等待所有完成
        completion_tasks = [
            workflow_engine.wait_for_completion(execution_id, timeout=30)
            for execution_id in execution_ids
        ]
        
        executions = await asyncio.gather(*completion_tasks)
        
        # 验证可扩展性
        completed_count = sum(1 for execution in executions 
                             if execution.status.value == "completed")
        assert completed_count >= 8  # 至少80%成功完成

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, business_components, mock_agents):
        """测试内存使用效率"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        team_manager = business_components["team_manager"]
        
        # 创建大量团队和执行任务
        for i in range(50):
            team_id = f"memory_test_team_{i}"
            await team_manager.create_team(
                team_id=team_id,
                team_name=f"Memory Test Team {i}",
                agents=mock_agents[:3]
            )
            
            # 执行任务
            task = UniversalTask(
                task_id=f"memory_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"Memory test task {i}"
            )
            
            await team_manager.execute_team_task(
                team_id, task, CollaborationPattern.SEQUENTIAL
            )
        
        # 检查内存使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（小于200MB）
        assert memory_increase < 200 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 