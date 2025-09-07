"""
AutoGen v0.4 Adapter Comprehensive Tests
Complete test suite for the new AutoGen v0.4 (autogen-agentchat) adapter
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Test target imports
from layers.adapter.autogen.adapter import (
    AutoGenV04Adapter, 
    create_autogen_v04_adapter,
    AUTOGEN_V04_AVAILABLE
)
from layers.framework.abstractions.task import (
    UniversalTask, 
    TaskType, 
    TaskPriority, 
    TaskRequirements
)
from layers.framework.abstractions.result import ResultStatus
from layers.framework.abstractions.context import UniversalContext
from layers.adapter.base import (
    AdapterError, 
    AdapterInitializationError, 
    AdapterExecutionError
)


@pytest.mark.autogen
class TestAutoGenV04Adapter:
    """Comprehensive test suite for AutoGen v0.4 adapter"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        self.test_api_key = os.getenv("OPENAI_API_KEY_TEST", "test-key-12345")
        self.real_api_key = os.getenv("OPENAI_API_KEY")
        self.work_dir = tempfile.mkdtemp()
        
        yield
        
        # Cleanup
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
    
    def test_adapter_availability(self):
        """Test AutoGen v0.4 availability detection"""
        if AUTOGEN_V04_AVAILABLE:
            # Test successful initialization
            adapter = AutoGenV04Adapter("test_adapter")
            assert adapter.name == "test_adapter"
            assert hasattr(adapter, 'agents')
            assert hasattr(adapter, 'llm_backends')
        else:
            # Test error when not available
            with pytest.raises(AdapterInitializationError):
                AutoGenV04Adapter("test_adapter")
    
    def test_adapter_initialization(self):
        """Test adapter initialization with various configs"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        # Test minimal initialization
        adapter1 = AutoGenV04Adapter("minimal")
        assert adapter1.name == "minimal"
        assert adapter1.default_model == "gpt-3.5-turbo"
        
        # Test full configuration
        config = {
            "default_model": "gpt-4",
            "default_temperature": 0.8,
            "work_dir": self.work_dir
        }
        adapter2 = AutoGenV04Adapter("configured", config)
        assert adapter2.default_model == "gpt-4"
        assert adapter2.default_temperature == 0.8
        assert adapter2.work_dir == self.work_dir
    
    def test_adapter_info(self):
        """Test adapter info provides complete information"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("info_test")
        info = adapter.get_info()
        
        assert info.name == "info_test"
        assert info.version == "0.4.0"
        assert "AutoGen v0.4" in info.description
        assert len(info.capabilities) > 0
        assert len(info.supported_models) > 0
    
    def test_llm_backend_creation(self):
        """Test LLM backend creation and validation"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("backend_test")
        
        # Test OpenAI backend creation
        backend_id = adapter.create_llm_backend(
            backend_id="openai_backend",
            backend_type="openai",
            api_key=self.test_api_key,
            model="gpt-3.5-turbo"
        )
        assert backend_id == "openai_backend"
        assert backend_id in adapter.llm_backends
        
        # Test DeepSeek backend creation
        backend_id = adapter.create_llm_backend(
            backend_id="deepseek_backend",
            backend_type="deepseek",
            api_key=self.test_api_key,
            model="deepseek-chat"
        )
        assert backend_id == "deepseek_backend"
        assert backend_id in adapter.llm_backends
        
        # Test invalid backend type
        with pytest.raises(AdapterError):
            adapter.create_llm_backend(
                backend_id="invalid",
                backend_type="invalid_type",
                api_key=self.test_api_key
            )
        
        # Test missing API key
        with pytest.raises(AdapterError):
            adapter.create_llm_backend(
                backend_id="no_key",
                backend_type="openai"
            )
    
    def test_assistant_agent_creation(self):
        """Test AssistantAgent creation"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("agent_test")
        
        # Create LLM backend first
        backend_id = adapter.create_llm_backend(
            backend_id="test_backend",
            backend_type="openai",
            api_key=self.test_api_key,
            model="gpt-3.5-turbo"
        )
        
        # Create assistant agent
        agent_id = adapter.create_assistant_agent(
            agent_id="test_assistant",
            name="test_assistant",
            system_message="You are a helpful assistant",
            backend_id=backend_id
        )
        
        assert agent_id == "test_assistant"
        assert agent_id in adapter.agents
        
        # Test with non-existent backend
        with pytest.raises(AdapterError):
            adapter.create_assistant_agent(
                "invalid_agent", "Invalid", "Test", "non_existent_backend"
            )
    
    def test_code_executor_agent_creation(self):
        """Test CodeExecutorAgent creation"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("executor_test")
        
        # Create code executor agent
        agent_id = adapter.create_code_executor_agent(
            agent_id="test_executor",
            name="test_executor",
            work_dir=self.work_dir
        )
        
        assert agent_id == "test_executor"
        assert agent_id in adapter.code_executors
    
    def test_user_proxy_agent_creation(self):
        """Test UserProxyAgent creation"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("proxy_test")
        
        # Create user proxy agent
        agent_id = adapter.create_user_proxy_agent(
            agent_id="test_proxy",
            name="test_proxy"
        )
        
        assert agent_id == "test_proxy"
        assert agent_id in adapter.user_proxies
    
    def test_team_creation(self):
        """Test team creation with various agent types"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("team_test")
        
        # Create LLM backend and agents
        backend_id = adapter.create_llm_backend(
            backend_id="client",
            backend_type="openai",
            api_key=self.test_api_key,
            model="gpt-3.5-turbo"
        )
        
        assistant_id = adapter.create_assistant_agent(
            "assistant", "assistant", "Test", backend_id
        )
        executor_id = adapter.create_code_executor_agent("executor", "executor")
        proxy_id = adapter.create_user_proxy_agent("proxy", "proxy")
        
        # Create team
        team_id = adapter._create_team_internal(
            team_id="test_team",
            agent_ids=[assistant_id, executor_id],
            max_turns=5,
            termination_keywords=["TERMINATE"]
        )
        
        assert team_id == "test_team"
        assert team_id in adapter.teams
        
        # Test team with non-existent agent
        with pytest.raises(AdapterError):
            adapter._create_team_internal("invalid_team", ["non_existent_agent"])
    
    @pytest.mark.asyncio
    async def test_chat_task_execution(self):
        """Test chat task execution with different LLM backends"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("chat_test")
        
        # Test with OpenAI backend
        with patch('layers.adapter.autogen.llm_backend.OpenAIBackend') as mock_backend_class:
            with patch('layers.adapter.autogen.adapter.AssistantAgent') as mock_agent_class:
                # Setup mocks
                mock_backend = Mock()
                mock_backend.chat_completion = AsyncMock(return_value={
                    "choices": [{"message": {"content": "Hello! How can I help you?"}}]
                })
                mock_backend_class.return_value = mock_backend
                
                mock_agent = Mock()
                mock_response = Mock()
                mock_response.chat_message.content = "Hello! How can I help you?"
                mock_agent.on_messages = AsyncMock(return_value=mock_response)
                mock_agent.name = "Test Assistant"
                mock_agent_class.return_value = mock_agent
                
                # Create backend and agent
                backend_id = adapter.create_llm_backend(
                    backend_id="openai_test",
                    backend_type="openai",
                    api_key=self.test_api_key
                )
                agent_id = adapter.create_assistant_agent(
                    "openai_agent",
                    "OpenAI Assistant",
                    "Test",
                    backend_id
                )
                
                # Execute task
                task = UniversalTask(
                    content="Hello, how are you?",
                    task_type=TaskType.CONVERSATION,
                    priority=TaskPriority.NORMAL,
                    requirements=TaskRequirements(),
                    context={},
                    task_id="openai_chat_test"
                )
                
                context = UniversalContext({'user_id': 'test_user'})
                result = await adapter.execute_task(task, context)
                
                assert result.status == ResultStatus.SUCCESS
                assert "reply" in result.content
                assert result.content["agent_id"] == agent_id
        
        # Clear agents for next test
        adapter.agents.clear()
        
        # Test with DeepSeek backend
        with patch('layers.adapter.autogen.llm_backend.DeepSeekBackend') as mock_backend_class:
            with patch('layers.adapter.autogen.adapter.AssistantAgent') as mock_agent_class:
                # Setup mocks
                mock_backend = Mock()
                mock_backend.chat_completion = AsyncMock(return_value={
                    "choices": [{"message": {"content": "Hello from DeepSeek!"}}]
                })
                mock_backend_class.return_value = mock_backend
                
                mock_agent = Mock()
                mock_response = Mock()
                mock_response.chat_message.content = "Hello from DeepSeek!"
                mock_agent.on_messages = AsyncMock(return_value=mock_response)
                mock_agent.name = "Test Assistant"
                mock_agent_class.return_value = mock_agent
                
                # Create backend and agent
                backend_id = adapter.create_llm_backend(
                    backend_id="deepseek_test",
                    backend_type="deepseek",
                    api_key=self.test_api_key
                )
                agent_id = adapter.create_assistant_agent(
                    "deepseek_agent",
                    "deepseek_assistant",
                    "Test",
                    backend_id
                )
                
                # Execute task
                task = UniversalTask(
                    content="Hello, how are you?",
                    task_type=TaskType.CONVERSATION,
                    priority=TaskPriority.NORMAL,
                    requirements=TaskRequirements(),
                    context={},
                    task_id="deepseek_chat_test"
                )
                
                context = UniversalContext({'user_id': 'test_user'})
                result = await adapter.execute_task(task, context)
                
                assert result.status == ResultStatus.SUCCESS
                assert "reply" in result.content
                assert result.content["agent_id"] == agent_id
    
    @pytest.mark.asyncio
    async def test_code_task_execution(self):
        """Test code generation task execution"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("code_test")
        
        # Mock components
        with patch('layers.adapter.autogen.adapter.create_llm_backend'):
            with patch('layers.adapter.autogen.adapter.AssistantAgent'):
                with patch('layers.adapter.autogen.adapter.CodeExecutorAgent'):
                    with patch('layers.adapter.autogen.adapter.RoundRobinGroupChat') as mock_team:
                        # Setup mocks
                        mock_team_instance = Mock()
                        mock_result = Mock()
                        mock_result.messages = ["msg1", "msg2"]
                        mock_team_instance.run = AsyncMock(return_value=mock_result)
                        mock_team.return_value = mock_team_instance
                        
                        # Create components
                        backend_id = adapter.create_llm_backend(
                            backend_id="client",
                            backend_type="openai",
                            api_key=self.test_api_key,
                            model="gpt-3.5-turbo"
                        )
                        agent_id = adapter.create_assistant_agent("agent", "agent", "Test", backend_id)
                        
                        # Execute task
                        task = UniversalTask(
                            content="Write a Python function to calculate factorial",
                            task_type=TaskType.CODE_GENERATION,
                            priority=TaskPriority.NORMAL,
                            requirements=TaskRequirements(),
                            context={},
                            task_id="code_test"
                        )
                        
                        context = UniversalContext({'user_id': 'test_user'})
                        result = await adapter.execute_task(task, context)
                        
                        assert result.status == ResultStatus.SUCCESS
                        assert "code_result" in result.content
    
    @pytest.mark.asyncio
    async def test_collaboration_task_execution(self):
        """Test collaboration task execution"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("collab_test")
        
        # Mock components
        with patch('layers.adapter.autogen.adapter.create_llm_backend'):
            with patch('layers.adapter.autogen.adapter.AssistantAgent') as mock_agent:
                with patch('layers.adapter.autogen.adapter.RoundRobinGroupChat') as mock_team:
                    # Setup mocks
                    mock_agent_instance = Mock()
                    mock_agent_instance.name = "Test Agent"
                    mock_agent.return_value = mock_agent_instance
                    
                    mock_team_instance = Mock()
                    mock_team_instance.participants = [mock_agent_instance]
                    mock_result = Mock()
                    mock_result.messages = ["msg1", "msg2", "msg3"]
                    mock_team_instance.run = AsyncMock(return_value=mock_result)
                    mock_team.return_value = mock_team_instance
                    
                    # Create components
                    backend_id = adapter.create_llm_backend(
                        backend_id="client",
                        backend_type="openai",
                        api_key=self.test_api_key,
                        model="gpt-3.5-turbo"
                    )
                    agent_id = adapter.create_assistant_agent("agent", "agent", "Test", backend_id)
                    team_id = adapter._create_team_internal("team", [agent_id])
                    
                    # Execute task
                    task = UniversalTask(
                        content="Let's collaborate on solving this problem",
                        task_type=TaskType.TOOL_EXECUTION,
                        priority=TaskPriority.HIGH,
                        requirements=TaskRequirements(),
                        context={},
                        task_id="collab_test"
                    )
                    
                    context = UniversalContext({'user_id': 'test_user'})
                    result = await adapter.execute_task(task, context)
                    
                    assert result.status == ResultStatus.SUCCESS
                    assert "participants" in result.content
                    assert result.content["team_id"] == team_id
    
    @pytest.mark.asyncio
    async def test_task_execution_errors(self):
        """Test task execution error handling"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("error_test")
        
        # Test unsupported task type
        task = UniversalTask(
            content="Test task",
            task_type="UNSUPPORTED_TYPE",
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={},
            task_id="error_test"
        )
        
        context = UniversalContext({'user_id': 'test_user'})
        result = await adapter.execute_task(task, context)
        
        assert result.status == ResultStatus.FAILURE
        assert "error" in result.content
    
    def test_agent_status_retrieval(self):
        """Test agent status retrieval"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("status_test")
        
        # Test non-existent agent
        status = adapter.get_agent_status("non_existent")
        assert status["status"] == "not_found"
        
        # Create agents and test status
        with patch('layers.adapter.autogen.adapter.create_llm_backend'):
            with patch('layers.adapter.autogen.adapter.AssistantAgent') as mock_agent:
                mock_agent_instance = Mock()
                mock_agent_instance.name = "Test Agent"
                mock_agent.return_value = mock_agent_instance
                
                backend_id = adapter.create_llm_backend(
                    backend_id="client",
                    backend_type="openai",
                    api_key=self.test_api_key,
                    model="gpt-3.5-turbo"
                )
                agent_id = adapter.create_assistant_agent("agent", "agent", "Test", backend_id)
                
                status = adapter.get_agent_status(agent_id)
                assert status["status"] == "active"
                assert status["agent_type"] == "assistant"
                assert status["agent_id"] == agent_id
    
    def test_team_status_retrieval(self):
        """Test team status retrieval"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("team_status_test")
        
        # Test non-existent team
        status = adapter.get_team_status("non_existent")
        assert status["status"] == "not_found"
        
        # Create team and test status
        with patch('layers.adapter.autogen.adapter.create_llm_backend'):
            with patch('layers.adapter.autogen.adapter.AssistantAgent') as mock_agent:
                with patch('layers.adapter.autogen.adapter.RoundRobinGroupChat') as mock_team:
                    mock_agent_instance = Mock()
                    mock_agent_instance.name = "Test Agent"
                    mock_agent.return_value = mock_agent_instance
                    
                    mock_team_instance = Mock()
                    mock_team_instance.participants = [mock_agent_instance]
                    mock_team.return_value = mock_team_instance
                    
                    backend_id = adapter.create_llm_backend(
                        backend_id="client",
                        backend_type="openai",
                        api_key=self.test_api_key,
                        model="gpt-3.5-turbo"
                    )
                    agent_id = adapter.create_assistant_agent("agent", "agent", "Test", backend_id)
                    team_id = adapter._create_team_internal("team", [agent_id])
                    
                    status = adapter.get_team_status(team_id)
                    assert status["status"] == "active"
                    assert status["team_id"] == team_id
                    assert len(status["participants"]) == 1
    
    def test_adapter_status(self):
        """Test adapter status"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("adapter_status_test")
        status = adapter.get_adapter_status()
        
        assert status["adapter_name"] == "adapter_status_test"
        assert status["autogen_version"] == "0.4+"
        assert status["autogen_available"] == AUTOGEN_V04_AVAILABLE
        assert "agents_count" in status
        assert "teams_count" in status
        assert "model_clients_count" in status
    
    @pytest.mark.asyncio
    async def test_adapter_cleanup(self):
        """Test adapter cleanup and resource management"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        adapter = AutoGenV04Adapter("cleanup_test")
        
        # Mock model client with close method
        with patch('layers.adapter.autogen.adapter.create_llm_backend') as mock_client_class:
            mock_client = Mock()
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Create LLM backend
            adapter.create_llm_backend(
                backend_id="client",
                backend_type="openai",
                api_key=self.test_api_key,
                model="gpt-3.5-turbo"
            )
            
            # Test cleanup
            await adapter.close()
            
            # Verify close was called
            mock_client.close.assert_called_once()
    
    def test_convenience_function(self):
        """Test convenience function for adapter creation"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        with patch('layers.adapter.autogen.adapter.create_llm_backend'):
            adapter = create_autogen_v04_adapter(
                name="convenience_test",
                api_key=self.test_api_key,
                model="gpt-4",
                temperature=0.8
            )
            
            assert adapter.name == "convenience_test"
            assert adapter.default_model == "gpt-4"
            assert "default" in adapter.llm_backends


