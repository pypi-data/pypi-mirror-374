"""
Framework Layer
框架层，提供核心抽象和接口
"""

from .abstractions.agent import UniversalAgent, AgentCapability, AgentStatus
from .abstractions.task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from .abstractions.result import UniversalResult, ResultStatus, ResultType, ResultMetadata
from .abstractions.context import UniversalContext
from .abstractions.cognitive_agent import CognitiveUniversalAgent, AgentType
from .abstractions.agent_factory_manager import AgentFactoryManager
from .abstractions.team import UniversalTeam, TeamConfig, TeamType, CommunicationPattern
from .abstractions.a2a_protocol import A2AMessageType, A2ACapabilityType, A2AProtocolVersion, A2AMessage, A2AProtocolHandler
from .abstractions.a2a_integration import A2AIntegrationManager, A2AAdapterBridge, A2AMessageRouter

__all__ = [
    # 基础抽象
    "UniversalAgent",
    "AgentCapability",
    "AgentStatus",
    "UniversalTask",
    "TaskType",
    "TaskPriority",
    "TaskRequirements",
    "UniversalContext",
    "UniversalResult",
    "ResultStatus",
    "ResultType",
    "ResultMetadata",
    
    # 认知抽象
    "CognitiveUniversalAgent",
    "AgentType",
    
    # 团队
    "UniversalTeam",
    "TeamType",
    "TeamConfig",
    "CommunicationPattern",
    
    # 工厂
    "AgentFactoryManager",
    
    # 协议
    "A2AMessageType",
    "A2ACapabilityType",
    "A2AProtocolVersion",
    "A2AMessage",
    "A2AProtocolHandler",
    
    # 集成
    "A2AIntegrationManager",
    "A2AAdapterBridge",
    "A2AMessageRouter",
]

__version__ = "3.0.0"
__author__ = "Agent Development Center Framework Team" 