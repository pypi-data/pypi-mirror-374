"""
Unit tests for UniversalTask abstraction
"""

import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import patch, Mock

from layers.framework.abstractions.task import (
    UniversalTask,
    TaskType,
    TaskPriority, 
    TaskStatus,
    TaskRequirements,
    TaskMetadata
)
from layers.framework.abstractions.result import UniversalResult, ResultStatus


class TestTaskType:
    """Test TaskType enum"""
    
    def test_task_type_values(self):
        """Test that all task types have correct values"""
        assert TaskType.CONVERSATION.value == "conversation"
        assert TaskType.CODE_GENERATION.value == "code_generation"
        assert TaskType.CODE_EXECUTION.value == "code_execution"
        assert TaskType.FILE_OPERATION.value == "file_operation"
        assert TaskType.WEB_SEARCH.value == "web_search"
        assert TaskType.ANALYSIS.value == "analysis"
        assert TaskType.PLANNING.value == "planning"
        assert TaskType.TOOL_EXECUTION.value == "tool_execution"
        assert TaskType.CUSTOM.value == "custom"
    
    def test_task_type_count(self):
        """Test that we have all expected task types"""
        types = list(TaskType)
        assert len(types) == 9


class TestTaskPriority:
    """Test TaskPriority enum"""
    
    def test_priority_values(self):
        """Test that all priorities have correct values"""
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.NORMAL.value == "normal"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.URGENT.value == "urgent"
    
    def test_priority_count(self):
        """Test that we have all expected priorities"""
        priorities = list(TaskPriority)
        assert len(priorities) == 4


