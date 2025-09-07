"""
Context Engineering Module - 上下文工程模块
提供动态、智能的上下文管理和优化功能
"""

from .context_manager import ContextManager
from .context_store import ContextStore
from .relevance_engine import RelevanceEngine
from .memory_manager import MemoryManager
from .context_adapter import ContextAdapter
from .context_optimizer import ContextOptimizer

__all__ = [
    "ContextManager",
    "ContextStore", 
    "RelevanceEngine",
    "MemoryManager",
    "ContextAdapter",
    "ContextOptimizer"
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Context Engineering Team" 