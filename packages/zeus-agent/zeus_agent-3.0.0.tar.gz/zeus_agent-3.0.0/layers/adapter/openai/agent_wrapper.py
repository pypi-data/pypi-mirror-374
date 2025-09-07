"""
OpenAI Agent Wrapper
OpenAI Agent包装器，提供高级Agent功能
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ...framework.abstractions.agent import UniversalAgent, AgentCapability, AgentStatus
from ...framework.abstractions.task import UniversalTask, TaskType
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult, ResultStatus, ErrorInfo
from .adapter import OpenAIAdapter

logger = logging.getLogger(__name__)


class OpenAIAgentWrapper(UniversalAgent):
    """
    OpenAI Agent包装器
    
    将OpenAI API包装为UniversalAgent接口
    """
    
    def __init__(self, 
                 name: str,
                 adapter: OpenAIAdapter,
                 description: str = "",
                 capabilities: List[AgentCapability] = None,
                 config: Dict[str, Any] = None):
        
        # 默认能力
        if capabilities is None:
            capabilities = [
                AgentCapability.CONVERSATION,
                AgentCapability.CODE_GENERATION,
                AgentCapability.TOOL_CALLING,
                AgentCapability.REASONING,
            ]
        
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            config=config or {}
        )
        
        self.adapter = adapter
        self.system_message = config.get("system_message", "") if config else ""
        self.model_config = config.get("model_config", "default") if config else "default"
        
    async def execute(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """
        执行任务
        
        Args:
            task: 要执行的任务
            context: 执行上下文
            
        Returns:
            UniversalResult: 执行结果
        """
        try:
            self.status = AgentStatus.BUSY
            self.metadata.last_active = datetime.now()
            
            # 增强上下文
            enhanced_context = self._enhance_context(context)
            
            # 执行任务
            result = await self.adapter.execute_task(task, enhanced_context)
            
            # 更新统计
            self.metadata.total_tasks += 1
            if result.is_successful():
                self.metadata.successful_tasks += 1
            else:
                self.metadata.failed_tasks += 1
            
            # 更新平均响应时间
            if result.metadata and result.metadata.execution_time:
                total_time = (self.metadata.average_response_time * (self.metadata.total_tasks - 1) + 
                            result.metadata.execution_time)
                self.metadata.average_response_time = total_time / self.metadata.total_tasks
            
            self.status = AgentStatus.IDLE
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.metadata.total_tasks += 1
            self.metadata.failed_tasks += 1
            
            logger.error(f"Task execution failed for agent {self.name}: {e}")
            
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=f"Agent execution failed: {str(e)}"
                )
            )
    
    def _enhance_context(self, context: UniversalContext) -> UniversalContext:
        """增强上下文信息"""
        enhanced_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
        
        # 复制原有上下文
        for key in context.keys():
            enhanced_context.set(key, context.get(key))
        
        # 添加Agent特定信息
        if self.system_message:
            enhanced_context.set("system_message", self.system_message)
        
        enhanced_context.set("model_config", self.model_config)
        enhanced_context.set("agent_name", self.name)
        enhanced_context.set("agent_capabilities", [cap.value for cap in self.capabilities])
        
        return enhanced_context
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取Agent的配置模式
        
        Returns:
            Dict: JSON Schema格式的配置模式
        """
        return {
            "type": "object",
            "properties": {
                "system_message": {
                    "type": "string",
                    "description": "System message for the agent",
                    "default": ""
                },
                "model_config": {
                    "type": "string",
                    "description": "Model configuration name",
                    "default": "default"
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "default": 0.7
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens in response",
                    "minimum": 1,
                    "maximum": 4096,
                    "default": 2000
                }
            }
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置Agent
        
        Args:
            config: 配置字典
        """
        if "system_message" in config:
            self.system_message = config["system_message"]
        
        if "model_config" in config:
            self.model_config = config["model_config"]
        
        # 更新基础配置
        self.config.update(config)
        
        logger.info(f"Agent {self.name} configured with new settings")
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        简化的聊天接口
        
        Args:
            message: 用户消息
            conversation_history: 对话历史
            
        Returns:
            str: Agent回复
        """
        # 创建任务
        task = UniversalTask(
            content=message,
            task_type=TaskType.CONVERSATION
        )
        
        # 创建上下文
        context = UniversalContext()
        if conversation_history:
            context.set("conversation_history", conversation_history)
        
        # 执行任务
        result = await self.execute(task, context)
        
        if result.is_successful():
            if isinstance(result.content, str):
                return result.content
            elif isinstance(result.content, dict):
                return result.content.get("message", str(result.content))
            else:
                return str(result.content)
        else:
            error_msg = result.error.error_message if result.error else "Unknown error"
            return f"Sorry, I encountered an error: {error_msg}"
    
    async def generate_code(self, description: str, language: str = "python") -> Dict[str, Any]:
        """
        代码生成接口
        
        Args:
            description: 代码描述
            language: 编程语言
            
        Returns:
            Dict: 代码生成结果
        """
        # 创建任务
        task = UniversalTask(
            content=description,
            task_type=TaskType.CODE_GENERATION
        )
        
        # 创建上下文
        context = UniversalContext()
        context.set("language", language)
        
        # 执行任务
        result = await self.execute(task, context)
        
        if result.is_successful() and isinstance(result.content, dict):
            return result.content
        else:
            return {
                "code": "",
                "language": language,
                "explanation": result.error.error_message if result.error else "Code generation failed",
                "error": True
            }
    
    async def analyze(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        内容分析接口
        
        Args:
            content: 要分析的内容
            analysis_type: 分析类型
            
        Returns:
            Dict: 分析结果
        """
        # 创建任务
        task = UniversalTask(
            content=content,
            task_type=TaskType.ANALYSIS
        )
        
        # 创建上下文
        context = UniversalContext()
        context.set("analysis_type", analysis_type)
        
        # 执行任务
        result = await self.execute(task, context)
        
        if result.is_successful() and isinstance(result.content, dict):
            return result.content
        else:
            return {
                "analysis_type": analysis_type,
                "analysis": result.error.error_message if result.error else "Analysis failed",
                "confidence": 0.0,
                "error": True
            }
    
    def __str__(self) -> str:
        return f"OpenAIAgentWrapper(name='{self.name}', status='{self.status.value}', model_config='{self.model_config}')" 