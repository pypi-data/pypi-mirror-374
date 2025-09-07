"""
LLM Infrastructure Layer
提供统一的LLM服务基础设施
"""

# 导入所有提供商以确保注册
from .providers import openai, deepseek

# 导入主要接口
from .providers.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMError,
    LLMCapability,
    LLMModelType,
    LLMProviderFactory
)

from .client_manager import (
    LLMClientManager,
    llm_manager,
    initialize_llm_manager,
    get_llm_response,
    get_llm_stream
)

__all__ = [
    # 基础类
    "LLMProvider",
    "LLMRequest", 
    "LLMResponse",
    "LLMError",
    "LLMCapability",
    "LLMModelType",
    "LLMProviderFactory",
    
    # 管理器
    "LLMClientManager",
    "llm_manager",
    
    # 便捷函数
    "initialize_llm_manager",
    "get_llm_response",
    "get_llm_stream"
] 