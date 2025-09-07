"""
KnowledgeBasedAgent基类
基于Zeus平台的知识驱动Agent开发基类

核心理念：
- 继承CognitiveAgent，提供知识库驱动的开发模式
- 80%时间构建知识库，20%时间写代码
- 配置驱动初始化，装饰器能力注入
- 自动RAG集成和知识管理
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json
from datetime import datetime

from .cognitive_agent import CognitiveAgent, AgentIdentity
from ..intelligent_context.intelligent_context_layer import IntelligentContextLayer, RAGProcessingMode
from ..intelligent_context.vector_database_service import VectorDatabaseService
from ..intelligent_context.embedding_service import EmbeddingService
from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.task import UniversalTask, TaskType
from ..framework.abstractions.result import UniversalResult, ResultStatus, ErrorInfo
from ..infrastructure.llm.client_manager import llm_manager
from .self_learning_knowledge_manager import IntelligentKnowledgeEvolutionManager

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeConfig:
    """知识库配置"""
    knowledge_base_path: str
    vector_db_collection: str = "agent_knowledge"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    retrieval_top_k: int = 5
    confidence_threshold: float = 0.7
    enable_semantic_cache: bool = True


@dataclass 
class AgentCapability:
    """Agent能力定义"""
    name: str
    description: str
    method_name: str
    enabled: bool = True
    confidence_threshold: float = 0.7
    knowledge_sources: List[str] = field(default_factory=list)
    require_llm: bool = True


@dataclass
class KnowledgeBasedAgentConfig:
    """知识驱动Agent配置"""
    agent_name: str
    agent_description: str
    knowledge_config: KnowledgeConfig
    capabilities: List[AgentCapability] = field(default_factory=list)
    llm_config: Dict[str, Any] = field(default_factory=dict)
    performance_tracking: bool = True


class CapabilityDecorator:
    """能力装饰器工厂"""
    
    @staticmethod
    def capability(name: str, 
                  description: str,
                  knowledge_sources: List[str] = None,
                  confidence_threshold: float = 0.7,
                  require_llm: bool = True):
        """注册能力装饰器"""
        def decorator(func: Callable) -> Callable:
            # 将能力信息附加到函数
            func._capability_info = AgentCapability(
                name=name,
                description=description, 
                method_name=func.__name__,
                confidence_threshold=confidence_threshold,
                knowledge_sources=knowledge_sources or [],
                require_llm=require_llm
            )
            return func
        return decorator
    
    @staticmethod
    def knowledge_enhanced(sources: List[str] = None,
                          top_k: int = 5,
                          min_confidence: float = 0.7,
                          enable_learning: bool = True):
        """知识增强装饰器 - 支持自学习"""
        def decorator(func: Callable) -> Callable:
            async def wrapper(self, *args, **kwargs):
                query = kwargs.get('query', str(args[0]) if args else '')
                
                # 自动注入相关知识
                if hasattr(self, '_inject_knowledge'):
                    knowledge = await self._inject_knowledge(
                        query=query,
                        sources=sources,
                        top_k=top_k,
                        min_confidence=min_confidence
                    )
                    kwargs['injected_knowledge'] = knowledge
                
                # 执行原始方法
                result = await func(self, *args, **kwargs)
                
                # 自学习处理
                if (enable_learning and 
                    hasattr(self, 'knowledge_evolution_manager') and 
                    self.knowledge_evolution_manager and
                    hasattr(result, 'data') and 
                    result.data and
                    'answer' in result.data):
                    
                    # 启动知识演化流程
                    try:
                        response_id = await self.knowledge_evolution_manager.process_llm_response(
                            query=query,
                            llm_response=result.data['answer'],
                            user_context=kwargs.get('context', {})
                        )
                        
                        # 将response_id添加到结果中，供后续反馈使用
                        if not result.data:
                            result.data = {}
                        result.data['learning_response_id'] = response_id
                            
                    except Exception as e:
                        logger.warning(f"自学习处理失败: {e}")
                        import traceback
                        traceback.print_exc()
                
                return result
            
            # 保留原函数的元数据
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator
    
    @staticmethod
    def context_aware(save_context: bool = True):
        """上下文感知装饰器"""
        def decorator(func: Callable) -> Callable:
            async def wrapper(self, *args, **kwargs):
                # 注入上下文
                if hasattr(self, '_get_context'):
                    context = await self._get_context()
                    kwargs['context'] = context
                
                result = await func(self, *args, **kwargs)
                
                # 保存上下文
                if save_context and hasattr(self, '_save_context'):
                    await self._save_context(result)
                
                return result
            return wrapper
        return decorator


class KnowledgeBasedAgent(CognitiveAgent):
    """
    知识驱动Agent基类
    
    提供知识库驱动的Agent开发模式：
    1. 配置驱动初始化
    2. 自动知识库集成
    3. 装饰器能力注入
    4. 智能RAG检索
    """
    
    def __init__(self, config: KnowledgeBasedAgentConfig, llm_adapter=None):
        """初始化知识驱动Agent"""
        
        # 初始化认知Agent
        identity = AgentIdentity(
            agent_id=f"knowledge_agent_{config.agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=config.agent_name,
            role=config.agent_description,
            description=f"基于知识驱动的{config.agent_description}",
            expertise_domains=["knowledge_retrieval", "rag_processing"]
        )
        super().__init__(identity=identity, config={"llm_adapter": llm_adapter})
        
        self.config = config
        self.capabilities: Dict[str, AgentCapability] = {}
        self.knowledge_stats = {
            "knowledge_base_size": 0,
            "retrieval_count": 0,
            "cache_hit_rate": 0.0,
            "avg_confidence": 0.0
        }
        
        # 初始化知识组件
        self.vector_db = None
        self.embedding_service = None
        self.context_layer = None
        
        # 初始化自学习组件
        self.memory_system = None
        self.knowledge_evolution_manager = None
        self.integrated_knowledge_service = None
        
        logger.info(f"🧠 初始化知识驱动Agent: {config.agent_name}")
    
    async def initialize(self) -> UniversalResult:
        """初始化Agent和知识系统"""
        try:
            # 1. 初始化向量数据库
            self.vector_db = VectorDatabaseService(
                collection_name=self.config.knowledge_config.vector_db_collection
            )
            
            # 2. 初始化嵌入服务
            self.embedding_service = EmbeddingService()
            await self.embedding_service.initialize(
                model_name=self.config.knowledge_config.embedding_model
            )
            
            # 3. 初始化智能上下文层
            self.context_layer = IntelligentContextLayer()
            
            # 4. 初始化集成知识服务
            from ..intelligent_context.integrated_knowledge_service import IntegratedKnowledgeService
            self.integrated_knowledge_service = IntegratedKnowledgeService(
                vector_db_config={"collection_name": self.config.knowledge_config.vector_db_collection},
                embedding_config=None
            )
            
            # 5. 初始化记忆系统
            from .memory import MemorySystem
            memory_config = {
                "working": {"capacity": 7, "decay_time": 300},
                "episodic": {},
                "semantic": {},
                "procedural": {},
                "persistence": {
                    "database_path": "memory_database.db",
                    "persistence_mode": "batch",
                    "batch_size": 50
                }
            }
            self.memory_system = MemorySystem(memory_config)
            await self.memory_system.initialize()
            
            # 6. 初始化自学习知识演化管理器
            evolution_config = {
                "quality": {
                    "high_quality_threshold": 0.8,
                    "medium_quality_threshold": 0.6
                },
                "consolidation_interval": 1800,  # 30分钟
                "crystallization_interval": 3600  # 1小时
            }
            self.knowledge_evolution_manager = IntelligentKnowledgeEvolutionManager(
                memory_system=self.memory_system,
                knowledge_service=self.integrated_knowledge_service,
                config=evolution_config
            )
            
            # 7. 加载知识库
            await self._load_knowledge_base()
            
            # 8. 发现和注册能力
            self._discover_capabilities()
            
            # 9. 初始化LLM管理器（如果需要）
            if any(cap.require_llm for cap in self.capabilities.values()):
                await self._initialize_llm()
            
            logger.info(f"✅ {self.config.agent_name} 初始化完成")
            logger.info(f"📚 知识库大小: {self.knowledge_stats['knowledge_base_size']}")
            logger.info(f"🎯 注册能力: {list(self.capabilities.keys())}")
            
            return UniversalResult(
                data={"initialized_capabilities": list(self.capabilities.keys())},
                status=ResultStatus.SUCCESS,
                content="知识驱动Agent初始化成功"
            )
            
        except Exception as e:
            logger.error(f"❌ Agent初始化失败: {e}")
            return UniversalResult(
                content="Agent初始化失败",
                status=ResultStatus.FAILURE,
                error=ErrorInfo(
                    error_type="initialization_error",
                    error_message=str(e)
                )
            )
    
    async def _load_knowledge_base(self):
        """加载知识库到向量数据库"""
        knowledge_path = Path(self.config.knowledge_config.knowledge_base_path)
        
        if not knowledge_path.exists():
            logger.warning(f"知识库文件不存在: {knowledge_path}")
            return
        
        try:
            # 检查是否已加载
            current_count = self.vector_db.collection.count()
            if current_count > 0:
                logger.info(f"知识库已存在 {current_count} 个文档，跳过加载")
                self.knowledge_stats["knowledge_base_size"] = current_count
                return
            
            # 加载JSON格式知识库
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
            
            documents = []
            metadata_list = []
            
            # 处理不同格式的知识库
            if isinstance(knowledge_data, dict):
                if "documents" in knowledge_data:
                    # 标准格式
                    for doc in knowledge_data["documents"]:
                        content = doc.get("content", "")
                        if content:
                            documents.append(content)
                            metadata_list.append({
                                "source": doc.get("source", "unknown"),
                                "category": doc.get("category", "general"),
                                "title": doc.get("title", "")
                            })
                elif "knowledge_items" in knowledge_data:
                    # FPGA知识库格式
                    for item in knowledge_data["knowledge_items"]:
                        title = item.get("title", "")
                        if "chunks" in item:
                            for chunk in item["chunks"]:
                                content = chunk.get("content", "")
                                if content:
                                    documents.append(content)
                                    # ChromaDB metadata只支持基本类型，将列表转为字符串
                                    tags = item.get("tags", [])
                                    metadata_list.append({
                                        "source": item.get("domain", "unknown"),
                                        "category": item.get("knowledge_type", "general"),
                                        "title": title,
                                        "chunk_id": chunk.get("chunk_id", ""),
                                        "tags": ",".join(tags) if tags else ""
                            })
                else:
                    # 直接键值对格式
                    for key, value in knowledge_data.items():
                        if isinstance(value, str):
                            documents.append(value)
                            metadata_list.append({
                                "source": "knowledge_base",
                                "category": key,
                                "title": key
                            })
            
            if documents:
                # 批量生成嵌入
                embeddings = await self.embedding_service.embed_texts(documents)
                
                # 准备VectorDocument对象
                from layers.intelligent_context.vector_database_service import VectorDocument
                import uuid
                
                vector_docs = []
                for i, (content, metadata, emb) in enumerate(zip(documents, metadata_list, embeddings)):
                    vector_docs.append(VectorDocument(
                        id=str(uuid.uuid4()),
                        content=content,
                        embedding=emb.embedding,
                        metadata=metadata
                    ))
                
                # 添加到向量数据库
                await self.vector_db.add_documents(vector_docs)
                
                self.knowledge_stats["knowledge_base_size"] = len(documents)
                logger.info(f"✅ 已加载 {len(documents)} 个知识文档")
            
        except Exception as e:
            logger.error(f"❌ 知识库加载失败: {e}")
    
    def _discover_capabilities(self):
        """发现和注册Agent能力"""
        # 通过反射发现带有_capability_info的方法
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_capability_info'):
                capability = attr._capability_info
                self.capabilities[capability.name] = capability
                logger.info(f"🎯 发现能力: {capability.name}")
        
        # 从配置中添加额外能力
        for cap in self.config.capabilities:
            if cap.name not in self.capabilities:
                self.capabilities[cap.name] = cap
                logger.info(f"📋 配置能力: {cap.name}")
    
    async def _initialize_llm(self):
        """初始化LLM管理器"""
        try:
            # 如果llm_manager未初始化，则初始化
            if not hasattr(llm_manager, 'providers') or not llm_manager.providers:
                from ..infrastructure.llm import initialize_llm_manager
                await initialize_llm_manager()
                
            logger.info("✅ LLM管理器初始化完成")
            
        except Exception as e:
            logger.warning(f"⚠️ LLM初始化失败: {e}")
    
    async def _inject_knowledge(self, 
                              query: str,
                              sources: List[str] = None,
                              top_k: int = 5,
                              min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """注入相关知识"""
        try:
            # 生成查询嵌入
            query_embedding = await self.embedding_service.embed_text(query)
            
            # 检索相关文档
            filter_condition = None
            if sources:
                if isinstance(sources, list) and len(sources) == 1:
                    filter_condition = {"source": sources[0]}
                elif isinstance(sources, list):
                    filter_condition = {"source": {"$in": sources}}
                else:
                    filter_condition = {"source": sources}
            
            results = await self.vector_db.search(
                query=query,
                query_embedding=query_embedding.embedding,
                top_k=top_k,
                filters=filter_condition
            )
            
            logger.debug(f"🔍 原始搜索结果数量: {len(results)}")
            if results:
                scores = [r.score for r in results]
                logger.debug(f"🔍 相似度分数范围: {min(scores):.3f} - {max(scores):.3f}, 阈值: {min_confidence}")
            
            # 过滤低置信度结果
            filtered_results = [
                {
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "confidence": result.score
                }
                for result in results
                if result.score >= min_confidence
            ]
            
            self.knowledge_stats["retrieval_count"] += 1
            if filtered_results:
                avg_conf = sum(r["confidence"] for r in filtered_results) / len(filtered_results)
                self.knowledge_stats["avg_confidence"] = avg_conf
            
            logger.debug(f"🔍 为查询 '{query}' 检索到 {len(filtered_results)} 个相关知识")
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ 知识注入失败: {e}")
            return []
    
    async def _get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return {
            "agent_name": self.config.agent_name,
            "timestamp": datetime.now().isoformat(),
            "knowledge_stats": self.knowledge_stats,
            "available_capabilities": list(self.capabilities.keys())
        }
    
    async def _save_context(self, result: Any):
        """保存执行结果到上下文"""
        # 这里可以实现上下文保存逻辑
        pass
    
    async def route_capability(self, query: str, **kwargs) -> UniversalResult:
        """智能路由到合适的能力"""
        try:
            # 简单的关键词匹配路由（后续可以改进为LLM路由）
            best_capability = None
            best_score = 0.0
            
            query_lower = query.lower()
            
            for cap_name, capability in self.capabilities.items():
                if not capability.enabled:
                    continue
                    
                # 基于描述的关键词匹配（智能分词）
                desc_lower = capability.description.lower()
                
                # 简单有效的关键词匹配：直接检查关键词是否在文本中
                import re
                
                # 提取英文关键词
                desc_en_words = re.findall(r'[a-zA-Z]+', desc_lower)
                query_en_words = re.findall(r'[a-zA-Z]+', query_lower)
                
                # 计算匹配分数
                score = 0
                
                # 英文关键词匹配
                for word in query_en_words:
                    if word in desc_lower:
                        score += 2  # 英文匹配权重高
                
                for word in desc_en_words:
                    if word in query_lower:
                        score += 2
                
                # 中文关键词匹配（常见技术词汇）
                cn_keywords = ['设计', '编程', '语法', '分析', '约束', '时序']
                for keyword in cn_keywords:
                    if keyword in query_lower and keyword in desc_lower:
                        score += 1
                
                # 调试信息
                logger.info(f"🔍 能力匹配: {cap_name}")
                logger.info(f"   查询: '{query}' -> 英文词: {query_en_words}")
                logger.info(f"   描述: '{capability.description}' -> 英文词: {desc_en_words}")
                logger.info(f"   最终分数: {score}")
                
                if score > best_score:
                    best_score = score
                    best_capability = capability
            
            if best_capability and best_score > 0:
                # 调用对应的方法
                method = getattr(self, best_capability.method_name, None)
                if method:
                    logger.info(f"🎯 路由到能力: {best_capability.name}")
                    return await method(query, **kwargs)
            
            # 如果没有匹配的能力，使用默认处理
            return await self.default_capability_handler(query, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ 能力路由失败: {e}")
            return UniversalResult(
                content="能力路由失败",
                status=ResultStatus.FAILURE,
                error=ErrorInfo(
                    error_type="routing_error",
                    error_message=str(e)
                )
            )
    
    @abstractmethod
    async def default_capability_handler(self, query: str, **kwargs) -> UniversalResult:
        """默认能力处理器（子类必须实现）"""
        pass
    
    async def provide_feedback(self, response_id: str, feedback: Dict[str, Any]) -> UniversalResult:
        """提供用户反馈，推进知识演化"""
        if not self.knowledge_evolution_manager:
            return UniversalResult(
                content="自学习功能未启用",
                status=ResultStatus.FAILURE,
                error=ErrorInfo(
                    error_type="learning_not_enabled",
                    error_message="Knowledge evolution manager not initialized"
                )
            )
        
        return await self.knowledge_evolution_manager.collect_user_feedback(response_id, feedback)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        if not self.knowledge_evolution_manager:
            return {"learning_enabled": False}
        
        return {
            "learning_enabled": True,
            **self.knowledge_evolution_manager.get_evolution_metrics()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = {
            "knowledge_stats": self.knowledge_stats,
            "capabilities_count": len(self.capabilities),
            "enabled_capabilities": len([c for c in self.capabilities.values() if c.enabled]),
            "llm_required_capabilities": len([c for c in self.capabilities.values() if c.require_llm])
        }
        
        # 添加学习统计
        stats.update(self.get_learning_stats())
        
        return stats


# 导出装饰器到模块级别
capability = CapabilityDecorator.capability
knowledge_enhanced = CapabilityDecorator.knowledge_enhanced  
context_aware = CapabilityDecorator.context_aware 