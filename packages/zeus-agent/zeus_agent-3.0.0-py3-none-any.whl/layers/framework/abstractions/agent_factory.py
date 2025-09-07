"""
Agent Factory - 强大的Agent创建工厂
让开发者能够简单快速地创建各种类型的Agent
"""

import asyncio
from typing import Dict, Any, List, Optional, Union, Type
from pathlib import Path
import yaml
from datetime import datetime

from .agent import UniversalAgent, AgentCapability, AgentStatus
from .task import UniversalTask, TaskType
from .context import UniversalContext
from .result import UniversalResult
from ...adapter.registry.adapter_registry import AdapterRegistry


class AgentFactory:
    """
    强大的Agent创建工厂
    
    提供简单易用的API来创建各种类型的Agent
    """
    
    def __init__(self):
        self.adapter_registry = AdapterRegistry()
        self.agent_templates = self._load_agent_templates()
    
    def _load_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载预定义的Agent模板"""
        return {
            "chatbot": {
                "description": "通用聊天机器人",
                "capabilities": [AgentCapability.CONVERSATION, AgentCapability.REASONING],
                "default_config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            "coder": {
                "description": "代码生成和编程助手",
                "capabilities": [AgentCapability.CODE_GENERATION, AgentCapability.CODE_EXECUTION],
                "default_config": {
                    "model": "gpt-4",
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            },
            "researcher": {
                "description": "研究和信息搜索助手",
                "capabilities": [AgentCapability.WEB_SEARCH, AgentCapability.REASONING],
                "default_config": {
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 1500
                }
            },
            "planner": {
                "description": "任务规划和项目管理助手",
                "capabilities": [AgentCapability.PLANNING, AgentCapability.REASONING],
                "default_config": {
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 1200
                }
            },
            "multimodal": {
                "description": "多模态内容处理助手",
                "capabilities": [AgentCapability.MULTIMODAL, AgentCapability.CONVERSATION],
                "default_config": {
                    "model": "gpt-4-vision-preview",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
        }
    
    async def create_agent(self, 
                          agent_type: str,
                          name: str,
                          framework: str = "autogen",
                          config: Optional[Dict[str, Any]] = None,
                          **kwargs) -> UniversalAgent:
        """
        创建Agent的简单方法
        
        Args:
            agent_type: Agent类型 (chatbot, coder, researcher, planner, multimodal)
            name: Agent名称
            framework: 使用的框架 (autogen, openai, langraph)
            config: 自定义配置
            **kwargs: 其他参数
            
        Returns:
            UniversalAgent: 创建的Agent实例
            
        Example:
            # 创建一个聊天机器人
            chatbot = await factory.create_agent("chatbot", "MyAssistant")
            
            # 创建一个代码助手
            coder = await factory.create_agent("coder", "CodeHelper", framework="openai")
        """
        # 获取模板配置
        if agent_type not in self.agent_templates:
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(self.agent_templates.keys())}")
        
        template = self.agent_templates[agent_type]
        
        # 合并配置
        final_config = template["default_config"].copy()
        if config:
            final_config.update(config)
        
        # 添加框架配置
        framework_config = {
            "agent_type": agent_type,
            "name": name,
            "description": template["description"],
            "capabilities": [cap.value for cap in template["capabilities"]],
            "framework": framework,
            framework: final_config
        }
        
        # 创建Agent
        agent = await self._create_agent_from_config(framework_config)
        
        # 应用额外参数
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        return agent
    
    async def create_chatbot(self, 
                           name: str,
                           personality: str = "assistant",
                           framework: str = "autogen",
                           **config) -> UniversalAgent:
        """
        快速创建聊天机器人
        
        Args:
            name: 机器人名称
            personality: 个性类型 (assistant, tutor, creative)
            framework: 使用的框架
            **config: 其他配置参数
            
        Returns:
            UniversalAgent: 聊天机器人实例
            
        Example:
            # 创建一个助手风格的聊天机器人
            assistant = await factory.create_chatbot("Alice", personality="assistant")
            
            # 创建一个导师风格的聊天机器人
            tutor = await factory.create_chatbot("Teacher", personality="tutor", framework="openai")
        """
        # 根据个性设置不同的系统提示
        personality_prompts = {
            "assistant": "You are a helpful and professional AI assistant.",
            "tutor": "You are a patient and encouraging educational tutor.",
            "creative": "You are an imaginative and inspiring creative companion."
        }
        
        system_prompt = personality_prompts.get(personality, personality_prompts["assistant"])
        
        # 创建配置
        chatbot_config = {
            "system_prompt": system_prompt,
            "personality": personality,
            **config
        }
        
        return await self.create_agent("chatbot", name, framework, chatbot_config)
    
    async def create_coder(self, 
                          name: str,
                          programming_languages: List[str] = None,
                          framework: str = "autogen",
                          **config) -> UniversalAgent:
        """
        快速创建代码助手
        
        Args:
            name: 助手名称
            programming_languages: 支持的编程语言列表
            framework: 使用的框架
            **config: 其他配置参数
            
        Returns:
            UniversalAgent: 代码助手实例
            
        Example:
            # 创建一个Python代码助手
            python_coder = await factory.create_coder("PythonHelper", ["python"])
            
            # 创建一个全栈开发助手
            fullstack_coder = await factory.create_coder("FullStackDev", 
                                                       ["python", "javascript", "typescript"])
        """
        if programming_languages is None:
            programming_languages = ["python"]
        
        system_prompt = f"""You are an expert programming assistant specializing in {', '.join(programming_languages)}.
        You can generate code, debug issues, explain concepts, and help with software development tasks.
        Always provide clear, well-documented, and production-ready code."""
        
        coder_config = {
            "system_prompt": system_prompt,
            "programming_languages": programming_languages,
            "temperature": 0.2,  # 代码生成需要更确定性
            **config
        }
        
        return await self.create_agent("coder", name, framework, coder_config)
    
    async def create_researcher(self, 
                               name: str,
                               research_domains: List[str] = None,
                               framework: str = "autogen",
                               **config) -> UniversalAgent:
        """
        快速创建研究助手
        
        Args:
            name: 助手名称
            research_domains: 研究领域列表
            framework: 使用的框架
            **config: 其他配置参数
            
        Returns:
            UniversalAgent: 研究助手实例
        """
        if research_domains is None:
            research_domains = ["general"]
        
        system_prompt = f"""You are a research assistant specializing in {', '.join(research_domains)}.
        You can help with literature review, data analysis, hypothesis formation, and research methodology.
        Always provide well-sourced, accurate, and comprehensive information."""
        
        researcher_config = {
            "system_prompt": system_prompt,
            "research_domains": research_domains,
            **config
        }
        
        return await self.create_agent("researcher", name, framework, researcher_config)
    
    async def create_team(self, 
                         agents: List[Dict[str, Any]],
                         team_name: str = "AgentTeam") -> 'AgentTeam':
        """
        创建Agent团队
        
        Args:
            agents: Agent配置列表
            team_name: 团队名称
            
        Returns:
            AgentTeam: Agent团队实例
            
        Example:
            # 创建一个开发团队
            team = await factory.create_team([
                {"type": "coder", "name": "BackendDev", "languages": ["python", "java"]},
                {"type": "coder", "name": "FrontendDev", "languages": ["javascript", "react"]},
                {"type": "researcher", "name": "TechLead", "domains": ["architecture", "best_practices"]}
            ], "DevelopmentTeam")
        """
        team_agents = []
        
        for agent_config in agents:
            agent_type = agent_config["type"]
            agent_name = agent_config["name"]
            
            # 根据类型创建Agent
            if agent_type == "chatbot":
                agent = await self.create_chatbot(agent_name, **agent_config)
            elif agent_type == "coder":
                agent = await self.create_coder(agent_name, **agent_config)
            elif agent_type == "researcher":
                agent = await self.create_researcher(agent_name, **agent_config)
            else:
                agent = await self.create_agent(agent_type, agent_name, **agent_config)
            
            team_agents.append(agent)
        
        return AgentTeam(team_name, team_agents)
    
    async def _create_agent_from_config(self, config: Dict[str, Any]) -> UniversalAgent:
        """从配置创建Agent的内部方法"""
        framework = config.get("framework", "autogen")
        
        # 初始化Adapter
        adapter = await self.adapter_registry.initialize_adapter(framework, config)
        
        # 创建Agent
        agent = await adapter.create_agent(config)
        
        return agent
    
    def list_agent_types(self) -> List[str]:
        """获取所有可用的Agent类型"""
        return list(self.agent_templates.keys())
    
    def get_agent_template(self, agent_type: str) -> Dict[str, Any]:
        """获取Agent模板信息"""
        if agent_type not in self.agent_templates:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return self.agent_templates[agent_type].copy()
    
    def add_agent_template(self, 
                          agent_type: str, 
                          description: str,
                          capabilities: List[AgentCapability],
                          default_config: Dict[str, Any]) -> None:
        """添加新的Agent模板"""
        self.agent_templates[agent_type] = {
            "description": description,
            "capabilities": capabilities,
            "default_config": default_config
        }


class AgentTeam:
    """
    Agent团队类
    管理多个Agent的协作
    """
    
    def __init__(self, name: str, agents: List[UniversalAgent]):
        self.name = name
        self.agents = agents
        self.conversation_history = []
    
    async def execute_task(self, task: str, agent_selector: str = "auto") -> UniversalResult:
        """
        执行任务，自动选择合适的Agent
        
        Args:
            task: 任务描述
            agent_selector: Agent选择策略 ("auto", "round_robin", "capability")
            
        Returns:
            UniversalResult: 执行结果
        """
        # 选择Agent
        if agent_selector == "auto":
            agent = self._select_best_agent(task)
        elif agent_selector == "round_robin":
            agent = self._select_round_robin()
        else:
            agent = self.agents[0]  # 默认选择第一个
        
        # 创建任务
        universal_task = UniversalTask(
            content=task,
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = UniversalContext({
            "team_name": self.name,
            "selected_agent": agent.name,
            "available_agents": [a.name for a in self.agents]
        })
        
        # 执行任务
        result = await agent.execute(universal_task, context)
        
        # 记录历史
        self.conversation_history.append({
            "task": task,
            "agent": agent.name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _select_best_agent(self, task: str) -> UniversalAgent:
        """根据任务内容选择最合适的Agent"""
        # 简单的关键词匹配
        task_lower = task.lower()
        
        for agent in self.agents:
            if "code" in task_lower and AgentCapability.CODE_GENERATION in agent.capabilities:
                return agent
            if "research" in task_lower and AgentCapability.WEB_SEARCH in agent.capabilities:
                return agent
            if "plan" in task_lower and AgentCapability.PLANNING in agent.capabilities:
                return agent
        
        # 默认返回第一个Agent
        return self.agents[0]
    
    def _select_round_robin(self) -> UniversalAgent:
        """轮询选择Agent"""
        # 简单的轮询实现
        if not hasattr(self, '_current_agent_index'):
            self._current_agent_index = 0
        
        agent = self.agents[self._current_agent_index]
        self._current_agent_index = (self._current_agent_index + 1) % len(self.agents)
        
        return agent
    
    def get_team_status(self) -> Dict[str, Any]:
        """获取团队状态"""
        return {
            "name": self.name,
            "agent_count": len(self.agents),
            "agents": [agent.name for agent in self.agents],
            "conversation_count": len(self.conversation_history),
            "last_activity": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }


# 全局工厂实例
agent_factory = AgentFactory() 