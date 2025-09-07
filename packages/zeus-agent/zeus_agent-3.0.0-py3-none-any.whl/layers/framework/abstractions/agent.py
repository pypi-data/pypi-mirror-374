"""
Universal Agent Abstraction
通用Agent抽象类，定义所有Agent框架的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class AgentCapability(Enum):
    """Agent能力枚举"""
    CONVERSATION = "conversation"
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATIONS = "file_operations"
    WEB_SEARCH = "web_search"
    TOOL_CALLING = "tool_calling"
    MULTIMODAL = "multimodal"
    PLANNING = "planning"
    REASONING = "reasoning"
    
    # 业务能力
    PROJECT_MANAGEMENT = "project_management"
    ARCHITECTURE_DESIGN = "architecture_design"
    UI_UX_DESIGN = "ui_ux_design"
    DEBUGGING = "debugging"
    TESTING = "testing"
    QUALITY_ASSURANCE = "quality_assurance"
    DATA_ANALYSIS = "data_analysis"
    VISUALIZATION = "visualization"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TEXT_PROCESSING = "text_processing"


class AgentStatus(Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentMetadata:
    """Agent元数据"""
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks


class UniversalAgent(ABC):
    """
    通用Agent抽象基类
    
    所有框架的Agent包装器都必须实现这个接口
    """
    
    def __init__(self, 
                 name: str,
                 description: str = "",
                 capabilities: List[AgentCapability] = None,
                 config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.metadata = AgentMetadata()
        
    @abstractmethod
    async def execute(self, task: 'UniversalTask', context: 'UniversalContext') -> 'UniversalResult':
        """
        执行任务
        
        Args:
            task: 要执行的任务
            context: 执行上下文
            
        Returns:
            UniversalResult: 执行结果
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取Agent的配置模式
        
        Returns:
            Dict: JSON Schema格式的配置模式
        """
        pass
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置Agent
        
        Args:
            config: 配置字典
        """
        pass
    
    def get_capabilities(self) -> List[AgentCapability]:
        """获取Agent能力列表"""
        return self.capabilities.copy()
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """检查是否具有指定能力"""
        return capability in self.capabilities
    
    def get_status(self) -> AgentStatus:
        """获取Agent状态"""
        return self.status
    
    def get_metadata(self) -> AgentMetadata:
        """获取Agent元数据"""
        return self.metadata
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "name": self.name,
            "status": self.status.value,
            "total_tasks": self.metadata.total_tasks,
            "successful_tasks": self.metadata.successful_tasks,
            "failed_tasks": self.metadata.failed_tasks,
            "success_rate": self.metadata.success_rate,
            "average_response_time": self.metadata.average_response_time,
            "capabilities": [cap.value for cap in self.capabilities],
            "last_active": self.metadata.last_active.isoformat() if self.metadata.last_active else None
        }
    
    def __str__(self) -> str:
        return f"UniversalAgent(name='{self.name}', status='{self.status.value}', capabilities={len(self.capabilities)})"
    
    def __repr__(self) -> str:
        return self.__str__() 