class TestTaskStatus:
    """Test TaskStatus enum"""
    
    def test_status_values(self):
        """Test that all statuses have correct values"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
    
    def test_status_count(self):
        """Test that we have all expected statuses"""
        statuses = list(TaskStatus)
        assert len(statuses) == 5


class TestTaskRequirements:
    """Test TaskRequirements dataclass"""
    
    def test_default_initialization(self):
        """Test default requirements initialization"""
        req = TaskRequirements()
        
        assert req.capabilities == []
        assert req.max_execution_time is None
        assert req.memory_limit is None
        assert req.preferred_framework is None
        assert req.fallback_frameworks == []
    
    def test_full_initialization(self):
        """Test requirements initialization with all parameters"""
        req = TaskRequirements(
            capabilities=["conversation", "code_generation"],
            max_execution_time=300,
            memory_limit=1024,
            preferred_framework="openai",
            fallback_frameworks=["autogen", "langchain"]
        )
        
        assert req.capabilities == ["conversation", "code_generation"]
        assert req.max_execution_time == 300
        assert req.memory_limit == 1024
        assert req.preferred_framework == "openai"
        assert req.fallback_frameworks == ["autogen", "langchain"]


class TestTaskMetadata:
    """Test TaskMetadata dataclass"""
    
    def test_default_initialization(self):
        """Test default metadata initialization"""
        metadata = TaskMetadata()
        
        assert isinstance(metadata.created_at, datetime)
        assert metadata.started_at is None
        assert metadata.completed_at is None
        assert metadata.execution_time is None
        assert metadata.retries == 0
        assert metadata.max_retries == 3
    
    def test_custom_initialization(self):
        """Test metadata initialization with custom values"""
        created = datetime.now()
        metadata = TaskMetadata(
            created_at=created,
            retries=2,
            max_retries=5
        )
        
        assert metadata.created_at == created
        assert metadata.retries == 2
        assert metadata.max_retries == 5


class TestUniversalTask:
    """Test UniversalTask class"""
    
    def test_minimal_initialization(self):
        """Test task initialization with minimal parameters"""
        task = UniversalTask("Test task content")
        
        assert task.content == "Test task content"
        assert task.task_type == TaskType.CONVERSATION
        assert task.priority == TaskPriority.NORMAL
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.requirements, TaskRequirements)
        assert task.context == {}
        assert isinstance(task.metadata, TaskMetadata)
        assert task.result is None
        assert task.error is None
        assert len(task.id) > 0  # Should have generated ID
    
    def test_full_initialization(self):
        """Test task initialization with all parameters"""
        requirements = TaskRequirements(
            capabilities=["conversation"],
            max_execution_time=300,
            memory_limit=512
        )
        context = {"user_id": "123", "session": "abc"}
        
        task = UniversalTask(
            content="Complex task content",
            task_type=TaskType.CODE_GENERATION,
            priority=TaskPriority.HIGH,
            requirements=requirements,
            context=context,
            task_id="custom-task-id"
        )
        
        assert task.content == "Complex task content"
        assert task.task_type == TaskType.CODE_GENERATION
        assert task.priority == TaskPriority.HIGH
        assert task.requirements == requirements
        assert task.context == context
        assert task.id == "custom-task-id"
    
    def test_task_lifecycle_start(self):
        """Test task start operation"""
        task = UniversalTask("Test task")
        
        assert task.status == TaskStatus.PENDING
        assert task.metadata.started_at is None
        
        task.start()
        
        assert task.status == TaskStatus.RUNNING
        assert isinstance(task.metadata.started_at, datetime)
    
    def test_task_lifecycle_complete(self):
        """Test task completion"""
        task = UniversalTask("Test task")
        task.start()
        
        result = UniversalResult(content="Task completed successfully")
        task.complete(result)
        
        assert task.status == TaskStatus.COMPLETED
        assert task.result == result
        assert isinstance(task.metadata.completed_at, datetime)
        assert isinstance(task.metadata.execution_time, float)
        assert task.metadata.execution_time > 0
    
    def test_task_lifecycle_fail(self):
        """Test task failure"""
        task = UniversalTask("Test task")
        task.start()
        
        error_msg = "Task failed due to network error"
        task.fail(error_msg)
        
        assert task.status == TaskStatus.FAILED
        assert task.error == error_msg
        assert isinstance(task.metadata.completed_at, datetime)
        assert isinstance(task.metadata.execution_time, float)
    
    def test_task_lifecycle_cancel(self):
        """Test task cancellation"""
        task = UniversalTask("Test task")
        task.start()
        
        task.cancel()
        
        assert task.status == TaskStatus.CANCELLED
        assert isinstance(task.metadata.completed_at, datetime)
        assert isinstance(task.metadata.execution_time, float)
    
    def test_retry_mechanism(self):
        """Test task retry functionality"""
        task = UniversalTask("Test task")
        task.fail("First failure")
        
        assert task.status == TaskStatus.FAILED
        assert task.metadata.retries == 0
        
        # First retry should succeed
        success = task.retry()
        assert success is True
        assert task.status == TaskStatus.PENDING
        assert task.metadata.retries == 1
        assert task.error is None
        assert task.result is None
        
        # Fail and retry again
        task.fail("Second failure")
        success = task.retry()
        assert success is True
        assert task.metadata.retries == 2
        
        # Third retry
        task.fail("Third failure")
        success = task.retry()
        assert success is True
        assert task.metadata.retries == 3
        
        # Fourth retry should fail (exceeded max_retries)
        task.fail("Fourth failure")
        success = task.retry()
        assert success is False
        assert task.metadata.retries == 3
        assert task.status == TaskStatus.FAILED
    
    def test_context_management(self):
        """Test context management methods"""
        task = UniversalTask("Test task")
        
        # Initially empty
        assert task.context == {}
        assert not task.has_context("key1")
        assert task.get_context("key1") is None
        assert task.get_context("key1", "default") == "default"
        
        # Add context
        task.add_context("key1", "value1")
        assert task.has_context("key1")
        assert task.get_context("key1") == "value1"
        
        # Add more context
        task.add_context("key2", {"nested": "value"})
        assert task.get_context("key2") == {"nested": "value"}
        
        # Test context merging
        new_context = {"key3": "value3", "key1": "updated_value1"}
        task.merge_context(new_context)
        
        assert task.get_context("key1") == "updated_value1"  # Should be updated
        assert task.get_context("key2") == {"nested": "value"}  # Should remain
        assert task.get_context("key3") == "value3"  # Should be added
    
    def test_validation(self):
        """Test task validation"""
        # Valid task
        task = UniversalTask("Valid task content")
        assert task.is_valid()
        assert task.validate() == []
        
        # Empty content
        empty_task = UniversalTask("")
        assert not empty_task.is_valid()
        errors = empty_task.validate()
        assert "Task content cannot be empty" in errors
        
        # Whitespace only content
        whitespace_task = UniversalTask("   \n\t   ")
        assert not whitespace_task.is_valid()
        errors = whitespace_task.validate()
        assert "Task content cannot be empty" in errors
        
        # Invalid execution time
        requirements = TaskRequirements(max_execution_time=-10)
        invalid_time_task = UniversalTask("Content", requirements=requirements)
        assert not invalid_time_task.is_valid()
        errors = invalid_time_task.validate()
        assert "Max execution time must be positive" in errors
        
        # Invalid memory limit
        requirements = TaskRequirements(memory_limit=0)
        invalid_memory_task = UniversalTask("Content", requirements=requirements)
        assert not invalid_memory_task.is_valid()
        errors = invalid_memory_task.validate()
        assert "Memory limit must be positive" in errors
        
        # Multiple errors
        requirements = TaskRequirements(
            max_execution_time=-5,
            memory_limit=-100
        )
        multi_error_task = UniversalTask("", requirements=requirements)
        errors = multi_error_task.validate()
        assert len(errors) == 3  # Empty content + negative time + negative memory
    
    def test_can_execute(self):
        """Test execution eligibility"""
        task = UniversalTask("Test task")
        
        # Pending valid task should be executable
        assert task.can_execute()
        
        # Running task should be executable
        task.start()
        assert task.can_execute()
        
        # Completed task should not be executable
        result = UniversalResult(content="Done")
        task.complete(result)
        assert not task.can_execute()
        
        # Failed task should not be executable
        failed_task = UniversalTask("Test task")
        failed_task.fail("Error")
        assert not failed_task.can_execute()
        
        # Cancelled task should not be executable
        cancelled_task = UniversalTask("Test task")
        cancelled_task.cancel()
        assert not cancelled_task.can_execute()
        
        # Invalid task should not be executable
        invalid_task = UniversalTask("")
        assert not invalid_task.can_execute()
        
        # Task with too many retries should not be executable
        retry_task = UniversalTask("Test task")
        retry_task.metadata.retries = 5  # Exceeds max_retries (3)
        assert not retry_task.can_execute()


class TestTaskTiming:
    """Test task timing functionality"""
    
    def test_timeout_detection_no_start(self):
        """Test timeout detection when task hasn't started"""
        requirements = TaskRequirements(max_execution_time=60)
        task = UniversalTask("Test task", requirements=requirements)
        
        assert not task.is_timeout()
    
    def test_timeout_detection_no_limit(self):
        """Test timeout detection when no limit is set"""
        task = UniversalTask("Test task")
        task.start()
        
        assert not task.is_timeout()
    
    def test_timeout_detection_within_limit(self):
        """Test timeout detection within time limit"""
        requirements = TaskRequirements(max_execution_time=60)
        task = UniversalTask("Test task", requirements=requirements)
        task.start()
        
        assert not task.is_timeout()
    
    @patch('layers.framework.abstractions.task.datetime')
    def test_timeout_detection_exceeded(self, mock_datetime):
        """Test timeout detection when limit is exceeded"""
        # Setup mock datetime
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        current_time = datetime(2024, 1, 1, 12, 2, 0)  # 2 minutes later
        
        mock_datetime.now.return_value = start_time
        
        requirements = TaskRequirements(max_execution_time=60)  # 1 minute limit
        task = UniversalTask("Test task", requirements=requirements)
        task.start()
        
        # Now mock current time to be 2 minutes later
        mock_datetime.now.return_value = current_time
        
        assert task.is_timeout()
    
    def test_elapsed_time_not_started(self):
        """Test elapsed time when task hasn't started"""
        task = UniversalTask("Test task")
        
        assert task.get_elapsed_time() is None
    
    def test_elapsed_time_running(self):
        """Test elapsed time for running task"""
        task = UniversalTask("Test task")
        task.start()
        
        time.sleep(0.01)  # Small delay
        elapsed = task.get_elapsed_time()
        
        assert elapsed is not None
        assert elapsed > 0
        assert elapsed < 1  # Should be less than 1 second
    
    def test_elapsed_time_completed(self):
        """Test elapsed time for completed task"""
        task = UniversalTask("Test task")
        task.start()
        time.sleep(0.01)
        
        result = UniversalResult(content="Done")
        task.complete(result)
        
        elapsed = task.get_elapsed_time()
        assert elapsed is not None
        assert elapsed > 0
        assert elapsed == task.metadata.execution_time
    
    def test_remaining_time_no_limit(self):
        """Test remaining time when no limit is set"""
        task = UniversalTask("Test task")
        
        assert task.get_remaining_time() is None
    
    def test_remaining_time_not_started(self):
        """Test remaining time when task hasn't started"""
        requirements = TaskRequirements(max_execution_time=300)
        task = UniversalTask("Test task", requirements=requirements)
        
        assert task.get_remaining_time() == 300
    
    def test_remaining_time_running(self):
        """Test remaining time for running task"""
        requirements = TaskRequirements(max_execution_time=60)
        task = UniversalTask("Test task", requirements=requirements)
        task.start()
        
        time.sleep(0.01)
        remaining = task.get_remaining_time()
        
        assert remaining is not None
        assert remaining < 60
        assert remaining >= 0


