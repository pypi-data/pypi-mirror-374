"""
适配器注册表
管理所有适配器的注册和发现
"""

import importlib
import logging
from typing import Dict, Any, List, Optional, Type, Set
from dataclasses import dataclass, field
from datetime import datetime

from ..base import BaseAdapter, AdapterStatus, AdapterCapability, AdapterError
from ...framework.abstractions.layer_communication import LayerMessage, LayerMessageType, LayerMessageStatus

logger = logging.getLogger(__name__)


@dataclass
class AdapterInfo:
    """适配器信息"""
    name: str
    adapter_class: Type[BaseAdapter]
    module_path: str
    capabilities: List[AdapterCapability]
    is_builtin: bool = False
    is_enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdapterRegistry:
    """
    适配器注册表
    
    负责管理所有适配器的注册、发现和生命周期管理
    """
    
    def __init__(self):
        self._adapters: Dict[str, AdapterInfo] = {}
        self._instances: Dict[str, BaseAdapter] = {}
        self._default_adapter: Optional[str] = None
        self._discovery_paths: List[str] = []
        
    def register_adapter(self, 
                        name: str, 
                        adapter_class: Type[BaseAdapter], 
                        capabilities: List[AdapterCapability],
                        module_path: str,
                        is_builtin: bool = False,
                        priority: int = 0,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        注册适配器
        
        Args:
            name: 适配器名称
            adapter_class: 适配器类
            capabilities: 支持的能力
            module_path: 模块路径
            is_builtin: 是否为内置适配器
            priority: 优先级
            metadata: 额外元数据
        """
        if name in self._adapters:
            logger.warning(f"Adapter '{name}' already registered, overwriting")
        
        self._adapters[name] = AdapterInfo(
            name=name,
            adapter_class=adapter_class,
            module_path=module_path,
            capabilities=capabilities,
            is_builtin=is_builtin,
            priority=priority,
            metadata=metadata or {}
        )
        
        logger.info(f"Registered adapter: {name} (builtin: {is_builtin}, capabilities: {[c.value for c in capabilities]})")
    
    def unregister_adapter(self, name: str) -> None:
        """
        注销适配器
        
        Args:
            name: 适配器名称
        """
        if name in self._adapters:
            del self._adapters[name]
            logger.info(f"Unregistered adapter: {name}")
        
        if name in self._instances:
            del self._instances[name]
    
    async def get_adapter(self, 
                         name: str, 
                         config: Optional[Dict[str, Any]] = None,
                         force_recreate: bool = False) -> BaseAdapter:
        """
        获取适配器实例
        
        Args:
            name: 适配器名称
            config: 配置信息
            force_recreate: 是否强制重新创建
            
        Returns:
            BaseAdapter: 适配器实例
            
        Raises:
            AdapterError: 适配器不存在或初始化失败
        """
        if name not in self._adapters:
            raise AdapterError(f"Adapter '{name}' not found")
        
        adapter_info = self._adapters[name]
        
        # 检查适配器是否已存在且不需要重新创建
        if not force_recreate and name in self._instances:
            adapter = self._instances[name]
            if adapter.is_ready():
                return adapter
        
        # 创建新的适配器实例
        try:
            adapter = adapter_info.adapter_class(name)
            
            # 初始化适配器
            if config:
                await adapter.initialize(config)
            else:
                # 使用默认配置初始化
                await adapter.initialize({})
            
            self._instances[name] = adapter
            logger.info(f"Created and initialized adapter instance: {name}")
            
            return adapter
            
        except Exception as e:
            logger.error(f"Failed to create adapter '{name}': {str(e)}")
            raise AdapterError(f"Adapter creation failed: {str(e)}")
    
    def list_adapters(self, 
                     enabled_only: bool = True,
                     with_capabilities: Optional[List[AdapterCapability]] = None) -> List[str]:
        """
        列出所有适配器
        
        Args:
            enabled_only: 是否只列出启用的适配器
            with_capabilities: 过滤具有指定能力的适配器
            
        Returns:
            List[str]: 适配器名称列表
        """
        adapters = []
        
        for name, info in self._adapters.items():
            # 过滤启用的适配器
            if enabled_only and not info.is_enabled:
                continue
            
            # 过滤能力
            if with_capabilities:
                has_all_capabilities = all(
                    capability in info.capabilities for capability in with_capabilities
                )
                if not has_all_capabilities:
                    continue
            
            adapters.append(name)
        
        # 按优先级排序
        adapters.sort(key=lambda name: self._adapters[name].priority, reverse=True)
        
        return adapters
    
    def get_adapter_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取适配器详细信息
        
        Args:
            name: 适配器名称
            
        Returns:
            Optional[Dict[str, Any]]: 适配器信息，如果不存在返回None
        """
        if name not in self._adapters:
            return None
        
        info = self._adapters[name]
        return {
            "name": info.name,
            "class": info.adapter_class.__name__,
            "module": info.module_path,
            "capabilities": [cap.value for cap in info.capabilities],
            "is_builtin": info.is_builtin,
            "is_enabled": info.is_enabled,
            "priority": info.priority,
            "metadata": info.metadata
        }
    
    def set_default_adapter(self, name: str) -> None:
        """
        设置默认适配器
        
        Args:
            name: 适配器名称
            
        Raises:
            AdapterError: 适配器不存在
        """
        if name not in self._adapters:
            raise AdapterError(f"Adapter '{name}' not found")
        
        self._default_adapter = name
        logger.info(f"Set default adapter to: {name}")
    
    def get_default_adapter(self) -> Optional[str]:
        """
        获取默认适配器
        
        Returns:
            Optional[str]: 默认适配器名称
        """
        return self._default_adapter
    
    def enable_adapter(self, name: str) -> None:
        """
        启用适配器
        
        Args:
            name: 适配器名称
            
        Raises:
            AdapterError: 适配器不存在
        """
        if name not in self._adapters:
            raise AdapterError(f"Adapter '{name}' not found")
        
        self._adapters[name].is_enabled = True
        logger.info(f"Enabled adapter: {name}")
    
    def disable_adapter(self, name: str) -> None:
        """
        禁用适配器
        
        Args:
            name: 适配器名称
            
        Raises:
            AdapterError: 适配器不存在
        """
        if name not in self._adapters:
            raise AdapterError(f"Adapter '{name}' not found")
        
        self._adapters[name].is_enabled = False
        
        # 移除实例
        if name in self._instances:
            del self._instances[name]
        
        logger.info(f"Disabled adapter: {name}")
    
    def set_discovery_paths(self, paths: List[str]) -> None:
        """
        设置适配器发现路径
        
        Args:
            paths: 路径列表
        """
        self._discovery_paths = paths.copy()
        logger.info(f"Set discovery paths: {paths}")
    
    async def discover_adapters(self) -> List[str]:
        """
        自动发现适配器
        
        Returns:
            List[str]: 发现的适配器名称列表
        """
        discovered = []
        
        for path in self._discovery_paths:
            try:
                # 尝试导入模块并查找适配器类
                module = importlib.import_module(path)
                
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseAdapter) and 
                        attr != BaseAdapter):
                        
                        # 获取适配器名称
                        adapter_name = getattr(attr, 'DEFAULT_NAME', attr.__name__.lower())
                        
                        # 获取能力列表
                        capabilities = getattr(attr, 'DEFAULT_CAPABILITIES', [])
                        
                        # 注册适配器
                        self.register_adapter(
                            name=adapter_name,
                            adapter_class=attr,
                            capabilities=capabilities,
                            module_path=path,
                            is_builtin=False
                        )
                        
                        discovered.append(adapter_name)
                        logger.info(f"Discovered adapter: {adapter_name} from {path}")
                        
            except ImportError as e:
                logger.warning(f"Failed to import discovery path {path}: {str(e)}")
                continue
        
        return discovered
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        检查所有适配器的健康状态
        
        Returns:
            Dict[str, Dict[str, Any]]: 健康检查结果
        """
        results = {}
        
        for name in self.list_adapters(enabled_only=True):
            try:
                adapter = await self.get_adapter(name)
                health = await adapter.health_check()
                results[name] = health
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def clear_instances(self) -> None:
        """清除所有适配器实例"""
        self._instances.clear()
        logger.info("Cleared all adapter instances")
    
    def __contains__(self, name: str) -> bool:
        """检查适配器是否存在"""
        return name in self._adapters
    
    def __len__(self) -> int:
        """获取适配器数量"""
        return len(self._adapters)
    
    def __str__(self) -> str:
        return f"AdapterRegistry(adapters={len(self._adapters)}, instances={len(self._instances)})"
    
    def __repr__(self) -> str:
        return self.__str__()


# 全局适配器注册表实例
_adapter_registry = AdapterRegistry()

def get_adapter_registry() -> AdapterRegistry:
    """获取全局适配器注册表"""
    return _adapter_registry

def register_adapter(name: str, 
                    adapter_class: Type[BaseAdapter], 
                    capabilities: List[AdapterCapability],
                    module_path: str,
                    **kwargs) -> None:
    """全局注册适配器"""
    _adapter_registry.register_adapter(
        name, adapter_class, capabilities, module_path, **kwargs
    )

async def get_adapter(name: str, **kwargs) -> BaseAdapter:
    """全局获取适配器"""
    return await _adapter_registry.get_adapter(name, **kwargs)

def list_adapters(**kwargs) -> List[str]:
    """全局列出适配器"""
    return _adapter_registry.list_adapters(**kwargs)
