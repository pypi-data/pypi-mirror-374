"""
DeepSeekAdapter单元测试
测试DeepSeek适配器的所有功能
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

from layers.adapter.deepseek.adapter import DeepSeekAdapter, DeepSeekAgent


class TestDeepSeekAdapter:
    """测试DeepSeekAdapter类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.adapter = DeepSeekAdapter("test_adapter")
        
        # 模拟配置
        self.mock_config = {
            "api_key": "test_api_key_12345",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-coder",
            "timeout": 30,
            "max_retries": 3
        }
    
    def test_adapter_initialization(self):
        """测试适配器初始化"""
        assert self.adapter.name == "test_adapter"
        assert self.adapter.api_key is None
        assert self.adapter.base_url is None
        assert self.adapter.model is None
        assert self.adapter.timeout == 30
        assert self.adapter.max_retries == 3
        assert self.adapter.client is None
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_initialize_success(self, mock_openai_client):
        """测试成功初始化"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_openai_client.return_value = mock_client
        
        # 初始化适配器
        success = await self.adapter.initialize(self.mock_config)
        
        assert success is True
        assert self.adapter.api_key == "test_api_key_12345"
        assert self.adapter.base_url == "https://api.deepseek.com/v1"
        assert self.adapter.model == "deepseek-coder"
        assert self.adapter.client == mock_client
        
        # 验证OpenAI客户端被正确创建
        mock_openai_client.assert_called_once_with(
            api_key="test_api_key_12345",
            base_url="https://api.deepseek.com/v1"
        )
    
    async def test_initialize_missing_api_key(self):
        """测试缺少API密钥的初始化"""
        config_without_key = {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-coder"
        }
        
        success = await self.adapter.initialize(config_without_key)
        assert success is False
        assert self.adapter.api_key is None
    
    async def test_initialize_missing_base_url(self):
        """测试缺少基础URL的初始化"""
        config_without_url = {
            "api_key": "test_api_key_12345",
            "model": "deepseek-coder"
        }
        
        success = await self.adapter.initialize(config_without_url)
        assert success is False
        assert self.adapter.base_url is None
    
    async def test_initialize_missing_model(self):
        """测试缺少模型的初始化"""
        config_without_model = {
            "api_key": "test_api_key_12345",
            "base_url": "https://api.deepseek.com/v1"
        }
        
        success = await self.adapter.initialize(config_without_model)
        assert success is False
        assert self.adapter.model is None
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_initialize_with_custom_timeout(self, mock_openai_client):
        """测试使用自定义超时的初始化"""
        mock_client = Mock()
        mock_openai_client.return_value = mock_client
        
        config_with_timeout = self.mock_config.copy()
        config_with_timeout["timeout"] = 60
        
        success = await self.adapter.initialize(config_with_timeout)
        
        assert success is True
        assert self.adapter.timeout == 60
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_initialize_with_custom_retries(self, mock_openai_client):
        """测试使用自定义重试次数的初始化"""
        mock_client = Mock()
        mock_openai_client.return_value = mock_client
        
        config_with_retries = self.mock_config.copy()
        config_with_retries["max_retries"] = 5
        
        success = await self.adapter.initialize(config_with_retries)
        
        assert success is True
        assert self.adapter.max_retries == 5
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_create_agent_success(self, mock_openai_client):
        """测试成功创建Agent"""
        # 初始化适配器
        mock_client = Mock()
        mock_openai_client.return_value = mock_client
        await self.adapter.initialize(self.mock_config)
        
        # 创建Agent
        agent_config = {
            "name": "test_agent",
            "description": "Test DeepSeek agent",
            "capabilities": ["conversation", "code_generation"]
        }
        
        agent = await self.adapter.create_agent(agent_config)
        
        assert agent is not None
        assert isinstance(agent, DeepSeekAgent)
        assert agent.name == "test_agent"
        assert agent.description == "Test DeepSeek agent"
        assert agent.adapter == self.adapter
        assert agent.agent_id is not None
    
    async def test_create_agent_without_initialization(self):
        """测试未初始化时创建Agent"""
        agent_config = {
            "name": "test_agent",
            "description": "Test agent"
        }
        
        agent = await self.adapter.create_agent(agent_config)
        assert agent is None
    
    async def test_create_agent_missing_name(self):
        """测试缺少名称时创建Agent"""
        # 初始化适配器
        await self.adapter.initialize(self.mock_config)
        
        agent_config = {
            "description": "Test agent without name"
        }
        
        agent = await self.adapter.create_agent(agent_config)
        assert agent is None
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_test_connection_success(self, mock_openai_client):
        """测试成功连接测试"""
        # 模拟成功的API调用
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello from DeepSeek"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client
        
        # 初始化适配器
        await self.adapter.initialize(self.mock_config)
        
        # 测试连接
        success = await self.adapter.test_connection()
        assert success is True
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_test_connection_failure(self, mock_openai_client):
        """测试连接测试失败"""
        # 模拟失败的API调用
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API connection failed")
        )
        mock_openai_client.return_value = mock_client
        
        # 初始化适配器
        await self.adapter.initialize(self.mock_config)
        
        # 测试连接
        success = await self.adapter.test_connection()
        assert success is False
    
    async def test_test_connection_without_initialization(self):
        """测试未初始化时的连接测试"""
        success = await self.adapter.test_connection()
        assert success is False
    
    def test_get_status(self):
        """测试获取适配器状态"""
        # 未初始化状态
        status = self.adapter.get_status()
        assert status["initialized"] is False
        assert status["api_key"] is None
        assert status["base_url"] is None
        assert status["model"] is None
        
        # 初始化后状态
        asyncio.run(self.adapter.initialize(self.mock_config))
        status = self.adapter.get_status()
        assert status["initialized"] is True
        assert status["api_key"] == "test_api_key_12345"
        assert status["base_url"] == "https://api.deepseek.com/v1"
        assert status["model"] == "deepseek-coder"
    
    def test_get_capabilities(self):
        """测试获取适配器能力"""
        capabilities = self.adapter.get_capabilities()
        assert "conversation" in capabilities
        assert "code_generation" in capabilities
        assert "text_analysis" in capabilities
        assert len(capabilities) == 3


class TestDeepSeekAgent:
    """测试DeepSeekAgent类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_adapter = Mock(spec=DeepSeekAdapter)
        self.mock_adapter.model = "deepseek-coder"
        self.mock_adapter.timeout = 30
        
        self.agent = DeepSeekAgent(
            name="test_agent",
            description="Test DeepSeek agent",
            adapter=self.mock_adapter
        )
    
    def test_agent_initialization(self):
        """测试Agent初始化"""
        assert self.agent.name == "test_agent"
        assert self.agent.description == "Test DeepSeek agent"
        assert self.agent.adapter == self.mock_adapter
        assert self.agent.agent_id is not None
        assert len(self.agent.agent_id) > 0
    
    def test_agent_id_uniqueness(self):
        """测试Agent ID的唯一性"""
        agent1 = DeepSeekAgent("agent1", "First agent", self.mock_adapter)
        agent2 = DeepSeekAgent("agent2", "Second agent", self.mock_adapter)
        
        assert agent1.agent_id != agent2.agent_id
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_chat_success(self, mock_openai_client):
        """测试成功聊天"""
        # 模拟成功的API调用
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you today?"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client
        
        # 模拟适配器客户端
        self.mock_adapter.client = mock_client
        
        # 执行聊天
        message = "Hello, how are you?"
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        response = await self.agent.chat(message, context)
        
        assert response is not None
        assert "Hello! How can I help you today?" in response
        
        # 验证API调用
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        
        # 验证消息格式
        messages = call_args[1]["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == message
        
        # 验证模型
        assert call_args[1]["model"] == "deepseek-coder"
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_chat_with_context(self, mock_openai_client):
        """测试带上下文的聊天"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I see you're working on a Python project."
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client
        
        self.mock_adapter.client = mock_client
        
        # 执行带上下文的聊天
        message = "What should I do next?"
        context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "project_type": "Python",
            "current_task": "API development"
        }
        
        response = await self.agent.chat(message, context)
        
        assert response is not None
        
        # 验证上下文被包含在消息中
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        
        # 应该包含上下文信息
        assert any("Python" in str(msg.get("content", "")) for msg in messages)
    
    @patch('layers.adapter.deepseek.adapter.openai.AsyncOpenAI')
    async def test_chat_api_failure(self, mock_openai_client):
        """测试聊天API失败"""
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API request failed")
        )
        mock_openai_client.return_value = mock_client
        
        self.mock_adapter.client = mock_client
        
        # 执行聊天应该失败
        message = "Hello"
        context = {}
        
        with pytest.raises(Exception, match="API request failed"):
            await self.agent.chat(message, context)
    
    async def test_chat_without_adapter_client(self):
        """测试没有适配器客户端时的聊天"""
        self.mock_adapter.client = None
        
        message = "Hello"
        context = {}
        
        with pytest.raises(ValueError, match="Adapter not properly initialized"):
            await self.agent.chat(message, context)
    
    def test_agent_representation(self):
        """测试Agent的字符串表示"""
        representation = str(self.agent)
        assert "test_agent" in representation
        assert "DeepSeekAgent" in representation
        assert self.agent.agent_id in representation
    
    def test_agent_equality(self):
        """测试Agent相等性"""
        agent1 = DeepSeekAgent("agent1", "First agent", self.mock_adapter)
        agent2 = DeepSeekAgent("agent2", "Second agent", self.mock_adapter)
        agent3 = DeepSeekAgent("agent1", "First agent", self.mock_adapter)
        
        # 相同名称和描述的Agent应该相等
        assert agent1 == agent3
        assert agent1 != agent2
        
        # 与不同类型对象比较
        assert agent1 != "not_an_agent"
        assert agent1 != None


if __name__ == "__main__":
    pytest.main([__file__]) 