class TestTaskCheckpoints:
    """Test task checkpoint functionality"""
    
    def test_add_first_checkpoint(self):
        """Test adding the first checkpoint"""
        task = UniversalTask("Test task")
        
        assert task.get_checkpoints() == []
        
        task.add_checkpoint("start", {"phase": "initialization"})
        
        checkpoints = task.get_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0]["name"] == "start"
        assert checkpoints[0]["data"] == {"phase": "initialization"}
        assert isinstance(checkpoints[0]["timestamp"], datetime)
    
    def test_add_multiple_checkpoints(self):
        """Test adding multiple checkpoints"""
        task = UniversalTask("Test task")
        
        task.add_checkpoint("start")
        task.add_checkpoint("middle", {"progress": 50})
        task.add_checkpoint("end", {"result": "success"})
        
        checkpoints = task.get_checkpoints()
        assert len(checkpoints) == 3
        
        assert checkpoints[0]["name"] == "start"
        assert checkpoints[0]["data"] == {}
        
        assert checkpoints[1]["name"] == "middle"
        assert checkpoints[1]["data"] == {"progress": 50}
        
        assert checkpoints[2]["name"] == "end"
        assert checkpoints[2]["data"] == {"result": "success"}
    
    def test_checkpoint_timestamps(self):
        """Test that checkpoints have proper timestamps"""
        task = UniversalTask("Test task")
        
        task.add_checkpoint("first")
        time.sleep(0.01)
        task.add_checkpoint("second")
        
        checkpoints = task.get_checkpoints()
        assert checkpoints[0]["timestamp"] < checkpoints[1]["timestamp"]


