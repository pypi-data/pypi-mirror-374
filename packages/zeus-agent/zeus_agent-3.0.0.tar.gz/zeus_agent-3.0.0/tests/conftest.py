"""
Global pytest configuration and fixtures for ADC test suite.
"""
import pytest
import asyncio
import tempfile
import os
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock

# Test configuration
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """Create a temporary config file for testing."""
    config_content = """
environment: test
debug: true
logging:
  level: DEBUG
  format: json
database:
  url: sqlite:///:memory:
cache:
  type: memory
  ttl: 300
"""
    config_file = temp_dir / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = AsyncMock(
        choices=[
            Mock(
                message=Mock(
                    content="Test response from OpenAI",
                    role="assistant"
                )
            )
        ],
        usage=Mock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    )
    return mock_client

@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """Sample task data for testing."""
    return {
        "id": "test-task-123",
        "content": "Test task content",
        "priority": "high",
        "requirements": {
            "max_execution_time": 30.0,
            "memory_limit": 1024,
            "cpu_limit": 2
        },
        "context": {
            "user_id": "test-user",
            "session_id": "test-session"
        }
    }

@pytest.fixture
def sample_agent_config() -> Dict[str, Any]:
    """Sample agent configuration for testing."""
    return {
        "name": "test-agent",
        "type": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "capabilities": ["text_generation", "code_analysis"]
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set test environment variables
    os.environ["ADC_ENV"] = "test"
    os.environ["ADC_LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup after test
    test_env_vars = ["ADC_ENV", "ADC_LOG_LEVEL"]
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]

@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed_ms(self) -> float:
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return 0.0
        
        def assert_under(self, max_ms: float):
            assert self.elapsed_ms < max_ms, f"Operation took {self.elapsed_ms:.2f}ms, limit is {max_ms}ms"
    
    return Timer()

# Performance test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test with timing requirements"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker for tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["slow", "benchmark", "stress"]):
            item.add_marker(pytest.mark.slow) 

# AutoGen adapter test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests requiring real API keys"
    )
    config.addinivalue_line(
        "markers", "autogen: marks tests specific to AutoGen adapter"
    )
    config.addinivalue_line(
        "markers", "api_key_required: marks tests requiring valid API keys"
    )

@pytest.fixture(scope="session")
def test_api_key():
    """Provide test API key from environment"""
    return os.getenv("OPENAI_API_KEY_TEST", "test-key-12345")

@pytest.fixture(scope="session") 
def real_api_key():
    """Provide real API key for integration tests"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No real OPENAI_API_KEY provided for integration test")
    return api_key

@pytest.fixture
def temp_work_dir():
    """Provide temporary work directory"""
    work_dir = tempfile.mkdtemp()
    yield work_dir
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)

@pytest.fixture
def mock_llm_config(test_api_key):
    """Provide mock LLM configuration"""
    return {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "api_key": test_api_key
    }

@pytest.fixture
def real_llm_config(real_api_key):
    """Provide real LLM configuration for integration tests"""
    return {
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": 100,
        "api_key": real_api_key
    } 