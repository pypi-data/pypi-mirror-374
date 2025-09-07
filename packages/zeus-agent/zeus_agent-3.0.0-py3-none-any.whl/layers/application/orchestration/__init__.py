"""
应用编排层核心模块
提供应用组装、服务发现、负载均衡、生命周期管理等核心功能
"""

from .orchestrator import ApplicationOrchestrator
from .service_registry import ServiceRegistry
from .load_balancer import LoadBalancer
from .lifecycle_manager import ApplicationLifecycleManager

__all__ = [
    "ApplicationOrchestrator",
    "ServiceRegistry", 
    "LoadBalancer",
    "ApplicationLifecycleManager"
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Application Team" 