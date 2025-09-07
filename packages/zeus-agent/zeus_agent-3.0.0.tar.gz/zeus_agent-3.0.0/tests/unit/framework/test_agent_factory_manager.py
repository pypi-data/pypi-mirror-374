"""
Agent Factory Manager Tests
测试Agent工厂管理器的功能
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from layers.framework.abstractions.agent_factory_manager import (
    AgentFactoryManager,
    AgentType,
    ModelConfig,
    ToolConfig,
    MemoryConfig,
    BehaviorConfig,
    AgentConfig,
    TeamConfig,
    TeamType,
    CommunicationPattern
)
from layers.framework.abstractions.agent import AgentCapability
from layers.adapter.registry.adapter_registry import AdapterRegistry


@pytest.mark.asyncio
class TestAgentFactoryManager:
    """测试Agent工厂管理器"""
    
    @pytest_asyncio.fixture
    async def factory_manager(self):
        """创建工厂管理器实例"""
        with patch('layers.framework.abstractions.agent_factory_manager.AdapterRegistry') as mock_registry:
            # 模拟适配器注册表
            mock_registry_instance = Mock()
            mock_registry_instance.get_adapter = AsyncMock()
            mock_registry.return_value = mock_registry_instance
            
            factory = AgentFactoryManager()
            factory.adapter_registry = mock_registry_instance
            return factory
    
    async def test_agent_templates(self, factory_manager):
        """测试Agent模板管理"""
        # 验证预定义模板
        templates = factory_manager.list_agent_types()
        assert "conversational" in templates
        assert "coding" in templates
        assert "research" in templates
        assert "multimodal" in templates
        assert "planner" in templates
        
        # 验证模板内容
        coding_template = factory_manager.get_agent_template("coding")
        assert coding_template["description"] == "代码生成和执行智能体"
        assert AgentCapability.CODE_GENERATION in coding_template["capabilities"]
        assert coding_template["default_model"]["provider"] == "openai"
        
        # 添加新模板
        factory_manager.add_agent_template(
            agent_type="custom",
            description="自定义智能体",
            capabilities=[AgentCapability.CONVERSATION],
            default_model={
                "provider": "anthropic",
                "model": "claude-2",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        
        # 验证新模板
        assert "custom" in factory_manager.list_agent_types()
        custom_template = factory_manager.get_agent_template("custom")
        assert custom_template["description"] == "自定义智能体"
        assert custom_template["default_model"]["provider"] == "anthropic"
    
    async def test_team_templates(self, factory_manager):
        """测试团队模板管理"""
        # 验证预定义模板
        templates = factory_manager.list_team_types()
        assert "development" in templates
        assert "research" in templates
        assert "creative" in templates
        
        # 验证模板内容
        dev_template = factory_manager.get_team_template("development")
        assert dev_template["description"] == "软件开发团队"
        assert dev_template["type"] == TeamType.COLLABORATIVE
        assert len(dev_template["default_agents"]) == 3
        
        # 添加新模板
        factory_manager.add_team_template(
            team_type="custom_team",
            description="自定义团队",
            team_config={
                "type": TeamType.SELECTOR,
                "communication_pattern": CommunicationPattern.PEER_TO_PEER,
                "default_agents": [
                    {
                        "type": "conversational",
                        "name": "Leader",
                        "description": "团队领导"
                    }
                ]
            }
        )
        
        # 验证新模板
        assert "custom_team" in factory_manager.list_team_types()
        custom_template = factory_manager.get_team_template("custom_team")
        assert custom_template["description"] == "自定义团队"
        assert custom_template["type"] == TeamType.SELECTOR
    
    async def test_create_conversational_agent(self, factory_manager):
        """测试创建对话智能体"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建对话智能体
        agent = await factory_manager.create_conversational_agent(
            name="test_assistant",
            personality="tutor",
            framework="autogen"
        )
        
        # 验证适配器调用
        mock_adapter.create_agent.assert_called_once()
        agent_config = mock_adapter.create_agent.call_args[0][0]
        
        assert agent_config.name == "test_assistant"
        assert agent_config.type == AgentType.CONVERSATIONAL
        assert "educational tutor" in agent_config.system_message.lower()
        assert AgentCapability.CONVERSATION in agent_config.capabilities
    
    async def test_create_coding_agent(self, factory_manager):
        """测试创建编码智能体"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建编码智能体
        agent = await factory_manager.create_coding_agent(
            name="code_expert",
            programming_languages=["python", "typescript"],
            framework="autogen"
        )
        
        # 验证适配器调用
        mock_adapter.create_agent.assert_called_once()
        agent_config = mock_adapter.create_agent.call_args[0][0]
        
        assert agent_config.name == "code_expert"
        assert agent_config.type == AgentType.CODING
        assert "python" in agent_config.system_message.lower()
        assert "typescript" in agent_config.system_message.lower()
        assert AgentCapability.CODE_GENERATION in agent_config.capabilities
        assert agent_config.model.temperature == 0.2  # 代码生成需要更确定性
    
    async def test_create_research_agent(self, factory_manager):
        """测试创建研究智能体"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建研究智能体
        agent = await factory_manager.create_research_agent(
            name="researcher",
            research_domains=["machine_learning", "nlp"],
            framework="autogen"
        )
        
        # 验证适配器调用
        mock_adapter.create_agent.assert_called_once()
        agent_config = mock_adapter.create_agent.call_args[0][0]
        
        assert agent_config.name == "researcher"
        assert agent_config.type == AgentType.RESEARCH
        assert "machine learning" in agent_config.system_message.lower()
        assert "nlp" in agent_config.system_message.lower()
        assert AgentCapability.WEB_SEARCH in agent_config.capabilities
        assert AgentCapability.REASONING in agent_config.capabilities
    
    async def test_create_multimodal_agent(self, factory_manager):
        """测试创建多模态智能体"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建多模态智能体
        agent = await factory_manager.create_multimodal_agent(
            name="vision_assistant",
            capabilities=["image", "video"],
            framework="autogen"
        )
        
        # 验证适配器调用
        mock_adapter.create_agent.assert_called_once()
        agent_config = mock_adapter.create_agent.call_args[0][0]
        
        assert agent_config.name == "vision_assistant"
        assert agent_config.type == AgentType.MULTIMODAL
        assert "image" in agent_config.system_message.lower()
        assert "video" in agent_config.system_message.lower()
        assert AgentCapability.MULTIMODAL in agent_config.capabilities
    
    async def test_create_development_team(self, factory_manager):
        """测试创建开发团队"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_team = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建开发团队
        team = await factory_manager.create_development_team(
            name="dev_team",
            backend_languages=["python", "go"],
            frontend_languages=["typescript", "react"],
            framework="autogen"
        )
        
        # 验证适配器调用
        mock_adapter.create_team.assert_called_once()
        team_config = mock_adapter.create_team.call_args[0][0]
        
        assert team_config.name == "dev_team"
        assert team_config.type == TeamType.COLLABORATIVE
        assert len(team_config.agents) == 3  # Backend, Frontend, TechLead
        
        # 验证团队成员配置
        backend_dev = next(a for a in team_config.agents if a["name"] == "BackendDev")
        frontend_dev = next(a for a in team_config.agents if a["name"] == "FrontendDev")
        tech_lead = next(a for a in team_config.agents if a["name"] == "TechLead")
        
        assert "python" in backend_dev["programming_languages"]
        assert "go" in backend_dev["programming_languages"]
        assert "typescript" in frontend_dev["programming_languages"]
        assert "react" in frontend_dev["programming_languages"]
        assert "architecture" in tech_lead["research_domains"]
    
    async def test_error_handling(self, factory_manager):
        """测试错误处理"""
        # 测试无效的Agent类型
        with pytest.raises(ValueError, match="Unknown agent type"):
            factory_manager.get_agent_template("invalid_type")
        
        # 测试无效的团队类型
        with pytest.raises(ValueError, match="Unknown team type"):
            factory_manager.get_team_template("invalid_team")
        
        # 测试适配器错误
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock(side_effect=Exception("Adapter error"))
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        with pytest.raises(Exception, match="Adapter error"):
            await factory_manager.create_conversational_agent(
                name="test",
                framework="autogen"
            )
    
    async def test_custom_agent_creation(self, factory_manager):
        """测试自定义Agent创建"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.create_agent = AsyncMock()
        factory_manager.adapter_registry.get_adapter.return_value = mock_adapter
        
        # 创建自定义配置
        custom_config = {
            "model": {
                "provider": "anthropic",
                "model": "claude-2",
                "temperature": 0.5
            },
            "tools": [
                {
                    "name": "custom_tool",
                    "type": "api",
                    "description": "Custom API tool"
                }
            ],
            "memory": {
                "enabled": True,
                "max_memories": 2000
            }
        }
        
        # 创建自定义Agent
        agent = await factory_manager.create_agent(
            agent_type="conversational",
            name="custom_agent",
            framework="autogen",
            config=custom_config
        )
        
        # 验证适配器调用
        mock_adapter.create_agent.assert_called_once()
        agent_config = mock_adapter.create_agent.call_args[0][0]
        
        assert agent_config.name == "custom_agent"
        assert agent_config.model.provider == "anthropic"
        assert agent_config.model.model == "claude-2"
        assert len(agent_config.tools) == 1
        assert agent_config.tools[0].name == "custom_tool"
        assert agent_config.memory.max_memories == 2000 