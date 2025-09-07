"""
集成测试配置文件
提供测试环境设置和共享fixture
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus
from layers.business.workflows.workflow_engine import WorkflowEngine
from layers.business.teams.collaboration_manager import CollaborationManager
from layers.application.orchestration.orchestrator import ApplicationOrchestrator


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_agent():
    """创建模拟Agent"""
    agent = Mock(spec=UniversalAgent)
    agent.name = "Test Agent"
    agent.description = "A test agent for integration testing"
    agent.capabilities = [AgentCapability.CONVERSATION, AgentCapability.CODE_GENERATION]
    agent.agent_id = "test_agent_001"
    
    # 模拟execute方法
    agent.execute = AsyncMock(return_value=UniversalResult(
        data="Task completed successfully",
        status=ResultStatus.SUCCESS
    ))
    
    # 模拟抽象方法
    agent.get_schema = Mock(return_value={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "capabilities": {"type": "array", "items": {"type": "string"}}
        }
    })
    
    agent.configure = Mock()
    
    return agent


@pytest.fixture
def mock_context():
    """创建模拟上下文"""
    return UniversalContext(
        data={
            "user_id": "test_user_001",
            "session_id": "test_session_001",
            "project_name": "Integration Test Project",
            "test_data": {"key": "value"}
        },
        session_id="test_session_001",
        user_id="test_user_001"
    )


@pytest.fixture
def mock_task():
    """创建模拟任务"""
    return UniversalTask(
        task_id="test_task_001",
        title="Integration Test Task",
        description="A task for testing integration",
        content="Execute integration test",
        task_type=TaskType.ANALYSIS,
        priority=1
    )


@pytest.fixture
def workflow_engine():
    """创建工作流引擎实例"""
    return WorkflowEngine()


@pytest.fixture
def collaboration_manager():
    """创建协作管理器实例"""
    return CollaborationManager()


@pytest.fixture
def application_orchestrator():
    """创建应用编排器实例"""
    return ApplicationOrchestrator()


@pytest.fixture
def integration_test_data():
    """提供集成测试数据"""
    return {
        "workflow_definitions": [
            {
                "workflow_id": "integration_workflow_001",
                "name": "Integration Test Workflow",
                "description": "Workflow for testing layer integration",
                "steps": [
                    {
                        "step_id": "step_1",
                        "name": "Data Preparation",
                        "step_type": "data_preparation",
                        "config": {"data_source": "test_db", "format": "json"}
                    },
                    {
                        "step_id": "step_2",
                        "name": "Agent Task",
                        "step_type": "agent_task",
                        "config": {"agent_id": "test_agent_001", "task_type": "analysis"}
                    },
                    {
                        "step_id": "step_3",
                        "name": "Result Processing",
                        "step_type": "result_processing",
                        "config": {"output_format": "csv", "save_path": "/tmp/results"}
                    }
                ]
            }
        ],
        "team_configurations": [
            {
                "team_id": "integration_team_001",
                "name": "Integration Test Team",
                "members": [
                    {
                        "member_id": "member_001",
                        "name": "Test Developer",
                        "email": "dev@test.com",
                        "role": "developer"
                    },
                    {
                        "member_id": "member_002",
                        "name": "Test Tester",
                        "email": "tester@test.com",
                        "role": "tester"
                    }
                ]
            }
        ],
        "application_configs": [
            {
                "app_id": "integration_app_001",
                "name": "Integration Test App",
                "version": "1.0.0",
                "app_type": "web_service",
                "description": "Application for testing integration",
                "dependencies": [],
                "config": {"port": 8080, "host": "localhost"}
            }
        ]
    }


@pytest.fixture
def mock_api_responses():
    """模拟API响应"""
    return {
        "success": {
            "status": "success",
            "data": {"result": "Operation completed successfully"},
            "message": "Request processed successfully"
        },
        "error": {
            "status": "error",
            "error": "API request failed",
            "message": "An error occurred during processing"
        },
        "timeout": {
            "status": "timeout",
            "error": "Request timeout",
            "message": "Request timed out"
        }
    }


@pytest.fixture
def test_environment():
    """测试环境配置"""
    return {
        "database_url": "sqlite:///test.db",
        "cache_url": "redis://localhost:6379/1",
        "log_level": "DEBUG",
        "timeout": 30,
        "max_retries": 3,
        "test_mode": True
    }


@pytest.fixture
def cleanup_test_data():
    """清理测试数据的fixture"""
    # 在测试前清理
    yield
    
    # 在测试后清理
    # 这里可以添加清理逻辑，比如删除测试文件、清理数据库等


class IntegrationTestBase:
    """集成测试基类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.setup_test_environment()
        self.setup_test_data()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.cleanup_test_data()
    
    def setup_test_environment(self):
        """设置测试环境"""
        # 设置测试环境变量
        import os
        os.environ["TEST_MODE"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    def setup_test_data(self):
        """设置测试数据"""
        # 初始化测试数据
        pass
    
    def cleanup_test_data(self):
        """清理测试数据"""
        # 清理测试过程中创建的数据
        pass
    
    async def wait_for_condition(self, condition_func, timeout=10, interval=0.1):
        """等待条件满足"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    def assert_workflow_completed(self, workflow_engine, execution_id):
        """断言工作流完成"""
        execution = workflow_engine.executions.get(execution_id)
        assert execution is not None
        assert execution.status == "completed"
    
    def assert_agent_registered(self, workflow_engine, agent_id):
        """断言Agent已注册"""
        assert agent_id in workflow_engine.agents
    
    def assert_team_created(self, collaboration_manager, team_id):
        """断言团队已创建"""
        assert team_id in collaboration_manager.teams
    
    def assert_application_registered(self, orchestrator, app_id):
        """断言应用已注册"""
        assert app_id in orchestrator.applications 