class TestTaskSerialization:
    """Test task serialization and deserialization"""
    
    def test_to_dict_minimal(self):
        """Test converting minimal task to dictionary"""
        task = UniversalTask("Test content")
        
        data = task.to_dict()
        
        assert data["content"] == "Test content"
        assert data["task_type"] == "conversation"
        assert data["priority"] == "normal"
        assert data["status"] == "pending"
        assert "id" in data
        assert data["context"] == {}
        assert data["error"] is None
        assert data["result"] is None
        
        # Check requirements
        req = data["requirements"]
        assert req["capabilities"] == []
        assert req["max_execution_time"] is None
        
        # Check metadata
        meta = data["metadata"]
        assert "created_at" in meta
        assert meta["started_at"] is None
        assert meta["retries"] == 0
    
    def test_to_dict_complete(self):
        """Test converting complete task to dictionary"""
        requirements = TaskRequirements(
            capabilities=["conversation"],
            max_execution_time=300
        )
        
        task = UniversalTask(
            content="Complex task",
            task_type=TaskType.CODE_GENERATION,
            priority=TaskPriority.HIGH,
            requirements=requirements,
            context={"user": "test"},
            task_id="test-123"
        )
        
        task.start()
        result = UniversalResult(content="Task completed")
        task.complete(result)
        
        data = task.to_dict()
        
        assert data["id"] == "test-123"
        assert data["task_type"] == "code_generation"
        assert data["priority"] == "high"
        assert data["status"] == "completed"
        assert data["context"] == {"user": "test"}
        assert data["requirements"]["capabilities"] == ["conversation"]
        assert data["metadata"]["started_at"] is not None
        assert data["metadata"]["completed_at"] is not None
        assert data["result"] is not None
    
    def test_from_dict_minimal(self):
        """Test creating task from minimal dictionary"""
        data = {
            "content": "Test content",
            "task_type": "conversation",
            "priority": "normal",
            "status": "pending"
        }
        
        task = UniversalTask.from_dict(data)
        
        assert task.content == "Test content"
        assert task.task_type == TaskType.CONVERSATION
        assert task.priority == TaskPriority.NORMAL
        assert task.status == TaskStatus.PENDING
    
    def test_from_dict_complete(self):
        """Test creating task from complete dictionary"""
        data = {
            "id": "test-456",
            "content": "Complex task",
            "task_type": "code_generation",
            "priority": "high",
            "status": "completed",
            "requirements": {
                "capabilities": ["code_generation"],
                "max_execution_time": 600,
                "memory_limit": 1024,
                "preferred_framework": "openai",
                "fallback_frameworks": ["autogen"]
            },
            "context": {"session": "abc123"},
            "metadata": {
                "created_at": "2024-01-01T12:00:00",
                "started_at": "2024-01-01T12:00:05",
                "completed_at": "2024-01-01T12:05:00",
                "execution_time": 295.0,
                "retries": 1,
                "max_retries": 5
            },
            "error": None,
            "result": None
        }
        
        task = UniversalTask.from_dict(data)
        
        assert task.id == "test-456"
        assert task.content == "Complex task"
        assert task.task_type == TaskType.CODE_GENERATION
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.COMPLETED
        assert task.context == {"session": "abc123"}
        
        # Check requirements
        assert task.requirements.capabilities == ["code_generation"]
        assert task.requirements.max_execution_time == 600
        assert task.requirements.memory_limit == 1024
        assert task.requirements.preferred_framework == "openai"
        assert task.requirements.fallback_frameworks == ["autogen"]
        
        # Check metadata
        assert task.metadata.retries == 1
        assert task.metadata.max_retries == 5
        assert task.metadata.execution_time == 295.0
    
    def test_round_trip_serialization(self):
        """Test that task can be serialized and deserialized without loss"""
        original = UniversalTask(
            content="Round trip test",
            task_type=TaskType.ANALYSIS,
            priority=TaskPriority.URGENT,
            context={"test": "data"},
            task_id="round-trip-123"
        )
        
        original.add_checkpoint("start", {"phase": 1})
        original.start()
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = UniversalTask.from_dict(data)
        
        # Compare
        assert restored.id == original.id
        assert restored.content == original.content
        assert restored.task_type == original.task_type
        assert restored.priority == original.priority
        assert restored.status == original.status
        assert restored.context == original.context


class TestTaskEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_long_content(self):
        """Test task with very long content"""
        long_content = "A" * 10000
        task = UniversalTask(long_content)
        
        assert task.content == long_content
        assert task.is_valid()
        
        # String representation should be truncated
        str_repr = str(task)
        assert len(str_repr) < len(long_content)
        assert "..." in str_repr
    
    def test_unicode_content(self):
        """Test task with unicode content"""
        unicode_content = "测试任务 🚀 émojis and ñoñ-ASCII"
        task = UniversalTask(unicode_content)
        
        assert task.content == unicode_content
        assert task.is_valid()
        
        # Should serialize/deserialize correctly
        data = task.to_dict()
        restored = UniversalTask.from_dict(data)
        assert restored.content == unicode_content
    
    def test_none_context_merge(self):
        """Test merging None context"""
        task = UniversalTask("Test task")
        task.add_context("existing", "value")
        
        task.merge_context(None)
        
        # Should not crash and existing context should remain
        assert task.get_context("existing") == "value"
    
    def test_concurrent_checkpoint_access(self):
        """Test concurrent access to checkpoints"""
        import threading
        
        task = UniversalTask("Concurrent test")
        
        def add_checkpoints(prefix):
            for i in range(10):
                task.add_checkpoint(f"{prefix}_{i}")
        
        # Create multiple threads adding checkpoints
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_checkpoints, args=(f"thread_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have all checkpoints
        checkpoints = task.get_checkpoints()
        assert len(checkpoints) == 30  # 3 threads * 10 checkpoints each


class TestTaskPerformance:
    """Test task performance characteristics"""
    
    def test_large_context_performance(self):
        """Test performance with large context"""
        task = UniversalTask("Performance test")
        
        # Add many context items
        for i in range(1000):
            task.add_context(f"key_{i}", f"value_{i}")
        
        assert len(task.context) == 1000
        assert task.get_context("key_500") == "value_500"
        
        # Should still be fast to serialize
        start_time = time.time()
        data = task.to_dict()
        serialize_time = time.time() - start_time
        
        assert serialize_time < 1.0  # Should complete within 1 second
        assert len(data["context"]) == 1000
    
    def test_many_checkpoints_performance(self):
        """Test performance with many checkpoints"""
        task = UniversalTask("Checkpoint performance test")
        
        # Add many checkpoints
        start_time = time.time()
        for i in range(1000):
            task.add_checkpoint(f"checkpoint_{i}", {"index": i})
        add_time = time.time() - start_time
        
        assert add_time < 1.0  # Should complete within 1 second
        assert len(task.get_checkpoints()) == 1000


if __name__ == "__main__":
    pytest.main([__file__]) 