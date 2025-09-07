"""
Integration tests for framework abstraction layer components
Tests how UniversalAgent, UniversalTask, UniversalContext, and UniversalResult work together
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from layers.framework.abstractions.agent import UniversalAgent, AgentCapability, AgentStatus
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus, ResultType


class MockChatAgent(UniversalAgent):
    """Mock agent for testing that implements conversation capability"""
    
    def __init__(self):
        super().__init__(
            name="Mock Chat Agent",
            description="A mock agent for testing conversation capabilities",
            capabilities=[AgentCapability.CONVERSATION, AgentCapability.REASONING]
        )
    
    async def execute(self, task: UniversalTask, context: UniversalContext = None) -> UniversalResult:
        """Mock execution that simulates a conversation task"""
        if not self.has_capability(AgentCapability.CONVERSATION):
            return UniversalResult(
                content="Agent does not support conversation",
                status=ResultStatus.FAILURE
            )
        
        # Simulate processing
        self.status = AgentStatus.BUSY
        
        # Use context if provided
        user_name = "User"
        if context and context.has("user_name"):
            user_name = context.get("user_name")
        
        # Generate response based on task content
        response = f"Hello {user_name}! You said: '{task.content}'. How can I help you?"
        
        # Create result with artifacts and steps
        result = UniversalResult(
            content=response,
            status=ResultStatus.SUCCESS,
            result_type=ResultType.TEXT
        )
        
        # Add some processing steps
        result.add_intermediate_step("parse_input", "Parsed user input", {"input_length": len(task.content)})
        result.add_intermediate_step("generate_response", "Generated response", {"response_length": len(response)})
        
        # Add artifact
        result.add_artifact("conversation_log", f"User: {task.content}\nAgent: {response}", "text")
        
        self.status = AgentStatus.IDLE
        return result
    
    def get_schema(self) -> Dict[str, Any]:
        """Return agent schema"""
        return {
            "agent_type": "conversational",
            "input_format": "text",
            "output_format": "text",
            "max_input_length": 1000
        }
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure agent"""
        return True


