"""
Unit tests for UniversalAgent abstraction
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

from layers.framework.abstractions.agent import (
    UniversalAgent, 
    AgentCapability, 
    AgentStatus, 
    AgentMetadata
)
from layers.framework.abstractions.task import UniversalTask
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class MockAgent(UniversalAgent):
    """Mock implementation of UniversalAgent for testing"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.execute_calls = []
        self.configure_calls = []
    
    async def execute(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """Mock execute method"""
        self.execute_calls.append((task, context))
        # Simulate task execution
        self.status = AgentStatus.BUSY
        await asyncio.sleep(0.01)  # Simulate work
        self.status = AgentStatus.IDLE
        
        # Update metadata
        self.metadata.total_tasks += 1
        self.metadata.successful_tasks += 1
        self.metadata.last_active = datetime.now()
        
        return UniversalResult(
            content={"result": "mock execution completed", "task_id": task.id},
            status=ResultStatus.SUCCESS
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Mock schema method"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "temperature": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["name"]
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Mock configure method"""
        self.configure_calls.append(config)
        self.config.update(config)


class TestAgentCapability:
    """Test AgentCapability enum"""
    
    def test_capability_values(self):
        """Test that all capabilities have correct values"""
        assert AgentCapability.CONVERSATION.value == "conversation"
        assert AgentCapability.CODE_GENERATION.value == "code_generation"
        assert AgentCapability.CODE_EXECUTION.value == "code_execution"
        assert AgentCapability.FILE_OPERATIONS.value == "file_operations"
        assert AgentCapability.WEB_SEARCH.value == "web_search"
        assert AgentCapability.TOOL_CALLING.value == "tool_calling"
        assert AgentCapability.MULTIMODAL.value == "multimodal"
        assert AgentCapability.PLANNING.value == "planning"
        assert AgentCapability.REASONING.value == "reasoning"
    
    def test_capability_count(self):
        """Test that we have all expected capabilities"""
        capabilities = list(AgentCapability)
        assert len(capabilities) == 9


class TestAgentStatus:
    """Test AgentStatus enum"""
    
    def test_status_values(self):
        """Test that all statuses have correct values"""
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.BUSY.value == "busy"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.OFFLINE.value == "offline"
    
    def test_status_count(self):
        """Test that we have all expected statuses"""
        statuses = list(AgentStatus)
        assert len(statuses) == 4


class TestAgentMetadata:
    """Test AgentMetadata dataclass"""
    
    def test_default_initialization(self):
        """Test default metadata initialization"""
        metadata = AgentMetadata()
        
        assert isinstance(metadata.created_at, datetime)
        assert metadata.last_active is None
        assert metadata.total_tasks == 0
        assert metadata.successful_tasks == 0
        assert metadata.failed_tasks == 0
        assert metadata.average_response_time == 0.0
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        metadata = AgentMetadata()
        
        # No tasks
        assert metadata.success_rate == 0.0
        
        # Some tasks
        metadata.total_tasks = 10
        metadata.successful_tasks = 8
        assert metadata.success_rate == 0.8
        
        # All successful
        metadata.successful_tasks = 10
        assert metadata.success_rate == 1.0
        
        # All failed
        metadata.successful_tasks = 0
        assert metadata.success_rate == 0.0
    
    def test_success_rate_edge_cases(self):
        """Test success rate edge cases"""
        metadata = AgentMetadata()
        
        # Division by zero protection
        metadata.total_tasks = 0
        metadata.successful_tasks = 0
        assert metadata.success_rate == 0.0
        
        # Negative values (shouldn't happen but test robustness)
        metadata.total_tasks = -1
        assert metadata.success_rate == 0.0


class TestUniversalAgent:
    """Test UniversalAgent abstract class"""
    
    def test_initialization_minimal(self):
        """Test agent initialization with minimal parameters"""
        agent = MockAgent("test-agent")
        
        assert agent.name == "test-agent"
        assert agent.description == ""
        assert agent.capabilities == []
        assert agent.config == {}
        assert agent.status == AgentStatus.IDLE
        assert isinstance(agent.metadata, AgentMetadata)
    
    def test_initialization_full(self):
        """Test agent initialization with all parameters"""
        capabilities = [AgentCapability.CONVERSATION, AgentCapability.CODE_GENERATION]
        config = {"temperature": 0.7, "max_tokens": 1000}
        description = "Test agent description"
        
        agent = MockAgent(
            name="full-agent",
            description=description,
            capabilities=capabilities,
            config=config
        )
        
        assert agent.name == "full-agent"
        assert agent.description == description
        assert agent.capabilities == capabilities
        assert agent.config == config
        assert agent.status == AgentStatus.IDLE
    
    def test_get_capabilities(self):
        """Test capability management"""
        capabilities = [AgentCapability.CONVERSATION, AgentCapability.REASONING]
        agent = MockAgent("test", capabilities=capabilities)
        
        # Should return a copy
        returned_caps = agent.get_capabilities()
        assert returned_caps == capabilities
        assert returned_caps is not agent.capabilities  # Should be a copy
        
        # Modifying returned list shouldn't affect original
        returned_caps.append(AgentCapability.PLANNING)
        assert len(agent.capabilities) == 2
    
    def test_has_capability(self):
        """Test capability checking"""
        capabilities = [AgentCapability.CONVERSATION, AgentCapability.REASONING]
        agent = MockAgent("test", capabilities=capabilities)
        
        assert agent.has_capability(AgentCapability.CONVERSATION)
        assert agent.has_capability(AgentCapability.REASONING)
        assert not agent.has_capability(AgentCapability.CODE_GENERATION)
        assert not agent.has_capability(AgentCapability.MULTIMODAL)
    
    def test_status_management(self):
        """Test status getting and setting"""
        agent = MockAgent("test")
        
        assert agent.get_status() == AgentStatus.IDLE
        
        agent.status = AgentStatus.BUSY
        assert agent.get_status() == AgentStatus.BUSY
        
        agent.status = AgentStatus.ERROR
        assert agent.get_status() == AgentStatus.ERROR
    
    def test_metadata_access(self):
        """Test metadata access"""
        agent = MockAgent("test")
        metadata = agent.get_metadata()
        
        assert isinstance(metadata, AgentMetadata)
        assert metadata is agent.metadata  # Should return the actual object
    
    def test_performance_metrics(self):
        """Test performance metrics generation"""
        capabilities = [AgentCapability.CONVERSATION, AgentCapability.REASONING]
        agent = MockAgent("perf-test", capabilities=capabilities)
        
        # Set some metadata
        agent.metadata.total_tasks = 5
        agent.metadata.successful_tasks = 4
        agent.metadata.failed_tasks = 1
        agent.metadata.average_response_time = 1.5
        agent.metadata.last_active = datetime(2024, 1, 1, 12, 0, 0)
        
        metrics = agent.get_performance_metrics()
        
        assert metrics["name"] == "perf-test"
        assert metrics["status"] == "idle"
        assert metrics["total_tasks"] == 5
        assert metrics["successful_tasks"] == 4
        assert metrics["failed_tasks"] == 1
        assert metrics["success_rate"] == 0.8
        assert metrics["average_response_time"] == 1.5
        assert metrics["capabilities"] == ["conversation", "reasoning"]
        assert metrics["last_active"] == "2024-01-01T12:00:00"
    
    def test_performance_metrics_no_last_active(self):
        """Test performance metrics when last_active is None"""
        agent = MockAgent("test")
        metrics = agent.get_performance_metrics()
        
        assert metrics["last_active"] is None
    
    @pytest.mark.asyncio
    async def test_execute_method(self):
        """Test the execute method"""
        agent = MockAgent("exec-test")
        
        # Create mock task and context
        task = Mock(spec=UniversalTask)
        task.id = "test-task-123"
        context = Mock(spec=UniversalContext)
        
        # Execute
        result = await agent.execute(task, context)
        
        # Verify execution was tracked
        assert len(agent.execute_calls) == 1
        assert agent.execute_calls[0] == (task, context)
        
        # Verify result
        assert isinstance(result, UniversalResult)
        assert result.content["task_id"] == "test-task-123"
        assert result.status == ResultStatus.SUCCESS
        
        # Verify metadata was updated
        assert agent.metadata.total_tasks == 1
        assert agent.metadata.successful_tasks == 1
        assert agent.metadata.last_active is not None
    
    def test_get_schema_method(self):
        """Test the get_schema method"""
        agent = MockAgent("schema-test")
        schema = agent.get_schema()
        
        assert isinstance(schema, dict)
        assert "type" in schema
        assert "properties" in schema
        assert schema["type"] == "object"
    
    def test_configure_method(self):
        """Test the configure method"""
        agent = MockAgent("config-test")
        config = {"temperature": 0.8, "model": "gpt-4"}
        
        agent.configure(config)
        
        # Verify configure was called
        assert len(agent.configure_calls) == 1
        assert agent.configure_calls[0] == config
        
        # Verify config was updated
        assert agent.config["temperature"] == 0.8
        assert agent.config["model"] == "gpt-4"
    
    def test_string_representation(self):
        """Test string representations"""
        capabilities = [AgentCapability.CONVERSATION]
        agent = MockAgent("str-test", capabilities=capabilities)
        
        str_repr = str(agent)
        assert "UniversalAgent" in str_repr
        assert "str-test" in str_repr
        assert "idle" in str_repr
        assert "1" in str_repr  # capability count
        
        # __repr__ should be the same as __str__
        assert repr(agent) == str(agent)
    
    def test_capability_list_immutability(self):
        """Test that capabilities list can't be modified externally"""
        original_caps = [AgentCapability.CONVERSATION, AgentCapability.REASONING]
        agent = MockAgent("immutable-test", capabilities=original_caps)
        
        # Get capabilities and try to modify
        caps = agent.get_capabilities()
        caps.clear()
        
        # Original should be unchanged
        assert len(agent.capabilities) == 2
        assert agent.capabilities == original_caps


class TestAgentConcurrency:
    """Test agent behavior under concurrent conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """Test concurrent task execution"""
        agent = MockAgent("concurrent-test")
        
        # Create multiple tasks
        tasks = []
        contexts = []
        for i in range(5):
            task = Mock(spec=UniversalTask)
            task.id = f"task-{i}"
            context = Mock(spec=UniversalContext)
            tasks.append(task)
            contexts.append(context)
        
        # Execute concurrently
        results = await asyncio.gather(*[
            agent.execute(task, context) 
            for task, context in zip(tasks, contexts)
        ])
        
        # Verify all executions completed
        assert len(results) == 5
        assert all(isinstance(r, UniversalResult) for r in results)
        assert agent.metadata.total_tasks == 5
        assert agent.metadata.successful_tasks == 5
    
    @pytest.mark.asyncio
    async def test_status_transitions_during_execution(self):
        """Test status transitions during task execution"""
        agent = MockAgent("status-test")
        
        # Create a task
        task = Mock(spec=UniversalTask)
        task.id = "status-task"
        context = Mock(spec=UniversalContext)
        
        # Start execution
        initial_status = agent.get_status()
        assert initial_status == AgentStatus.IDLE
        
        # Execute (this will change status to BUSY then back to IDLE)
        result = await agent.execute(task, context)
        
        # Should be back to IDLE
        final_status = agent.get_status()
        assert final_status == AgentStatus.IDLE
        assert result.status == ResultStatus.SUCCESS


class TestAgentErrorHandling:
    """Test error handling in agent operations"""
    
    def test_initialization_with_invalid_types(self):
        """Test initialization with invalid parameter types"""
        # Should handle None capabilities gracefully
        agent = MockAgent("test", capabilities=None)
        assert agent.capabilities == []
        
        # Should handle None config gracefully
        agent = MockAgent("test", config=None)
        assert agent.config == {}
    
    def test_capability_checking_with_invalid_input(self):
        """Test capability checking with edge cases"""
        agent = MockAgent("test")
        
        # Empty capabilities list
        assert not agent.has_capability(AgentCapability.CONVERSATION)
        
        # Check with actual capability enum
        agent.capabilities = [AgentCapability.CONVERSATION]
        assert agent.has_capability(AgentCapability.CONVERSATION)
    
    def test_metadata_edge_cases(self):
        """Test metadata behavior in edge cases"""
        agent = MockAgent("test")
        
        # Metadata should be properly initialized
        assert agent.metadata.success_rate == 0.0
        
        # Setting negative values (edge case)
        agent.metadata.total_tasks = -1
        assert agent.metadata.success_rate == 0.0


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent with other components"""
    
    @pytest.mark.asyncio
    async def test_agent_with_real_task_and_context(self):
        """Test agent with actual UniversalTask and UniversalContext objects"""
        # This would require importing and using real task/context objects
        # For now, we'll use mocks but in a more realistic way
        agent = MockAgent("integration-test")
        
        # Create more realistic mock objects
        task = Mock(spec=UniversalTask)
        task.id = "real-task-123"
        task.type = "conversation"
        task.data = {"message": "Hello, world!"}
        
        context = Mock(spec=UniversalContext)
        context.get.return_value = "test-value"
        
        result = await agent.execute(task, context)
        
        assert result.content["task_id"] == "real-task-123"
        assert result.status == ResultStatus.SUCCESS
        assert "result" in result.content


if __name__ == "__main__":
    pytest.main([__file__]) 