"""
认知架构层 - Cognitive Architecture Layer
提供Agent的认知能力：感知、推理、记忆、学习、通信
"""

# 认知Agent
from .cognitive_agent import (
    CognitiveAgent, CognitiveState, AgentIdentity, CognitiveMetrics,
    CognitiveMessageHandler
)

# 感知模块
from .perception import (
    PerceptionEngine, TextPerceptor, StructuredDataPerceptor,
    BasePerceptor, PerceptionResult, TextPerceptionResult,
    PerceptionType, SentimentType
)

# 推理模块
from .reasoning import (
    ReasoningEngine, LogicalReasoner, CausalReasoner,
    AnalogicalReasoner, InductiveReasoner, BaseReasoner,
    ReasoningResult, ReasoningStep, ReasoningType, ConfidenceLevel
)

# 记忆模块
from .memory import (
    MemorySystem, WorkingMemory, EpisodicMemory,
    SemanticMemory, ProceduralMemory, MemoryConsolidator,
    MemoryRetriever, ForgettingMechanism, MemoryType
)

# 学习模块
from .learning import (
    LearningModule, SupervisedLearning, UnsupervisedLearning,
    ReinforcementLearning, MetaLearning, ExperienceBuffer,
    PatternRecognizer, SkillAcquisition, LearningType, Experience, Skill
)

# 通信模块
from .communication import (
    CommunicationManager, MessageHandler, Message, MessageType,
    TeamProtocol, CommunicationChannel
)

# 层间通信管理器
from .communication_manager import (
    CognitiveCommunicationManager
)

__all__ = [
    # 认知Agent
    "CognitiveAgent", "CognitiveState", "AgentIdentity", "CognitiveMetrics",
    "CognitiveMessageHandler",
    
    # 感知模块
    "PerceptionEngine", "TextPerceptor", "StructuredDataPerceptor",
    "BasePerceptor", "PerceptionResult", "TextPerceptionResult",
    "PerceptionType", "SentimentType",
    
    # 推理模块
    "ReasoningEngine", "LogicalReasoner", "CausalReasoner",
    "AnalogicalReasoner", "InductiveReasoner", "BaseReasoner",
    "ReasoningResult", "ReasoningStep", "ReasoningType", "ConfidenceLevel",
    
    # 记忆模块
    "MemorySystem", "WorkingMemory", "EpisodicMemory",
    "SemanticMemory", "ProceduralMemory", "MemoryConsolidator",
    "MemoryRetriever", "ForgettingMechanism", "MemoryType",
    
    # 学习模块
    "LearningModule", "SupervisedLearning", "UnsupervisedLearning",
    "ReinforcementLearning", "MetaLearning", "ExperienceBuffer",
    "PatternRecognizer", "SkillAcquisition", "LearningType", "Experience", "Skill",
    
    # 通信模块
    "CommunicationManager", "MessageHandler", "Message", "MessageType",
    "TeamProtocol", "CommunicationChannel",
    
    # 层间通信管理器
    "CognitiveCommunicationManager"
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Cognitive Team" 