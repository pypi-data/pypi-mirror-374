"""
工作流集成测试
测试工作流引擎与其他组件的集成
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from layers.business.workflows.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowStep, 
    WorkflowStepType
)
from layers.framework.abstractions.agent import UniversalAgent, AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class TestWorkflowIntegration(IntegrationTestBase):
    """测试工作流集成"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        super().setup_method()
        self.workflow_engine = WorkflowEngine()
        self.setup_test_agents()
        self.setup_test_workflows()
    
    def setup_test_agents(self):
        """设置测试Agent"""
        # 创建模拟Agent
        self.test_agent = Mock(spec=UniversalAgent)
        self.test_agent.name = "Integration Test Agent"
        self.test_agent.description = "Agent for integration testing"
        self.test_agent.capabilities = [AgentCapability.CONVERSATION, AgentCapability.CODE_GENERATION]
        self.test_agent.agent_id = "integration_agent_001"
        
        # 模拟execute方法
        self.test_agent.execute = AsyncMock(return_value=UniversalResult(
            data="Integration test completed",
            status=ResultStatus.SUCCESS
        ))
        
        # 模拟抽象方法
        self.test_agent.get_schema = Mock(return_value={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "capabilities": {"type": "array", "items": {"type": "string"}}
            }
        })
        
        self.test_agent.configure = Mock()
        
        # 注册Agent
        self.workflow_engine.register_agent("integration_agent_001", self.test_agent)
    
    def setup_test_workflows(self):
        """设置测试工作流"""
        # 创建集成测试工作流
        self.integration_workflow = WorkflowDefinition(
            workflow_id="integration_workflow_001",
            name="Integration Test Workflow",
            description="Workflow for testing component integration",
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Data Preparation",
                    step_type=WorkflowStepType.DATA_PREPARATION,
                    config={
                        "data_source": "test_db",
                        "format": "json",
                        "filters": {"status": "active"}
                    }
                ),
                WorkflowStep(
                    step_id="step_2",
                    name="Agent Task Execution",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "integration_agent_001",
                        "task_content": "Analyze the prepared data",
                        "task_type": "ANALYSIS"
                    }
                ),
                WorkflowStep(
                    step_id="step_3",
                    name="Result Processing",
                    step_type=WorkflowStepType.RESULT_PROCESSING,
                    config={
                        "output_format": "csv",
                        "save_path": "/tmp/integration_results",
                        "include_metadata": True
                    }
                )
            ]
        )
        
        # 注册工作流
        asyncio.run(self.workflow_engine.register_workflow(self.integration_workflow))
    
    async def test_workflow_with_agent_integration(self):
        """测试工作流与Agent的集成"""
        # 创建测试上下文
        context = UniversalContext(
            data={
                "user_id": "integration_test_user",
                "session_id": "integration_test_session",
                "test_data": {"input": "test_value", "expected_output": "expected_result"}
            },
            session_id="integration_test_session",
            user_id="integration_test_user"
        )
        
        # 执行工作流
        execution_id = await self.workflow_engine.execute_workflow(
            "integration_workflow_001",
            context
        )
        
        assert execution_id is not None
        
        # 等待工作流完成
        await self.wait_for_workflow_completion(execution_id)
        
        # 验证执行结果
        execution = self.workflow_engine.executions[execution_id]
        assert execution.status == "completed"
        assert execution.workflow_id == "integration_workflow_001"
        
        # 验证所有步骤都完成
        for step_id in ["step_1", "step_2", "step_3"]:
            step_exec = execution.step_executions[step_id]
            assert step_exec.status == "completed"
            assert step_exec.result is not None
        
        # 验证Agent被正确调用
        self.test_agent.execute.assert_called_once()
        
        # 验证传递给Agent的上下文
        call_args = self.test_agent.execute.call_args
        passed_context = call_args[0][1]  # 第二个参数是上下文
        assert isinstance(passed_context, UniversalContext)
        assert passed_context.get("user_id") == "integration_test_user"
        assert passed_context.get("test_data") == {"input": "test_value", "expected_output": "expected_result"}
    
    async def test_workflow_context_propagation(self):
        """测试工作流上下文传播"""
        # 创建包含复杂数据的上下文
        complex_context = UniversalContext(
            data={
                "nested_data": {
                    "level1": {
                        "level2": {
                            "level3": "deep_value"
                        }
                    }
                },
                "list_data": [1, 2, 3, {"nested": "item"}],
                "string_data": "test_string",
                "numeric_data": 42,
                "boolean_data": True
            },
            session_id="context_test_session",
            user_id="context_test_user"
        )
        
        # 执行工作流
        execution_id = await self.workflow_engine.execute_workflow(
            "integration_workflow_001",
            complex_context
        )
        
        assert execution_id is not None
        
        # 等待工作流完成
        await self.wait_for_workflow_completion(execution_id)
        
        # 验证上下文被正确传播
        execution = self.workflow_engine.executions[execution_id]
        assert execution.status == "completed"
        
        # 验证Agent接收到的上下文
        self.test_agent.execute.assert_called_once()
        call_args = self.test_agent.execute.call_args
        passed_context = call_args[0][1]
        
        # 验证复杂数据被正确传递
        assert passed_context.get("nested_data")["level1"]["level2"]["level3"] == "deep_value"
        assert passed_context.get("list_data") == [1, 2, 3, {"nested": "item"}]
        assert passed_context.get("string_data") == "test_string"
        assert passed_context.get("numeric_data") == 42
        assert passed_context.get("boolean_data") is True
    
    async def test_workflow_error_handling(self):
        """测试工作流错误处理"""
        # 创建会失败的Agent
        failing_agent = Mock(spec=UniversalAgent)
        failing_agent.name = "Failing Agent"
        failing_agent.description = "Agent that always fails"
        failing_agent.capabilities = [AgentCapability.CONVERSATION]
        failing_agent.agent_id = "failing_agent_001"
        
        # 模拟失败的execute方法
        failing_agent.execute = AsyncMock(side_effect=Exception("Simulated agent failure"))
        failing_agent.get_schema = Mock(return_value={})
        failing_agent.configure = Mock()
        
        # 注册失败的Agent
        self.workflow_engine.register_agent("failing_agent_001", failing_agent)
        
        # 创建包含失败步骤的工作流
        failing_workflow = WorkflowDefinition(
            workflow_id="failing_workflow_001",
            name="Failing Integration Workflow",
            description="Workflow that will fail during execution",
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Successful Step",
                    step_type=WorkflowStepType.DATA_PREPARATION,
                    config={"data_source": "test_db"}
                ),
                WorkflowStep(
                    step_id="step_2",
                    name="Failing Step",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "failing_agent_001",
                        "task_content": "This will fail",
                        "task_type": "ANALYSIS"
                    }
                )
            ]
        )
        
        # 注册失败工作流
        await self.workflow_engine.register_workflow(failing_workflow)
        
        # 执行工作流
        context = UniversalContext(data={"test": "data"})
        execution_id = await self.workflow_engine.execute_workflow(
            "failing_workflow_001",
            context
        )
        
        assert execution_id is not None
        
        # 等待工作流完成（或失败）
        await self.wait_for_workflow_completion(execution_id, timeout=5)
        
        # 验证工作流失败
        execution = self.workflow_engine.executions[execution_id]
        assert execution.status == "failed"
        
        # 验证第一步成功
        step1_exec = execution.step_executions["step_1"]
        assert step1_exec.status == "completed"
        
        # 验证第二步失败
        step2_exec = execution.step_executions["step_2"]
        assert step2_exec.status == "failed"
        assert step2_exec.error is not None
        assert "Simulated agent failure" in step2_exec.error
    
    async def test_workflow_with_multiple_agents(self):
        """测试包含多个Agent的工作流"""
        # 创建第二个Agent
        second_agent = Mock(spec=UniversalAgent)
        second_agent.name = "Second Integration Agent"
        second_agent.description = "Second agent for integration testing"
        second_agent.capabilities = [AgentCapability.CODE_GENERATION]
        second_agent.agent_id = "integration_agent_002"
        
        # 模拟execute方法
        second_agent.execute = AsyncMock(return_value=UniversalResult(
            data="Second agent task completed",
            status=ResultStatus.SUCCESS
        ))
        
        second_agent.get_schema = Mock(return_value={})
        second_agent.configure = Mock()
        
        # 注册第二个Agent
        self.workflow_engine.register_agent("integration_agent_002", second_agent)
        
        # 创建多Agent工作流
        multi_agent_workflow = WorkflowDefinition(
            workflow_id="multi_agent_workflow_001",
            name="Multi-Agent Integration Workflow",
            description="Workflow with multiple agents",
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="First Agent Task",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "integration_agent_001",
                        "task_content": "First agent task",
                        "task_type": "ANALYSIS"
                    }
                ),
                WorkflowStep(
                    step_id="step_2",
                    name="Second Agent Task",
                    step_type=WorkflowStepType.AGENT_TASK,
                    config={
                        "agent_id": "integration_agent_002",
                        "task_content": "Second agent task",
                        "task_type": "CODE_GENERATION"
                    }
                )
            ]
        )
        
        # 注册多Agent工作流
        await self.workflow_engine.register_workflow(multi_agent_workflow)
        
        # 执行工作流
        context = UniversalContext(data={"multi_agent_test": True})
        execution_id = await self.workflow_engine.execute_workflow(
            "multi_agent_workflow_001",
            context
        )
        
        assert execution_id is not None
        
        # 等待工作流完成
        await self.wait_for_workflow_completion(execution_id)
        
        # 验证执行结果
        execution = self.workflow_engine.executions[execution_id]
        assert execution.status == "completed"
        
        # 验证两个Agent都被调用
        self.test_agent.execute.assert_called_once()
        second_agent.execute.assert_called_once()
        
        # 验证步骤执行顺序
        step1_exec = execution.step_executions["step_1"]
        step2_exec = execution.step_executions["step_2"]
        
        assert step1_exec.status == "completed"
        assert step2_exec.status == "completed"
        
        # 验证第二步在第一步之后执行
        assert step1_exec.start_time <= step2_exec.start_time
    
    async def wait_for_workflow_completion(self, execution_id, timeout=10):
        """等待工作流完成"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            execution = self.workflow_engine.executions.get(execution_id)
            if execution and execution.status in ["completed", "failed"]:
                return
            
            await asyncio.sleep(0.1)
        
        # 超时
        pytest.fail(f"Workflow execution {execution_id} did not complete within {timeout} seconds")


if __name__ == "__main__":
    pytest.main([__file__]) 