@pytest.mark.integration
@pytest.mark.api_key_required
class TestAutoGenV04AdapterIntegration:
    """Integration tests for AutoGen v0.4 adapter with real APIs"""
    
    @pytest.mark.asyncio
    async def test_real_deepseek_chat(self):
        """Test chat with real DeepSeek API"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("No DEEPSEEK_API_KEY for integration test")
        
        adapter = AutoGenV04Adapter("integration_test", {
            "backend_type": "deepseek",
            "default_model": "deepseek-chat"
        })
        
        try:
            # Create DeepSeek backend
            backend_id = adapter.create_llm_backend(
                backend_id="deepseek_test",
                backend_type="deepseek",
                api_key=api_key,
                model="deepseek-chat",
                temperature=0.1
            )
            
            # Create assistant agent
            agent_id = adapter.create_assistant_agent(
                "deepseek_agent",
                "deepseek_assistant",  # Must be a valid Python identifier
                "You are a helpful assistant. Be very brief.",
                backend_id
            )
            
            # Execute chat task
            task = UniversalTask(
                content="Say hello in exactly 3 words.",
                task_type=TaskType.CONVERSATION,
                priority=TaskPriority.NORMAL,
                requirements=TaskRequirements(),
                context={},
                task_id="deepseek_integration_test"
            )
            
            context = UniversalContext({'user_id': 'integration_user'})
            result = await asyncio.wait_for(
                adapter.execute_task(task, context),
                timeout=30.0
            )
            
            assert result.is_successful()
            assert "reply" in result.data
            assert len(result.data["reply"]) > 0
            assert result.data["agent_id"] == agent_id
            
        finally:
            await adapter.close()
    
    @pytest.mark.asyncio
    async def test_real_deepseek_team_chat(self):
        """Test team chat with real DeepSeek API"""
        if not AUTOGEN_V04_AVAILABLE:
            pytest.skip("AutoGen v0.4 not available")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("No DEEPSEEK_API_KEY for integration test")
        
        adapter = AutoGenV04Adapter("team_integration_test", {
            "backend_type": "deepseek",
            "default_model": "deepseek-chat"
        })
        
        try:
            # Create DeepSeek backend
            backend_id = adapter.create_llm_backend(
                backend_id="deepseek_team",
                backend_type="deepseek",
                api_key=api_key,
                model="deepseek-chat",
                temperature=0.1
            )
            
            # Create two assistant agents
            agent1_id = adapter.create_assistant_agent(
                "agent1",
                "creative_assistant",  # Must be a valid Python identifier
                "You are a creative assistant. Generate interesting ideas.",
                backend_id
            )
            
            agent2_id = adapter.create_assistant_agent(
                "agent2",
                "critical_assistant",  # Must be a valid Python identifier
                "You are a critical thinker. Analyze and improve ideas.",
                backend_id
            )
            
            # Create team
            team_id = adapter._create_team_internal(
                team_id="deepseek_team",
                agent_ids=[agent1_id, agent2_id],
                max_turns=3
            )
            
            # Execute collaboration task
            task = UniversalTask(
                content="Suggest a name for a new programming language and explain why it's good.",
                task_type=TaskType.TOOL_EXECUTION,
                priority=TaskPriority.NORMAL,
                requirements=TaskRequirements(),
                context={},
                task_id="deepseek_team_test"
            )
            
            context = UniversalContext({'user_id': 'integration_user'})
            result = await asyncio.wait_for(
                adapter.execute_task(task, context),
                timeout=60.0
            )
            
            assert result.status == ResultStatus.SUCCESS
            assert "team_id" in result.content
            assert result.content["team_id"] == team_id
            assert "conversation_log" in result.content
            assert len(result.content["conversation_log"]) > 0
            
        finally:
            await adapter.close()


if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",
        "--durations=10"
    ]) 