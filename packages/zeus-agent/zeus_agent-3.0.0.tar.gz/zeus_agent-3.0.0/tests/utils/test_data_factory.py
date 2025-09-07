"""
测试数据工厂
用于生成各种测试数据
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from layers.framework.abstractions.agent import AgentCapability
from layers.framework.abstractions.task import TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus, ResultMetadata
from layers.business.workflows.workflow_engine import (
    WorkflowDefinition, WorkflowStep, WorkflowStepType
)
from layers.business.teams.collaboration_manager import (
    TeamMember, CollaborationRole, Team
)
from layers.application.orchestration.models import (
    ApplicationConfig, ApplicationType, ServiceConfig
)


@dataclass
class TestDataConfig:
    """测试数据配置"""
    num_agents: int = 5
    num_tasks: int = 10
    num_workflows: int = 3
    num_teams: int = 2
    num_applications: int = 3
    include_failure_scenarios: bool = True
    include_edge_cases: bool = True


class TestDataFactory:
    """测试数据工厂"""
    
    def __init__(self, config: Optional[TestDataConfig] = None):
        self.config = config or TestDataConfig()
        self.generated_ids = set()
    
    def generate_unique_id(self, prefix: str = "test") -> str:
        """生成唯一ID"""
        while True:
            unique_id = f"{prefix}_{uuid.uuid4().hex[:8]}"
            if unique_id not in self.generated_ids:
                self.generated_ids.add(unique_id)
                return unique_id
    
    def create_mock_agent(self, 
                          name: Optional[str] = None,
                          capabilities: Optional[List[AgentCapability]] = None,
                          **kwargs) -> Dict[str, Any]:
        """创建模拟Agent数据"""
        agent_data = {
            "agent_id": self.generate_unique_id("agent"),
            "name": name or f"Test Agent {len(self.generated_ids)}",
            "description": f"Test agent for testing purposes",
            "capabilities": capabilities or [AgentCapability.CONVERSATION, AgentCapability.CODE_GENERATION],
            "config": {
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "tags": ["test", "integration"]
            }
        }
        agent_data.update(kwargs)
        return agent_data
    
    def create_mock_task(self,
                         title: Optional[str] = None,
                         task_type: Optional[TaskType] = None,
                         priority: Optional[TaskPriority] = None,
                         **kwargs) -> Dict[str, Any]:
        """创建模拟任务数据"""
        task_data = {
            "task_id": self.generate_unique_id("task"),
            "title": title or f"Test Task {len(self.generated_ids)}",
            "description": f"Test task for testing purposes",
            "content": f"Execute test task {len(self.generated_ids)}",
            "task_type": task_type or TaskType.ANALYSIS,
            "priority": priority or TaskPriority.MEDIUM,
            "created_at": datetime.now(),
            "due_date": datetime.now() + timedelta(days=7),
            "tags": ["test", "integration"],
            "metadata": {
                "estimated_duration": 30,
                "complexity": "medium",
                "dependencies": []
            }
        }
        task_data.update(kwargs)
        return task_data
    
    def create_mock_context(self,
                           data: Optional[Dict[str, Any]] = None,
                           session_id: Optional[str] = None,
                           user_id: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """创建模拟上下文数据"""
        context_data = {
            "data": data or {
                "user_id": user_id or self.generate_unique_id("user"),
                "session_id": session_id or self.generate_unique_id("session"),
                "project_name": f"Test Project {len(self.generated_ids)}",
                "environment": "test",
                "timestamp": datetime.now().isoformat(),
                "test_data": {
                    "input": "test_input",
                    "expected_output": "test_output",
                    "parameters": {"param1": "value1", "param2": "value2"}
                }
            },
            "session_id": session_id or self.generate_unique_id("session"),
            "user_id": user_id or self.generate_unique_id("user"),
            "timestamp": datetime.now()
        }
        context_data.update(kwargs)
        return context_data
    
    def create_mock_result(self,
                           data: Optional[Any] = None,
                           status: Optional[ResultStatus] = None,
                           **kwargs) -> Dict[str, Any]:
        """创建模拟结果数据"""
        result_data = {
            "data": data or f"Test result {len(self.generated_ids)}",
            "status": status or ResultStatus.SUCCESS,
            "metadata": ResultMetadata(
                execution_time=1.5,
                agent_name=f"Test Agent {len(self.generated_ids)}",
                task_type="test_task"
            ),
            "error": None,
            "warnings": [],
            "created_at": datetime.now()
        }
        result_data.update(kwargs)
        return result_data
    
    def create_mock_workflow_step(self,
                                  step_id: Optional[str] = None,
                                  step_type: Optional[WorkflowStepType] = None,
                                  **kwargs) -> Dict[str, Any]:
        """创建模拟工作流步骤数据"""
        step_data = {
            "step_id": step_id or self.generate_unique_id("step"),
            "name": f"Test Step {len(self.generated_ids)}",
            "step_type": step_type or WorkflowStepType.AGENT_TASK,
            "description": f"Test workflow step {len(self.generated_ids)}",
            "config": {
                "agent_id": self.generate_unique_id("agent"),
                "task_content": f"Execute step {len(self.generated_ids)}",
                "task_type": "ANALYSIS",
                "timeout": 30,
                "retry_count": 3
            },
            "dependencies": [],
            "timeout": 30,
            "retry_count": 3
        }
        step_data.update(kwargs)
        return step_data
    
    def create_mock_workflow(self,
                             workflow_id: Optional[str] = None,
                             num_steps: Optional[int] = None,
                             **kwargs) -> Dict[str, Any]:
        """创建模拟工作流数据"""
        num_steps = num_steps or 3
        steps = []
        
        for i in range(num_steps):
            step_type = WorkflowStepType.AGENT_TASK if i % 2 == 0 else WorkflowStepType.DATA_PREPARATION
            step = self.create_mock_workflow_step(
                step_type=step_type,
                config={
                    "agent_id": self.generate_unique_id("agent"),
                    "task_content": f"Execute step {i+1}",
                    "task_type": "ANALYSIS" if step_type == WorkflowStepType.AGENT_TASK else "data_prep"
                }
            )
            steps.append(step)
        
        workflow_data = {
            "workflow_id": workflow_id or self.generate_unique_id("workflow"),
            "name": f"Test Workflow {len(self.generated_ids)}",
            "description": f"Test workflow with {num_steps} steps",
            "steps": steps,
            "version": "1.0.0",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": ["test", "integration"],
            "metadata": {
                "estimated_duration": num_steps * 5,
                "complexity": "medium",
                "category": "test"
            }
        }
        workflow_data.update(kwargs)
        return workflow_data
    
    def create_mock_team_member(self,
                                name: Optional[str] = None,
                                role: Optional[CollaborationRole] = None,
                                **kwargs) -> Dict[str, Any]:
        """创建模拟团队成员数据"""
        member_data = {
            "member_id": self.generate_unique_id("member"),
            "name": name or f"Test Member {len(self.generated_ids)}",
            "email": f"member{len(self.generated_ids)}@test.com",
            "role": role or CollaborationRole.DEVELOPER,
            "skills": ["Python", "Testing", "Integration"],
            "experience_years": 3,
            "availability": "full_time",
            "timezone": "UTC",
            "metadata": {
                "department": "Engineering",
                "manager": "Test Manager",
                "hire_date": (datetime.now() - timedelta(days=365)).isoformat()
            }
        }
        member_data.update(kwargs)
        return member_data
    
    def create_mock_team(self,
                         team_id: Optional[str] = None,
                         num_members: Optional[int] = None,
                         **kwargs) -> Dict[str, Any]:
        """创建模拟团队数据"""
        num_members = num_members or 3
        members = []
        
        for i in range(num_members):
            role = CollaborationRole.DEVELOPER if i == 0 else CollaborationRole.TESTER if i == 1 else CollaborationRole.PROJECT_MANAGER
            member = self.create_mock_team_member(role=role)
            members.append(member)
        
        team_data = {
            "team_id": team_id or self.generate_unique_id("team"),
            "name": f"Test Team {len(self.generated_ids)}",
            "description": f"Test team with {num_members} members",
            "members": members,
            "created_at": datetime.now(),
            "status": "active",
            "metadata": {
                "department": "Engineering",
                "project": f"Test Project {len(self.generated_ids)}",
                "sprint": "Sprint 1"
            }
        }
        team_data.update(kwargs)
        return team_data
    
    def create_mock_service_config(self,
                                   service_id: Optional[str] = None,
                                   **kwargs) -> Dict[str, Any]:
        """创建模拟服务配置数据"""
        service_data = {
            "service_id": service_id or self.generate_unique_id("service"),
            "name": f"Test Service {len(self.generated_ids)}",
            "service_type": "http",
            "endpoint": f"http://localhost:{8000 + len(self.generated_ids)}",
            "health_check": f"/health/{len(self.generated_ids)}",
            "config": {
                "timeout": 30,
                "max_retries": 3,
                "rate_limit": 100
            },
            "dependencies": [],
            "metadata": {
                "version": "1.0.0",
                "maintainer": "test@example.com",
                "documentation": f"https://docs.test.com/service/{len(self.generated_ids)}"
            }
        }
        service_data.update(kwargs)
        return service_data
    
    def create_mock_application_config(self,
                                      app_id: Optional[str] = None,
                                      app_type: Optional[ApplicationType] = None,
                                      **kwargs) -> Dict[str, Any]:
        """创建模拟应用配置数据"""
        app_data = {
            "app_id": app_id or self.generate_unique_id("app"),
            "name": f"Test Application {len(self.generated_ids)}",
            "version": "1.0.0",
            "app_type": app_type or ApplicationType.WEB_SERVICE,
            "description": f"Test application for testing purposes",
            "dependencies": [],
            "config": {
                "port": 8000 + len(self.generated_ids),
                "host": "localhost",
                "environment": "test",
                "debug": True
            },
            "services": [
                self.create_mock_service_config()
            ],
            "metadata": {
                "maintainer": "test@example.com",
                "repository": f"https://github.com/test/app{len(self.generated_ids)}",
                "license": "MIT"
            }
        }
        app_data.update(kwargs)
        return app_data
    
    def create_failure_scenario_data(self) -> Dict[str, Any]:
        """创建失败场景测试数据"""
        return {
            "failing_agent": self.create_mock_agent(
                name="Failing Agent",
                capabilities=[AgentCapability.CONVERSATION],
                config={"failure_rate": 1.0}  # 100%失败率
            ),
            "failing_task": self.create_mock_task(
                title="Failing Task",
                task_type=TaskType.ANALYSIS,
                priority=TaskPriority.HIGH,
                metadata={"expected_failure": True}
            ),
            "failing_workflow": self.create_mock_workflow(
                workflow_id="failing_workflow",
                num_steps=2,
                steps=[
                    self.create_mock_workflow_step(
                        step_type=WorkflowStepType.AGENT_TASK,
                        config={"agent_id": "failing_agent", "expected_failure": True}
                    )
                ]
            ),
            "invalid_context": self.create_mock_context(
                data={"invalid_data": None, "missing_required": True}
            )
        }
    
    def create_edge_case_data(self) -> Dict[str, Any]:
        """创建边界情况测试数据"""
        return {
            "empty_workflow": self.create_mock_workflow(
                workflow_id="empty_workflow",
                num_steps=0,
                steps=[]
            ),
            "single_step_workflow": self.create_mock_workflow(
                workflow_id="single_step_workflow",
                num_steps=1
            ),
            "large_workflow": self.create_mock_workflow(
                workflow_id="large_workflow",
                num_steps=100
            ),
            "minimal_context": self.create_mock_context(
                data={},
                session_id="",
                user_id=""
            ),
            "complex_context": self.create_mock_context(
                data={
                    "deeply_nested": {
                        "level1": {
                            "level2": {
                                "level3": {
                                    "level4": {
                                        "level5": "very_deep_value"
                                    }
                                }
                            }
                        }
                    },
                    "large_list": list(range(1000)),
                    "large_dict": {f"key_{i}": f"value_{i}" for i in range(1000)}
                }
            )
        }
    
    def create_comprehensive_test_suite(self) -> Dict[str, Any]:
        """创建综合测试套件数据"""
        test_suite = {
            "agents": [self.create_mock_agent() for _ in range(self.config.num_agents)],
            "tasks": [self.create_mock_task() for _ in range(self.config.num_tasks)],
            "workflows": [self.create_mock_workflow() for _ in range(self.config.num_workflows)],
            "teams": [self.create_mock_team() for _ in range(self.config.num_teams)],
            "applications": [self.create_mock_application_config() for _ in range(self.config.num_applications)],
            "contexts": [self.create_mock_context() for _ in range(5)],
            "results": [self.create_mock_result() for _ in range(5)]
        }
        
        if self.config.include_failure_scenarios:
            test_suite["failure_scenarios"] = self.create_failure_scenario_data()
        
        if self.config.include_edge_cases:
            test_suite["edge_cases"] = self.create_edge_case_data()
        
        return test_suite
    
    def reset_generated_ids(self):
        """重置生成的ID集合"""
        self.generated_ids.clear()


# 便捷函数
def create_test_agent(**kwargs) -> Dict[str, Any]:
    """快速创建测试Agent"""
    factory = TestDataFactory()
    return factory.create_mock_agent(**kwargs)


def create_test_task(**kwargs) -> Dict[str, Any]:
    """快速创建测试任务"""
    factory = TestDataFactory()
    return factory.create_mock_task(**kwargs)


def create_test_workflow(**kwargs) -> Dict[str, Any]:
    """快速创建测试工作流"""
    factory = TestDataFactory()
    return factory.create_mock_workflow(**kwargs)


def create_test_team(**kwargs) -> Dict[str, Any]:
    """快速创建测试团队"""
    factory = TestDataFactory()
    return factory.create_mock_team(**kwargs)


def create_test_application(**kwargs) -> Dict[str, Any]:
    """快速创建测试应用"""
    factory = TestDataFactory()
    return factory.create_mock_application_config(**kwargs)


if __name__ == "__main__":
    # 测试数据工厂
    factory = TestDataFactory()
    
    # 创建综合测试套件
    test_suite = factory.create_comprehensive_test_suite()
    
    print("Generated Test Suite:")
    print(f"- {len(test_suite['agents'])} agents")
    print(f"- {len(test_suite['tasks'])} tasks")
    print(f"- {len(test_suite['workflows'])} workflows")
    print(f"- {len(test_suite['teams'])} teams")
    print(f"- {len(test_suite['applications'])} applications")
    
    # 显示示例数据
    print("\nExample Agent:")
    print(test_suite['agents'][0])
    
    print("\nExample Workflow:")
    print(test_suite['workflows'][0]) 