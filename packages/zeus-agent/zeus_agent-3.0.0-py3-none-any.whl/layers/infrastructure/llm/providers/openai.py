"""
OpenAI LLM Provider
提供OpenAI API的统一访问接口
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx

from .base import (
    LLMProvider, LLMRequest, LLMResponse, LLMError, 
    LLMCapability, LLMProviderFactory
)

logger = logging.getLogger(__name__)

# 尝试导入OpenAI客户端
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not available. Install with: pip install openai")


class OpenAIProvider(LLMProvider):
    """OpenAI LLM提供商"""
    
    # OpenAI模型配置
    MODELS = {
        "gpt-4o": {
            "max_tokens": 128000,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.VISION,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN,
                LLMCapability.TOOL_USE
            ]
        },
        "gpt-4o-mini": {
            "max_tokens": 128000,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN,
                LLMCapability.TOOL_USE
            ]
        },
        "gpt-4-turbo": {
            "max_tokens": 128000,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.VISION,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN,
                LLMCapability.TOOL_USE
            ]
        },
        "gpt-3.5-turbo": {
            "max_tokens": 16384,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN
            ]
        }
    }
    
    def __init__(self, name: str = "openai", **kwargs):
        # 从环境变量或参数获取配置
        api_key = kwargs.pop("api_key", None) or os.getenv("OPENAI_API_KEY")
        base_url = kwargs.pop("base_url", None) or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        super().__init__(name=name, api_key=api_key, base_url=base_url, **kwargs)
        
        if not OPENAI_AVAILABLE:
            raise LLMError("OpenAI client not available", provider=self.name)
        
        self.default_model = kwargs.get("default_model", "gpt-4o-mini")
        self.timeout = kwargs.get("timeout", 60.0)
        self.max_retries = kwargs.get("max_retries", 3)
    
    async def initialize(self) -> None:
        """初始化OpenAI客户端"""
        if not self.api_key:
            raise LLMError("OpenAI API key is required", provider=self.name)
        
        try:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            self.is_initialized = True
            logger.info(f"OpenAI provider initialized successfully")
            
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenAI client: {e}", provider=self.name)
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._client:
            await self._client.close()
            self._client = None
        self.is_initialized = False
        logger.info("OpenAI provider cleaned up")
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """发送对话补全请求"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.validate_request(request):
            raise LLMError("Invalid request", provider=self.name)
        
        try:
            # 准备请求参数
            params = {
                "model": request.model or self.default_model,
                "messages": request.messages,
                "temperature": request.temperature,
                "stream": False
            }
            
            # 添加可选参数
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            if request.functions:
                params["functions"] = request.functions
            
            if request.tools:
                params["tools"] = request.tools
            
            if request.response_format:
                params["response_format"] = request.response_format
            
            # 添加额外参数
            params.update(request.extra_params)
            
            # 发送请求
            response = await self._client.chat.completions.create(**params)
            
            # 解析响应
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # 处理函数调用
            function_call = None
            tool_calls = None
            
            if hasattr(choice.message, 'function_call') and choice.message.function_call:
                function_call = {
                    "name": choice.message.function_call.name,
                    "arguments": choice.message.function_call.arguments
                }
            
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in choice.message.tool_calls
                ]
            
            # 构建响应
            llm_response = LLMResponse(
                request_id=request.request_id,
                content=content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {},
                finish_reason=choice.finish_reason,
                function_call=function_call,
                tool_calls=tool_calls,
                metadata={
                    "provider": self.name,
                    "response_id": response.id,
                    "created": response.created
                }
            )
            
            logger.debug(f"OpenAI completion successful: {request.request_id}")
            return llm_response
            
        except Exception as e:
            error_msg = f"OpenAI API error: {e}"
            logger.error(error_msg)
            raise LLMError(error_msg, provider=self.name, model=request.model)
    
    async def chat_completion_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """流式对话补全"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 准备请求参数
            params = {
                "model": request.model or self.default_model,
                "messages": request.messages,
                "temperature": request.temperature,
                "stream": True
            }
            
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            # 发送流式请求
            async for chunk in await self._client.chat.completions.create(**params):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            error_msg = f"OpenAI streaming error: {e}"
            logger.error(error_msg)
            raise LLMError(error_msg, provider=self.name, model=request.model)
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.MODELS.keys())
    
    def get_capabilities(self) -> List[LLMCapability]:
        """获取提供商能力"""
        # 返回所有模型的并集能力
        all_capabilities = set()
        for model_info in self.MODELS.values():
            all_capabilities.update(model_info["capabilities"])
        return list(all_capabilities)
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """获取模型信息"""
        if model not in self.MODELS:
            raise LLMError(f"Unknown model: {model}", provider=self.name)
        
        return {
            "name": model,
            "provider": self.name,
            **self.MODELS[model]
        }
    
    def validate_request(self, request: LLMRequest) -> bool:
        """验证请求是否有效"""
        if not request.messages:
            logger.error("Empty messages in request")
            return False
        
        model = request.model or self.default_model
        if model not in self.MODELS:
            logger.error(f"Invalid model: {model}")
            return False
        
        # 验证消息格式
        for msg in request.messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                logger.error(f"Invalid message format: {msg}")
                return False
        
        return True


# 注册OpenAI提供商
LLMProviderFactory.register("openai", OpenAIProvider) 