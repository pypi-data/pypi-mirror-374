#!/usr/bin/env python3
"""
业务能力层演示示例
展示协作管理、工作流引擎、团队管理的实际应用

运行方式: python examples/business_layer_demo.py
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入业务能力层组件
from layers.business.teams.collaboration_manager import (
    CollaborationManager, CollaborationPattern, CollaborationRole, TeamMember
)
from layers.business.teams.team_engine import TeamManager
from layers.business.workflows.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowStep, WorkflowStepType
)
from layers.business.project import ProjectManager

# 导入框架抽象层
from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class DemoAgent:
    """演示用的Agent实现"""
    
    def __init__(self, agent_id: str, name: str, role: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.performance_score = 0.8 + (hash(agent_id) % 20) / 100  # 0.8-0.99
        self.availability = True
        self.workload = 0
    
    async def execute(self, task: UniversalTask, context: UniversalContext = None) -> UniversalResult:
        """执行任务"""
        logger.info(f"🤖 {self.name} 开始执行任务: {task.description}")
        
        # 模拟处理时间（基于角色和任务类型）
        processing_time = self._calculate_processing_time(task)
        await asyncio.sleep(processing_time)
        
        # 生成结果数据
        result_data = self._generate_result_data(task)
        
        # 模拟偶尔的失败
        success_rate = self.performance_score
        if hash(f"{task.task_id}{self.agent_id}") % 100 < success_rate * 100:
            status = ResultStatus.SUCCESS
            logger.info(f"✅ {self.name} 成功完成任务: {task.description}")
        else:
            status = ResultStatus.ERROR
            result_data["error"] = "模拟的任务执行失败"
            logger.warning(f"❌ {self.name} 任务执行失败: {task.description}")
        
        return UniversalResult(
            task_id=task.task_id,
            status=status,
            data=result_data,
            metadata={
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "role": self.role,
                "processing_time": processing_time,
                "performance_score": self.performance_score
            }
        )
    
    def _calculate_processing_time(self, task: UniversalTask) -> float:
        """根据任务类型和Agent角色计算处理时间"""
        base_time = 0.1
        
        # 任务类型影响
        type_multipliers = {
            TaskType.ANALYSIS: 1.5,
            TaskType.CREATIVE: 2.0,
            TaskType.DECISION_MAKING: 1.2,
            TaskType.PROBLEM_SOLVING: 1.8,
            TaskType.PROJECT: 0.8
        }
        
        # 角色影响
        role_multipliers = {
            "project_manager": 0.8,
            "architect": 1.5,
            "developer": 1.2,
            "tester": 1.0,
            "designer": 1.3,
            "analyst": 1.4
        }
        
        multiplier = type_multipliers.get(task.task_type, 1.0) * \
                    role_multipliers.get(self.role, 1.0)
        
        return base_time * multiplier
    
    def _generate_result_data(self, task: UniversalTask) -> Dict[str, Any]:
        """根据角色和任务类型生成结果数据"""
        if self.role == "project_manager":
            return {
                "project_plan": "详细的项目计划",
                "timeline": "2周开发周期",
                "resource_allocation": "团队成员分配完成",
                "risk_assessment": "低风险项目"
            }
        elif self.role == "architect":
            return {
                "architecture_design": "系统架构设计图",
                "technical_specifications": "详细技术规格",
                "component_breakdown": ["前端模块", "后端API", "数据库设计"],
                "technology_stack": ["Python", "React", "PostgreSQL"]
            }
        elif self.role == "developer":
            return {
                "code_implementation": "功能模块实现完成",
                "unit_tests": "单元测试覆盖率95%",
                "code_quality": "代码审查通过",
                "documentation": "代码文档已更新"
            }
        elif self.role == "tester":
            return {
                "test_results": "所有测试用例通过",
                "test_coverage": "98%测试覆盖率",
                "bug_report": "发现并修复3个minor bug",
                "quality_metrics": "质量指标达标"
            }
        elif self.role == "designer":
            return {
                "ui_design": "用户界面设计完成",
                "user_experience": "用户体验优化建议",
                "design_assets": "设计资源包",
                "prototype": "交互原型链接"
            }
        elif self.role == "analyst":
            return {
                "data_analysis": "数据分析报告",
                "insights": ["用户行为洞察", "性能优化建议", "业务增长机会"],
                "metrics": {"准确率": 0.95, "处理速度": "1.2s"},
                "recommendations": "基于数据的建议"
            }
        else:
            return {
                "task_completed": True,
                "output": f"{self.role}完成了任务处理",
                "quality_score": self.performance_score
            }


class BusinessLayerDemo:
    """业务能力层演示主类"""
    
    def __init__(self):
        self.collaboration_manager = CollaborationManager()
        self.team_manager = TeamManager()
        self.workflow_engine = WorkflowEngine()
        self.project_manager = ProjectManager()
        
        # 创建演示用的Agent团队
        self.agents = self._create_demo_agents()
    
    def _create_demo_agents(self) -> List[DemoAgent]:
        """创建演示用的Agent团队"""
        agents_config = [
            ("pm_001", "Alice (项目经理)", "project_manager", 
             [AgentCapability.PROJECT_MANAGEMENT, AgentCapability.REASONING]),
            ("arch_001", "Bob (架构师)", "architect",
             [AgentCapability.ARCHITECTURE_DESIGN, AgentCapability.REASONING]),
            ("dev_001", "Charlie (前端开发)", "developer",
             [AgentCapability.CODE_GENERATION, AgentCapability.UI_UX_DESIGN]),
            ("dev_002", "Diana (后端开发)", "developer",
             [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING]),
            ("test_001", "Eve (测试工程师)", "tester",
             [AgentCapability.TESTING, AgentCapability.QUALITY_ASSURANCE]),
            ("design_001", "Frank (UI设计师)", "designer",
             [AgentCapability.UI_UX_DESIGN, AgentCapability.VISUALIZATION]),
            ("analyst_001", "Grace (数据分析师)", "analyst",
             [AgentCapability.DATA_ANALYSIS, AgentCapability.REASONING])
        ]
        
        agents = []
        for agent_id, name, role, capabilities in agents_config:
            agent = DemoAgent(agent_id, name, role, capabilities)
            agents.append(agent)
        
        return agents
    
    async def run_demo(self):
        """运行完整的业务能力层演示"""
        print("🚀 业务能力层演示开始")
        print("=" * 60)
        
        try:
            # 1. 协作管理演示
            await self._demo_collaboration_management()
            
            # 2. 工作流引擎演示
            await self._demo_workflow_engine()
            
            # 3. 团队管理演示
            await self._demo_team_management()
            
            # 4. 综合项目演示
            await self._demo_integrated_project()
            
            print("\n🎉 业务能力层演示完成！")
            
        except Exception as e:
            logger.error(f"演示过程中发生错误: {e}")
            raise
    
    async def _demo_collaboration_management(self):
        """演示协作管理功能"""
        print("\n📋 1. 协作管理演示")
        print("-" * 40)
        
        # 创建开发团队
        team_id = "dev_team_demo"
        team_members = [
            TeamMember(agent=self.agents[1], role=CollaborationRole.LEADER,    # 架构师作为技术负责人
                      capabilities=self.agents[1].capabilities),
            TeamMember(agent=self.agents[2], role=CollaborationRole.CONTRIBUTOR, # 前端开发
                      capabilities=self.agents[2].capabilities),
            TeamMember(agent=self.agents[3], role=CollaborationRole.CONTRIBUTOR, # 后端开发
                      capabilities=self.agents[3].capabilities),
            TeamMember(agent=self.agents[4], role=CollaborationRole.REVIEWER,   # 测试工程师
                      capabilities=self.agents[4].capabilities)
        ]
        
        await self.collaboration_manager.create_team(team_id, team_members)
        print(f"✅ 创建开发团队 '{team_id}' 成功，包含 {len(team_members)} 名成员")
        
        # 演示不同的协作模式
        collaboration_patterns = [
            (CollaborationPattern.PARALLEL, "并行协作 - 多人同时进行代码审查"),
            (CollaborationPattern.EXPERT_CONSULTATION, "专家会诊 - 架构设计决策"),
            (CollaborationPattern.PEER_REVIEW, "同行评议 - 代码质量评估"),
            (CollaborationPattern.SEQUENTIAL, "顺序协作 - 开发测试流水线")
        ]
        
        for pattern, description in collaboration_patterns:
            print(f"\n🔄 演示协作模式: {pattern.value}")
            print(f"   场景: {description}")
            
            task = UniversalTask(
                task_id=f"collab_demo_{pattern.value}",
                task_type=TaskType.ANALYSIS,
                description=f"协作演示任务 - {description}",
                priority=TaskPriority.NORMAL,
                context=UniversalContext(
                    session_id="demo_session",
                    data={"collaboration_demo": True, "pattern": pattern.value}
                )
            )
            
            result = await self.collaboration_manager.collaborate(
                team_id=team_id,
                task=task,
                pattern=pattern
            )
            
            print(f"   ✅ 协作完成，状态: {result.final_result.status.value}")
            print(f"   📊 参与成员: {len(result.individual_results)} 人")
            print(f"   🎯 共识分数: {result.consensus_score:.2f}")
            
            if result.collaboration_metrics:
                execution_time = result.collaboration_metrics.get("execution_time", 0)
                print(f"   ⏱️ 执行时间: {execution_time:.2f}秒")
    
    async def _demo_workflow_engine(self):
        """演示工作流引擎功能"""
        print("\n⚙️ 2. 工作流引擎演示")
        print("-" * 40)
        
        # 注册Agent到工作流引擎
        for agent in self.agents:
            self.workflow_engine.register_agent(agent.agent_id, agent)
        
        print(f"✅ 注册了 {len(self.agents)} 个Agent到工作流引擎")
        
        # 定义软件开发工作流
        dev_workflow = WorkflowDefinition(
            workflow_id="software_development_workflow",
            name="软件开发标准流程",
            description="从需求分析到部署的完整软件开发流程",
            steps=[
                WorkflowStep(
                    step_id="requirement_analysis",
                    name="需求分析",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "analyst_001"},
                    timeout=60
                ),
                WorkflowStep(
                    step_id="architecture_design",
                    name="架构设计",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "arch_001"},
                    dependencies=["requirement_analysis"],
                    timeout=60
                ),
                WorkflowStep(
                    step_id="ui_design",
                    name="UI设计",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "design_001"},
                    dependencies=["architecture_design"],
                    timeout=60
                ),
                WorkflowStep(
                    step_id="parallel_development",
                    name="并行开发",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {
                                "step_id": "frontend_dev",
                                "step_type": "agent_task",
                                "config": {"agent_id": "dev_001"}
                            },
                            {
                                "step_id": "backend_dev",
                                "step_type": "agent_task",
                                "config": {"agent_id": "dev_002"}
                            }
                        ]
                    },
                    dependencies=["ui_design"],
                    timeout=120
                ),
                WorkflowStep(
                    step_id="integration_testing",
                    name="集成测试",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "test_001"},
                    dependencies=["parallel_development"],
                    timeout=60
                ),
                WorkflowStep(
                    step_id="project_review",
                    name="项目评审",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "pm_001"},
                    dependencies=["integration_testing"],
                    timeout=30
                )
            ],
            timeout=600
        )
        
        # 注册工作流
        await self.workflow_engine.register_workflow(dev_workflow)
        print(f"✅ 注册工作流 '{dev_workflow.name}' 成功，包含 {len(dev_workflow.steps)} 个步骤")
        
        # 执行工作流
        project_task = UniversalTask(
            task_id="demo_project_001",
            task_type=TaskType.PROJECT,
            description="演示项目：用户管理系统开发",
            priority=TaskPriority.HIGH,
            context=UniversalContext(
                session_id="workflow_demo",
                data={
                    "project_name": "用户管理系统",
                    "requirements": ["用户注册", "登录认证", "权限管理", "数据统计"],
                    "timeline": "2周"
                }
            )
        )
        
        print(f"\n🚀 开始执行工作流...")
        print(f"   项目: {project_task.description}")
        
        execution_id = await self.workflow_engine.start_workflow(
            "software_development_workflow", 
            project_task
        )
        
        # 监控工作流执行
        print(f"   执行ID: {execution_id}")
        print("   执行进度:")
        
        execution = await self.workflow_engine.wait_for_completion(execution_id, timeout=120)
        
        # 显示执行结果
        print(f"\n📊 工作流执行完成")
        print(f"   最终状态: {execution.status.value}")
        print(f"   执行步骤: {len(execution.step_executions)}")
        print(f"   开始时间: {execution.start_time.strftime('%H:%M:%S')}")
        print(f"   结束时间: {execution.end_time.strftime('%H:%M:%S')}")
        
        # 显示各步骤执行情况
        for step_id, step_execution in execution.step_executions.items():
            status_emoji = "✅" if step_execution.status.value == "completed" else "❌"
            print(f"   {status_emoji} {step_id}: {step_execution.status.value}")
    
    async def _demo_team_management(self):
        """演示团队管理功能"""
        print("\n👥 3. 团队管理演示")
        print("-" * 40)
        
        # 创建项目团队
        project_team_id = "full_stack_team"
        
        await self.team_manager.create_team(
            team_id=project_team_id,
            name="全栈开发团队",
            agents=self.agents,
            team_config={
                "max_size": 10,
                "collaboration_pattern": CollaborationPattern.HIERARCHICAL,
                "performance_threshold": 0.8
            }
        )
        
        print(f"✅ 创建全栈开发团队，包含 {len(self.agents)} 名成员")
        
        # 执行团队任务以建立基线性能
        baseline_tasks = []
        for i in range(3):
            task = UniversalTask(
                task_id=f"baseline_task_{i}",
                task_type=TaskType.ANALYSIS,
                description=f"基线性能测试任务 {i+1}",
                priority=TaskPriority.NORMAL
            )
            
            result = await self.team_manager.execute_team_task(
                project_team_id, task, CollaborationPattern.ROUND_ROBIN
            )
            baseline_tasks.append(result)
        
        print(f"✅ 完成 {len(baseline_tasks)} 个基线任务")
        
        # 获取团队性能指标
        performance = await self.team_manager.get_team_performance(project_team_id)
        print(f"\n📊 团队性能分析:")
        print(f"   整体评分: {performance['overall_score']:.2f}")
        print(f"   协作效率: {performance['collaboration_efficiency']:.2f}")
        print(f"   任务完成率: {performance['task_completion_rate']:.2f}")
        
        # 显示个人性能
        print(f"   个人表现:")
        for agent_id, score in performance['individual_scores'].items():
            agent_name = next(agent.name for agent in self.agents if agent.agent_id == agent_id)
            print(f"     • {agent_name}: {score:.2f}")
        
        # 获取优化建议
        optimization_suggestions = await self.team_manager.get_optimization_suggestions(project_team_id)
        print(f"\n💡 团队优化建议:")
        
        if optimization_suggestions:
            for suggestion in optimization_suggestions:
                suggestion_type = suggestion.get("type", "未知")
                description = suggestion.get("description", "无描述")
                impact = suggestion.get("impact", "未知")
                print(f"   • {suggestion_type}: {description} (影响: {impact})")
        else:
            print("   • 暂无优化建议")
        
        # 分析协作模式推荐
        pattern_recommendations = await self.team_manager.get_collaboration_pattern_recommendations(project_team_id)
        print(f"\n🎯 协作模式推荐:")
        
        if isinstance(pattern_recommendations, dict) and "pattern_rankings" in pattern_recommendations:
            for pattern, score in pattern_recommendations["pattern_rankings"].items():
                print(f"   • {pattern}: {score:.2f}")
        else:
            print("   • 暂无协作模式推荐")
    
    async def _demo_integrated_project(self):
        """演示综合项目管理"""
        print("\n🏗️ 4. 综合项目演示")
        print("-" * 40)
        
        # 创建项目
        project_config = {
            "project_id": "demo_ecommerce_project",
            "name": "电商平台开发项目",
            "description": "开发一个完整的电商平台，包含用户管理、商品管理、订单处理等功能",
            "timeline": {
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30)
            },
            "requirements": {
                "features": [
                    "用户注册登录",
                    "商品浏览搜索", 
                    "购物车管理",
                    "订单处理",
                    "支付集成",
                    "后台管理"
                ],
                "quality_standards": {
                    "test_coverage": 90,
                    "performance": "页面加载<2s",
                    "security": "OWASP标准"
                }
            }
        }
        
        project_id = self.project_manager.create_project(project_config["name"], project_config["description"])
        print(f"✅ 创建项目: {project_config['name']}")
        print(f"   项目ID: {project_id}")
        print(f"   功能模块: {len(project_config['requirements']['features'])} 个")
        
        # 为项目分配团队
        project_team_id = "ecommerce_dev_team"
        
        await self.team_manager.create_team(
            team_id=project_team_id,
            name="电商开发团队",
            agents=self.agents,
            team_config={
                "project_id": project_id,
                "collaboration_pattern": CollaborationPattern.HIERARCHICAL,
                "specialization": "full_stack_development"
            }
        )
        
        self.project_manager.assign_team(project_id, project_team_id)
        print(f"✅ 分配团队到项目，团队规模: {len(self.agents)} 人")
        
        # 注册项目Agent到工作流引擎
        for agent in self.agents:
            self.workflow_engine.register_agent(agent.agent_id, agent)
        
        # 定义电商项目工作流
        ecommerce_workflow = WorkflowDefinition(
            workflow_id="ecommerce_development_workflow",
            name="电商平台开发流程",
            steps=[
                # 项目启动
                WorkflowStep(
                    step_id="project_kickoff",
                    name="项目启动会议",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "pm_001"},
                    timeout=30
                ),
                # 需求分析和架构设计（并行）
                WorkflowStep(
                    step_id="analysis_and_design",
                    name="需求分析与架构设计",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {
                                "step_id": "business_analysis",
                                "step_type": "agent_task",
                                "config": {"agent_id": "analyst_001"}
                            },
                            {
                                "step_id": "system_architecture",
                                "step_type": "agent_task",
                                "config": {"agent_id": "arch_001"}
                            },
                            {
                                "step_id": "ui_ux_design",
                                "step_type": "agent_task",
                                "config": {"agent_id": "design_001"}
                            }
                        ]
                    },
                    dependencies=["project_kickoff"],
                    timeout=90
                ),
                # 核心功能开发
                WorkflowStep(
                    step_id="core_development",
                    name="核心功能开发",
                    step_type=WorkflowStepType.PARALLEL,
                    config={
                        "parallel_steps": [
                            {
                                "step_id": "frontend_development",
                                "step_type": "agent_task",
                                "config": {"agent_id": "dev_001"}
                            },
                            {
                                "step_id": "backend_api",
                                "step_type": "agent_task",
                                "config": {"agent_id": "dev_002"}
                            }
                        ]
                    },
                    dependencies=["analysis_and_design"],
                    timeout=150
                ),
                # 集成测试
                WorkflowStep(
                    step_id="integration_testing",
                    name="系统集成测试",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "test_001"},
                    dependencies=["core_development"],
                    timeout=60
                ),
                # 项目验收
                WorkflowStep(
                    step_id="project_acceptance",
                    name="项目验收评审",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={"agent_id": "pm_001"},
                    dependencies=["integration_testing"],
                    timeout=30
                )
            ],
            timeout=600
        )
        
        await self.workflow_engine.register_workflow(ecommerce_workflow)
        print(f"✅ 注册电商开发工作流，包含 {len(ecommerce_workflow.steps)} 个步骤")
        
        # 执行项目工作流
        project_task = UniversalTask(
            task_id="ecommerce_project_execution",
            task_type=TaskType.COMPLEX_PROJECT,
            description="执行电商平台开发项目",
            priority=TaskPriority.URGENT,
            context=UniversalContext(
                session_id="integrated_demo",
                data={
                    "project_id": project_config["project_id"],
                    "team_id": project_team_id,
                    "requirements": project_config["requirements"],
                    "timeline": project_config["timeline"]
                }
            )
        )
        
        print(f"\n🚀 开始执行综合项目工作流...")
        
        execution_id = await self.workflow_engine.start_workflow(
            "ecommerce_development_workflow",
            project_task
        )
        
        execution = await self.workflow_engine.wait_for_completion(execution_id, timeout=180)
        
        # 显示项目执行结果
        print(f"\n📊 项目执行结果:")
        print(f"   执行状态: {execution.status.value}")
        print(f"   完成步骤: {len(execution.step_executions)}")
        
        if execution.status.value == "completed":
            print(f"   🎉 项目成功完成！")
            
            # 获取最终团队性能
            final_performance = await self.team_manager.get_team_performance(project_team_id)
            print(f"   团队最终评分: {final_performance['overall_score']:.2f}")
            
            # 获取项目统计
            project_status = self.project_manager.get_project_status(project_id)
            print(f"   项目状态: {project_status.get('status', 'completed')}")
            
        else:
            print(f"   ⚠️ 项目执行遇到问题")
            
        # 显示详细的步骤执行情况
        print(f"\n📋 详细执行报告:")
        for step_id, step_execution in execution.step_executions.items():
            status_emoji = "✅" if step_execution.status.value == "completed" else "❌"
            duration = 0
            if step_execution.start_time and step_execution.end_time:
                duration = (step_execution.end_time - step_execution.start_time).total_seconds()
            
            print(f"   {status_emoji} {step_id}")
            print(f"      状态: {step_execution.status.value}")
            print(f"      耗时: {duration:.1f}秒")
            
            if step_execution.result:
                agent_name = getattr(step_execution.result.metadata, "agent_name", "未知")
                print(f"      执行者: {agent_name}")


async def main():
    """主函数"""
    print("🌟 Agent Development Center - 业务能力层演示")
    print("=" * 60)
    print("本演示将展示业务能力层的核心功能：")
    print("• 协作管理 - 多种Agent协作模式")
    print("• 工作流引擎 - 复杂业务流程编排")
    print("• 团队管理 - 智能团队优化")
    print("• 综合项目 - 端到端项目管理")
    print("=" * 60)
    
    # 创建并运行演示
    demo = BusinessLayerDemo()
    await demo.run_demo()
    
    print("\n" + "=" * 60)
    print("💡 演示要点总结：")
    print("• 业务能力层提供了丰富的Agent协作模式")
    print("• 工作流引擎支持复杂的业务流程编排")
    print("• 团队管理器能够智能优化团队配置")
    print("• 各组件可以无缝集成形成完整的业务解决方案")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 