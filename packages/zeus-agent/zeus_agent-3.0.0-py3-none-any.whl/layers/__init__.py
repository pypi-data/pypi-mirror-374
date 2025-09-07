"""
Layers Package
分层架构的实现
"""

# 基础抽象
from .framework.abstractions.agent import UniversalAgent, AgentCapability, AgentStatus
from .framework.abstractions.task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from .framework.abstractions.result import UniversalResult, ResultStatus, ResultType, ResultMetadata
from .framework.abstractions.context import UniversalContext

# 认知抽象
from .framework.abstractions.cognitive_agent import CognitiveUniversalAgent, AgentType
from .framework.abstractions.agent_factory_manager import AgentFactoryManager

# 团队
from .framework.abstractions.team import UniversalTeam, TeamConfig, TeamType, CommunicationPattern

# 协议
from .framework.abstractions.a2a_protocol import A2AMessageType, A2ACapabilityType, A2AProtocolVersion, A2AMessage, A2AProtocolHandler
from .framework.abstractions.a2a_integration import A2AIntegrationManager, A2AAdapterBridge, A2AMessageRouter

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
__author__ = "Agent Development Center Team" 