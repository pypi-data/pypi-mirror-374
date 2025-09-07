"""
Cognitive Universal Agent - 认知通用Agent抽象
支持高级认知功能：对话、工具执行、代码生成、内容分析等
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .agent import UniversalAgent, AgentCapability, AgentStatus
from .task import UniversalTask, TaskType
from .context import UniversalContext
from .result import UniversalResult, ResultStatus, ResultMetadata


class AgentType(Enum):
    """Agent类型枚举"""
    CONVERSATIONAL = "conversational"
    CODING = "coding"
    RESEARCH = "research"
    MULTIMODAL = "multimodal"
    TASK_ORIENTED = "task_oriented"
    HYBRID = "hybrid"


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str  # openai, azure, anthropic, ollama
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None


@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    type: str  # python_execution, http, azure_search, custom
    description: str = ""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConfig:
    """记忆配置"""
    enabled: bool = True
    max_memories: int = 1000
    memory_type: str = "conversation"  # conversation, task, long_term


@dataclass
class BehaviorConfig:
    """行为配置"""
    max_consecutive_auto_reply: int = 3
    human_input_mode: str = "NEVER"  # NEVER, ALWAYS, TERMINATE
    code_execution_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    type: AgentType
    model: ModelConfig
    capabilities: List[AgentCapability]
    tools: List[ToolConfig] = field(default_factory=list)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    system_message: str = ""
    description: str = ""


@dataclass
class ChatContext:
    """对话上下文"""
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatResponse:
    """对话响应"""
    content: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeResult:
    """代码生成结果"""
    code: str
    language: str
    explanation: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeExecutionResult:
    """代码执行结果"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    return_code: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """分析结果"""
    analysis_type: str
    result: Dict[str, Any]
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveUniversalAgent(UniversalAgent):
    """
    认知通用Agent抽象
    
    支持高级认知功能：
    - 对话理解和生成
    - 工具使用和执行
    - 代码生成和执行
    - 内容分析和理解
    - 记忆管理
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(
            name=config.name,
            description=config.description,
            capabilities=config.capabilities,
            config=config.__dict__
        )
        
        self.agent_config = config
        self.conversation_history = []
        self.memory = {}
        self.tools = {}
        self.status = AgentStatus.IDLE
        
    async def chat(self, message: str, context: Optional[ChatContext] = None) -> ChatResponse:
        """
        基础对话功能
        
        Args:
            message: 用户消息
            context: 对话上下文
            
        Returns:
            ChatResponse: 对话响应
        """
        if context is None:
            context = ChatContext()
        
        # 创建任务
        task = UniversalTask(
            content=message,
            task_type=TaskType.CONVERSATION
        )
        
        # 创建执行上下文
        exec_context = UniversalContext({
            "conversation_mode": True,
            "conversation_history": context.conversation_history,
            "user_preferences": context.user_preferences,
            "session_data": context.session_data,
            "timestamp": context.timestamp.isoformat()
        })
        
        # 执行任务
        result = await self.execute(task, exec_context)
        
        if result.is_successful():
            response_content = result.content.get("response", "I apologize, but I couldn't generate a response.")
            
            # 记录对话历史
            self.conversation_history.append({
                "user": message,
                "assistant": response_content,
                "timestamp": datetime.now().isoformat()
            })
            
            return ChatResponse(
                content=response_content,
                confidence=result.metadata.confidence if hasattr(result.metadata, "confidence") else 1.0,
                metadata=result.metadata.framework_info,
                timestamp=datetime.now()
            )
        else:
            error_msg = result.error.get("message", "Unknown error") if result.error else "Unknown error"
            return ChatResponse(
                content=f"I encountered an error: {error_msg}",
                confidence=0.0,
                metadata={"error": True}
            )
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        工具执行功能
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 工具执行结果
        """
        start_time = datetime.now()
        
        try:
            # 创建工具执行任务
            task = UniversalTask(
                content=f"Execute tool: {tool_name}",
                task_type=TaskType.TOOL_EXECUTION
            )
            
            # 创建上下文
            context = UniversalContext({
                "tool_name": tool_name,
                "tool_parameters": kwargs,
                "timestamp": datetime.now().isoformat()
            })
            
            # 执行任务
            result = await self.execute(task, context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.is_successful():
                return ToolResult(
                    success=True,
                    result=result.content.get("tool_result"),
                    execution_time=execution_time,
                    metadata=result.metadata.framework_info
                )
            else:
                error_msg = result.error.get("message", "Tool execution failed") if result.error else "Tool execution failed"
                return ToolResult(
                    success=False,
                    result=None,
                    error_message=error_msg,
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def generate_code(self, description: str, language: str = "python") -> CodeResult:
        """
        代码生成功能
        
        Args:
            description: 代码描述
            language: 编程语言
            
        Returns:
            CodeResult: 代码生成结果
        """
        # 创建代码生成任务
        task = UniversalTask(
            content=f"Generate {language} code for: {description}",
            task_type=TaskType.CODE_GENERATION
        )
        
        # 创建上下文
        context = UniversalContext({
            "language": language,
            "code_generation": True,
            "timestamp": datetime.now().isoformat()
        })
        
        # 执行任务
        result = await self.execute(task, context)
        
        if result.is_successful():
            return CodeResult(
                code=result.content.get("code", ""),
                language=language,
                explanation=result.content.get("explanation", ""),
                dependencies=result.content.get("dependencies", []),
                metadata=result.metadata.framework_info
            )
        else:
            error_msg = result.error.get("message", "Code generation failed") if result.error else "Code generation failed"
            return CodeResult(
                code="",
                language=language,
                explanation=f"Error: {error_msg}",
                metadata={"error": True}
            )
    
    async def execute_code(self, code: str, language: str = "python") -> CodeExecutionResult:
        """
        代码执行功能
        
        Args:
            code: 要执行的代码
            language: 编程语言
            
        Returns:
            CodeExecutionResult: 代码执行结果
        """
        start_time = datetime.now()
        
        try:
            # 创建代码执行任务
            task = UniversalTask(
                content=code,
                task_type=TaskType.CODE_EXECUTION
            )
            
            # 创建上下文
            context = UniversalContext({
                "language": language,
                "code_execution": True,
                "timestamp": datetime.now().isoformat()
            })
            
            # 执行任务
            result = await self.execute(task, context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.is_successful():
                return CodeExecutionResult(
                    success=True,
                    output=result.content.get("output", ""),
                    execution_time=execution_time,
                    return_code=result.content.get("return_code", 0),
                    metadata=result.metadata.framework_info
                )
            else:
                error_msg = result.error.get("message", "Code execution failed") if result.error else "Code execution failed"
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=error_msg,
                    execution_time=execution_time,
                    return_code=-1
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CodeExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                return_code=-1
            )
    
    async def analyze_content(self, content: str, analysis_type: str = "general") -> AnalysisResult:
        """
        内容分析功能
        
        Args:
            content: 要分析的内容
            analysis_type: 分析类型 (general, sentiment, structure, etc.)
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 创建分析任务
        task = UniversalTask(
            content=f"Analyze the following content for {analysis_type}: {content}",
            task_type=TaskType.ANALYSIS
        )
        
        # 创建上下文
        context = UniversalContext({
            "analysis_type": analysis_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 执行任务
        result = await self.execute(task, context)
        
        if result.is_successful():
            return AnalysisResult(
                analysis_type=analysis_type,
                result=result.content,
                confidence=result.metadata.confidence if hasattr(result.metadata, "confidence") else 1.0,
                metadata=result.metadata.framework_info
            )
        else:
            error_msg = result.error.get("message", "Analysis failed") if result.error else "Analysis failed"
            return AnalysisResult(
                analysis_type=analysis_type,
                result={"error": error_msg},
                confidence=0.0,
                metadata={"error": True}
            )
    
    async def remember(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        记忆功能 - 让Agent记住信息
        
        Args:
            key: 记忆键
            value: 记忆值
            metadata: 元数据
        """
        if not self.agent_config.memory.enabled:
            return
        
        self.memory[key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 限制记忆数量
        if len(self.memory) > self.agent_config.memory.max_memories:
            # 删除最旧的记忆
            oldest_key = min(self.memory.keys(), key=lambda k: self.memory[k]["timestamp"])
            del self.memory[oldest_key]
    
    async def recall(self, key: str) -> Optional[Any]:
        """
        回忆功能 - 获取记忆的信息
        
        Args:
            key: 记忆键
            
        Returns:
            Optional[Any]: 记忆的值
        """
        if key in self.memory:
            return self.memory[key]["value"]
        return None
    
    async def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            
        Returns:
            List[Dict[str, Any]]: 匹配的记忆列表
        """
        # 简单的关键词搜索实现
        results = []
        query_lower = query.lower()
        
        for key, memory_item in self.memory.items():
            value_str = str(memory_item["value"]).lower()
            if query_lower in value_str or query_lower in key.lower():
                results.append({
                    "key": key,
                    "value": memory_item["value"],
                    "metadata": memory_item["metadata"],
                    "timestamp": memory_item["timestamp"]
                })
        
        return results
    
    def get_cognitive_metrics(self) -> Dict[str, Any]:
        """
        获取认知性能指标
        
        Returns:
            Dict[str, Any]: 认知性能指标
        """
        base_metrics = self.get_performance_metrics()
        
        cognitive_metrics = {
            **base_metrics,
            "agent_type": self.agent_config.type.value,
            "conversation_count": len(self.conversation_history),
            "memory_count": len(self.memory),
            "tool_count": len(self.agent_config.tools),
            "capabilities": [cap.value for cap in self.capabilities],
            "model_provider": self.agent_config.model.provider,
            "model_name": self.agent_config.model.model
        }
        
        return cognitive_metrics
    
    def __str__(self) -> str:
        return f"CognitiveUniversalAgent(name='{self.name}', type='{self.agent_config.type.value}', conversations={len(self.conversation_history)})" 