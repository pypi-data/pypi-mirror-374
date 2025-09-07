"""
Unit tests for UniversalResult abstraction
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from layers.framework.abstractions.result import (
    UniversalResult,
    ResultStatus,
    ResultType,
    ResultMetadata,
    ErrorInfo
)


class TestResultStatus:
    """Test ResultStatus enum"""
    
    def test_status_values(self):
        """Test that all statuses have correct values"""
        assert ResultStatus.SUCCESS.value == "success"
        assert ResultStatus.PARTIAL_SUCCESS.value == "partial_success"
        assert ResultStatus.FAILURE.value == "failure"
        assert ResultStatus.ERROR.value == "error"
        assert ResultStatus.TIMEOUT.value == "timeout"
        assert ResultStatus.CANCELLED.value == "cancelled"
    
    def test_status_count(self):
        """Test that we have all expected statuses"""
        statuses = list(ResultStatus)
        assert len(statuses) == 6


class TestResultType:
    """Test ResultType enum"""
    
    def test_type_values(self):
        """Test that all types have correct values"""
        assert ResultType.TEXT.value == "text"
        assert ResultType.CODE.value == "code"
        assert ResultType.FILE.value == "file"
        assert ResultType.JSON.value == "json"
        assert ResultType.BINARY.value == "binary"
        assert ResultType.MULTIMODAL.value == "multimodal"
        assert ResultType.STRUCTURED.value == "structured"
        assert ResultType.ANALYSIS.value == "analysis"
    
    def test_type_count(self):
        """Test that we have all expected types"""
        types = list(ResultType)
        assert len(types) == 8


class TestResultMetadata:
    """Test ResultMetadata dataclass"""
    
    def test_default_initialization(self):
        """Test default metadata initialization"""
        metadata = ResultMetadata()
        
        assert metadata.execution_time is None
        assert metadata.memory_usage is None
        assert metadata.token_usage is None
        assert metadata.model_info is None
        assert metadata.framework_info is None
        assert isinstance(metadata.created_at, datetime)
    
    def test_full_initialization(self):
        """Test metadata initialization with all parameters"""
        created = datetime(2024, 1, 1, 12, 0, 0)
        token_usage = {"input": 100, "output": 50}
        model_info = {"name": "gpt-4", "version": "0613"}
        
        metadata = ResultMetadata(
            execution_time=2.5,
            memory_usage=1024,
            token_usage=token_usage,
            model_info=model_info,
            framework_info={"framework": "openai"},
            created_at=created
        )
        
        assert metadata.execution_time == 2.5
        assert metadata.memory_usage == 1024
        assert metadata.token_usage == token_usage
        assert metadata.model_info == model_info
        assert metadata.framework_info == {"framework": "openai"}
        assert metadata.created_at == created


class TestErrorInfo:
    """Test ErrorInfo dataclass"""
    
    def test_minimal_initialization(self):
        """Test error info initialization with minimal parameters"""
        error = ErrorInfo(
            error_type="ValidationError",
            error_message="Invalid input provided"
        )
        
        assert error.error_type == "ValidationError"
        assert error.error_message == "Invalid input provided"
        assert error.error_code is None
        assert error.stack_trace is None
        assert error.retry_suggestions == []
    
    def test_full_initialization(self):
        """Test error info initialization with all parameters"""
        error = ErrorInfo(
            error_type="NetworkError",
            error_message="Connection timeout",
            error_code="TIMEOUT_001",
            stack_trace="Traceback...",
            retry_suggestions=["Check network connection", "Retry with backoff"]
        )
        
        assert error.error_type == "NetworkError"
        assert error.error_message == "Connection timeout"
        assert error.error_code == "TIMEOUT_001"
        assert error.stack_trace == "Traceback..."
        assert error.retry_suggestions == ["Check network connection", "Retry with backoff"]


class TestUniversalResult:
    """Test UniversalResult class"""
    
    def test_minimal_initialization(self):
        """Test result initialization with minimal parameters"""
        result = UniversalResult("Simple text result")
        
        assert result.content == "Simple text result"
        assert result.status == ResultStatus.SUCCESS
        assert result.result_type == ResultType.TEXT
        assert isinstance(result.metadata, ResultMetadata)
        assert result.error is None
        assert result.artifacts == []
        assert result.intermediate_steps == []
        assert result.citations == []
        assert result.confidence_score is None
    
    def test_full_initialization(self):
        """Test result initialization with all parameters"""
        metadata = ResultMetadata(execution_time=1.5)
        error = ErrorInfo("TestError", "Test error message")
        
        result = UniversalResult(
            content={"key": "value"},
            status=ResultStatus.PARTIAL_SUCCESS,
            result_type=ResultType.JSON,
            metadata=metadata,
            error=error
        )
        
        assert result.content == {"key": "value"}
        assert result.status == ResultStatus.PARTIAL_SUCCESS
        assert result.result_type == ResultType.JSON
        assert result.metadata == metadata
        assert result.error == error
    
    def test_artifact_management(self):
        """Test artifact management methods"""
        result = UniversalResult("Test result")
        
        # Initially no artifacts
        assert result.artifacts == []
        assert result.get_artifact("test") is None
        assert result.get_artifacts_by_type("file") == []
        
        # Add artifacts
        result.add_artifact("file1", "content1", "file")
        result.add_artifact("file2", "content2", "file")
        result.add_artifact("image1", b"binary_data", "image")
        
        assert len(result.artifacts) == 3
        
        # Get specific artifact
        file1 = result.get_artifact("file1")
        assert file1 is not None
        assert file1["name"] == "file1"
        assert file1["content"] == "content1"
        assert file1["type"] == "file"
        assert "created_at" in file1
        
        # Get artifacts by type
        files = result.get_artifacts_by_type("file")
        assert len(files) == 2
        images = result.get_artifacts_by_type("image")
        assert len(images) == 1
    
    def test_intermediate_steps(self):
        """Test intermediate steps functionality"""
        result = UniversalResult("Test result")
        
        assert result.intermediate_steps == []
        
        # Add steps
        result.add_intermediate_step("step1", "First step")
        result.add_intermediate_step("step2", "Second step", {"data": "value"})
        
        assert len(result.intermediate_steps) == 2
        
        step1 = result.intermediate_steps[0]
        assert step1["step_name"] == "step1"
        assert step1["description"] == "First step"
        assert step1["data"] is None
        assert "timestamp" in step1
        
        step2 = result.intermediate_steps[1]
        assert step2["step_name"] == "step2"
        assert step2["description"] == "Second step"
        assert step2["data"] == {"data": "value"}
    
    def test_citations(self):
        """Test citations functionality"""
        result = UniversalResult("Test result")
        
        assert result.citations == []
        
        # Add citations
        result.add_citation("Wikipedia", "Python Programming")
        result.add_citation("MDN", "JavaScript Guide", "https://developer.mozilla.org", "JS content")
        
        assert len(result.citations) == 2
        
        citation1 = result.citations[0]
        assert citation1["source"] == "Wikipedia"
        assert citation1["title"] == "Python Programming"
        assert citation1["url"] is None
        assert citation1["content"] is None
        assert "timestamp" in citation1
        
        citation2 = result.citations[1]
        assert citation2["source"] == "MDN"
        assert citation2["title"] == "JavaScript Guide"
        assert citation2["url"] == "https://developer.mozilla.org"
        assert citation2["content"] == "JS content"
    
    def test_status_checking(self):
        """Test status checking methods"""
        # Success
        success_result = UniversalResult("Success", status=ResultStatus.SUCCESS)
        assert success_result.is_successful()
        assert not success_result.is_failed()
        
        # Partial success
        partial_result = UniversalResult("Partial", status=ResultStatus.PARTIAL_SUCCESS)
        assert partial_result.is_successful()
        assert not partial_result.is_failed()
        
        # Failure
        failure_result = UniversalResult("Failed", status=ResultStatus.FAILURE)
        assert not failure_result.is_successful()
        assert failure_result.is_failed()
        
        # Error
        error_result = UniversalResult("Error", status=ResultStatus.ERROR)
        assert not error_result.is_successful()
        assert error_result.is_failed()
        
        # Timeout
        timeout_result = UniversalResult("Timeout", status=ResultStatus.TIMEOUT)
        assert not timeout_result.is_successful()
        assert timeout_result.is_failed()
        
        # Cancelled
        cancelled_result = UniversalResult("Cancelled", status=ResultStatus.CANCELLED)
        assert not cancelled_result.is_successful()
        assert not cancelled_result.is_failed()  # Cancelled is neither success nor failure
    
    def test_content_conversion(self):
        """Test content conversion methods"""
        # String content
        string_result = UniversalResult("Simple text")
        assert string_result.get_text_content() == "Simple text"
        assert string_result.get_json_content() == {"text": "Simple text"}
        
        # Dict content
        dict_content = {"key": "value", "number": 42}
        dict_result = UniversalResult(dict_content)
        assert dict_result.get_json_content() == dict_content
        text_content = dict_result.get_text_content()
        assert "key" in text_content
        assert "value" in text_content
        
        # Valid JSON string
        json_string = '{"valid": "json"}'
        json_result = UniversalResult(json_string)
        assert json_result.get_json_content() == {"valid": "json"}
        
        # Invalid JSON string
        invalid_json = "not json"
        invalid_result = UniversalResult(invalid_json)
        assert invalid_result.get_json_content() == {"text": "not json"}
        
        # Other types
        number_result = UniversalResult(42)
        assert number_result.get_text_content() == "42"
        assert number_result.get_json_content() == {"value": 42}
    
    def test_confidence_score(self):
        """Test confidence score functionality"""
        result = UniversalResult("Test result")
        
        assert result.confidence_score is None
        
        # Valid scores
        result.set_confidence_score(0.0)
        assert result.confidence_score == 0.0
        
        result.set_confidence_score(0.5)
        assert result.confidence_score == 0.5
        
        result.set_confidence_score(1.0)
        assert result.confidence_score == 1.0
        
        # Invalid scores
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            result.set_confidence_score(-0.1)
        
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            result.set_confidence_score(1.1)


class TestResultSerialization:
    """Test result serialization and deserialization"""
    
    def test_to_dict_minimal(self):
        """Test converting minimal result to dictionary"""
        result = UniversalResult("Test content")
        
        data = result.to_dict()
        
        assert data["content"] == "Test content"
        assert data["status"] == "success"
        assert data["result_type"] == "text"
        assert data["error"] is None
        assert data["artifacts"] == []
        assert data["intermediate_steps"] == []
        assert data["citations"] == []
        assert data["confidence_score"] is None
        
        # Check metadata
        metadata = data["metadata"]
        assert metadata["execution_time"] is None
        assert metadata["memory_usage"] is None
        assert "created_at" in metadata
    
    def test_to_dict_complete(self):
        """Test converting complete result to dictionary"""
        metadata = ResultMetadata(
            execution_time=2.5,
            memory_usage=1024,
            token_usage={"input": 100, "output": 50}
        )
        error = ErrorInfo("TestError", "Test message", "ERR001", "Stack trace", ["Retry"])
        
        result = UniversalResult(
            content={"result": "data"},
            status=ResultStatus.PARTIAL_SUCCESS,
            result_type=ResultType.JSON,
            metadata=metadata,
            error=error
        )
        
        result.add_artifact("file1", "content", "file")
        result.add_intermediate_step("step1", "Description")
        result.add_citation("Source", "Title")
        result.set_confidence_score(0.8)
        
        data = result.to_dict()
        
        assert data["content"] == {"result": "data"}
        assert data["status"] == "partial_success"
        assert data["result_type"] == "json"
        assert data["confidence_score"] == 0.8
        
        # Check error
        error_data = data["error"]
        assert error_data["error_type"] == "TestError"
        assert error_data["error_message"] == "Test message"
        assert error_data["error_code"] == "ERR001"
        assert error_data["retry_suggestions"] == ["Retry"]
        
        # Check metadata
        metadata_data = data["metadata"]
        assert metadata_data["execution_time"] == 2.5
        assert metadata_data["memory_usage"] == 1024
        assert metadata_data["token_usage"] == {"input": 100, "output": 50}
        
        # Check collections
        assert len(data["artifacts"]) == 1
        assert len(data["intermediate_steps"]) == 1
        assert len(data["citations"]) == 1
    
    def test_from_dict_minimal(self):
        """Test creating result from minimal dictionary"""
        data = {
            "content": "Test content",
            "status": "success",
            "result_type": "text",
            "metadata": {
                "created_at": "2024-01-01T12:00:00"
            }
        }
        
        result = UniversalResult.from_dict(data)
        
        assert result.content == "Test content"
        assert result.status == ResultStatus.SUCCESS
        assert result.result_type == ResultType.TEXT
        assert result.error is None
    
    def test_from_dict_complete(self):
        """Test creating result from complete dictionary"""
        data = {
            "content": {"key": "value"},
            "status": "error",
            "result_type": "json",
            "metadata": {
                "execution_time": 3.0,
                "memory_usage": 2048,
                "token_usage": {"input": 200, "output": 100},
                "created_at": "2024-01-01T12:00:00"
            },
            "error": {
                "error_type": "NetworkError",
                "error_message": "Connection failed",
                "error_code": "NET001",
                "stack_trace": "Traceback...",
                "retry_suggestions": ["Check connection", "Retry"]
            },
            "artifacts": [{"name": "file1", "content": "data", "type": "file"}],
            "intermediate_steps": [{"step_name": "step1", "description": "desc"}],
            "citations": [{"source": "src", "title": "title"}],
            "confidence_score": 0.9
        }
        
        result = UniversalResult.from_dict(data)
        
        assert result.content == {"key": "value"}
        assert result.status == ResultStatus.ERROR
        assert result.result_type == ResultType.JSON
        assert result.confidence_score == 0.9
        
        # Check error
        assert result.error.error_type == "NetworkError"
        assert result.error.error_message == "Connection failed"
        assert result.error.error_code == "NET001"
        assert result.error.retry_suggestions == ["Check connection", "Retry"]
        
        # Check metadata
        assert result.metadata.execution_time == 3.0
        assert result.metadata.memory_usage == 2048
        assert result.metadata.token_usage == {"input": 200, "output": 100}
        
        # Check collections
        assert len(result.artifacts) == 1
        assert len(result.intermediate_steps) == 1
        assert len(result.citations) == 1
    
    def test_round_trip_serialization(self):
        """Test that result can be serialized and deserialized without loss"""
        original = UniversalResult(
            content="Round trip test",
            status=ResultStatus.PARTIAL_SUCCESS,
            result_type=ResultType.ANALYSIS
        )
        
        original.add_artifact("test_file", "test_content", "file")
        original.add_intermediate_step("process", "Processing data", {"progress": 50})
        original.add_citation("Wikipedia", "Test Article", "https://example.com")
        original.set_confidence_score(0.75)
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = UniversalResult.from_dict(data)
        
        # Compare
        assert restored.content == original.content
        assert restored.status == original.status
        assert restored.result_type == original.result_type
        assert restored.confidence_score == original.confidence_score
        assert len(restored.artifacts) == len(original.artifacts)
        assert len(restored.intermediate_steps) == len(original.intermediate_steps)
        assert len(restored.citations) == len(original.citations)


class TestResultEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_large_content(self):
        """Test result with large content"""
        large_content = {"data": "A" * 10000, "numbers": list(range(1000))}
        result = UniversalResult(large_content)
        
        assert result.content == large_content
        assert result.get_json_content() == large_content
        
        # Should serialize without issues
        data = result.to_dict()
        restored = UniversalResult.from_dict(data)
        assert restored.content == large_content
    
    def test_unicode_content(self):
        """Test result with unicode content"""
        unicode_content = "测试内容 🚀 émojis and ñoñ-ASCII"
        result = UniversalResult(unicode_content)
        
        assert result.content == unicode_content
        assert result.get_text_content() == unicode_content
        
        # Should serialize/deserialize correctly
        data = result.to_dict()
        restored = UniversalResult.from_dict(data)
        assert restored.content == unicode_content
    
    def test_none_content(self):
        """Test result with None content"""
        result = UniversalResult(None)
        
        assert result.content is None
        assert result.get_text_content() == "None"
        assert result.get_json_content() == {"value": None}
    
    def test_binary_content(self):
        """Test result with binary content"""
        binary_content = b"binary data \x00\x01\x02"
        result = UniversalResult(binary_content, result_type=ResultType.BINARY)
        
        assert result.content == binary_content
        assert result.result_type == ResultType.BINARY
        
        # Text conversion should work
        text = result.get_text_content()
        assert isinstance(text, str)
    
    def test_malformed_json_content(self):
        """Test handling of malformed JSON content"""
        malformed_json = '{"incomplete": json'
        result = UniversalResult(malformed_json)
        
        # Should handle gracefully
        json_content = result.get_json_content()
        assert json_content == {"text": malformed_json}
    
    def test_artifact_name_collision(self):
        """Test handling of artifact name collisions"""
        result = UniversalResult("Test")
        
        result.add_artifact("same_name", "content1", "file")
        result.add_artifact("same_name", "content2", "file")
        
        # Should have both artifacts
        assert len(result.artifacts) == 2
        
        # get_artifact should return the first one
        artifact = result.get_artifact("same_name")
        assert artifact["content"] == "content1"


if __name__ == "__main__":
    pytest.main([__file__]) 