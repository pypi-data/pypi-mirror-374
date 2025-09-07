"""
LLM Provider Base Classes
定义所有LLM提供商的统一接口和抽象基类
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class LLMModelType(Enum):
    """LLM模型类型枚举"""
    CHAT = "chat"              # 对话模型
    COMPLETION = "completion"  # 补全模型
    EMBEDDING = "embedding"    # 嵌入模型
    IMAGE = "image"           # 图像理解模型
    CODE = "code"             # 代码模型


class LLMCapability(Enum):
    """LLM能力枚举"""
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    VISION = "vision"
    JSON_MODE = "json_mode"
    SYSTEM_MESSAGE = "system_message"
    MULTI_TURN = "multi_turn"
    TOOL_USE = "tool_use"


class LLMRequest:
    """LLM请求封装"""
    
    def __init__(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.request_id = str(uuid.uuid4())
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream
        self.functions = functions
        self.tools = tools
        self.response_format = response_format
        self.extra_params = kwargs
        self.created_at = datetime.now()


class LLMResponse:
    """LLM响应封装"""
    
    def __init__(
        self,
        request_id: str,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
        function_call: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.response_id = str(uuid.uuid4())
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "request_id": self.request_id,
            "response_id": self.response_id,
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "function_call": self.function_call,
            "tool_calls": self.tool_calls,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class LLMError(Exception):
    """LLM相关错误基类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.provider = provider
        self.model = model
        self.timestamp = datetime.now()


class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    def __init__(self, name: str, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, **kwargs):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs
        self.is_initialized = False
        self._client = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化提供商"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass
    
    @abstractmethod
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """发送对话补全请求"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """流式对话补全"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[LLMCapability]:
        """获取提供商能力"""
        pass
    
    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """获取模型信息"""
        pass
    
    @abstractmethod
    def validate_request(self, request: LLMRequest) -> bool:
        """验证请求是否有效"""
        pass
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 发送简单的测试请求
            test_request = LLMRequest(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            await self.chat_completion(test_request)
            return True
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, initialized={self.is_initialized})>"


class LLMProviderFactory:
    """LLM提供商工厂类"""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        """注册提供商类"""
        cls._providers[name] = provider_class
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def create(cls, name: str, **kwargs) -> LLMProvider:
        """创建提供商实例"""
        if name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {name}")
        
        provider_class = cls._providers[name]
        return provider_class(name=name, **kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有注册的提供商"""
        return list(cls._providers.keys()) 