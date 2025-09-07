"""
Application Layer - 应用层
包含应用编排、API网关、任务队列、CLI工具、Web界面等
"""

__version__ = "3.0.0"
__description__ = "应用层 - 应用编排、CLI工具、Web界面、API文档"

# 导入核心组件
from .orchestration.orchestrator import ApplicationOrchestrator
from .orchestration.service_registry import ServiceRegistry
from .orchestration.load_balancer import LoadBalancer
from .orchestration.lifecycle_manager import ApplicationLifecycleManager

# 导入CLI工具
from .cli.commands import CommandRegistry
from .cli.enhanced_commands import EnhancedCommandRegistry
from .cli.interactive import InteractiveShell

# 导入Web界面
from .web.web_manager import WebInterfaceManager
from .web.api_docs_generator import APIDocsGenerator

# 导入通信管理
from .communication_manager import ApplicationCommunicationManager

__all__ = [
    # 应用编排
    "ApplicationOrchestrator",
    "ServiceRegistry", 
    "LoadBalancer",
    "ApplicationLifecycleManager",
    
    # CLI工具
    "CommandRegistry",
    "EnhancedCommandRegistry", 
    "InteractiveShell",
    
    # Web界面
    "WebInterfaceManager",
    "APIDocsGenerator",
    
    # 通信管理
    "ApplicationCommunicationManager",
    
    # 版本信息
    "__version__",
    "__description__"
] 