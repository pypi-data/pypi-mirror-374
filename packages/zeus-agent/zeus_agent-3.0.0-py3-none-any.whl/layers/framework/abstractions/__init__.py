"""
Framework Abstractions
框架抽象层，提供核心抽象和接口
"""

from .agent import UniversalAgent, AgentCapability, AgentStatus
from .task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from .result import UniversalResult, ResultStatus, ResultType, ResultMetadata
from .context import UniversalContext
from .cognitive_agent import CognitiveUniversalAgent, AgentType, ModelConfig, ToolConfig, MemoryConfig, BehaviorConfig
from .agent_factory_manager import AgentFactoryManager
from .team import UniversalTeam, TeamConfig, TeamType, CommunicationPattern
from .a2a_protocol import A2AMessageType, A2ACapabilityType, A2AProtocolVersion, A2AMessage, A2AProtocolHandler
from .a2a_integration import A2AIntegrationManager, A2AAdapterBridge, A2AMessageRouter

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
    "ModelConfig",
    "ToolConfig",
    "MemoryConfig",
    "BehaviorConfig",
    
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