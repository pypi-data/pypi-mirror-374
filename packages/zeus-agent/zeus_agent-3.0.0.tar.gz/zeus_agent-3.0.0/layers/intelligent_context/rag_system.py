"""
智能上下文层 - RAG系统组件

实现模块化RAG架构，包含：
- 检索模块 (Retrieval)
- 增强模块 (Augmentation) 
- 生成模块 (Generation)
- 反馈模块 (Feedback)
- 评估模块 (Evaluation)
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import logging
import hashlib
import json

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask

logger = logging.getLogger(__name__)

class RetrievalStrategy(Enum):
    """检索策略"""
    SEMANTIC = "semantic"           # 语义检索
    KEYWORD = "keyword"            # 关键词检索  
    HYBRID = "hybrid"              # 混合检索
    GRAPH = "graph"                # 图谱检索
    CONTEXTUAL = "contextual"      # 上下文感知检索

class AugmentationMethod(Enum):
    """增强方法"""
    CONCATENATION = "concatenation"  # 简单拼接
    INTEGRATION = "integration"      # 智能整合
    SUMMARIZATION = "summarization"  # 摘要增强
    FILTERING = "filtering"          # 过滤增强
    RANKING = "ranking"              # 排序增强

class GenerationMode(Enum):
    """生成模式"""
    DIRECT = "direct"               # 直接生成
    GUIDED = "guided"              # 引导生成
    ITERATIVE = "iterative"        # 迭代生成
    MULTI_STEP = "multi_step"      # 多步生成

@dataclass
class RetrievalResult:
    """检索结果"""
    documents: List[Dict[str, Any]] = field(default_factory=list)
    scores: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    retrieval_time: float = 0.0
    strategy_used: RetrievalStrategy = RetrievalStrategy.SEMANTIC

@dataclass
class AugmentationResult:
    """增强结果"""
    augmented_context: str = ""
    source_documents: List[Dict[str, Any]] = field(default_factory=list)
    augmentation_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    method_used: AugmentationMethod = AugmentationMethod.INTEGRATION

@dataclass
class GenerationResult:
    """生成结果"""
    generated_content: str = ""
    confidence_score: float = 0.0
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    mode_used: GenerationMode = GenerationMode.GUIDED

@dataclass
class RAGMetrics:
    """RAG系统指标"""
    retrieval_precision: float = 0.0    # 检索精确率
    retrieval_recall: float = 0.0       # 检索召回率
    augmentation_quality: float = 0.0   # 增强质量
    generation_relevance: float = 0.0   # 生成相关性
    end_to_end_latency: float = 0.0    # 端到端延迟
    token_efficiency: float = 0.0       # Token效率
    user_satisfaction: float = 0.0      # 用户满意度

class RAGSystem:
    """
    RAG系统核心组件
    
    实现完整的检索增强生成流程：
    1. 智能检索 - 多策略文档检索
    2. 上下文增强 - 智能整合检索结果
    3. 质量控制 - 确保生成质量
    4. 反馈学习 - 持续优化
    5. 性能评估 - 全面指标监控
    """
    
    def __init__(self):
        # 模拟的知识库 - 在实际实现中应该连接真实的向量数据库
        self.knowledge_base = {
            "documents": [],
            "embeddings": {},
            "metadata": {},
            "index": {}
        }
        
        # RAG历史记录
        self.rag_history: List[Dict[str, Any]] = []
        self.metrics_history: List[RAGMetrics] = []
        
        # 配置参数
        self.config = {
            "max_retrieved_docs": 5,
            "relevance_threshold": 0.3,
            "max_context_length": 2000,
            "enable_reranking": True,
            "enable_feedback_learning": True
        }
        
    async def enhance_with_rag(self, 
                              context: UniversalContext, 
                              task: UniversalTask,
                              retrieval_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID) -> UniversalContext:
        """
        使用RAG增强上下文
        
        Args:
            context: 原始上下文
            task: 相关任务
            retrieval_strategy: 检索策略
            
        Returns:
            RAG增强后的上下文
        """
        try:
            start_time = datetime.now()
            
            # 1. 检索阶段
            retrieval_result = await self._retrieve_documents(task, context, retrieval_strategy)
            
            # 2. 增强阶段
            augmentation_result = await self._augment_context(
                context, retrieval_result, AugmentationMethod.INTEGRATION
            )
            
            # 3. 质量控制
            quality_score = await self._assess_rag_quality(augmentation_result, task)
            
            # 4. 如果质量不够，尝试其他策略
            if quality_score < 0.6:
                # 尝试不同的检索策略
                alternative_strategy = self._get_alternative_strategy(retrieval_strategy)
                retrieval_result = await self._retrieve_documents(task, context, alternative_strategy)
                augmentation_result = await self._augment_context(
                    context, retrieval_result, AugmentationMethod.FILTERING
                )
                quality_score = await self._assess_rag_quality(augmentation_result, task)
            
            # 5. 创建增强后的上下文
            enhanced_context = await self._create_enhanced_context(
                context, augmentation_result, retrieval_result
            )
            
            # 6. 记录指标
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            rag_metrics = RAGMetrics(
                retrieval_precision=self._calculate_retrieval_precision(retrieval_result),
                retrieval_recall=self._calculate_retrieval_recall(retrieval_result),
                augmentation_quality=quality_score,
                generation_relevance=await self._assess_generation_relevance(enhanced_context, task),
                end_to_end_latency=processing_time,
                token_efficiency=self._calculate_token_efficiency(context, enhanced_context),
                user_satisfaction=0.8  # 默认值，实际应该从反馈中获取
            )
            
            # 7. 保存历史记录
            self.rag_history.append({
                'timestamp': end_time.isoformat(),
                'task_id': getattr(task, 'id', 'unknown'),
                'strategy_used': retrieval_strategy.value,
                'quality_score': quality_score,
                'processing_time': processing_time,
                'documents_retrieved': len(retrieval_result.documents)
            })
            self.metrics_history.append(rag_metrics)
            
            # 8. 添加RAG元数据到上下文
            enhanced_context.set('rag_metadata', {
                'strategy_used': retrieval_strategy.value,
                'documents_count': len(retrieval_result.documents),
                'quality_score': quality_score,
                'processing_time': processing_time,
                'retrieval_scores': retrieval_result.scores,
                'augmentation_method': augmentation_result.method_used.value,
                'metrics': {
                    'precision': rag_metrics.retrieval_precision,
                    'recall': rag_metrics.retrieval_recall,
                    'relevance': rag_metrics.generation_relevance,
                    'efficiency': rag_metrics.token_efficiency
                }
            })
            
            logger.info(f"RAG enhancement completed with strategy {retrieval_strategy.value}, "
                       f"quality score: {quality_score:.2f}, docs retrieved: {len(retrieval_result.documents)}")
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"RAG enhancement failed: {str(e)}")
            # 返回原始上下文作为fallback
            return context
    
    async def _retrieve_documents(self, 
                                task: UniversalTask, 
                                context: UniversalContext,
                                strategy: RetrievalStrategy) -> RetrievalResult:
        """文档检索"""
        start_time = datetime.now()
        
        # 构建查询
        query = await self._build_retrieval_query(task, context)
        
        # 根据策略执行检索
        if strategy == RetrievalStrategy.SEMANTIC:
            documents, scores = await self._semantic_retrieval(query)
        elif strategy == RetrievalStrategy.KEYWORD:
            documents, scores = await self._keyword_retrieval(query)
        elif strategy == RetrievalStrategy.HYBRID:
            documents, scores = await self._hybrid_retrieval(query)
        elif strategy == RetrievalStrategy.GRAPH:
            documents, scores = await self._graph_retrieval(query, context)
        elif strategy == RetrievalStrategy.CONTEXTUAL:
            documents, scores = await self._contextual_retrieval(query, context)
        else:
            documents, scores = await self._semantic_retrieval(query)
        
        # 重排序
        if self.config["enable_reranking"] and len(documents) > 1:
            documents, scores = await self._rerank_documents(documents, scores, query, task)
        
        # 过滤低分文档
        filtered_docs, filtered_scores = self._filter_by_relevance(
            documents, scores, self.config["relevance_threshold"]
        )
        
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        return RetrievalResult(
            documents=filtered_docs[:self.config["max_retrieved_docs"]],
            scores=filtered_scores[:self.config["max_retrieved_docs"]],
            metadata={
                'query': query,
                'total_candidates': len(documents),
                'filtered_count': len(filtered_docs)
            },
            retrieval_time=retrieval_time,
            strategy_used=strategy
        )
    
    async def _build_retrieval_query(self, task: UniversalTask, context: UniversalContext) -> str:
        """构建检索查询"""
        query_parts = []
        
        # 从任务内容提取查询
        if hasattr(task, 'content') and task.content:
            query_parts.append(task.content)
        
        # 从上下文提取关键信息
        context_data = context.get_all() if hasattr(context, 'get_all') else {}
        
        # 提取关键词
        for key in ['keywords', 'topics', 'focus_areas']:
            if key in context_data:
                value = context_data[key]
                if isinstance(value, list):
                    query_parts.extend(value)
                else:
                    query_parts.append(str(value))
        
        # 从历史对话中提取相关信息
        if 'history' in context_data:
            history = context_data['history']
            if isinstance(history, list) and history:
                # 取最近的对话内容
                recent_history = history[-2:] if len(history) > 2 else history
                for item in recent_history:
                    if isinstance(item, dict) and 'content' in item:
                        query_parts.append(item['content'])
        
        # 构建最终查询
        query = " ".join(str(part) for part in query_parts if part)
        
        # 限制查询长度
        if len(query) > 200:
            query = query[:200] + "..."
        
        return query if query.strip() else "general information"
    
    async def _semantic_retrieval(self, query: str) -> Tuple[List[Dict], List[float]]:
        """语义检索"""
        # 模拟语义检索 - 在实际实现中应该使用向量数据库
        mock_documents = [
            {
                "id": "doc_1",
                "title": "Agent Development Best Practices",
                "content": "This document covers best practices for developing AI agents, including architecture design, testing strategies, and deployment considerations.",
                "metadata": {"type": "guide", "category": "development"}
            },
            {
                "id": "doc_2", 
                "title": "Context Engineering Principles",
                "content": "Context engineering is crucial for effective agent performance. This includes proper context window management, information prioritization, and failure mode detection.",
                "metadata": {"type": "technical", "category": "context"}
            },
            {
                "id": "doc_3",
                "title": "RAG System Implementation",
                "content": "Retrieval-Augmented Generation systems combine the power of large language models with external knowledge sources for enhanced accuracy and relevance.",
                "metadata": {"type": "implementation", "category": "rag"}
            },
            {
                "id": "doc_4",
                "title": "Multi-Agent Collaboration Patterns",
                "content": "Various collaboration patterns exist for multi-agent systems, including sequential, parallel, hierarchical, and consensus-based approaches.",
                "metadata": {"type": "pattern", "category": "collaboration"}
            },
            {
                "id": "doc_5",
                "title": "Performance Optimization Techniques",
                "content": "Optimizing agent performance involves careful attention to context management, caching strategies, and efficient resource utilization.",
                "metadata": {"type": "optimization", "category": "performance"}
            }
        ]
        
        # 简单的相似度计算 - 基于关键词匹配
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in mock_documents:
            doc_text = (doc["title"] + " " + doc["content"]).lower()
            doc_words = set(doc_text.split())
            
            # 计算Jaccard相似度
            intersection = len(query_words.intersection(doc_words))
            union = len(query_words.union(doc_words))
            similarity = intersection / union if union > 0 else 0.0
            
            # 添加一些随机性来模拟真实的语义相似度
            import random
            similarity += random.uniform(-0.1, 0.1)
            similarity = max(0.0, min(1.0, similarity))
            
            scored_docs.append((doc, similarity))
        
        # 按相似度排序
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        documents = [doc for doc, _ in scored_docs]
        scores = [score for _, score in scored_docs]
        
        return documents, scores
    
    async def _keyword_retrieval(self, query: str) -> Tuple[List[Dict], List[float]]:
        """关键词检索"""
        # 使用语义检索的结果，但调整评分逻辑
        documents, _ = await self._semantic_retrieval(query)
        
        # 重新计算基于关键词匹配的分数
        query_keywords = query.lower().split()
        scores = []
        
        for doc in documents:
            doc_text = (doc["title"] + " " + doc["content"]).lower()
            
            # 计算关键词匹配分数
            matches = sum(1 for keyword in query_keywords if keyword in doc_text)
            score = matches / len(query_keywords) if query_keywords else 0.0
            scores.append(score)
        
        return documents, scores
    
    async def _hybrid_retrieval(self, query: str) -> Tuple[List[Dict], List[float]]:
        """混合检索 - 结合语义和关键词检索"""
        # 获取语义检索结果
        semantic_docs, semantic_scores = await self._semantic_retrieval(query)
        
        # 获取关键词检索结果
        keyword_docs, keyword_scores = await self._keyword_retrieval(query)
        
        # 合并和重新评分
        doc_scores = {}
        
        # 语义检索权重 0.6
        for i, doc in enumerate(semantic_docs):
            doc_id = doc["id"]
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + semantic_scores[i] * 0.6
        
        # 关键词检索权重 0.4
        for i, doc in enumerate(keyword_docs):
            doc_id = doc["id"]
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + keyword_scores[i] * 0.4
        
        # 创建文档索引
        all_docs = {doc["id"]: doc for doc in semantic_docs + keyword_docs}
        
        # 按分数排序
        sorted_items = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        documents = [all_docs[doc_id] for doc_id, _ in sorted_items]
        scores = [score for _, score in sorted_items]
        
        return documents, scores
    
    async def _graph_retrieval(self, query: str, context: UniversalContext) -> Tuple[List[Dict], List[float]]:
        """图谱检索"""
        # 模拟基于知识图谱的检索
        # 在实际实现中，这里会连接到知识图谱数据库
        
        # 先进行语义检索作为基础
        documents, base_scores = await self._semantic_retrieval(query)
        
        # 基于图谱关系调整分数
        enhanced_scores = []
        for i, doc in enumerate(documents):
            base_score = base_scores[i]
            
            # 模拟图谱增强：如果文档类型与查询相关，提高分数
            doc_category = doc.get("metadata", {}).get("category", "")
            
            # 简单的类别相关性提升
            if "context" in query.lower() and doc_category == "context":
                base_score += 0.2
            elif "rag" in query.lower() and doc_category == "rag":
                base_score += 0.2
            elif "agent" in query.lower() and doc_category == "development":
                base_score += 0.15
            
            enhanced_scores.append(min(base_score, 1.0))
        
        return documents, enhanced_scores
    
    async def _contextual_retrieval(self, query: str, context: UniversalContext) -> Tuple[List[Dict], List[float]]:
        """上下文感知检索"""
        # 基于上下文信息增强检索
        documents, base_scores = await self._semantic_retrieval(query)
        
        # 从上下文中提取额外信息
        context_data = context.get_all() if hasattr(context, 'get_all') else {}
        
        # 上下文关键词
        context_keywords = set()
        for key in ['keywords', 'topics', 'previous_queries']:
            if key in context_data:
                value = context_data[key]
                if isinstance(value, list):
                    context_keywords.update(str(v).lower() for v in value)
                else:
                    context_keywords.update(str(value).lower().split())
        
        # 基于上下文调整分数
        contextual_scores = []
        for i, doc in enumerate(documents):
            base_score = base_scores[i]
            
            # 检查文档是否包含上下文关键词
            doc_text = (doc["title"] + " " + doc["content"]).lower()
            context_matches = sum(1 for keyword in context_keywords if keyword in doc_text)
            
            if context_keywords:
                context_boost = (context_matches / len(context_keywords)) * 0.3
                base_score += context_boost
            
            contextual_scores.append(min(base_score, 1.0))
        
        return documents, contextual_scores
    
    async def _rerank_documents(self, 
                              documents: List[Dict], 
                              scores: List[float],
                              query: str,
                              task: UniversalTask) -> Tuple[List[Dict], List[float]]:
        """文档重排序"""
        if len(documents) <= 1:
            return documents, scores
        
        # 重排序因子
        rerank_scores = []
        
        for i, doc in enumerate(documents):
            original_score = scores[i]
            
            # 因子1: 文档长度适中性 (太短或太长都不好)
            content_length = len(doc.get("content", ""))
            length_factor = 1.0
            if content_length < 50:
                length_factor = 0.7
            elif content_length > 1000:
                length_factor = 0.8
            
            # 因子2: 文档类型相关性
            doc_type = doc.get("metadata", {}).get("type", "")
            task_type = getattr(task, 'task_type', None)
            type_factor = 1.0
            
            if task_type and hasattr(task_type, 'name'):
                if task_type.name == 'CODE_GENERATION' and doc_type == 'implementation':
                    type_factor = 1.2
                elif task_type.name == 'ANALYSIS' and doc_type == 'technical':
                    type_factor = 1.1
                elif task_type.name == 'PLANNING' and doc_type == 'guide':
                    type_factor = 1.15
            
            # 因子3: 新近性 (模拟)
            freshness_factor = 1.0  # 在实际实现中基于文档时间戳
            
            # 计算最终重排序分数
            rerank_score = original_score * length_factor * type_factor * freshness_factor
            rerank_scores.append(rerank_score)
        
        # 重新排序
        sorted_pairs = sorted(zip(documents, rerank_scores), key=lambda x: x[1], reverse=True)
        reranked_docs = [doc for doc, _ in sorted_pairs]
        reranked_scores = [score for _, score in sorted_pairs]
        
        return reranked_docs, reranked_scores
    
    def _filter_by_relevance(self, 
                           documents: List[Dict], 
                           scores: List[float], 
                           threshold: float) -> Tuple[List[Dict], List[float]]:
        """按相关性过滤文档"""
        filtered_docs = []
        filtered_scores = []
        
        for doc, score in zip(documents, scores):
            if score >= threshold:
                filtered_docs.append(doc)
                filtered_scores.append(score)
        
        return filtered_docs, filtered_scores
    
    async def _augment_context(self, 
                             context: UniversalContext,
                             retrieval_result: RetrievalResult,
                             method: AugmentationMethod) -> AugmentationResult:
        """上下文增强"""
        if method == AugmentationMethod.CONCATENATION:
            return await self._concatenation_augmentation(context, retrieval_result)
        elif method == AugmentationMethod.INTEGRATION:
            return await self._integration_augmentation(context, retrieval_result)
        elif method == AugmentationMethod.SUMMARIZATION:
            return await self._summarization_augmentation(context, retrieval_result)
        elif method == AugmentationMethod.FILTERING:
            return await self._filtering_augmentation(context, retrieval_result)
        elif method == AugmentationMethod.RANKING:
            return await self._ranking_augmentation(context, retrieval_result)
        else:
            return await self._integration_augmentation(context, retrieval_result)
    
    async def _concatenation_augmentation(self, 
                                        context: UniversalContext,
                                        retrieval_result: RetrievalResult) -> AugmentationResult:
        """简单拼接增强"""
        augmented_parts = []
        
        # 添加检索到的文档
        for i, doc in enumerate(retrieval_result.documents):
            score = retrieval_result.scores[i] if i < len(retrieval_result.scores) else 0.0
            doc_text = f"[Document {i+1} (relevance: {score:.2f})]:\n{doc.get('title', 'Untitled')}\n{doc.get('content', '')}\n"
            augmented_parts.append(doc_text)
        
        augmented_context = "\n\n".join(augmented_parts)
        
        # 限制长度
        if len(augmented_context) > self.config["max_context_length"]:
            augmented_context = augmented_context[:self.config["max_context_length"]] + "..."
        
        return AugmentationResult(
            augmented_context=augmented_context,
            source_documents=retrieval_result.documents,
            augmentation_metadata={
                'method': 'concatenation',
                'total_length': len(augmented_context),
                'documents_used': len(retrieval_result.documents)
            },
            quality_score=0.7,  # 基础质量分数
            method_used=AugmentationMethod.CONCATENATION
        )
    
    async def _integration_augmentation(self, 
                                      context: UniversalContext,
                                      retrieval_result: RetrievalResult) -> AugmentationResult:
        """智能整合增强"""
        # 按主题分组文档
        topic_groups = self._group_documents_by_topic(retrieval_result.documents)
        
        augmented_parts = []
        
        for topic, docs in topic_groups.items():
            if not docs:
                continue
            
            # 为每个主题创建整合的描述
            topic_content = []
            for doc in docs:
                # 提取关键信息
                title = doc.get('title', '')
                content = doc.get('content', '')
                
                # 简化内容提取
                key_sentences = self._extract_key_sentences(content, 2)
                topic_content.extend(key_sentences)
            
            if topic_content:
                integrated_content = f"## {topic}\n" + "\n".join(f"- {sentence}" for sentence in topic_content)
                augmented_parts.append(integrated_content)
        
        augmented_context = "\n\n".join(augmented_parts)
        
        # 限制长度
        if len(augmented_context) > self.config["max_context_length"]:
            augmented_context = augmented_context[:self.config["max_context_length"]] + "..."
        
        return AugmentationResult(
            augmented_context=augmented_context,
            source_documents=retrieval_result.documents,
            augmentation_metadata={
                'method': 'integration',
                'topics_identified': list(topic_groups.keys()),
                'total_length': len(augmented_context),
                'integration_quality': 0.85
            },
            quality_score=0.85,
            method_used=AugmentationMethod.INTEGRATION
        )
    
    async def _summarization_augmentation(self, 
                                        context: UniversalContext,
                                        retrieval_result: RetrievalResult) -> AugmentationResult:
        """摘要增强"""
        summaries = []
        
        for i, doc in enumerate(retrieval_result.documents):
            title = doc.get('title', f'Document {i+1}')
            content = doc.get('content', '')
            score = retrieval_result.scores[i] if i < len(retrieval_result.scores) else 0.0
            
            # 简单的摘要提取 - 取前两句
            sentences = content.split('.')[:2]
            summary = '. '.join(sentence.strip() for sentence in sentences if sentence.strip())
            
            if summary:
                summaries.append(f"**{title}** (relevance: {score:.2f}): {summary}")
        
        augmented_context = "\n\n".join(summaries)
        
        return AugmentationResult(
            augmented_context=augmented_context,
            source_documents=retrieval_result.documents,
            augmentation_metadata={
                'method': 'summarization',
                'summaries_created': len(summaries),
                'compression_ratio': len(augmented_context) / sum(len(doc.get('content', '')) for doc in retrieval_result.documents) if retrieval_result.documents else 1.0
            },
            quality_score=0.75,
            method_used=AugmentationMethod.SUMMARIZATION
        )
    
    async def _filtering_augmentation(self, 
                                    context: UniversalContext,
                                    retrieval_result: RetrievalResult) -> AugmentationResult:
        """过滤增强 - 只保留最相关的信息"""
        # 只保留高分文档
        high_score_threshold = 0.5
        filtered_docs = []
        filtered_scores = []
        
        for i, doc in enumerate(retrieval_result.documents):
            score = retrieval_result.scores[i] if i < len(retrieval_result.scores) else 0.0
            if score >= high_score_threshold:
                filtered_docs.append(doc)
                filtered_scores.append(score)
        
        # 如果过滤后没有文档，降低阈值
        if not filtered_docs and retrieval_result.documents:
            filtered_docs = retrieval_result.documents[:2]  # 至少保留前两个
            filtered_scores = retrieval_result.scores[:2]
        
        # 创建过滤后的检索结果
        filtered_retrieval = RetrievalResult(
            documents=filtered_docs,
            scores=filtered_scores,
            metadata=retrieval_result.metadata,
            retrieval_time=retrieval_result.retrieval_time,
            strategy_used=retrieval_result.strategy_used
        )
        
        # 使用整合方法处理过滤后的文档
        return await self._integration_augmentation(context, filtered_retrieval)
    
    async def _ranking_augmentation(self, 
                                  context: UniversalContext,
                                  retrieval_result: RetrievalResult) -> AugmentationResult:
        """排序增强 - 按重要性排序呈现"""
        # 重新排序文档
        scored_docs = list(zip(retrieval_result.documents, retrieval_result.scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        augmented_parts = []
        
        for rank, (doc, score) in enumerate(scored_docs, 1):
            title = doc.get('title', f'Document {rank}')
            content = doc.get('content', '')
            
            # 根据排名调整展示详细程度
            if rank <= 2:
                # 前两名显示完整内容
                doc_text = f"#{rank} **{title}** (score: {score:.2f})\n{content}"
            else:
                # 其他显示摘要
                sentences = content.split('.')[:1]  # 只显示第一句
                summary = sentences[0].strip() if sentences and sentences[0].strip() else content[:100]
                doc_text = f"#{rank} **{title}** (score: {score:.2f}): {summary}"
            
            augmented_parts.append(doc_text)
        
        augmented_context = "\n\n".join(augmented_parts)
        
        # 限制长度
        if len(augmented_context) > self.config["max_context_length"]:
            augmented_context = augmented_context[:self.config["max_context_length"]] + "..."
        
        return AugmentationResult(
            augmented_context=augmented_context,
            source_documents=retrieval_result.documents,
            augmentation_metadata={
                'method': 'ranking',
                'ranking_applied': True,
                'detailed_items': min(2, len(scored_docs)),
                'summary_items': max(0, len(scored_docs) - 2)
            },
            quality_score=0.8,
            method_used=AugmentationMethod.RANKING
        )
    
    def _group_documents_by_topic(self, documents: List[Dict]) -> Dict[str, List[Dict]]:
        """按主题分组文档"""
        topic_groups = {}
        
        for doc in documents:
            # 从元数据中获取类别作为主题
            topic = doc.get('metadata', {}).get('category', 'General')
            
            if topic not in topic_groups:
                topic_groups[topic] = []
            
            topic_groups[topic].append(doc)
        
        return topic_groups
    
    def _extract_key_sentences(self, text: str, max_sentences: int = 2) -> List[str]:
        """提取关键句子"""
        if not text:
            return []
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # 简单启发式：选择较长的句子作为关键句子
        sentences.sort(key=len, reverse=True)
        
        return sentences[:max_sentences]
    
    async def _assess_rag_quality(self, augmentation_result: AugmentationResult, task: UniversalTask) -> float:
        """评估RAG质量"""
        quality_factors = []
        
        # 因子1: 内容相关性
        task_content = getattr(task, 'content', '').lower()
        augmented_content = augmentation_result.augmented_context.lower()
        
        if task_content and augmented_content:
            task_words = set(task_content.split())
            aug_words = set(augmented_content.split())
            overlap = len(task_words.intersection(aug_words))
            relevance = min(overlap / max(len(task_words), 1), 1.0)
            quality_factors.append(relevance)
        
        # 因子2: 内容丰富度
        content_richness = min(len(augmentation_result.augmented_context) / 500, 1.0)
        quality_factors.append(content_richness)
        
        # 因子3: 源文档质量
        if augmentation_result.source_documents:
            avg_doc_length = sum(len(doc.get('content', '')) for doc in augmentation_result.source_documents) / len(augmentation_result.source_documents)
            doc_quality = min(avg_doc_length / 200, 1.0)
            quality_factors.append(doc_quality)
        
        # 因子4: 方法适用性
        method_quality = {
            AugmentationMethod.CONCATENATION: 0.6,
            AugmentationMethod.INTEGRATION: 0.9,
            AugmentationMethod.SUMMARIZATION: 0.75,
            AugmentationMethod.FILTERING: 0.8,
            AugmentationMethod.RANKING: 0.85
        }.get(augmentation_result.method_used, 0.7)
        quality_factors.append(method_quality)
        
        # 综合评分
        if not quality_factors:
            return 0.5
        
        return sum(quality_factors) / len(quality_factors)
    
    def _get_alternative_strategy(self, current_strategy: RetrievalStrategy) -> RetrievalStrategy:
        """获取替代检索策略"""
        alternatives = {
            RetrievalStrategy.SEMANTIC: RetrievalStrategy.HYBRID,
            RetrievalStrategy.KEYWORD: RetrievalStrategy.SEMANTIC,
            RetrievalStrategy.HYBRID: RetrievalStrategy.CONTEXTUAL,
            RetrievalStrategy.GRAPH: RetrievalStrategy.SEMANTIC,
            RetrievalStrategy.CONTEXTUAL: RetrievalStrategy.HYBRID
        }
        
        return alternatives.get(current_strategy, RetrievalStrategy.SEMANTIC)
    
    async def _create_enhanced_context(self, 
                                     original_context: UniversalContext,
                                     augmentation_result: AugmentationResult,
                                     retrieval_result: RetrievalResult) -> UniversalContext:
        """创建增强后的上下文"""
        # 获取原始上下文数据
        original_data = original_context.get_all() if hasattr(original_context, 'get_all') else {}
        
        # 创建增强后的上下文
        enhanced_data = original_data.copy()
        enhanced_data.update({
            'rag_enhanced_content': augmentation_result.augmented_context,
            'retrieved_documents': [
                {
                    'id': doc.get('id', f'doc_{i}'),
                    'title': doc.get('title', ''),
                    'content_preview': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                    'metadata': doc.get('metadata', {}),
                    'relevance_score': retrieval_result.scores[i] if i < len(retrieval_result.scores) else 0.0
                }
                for i, doc in enumerate(retrieval_result.documents)
            ],
            'rag_processing_info': {
                'retrieval_strategy': retrieval_result.strategy_used.value,
                'augmentation_method': augmentation_result.method_used.value,
                'quality_score': augmentation_result.quality_score,
                'retrieval_time': retrieval_result.retrieval_time,
                'documents_count': len(retrieval_result.documents)
            }
        })
        
        enhanced_context = UniversalContext(enhanced_data)
        
        # 保持原始上下文ID
        if 'context_id' in original_data:
            enhanced_context.set('context_id', original_data['context_id'])
        
        return enhanced_context
    
    # 指标计算方法
    def _calculate_retrieval_precision(self, retrieval_result: RetrievalResult) -> float:
        """计算检索精确率"""
        if not retrieval_result.documents:
            return 0.0
        
        # 简化计算：基于平均相关性分数
        avg_score = sum(retrieval_result.scores) / len(retrieval_result.scores) if retrieval_result.scores else 0.0
        return min(avg_score * 1.2, 1.0)  # 稍微提升以模拟精确率
    
    def _calculate_retrieval_recall(self, retrieval_result: RetrievalResult) -> float:
        """计算检索召回率"""
        # 模拟召回率计算
        # 在实际实现中，需要知道相关文档的总数
        retrieved_count = len(retrieval_result.documents)
        
        # 假设相关文档总数为10
        total_relevant = 10
        
        return min(retrieved_count / total_relevant, 1.0)
    
    async def _assess_generation_relevance(self, enhanced_context: UniversalContext, task: UniversalTask) -> float:
        """评估生成相关性"""
        # 检查增强内容与任务的相关性
        rag_content = enhanced_context.get('rag_enhanced_content', '')
        task_content = getattr(task, 'content', '')
        
        if not rag_content or not task_content:
            return 0.5
        
        # 简单的词汇重叠计算
        rag_words = set(rag_content.lower().split())
        task_words = set(task_content.lower().split())
        
        if not task_words:
            return 0.5
        
        overlap = len(rag_words.intersection(task_words))
        relevance = min(overlap / len(task_words), 1.0)
        
        return relevance
    
    def _calculate_token_efficiency(self, original_context: UniversalContext, enhanced_context: UniversalContext) -> float:
        """计算Token效率"""
        # 估算Token使用量
        original_size = len(str(original_context.get_all() if hasattr(original_context, 'get_all') else {}))
        enhanced_size = len(str(enhanced_context.get_all() if hasattr(enhanced_context, 'get_all') else {}))
        
        if original_size == 0:
            return 1.0
        
        # 效率 = 信息增益 / Token增长
        size_ratio = enhanced_size / original_size
        
        # 假设信息增益与RAG内容长度相关
        rag_content = enhanced_context.get('rag_enhanced_content', '')
        info_gain = min(len(rag_content) / 1000, 1.0)  # 标准化到0-1
        
        if size_ratio <= 1.0:
            return 1.0  # 没有增加Token使用量
        
        efficiency = info_gain / (size_ratio - 1.0) if size_ratio > 1.0 else 1.0
        return min(efficiency, 1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """获取RAG系统状态"""
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        
        avg_metrics = {}
        if recent_metrics:
            avg_metrics = {
                'avg_precision': sum(m.retrieval_precision for m in recent_metrics) / len(recent_metrics),
                'avg_recall': sum(m.retrieval_recall for m in recent_metrics) / len(recent_metrics),
                'avg_quality': sum(m.augmentation_quality for m in recent_metrics) / len(recent_metrics),
                'avg_relevance': sum(m.generation_relevance for m in recent_metrics) / len(recent_metrics),
                'avg_latency': sum(m.end_to_end_latency for m in recent_metrics) / len(recent_metrics),
                'avg_efficiency': sum(m.token_efficiency for m in recent_metrics) / len(recent_metrics)
            }
        
        return {
            'component': 'RAGSystem',
            'version': '1.0.0',
            'total_queries_processed': len(self.rag_history),
            'knowledge_base_size': len(self.knowledge_base['documents']),
            'retrieval_strategies': [s.value for s in RetrievalStrategy],
            'augmentation_methods': [m.value for m in AugmentationMethod],
            'configuration': self.config,
            'performance_metrics': avg_metrics,
            'last_processing_time': (
                self.rag_history[-1]['processing_time'] 
                if self.rag_history else 0.0
            )
        } 