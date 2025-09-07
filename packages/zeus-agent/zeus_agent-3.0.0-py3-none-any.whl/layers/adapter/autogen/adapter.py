"""
AutoGen Adapter v0.4 - New AutoGen AgentChat API Adapter
Adapts to the new AutoGen 0.7.4+ API structure with autogen-agentchat
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
import uuid

# New AutoGen v0.4 imports
try:
    import autogen_agentchat
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, CodeExecutorAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.messages import TextMessage, MultiModalMessage
    from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
    from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
    from autogen_core import CancellationToken
    from .llm_backend import create_llm_backend, LLMBackend
    AUTOGEN_V04_AVAILABLE = True
except ImportError as e:
    AUTOGEN_V04_AVAILABLE = False
    logging.warning(f"AutoGen v0.4 (autogen-agentchat) not available: {e}")

# ADC framework imports
from ...framework.abstractions.agent import UniversalAgent, AgentCapability
from ...framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult, ResultStatus, ResultType, ResultMetadata
from ..base import BaseAdapter, AdapterCapability, AdapterError, AdapterInitializationError, AdapterExecutionError, AdapterStatus

logger = logging.getLogger(__name__)


class AutoGenV04Adapter(BaseAdapter):
    """AutoGen v0.4 (AgentChat) Adapter for ADC Framework"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize AutoGen v0.4 adapter"""
        if not AUTOGEN_V04_AVAILABLE:
            raise AdapterInitializationError("AutoGen v0.4 (autogen-agentchat) not available")
        
        super().__init__(name)
        self.config = config or {}
        
        # Agent storage
        self.agents: Dict[str, AssistantAgent] = {}
        self.code_executors: Dict[str, CodeExecutorAgent] = {}
        self.user_proxies: Dict[str, UserProxyAgent] = {}
        self.teams: Dict[str, RoundRobinGroupChat] = {}
        
        # LLM backend storage
        self.llm_backends: Dict[str, LLMBackend] = {}
        
        # Default configurations
        self.default_backend_type = self.config.get("backend_type", "openai")
        self.default_model = self.config.get("default_model", "gpt-3.5-turbo")
        self.default_temperature = self.config.get("default_temperature", 0.7)
        self.work_dir = self.config.get("work_dir", "temp")
        
        logger.info(f"Initialized AutoGen v0.4 adapter: {name}")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize adapter with configuration"""
        try:
            self.config.update(config)
            self.status = AdapterStatus.INITIALIZING
            
            # Update default configurations
            self.default_model = config.get("model", self.default_model)
            self.default_temperature = config.get("temperature", self.default_temperature)
            self.work_dir = config.get("work_dir", self.work_dir)
            
            # 创建默认的LLM后端
            await self._create_default_llm_backend(config)
            
            # 创建默认的assistant agent
            await self._create_default_agent(config)
            
            self.status = AdapterStatus.READY
            self.is_initialized = True
            self.metadata.last_initialized = datetime.now()
            self.metadata.initialization_count += 1
            
            logger.info(f"AutoGen v0.4 adapter '{self.name}' initialized successfully")
            
        except Exception as e:
            self.status = AdapterStatus.ERROR
            logger.error(f"Failed to initialize adapter '{self.name}': {e}")
            raise AdapterInitializationError(f"Initialization failed: {str(e)}")
    
    async def _create_default_llm_backend(self, config: Dict[str, Any]) -> None:
        """创建默认的LLM后端"""
        try:
            llm_backend = config.get('llm_backend', 'deepseek')
            api_key = config.get('api_key')
            model = config.get('model', 'deepseek-chat')
            base_url = config.get('base_url', 'https://api.deepseek.com/v1')
            temperature = config.get('temperature', 0.1)
            max_tokens = config.get('max_tokens', 200)
            
            if not api_key:
                raise AdapterInitializationError("API key is required")
            
            # 创建LLM后端
            backend = create_llm_backend(
                backend_type=llm_backend,
                api_key=api_key,
                model=model,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            backend_id = f"{self.name}_default_backend"
            self.llm_backends[backend_id] = backend
            
            logger.info(f"Created default LLM backend: {backend_id} ({llm_backend})")
            
        except Exception as e:
            logger.error(f"Failed to create default LLM backend: {e}")
            raise
    
    async def _create_default_agent(self, config: Dict[str, Any]) -> None:
        """创建默认的assistant agent"""
        try:
            backend_id = f"{self.name}_default_backend"
            agent_id = f"{self.name}_default_agent"
            
            # 确保后端存在
            if backend_id not in self.llm_backends:
                raise AdapterInitializationError("Default LLM backend not found")
            
            # 创建默认agent
            system_message = "You are Ares, a professional FPGA design expert. You are skilled in Verilog/SystemVerilog, timing analysis, synthesis optimization, and verification."
            
            self.create_assistant_agent(
                agent_id=agent_id,
                name="Ares",
                system_message=system_message,
                backend_id=backend_id
            )
            
            logger.info(f"Created default assistant agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to create default agent: {e}")
            raise
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> Any:
        """Create agent with configuration"""
        agent_type = agent_config.get("type", "assistant")
        
        if agent_type == "assistant":
            return self.create_assistant_agent(
                agent_id=agent_config["agent_id"],
                name=agent_config["name"],
                system_message=agent_config.get("system_message", "You are a helpful assistant."),
                backend_id=agent_config["backend_id"],
                tools=agent_config.get("tools", [])
            )
        elif agent_type == "code_executor":
            return self.create_code_executor_agent(
                agent_id=agent_config["agent_id"],
                name=agent_config["name"],
                work_dir=agent_config.get("work_dir")
            )
        elif agent_type == "user_proxy":
            return self.create_user_proxy_agent(
                agent_id=agent_config["agent_id"],
                name=agent_config["name"]
            )
        else:
            raise AdapterExecutionError(f"Unsupported agent type: {agent_type}")
    
    async def create_team(self, team_config: Dict[str, Any]) -> Any:
        """Create team with configuration"""
        return self._create_team_internal(
            team_id=team_config["team_id"],
            agent_ids=team_config["agent_ids"],
            max_turns=team_config.get("max_turns", 10),
            termination_keywords=team_config.get("termination_keywords", [])
        )
    
    def get_capabilities(self) -> List['AdapterCapability']:
        """Get adapter capabilities"""
        from ..base import AdapterCapability
        return [
            AdapterCapability.CONVERSATION,
            AdapterCapability.CODE_GENERATION,
            AdapterCapability.CODE_EXECUTION,
            AdapterCapability.TOOL_CALLING,
            AdapterCapability.TEAM_COLLABORATION
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "adapter_name": self.name,
                "status": self.status.value,
                "initialized": self.is_initialized,
                "autogen_available": AUTOGEN_V04_AVAILABLE,
                "agents_count": len(self.agents),
                "teams_count": len(self.teams),
                "model_clients_count": len(self.llm_backends),
                "timestamp": datetime.now().isoformat(),
                "healthy": True
            }
            
            # Check if we can import required modules
            if not AUTOGEN_V04_AVAILABLE:
                health_status["healthy"] = False
                health_status["error"] = "AutoGen v0.4 not available"
            
            return health_status
            
        except Exception as e:
            return {
                "adapter_name": self.name,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_info(self):
        """Get adapter information"""
        from dataclasses import dataclass
        
        @dataclass
        class AdapterInfo:
            name: str
            version: str
            description: str
            capabilities: List[str]
            supported_models: List[str]
        
        return AdapterInfo(
            name=self.name,
            version="0.4.0",
            description="AutoGen v0.4 AgentChat API Adapter - Modern async multi-agent framework",
            capabilities=[
                "conversation",
                "code_generation", 
                "tool_use",
                "multi_agent_collaboration",
                "async_execution"
            ],
            supported_models=[
                "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"
            ]
        )
    
    def create_llm_backend(self, backend_id: str, backend_type: str, api_key: str = None,
                          model: str = None, **kwargs) -> str:
        """Create LLM backend"""
        try:
            # Create backend
            # Prepare backend config
            backend_config = {
                "api_key": api_key,
                "model": model or self.default_model,
                "temperature": kwargs.get("temperature", self.default_temperature)
            }
            backend_config.update(kwargs)
            
            # Create backend
            backend = create_llm_backend(
                backend_type=backend_type,
                **backend_config
            )
            
            self.llm_backends[backend_id] = backend
            logger.info(f"Created LLM backend: {backend_id} of type {backend_type}")
            return backend_id
            
        except Exception as e:
            logger.error(f"Error creating LLM backend {backend_id}: {e}")
            raise AdapterError(f"Failed to create LLM backend: {str(e)}")
    
    def create_assistant_agent(self, agent_id: str, name: str, 
                             system_message: str, backend_id: str,
                             tools: Optional[List[Callable]] = None) -> str:
        """Create AssistantAgent with new v0.4 API"""
        try:
            if backend_id not in self.llm_backends:
                raise AdapterError(f"LLM backend {backend_id} not found")
            
            llm_backend = self.llm_backends[backend_id]
            
            # Create assistant agent
            agent = AssistantAgent(
                name=name,
                system_message=system_message,
                model_client=llm_backend,
                tools=tools or []
            )
            
            self.agents[agent_id] = agent
            logger.info(f"Created AssistantAgent: {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Error creating AssistantAgent {agent_id}: {e}")
            raise AdapterError(f"Failed to create AssistantAgent: {str(e)}")
    
    def create_code_executor_agent(self, agent_id: str, name: str, 
                                 work_dir: Optional[str] = None) -> str:
        """Create CodeExecutorAgent"""
        try:
            executor_work_dir = work_dir or self.work_dir
            
            # Create code executor
            code_executor = LocalCommandLineCodeExecutor(work_dir=executor_work_dir)
            
            # Create code executor agent
            agent = CodeExecutorAgent(
                name=name,
                code_executor=code_executor
            )
            
            self.code_executors[agent_id] = agent
            logger.info(f"Created CodeExecutorAgent: {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Error creating CodeExecutorAgent {agent_id}: {e}")
            raise AdapterError(f"Failed to create CodeExecutorAgent: {str(e)}")
    
    def create_user_proxy_agent(self, agent_id: str, name: str) -> str:
        """Create UserProxyAgent"""
        try:
            agent = UserProxyAgent(name=name)
            self.user_proxies[agent_id] = agent
            logger.info(f"Created UserProxyAgent: {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Error creating UserProxyAgent {agent_id}: {e}")
            raise AdapterError(f"Failed to create UserProxyAgent: {str(e)}")
    
    def _create_team_internal(self, team_id: str, agent_ids: List[str], 
                   max_turns: int = 10, termination_keywords: List[str] = None) -> str:
        """Create RoundRobinGroupChat team"""
        try:
            # Collect agents
            team_agents = []
            
            for agent_id in agent_ids:
                if agent_id in self.agents:
                    team_agents.append(self.agents[agent_id])
                elif agent_id in self.code_executors:
                    team_agents.append(self.code_executors[agent_id])
                elif agent_id in self.user_proxies:
                    team_agents.append(self.user_proxies[agent_id])
                else:
                    raise AdapterError(f"Agent {agent_id} not found")
            
            if not team_agents:
                raise AdapterError("No agents provided for team")
            
            # Create termination conditions
            termination_conditions = [MaxMessageTermination(max_turns)]
            
            if termination_keywords:
                for keyword in termination_keywords:
                    termination_conditions.append(TextMentionTermination(keyword))
            
            # Combine termination conditions
            termination = termination_conditions[0]
            for condition in termination_conditions[1:]:
                termination = termination | condition
            
            # Create team
            team = RoundRobinGroupChat(
                participants=team_agents,
                termination_condition=termination
            )
            
            self.teams[team_id] = team
            logger.info(f"Created team: {team_id} with {len(team_agents)} agents")
            return team_id
            
        except Exception as e:
            logger.error(f"Error creating team {team_id}: {e}")
            raise AdapterError(f"Failed to create team: {str(e)}")
    
    async def execute_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """Execute task using AutoGen v0.4 async API"""
        try:
            logger.info(f"Executing task: {task.id} of type {task.task_type}")
            
            if task.task_type == TaskType.CONVERSATION:
                return await self._execute_chat_task(task, context)
            elif task.task_type == TaskType.CODE_GENERATION:
                return await self._execute_code_task(task, context)
            elif task.task_type == TaskType.TOOL_EXECUTION:
                return await self._execute_collaboration_task(task, context)
            else:
                raise AdapterExecutionError(f"Unsupported task type: {task.task_type}")
                
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            return UniversalResult(
                content={"error": str(e)},
                status=ResultStatus.FAILURE,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    framework_info={
                        "task_id": task.id,
                    "adapter": self.name,
                    "timestamp": datetime.now().isoformat()
                }
                )
            )
    
    async def _execute_chat_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """Execute chat task with AssistantAgent"""
        if not self.agents:
            raise AdapterExecutionError("No assistant agents available for chat task")
        
        # Use first available agent
        agent_id = next(iter(self.agents.keys()))
        agent = self.agents[agent_id]
        
        # Initialize cleanup variables
        temp_user_proxy_id = None
        
        try:
            # Try direct LLM call first as a fallback
            logger.debug(f"Agent attributes: {dir(agent)}")
            logger.debug(f"Agent model_client: {getattr(agent, 'model_client', 'Not found')}")
            logger.debug(f"Agent _model_client: {getattr(agent, '_model_client', 'Not found')}")
            
            # Try to get the LLM backend from the agent
            llm_backend = None
            if hasattr(agent, 'model_client') and agent.model_client:
                llm_backend = agent.model_client
            elif hasattr(agent, '_model_client') and agent._model_client:
                llm_backend = agent._model_client
            
            if llm_backend:
                # Direct LLM call
                message_content = str(task.content) if task.content else ""
                messages = [
                    {"role": "user", "content": message_content}
                ]
                
                logger.debug(f"Attempting direct LLM call with messages: {messages}")
                logger.debug(f"Using LLM backend: {llm_backend}")
                
                # Make direct call to LLM
                response = await llm_backend.create(messages)
                logger.debug(f"Direct LLM response: {response}")
                
                # Extract content from response
                if 'choices' in response and len(response['choices']) > 0:
                    reply_content = response['choices'][0]['message']['content']
                    logger.debug(f"Extracted reply content: {reply_content}")
                    
                    return UniversalResult(
                        content={
                            "reply": reply_content,
                            "agent_id": agent_id,
                            "message_type": "text",
                            "method": "direct_llm_call"
                        },
                        status=ResultStatus.SUCCESS,
                        result_type=ResultType.TEXT,
                        metadata=ResultMetadata(
                            framework_info={
                                "task_id": task.id,
                                "adapter": self.name,
                                "agent_name": agent.name,
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    )
                else:
                    raise AdapterExecutionError("Invalid LLM response format")
            
            # Fallback to original method
            logger.debug("Falling back to AutoGen agent method")
            
            # Create a temporary user proxy for this conversation
            temp_user_proxy_id = f"temp_user_{uuid.uuid4().hex[:8]}"
            user_proxy = UserProxyAgent(name="user_proxy")
            
            # Create a simple conversation between user proxy and assistant
            # Use the chat method instead of on_messages
            message_content = str(task.content) if task.content else ""
            
            # Create a simple message format that AutoGen can handle
            messages = [
                {"role": "user", "content": message_content}
            ]
            
            # Use the agent's chat method if available, otherwise fall back to on_messages
            if hasattr(agent, 'chat'):
                response = await agent.chat(messages, user_proxy)
                reply_content = str(response) if response else "No response"
            else:
                # Fallback to on_messages
                message = TextMessage(content=message_content, source="user")
                response = await agent.on_messages([message], CancellationToken())
                
                # Extract content safely
                if hasattr(response, 'chat_message') and response.chat_message:
                    reply_content = str(response.chat_message.content) if hasattr(response.chat_message, 'content') else str(response.chat_message)
                else:
                    reply_content = str(response) if response else "No response"
            
            logger.debug(f"Agent response type: {type(response)}")
            logger.debug(f"Agent response: {response}")
            logger.debug(f"Extracted reply content: {reply_content}")
            
            if not reply_content or reply_content == "No response":
                raise AdapterExecutionError("No model result was produced.")
            
            return UniversalResult(
                content={
                    "reply": reply_content,
                    "agent_id": agent_id,
                    "message_type": "text"
                },
                status=ResultStatus.SUCCESS,
                result_type=ResultType.TEXT,
                metadata=ResultMetadata(
                    framework_info={
                        "task_id": task.id,
                        "adapter": self.name,
                        "agent_name": agent.name,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            )
            
        except asyncio.CancelledError:
            raise AdapterExecutionError("Task was cancelled")
        except Exception as e:
            raise AdapterExecutionError(f"Chat execution failed: {str(e)}")
        finally:
            # Cleanup temporary user proxy
            if temp_user_proxy_id and temp_user_proxy_id in self.user_proxies:
                del self.user_proxies[temp_user_proxy_id]
    
    async def _execute_code_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """Execute code generation task"""
        if not self.agents:
            raise AdapterExecutionError("No agents available for code task")
        
        # Create a team with assistant and code executor
        if not self.code_executors:
            # Create a temporary code executor
            temp_executor_id = f"temp_executor_{uuid.uuid4().hex[:8]}"
            self.create_code_executor_agent(temp_executor_id, "Code Executor")
        
        agent_id = next(iter(self.agents.keys()))
        executor_id = next(iter(self.code_executors.keys()))
        
        # Create temporary team
        temp_team_id = f"temp_team_{uuid.uuid4().hex[:8]}"
        self._create_team_internal(temp_team_id, [agent_id, executor_id], max_turns=5, 
                        termination_keywords=["TERMINATE"])
        
        team = self.teams[temp_team_id]
        
        try:
            # Run team task
            result = await team.run(task=task.content)
            
            return UniversalResult(
                content={
                    "code_result": "Code task completed",
                    "team_id": temp_team_id,
                    "messages_count": len(result.messages) if hasattr(result, 'messages') else 0
                },
                status=ResultStatus.SUCCESS,
                result_type=ResultType.CODE,
                metadata=ResultMetadata(
                    framework_info={
                        "task_id": task.id,
                    "adapter": self.name,
                    "timestamp": datetime.now().isoformat()
                }
                )
            )
            
        except Exception as e:
            raise AdapterExecutionError(f"Code execution failed: {str(e)}")
        finally:
            # Cleanup temporary team
            if temp_team_id in self.teams:
                del self.teams[temp_team_id]
    
    async def _execute_collaboration_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """Execute collaboration task with team"""
        if not self.teams:
            raise AdapterExecutionError("No teams available for collaboration task")
        
        # Use first available team
        team_id = next(iter(self.teams.keys()))
        team = self.teams[team_id]
        
        try:
            result = await team.run(task=task.content)
            
            return UniversalResult(
                content={
                    "team_id": team_id,
                    "status": "completed",
                    "participants": [agent.name for agent in team.participants],
                    "messages_count": len(result.messages) if hasattr(result, 'messages') else 0
                },
                status=ResultStatus.SUCCESS,
                result_type=ResultType.STRUCTURED,
                metadata=ResultMetadata(
                    framework_info={
                        "task_id": task.id,
                    "adapter": self.name,
                    "timestamp": datetime.now().isoformat()
                }
                )
            )
            
        except Exception as e:
            raise AdapterExecutionError(f"Collaboration failed: {str(e)}")
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent status"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return {
                "agent_id": agent_id,
                "status": "active",
                "agent_type": "assistant",
                "name": agent.name
            }
        elif agent_id in self.code_executors:
            agent = self.code_executors[agent_id]
            return {
                "agent_id": agent_id,
                "status": "active", 
                "agent_type": "code_executor",
                "name": agent.name
            }
        elif agent_id in self.user_proxies:
            agent = self.user_proxies[agent_id]
            return {
                "agent_id": agent_id,
                "status": "active",
                "agent_type": "user_proxy", 
                "name": agent.name
            }
        else:
            return {
                "agent_id": agent_id,
                "status": "not_found"
            }
    
    def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """Get team status"""
        if team_id not in self.teams:
            return {
                "team_id": team_id,
                "status": "not_found"
            }
        
        team = self.teams[team_id]
        return {
            "team_id": team_id,
            "status": "active",
            "participants": [agent.name for agent in team.participants],
            "participant_count": len(team.participants)
        }
    
    def get_adapter_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "adapter_name": self.name,
            "autogen_version": "0.4+",
            "autogen_available": AUTOGEN_V04_AVAILABLE,
            "agents_count": len(self.agents),
            "code_executors_count": len(self.code_executors),
            "user_proxies_count": len(self.user_proxies),
            "teams_count": len(self.teams),
            "model_clients_count": len(self.llm_backends)
        }
    
    async def close(self):
        """Close adapter and cleanup resources"""
        try:
            # Close LLM backends
            for backend in self.llm_backends.values():
                await backend.close()
            
            logger.info(f"Closed AutoGen v0.4 adapter: {self.name}")
            
        except Exception as e:
            logger.error(f"Error closing adapter: {e}")


# Convenience function to create adapter
def create_autogen_v04_adapter(name: str, backend_type: str = "openai", api_key: str = None,
                              model: str = None, **kwargs) -> AutoGenV04Adapter:
    """Create AutoGen v0.4 adapter with default configuration"""
    config = {
        "backend_type": backend_type,
        "default_model": model,
        "default_temperature": kwargs.get("temperature", 0.7),
        "work_dir": kwargs.get("work_dir", "temp")
    }
    
    adapter = AutoGenV04Adapter(name, config)
    
    # Create default LLM backend
    adapter.create_llm_backend(
        backend_id="default",
        backend_type=backend_type,
        api_key=api_key,
        model=model,
        **kwargs
    )
    
    return adapter 