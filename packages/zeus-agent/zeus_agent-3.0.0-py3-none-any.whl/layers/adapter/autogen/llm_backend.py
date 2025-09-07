"""
LLM Backend Abstraction for AutoGen Adapter
Supports different LLM services like OpenAI, DeepSeek, etc.
"""

import os
import logging
import json
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    def __init__(self):
        """Initialize LLM backend"""
        self.model_info = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True
        }
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to LLM service"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close any resources"""
        pass


class OpenAIBackend(LLMBackend):
    """OpenAI API backend"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo",
                 base_url: str = "https://api.openai.com/v1",
                 **kwargs):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 1000)
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Update model info
        self.model_info.update({
            "family": "openai",
            "vision": model.endswith("-vision")
        })
        
        logger.info(f"Initialized OpenAI backend with model {model}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to OpenAI API"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens)
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class DeepSeekBackend(LLMBackend):
    """DeepSeek API backend"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat",
                 base_url: str = "https://api.deepseek.com/v1",
                 **kwargs):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 1000)
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Update model info
        self.model_info.update({
            "family": "deepseek",
            "vision": False  # DeepSeek doesn't support vision yet
        })
        
        logger.info(f"Initialized DeepSeek backend with model {model}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to DeepSeek API"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens)
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


def create_llm_backend(backend_type: str, api_key: str = None, **kwargs) -> LLMBackend:
    """Create LLM backend instance"""
    if backend_type == "openai":
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        return OpenAIBackend(api_key=api_key, **kwargs)
        
    elif backend_type == "deepseek":
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key not provided")
        return DeepSeekBackend(api_key=api_key, **kwargs)
        
    else:
        raise ValueError(f"Unsupported LLM backend type: {backend_type}") 