"""
KnowledgeBasedAgent基类
提供知识库驱动的Agent开发架构

设计理念：
- 知识库优先：80%的时间构建知识库，20%的时间写代码
- 声明式能力：通过装饰器声明Agent能力
- 智能增强：自动知识检索和上下文感知
- 可扩展性：支持多种知识源和AI后端
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .decorators import (
    CapabilityMetadata, KnowledgeEnhancementConfig, ContextAwarenessConfig,
    list_all_capabilities, get_method_capabilities
)
from ...intelligent_context.integrated_knowledge_service import IntegratedKnowledgeService
from ...intelligent_context.context_engineering import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class AgentRequest:
    """Agent请求"""
    content: str
    request_type: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResponse:
    """Agent响应"""
    content: str
    response_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    processing_time: float = 0.0
    knowledge_sources: List[str] = field(default_factory=list)
    capabilities_used: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    knowledge_base_path: Optional[str] = None
    ai_backend: str = "mock"
    enable_knowledge_enhancement: bool = True
    enable_context_awareness: bool = True
    enable_performance_monitoring: bool = True
    max_context_window: int = 4000
    default_confidence_threshold: float = 0.7


class KnowledgeBasedAgent(ABC):
    """
    知识库驱动的Agent基类
    
    提供：
    - 自动知识库集成
    - 装饰器驱动的能力管理
    - 上下文感知和记忆
    - 性能监控和优化
    - 可扩展的AI后端支持
    """
    
    def __init__(self, config: AgentConfig):
        """初始化知识库驱动的Agent"""
        self.config = config
        self.name = config.name
        self.version = config.version
        self.agent_id = f"{config.name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 知识服务
        self.knowledge_service: Optional[IntegratedKnowledgeService] = None
        self.context_manager: Optional[ContextManager] = None
        
        # 状态管理
        self.is_initialized = False
        self.capabilities: Dict[str, CapabilityMetadata] = {}
        self.performance_stats = {
            'requests_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'knowledge_retrieval_count': 0,
            'context_usage_count': 0
        }
        
        # 增强上下文（由装饰器注入）
        self.enhanced_context: Optional[List[Dict[str, Any]]] = None
        self.current_context: Optional[Dict[str, Any]] = None
        
        logger.info(f"🚀 创建知识库驱动Agent: {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化Agent"""
        if self.is_initialized:
            logger.warning(f"Agent {self.name} 已经初始化")
            return
        
        logger.info(f"🔧 初始化Agent: {self.name}")
        
        try:
            # 1. 初始化知识服务
            if self.config.enable_knowledge_enhancement:
                await self._initialize_knowledge_service()
            
            # 2. 初始化上下文管理
            if self.config.enable_context_awareness:
                await self._initialize_context_manager()
            
            # 3. 发现和注册能力
            await self._discover_capabilities()
            
            # 4. 加载知识库
            if self.config.knowledge_base_path:
                await self._load_knowledge_base()
            
            # 5. 执行自定义初始化
            await self._custom_initialize()
            
            self.is_initialized = True
            logger.info(f"✅ Agent初始化完成: {self.name} ({len(self.capabilities)} 个能力)")
            
        except Exception as e:
            logger.error(f"❌ Agent初始化失败: {e}")
            raise
    
    async def _initialize_knowledge_service(self):
        """初始化知识服务"""
        try:
            self.knowledge_service = IntegratedKnowledgeService()
            await self.knowledge_service.initialize()
            logger.info("✅ 知识服务初始化成功")
        except Exception as e:
            logger.error(f"❌ 知识服务初始化失败: {e}")
            raise
    
    async def _initialize_context_manager(self):
        """初始化上下文管理器"""
        try:
            self.context_manager = ContextManager()
            await self.context_manager.initialize()
            logger.info("✅ 上下文管理器初始化成功")
        except Exception as e:
            logger.error(f"❌ 上下文管理器初始化失败: {e}")
            raise
    
    async def _discover_capabilities(self):
        """发现和注册Agent能力"""
        logger.info("🔍 发现Agent能力...")
        
        # 获取类的所有方法
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            
            # 检查是否为能力方法
            if hasattr(attr, '_is_capability') and attr._is_capability:
                capability_metadata = attr._capability_metadata
                self.capabilities[capability_metadata.name] = capability_metadata
                logger.debug(f"📋 发现能力: {capability_metadata.name} ({capability_metadata.capability_type.value})")
        
        logger.info(f"✅ 能力发现完成，共 {len(self.capabilities)} 个能力")
    
    async def _load_knowledge_base(self):
        """加载知识库"""
        if not self.knowledge_service or not self.config.knowledge_base_path:
            return
        
        logger.info(f"📚 加载知识库: {self.config.knowledge_base_path}")
        
        try:
            knowledge_path = Path(self.config.knowledge_base_path)
            if knowledge_path.exists():
                # 加载知识库文件
                await self._load_knowledge_files(knowledge_path)
                logger.info("✅ 知识库加载完成")
            else:
                logger.warning(f"知识库路径不存在: {knowledge_path}")
        except Exception as e:
            logger.error(f"❌ 知识库加载失败: {e}")
    
    async def _load_knowledge_files(self, knowledge_path: Path):
        """加载知识库文件"""
        # 这里可以实现具体的知识库加载逻辑
        # 支持多种格式：markdown, yaml, json等
        pass
    
    @abstractmethod
    async def _custom_initialize(self):
        """自定义初始化逻辑（子类实现）"""
        pass
    
    async def process_request(self, request: Union[str, AgentRequest]) -> AgentResponse:
        """处理请求"""
        if not self.is_initialized:
            await self.initialize()
        
        # 标准化请求
        if isinstance(request, str):
            request = AgentRequest(content=request)
        
        start_time = datetime.now()
        logger.info(f"📨 处理请求: {request.content[:100]}...")
        
        try:
            # 更新统计信息
            self.performance_stats['requests_processed'] += 1
            
            # 处理请求
            response = await self._process_request_internal(request)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            
            # 更新性能统计
            self._update_performance_stats(processing_time)
            
            logger.info(f"✅ 请求处理完成 (耗时: {processing_time:.2f}s, 置信度: {response.confidence:.2f})")
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 请求处理失败 (耗时: {processing_time:.2f}s): {e}")
            
            return AgentResponse(
                content=f"处理请求时发生错误: {str(e)}",
                response_type="error",
                confidence=0.0,
                processing_time=processing_time
            )
    
    @abstractmethod
    async def _process_request_internal(self, request: AgentRequest) -> AgentResponse:
        """内部请求处理逻辑（子类实现）"""
        pass
    
    async def _retrieve_knowledge(self, query: str, config: KnowledgeEnhancementConfig) -> List[Dict[str, Any]]:
        """检索相关知识"""
        if not self.knowledge_service:
            return []
        
        try:
            logger.debug(f"🔍 检索知识: {query[:50]}...")
            
            results = await self.knowledge_service.search(
                query=query,
                top_k=config.retrieval_count,
                confidence_threshold=config.confidence_threshold
            )
            
            # 更新统计信息
            self.performance_stats['knowledge_retrieval_count'] += 1
            
            # 转换为标准格式
            knowledge_items = []
            for result in results:
                knowledge_items.append({
                    'content': result.content,
                    'metadata': result.metadata,
                    'score': result.score,
                    'source': 'knowledge_base'
                })
            
            logger.debug(f"💡 检索到 {len(knowledge_items)} 条知识")
            return knowledge_items
            
        except Exception as e:
            logger.error(f"❌ 知识检索失败: {e}")
            return []
    
    async def _load_context(self, config: ContextAwarenessConfig) -> Dict[str, Any]:
        """加载上下文"""
        if not self.context_manager:
            return {}
        
        try:
            context = {}
            
            # 加载对话历史
            if config.enable_conversation_history:
                history = await self.context_manager.get_conversation_history(
                    window_size=config.history_window_size
                )
                context['history'] = history
            
            # 加载任务上下文
            if config.enable_task_context:
                task_context = await self.context_manager.get_task_context()
                context['task'] = task_context
            
            # 更新统计信息
            self.performance_stats['context_usage_count'] += 1
            
            return context
            
        except Exception as e:
            logger.error(f"❌ 上下文加载失败: {e}")
            return {}
    
    async def _update_context(self, method_name: str, args: tuple, kwargs: dict, result: Any):
        """更新上下文"""
        if not self.context_manager:
            return
        
        try:
            await self.context_manager.update_context({
                'method': method_name,
                'args': str(args)[:200],  # 限制长度
                'kwargs': str(kwargs)[:200],
                'result': str(result)[:500],
                'timestamp': datetime.now()
            })
        except Exception as e:
            logger.error(f"❌ 上下文更新失败: {e}")
    
    def _update_performance_stats(self, processing_time: float):
        """更新性能统计"""
        self.performance_stats['total_processing_time'] += processing_time
        self.performance_stats['average_processing_time'] = (
            self.performance_stats['total_processing_time'] / 
            self.performance_stats['requests_processed']
        )
    
    def get_capabilities(self) -> Dict[str, CapabilityMetadata]:
        """获取Agent能力"""
        return self.capabilities.copy()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.performance_stats.copy()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            'name': self.name,
            'version': self.version,
            'agent_id': self.agent_id,
            'is_initialized': self.is_initialized,
            'capabilities_count': len(self.capabilities),
            'config': {
                'ai_backend': self.config.ai_backend,
                'enable_knowledge_enhancement': self.config.enable_knowledge_enhancement,
                'enable_context_awareness': self.config.enable_context_awareness,
                'max_context_window': self.config.max_context_window
            },
            'performance_stats': self.get_performance_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            'status': 'healthy',
            'agent_info': self.get_agent_info(),
            'services': {}
        }
        
        try:
            # 检查知识服务
            if self.knowledge_service:
                kb_health = await self.knowledge_service.health_check()
                health_status['services']['knowledge_service'] = kb_health
            
            # 检查上下文管理器
            if self.context_manager:
                context_health = await self.context_manager.health_check()
                health_status['services']['context_manager'] = context_health
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status
    
    async def cleanup(self):
        """清理资源"""
        logger.info(f"🧹 清理Agent资源: {self.name}")
        
        try:
            # 清理知识服务
            if self.knowledge_service:
                await self.knowledge_service.cleanup()
            
            # 清理上下文管理器
            if self.context_manager:
                await self.context_manager.cleanup()
            
            # 执行自定义清理
            await self._custom_cleanup()
            
            self.is_initialized = False
            logger.info(f"✅ Agent资源清理完成: {self.name}")
            
        except Exception as e:
            logger.error(f"❌ Agent资源清理失败: {e}")
    
    async def _custom_cleanup(self):
        """自定义清理逻辑（子类实现）"""
        pass
    
    def __repr__(self) -> str:
        return f"KnowledgeBasedAgent(name='{self.name}', version='{self.version}', capabilities={len(self.capabilities)})" 