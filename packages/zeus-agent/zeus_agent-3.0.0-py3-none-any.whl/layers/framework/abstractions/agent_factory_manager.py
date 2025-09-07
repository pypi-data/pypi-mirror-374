"""
Agent Factory Manager - Agent工厂管理器
支持新的抽象层设计，提供简单易用的API
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import yaml
from datetime import datetime

from .cognitive_agent import (
    CognitiveUniversalAgent, AgentConfig, ModelConfig, ToolConfig, 
    MemoryConfig, BehaviorConfig, AgentType, ChatContext
)
from .team import (
    TeamConfig, TeamType, UniversalTeam, RoundRobinTeam, SelectorTeam, SwarmTeam,
    CommunicationPattern
)
from .agent import AgentCapability
from ...adapter.registry.adapter_registry import AdapterRegistry


class AgentFactoryManager:
    """
    Agent工厂管理器
    
    提供简单易用的API来创建各种类型的Agent和团队
    """
    
    def __init__(self):
        self.adapter_registry = AdapterRegistry()
        self.agent_templates = self._load_agent_templates()
        self.team_templates = self._load_team_templates()
    
    def _load_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载预定义的Agent模板"""
        return {
            "conversational": {
                "description": "通用对话智能体",
                "capabilities": [AgentCapability.CONVERSATION, AgentCapability.REASONING],
                "default_model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            "coding": {
                "description": "代码生成和执行智能体",
                "capabilities": [AgentCapability.CODE_GENERATION, AgentCapability.CODE_EXECUTION],
                "default_model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "default_tools": [
                    {
                        "name": "python_executor",
                        "type": "python_execution",
                        "description": "Python代码执行工具",
                        "config": {
                            "timeout": 30,
                            "work_dir": "./workspace"
                        }
                    }
                ]
            },
            "research": {
                "description": "研究和信息搜索智能体",
                "capabilities": [AgentCapability.WEB_SEARCH, AgentCapability.REASONING],
                "default_model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 1500
                },
                "default_tools": [
                    {
                        "name": "web_search",
                        "type": "http",
                        "description": "网络搜索工具",
                        "config": {
                            "base_url": "https://api.search.com"
                        }
                    },
                    {
                        "name": "document_reader",
                        "type": "file_reader",
                        "description": "文档阅读工具",
                        "config": {
                            "allowed_extensions": [".pdf", ".txt", ".docx"]
                        }
                    }
                ]
            },
            "multimodal": {
                "description": "多模态内容处理智能体",
                "capabilities": [AgentCapability.MULTIMODAL, AgentCapability.CONVERSATION],
                "default_model": {
                    "provider": "openai",
                    "model": "gpt-4-vision-preview",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            "planner": {
                "description": "任务规划和项目管理智能体",
                "capabilities": [AgentCapability.PLANNING, AgentCapability.REASONING],
                "default_model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 1200
                }
            }
        }
    
    def _load_team_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载预定义的团队模板"""
        return {
            "development": {
                "description": "软件开发团队",
                "type": TeamType.COLLABORATIVE,
                "communication_pattern": CommunicationPattern.HIERARCHICAL,
                "default_agents": [
                    {
                        "type": "coding",
                        "name": "BackendDev",
                        "description": "后端开发专家",
                        "languages": ["python", "java", "go"]
                    },
                    {
                        "type": "coding",
                        "name": "FrontendDev",
                        "description": "前端开发专家",
                        "languages": ["javascript", "typescript", "react"]
                    },
                    {
                        "type": "research",
                        "name": "TechLead",
                        "description": "技术架构师",
                        "domains": ["architecture", "best_practices", "security"]
                    }
                ]
            },
            "research": {
                "description": "研究分析团队",
                "type": TeamType.SELECTOR,
                "communication_pattern": CommunicationPattern.PEER_TO_PEER,
                "default_agents": [
                    {
                        "type": "research",
                        "name": "DataAnalyst",
                        "description": "数据分析师",
                        "domains": ["statistics", "machine_learning"]
                    },
                    {
                        "type": "research",
                        "name": "DomainExpert",
                        "description": "领域专家",
                        "domains": ["business", "industry"]
                    },
                    {
                        "type": "planner",
                        "name": "ResearchCoordinator",
                        "description": "研究协调员",
                        "domains": ["project_management", "methodology"]
                    }
                ]
            },
            "creative": {
                "description": "创意内容团队",
                "type": TeamType.SWARM,
                "communication_pattern": CommunicationPattern.BROADCAST,
                "default_agents": [
                    {
                        "type": "conversational",
                        "name": "ContentWriter",
                        "description": "内容创作者",
                        "personality": "creative"
                    },
                    {
                        "type": "multimodal",
                        "name": "VisualDesigner",
                        "description": "视觉设计师",
                        "capabilities": ["image_generation", "design"]
                    },
                    {
                        "type": "research",
                        "name": "TrendAnalyst",
                        "description": "趋势分析师",
                        "domains": ["marketing", "social_media"]
                    }
                ]
            }
        }
    
    async def create_agent(self, 
                          agent_type: str,
                          name: str,
                          framework: str = "autogen",
                          config: Optional[Dict[str, Any]] = None,
                          **kwargs) -> CognitiveUniversalAgent:
        """
        创建Agent的简单方法
        
        Args:
            agent_type: Agent类型 (conversational, coding, research, multimodal, planner)
            name: Agent名称
            framework: 使用的框架 (autogen, openai, langraph)
            config: 自定义配置
            **kwargs: 其他参数
            
        Returns:
            EnhancedUniversalAgent: 创建的Agent实例
        """
        # 获取模板配置
        if agent_type not in self.agent_templates:
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(self.agent_templates.keys())}")
        
        template = self.agent_templates[agent_type]
        
        # 合并配置
        final_config = template.copy()
        if config:
            final_config.update(config)
        
        # 创建Agent配置
        agent_config = self._create_agent_config(name, agent_type, final_config, framework, **kwargs)
        
        # 创建Agent
        adapter = await self.adapter_registry.get_adapter(framework)
        agent = await adapter.create_agent(agent_config)
        
        return agent
    
    async def create_conversational_agent(self, name: str, personality: str = "assistant",
                                          framework: str = "autogen",
                                          **config) -> CognitiveUniversalAgent:
        """
        快速创建对话智能体
        
        Args:
            name: Agent名称
            personality: 性格类型 (assistant, tutor, creative, analyst, friend)
            framework: 使用的框架
            **config: 其他配置
        """
        template = self.get_agent_template("conversational")
        agent_config = self._create_agent_config(
            name=name,
            agent_type="conversational",
            template=template,
            framework=framework,
            personality=personality,
            **config
        )
        
        adapter = await self.adapter_registry.get_adapter(framework)
        return await adapter.create_agent(agent_config)
    
    async def create_coding_agent(self, name: str,
                                   programming_languages: List[str] = None,
                                   framework: str = "autogen",
                                   **config) -> CognitiveUniversalAgent:
        """
        快速创建编码智能体
        
        Args:
            name: Agent名称
            programming_languages: 编程语言列表
            framework: 使用的框架
            **config: 其他配置
        """
        template = self.get_agent_template("coding")
        agent_config = self._create_agent_config(
            name=name,
            agent_type="coding",
            template=template,
            framework=framework,
            programming_languages=programming_languages or ["python"],
            **config
        )
        
        adapter = await self.adapter_registry.get_adapter(framework)
        return await adapter.create_agent(agent_config)
    
    async def create_research_agent(self, name: str,
                                     research_domains: List[str] = None,
                                     framework: str = "autogen",
                                     **config) -> CognitiveUniversalAgent:
        """
        快速创建研究智能体
        
        Args:
            name: Agent名称
            research_domains: 研究领域列表
            framework: 使用的框架
            **config: 其他配置
        """
        template = self.get_agent_template("research")
        agent_config = self._create_agent_config(
            name=name,
            agent_type="research",
            template=template,
            framework=framework,
            research_domains=research_domains or ["general"],
            **config
        )
        
        adapter = await self.adapter_registry.get_adapter(framework)
        return await adapter.create_agent(agent_config)
    
    async def create_multimodal_agent(self, name: str,
                                       capabilities: List[str] = None,
                                       framework: str = "autogen",
                                       **config) -> CognitiveUniversalAgent:
        """
        快速创建多模态智能体
        
        Args:
            name: Agent名称
            capabilities: 多模态能力列表 (image, video, audio, text)
            framework: 使用的框架
            **config: 其他配置
        """
        template = self.get_agent_template("multimodal")
        agent_config = self._create_agent_config(
            name=name,
            agent_type="multimodal",
            template=template,
            framework=framework,
            capabilities=capabilities or ["image", "text"],
            **config
        )
        
        adapter = await self.adapter_registry.get_adapter(framework)
        return await adapter.create_agent(agent_config)
    
    async def create_team(self, 
                         team_type: str,
                         name: str,
                         agent_configs: List[Dict[str, Any]],
                         framework: str = "autogen",
                         **config) -> UniversalTeam:
        """
        创建智能体团队
        
        Args:
            team_type: 团队类型 (development, research, creative, custom)
            name: 团队名称
            agent_configs: Agent配置列表
            framework: 使用的框架
            **config: 其他配置参数
            
        Returns:
            UniversalTeam: 智能体团队实例
        """
        # 获取团队模板
        if team_type in self.team_templates:
            template = self.team_templates[team_type]
            team_config = template.copy()
            team_config.update(config)
        else:
            # 自定义团队
            team_config = {
                "type": TeamType.COLLABORATIVE,
                "communication_pattern": CommunicationPattern.ROUND_ROBIN,
                **config
            }
        
        # 创建团队配置
        team_config_obj = TeamConfig(
            name=name,
            type=team_config.get("type", TeamType.COLLABORATIVE),
            agents=agent_configs,
            communication_pattern=team_config.get("communication_pattern", CommunicationPattern.ROUND_ROBIN),
            max_rounds=team_config.get("max_rounds", 10),
            timeout=team_config.get("timeout", 300)
        )
        
        # 创建团队
        adapter = await self.adapter_registry.get_adapter(framework)
        team = await adapter.create_team(team_config_obj)
        
        # 初始化团队中的Agent
        await team.initialize_agents(self)
        
        return team
    
    async def create_development_team(self, 
                                    name: str,
                                    backend_languages: List[str] = None,
                                    frontend_languages: List[str] = None,
                                    framework: str = "autogen",
                                    **config) -> UniversalTeam:
        """
        快速创建开发团队
        
        Args:
            name: 团队名称
            backend_languages: 后端编程语言
            frontend_languages: 前端编程语言
            framework: 使用的框架
            **config: 其他配置参数
            
        Returns:
            UniversalTeam: 开发团队实例
        """
        if backend_languages is None:
            backend_languages = ["python", "java"]
        if frontend_languages is None:
            frontend_languages = ["javascript", "typescript"]
        
        agent_configs = [
            {
                "type": "coding",
                "name": "BackendDev",
                "description": "后端开发专家",
                "programming_languages": backend_languages
            },
            {
                "type": "coding",
                "name": "FrontendDev",
                "description": "前端开发专家",
                "programming_languages": frontend_languages
            },
            {
                "type": "research",
                "name": "TechLead",
                "description": "技术架构师",
                "research_domains": ["architecture", "best_practices", "security"]
            }
        ]
        
        return await self.create_team("development", name, agent_configs, framework, **config)
    
    def _create_agent_config(self, name: str, agent_type: str, template: Dict[str, Any], 
                           framework: str, **kwargs) -> AgentConfig:
        """创建Agent配置对象"""
        # 获取基础配置
        base_config = template.copy()
        
        # 合并自定义配置
        if kwargs.get("config"):
            for key, value in kwargs["config"].items():
                if key in base_config:
                    if isinstance(base_config[key], dict):
                        base_config[key].update(value)
                    else:
                        base_config[key] = value
                else:
                    base_config[key] = value
        
        # 创建模型配置
        model_config = ModelConfig(
            provider=base_config.get("model", {}).get("provider", template["default_model"]["provider"]),
            model=base_config.get("model", {}).get("model", template["default_model"]["model"]),
            temperature=base_config.get("model", {}).get("temperature", template["default_model"]["temperature"]),
            max_tokens=base_config.get("model", {}).get("max_tokens", template["default_model"]["max_tokens"]),
            api_key=base_config.get("model", {}).get("api_key"),
            base_url=base_config.get("model", {}).get("base_url"),
            api_version=base_config.get("model", {}).get("api_version")
        )
        
        # 创建工具配置
        tools_config = []
        for tool_data in base_config.get("tools", template.get("default_tools", [])):
            tool_config = ToolConfig(
                name=tool_data["name"],
                type=tool_data["type"],
                description=tool_data.get("description", ""),
                enabled=tool_data.get("enabled", True),
                config=tool_data.get("config", {})
            )
            tools_config.append(tool_config)
        
        # 创建记忆配置
        memory_config = MemoryConfig(
            enabled=base_config.get("memory", {}).get("enabled", True),
            max_memories=base_config.get("memory", {}).get("max_memories", 1000),
            memory_type=base_config.get("memory", {}).get("memory_type", "conversation")
        )
        
        # 创建行为配置
        behavior_config = BehaviorConfig(
            max_consecutive_auto_reply=base_config.get("behavior", {}).get("max_consecutive_auto_reply", 3),
            human_input_mode=base_config.get("behavior", {}).get("human_input_mode", "NEVER"),
            code_execution_config=base_config.get("behavior", {}).get("code_execution_config", {})
        )
        
        # 生成系统提示
        system_message = self._generate_system_message(agent_type, base_config, **kwargs)
        
        # 处理capabilities
        if agent_type == "multimodal":
            capabilities = [AgentCapability.MULTIMODAL]
        else:
            capabilities = template["capabilities"]
        
        # 创建Agent配置
        agent_config = AgentConfig(
            name=name,
            type=AgentType(agent_type),
            model=model_config,
            capabilities=capabilities,
            tools=tools_config,
            memory=memory_config,
            behavior=behavior_config,
            system_message=system_message,
            description=template["description"]
        )
        
        return agent_config
    
    def _format_domain_name(self, domain: str) -> str:
        """格式化领域名称"""
        return domain.replace("_", " ").lower()
    
    def _generate_system_message(self, agent_type: str, config: Dict[str, Any], **kwargs) -> str:
        """生成系统提示"""
        if agent_type == "conversational":
            personality = kwargs.get("personality", "assistant")
            personality_prompts = {
                "assistant": "You are a helpful and professional AI assistant.",
                "tutor": "You are a patient and encouraging educational tutor, focused on helping students learn and grow.",
                "creative": "You are an imaginative and inspiring creative companion.",
                "analyst": "You are a thorough and analytical AI assistant.",
                "friend": "You are a friendly and supportive AI companion."
            }
            return personality_prompts.get(personality, personality_prompts["assistant"])
            
        elif agent_type == "coding":
            languages = kwargs.get("programming_languages", ["python"])
            return f"""You are an expert programming assistant specializing in {', '.join(languages)}.
