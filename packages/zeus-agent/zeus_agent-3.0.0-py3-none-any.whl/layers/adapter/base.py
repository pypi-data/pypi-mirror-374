"""
适配器基类
定义所有适配器的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from ..framework.abstractions.layer_communication import LayerMessage, LayerMessageType, LayerMessageStatus


class AdapterCapability(Enum):
    """适配器能力枚举"""
    CONVERSATION = "conversation"
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    TOOL_CALLING = "tool_calling"
    MULTIMODAL = "multimodal"
    TEAM_COLLABORATION = "team_collaboration"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"


class AdapterStatus(Enum):
    """适配器状态枚举"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AdapterMetadata:
    """适配器元数据"""
    created_at: datetime = field(default_factory=datetime.now)
    last_initialized: Optional[datetime] = None
    initialization_count: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_initialization_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """计算操作成功率"""
        total_operations = self.successful_operations + self.failed_operations
        if total_operations == 0:
            return 0.0
        return self.successful_operations / total_operations


class BaseAdapter(ABC):
    """
    适配器基类
    
    所有框架适配器都必须实现这个接口
    """
    
    def __init__(self, name: str):
        self.name = name
        self.status = AdapterStatus.NOT_INITIALIZED
        self.metadata = AdapterMetadata()
        self.config: Dict[str, Any] = {}
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        初始化适配器
        
        Args:
            config: 配置字典
            
        Raises:
            AdapterInitializationError: 初始化失败时抛出
        """
        pass
    
    @abstractmethod
    async def create_agent(self, agent_config: Dict[str, Any]) -> Any:
        """
        创建智能体
        
        Args:
            agent_config: 智能体配置
            
        Returns:
            Any: 框架特定的智能体对象
            
        Raises:
            AdapterExecutionError: 创建失败时抛出
        """
        pass
    
    @abstractmethod
    async def create_team(self, team_config: Dict[str, Any]) -> Any:
        """
        创建团队
        
        Args:
            team_config: 团队配置
            
        Returns:
            Any: 框架特定的团队对象
            
        Raises:
            AdapterExecutionError: 创建失败时抛出
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AdapterCapability]:
        """
        获取适配器支持的能力
        
        Returns:
            List[AdapterCapability]: 支持的能力列表
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        执行健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        pass
    
    def get_status(self) -> AdapterStatus:
        """获取适配器状态"""
        return self.status
    
    def get_metadata(self) -> AdapterMetadata:
        """获取适配器元数据"""
        return self.metadata
    
    def get_config(self) -> Dict[str, Any]:
        """获取适配器配置"""
        return self.config.copy()
    
    def is_ready(self) -> bool:
        """检查适配器是否就绪"""
        return self.status == AdapterStatus.READY and self.is_initialized
    
    def __str__(self) -> str:
        return f"BaseAdapter(name='{self.name}', status='{self.status.value}', initialized={self.is_initialized})"
    
    def __repr__(self) -> str:
        return self.__str__()


class AdapterError(Exception):
    """适配器基础错误"""
    pass


class AdapterInitializationError(AdapterError):
    """适配器初始化错误"""
    pass


class AdapterExecutionError(AdapterError):
    """适配器执行错误"""
    pass


class AdapterConfigurationError(AdapterError):
    """适配器配置错误"""
    pass


class AdapterHealthCheckError(AdapterError):
    """适配器健康检查错误"""
    pass
