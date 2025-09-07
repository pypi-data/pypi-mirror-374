"""
高级融合策略 - 多源知识智能融合

实现多种高级知识融合策略，包括时间感知融合、语义融合、
成本感知融合、质量驱动融合等，提升复杂查询的处理能力。

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class AdvancedFusionStrategy(Enum):
    """高级融合策略类型"""
    TEMPORAL_FUSION = "temporal_fusion"              # 时间感知融合
    SEMANTIC_FUSION = "semantic_fusion"              # 语义融合
    COST_AWARE_FUSION = "cost_aware_fusion"         # 成本感知融合
    QUALITY_DRIVEN_FUSION = "quality_driven_fusion" # 质量驱动融合
    CONTEXTUAL_FUSION = "contextual_fusion"         # 上下文融合
    MULTI_PERSPECTIVE_FUSION = "multi_perspective_fusion"  # 多视角融合

class FusionTrigger(Enum):
    """融合触发条件"""
    CONFIDENCE_AMBIGUITY = "confidence_ambiguity"    # 置信度模糊
    COMPLEX_QUERY = "complex_query"                  # 复杂查询
    EXPERT_USER = "expert_user"                      # 专家用户
    HIGH_STAKES = "high_stakes"                      # 高风险场景
    RESEARCH_MODE = "research_mode"                  # 研究模式
    QUALITY_PRIORITY = "quality_priority"            # 质量优先

@dataclass
class KnowledgeSource:
    """知识源信息"""
    source_type: str
    content: str
    confidence: float
    cost: float
    latency: float
    timestamp: datetime
    authority_level: float  # 权威性等级
    freshness_score: float  # 新鲜度分数
    relevance_score: float  # 相关性分数
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FusionContext:
    """融合上下文"""
    query: str
    user_role: str
    conversation_context: Optional[Dict] = None
    quality_requirements: Optional[Dict] = None
    cost_constraints: Optional[Dict] = None
    time_constraints: Optional[Dict] = None
    domain_context: Optional[Dict] = None

@dataclass
class FusionResult:
    """融合结果"""
    fused_content: str
    fusion_strategy: AdvancedFusionStrategy
    source_contributions: Dict[str, float]  # 各源的贡献比例
    confidence_score: float
    total_cost: float
    fusion_reasoning: List[str]
    quality_indicators: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

class FusionStrategy(ABC):
    """融合策略抽象基类"""
    
    @abstractmethod
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否应该触发融合"""
        pass
    
    @abstractmethod
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行源融合"""
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        pass

class TemporalFusionStrategy(FusionStrategy):
    """时间感知融合策略"""
    
    def __init__(self, freshness_weight: float = 0.3):
        self.freshness_weight = freshness_weight
        self.strategy_type = AdvancedFusionStrategy.TEMPORAL_FUSION
    
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否触发时间感知融合"""
        if len(sources) < 2:
            return False, 0.0
        
        # 检查时间敏感性
        temporal_keywords = ['最新', '当前', '现在', '今年', '最近', '新版本', '更新']
        has_temporal_need = any(keyword in context.query for keyword in temporal_keywords)
        
        if not has_temporal_need:
            return False, 0.0
        
        # 检查源的时间分布
        freshness_scores = [source.freshness_score for source in sources]
        freshness_variance = np.var(freshness_scores) if len(freshness_scores) > 1 else 0
        
        # 如果有显著的新鲜度差异，建议融合
        trigger_confidence = min(1.0, freshness_variance * 2)
        should_trigger = freshness_variance > 0.2
        
        return should_trigger, trigger_confidence
    
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行时间感知融合"""
        # 按新鲜度排序
        sorted_sources = sorted(sources, key=lambda x: x.freshness_score, reverse=True)
        
        # 计算时间权重
        time_weights = []
        for source in sorted_sources:
            # 新鲜度越高，权重越大
            time_weight = source.freshness_score * self.freshness_weight
            # 权威性调整
            authority_weight = source.authority_level * (1 - self.freshness_weight)
            total_weight = time_weight + authority_weight
            time_weights.append(total_weight)
        
        # 归一化权重
        total_weight = sum(time_weights)
        normalized_weights = [w / total_weight for w in time_weights] if total_weight > 0 else [1/len(sources)] * len(sources)
        
        # 构建融合内容
        fused_parts = []
        source_contributions = {}
        
        for i, (source, weight) in enumerate(zip(sorted_sources, normalized_weights)):
            if weight > 0.1:  # 只包含权重显著的源
                freshness_info = "最新" if source.freshness_score > 0.8 else ("较新" if source.freshness_score > 0.5 else "较旧")
                fused_parts.append(
                    f"【{freshness_info}信息 - 权重{weight:.1%}】\n"
                    f"{source.content[:300]}..."
                )
                source_contributions[source.source_type] = weight
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算融合置信度
        weighted_confidence = sum(source.confidence * weight 
                                for source, weight in zip(sorted_sources, normalized_weights))
        
        # 计算总成本
        total_cost = sum(source.cost for source in sources)
        
        return FusionResult(
            fused_content=fused_content,
            fusion_strategy=self.strategy_type,
            source_contributions=source_contributions,
            confidence_score=weighted_confidence,
            total_cost=total_cost,
            fusion_reasoning=[
                f"时间感知融合，优先最新信息",
                f"融合了{len(source_contributions)}个不同新鲜度的源",
                f"新鲜度权重: {self.freshness_weight:.1%}"
            ],
            quality_indicators={
                'temporal_relevance': max(source.freshness_score for source in sources),
                'information_diversity': len(source_contributions),
                'authority_balance': sum(source.authority_level for source in sources) / len(sources)
            }
        )
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'freshness_weight': self.freshness_weight,
            'description': '基于时间新鲜度的智能融合策略'
        }

class SemanticFusionStrategy(FusionStrategy):
    """语义融合策略"""
    
    def __init__(self, semantic_threshold: float = 0.7):
        self.semantic_threshold = semantic_threshold
        self.strategy_type = AdvancedFusionStrategy.SEMANTIC_FUSION
    
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否触发语义融合"""
        if len(sources) < 2:
            return False, 0.0
        
        # 检查语义复杂性
        complex_indicators = ['如何实现', '设计方案', '架构分析', '比较评估', '优缺点']
        is_complex_semantic = any(indicator in context.query for indicator in complex_indicators)
        
        if not is_complex_semantic:
            return False, 0.0
        
        # 检查源的相关性分布
        relevance_scores = [source.relevance_score for source in sources]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # 如果多个源都有较高相关性，建议融合
        high_relevance_count = sum(1 for score in relevance_scores if score > self.semantic_threshold)
        trigger_confidence = high_relevance_count / len(sources)
        should_trigger = high_relevance_count >= 2 and avg_relevance > self.semantic_threshold
        
        return should_trigger, trigger_confidence
    
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行语义融合"""
        # 按相关性排序
        sorted_sources = sorted(sources, key=lambda x: x.relevance_score, reverse=True)
        
        # 语义聚类 - 将相似内容分组
        semantic_groups = await self._cluster_by_semantics(sorted_sources)
        
        # 构建分层融合内容
        fused_parts = []
        source_contributions = {}
        
        for group_name, group_sources in semantic_groups.items():
            if len(group_sources) > 0:
                # 计算组权重
                group_weight = sum(source.relevance_score for source in group_sources) / len(group_sources)
                
                # 选择组内最佳代表
                representative = max(group_sources, key=lambda x: x.confidence * x.authority_level)
                
                fused_parts.append(
                    f"【{group_name} - 相关性{group_weight:.1%}】\n"
                    f"{representative.content[:400]}..."
                )
                
                for source in group_sources:
                    source_contributions[source.source_type] = source_contributions.get(
                        source.source_type, 0) + group_weight / len(group_sources)
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算语义融合置信度
        semantic_confidence = sum(source.relevance_score * source.confidence 
                                for source in sorted_sources) / len(sorted_sources)
        
        total_cost = sum(source.cost for source in sources)
        
        return FusionResult(
            fused_content=fused_content,
            fusion_strategy=self.strategy_type,
            source_contributions=source_contributions,
            confidence_score=semantic_confidence,
            total_cost=total_cost,
            fusion_reasoning=[
                f"语义融合，聚合{len(semantic_groups)}个主题视角",
                f"基于相关性阈值{self.semantic_threshold:.1%}",
                f"整合了{len(sources)}个不同语义源"
            ],
            quality_indicators={
                'semantic_coverage': len(semantic_groups),
                'relevance_depth': max(source.relevance_score for source in sources),
                'content_diversity': len(set(source.source_type for source in sources))
            }
        )
    
    async def _cluster_by_semantics(self, sources: List[KnowledgeSource]) -> Dict[str, List[KnowledgeSource]]:
        """按语义聚类"""
        # 简化的语义聚类（实际实现中会使用更复杂的算法）
        clusters = {
            '理论基础': [],
            '实践应用': [],
            '设计方法': [],
            '最佳实践': []
        }
        
        for source in sources:
            content_lower = source.content.lower()
            
            # 简单的关键词匹配分类
            if any(word in content_lower for word in ['理论', '原理', '概念', '定义']):
                clusters['理论基础'].append(source)
            elif any(word in content_lower for word in ['实现', '应用', '示例', '代码']):
                clusters['实践应用'].append(source)
            elif any(word in content_lower for word in ['设计', '方法', '步骤', '流程']):
                clusters['设计方法'].append(source)
            else:
                clusters['最佳实践'].append(source)
        
        # 移除空聚类
        return {k: v for k, v in clusters.items() if v}
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'semantic_threshold': self.semantic_threshold,
            'description': '基于语义相似性的智能聚类融合策略'
        }

class CostAwareFusionStrategy(FusionStrategy):
    """成本感知融合策略"""
    
    def __init__(self, cost_budget: float = 2.0, efficiency_threshold: float = 0.8):
        self.cost_budget = cost_budget
        self.efficiency_threshold = efficiency_threshold
        self.strategy_type = AdvancedFusionStrategy.COST_AWARE_FUSION
    
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否触发成本感知融合"""
        if len(sources) < 2:
            return False, 0.0
        
        # 检查成本约束
        total_cost = sum(source.cost for source in sources)
        if total_cost > self.cost_budget:
            return False, 0.0
        
        # 检查成本效益
        cost_efficiency_scores = []
        for source in sources:
            # 成本效益 = 置信度 / 成本
            efficiency = source.confidence / max(source.cost, 0.001)
            cost_efficiency_scores.append(efficiency)
        
        avg_efficiency = sum(cost_efficiency_scores) / len(cost_efficiency_scores)
        
        # 如果成本效益高且在预算内，建议融合
        should_trigger = avg_efficiency > self.efficiency_threshold
        trigger_confidence = min(1.0, avg_efficiency / self.efficiency_threshold)
        
        return should_trigger, trigger_confidence
    
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行成本感知融合"""
        # 计算成本效益权重
        efficiency_weights = []
        for source in sources:
            efficiency = source.confidence / max(source.cost, 0.001)
            efficiency_weights.append(efficiency)
        
        # 归一化权重
        total_efficiency = sum(efficiency_weights)
        normalized_weights = [w / total_efficiency for w in efficiency_weights] if total_efficiency > 0 else [1/len(sources)] * len(sources)
        
        # 按成本效益排序
        source_efficiency_pairs = list(zip(sources, normalized_weights))
        source_efficiency_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # 构建成本感知融合内容
        fused_parts = []
        source_contributions = {}
        cumulative_cost = 0.0
        
        for source, weight in source_efficiency_pairs:
            if cumulative_cost + source.cost <= self.cost_budget and weight > 0.05:
                efficiency = source.confidence / max(source.cost, 0.001)
                fused_parts.append(
                    f"【高效源 - 效益{efficiency:.1f}, 权重{weight:.1%}】\n"
                    f"{source.content[:350]}..."
                )
                source_contributions[source.source_type] = weight
                cumulative_cost += source.cost
            else:
                break
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算加权置信度
        included_sources = [source for source, weight in source_efficiency_pairs 
                          if source.source_type in source_contributions]
        weighted_confidence = sum(source.confidence * source_contributions[source.source_type] 
                                for source in included_sources)
        
        return FusionResult(
            fused_content=fused_content,
            fusion_strategy=self.strategy_type,
            source_contributions=source_contributions,
            confidence_score=weighted_confidence,
            total_cost=cumulative_cost,
            fusion_reasoning=[
                f"成本感知融合，预算${self.cost_budget:.2f}",
                f"实际成本${cumulative_cost:.2f}，效益阈值{self.efficiency_threshold:.1f}",
                f"选择了{len(source_contributions)}个高效益源"
            ],
            quality_indicators={
                'cost_efficiency': weighted_confidence / max(cumulative_cost, 0.001),
                'budget_utilization': cumulative_cost / self.cost_budget,
                'source_efficiency': sum(efficiency_weights) / len(efficiency_weights)
            }
        )
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'cost_budget': self.cost_budget,
            'efficiency_threshold': self.efficiency_threshold,
            'description': '基于成本效益优化的智能融合策略'
        }

class QualityDrivenFusionStrategy(FusionStrategy):
    """质量驱动融合策略"""
    
    def __init__(self, quality_threshold: float = 0.8, authority_weight: float = 0.4):
        self.quality_threshold = quality_threshold
        self.authority_weight = authority_weight
        self.strategy_type = AdvancedFusionStrategy.QUALITY_DRIVEN_FUSION
    
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否触发质量驱动融合"""
        if len(sources) < 2:
            return False, 0.0
        
        # 检查是否为质量敏感查询
        quality_indicators = ['最佳', '推荐', '标准', '规范', '权威', '官方']
        is_quality_sensitive = any(indicator in context.query for indicator in quality_indicators)
        
        # 检查用户角色
        is_expert_user = context.user_role in ['expert', 'researcher']
        
        # 检查源的质量分布
        high_quality_sources = [s for s in sources 
                              if s.confidence > self.quality_threshold and s.authority_level > 0.7]
        
        should_trigger = (is_quality_sensitive or is_expert_user) and len(high_quality_sources) >= 2
        trigger_confidence = len(high_quality_sources) / len(sources)
        
        return should_trigger, trigger_confidence
    
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行质量驱动融合"""
        # 计算质量权重
        quality_weights = []
        for source in sources:
            # 综合质量分数 = 置信度 * 权威性权重 + 权威性 * (1-权威性权重)
            quality_score = (source.confidence * (1 - self.authority_weight) + 
                           source.authority_level * self.authority_weight)
            quality_weights.append(quality_score)
        
        # 归一化权重
        total_quality = sum(quality_weights)
        normalized_weights = [w / total_quality for w in quality_weights] if total_quality > 0 else [1/len(sources)] * len(sources)
        
        # 按质量排序
        quality_ranked = list(zip(sources, normalized_weights))
        quality_ranked.sort(key=lambda x: x[1], reverse=True)
        
        # 构建质量驱动融合内容
        fused_parts = []
        source_contributions = {}
        
        for source, weight in quality_ranked:
            if weight > 0.1:  # 只包含高质量源
                authority_label = "权威" if source.authority_level > 0.8 else ("可信" if source.authority_level > 0.6 else "一般")
                confidence_label = "高信度" if source.confidence > 0.8 else ("中信度" if source.confidence > 0.6 else "低信度")
                
                fused_parts.append(
                    f"【{authority_label}源 - {confidence_label}, 权重{weight:.1%}】\n"
                    f"{source.content[:400]}..."
                )
                source_contributions[source.source_type] = weight
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算质量加权置信度
        quality_confidence = sum(source.confidence * weight 
                               for source, weight in quality_ranked 
                               if source.source_type in source_contributions)
        
        total_cost = sum(source.cost for source in sources if source.source_type in source_contributions)
        
        return FusionResult(
            fused_content=fused_content,
            fusion_strategy=self.strategy_type,
            source_contributions=source_contributions,
            confidence_score=quality_confidence,
            total_cost=total_cost,
            fusion_reasoning=[
                f"质量驱动融合，权威性权重{self.authority_weight:.1%}",
                f"质量阈值{self.quality_threshold:.1%}",
                f"选择了{len(source_contributions)}个高质量源"
            ],
            quality_indicators={
                'average_authority': sum(source.authority_level for source in sources if source.source_type in source_contributions) / len(source_contributions),
                'average_confidence': quality_confidence,
                'quality_consistency': min(source.confidence for source in sources if source.source_type in source_contributions)
            }
        )
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'quality_threshold': self.quality_threshold,
            'authority_weight': self.authority_weight,
            'description': '基于质量和权威性的融合策略'
        }

class MultiPerspectiveFusionStrategy(FusionStrategy):
    """多视角融合策略"""
    
    def __init__(self, perspective_diversity_threshold: float = 0.6):
        self.perspective_diversity_threshold = perspective_diversity_threshold
        self.strategy_type = AdvancedFusionStrategy.MULTI_PERSPECTIVE_FUSION
    
    async def should_trigger(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Tuple[bool, float]:
        """判断是否触发多视角融合"""
        if len(sources) < 3:  # 至少需要3个源才能形成多视角
            return False, 0.0
        
        # 检查是否为多视角查询
        perspective_indicators = ['比较', '对比', '优缺点', '差异', '选择', '评估']
        needs_multiple_perspectives = any(indicator in context.query for indicator in perspective_indicators)
        
        # 检查源的多样性
        source_types = set(source.source_type for source in sources)
        diversity_score = len(source_types) / len(sources)
        
        should_trigger = needs_multiple_perspectives and diversity_score > self.perspective_diversity_threshold
        trigger_confidence = diversity_score
        
        return should_trigger, trigger_confidence
    
    async def fuse_sources(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> FusionResult:
        """执行多视角融合"""
        # 按源类型分组
        source_groups = defaultdict(list)
        for source in sources:
            source_groups[source.source_type].append(source)
        
        # 为每个视角选择最佳代表
        perspective_representatives = {}
        for source_type, group_sources in source_groups.items():
            # 选择该类型中置信度最高的源
            best_source = max(group_sources, key=lambda x: x.confidence)
            perspective_representatives[source_type] = best_source
        
        # 构建多视角融合内容
        fused_parts = []
        source_contributions = {}
        
        perspective_labels = {
            'local_kb': '知识库视角',
            'ai_training': 'AI分析视角',
            'web_search': '最新资讯视角'
        }
        
        for source_type, representative in perspective_representatives.items():
            perspective_label = perspective_labels.get(source_type, f'{source_type}视角')
            
            # 计算视角权重（基于置信度和权威性）
            perspective_weight = (representative.confidence + representative.authority_level) / 2
            
            fused_parts.append(
                f"【{perspective_label} - 权重{perspective_weight:.1%}】\n"
                f"{representative.content[:350]}..."
            )
            source_contributions[source_type] = perspective_weight
        
        # 归一化贡献权重
        total_contribution = sum(source_contributions.values())
        if total_contribution > 0:
            source_contributions = {k: v/total_contribution for k, v in source_contributions.items()}
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算多视角置信度
        multi_perspective_confidence = sum(rep.confidence * source_contributions[source_type] 
                                         for source_type, rep in perspective_representatives.items())
        
        total_cost = sum(rep.cost for rep in perspective_representatives.values())
        
        return FusionResult(
            fused_content=fused_content,
            fusion_strategy=self.strategy_type,
            source_contributions=source_contributions,
            confidence_score=multi_perspective_confidence,
            total_cost=total_cost,
            fusion_reasoning=[
                f"多视角融合，整合{len(perspective_representatives)}个不同视角",
                f"视角多样性阈值{self.perspective_diversity_threshold:.1%}",
                f"提供全面的多角度分析"
            ],
            quality_indicators={
                'perspective_diversity': len(perspective_representatives),
                'viewpoint_balance': min(source_contributions.values()) / max(source_contributions.values()) if source_contributions else 0,
                'comprehensive_coverage': sum(rep.relevance_score for rep in perspective_representatives.values()) / len(perspective_representatives)
            }
        )
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'cost_budget': self.cost_budget,
            'diversity_threshold': self.perspective_diversity_threshold,
            'description': '提供多个视角的全面融合策略'
        }

class IntelligentFusionDecider:
    """智能融合决策器"""
    
    def __init__(self):
        self.fusion_strategies = {
            AdvancedFusionStrategy.TEMPORAL_FUSION: TemporalFusionStrategy(),
            AdvancedFusionStrategy.SEMANTIC_FUSION: SemanticFusionStrategy(),
            AdvancedFusionStrategy.COST_AWARE_FUSION: CostAwareFusionStrategy(),
            AdvancedFusionStrategy.QUALITY_DRIVEN_FUSION: QualityDrivenFusionStrategy(),
            AdvancedFusionStrategy.MULTI_PERSPECTIVE_FUSION: MultiPerspectiveFusionStrategy()
        }
        
        self.fusion_history: List[Dict[str, Any]] = []
        
        logger.info("🧠 智能融合决策器初始化完成")
    
    async def decide_fusion_strategy(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext
    ) -> Optional[Tuple[AdvancedFusionStrategy, float]]:
        """决定最佳融合策略"""
        if len(sources) < 2:
            return None
        
        # 评估所有可用策略
        strategy_scores = {}
        
        for strategy_type, strategy in self.fusion_strategies.items():
            try:
                should_trigger, confidence = await strategy.should_trigger(sources, context)
                if should_trigger:
                    strategy_scores[strategy_type] = confidence
                    logger.debug(f"🎯 策略 {strategy_type.value} 可用，置信度: {confidence:.3f}")
            except Exception as e:
                logger.error(f"❌ 策略 {strategy_type.value} 评估失败: {e}")
        
        if not strategy_scores:
            return None
        
        # 选择最佳策略
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        
        logger.info(f"🎯 选择融合策略: {best_strategy[0].value} (置信度: {best_strategy[1]:.3f})")
        
        return best_strategy
    
    async def execute_fusion(
        self, 
        sources: List[KnowledgeSource], 
        context: FusionContext,
        strategy_type: AdvancedFusionStrategy
    ) -> FusionResult:
        """执行融合策略"""
        try:
            strategy = self.fusion_strategies[strategy_type]
            result = await strategy.fuse_sources(sources, context)
            
            # 记录融合历史
            self.fusion_history.append({
                'timestamp': datetime.now(),
                'query': context.query,
                'strategy': strategy_type.value,
                'source_count': len(sources),
                'confidence': result.confidence_score,
                'cost': result.total_cost
            })
            
            logger.info(f"✅ 融合执行成功: {strategy_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 融合执行失败: {e}")
            raise
    
    async def get_fusion_analytics(self) -> Dict[str, Any]:
        """获取融合分析数据"""
        if not self.fusion_history:
            return {'total_fusions': 0}
        
        # 统计融合策略使用情况
        strategy_usage = defaultdict(int)
        for record in self.fusion_history:
            strategy_usage[record['strategy']] += 1
        
        # 计算平均指标
        total_fusions = len(self.fusion_history)
        avg_confidence = sum(record['confidence'] for record in self.fusion_history) / total_fusions
        avg_cost = sum(record['cost'] for record in self.fusion_history) / total_fusions
        avg_sources = sum(record['source_count'] for record in self.fusion_history) / total_fusions
        
        return {
            'total_fusions': total_fusions,
            'strategy_distribution': dict(strategy_usage),
            'average_confidence': avg_confidence,
            'average_cost': avg_cost,
            'average_sources_per_fusion': avg_sources,
            'most_used_strategy': max(strategy_usage.items(), key=lambda x: x[1])[0] if strategy_usage else None
        }

# 工厂函数
def create_intelligent_fusion_decider() -> IntelligentFusionDecider:
    """创建智能融合决策器"""
    return IntelligentFusionDecider() 