class TestFrameworkIntegration:
    """Test integration between framework components"""
    
    @pytest.mark.asyncio
    async def test_basic_agent_task_execution(self):
        """Test basic agent executing a task"""
        # Create agent
        agent = MockChatAgent()
        
        # Create task
        task = UniversalTask(
            content="Hello, how are you?",
            task_type=TaskType.CONVERSATION,
            priority=TaskPriority.NORMAL
        )
        
        # Execute task
        result = await agent.execute(task)
        
        # Verify result
        assert result.status == ResultStatus.SUCCESS
        assert "Hello User!" in result.content
        assert "Hello, how are you?" in result.content
        assert len(result.intermediate_steps) == 2
        assert len(result.artifacts) == 1
        
        # Verify agent status
        assert agent.get_status() == AgentStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_agent_with_context(self):
        """Test agent execution with context"""
        # Create agent
        agent = MockChatAgent()
        
        # Create context
        context = UniversalContext()
        context.set("user_name", "Alice")
        context.set("session_id", "session_123")
        context.set("preferences", {"language": "en", "tone": "friendly"})
        
        # Create task
        task = UniversalTask(
            content="What's the weather like?",
            task_type=TaskType.CONVERSATION
        )
        task.add_context("source", "mobile_app")
        
        # Execute with context
        result = await agent.execute(task, context)
        
        # Verify context was used
        assert "Hello Alice!" in result.content
        assert result.status == ResultStatus.SUCCESS
        
        # Verify context remains intact
        assert context.get("user_name") == "Alice"
        assert context.get("session_id") == "session_123"
    
    @pytest.mark.asyncio
    async def test_task_lifecycle_with_agent(self):
        """Test complete task lifecycle"""
        agent = MockChatAgent()
        
        # Create and configure task
        task = UniversalTask(
            content="Tell me a joke",
            task_type=TaskType.CONVERSATION,
            priority=TaskPriority.HIGH
        )
        
        # Verify initial state
        assert task.status.value == "pending"
        assert task.can_execute()
        assert task.is_valid()
        
        # Start task
        task.start()
        assert task.status.value == "running"
        assert task.metadata.started_at is not None
        
        # Execute
        result = await agent.execute(task)
        
        # Complete task
        task.complete(result)
        assert task.status.value == "completed"
        assert task.result == result
        assert task.metadata.completed_at is not None
        assert task.metadata.execution_time is not None
    
    def test_context_sharing_between_tasks(self):
        """Test context sharing and isolation"""
        # Create shared context
        shared_context = UniversalContext()
        shared_context.set("user_id", "user_123")
        shared_context.set("session_start", datetime.now())
        
        # Create first task with context
        task1 = UniversalTask("First message", task_type=TaskType.CONVERSATION)
        task1.add_context("message_id", "msg_001")
        
        # Create second task with different context
        task2 = UniversalTask("Second message", task_type=TaskType.CONVERSATION)
        task2.add_context("message_id", "msg_002")
        
        # Merge shared context - extract the actual context data
        context_data = shared_context.to_dict()["context"]
        # Convert to simple dict format that task expects
        simple_context = {key: entry["value"] for key, entry in context_data.items()}
        task1.merge_context(simple_context)
        task2.merge_context(simple_context)
        
        # Verify both tasks have shared data
        assert task1.get_context("user_id") == "user_123"
        assert task2.get_context("user_id") == "user_123"
        
        # Verify tasks maintain separate contexts
        assert task1.get_context("message_id") == "msg_001"
        assert task2.get_context("message_id") == "msg_002"
    
    def test_result_artifact_chaining(self):
        """Test chaining results through artifacts"""
        # Create first result
        result1 = UniversalResult(
            content="First step completed",
            result_type=ResultType.TEXT
        )
        result1.add_artifact("data", {"processed": True, "count": 5}, "json")
        result1.add_intermediate_step("process", "Processed initial data")
        
        # Create second result that uses first result's artifacts
        first_artifact = result1.get_artifact("data")
        result2 = UniversalResult(
            content=f"Second step: processed {first_artifact['content']['count']} items",
            result_type=ResultType.TEXT
        )
        result2.add_artifact("summary", {"total_processed": first_artifact['content']['count']}, "json")
        result2.add_intermediate_step("summarize", "Created summary from previous result")
        
        # Verify chaining
        assert result2.content == "Second step: processed 5 items"
        summary = result2.get_artifact("summary")
        assert summary['content']['total_processed'] == 5
    
    @pytest.mark.asyncio
    async def test_agent_capability_validation(self):
        """Test agent capability validation"""
        agent = MockChatAgent()
        
        # Test supported capability
        conversation_task = UniversalTask(
            content="Hello",
            task_type=TaskType.CONVERSATION
        )
        result = await agent.execute(conversation_task)
        assert result.status == ResultStatus.SUCCESS
        
        # Test with task requiring unsupported capability
        # Note: Our mock agent doesn't check task type vs capabilities in this simple implementation
        # but in a real implementation, you might want to validate this
        
        # Verify agent capabilities
        assert agent.has_capability(AgentCapability.CONVERSATION)
        assert agent.has_capability(AgentCapability.REASONING)
        assert not agent.has_capability(AgentCapability.CODE_EXECUTION)
    
    def test_error_propagation(self):
        """Test error handling and propagation"""
        # Create task with invalid content
        invalid_task = UniversalTask("")  # Empty content
        
        # Validate task
        assert not invalid_task.is_valid()
        errors = invalid_task.validate()
        assert "Task content cannot be empty" in errors
        
        # Create result with error
        error_result = UniversalResult(
            content="Task failed",
            status=ResultStatus.ERROR
        )
        
        # Test error status checking
        assert not error_result.is_successful()
        assert error_result.is_failed()
    
    def test_serialization_compatibility(self):
        """Test that all components can be serialized together"""
        # Create a complete workflow
        context = UniversalContext()
        context.set("workflow_id", "wf_123")
        context.set("step", 1)
        
        task = UniversalTask(
            content="Process data",
            task_type=TaskType.ANALYSIS,
            priority=TaskPriority.HIGH,
            context={"source": "api"}
        )
        
        result = UniversalResult(
            content={"processed": True, "items": 42},
            result_type=ResultType.JSON
        )
        result.add_artifact("report", "Processing complete", "text")
        
        # Serialize all components
        context_data = context.to_dict()
        task_data = task.to_dict()
        result_data = result.to_dict()
        
        # Deserialize
        restored_context = UniversalContext.from_dict(context_data)
        restored_task = UniversalTask.from_dict(task_data)
        restored_result = UniversalResult.from_dict(result_data)
        
        # Verify integrity
        assert restored_context.get("workflow_id") == "wf_123"
        assert restored_task.content == "Process data"
        assert restored_result.content == {"processed": True, "items": 42}
        assert len(restored_result.artifacts) == 1
    
    @pytest.mark.asyncio
    async def test_performance_metrics_integration(self):
        """Test performance metrics across components"""
        agent = MockChatAgent()
        
        # Execute multiple tasks to build metrics
        tasks = [
            UniversalTask(f"Message {i}", task_type=TaskType.CONVERSATION)
            for i in range(3)
        ]
        
        results = []
        for task in tasks:
            task.start()
            result = await agent.execute(task)
            task.complete(result)
            results.append(result)
        
        # Check agent metrics
        metrics = agent.get_performance_metrics()
        assert "total_tasks" in metrics
        assert "average_response_time" in metrics
        
        # Verify all tasks completed successfully
        assert all(result.is_successful() for result in results)
        assert all(task.status.value == "completed" for task in tasks)


if __name__ == "__main__":
    pytest.main([__file__]) 