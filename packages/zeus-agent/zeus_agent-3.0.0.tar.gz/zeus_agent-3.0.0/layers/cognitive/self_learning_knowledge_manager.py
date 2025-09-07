"""
自学习知识管理器
实现Memory-Knowledge集成的4阶段知识演化架构

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import re
from pathlib import Path

from .memory import MemorySystem, MemoryType, MemoryItem, EpisodicMemory, SemanticMemory
from ..intelligent_context.integrated_knowledge_service import IntegratedKnowledgeService, KnowledgeItem
from ..framework.abstractions.result import UniversalResult, ResultStatus, ErrorInfo

logger = logging.getLogger(__name__)


class KnowledgeEvolutionStage(Enum):
    """知识演化阶段"""
    IMMEDIATE = "immediate"      # 即时响应阶段 (Working Memory)
    EXPERIENTIAL = "experiential"  # 经验记录阶段 (Episodic Memory)
    CONCEPTUAL = "conceptual"    # 概念抽象阶段 (Semantic Memory)
    CRYSTALLIZED = "crystallized"  # 知识固化阶段 (Knowledge Base)


class FeedbackType(Enum):
    """反馈类型"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    CORRECTION = "correction"
    ENHANCEMENT = "enhancement"
    NEUTRAL = "neutral"


class QualityDimension(Enum):
    """质量维度"""
    USER_FEEDBACK = "user_feedback"     # 用户反馈
    CONSISTENCY = "consistency"         # 一致性
    COMPLETENESS = "completeness"       # 完整性
    VERIFIABILITY = "verifiability"     # 可验证性
    RELEVANCE = "relevance"             # 相关性


@dataclass
class LearningResponse:
    """学习响应项"""
    response_id: str
    query: str
    llm_response: str
    user_context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    stage: KnowledgeEvolutionStage = KnowledgeEvolutionStage.IMMEDIATE
    
    # 反馈和质量信息
    user_feedback: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    quality_breakdown: Dict[QualityDimension, float] = field(default_factory=dict)
    
    # 追踪信息
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    validation_count: int = 0
    
    # 关联信息
    related_responses: List[str] = field(default_factory=list)
    extracted_concepts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEvolutionMetrics:
    """知识演化指标"""
    total_responses: int = 0
    stage_distribution: Dict[str, int] = field(default_factory=lambda: {
        "immediate": 0, "experiential": 0, "conceptual": 0, "crystallized": 0
    })
    average_quality_score: float = 0.0
    crystallization_rate: float = 0.0  # 固化率
    user_satisfaction_rate: float = 0.0
    knowledge_retention_rate: float = 0.0


