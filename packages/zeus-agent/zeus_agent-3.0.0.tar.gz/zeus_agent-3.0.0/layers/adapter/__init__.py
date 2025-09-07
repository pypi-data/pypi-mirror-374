"""
适配器层 - Adapter Layer
提供各种AI框架的适配器，实现框架无关的Agent开发
"""

# 基础适配器
from .base import BaseAdapter, AdapterStatus, AdapterCapability

# 适配器注册表
from .registry.adapter_registry import AdapterRegistry

# 层间通信管理器
from .communication_manager import (
    AdapterCommunicationManager,
    adapter_communication_manager
)

__all__ = [
    # 基础适配器
    'BaseAdapter',
    'AdapterStatus', 
    'AdapterCapability',
    
    # 适配器注册表
    'AdapterRegistry',
    
    # 层间通信管理器
    'AdapterCommunicationManager',
    'adapter_communication_manager'
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Adapter Team" 