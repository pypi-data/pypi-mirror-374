"""
DeepSeek LLM Provider
提供DeepSeek API的统一访问接口
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx
import json

from .base import (
    LLMProvider, LLMRequest, LLMResponse, LLMError, 
    LLMCapability, LLMProviderFactory
)

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM提供商"""
    
    # DeepSeek模型配置
    MODELS = {
        "deepseek-chat": {
            "max_tokens": 32768,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN,
                LLMCapability.TOOL_USE
            ]
        },
        "deepseek-coder": {
            "max_tokens": 32768,
            "capabilities": [
                LLMCapability.FUNCTION_CALLING,
                LLMCapability.STREAMING,
                LLMCapability.JSON_MODE,
                LLMCapability.SYSTEM_MESSAGE,
                LLMCapability.MULTI_TURN
            ]
        }
    }
    
    def __init__(self, name: str = "deepseek", **kwargs):
        # 从环境变量或参数获取配置
        api_key = kwargs.pop("api_key", None) or os.getenv("DEEPSEEK_API_KEY")
        base_url = kwargs.pop("base_url", None) or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        
        super().__init__(name=name, api_key=api_key, base_url=base_url, **kwargs)
        
        self.default_model = kwargs.get("default_model", "deepseek-chat")
        self.timeout = kwargs.get("timeout", 60.0)
        self.max_retries = kwargs.get("max_retries", 3)
    
    async def initialize(self) -> None:
        """初始化DeepSeek客户端"""
        if not self.api_key:
            raise LLMError("DeepSeek API key is required", provider=self.name)
        
        try:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            self.is_initialized = True
            logger.info(f"DeepSeek provider initialized successfully")
            
        except Exception as e:
            raise LLMError(f"Failed to initialize DeepSeek client: {e}", provider=self.name)
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self.is_initialized = False
        logger.info("DeepSeek provider cleaned up")
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """发送对话补全请求"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.validate_request(request):
            raise LLMError("Invalid request", provider=self.name)
        
        try:
            # 准备请求参数
            payload = {
                "model": request.model or self.default_model,
                "messages": request.messages,
                "temperature": request.temperature,
                "stream": False
            }
            
            # 添加可选参数
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            
            if request.functions:
                payload["functions"] = request.functions
            
            if request.tools:
                payload["tools"] = request.tools
            
            if request.response_format:
                payload["response_format"] = request.response_format
            
            # 添加额外参数
            payload.update(request.extra_params)
            
            logger.debug(f"DeepSeek API request: {payload}")
            
            # 发送请求
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            logger.debug(f"DeepSeek API response: {response_data}")
            
            # 解析响应
            if not response_data.get("choices"):
                raise LLMError("No choices in response", provider=self.name)
            
            choice = response_data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # 处理函数调用
            function_call = None
            tool_calls = None
            
            if "function_call" in message:
                function_call = message["function_call"]
            
            if "tool_calls" in message:
                tool_calls = message["tool_calls"]
            
            # 构建响应
            llm_response = LLMResponse(
                request_id=request.request_id,
                content=content,
                model=response_data.get("model", request.model or self.default_model),
                usage=response_data.get("usage", {}),
                finish_reason=choice.get("finish_reason"),
                function_call=function_call,
                tool_calls=tool_calls,
                metadata={
                    "provider": self.name,
                    "response_id": response_data.get("id"),
                    "created": response_data.get("created")
                }
            )
            
            logger.debug(f"DeepSeek completion successful: {request.request_id}")
            return llm_response
            
        except httpx.HTTPStatusError as e:
            error_msg = f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise LLMError(error_msg, provider=self.name, model=request.model)
        except Exception as e:
            error_msg = f"DeepSeek API error: {e}"
            logger.error(error_msg)
            raise LLMError(error_msg, provider=self.name, model=request.model)
    
    async def chat_completion_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """流式对话补全"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 准备请求参数
            payload = {
                "model": request.model or self.default_model,
                "messages": request.messages,
                "temperature": request.temperature,
                "stream": True
            }
            
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            
            # 发送流式请求
            async with self._client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            error_msg = f"DeepSeek streaming error: {e}"
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


# 注册DeepSeek提供商
LLMProviderFactory.register("deepseek", DeepSeekProvider) 