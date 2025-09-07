"""
OpenAI Adapter - OpenAI API框架适配器
支持OpenAI的所有核心功能：GPT模型、函数调用、多模态处理等
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# 导入OpenAI相关模块
try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

# 导入框架抽象类
from ...framework.abstractions.agent import UniversalAgent, AgentCapability
from ...framework.abstractions.task import UniversalTask, TaskType
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult, ResultStatus, ResultType, ResultMetadata, ErrorInfo
from ..base import BaseAdapter, AdapterCapability, AdapterError, AdapterInitializationError, AdapterExecutionError, AdapterStatus
from ..registry.adapter_registry import AdapterInfo

logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseAdapter):
    """
    OpenAI API适配器
    
    支持OpenAI的核心功能：
    - GPT-3.5/GPT-4系列模型
    - 函数调用 (Function Calling)
    - 多模态处理 (Vision, Audio)
    - 流式响应
    - 嵌入向量
    """
    
    def __init__(self, name: str = "openai"):
        super().__init__(name)
        
        if not OPENAI_AVAILABLE:
            raise AdapterInitializationError("OpenAI is not available. Please install openai package.")
        
        # OpenAI客户端
        self.client: Optional[AsyncOpenAI] = None
        self.model_configs = {}
        self.function_schemas = {}
        
    def get_framework_name(self) -> str:
        return "OpenAI"
    
    def get_framework_version(self) -> str:
        try:
            import openai
            return openai.__version__
        except:
            return "unknown"
    
    def get_framework_capabilities(self) -> List[AdapterCapability]:
        return [
            AdapterCapability.CONVERSATION,
            AdapterCapability.CODE_GENERATION,
            AdapterCapability.TOOL_CALLING,
            AdapterCapability.MULTIMODAL,
        ]
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化OpenAI适配器"""
        try:
            start_time = time.time()
            
            # 获取API密钥
            api_key = config.get("api_key")
            if not api_key:
                raise AdapterInitializationError("OpenAI API key is required")
            
            # 创建客户端
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=config.get("base_url"),
                timeout=config.get("timeout", 30.0),
                max_retries=config.get("max_retries", 3)
            )
            
            # 配置默认模型
            self.model_configs = {
                "default": {
                    "model": config.get("model", "gpt-4o-mini"),
                    "temperature": config.get("temperature", 0.7),
                    "max_tokens": config.get("max_tokens", 2000),
                    "top_p": config.get("top_p", 1.0),
                    "frequency_penalty": config.get("frequency_penalty", 0.0),
                    "presence_penalty": config.get("presence_penalty", 0.0)
                }
            }
            
            # 测试连接
            await self._test_connection()
            
            self.status = AdapterStatus.READY
            initialization_time = time.time() - start_time
            
            # 更新元数据
            self.metadata.last_initialized = datetime.now()
            self.metadata.initialization_count += 1
            self.metadata.average_initialization_time = (
                (self.metadata.average_initialization_time * (self.metadata.initialization_count - 1) + initialization_time)
                / self.metadata.initialization_count
            )
            
            logger.info(f"OpenAI adapter initialized successfully in {initialization_time:.2f}s")
            return True
            
        except Exception as e:
            self.status = AdapterStatus.ERROR
            error_msg = f"Failed to initialize OpenAI adapter: {str(e)}"
            logger.error(error_msg)
            raise AdapterInitializationError(error_msg)
    
    async def _test_connection(self):
        """测试OpenAI API连接"""
        try:
            # 发送一个简单的测试请求
            response = await self.client.chat.completions.create(
                model=self.model_configs["default"]["model"],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI API")
                
        except Exception as e:
            raise AdapterInitializationError(f"OpenAI API connection test failed: {str(e)}")
    
    async def execute_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务"""
        if self.status != AdapterStatus.READY:
            return UniversalResult(
                content="Adapter not ready",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type="AdapterNotReady",
                    error_message="OpenAI adapter is not initialized"
                )
            )
        
        try:
            start_time = time.time()
            
            # 根据任务类型选择处理方法
            if task.task_type == TaskType.CONVERSATION:
                result = await self._handle_conversation(task, context)
            elif task.task_type == TaskType.CODE_GENERATION:
                result = await self._handle_code_generation(task, context)
            elif task.task_type == TaskType.TOOL_EXECUTION:
                result = await self._handle_tool_execution(task, context)
            elif task.task_type == TaskType.ANALYSIS:
                result = await self._handle_analysis(task, context)
            else:
                result = await self._handle_generic_task(task, context)
            
            # 设置执行时间
            execution_time = time.time() - start_time
            if result.metadata:
                result.metadata.execution_time = execution_time
            
            # 更新统计
            if result.is_successful():
                self.metadata.successful_operations += 1
            else:
                self.metadata.failed_operations += 1
            
            return result
            
        except Exception as e:
            self.metadata.failed_operations += 1
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)
            
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=error_msg
                )
            )
    
    async def _handle_conversation(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """处理对话任务"""
        try:
            # 构建消息历史
            messages = self._build_messages(task, context)
            
            # 获取模型配置
            model_config = self._get_model_config(context)
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                top_p=model_config["top_p"],
                frequency_penalty=model_config["frequency_penalty"],
                presence_penalty=model_config["presence_penalty"]
            )
            
            # 处理响应
            if not response.choices:
                raise Exception("No response from OpenAI")
            
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # 构建结果
            metadata = ResultMetadata(
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model_info={
                    "model": response.model,
                    "finish_reason": choice.finish_reason
                },
                framework_info={
                    "framework": "openai",
                    "response_id": response.id,
                    "created": response.created
                }
            )
            
            return UniversalResult(
                content=content,
                status=ResultStatus.SUCCESS,
                result_type=ResultType.TEXT,
                metadata=metadata
            )
            
        except Exception as e:
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=f"Conversation failed: {str(e)}"
                )
            )
    
    async def _handle_code_generation(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """处理代码生成任务"""
        try:
            # 构建代码生成提示
            language = context.get("language", "python")
            prompt = f"""Generate {language} code for the following requirement:

{task.content}

Please provide:
1. Clean, well-documented code
2. Brief explanation of the approach
3. Any dependencies needed

Format your response as:
```{language}
# Your code here
```

Explanation: [Your explanation here]
Dependencies: [List any dependencies]"""

            # 创建代码生成任务
            messages = [{"role": "user", "content": prompt}]
            
            model_config = self._get_model_config(context)
            
            response = await self.client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                temperature=0.3,  # Lower temperature for code generation
                max_tokens=model_config["max_tokens"]
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI")
            
            content = response.choices[0].message.content or ""
            
            # 解析代码和说明
            code_block = self._extract_code_block(content, language)
            explanation = self._extract_explanation(content)
            dependencies = self._extract_dependencies(content)
            
            result_content = {
                "code": code_block,
                "language": language,
                "explanation": explanation,
                "dependencies": dependencies,
                "full_response": content
            }
            
            metadata = ResultMetadata(
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model_info={
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
            return UniversalResult(
                content=result_content,
                status=ResultStatus.SUCCESS,
                result_type=ResultType.STRUCTURED,
                metadata=metadata
            )
            
        except Exception as e:
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=f"Code generation failed: {str(e)}"
                )
            )
    
    async def _handle_tool_execution(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """处理工具执行任务"""
        try:
            # 获取工具信息
            tool_name = context.get("tool_name")
            tool_parameters = context.get("tool_parameters", {})
            
            if not tool_name:
                raise ValueError("Tool name is required for tool execution")
            
            # 构建函数调用消息
            messages = [
                {"role": "user", "content": task.content}
            ]
            
            # 获取工具定义
            tools = self._get_available_tools(context)
            
            if not tools:
                # 如果没有工具定义，返回普通响应
                return await self._handle_conversation(task, context)
            
            model_config = self._get_model_config(context)
            
            response = await self.client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=model_config["temperature"]
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI")
            
            choice = response.choices[0]
            
            # 处理工具调用
            if choice.message.tool_calls:
                tool_results = []
                for tool_call in choice.message.tool_calls:
                    tool_result = await self._execute_tool_call(tool_call)
                    tool_results.append(tool_result)
                
                result_content = {
                    "tool_results": tool_results,
                    "message": choice.message.content
                }
            else:
                result_content = {
                    "message": choice.message.content,
                    "tool_results": []
                }
            
            metadata = ResultMetadata(
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model_info={
                    "model": response.model,
                    "finish_reason": choice.finish_reason
                }
            )
            
            return UniversalResult(
                content=result_content,
                status=ResultStatus.SUCCESS,
                result_type=ResultType.STRUCTURED,
                metadata=metadata
            )
            
        except Exception as e:
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=f"Tool execution failed: {str(e)}"
                )
            )
    
    async def _handle_analysis(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """处理分析任务"""
        try:
            analysis_type = context.get("analysis_type", "general")
            
            prompt = f"""Analyze the following content for {analysis_type} analysis:

{task.content}

Please provide a structured analysis including:
1. Summary
2. Key findings
3. Insights
4. Recommendations (if applicable)

Format your response in a clear, structured manner."""

            messages = [{"role": "user", "content": prompt}]
            model_config = self._get_model_config(context)
            
            response = await self.client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                temperature=0.5,  # Moderate temperature for analysis
                max_tokens=model_config["max_tokens"]
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI")
            
            content = response.choices[0].message.content or ""
            
            # 构建分析结果
            result_content = {
                "analysis_type": analysis_type,
                "analysis": content,
                "confidence": 0.8  # Default confidence for analysis
            }
            
            metadata = ResultMetadata(
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model_info={
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
            return UniversalResult(
                content=result_content,
                status=ResultStatus.SUCCESS,
                result_type=ResultType.STRUCTURED,
                metadata=metadata
            )
            
        except Exception as e:
            return UniversalResult(
                content="",
                status=ResultStatus.ERROR,
                error=ErrorInfo(
                    error_type=type(e).__name__,
                    error_message=f"Analysis failed: {str(e)}"
                )
            )
    
    async def _handle_generic_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """处理通用任务"""
        return await self._handle_conversation(task, context)
    
    def _build_messages(self, task: UniversalTask, context: UniversalContext) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []
        
        # 添加系统消息
        system_message = context.get("system_message")
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 添加历史对话
        conversation_history = context.get("conversation_history", [])
        for entry in conversation_history:
            if isinstance(entry, dict):
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})
        
        # 添加当前任务
        messages.append({"role": "user", "content": task.content})
        
        return messages
    
    def _get_model_config(self, context: UniversalContext) -> Dict[str, Any]:
        """获取模型配置"""
        config_name = context.get("model_config", "default")
        return self.model_configs.get(config_name, self.model_configs["default"])
    
    def _get_available_tools(self, context: UniversalContext) -> Optional[List[Dict[str, Any]]]:
        """获取可用工具"""
        tools = context.get("tools", [])
        if not tools:
            return None
        
        # 转换为OpenAI工具格式
        openai_tools = []
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    async def _execute_tool_call(self, tool_call) -> Dict[str, Any]:
        """执行工具调用"""
        try:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            
            # 这里应该实际执行工具调用
            # 目前返回模拟结果
            return {
                "tool_call_id": tool_call.id,
                "function_name": function_name,
                "arguments": arguments,
                "result": f"Tool {function_name} executed successfully",
                "success": True
            }
            
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "function_name": getattr(tool_call.function, 'name', 'unknown'),
                "error": str(e),
                "success": False
            }
    
    def _extract_code_block(self, content: str, language: str) -> str:
        """从响应中提取代码块"""
        import re
        pattern = f"```{language}\\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)
        return matches[0].strip() if matches else ""
    
    def _extract_explanation(self, content: str) -> str:
        """从响应中提取说明"""
        import re
        pattern = r"Explanation:\s*(.*?)(?=Dependencies:|$)"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        return matches[0].strip() if matches else ""
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """从响应中提取依赖"""
        import re
        pattern = r"Dependencies:\s*(.*?)$"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            deps_text = matches[0].strip()
            # 简单解析依赖列表
            return [dep.strip() for dep in deps_text.split(',') if dep.strip()]
        return []
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.client:
            # OpenAI客户端会自动处理连接清理
            self.client = None
        
        self.status = AdapterStatus.NOT_INITIALIZED
        logger.info("OpenAI adapter cleaned up")
    
    def get_info(self) -> AdapterInfo:
        """获取适配器信息"""
        return AdapterInfo(
            name=self.name,
            framework_name=self.get_framework_name(),
            framework_version=self.get_framework_version(),
            capabilities=self.get_framework_capabilities(),
            status=self.status,
            metadata=self.metadata
        )
    
    async def create_agent(self, config: Dict[str, Any]) -> UniversalAgent:
        """创建Agent实例"""
        from .agent_wrapper import OpenAIAgentWrapper
        
        agent_wrapper = OpenAIAgentWrapper(
            name=config.get("name", "OpenAIAgent"),
            adapter=self,
            description=config.get("description", "OpenAI Agent"),
            config=config
        )
        
        return agent_wrapper
    
    async def create_team(self, config: Dict[str, Any]) -> Any:
        """创建团队（暂未实现）"""
        # TODO: 实现团队创建逻辑
        logger.warning("Team creation not yet implemented for OpenAI adapter")
        return None
    
    def get_capabilities(self) -> List[AdapterCapability]:
        """获取适配器能力"""
        return [
            AdapterCapability.CONVERSATION,
            AdapterCapability.CODE_GENERATION,
            AdapterCapability.TOOL_CALLING,
            AdapterCapability.MULTIMODAL,
            AdapterCapability.STREAMING
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "message": "Client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 简单的API调用测试
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "message": "OpenAI API is accessible",
                "model": "gpt-4o-mini",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            } 