You can generate code, debug issues, explain concepts, and help with software development tasks.
Always provide clear, well-documented, and production-ready code."""
            
        elif agent_type == "research":
            domains = [self._format_domain_name(d) for d in kwargs.get("research_domains", ["general"])]
            return f"""You are a research assistant specializing in {', '.join(domains)}.
You can help with literature review, data analysis, hypothesis formation, and research methodology.
Always provide well-sourced, accurate, and comprehensive information."""
            
        elif agent_type == "multimodal":
            capabilities = kwargs.get("capabilities", ["image", "text"])
            return f"""You are a multimodal AI assistant capable of processing {', '.join(capabilities)}.
You can analyze images, videos, audio, and text to provide comprehensive insights and responses."""
            
        elif agent_type == "planner":
            return """You are a task planning and project management assistant.
You can help with task breakdown, scheduling, resource allocation, and progress tracking.
Always provide clear, actionable, and well-organized plans."""
            
        else:
            return config.get("system_message", "")
    
    def list_agent_types(self) -> List[str]:
        """获取所有可用的Agent类型"""
        return list(self.agent_templates.keys())
    
    def list_team_types(self) -> List[str]:
        """获取所有可用的团队类型"""
        return list(self.team_templates.keys())
    
    def get_agent_template(self, agent_type: str) -> Dict[str, Any]:
        """获取Agent模板信息"""
        if agent_type not in self.agent_templates:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return self.agent_templates[agent_type].copy()
    
    def get_team_template(self, team_type: str) -> Dict[str, Any]:
        """获取团队模板信息"""
        if team_type not in self.team_templates:
            raise ValueError(f"Unknown team type: {team_type}")
        return self.team_templates[team_type].copy()
    
    def add_agent_template(self, 
                          agent_type: str, 
                          description: str,
                          capabilities: List[AgentCapability],
                          default_model: Dict[str, Any],
                          default_tools: List[Dict[str, Any]] = None) -> None:
        """添加新的Agent模板"""
        self.agent_templates[agent_type] = {
            "description": description,
            "capabilities": capabilities,
            "default_model": default_model,
            "default_tools": default_tools or []
        }
    
    def add_team_template(self,
                         team_type: str,
                         description: str,
                         team_config: Dict[str, Any]) -> None:
        """添加新的团队模板"""
        self.team_templates[team_type] = {
            "description": description,
            **team_config
        }


# 全局工厂实例
enhanced_agent_factory = AgentFactoryManager() 