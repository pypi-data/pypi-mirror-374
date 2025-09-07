"""
智能上下文层

提供智能上下文处理能力，包括：
- 智能上下文层核心组件
- 上下文工程
- 知识管理
- RAG系统（传统和Agentic）
- 质量控制
"""

from .intelligent_context_layer import IntelligentContextLayer, IntelligentContextResult, ProcessingMode, RAGProcessingMode
from .context_engineering import ContextEngineering, ContextEngineeringMode, ContextEngineeringStrategy, ContextTemplate, ContextRule
from .knowledge_management import KnowledgeManagement, KnowledgeItem, KnowledgeType, KnowledgeSource, KnowledgeStatus
from .rag_system import (
    RAGSystem, 
    RetrievalStrategy, 
    AugmentationMethod, 
    GenerationMode,
    RetrievalResult,
    AugmentationResult,
    GenerationResult,
    RAGMetrics
)

# Agentic RAG组件（可选导入，避免依赖问题）
try:
    from .agentic_rag_system import (
        AgenticRAGProcessor,
        ReflectionEngine,
        RAGPlanningEngine,
        QueryComplexity,
        ReflectionResult,
        RetrievalPlan,
        SimpleRetrievalPlan,
        MultiHopRetrievalPlan,
        CreativeRetrievalPlan,
        RAGContext,
        AgenticResponse
    )
    AGENTIC_RAG_AVAILABLE = True
except ImportError:
    AGENTIC_RAG_AVAILABLE = False
    # 创建占位符类，避免导入错误
    class AgenticRAGProcessor:
        def __init__(self, *args, **kwargs):
            raise ImportError("Agentic RAG系统不可用")
    
    class ReflectionEngine:
        def __init__(self, *args, **kwargs):
            raise ImportError("反思引擎不可用")
    
    class RAGPlanningEngine:
        def __init__(self, *args, **kwargs):
            raise ImportError("RAG规划引擎不可用")

from .quality_control import (
    QualityControl,
    QualityMetric,
    QualityLevel,
    QualityCheckType,
    QualityMetricResult,
    QualityAssessment
)

__all__ = [
    # 核心组件
    'IntelligentContextLayer',
    'IntelligentContextResult',
    'ProcessingMode',
    'RAGProcessingMode',  # 新增
    
    # 上下文工程
    'ContextEngineering',
    'ContextEngineeringMode',
    'ContextEngineeringStrategy',
    'ContextTemplate',
    'ContextRule',
    
    # 知识管理
    'KnowledgeManagement',
    'KnowledgeItem',
    'KnowledgeType',
    'KnowledgeSource',
    'KnowledgeStatus',
    
    # 传统RAG系统
    'RAGSystem',
    'RetrievalStrategy',
    'AugmentationMethod',
    'GenerationMode',
    'RetrievalResult',
    'AugmentationResult',
    'GenerationResult',
    'RAGMetrics',
    
    # Agentic RAG系统（如果可用）
    'AgenticRAGProcessor',
    'ReflectionEngine',
    'RAGPlanningEngine',
    'QueryComplexity',
    'ReflectionResult',
    'RetrievalPlan',
    'SimpleRetrievalPlan',
    'MultiHopRetrievalPlan',
    'CreativeRetrievalPlan',
    'RAGContext',
    'AgenticResponse',
    
    # 质量控制
    'QualityControl',
    'QualityMetric',
    'QualityLevel',
    'QualityCheckType',
    'QualityMetricResult',
    'QualityAssessment',
    
    # 可用性标志
    'AGENTIC_RAG_AVAILABLE'
]

__version__ = '2.0.0'  # 升级版本号以反映Agentic RAG支持 