class KnowledgeQualityAssessor:
    """知识质量评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 质量维度权重
        self.quality_weights = {
            QualityDimension.USER_FEEDBACK: 0.4,
            QualityDimension.CONSISTENCY: 0.25,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.VERIFIABILITY: 0.1,
            QualityDimension.RELEVANCE: 0.1
        }
        
        # 质量阈值
        self.high_quality_threshold = 0.8
        self.medium_quality_threshold = 0.6
        self.low_quality_threshold = 0.4
    
    async def assess_response_quality(self, 
                                    response: LearningResponse,
                                    existing_knowledge: List[str] = None) -> Tuple[float, Dict[QualityDimension, float]]:
        """评估响应质量"""
        
        quality_breakdown = {}
        
        # 1. 用户反馈维度
        feedback_score = self._assess_user_feedback(response.user_feedback)
        quality_breakdown[QualityDimension.USER_FEEDBACK] = feedback_score
        
        # 2. 一致性维度
        consistency_score = await self._assess_consistency(response, existing_knowledge)
        quality_breakdown[QualityDimension.CONSISTENCY] = consistency_score
        
        # 3. 完整性维度
        completeness_score = self._assess_completeness(response)
        quality_breakdown[QualityDimension.COMPLETENESS] = completeness_score
        
        # 4. 可验证性维度
        verifiability_score = self._assess_verifiability(response)
        quality_breakdown[QualityDimension.VERIFIABILITY] = verifiability_score
        
        # 5. 相关性维度
        relevance_score = self._assess_relevance(response)
        quality_breakdown[QualityDimension.RELEVANCE] = relevance_score
        
        # 计算加权总分
        total_score = sum(
            self.quality_weights[dim] * score 
            for dim, score in quality_breakdown.items()
        )
        
        logger.debug(f"质量评估完成: 总分={total_score:.3f}, 明细={quality_breakdown}")
        
        return total_score, quality_breakdown
    
    def _assess_user_feedback(self, feedback: Optional[Dict[str, Any]]) -> float:
        """评估用户反馈"""
        if not feedback:
            return 0.5  # 中性分数
        
        feedback_type = feedback.get("type", FeedbackType.NEUTRAL.value)
        
        if feedback_type == FeedbackType.THUMBS_UP.value:
            return 0.9
        elif feedback_type == FeedbackType.THUMBS_DOWN.value:
            return 0.1
        elif feedback_type == FeedbackType.CORRECTION.value:
            return 0.3
        elif feedback_type == FeedbackType.ENHANCEMENT.value:
            return 0.7
        else:
            return 0.5
    
    async def _assess_consistency(self, 
                                response: LearningResponse,
                                existing_knowledge: List[str] = None) -> float:
        """评估一致性"""
        if not existing_knowledge:
            return 0.7  # 默认分数
        
        # 简化的一致性检查：检查是否有明显矛盾
        response_text = response.llm_response.lower()
        
        contradiction_indicators = [
            "但是", "然而", "相反", "不是", "错误", "不对"
        ]
        
        contradiction_count = sum(
            1 for indicator in contradiction_indicators 
            if indicator in response_text
        )
        
        # 矛盾指示词越多，一致性越低
        consistency_score = max(0.1, 1.0 - contradiction_count * 0.2)
        
        return consistency_score
    
    def _assess_completeness(self, response: LearningResponse) -> float:
        """评估完整性"""
        response_text = response.llm_response
        
        # 基于长度和结构的启发式评估
        length_score = min(1.0, len(response_text) / 500)  # 500字符为满分
        
        # 检查是否有结构化内容
        structure_indicators = [
            "：", "。", "；", "、", "\n", "1.", "2.", "首先", "其次", "最后"
        ]
        
        structure_count = sum(
            1 for indicator in structure_indicators 
            if indicator in response_text
        )
        
        structure_score = min(1.0, structure_count / 5)  # 5个结构指示词为满分
        
        return 0.6 * length_score + 0.4 * structure_score
    
    def _assess_verifiability(self, response: LearningResponse) -> float:
        """评估可验证性"""
        response_text = response.llm_response
        
        # 检查是否包含具体信息
        verifiable_indicators = [
            "根据", "文档", "标准", "规范", "示例", "代码", "参数", "配置"
        ]
        
        verifiable_count = sum(
            1 for indicator in verifiable_indicators 
            if indicator in response_text
        )
        
        return min(1.0, verifiable_count / 3)  # 3个可验证指示词为满分
    
    def _assess_relevance(self, response: LearningResponse) -> float:
        """评估相关性"""
        query_words = set(response.query.lower().split())
        response_words = set(response.llm_response.lower().split())
        
        # 计算词汇重叠度
        if not query_words:
            return 0.5
        
        overlap = len(query_words.intersection(response_words))
        relevance_score = overlap / len(query_words)
        
        return min(1.0, relevance_score)


class KnowledgeConflictResolver:
    """知识冲突解决器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    async def resolve_knowledge_conflict(self, 
                                       existing_knowledge: Dict[str, Any],
                                       new_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """解决知识冲突"""
        
        # 策略1: 时效性优先
        if self._is_time_sensitive(existing_knowledge, new_knowledge):
            return self._apply_temporal_resolution(existing_knowledge, new_knowledge)
        
        # 策略2: 质量优先
        if self._has_quality_difference(existing_knowledge, new_knowledge):
            return self._apply_quality_resolution(existing_knowledge, new_knowledge)
        
        # 策略3: 用户偏好优先
        if self._has_user_preference(existing_knowledge, new_knowledge):
            return self._apply_preference_resolution(existing_knowledge, new_knowledge)
        
        # 默认策略: 合并知识
        return self._merge_knowledge(existing_knowledge, new_knowledge)
    
    def _is_time_sensitive(self, existing: Dict, new: Dict) -> bool:
        """检查是否为时间敏感的知识"""
        time_sensitive_keywords = ["最新", "当前", "现在", "今天", "版本", "更新"]
        
        existing_text = str(existing.get("content", "")).lower()
        new_text = str(new.get("content", "")).lower()
        
        return any(keyword in existing_text or keyword in new_text 
                  for keyword in time_sensitive_keywords)
    
    def _apply_temporal_resolution(self, existing: Dict, new: Dict) -> Dict:
        """应用时间优先解决策略"""
        existing_time = existing.get("timestamp", datetime.min)
        new_time = new.get("timestamp", datetime.min)
        
        if isinstance(existing_time, str):
            existing_time = datetime.fromisoformat(existing_time)
        if isinstance(new_time, str):
            new_time = datetime.fromisoformat(new_time)
        
        # 返回较新的知识，但保留历史记录
        if new_time > existing_time:
            result = new.copy()
            result["superseded_knowledge"] = existing
            return result
        else:
            return existing
    
    def _has_quality_difference(self, existing: Dict, new: Dict) -> bool:
        """检查是否有质量差异"""
        existing_quality = existing.get("quality_score", 0.5)
        new_quality = new.get("quality_score", 0.5)
        
        return abs(existing_quality - new_quality) > 0.2
    
    def _apply_quality_resolution(self, existing: Dict, new: Dict) -> Dict:
        """应用质量优先解决策略"""
        existing_quality = existing.get("quality_score", 0.5)
        new_quality = new.get("quality_score", 0.5)
        
        if new_quality > existing_quality:
            return new
        else:
            return existing
    
    def _has_user_preference(self, existing: Dict, new: Dict) -> bool:
        """检查是否有用户偏好"""
        # 简化实现：检查用户反馈
        existing_feedback = existing.get("user_feedback", {})
        new_feedback = new.get("user_feedback", {})
        
        return (existing_feedback.get("type") == FeedbackType.THUMBS_UP.value or 
                new_feedback.get("type") == FeedbackType.THUMBS_UP.value)
    
    def _apply_preference_resolution(self, existing: Dict, new: Dict) -> Dict:
        """应用用户偏好优先策略"""
        existing_feedback = existing.get("user_feedback", {})
        new_feedback = new.get("user_feedback", {})
        
        if new_feedback.get("type") == FeedbackType.THUMBS_UP.value:
            return new
        elif existing_feedback.get("type") == FeedbackType.THUMBS_UP.value:
            return existing
        else:
            return self._merge_knowledge(existing, new)
    
    def _merge_knowledge(self, existing: Dict, new: Dict) -> Dict:
        """合并知识"""
        merged = existing.copy()
        
        # 合并内容
        existing_content = existing.get("content", "")
        new_content = new.get("content", "")
        
        if new_content and new_content not in existing_content:
            merged["content"] = f"{existing_content}\n\n补充信息：{new_content}"
        
        # 保留更高的质量分数
        if new.get("quality_score", 0) > existing.get("quality_score", 0):
            merged["quality_score"] = new["quality_score"]
        
        # 记录合并历史
        merged["merged_from"] = [existing.get("id"), new.get("id")]
        merged["merged_at"] = datetime.now().isoformat()
        
        return merged


class IntelligentKnowledgeEvolutionManager:
    """智能知识演化管理器"""
    
    def __init__(self, 
                 memory_system: MemorySystem,
                 knowledge_service: IntegratedKnowledgeService,
                 config: Dict[str, Any] = None):
        """初始化知识演化管理器"""
        
        self.memory_system = memory_system
        self.knowledge_service = knowledge_service
        self.config = config or {}
        
        # 初始化组件
        self.quality_assessor = KnowledgeQualityAssessor(self.config.get("quality", {}))
        self.conflict_resolver = KnowledgeConflictResolver(self.config.get("conflict", {}))
        
        # 存储演化中的响应
        self.evolving_responses: Dict[str, LearningResponse] = {}
        
        # 演化指标
        self.metrics = KnowledgeEvolutionMetrics()
        
        # 配置参数
        self.consolidation_interval = self.config.get("consolidation_interval", 3600)  # 1小时
        self.crystallization_interval = self.config.get("crystallization_interval", 86400)  # 24小时
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 启动后台任务
        self._background_tasks = set()
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """启动后台任务"""
        
        # 定期巩固任务
        consolidation_task = asyncio.create_task(self._periodic_consolidation())
        self._background_tasks.add(consolidation_task)
        consolidation_task.add_done_callback(self._background_tasks.discard)
        
        # 定期固化任务
        crystallization_task = asyncio.create_task(self._periodic_crystallization())
        self._background_tasks.add(crystallization_task)
        crystallization_task.add_done_callback(self._background_tasks.discard)
    
    async def process_llm_response(self, 
                                 query: str,
                                 llm_response: str,
                                 user_context: Dict[str, Any] = None) -> str:
        """处理LLM响应，启动知识演化流程"""
        
        # 生成响应ID
        response_id = self._generate_response_id(query, llm_response)
        
        # 创建学习响应项
        learning_response = LearningResponse(
            response_id=response_id,
            query=query,
            llm_response=llm_response,
            user_context=user_context or {},
            stage=KnowledgeEvolutionStage.IMMEDIATE
        )
        
        # 存储到演化队列
        self.evolving_responses[response_id] = learning_response
        
        # Stage 1: 存储到Working Memory
        await self._store_to_working_memory(learning_response)
        
        # 更新指标
        self.metrics.total_responses += 1
        self.metrics.stage_distribution["immediate"] += 1
        
        self.logger.info(f"📝 启动知识演化流程: {response_id[:8]}...")
        
        return response_id
    
    async def collect_user_feedback(self, 
                                  response_id: str,
                                  feedback: Dict[str, Any]) -> UniversalResult:
        """收集用户反馈，推进知识演化"""
        
        if response_id not in self.evolving_responses:
            return UniversalResult(
                content="响应ID不存在",
                status=ResultStatus.FAILURE,
                error=ErrorInfo(
                    error_type="response_not_found",
                    error_message=f"Response ID {response_id} not found"
                )
            )
        
        learning_response = self.evolving_responses[response_id]
        learning_response.user_feedback = feedback
        learning_response.validation_count += 1
        
        # 评估质量
        quality_score, quality_breakdown = await self.quality_assessor.assess_response_quality(
            learning_response
        )
        
        learning_response.quality_score = quality_score
        learning_response.quality_breakdown = quality_breakdown
        
        # Stage 2: 根据质量决定演化路径
        if quality_score > self.quality_assessor.high_quality_threshold:
            # 高质量：快速通道到语义记忆
            await self._fast_track_to_semantic_memory(learning_response)
        elif quality_score > self.quality_assessor.medium_quality_threshold:
            # 中等质量：标准情景记忆流程
            await self._promote_to_episodic_memory(learning_response)
        else:
            # 低质量：标记或丢弃
            await self._mark_low_quality_response(learning_response)
        
        # 更新用户满意度指标
        if feedback.get("type") == FeedbackType.THUMBS_UP.value:
            self.metrics.user_satisfaction_rate = (
                self.metrics.user_satisfaction_rate * 0.9 + 0.1
            )
        elif feedback.get("type") == FeedbackType.THUMBS_DOWN.value:
            self.metrics.user_satisfaction_rate = (
                self.metrics.user_satisfaction_rate * 0.9
            )
        
        self.logger.info(f"✅ 收集反馈完成: {response_id[:8]}... 质量={quality_score:.3f}")
        
        return UniversalResult(
            content="反馈收集完成",
            status=ResultStatus.SUCCESS,
            data={
                "quality_score": quality_score,
                "quality_breakdown": quality_breakdown,
                "evolution_stage": learning_response.stage.value
            }
        )
    
    async def _store_to_working_memory(self, learning_response: LearningResponse):
        """存储到工作记忆"""
        
        # 创建记忆项
        memory_item = MemoryItem(
            item_id=learning_response.response_id,
            content={
                "query": learning_response.query,
                "response": learning_response.llm_response,
                "context": learning_response.user_context
            },
            memory_type=MemoryType.WORKING,
            importance=0.5,
            tags=["llm_response", "learning"],
            metadata={
                "stage": learning_response.stage.value,
                "timestamp": learning_response.timestamp.isoformat()
            }
        )
        
        # 存储到工作记忆
        await self.memory_system.working_memory.store(memory_item)
        
        self.logger.debug(f"💾 已存储到工作记忆: {learning_response.response_id[:8]}...")
    
    async def _promote_to_episodic_memory(self, learning_response: LearningResponse):
        """提升到情景记忆"""
        
        learning_response.stage = KnowledgeEvolutionStage.EXPERIENTIAL
        
        # 创建情景记忆
        episode_data = {
            "event": f"用户询问: {learning_response.query}",
            "context": {
                "query": learning_response.query,
                "response": learning_response.llm_response,
                "user_context": learning_response.user_context,
                "user_feedback": learning_response.user_feedback,
                "quality_score": learning_response.quality_score
            },
            "participants": ["user", "assistant"],
            "importance": learning_response.quality_score or 0.5,
            "emotional_valence": self._calculate_emotional_valence(learning_response),
            "metadata": {
                "response_id": learning_response.response_id,
                "stage": learning_response.stage.value
            }
        }
        
        # 存储到情景记忆
        await self.memory_system.store_memory(
            episode_data,
            memory_type=MemoryType.EPISODIC,
            **episode_data
        )
        
        # 更新指标
        self.metrics.stage_distribution["experiential"] += 1
        
        self.logger.debug(f"📚 已提升到情景记忆: {learning_response.response_id[:8]}...")
    
    async def _fast_track_to_semantic_memory(self, learning_response: LearningResponse):
        """快速通道到语义记忆"""
        
        # 先经过情景记忆
        await self._promote_to_episodic_memory(learning_response)
        
        # 立即提取概念
        await self._abstract_to_semantic_memory(learning_response)
    
    async def _abstract_to_semantic_memory(self, learning_response: LearningResponse):
        """抽象到语义记忆"""
        
        learning_response.stage = KnowledgeEvolutionStage.CONCEPTUAL
        
        # 提取概念和关键词
        concepts = self._extract_concepts(learning_response)
        learning_response.extracted_concepts = concepts
        
        # 为每个概念创建语义记忆
        for concept in concepts:
            concept_data = {
                "concept": concept,
                "definition": f"基于用户查询'{learning_response.query}'学习的概念",
                "properties": {
                    "source": "llm_learning",
                    "query": learning_response.query,
                    "response": learning_response.llm_response,
                    "quality_score": learning_response.quality_score
                },
                "confidence": learning_response.quality_score or 0.5,
                "source": "self_learning",
                "metadata": {
                    "response_id": learning_response.response_id,
                    "learning_timestamp": learning_response.timestamp.isoformat()
                }
            }
            
            # 存储到语义记忆
            await self.memory_system.store_memory(
                concept_data,
                memory_type=MemoryType.SEMANTIC,
                **concept_data
            )
        
        # 更新指标
        self.metrics.stage_distribution["conceptual"] += 1
        
        self.logger.debug(f"🧠 已抽象到语义记忆: {learning_response.response_id[:8]}... 概念={concepts}")
    
    async def _crystallize_to_knowledge_base(self, learning_response: LearningResponse):
        """固化到知识库"""
        
        learning_response.stage = KnowledgeEvolutionStage.CRYSTALLIZED
        
        # 创建知识项
        knowledge_content = self._format_knowledge_content(learning_response)
        
        knowledge_metadata = {
            "source": "self_learning",
            "quality_score": learning_response.quality_score,
            "validation_count": learning_response.validation_count,
            "user_feedback": learning_response.user_feedback,
            "learning_timestamp": learning_response.timestamp.isoformat(),
            "crystallization_timestamp": datetime.now().isoformat(),
            "concepts": learning_response.extracted_concepts,
            "original_query": learning_response.query
        }
        
        # 检查冲突
        existing_knowledge = await self._find_conflicting_knowledge(learning_response)
        
        if existing_knowledge:
            # 解决冲突
            resolved_knowledge = await self.conflict_resolver.resolve_knowledge_conflict(
                existing_knowledge, {
                    "content": knowledge_content,
                    "metadata": knowledge_metadata,
                    "quality_score": learning_response.quality_score,
                    "timestamp": learning_response.timestamp
                }
            )
            knowledge_content = resolved_knowledge.get("content", knowledge_content)
            knowledge_metadata.update(resolved_knowledge.get("metadata", {}))
        
        # 添加到知识库
        try:
            doc_id = await self.knowledge_service.add_knowledge(
                content=knowledge_content,
                metadata=knowledge_metadata
            )
            
            learning_response.metadata["knowledge_doc_id"] = doc_id
            
            # 更新指标
            self.metrics.stage_distribution["crystallized"] += 1
            self.metrics.crystallization_rate = (
                self.metrics.stage_distribution["crystallized"] / 
                max(1, self.metrics.total_responses)
            )
            
            self.logger.info(f"💎 已固化到知识库: {learning_response.response_id[:8]}... doc_id={doc_id[:8]}...")
            
        except Exception as e:
            self.logger.error(f"❌ 知识固化失败: {e}")
    
    async def _mark_low_quality_response(self, learning_response: LearningResponse):
        """标记低质量响应"""
        
        # 仍然存储到情景记忆，但标记为低质量
        learning_response.metadata["low_quality"] = True
        learning_response.metadata["quality_issues"] = self._identify_quality_issues(learning_response)
        
        await self._promote_to_episodic_memory(learning_response)
        
        self.logger.debug(f"⚠️ 标记为低质量: {learning_response.response_id[:8]}...")
    
    def _generate_response_id(self, query: str, response: str) -> str:
        """生成响应ID"""
        content = f"{query}:{response}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_emotional_valence(self, learning_response: LearningResponse) -> float:
        """计算情感效价"""
        if not learning_response.user_feedback:
            return 0.0
        
        feedback_type = learning_response.user_feedback.get("type", FeedbackType.NEUTRAL.value)
        
        if feedback_type == FeedbackType.THUMBS_UP.value:
            return 0.8
        elif feedback_type == FeedbackType.THUMBS_DOWN.value:
            return -0.8
        elif feedback_type == FeedbackType.ENHANCEMENT.value:
            return 0.3
        elif feedback_type == FeedbackType.CORRECTION.value:
            return -0.3
        else:
            return 0.0
    
    def _extract_concepts(self, learning_response: LearningResponse) -> List[str]:
        """提取概念和关键词"""
        
        # 简化的概念提取
        response_text = learning_response.llm_response
        query_text = learning_response.query
        
        # 提取名词和技术术语
        import re
        
        # 技术术语模式
        tech_patterns = [
            r'\b[A-Z]{2,}\b',  # 大写缩略词
            r'\b\w+(?:_\w+)+\b',  # 下划线连接的术语
            r'\b\w+\.\w+\b',  # 点连接的术语
        ]
        
        concepts = set()
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, response_text)
            concepts.update(matches)
        
        # 从查询中提取关键词
        query_words = [word for word in query_text.split() if len(word) > 3]
        concepts.update(query_words)
        
        return list(concepts)[:10]  # 限制数量
    
    def _format_knowledge_content(self, learning_response: LearningResponse) -> str:
        """格式化知识内容"""
        
        return f"""问题：{learning_response.query}

回答：{learning_response.llm_response}

质量评估：{learning_response.quality_score:.3f}
学习时间：{learning_response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
验证次数：{learning_response.validation_count}
相关概念：{', '.join(learning_response.extracted_concepts)}"""
    
    async def _find_conflicting_knowledge(self, learning_response: LearningResponse) -> Optional[Dict]:
        """查找冲突知识"""
        # 简化实现：基于概念重叠检查冲突
        # 实际实现可以更复杂
        return None
    
    def _identify_quality_issues(self, learning_response: LearningResponse) -> List[str]:
        """识别质量问题"""
        issues = []
        
        if learning_response.quality_score and learning_response.quality_score < 0.4:
            for dim, score in learning_response.quality_breakdown.items():
                if score < 0.5:
                    issues.append(f"低{dim.value}分数: {score:.3f}")
        
        return issues
    
    async def _periodic_consolidation(self):
        """定期巩固任务"""
        while True:
            try:
                await asyncio.sleep(self.consolidation_interval)
                await self._consolidate_memories()
            except Exception as e:
                self.logger.error(f"❌ 巩固任务失败: {e}")
    
    async def _periodic_crystallization(self):
        """定期固化任务"""
        while True:
            try:
                await asyncio.sleep(self.crystallization_interval)
                await self._crystallize_mature_knowledge()
            except Exception as e:
                self.logger.error(f"❌ 固化任务失败: {e}")
    
    async def _consolidate_memories(self):
        """巩固记忆"""
        # 查找可以从情景记忆提升到语义记忆的内容
        conceptual_candidates = []
        
        for response_id, learning_response in self.evolving_responses.items():
            if (learning_response.stage == KnowledgeEvolutionStage.EXPERIENTIAL and
                learning_response.quality_score and
                learning_response.quality_score > self.quality_assessor.medium_quality_threshold and
                learning_response.validation_count >= 2):
                
                conceptual_candidates.append(learning_response)
        
        for candidate in conceptual_candidates:
            await self._abstract_to_semantic_memory(candidate)
        
        if conceptual_candidates:
            self.logger.info(f"🔄 巩固了 {len(conceptual_candidates)} 个记忆到语义层")
    
    async def _crystallize_mature_knowledge(self):
        """固化成熟知识"""
        # 查找可以固化到知识库的内容
        crystallization_candidates = []
        
        for response_id, learning_response in self.evolving_responses.items():
            if (learning_response.stage == KnowledgeEvolutionStage.CONCEPTUAL and
                learning_response.quality_score and
                learning_response.quality_score > self.quality_assessor.high_quality_threshold and
                learning_response.validation_count >= 3 and
                learning_response.access_count >= 2):
                
                crystallization_candidates.append(learning_response)
        
        for candidate in crystallization_candidates:
            await self._crystallize_to_knowledge_base(candidate)
        
        if crystallization_candidates:
            self.logger.info(f"💎 固化了 {len(crystallization_candidates)} 个知识到知识库")
    
    def get_evolution_metrics(self) -> Dict[str, Any]:
        """获取演化指标"""
        return {
            "total_responses": self.metrics.total_responses,
            "stage_distribution": self.metrics.stage_distribution,
            "average_quality_score": self.metrics.average_quality_score,
            "crystallization_rate": self.metrics.crystallization_rate,
            "user_satisfaction_rate": self.metrics.user_satisfaction_rate,
            "knowledge_retention_rate": self.metrics.knowledge_retention_rate,
            "active_responses": len(self.evolving_responses)
        }
    
    async def shutdown(self):
        """关闭管理器"""
        # 取消后台任务
        for task in self._background_tasks:
            task.cancel()
        
        # 等待任务完成
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self.logger.info("🔄 知识演化管理器已关闭") 