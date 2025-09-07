"""
LLM Client Manager
统一的LLM服务管理和访问接口
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

from .providers.base import (
    LLMProvider, LLMRequest, LLMResponse, LLMError, 
    LLMCapability, LLMProviderFactory
)

logger = logging.getLogger(__name__)


class LLMClientManager:
    """LLM客户端管理器"""
    
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._default_provider: Optional[str] = None
        self._router = None
        self._cache = None
        self._rate_limiter = None
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化LLM客户端管理器"""
        config = config or {}
        
        # 初始化配置的提供商
        providers_config = config.get("providers", {})
        
        for provider_name, provider_config in providers_config.items():
            try:
                await self.add_provider(provider_name, provider_config)
                logger.info(f"Added LLM provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to add provider {provider_name}: {e}")
        
        # 设置默认提供商
        if config.get("default_provider"):
            self.set_default_provider(config["default_provider"])
        elif self._providers:
            # 如果没有指定默认提供商，使用第一个
            self.set_default_provider(next(iter(self._providers.keys())))
        
        logger.info(f"LLM Manager initialized with {len(self._providers)} providers")
    
    async def add_provider(self, name: str, config: Dict[str, Any]) -> None:
        """添加LLM提供商"""
        try:
            # 创建提供商实例
            provider = LLMProviderFactory.create(name, **config)
            
            # 初始化提供商
            await provider.initialize()
            
            # 添加到管理器
            self._providers[name] = provider
            
            logger.info(f"Successfully added LLM provider: {name}")
            
        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
            raise LLMError(f"Failed to add provider {name}: {e}")
    
    async def remove_provider(self, name: str) -> None:
        """移除LLM提供商"""
        if name not in self._providers:
            raise LLMError(f"Provider {name} not found")
        
        # 清理提供商资源
        await self._providers[name].cleanup()
        
        # 从管理器中移除
        del self._providers[name]
        
        # 如果是默认提供商，清除默认设置
        if self._default_provider == name:
            self._default_provider = None
            if self._providers:
                self._default_provider = next(iter(self._providers.keys()))
        
        logger.info(f"Removed LLM provider: {name}")
    
    def set_default_provider(self, name: str) -> None:
        """设置默认LLM提供商"""
        if name not in self._providers:
            raise LLMError(f"Provider {name} not found")
        
        self._default_provider = name
        logger.info(f"Set default LLM provider: {name}")
    
    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """获取LLM提供商"""
        provider_name = name or self._default_provider
        
        if not provider_name:
            raise LLMError("No provider specified and no default provider set")
        
        if provider_name not in self._providers:
            raise LLMError(f"Provider {provider_name} not found")
        
        return self._providers[provider_name]
    
    def list_providers(self) -> List[str]:
        """列出所有提供商"""
        return list(self._providers.keys())
    
    def get_provider_info(self, name: str) -> Dict[str, Any]:
        """获取提供商信息"""
        provider = self.get_provider(name)
        return {
            "name": provider.name,
            "models": provider.get_available_models(),
            "capabilities": [cap.value for cap in provider.get_capabilities()],
            "initialized": provider.is_initialized
        }
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """发送对话补全请求"""
        
        # 创建请求
        request = LLMRequest(
            messages=messages,
            model=model,
            **kwargs
        )
        
        # 选择提供商
        llm_provider = self.get_provider(provider)
        
        # 发送请求
        try:
            response = await llm_provider.chat_completion(request)
            logger.debug(f"Chat completion successful via {llm_provider.name}")
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed via {llm_provider.name}: {e}")
            raise
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ):
        """流式对话补全"""
        
        # 创建请求
        request = LLMRequest(
            messages=messages,
            model=model,
            stream=True,
            **kwargs
        )
        
        # 选择提供商
        llm_provider = self.get_provider(provider)
        
        # 发送流式请求
        try:
            async for chunk in llm_provider.chat_completion_stream(request):
                yield chunk
                
        except Exception as e:
            logger.error(f"Stream completion failed via {llm_provider.name}: {e}")
            raise
    
    async def health_check(self, provider: Optional[str] = None) -> Dict[str, bool]:
        """健康检查"""
        if provider:
            # 检查特定提供商
            llm_provider = self.get_provider(provider)
            result = await llm_provider.health_check()
            return {provider: result}
        else:
            # 检查所有提供商
            results = {}
            for name, llm_provider in self._providers.items():
                try:
                    results[name] = await llm_provider.health_check()
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {e}")
                    results[name] = False
            return results
    
    async def get_available_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """获取可用模型"""
        if provider:
            # 获取特定提供商的模型
            llm_provider = self.get_provider(provider)
            return {provider: llm_provider.get_available_models()}
        else:
            # 获取所有提供商的模型
            all_models = {}
            for name, llm_provider in self._providers.items():
                all_models[name] = llm_provider.get_available_models()
            return all_models
    
    async def cleanup(self) -> None:
        """清理所有资源"""
        for name, provider in self._providers.items():
            try:
                await provider.cleanup()
                logger.info(f"Cleaned up provider: {name}")
            except Exception as e:
                logger.error(f"Failed to cleanup provider {name}: {e}")
        
        self._providers.clear()
        self._default_provider = None
        logger.info("LLM Manager cleaned up")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "providers": list(self._providers.keys()),
            "default_provider": self._default_provider,
            "provider_info": {
                name: {
                    "models": provider.get_available_models(),
                    "capabilities": [cap.value for cap in provider.get_capabilities()],
                    "initialized": provider.is_initialized
                }
                for name, provider in self._providers.items()
            }
        }
    
    def __repr__(self) -> str:
        return f"<LLMClientManager(providers={list(self._providers.keys())}, default={self._default_provider})>"


# 全局LLM管理器实例
llm_manager = LLMClientManager()


# 便捷函数
async def initialize_llm_manager(config: Optional[Dict[str, Any]] = None) -> LLMClientManager:
    """初始化全局LLM管理器"""
    await llm_manager.initialize(config)
    return llm_manager


async def get_llm_response(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs
) -> LLMResponse:
    """获取LLM响应的便捷函数"""
    return await llm_manager.chat_completion(
        messages=messages,
        model=model,
        provider=provider,
        **kwargs
    )


async def get_llm_stream(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs
):
    """获取LLM流式响应的便捷函数"""
    async for chunk in llm_manager.chat_completion_stream(
        messages=messages,
        model=model,
        provider=provider,
        **kwargs
    ):
        yield chunk 