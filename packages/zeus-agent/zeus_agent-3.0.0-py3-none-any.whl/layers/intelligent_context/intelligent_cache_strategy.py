"""
智能缓存策略 - 高级缓存决策和优化算法

实现多种智能缓存策略，包括成本感知缓存、质量驱动缓存、
时间感知缓存等，为语义缓存系统提供决策支持。

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
import numpy as np
from collections import defaultdict

from .semantic_cache import CacheEntry, CachePriority, UserRole

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """缓存策略类型"""
    COST_AWARE = "cost_aware"              # 成本感知
    QUALITY_DRIVEN = "quality_driven"      # 质量驱动
    TEMPORAL_AWARE = "temporal_aware"      # 时间感知
    FREQUENCY_BASED = "frequency_based"    # 频率基础
    USER_ADAPTIVE = "user_adaptive"        # 用户自适应
    HYBRID = "hybrid"                      # 混合策略

class CacheDecisionFactor(Enum):
    """缓存决策因子"""
    QUERY_COMPLEXITY = "query_complexity"
    RESPONSE_LENGTH = "response_length"
    GENERATION_COST = "generation_cost"
    USER_SATISFACTION = "user_satisfaction"
    QUERY_FREQUENCY = "query_frequency"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    USER_ROLE_IMPORTANCE = "user_role_importance"

@dataclass
class CacheDecisionContext:
    """缓存决策上下文"""
    query: str
    response: str
    user_role: UserRole
    generation_cost: float
    quality_score: float
    response_time: float
    user_satisfaction: Optional[float] = None
    query_complexity: Optional[float] = None
    temporal_relevance: Optional[float] = None
    similar_queries_count: int = 0
    metadata: Dict[str, Any] = None

@dataclass
class CacheDecision:
    """缓存决策结果"""
    should_cache: bool
    priority: CachePriority
    ttl_seconds: int
    reasoning: List[str]
    confidence: float
    expected_value: float  # 预期价值

class IntelligentCacheStrategy:
    """智能缓存策略"""
    
    def __init__(
        self,
        strategy_type: CacheStrategy = CacheStrategy.HYBRID,
        cost_threshold: float = 0.1,
        quality_threshold: float = 0.6,
        frequency_threshold: int = 3
    ):
        self.strategy_type = strategy_type
        self.cost_threshold = cost_threshold
        self.quality_threshold = quality_threshold
        self.frequency_threshold = frequency_threshold
        
        # 决策因子权重
        self.factor_weights = self._initialize_factor_weights()
        
        # 查询频率统计
        self.query_frequency_stats: Dict[str, int] = defaultdict(int)
        
        # 用户行为模式
        self.user_behavior_patterns: Dict[UserRole, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        logger.info(f"🧠 智能缓存策略初始化 - 策略: {strategy_type.value}")
    
    def _initialize_factor_weights(self) -> Dict[CacheDecisionFactor, float]:
        """初始化决策因子权重"""
        base_weights = {
            CacheDecisionFactor.QUERY_COMPLEXITY: 0.15,
            CacheDecisionFactor.RESPONSE_LENGTH: 0.10,
            CacheDecisionFactor.GENERATION_COST: 0.25,
            CacheDecisionFactor.USER_SATISFACTION: 0.20,
            CacheDecisionFactor.QUERY_FREQUENCY: 0.15,
            CacheDecisionFactor.TEMPORAL_RELEVANCE: 0.10,
            CacheDecisionFactor.USER_ROLE_IMPORTANCE: 0.05
        }
        
        # 根据策略类型调整权重
        if self.strategy_type == CacheStrategy.COST_AWARE:
            base_weights[CacheDecisionFactor.GENERATION_COST] = 0.40
            base_weights[CacheDecisionFactor.QUERY_FREQUENCY] = 0.25
        elif self.strategy_type == CacheStrategy.QUALITY_DRIVEN:
            base_weights[CacheDecisionFactor.USER_SATISFACTION] = 0.35
            base_weights[CacheDecisionFactor.QUERY_COMPLEXITY] = 0.25
        elif self.strategy_type == CacheStrategy.FREQUENCY_BASED:
            base_weights[CacheDecisionFactor.QUERY_FREQUENCY] = 0.40
            base_weights[CacheDecisionFactor.TEMPORAL_RELEVANCE] = 0.20
        
        return base_weights
    
    async def make_cache_decision(self, context: CacheDecisionContext) -> CacheDecision:
        """做出缓存决策"""
        try:
            # 更新查询频率统计
            query_hash = self._hash_query(context.query)
            self.query_frequency_stats[query_hash] += 1
            
            # 计算各个决策因子的分数
            factor_scores = await self._calculate_factor_scores(context)
            
            # 计算综合评分
            total_score = self._calculate_weighted_score(factor_scores)
            
            # 基于评分做出决策
            decision = await self._make_decision_based_on_score(total_score, context)
            
            # 更新用户行为模式
            await self._update_user_behavior_pattern(context, decision)
            
            logger.debug(f"🧠 缓存决策: {context.query[:50]}... -> {decision.should_cache} (评分: {total_score:.3f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ 缓存决策失败: {e}")
            # 返回保守的决策
            return CacheDecision(
                should_cache=context.generation_cost > self.cost_threshold,
                priority=CachePriority.LOW,
                ttl_seconds=3600 * 24,  # 1天
                reasoning=[f"决策失败，使用保守策略: {str(e)}"],
                confidence=0.5,
                expected_value=context.generation_cost * 0.5
            )
    
    async def _calculate_factor_scores(self, context: CacheDecisionContext) -> Dict[CacheDecisionFactor, float]:
        """计算各个决策因子的分数"""
        scores = {}
        
        # 查询复杂度分数
        scores[CacheDecisionFactor.QUERY_COMPLEXITY] = await self._score_query_complexity(context)
        
        # 响应长度分数
        scores[CacheDecisionFactor.RESPONSE_LENGTH] = self._score_response_length(context)
        
        # 生成成本分数
        scores[CacheDecisionFactor.GENERATION_COST] = self._score_generation_cost(context)
        
        # 用户满意度分数
        scores[CacheDecisionFactor.USER_SATISFACTION] = self._score_user_satisfaction(context)
        
        # 查询频率分数
        scores[CacheDecisionFactor.QUERY_FREQUENCY] = self._score_query_frequency(context)
        
        # 时间相关性分数
        scores[CacheDecisionFactor.TEMPORAL_RELEVANCE] = await self._score_temporal_relevance(context)
        
        # 用户角色重要性分数
        scores[CacheDecisionFactor.USER_ROLE_IMPORTANCE] = self._score_user_role_importance(context)
        
        return scores
    
    async def _score_query_complexity(self, context: CacheDecisionContext) -> float:
        """评分查询复杂度"""
        if context.query_complexity is not None:
            return context.query_complexity
        
        # 基于查询长度和特征估算复杂度
        query_length = len(context.query)
        
        # 复杂查询指标
        complexity_indicators = [
            '如何实现', '设计', '优化', '调试', '分析',
            '比较', '评估', '选择', '配置', '集成'
        ]
        
        complexity_score = 0.0
        
        # 长度因子
        if query_length > 100:
            complexity_score += 0.4
        elif query_length > 50:
            complexity_score += 0.2
        
        # 复杂性关键词
        for indicator in complexity_indicators:
            if indicator in context.query:
                complexity_score += 0.2
                break
        
        # 技术术语密度
        technical_terms = ['FPGA', 'Verilog', 'HDL', 'RTL', '时序', '综合', '仿真']
        term_count = sum(1 for term in technical_terms if term in context.query)
        complexity_score += min(term_count * 0.1, 0.3)
        
        return min(complexity_score, 1.0)
    
    def _score_response_length(self, context: CacheDecisionContext) -> float:
        """评分响应长度"""
        response_length = len(context.response)
        
        # 长响应更有价值，更应该缓存
        if response_length > 2000:
            return 0.9
        elif response_length > 1000:
            return 0.7
        elif response_length > 500:
            return 0.5
        elif response_length > 200:
            return 0.3
        else:
            return 0.1
    
    def _score_generation_cost(self, context: CacheDecisionContext) -> float:
        """评分生成成本"""
        # 成本越高，缓存价值越大
        cost = context.generation_cost
        
        if cost > 1.0:
            return 1.0
        elif cost > 0.5:
            return 0.8
        elif cost > 0.2:
            return 0.6
        elif cost > 0.1:
            return 0.4
        else:
            return 0.2
    
    def _score_user_satisfaction(self, context: CacheDecisionContext) -> float:
        """评分用户满意度"""
        if context.user_satisfaction is not None:
            return context.user_satisfaction
        
        # 基于质量分数估算满意度
        if context.quality_score > 0.8:
            return 0.9
        elif context.quality_score > 0.6:
            return 0.7
        elif context.quality_score > 0.4:
            return 0.5
        else:
            return 0.3
    
    def _score_query_frequency(self, context: CacheDecisionContext) -> float:
        """评分查询频率"""
        query_hash = self._hash_query(context.query)
        frequency = self.query_frequency_stats[query_hash]
        
        # 频率越高，缓存价值越大
        if frequency > 10:
            return 1.0
        elif frequency > 5:
            return 0.8
        elif frequency > 2:
            return 0.6
        elif frequency > 1:
            return 0.4
        else:
            return 0.2
    
    async def _score_temporal_relevance(self, context: CacheDecisionContext) -> float:
        """评分时间相关性"""
        if context.temporal_relevance is not None:
            return context.temporal_relevance
        
        # 检查查询是否包含时间敏感的内容
        temporal_keywords = [
            '最新', '当前', '现在', '今年', '最近',
            '新版本', '更新', '发布', '趋势'
        ]
        
        has_temporal_content = any(keyword in context.query for keyword in temporal_keywords)
        
        if has_temporal_content:
            return 0.3  # 时间敏感内容缓存价值较低
        else:
            return 0.8  # 时间无关内容适合长期缓存
    
    def _score_user_role_importance(self, context: CacheDecisionContext) -> float:
        """评分用户角色重要性"""
        role_importance = {
            UserRole.EXPERT: 0.9,      # 专家的响应更有价值
            UserRole.RESEARCHER: 0.8,  # 研究者的响应也很有价值
            UserRole.INTERMEDIATE: 0.6, # 中级用户的响应有一定价值
            UserRole.BEGINNER: 0.4     # 初学者的响应价值较低
        }
        
        return role_importance.get(context.user_role, 0.5)
    
    def _calculate_weighted_score(self, factor_scores: Dict[CacheDecisionFactor, float]) -> float:
        """计算加权综合评分"""
        total_score = 0.0
        total_weight = 0.0
        
        for factor, score in factor_scores.items():
            weight = self.factor_weights.get(factor, 0.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / max(total_weight, 1.0)
    
    async def _make_decision_based_on_score(
        self, 
        total_score: float, 
        context: CacheDecisionContext
    ) -> CacheDecision:
        """基于评分做出决策"""
        reasoning = []
        
        # 决策阈值
        high_value_threshold = 0.75
        medium_value_threshold = 0.50
        low_value_threshold = 0.25
        
        if total_score >= high_value_threshold:
            should_cache = True
            priority = CachePriority.HIGH
            ttl_seconds = 3600 * 24 * 14  # 14天
            reasoning.append(f"高价值查询 (评分: {total_score:.3f})")
            expected_value = context.generation_cost * 0.8
            
        elif total_score >= medium_value_threshold:
            should_cache = True
            priority = CachePriority.MEDIUM
            ttl_seconds = 3600 * 24 * 7   # 7天
            reasoning.append(f"中等价值查询 (评分: {total_score:.3f})")
            expected_value = context.generation_cost * 0.6
            
        elif total_score >= low_value_threshold:
            should_cache = True
            priority = CachePriority.LOW
            ttl_seconds = 3600 * 24 * 3   # 3天
            reasoning.append(f"低价值查询 (评分: {total_score:.3f})")
            expected_value = context.generation_cost * 0.3
            
        else:
            should_cache = False
            priority = CachePriority.LOW
            ttl_seconds = 0
            reasoning.append(f"价值过低，不缓存 (评分: {total_score:.3f})")
            expected_value = 0.0
        
        # 特殊规则覆盖
        if context.generation_cost > 1.0:
            should_cache = True
            priority = max(priority, CachePriority.HIGH)
            reasoning.append("高成本查询强制缓存")
        
        if context.quality_score < 0.3:
            should_cache = False
            reasoning.append("质量过低，跳过缓存")
        
        confidence = min(total_score * 1.2, 1.0)  # 置信度基于评分
        
        return CacheDecision(
            should_cache=should_cache,
            priority=priority,
            ttl_seconds=ttl_seconds,
            reasoning=reasoning,
            confidence=confidence,
            expected_value=expected_value
        )
    
    async def _update_user_behavior_pattern(
        self, 
        context: CacheDecisionContext, 
        decision: CacheDecision
    ):
        """更新用户行为模式"""
        user_pattern = self.user_behavior_patterns[context.user_role]
        
        # 更新成本敏感度
        if context.generation_cost > 0.5 and decision.should_cache:
            user_pattern['cost_sensitivity'] = (user_pattern['cost_sensitivity'] * 0.9 + 0.8 * 0.1)
        
        # 更新质量偏好
        if context.quality_score > 0.8:
            user_pattern['quality_preference'] = (user_pattern['quality_preference'] * 0.9 + 0.9 * 0.1)
        
        # 更新复杂度偏好
        complexity_score = await self._score_query_complexity(context)
        if complexity_score > 0.7:
            user_pattern['complexity_preference'] = (user_pattern['complexity_preference'] * 0.9 + complexity_score * 0.1)
    
    def _hash_query(self, query: str) -> str:
        """生成查询哈希"""
        # 简单的查询规范化和哈希
        normalized = query.lower().strip()
        return str(hash(normalized))
    
    async def optimize_strategy(self, cache_performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """优化缓存策略"""
        optimization_result = {
            'weight_adjustments': {},
            'threshold_adjustments': {},
            'performance_improvement': 0.0,
            'recommendations': []
        }
        
        try:
            # 分析缓存性能数据
            hit_rate = cache_performance_data.get('hit_rate', 0.0)
            cost_efficiency = cache_performance_data.get('cost_efficiency', 0.0)
            average_quality = cache_performance_data.get('average_quality', 0.0)
            
            # 基于性能调整权重
            if hit_rate < 0.3:
                # 命中率低，提高频率因子权重
                self.factor_weights[CacheDecisionFactor.QUERY_FREQUENCY] *= 1.2
                optimization_result['weight_adjustments']['query_frequency'] = '+20%'
                optimization_result['recommendations'].append('提高查询频率权重以改善命中率')
            
            if cost_efficiency < 0.5:
                # 成本效率低，提高成本因子权重
                self.factor_weights[CacheDecisionFactor.GENERATION_COST] *= 1.1
                optimization_result['weight_adjustments']['generation_cost'] = '+10%'
                optimization_result['recommendations'].append('提高成本因子权重以改善成本效率')
            
            if average_quality < 0.6:
                # 质量偏低，提高质量因子权重
                self.factor_weights[CacheDecisionFactor.USER_SATISFACTION] *= 1.15
                optimization_result['weight_adjustments']['user_satisfaction'] = '+15%'
                optimization_result['recommendations'].append('提高用户满意度权重以改善缓存质量')
            
            # 归一化权重
            total_weight = sum(self.factor_weights.values())
            for factor in self.factor_weights:
                self.factor_weights[factor] /= total_weight
            
            logger.info(f"🔧 缓存策略优化完成: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ 缓存策略优化失败: {e}")
            return optimization_result

class AdaptiveCacheStrategy(IntelligentCacheStrategy):
    """自适应缓存策略"""
    
    def __init__(self, **kwargs):
        super().__init__(strategy_type=CacheStrategy.USER_ADAPTIVE, **kwargs)
        
        # 学习参数
        self.learning_rate = 0.1
        self.adaptation_window = 100  # 每100个决策后进行一次适应
        self.decision_history: List[Tuple[CacheDecisionContext, CacheDecision, float]] = []
    
    async def make_cache_decision(self, context: CacheDecisionContext) -> CacheDecision:
        """自适应的缓存决策"""
        decision = await super().make_cache_decision(context)
        
        # 记录决策历史
        self.decision_history.append((context, decision, 0.0))  # 初始反馈为0
        
        # 定期进行策略适应
        if len(self.decision_history) % self.adaptation_window == 0:
            await self._adapt_strategy()
        
        return decision
    
    async def provide_feedback(self, decision_index: int, feedback_score: float):
        """提供决策反馈"""
        if 0 <= decision_index < len(self.decision_history):
            context, decision, _ = self.decision_history[decision_index]
            self.decision_history[decision_index] = (context, decision, feedback_score)
    
    async def _adapt_strategy(self):
        """适应策略权重"""
        if not self.decision_history:
            return
        
        # 分析最近的决策反馈
        recent_decisions = self.decision_history[-self.adaptation_window:]
        positive_decisions = [d for d in recent_decisions if d[2] > 0.7]
        negative_decisions = [d for d in recent_decisions if d[2] < 0.3]
        
        # 基于正面反馈调整权重
        for context, decision, feedback in positive_decisions:
            factor_scores = await self._calculate_factor_scores(context)
            for factor, score in factor_scores.items():
                if score > 0.7:  # 高分因子
                    self.factor_weights[factor] *= (1 + self.learning_rate * 0.1)
        
        # 基于负面反馈调整权重
        for context, decision, feedback in negative_decisions:
            factor_scores = await self._calculate_factor_scores(context)
            for factor, score in factor_scores.items():
                if score > 0.7:  # 导致错误决策的高分因子
                    self.factor_weights[factor] *= (1 - self.learning_rate * 0.1)
        
        # 归一化权重
        total_weight = sum(self.factor_weights.values())
        for factor in self.factor_weights:
            self.factor_weights[factor] /= total_weight
        
        logger.info(f"🧠 自适应策略调整完成，处理了 {len(recent_decisions)} 个决策反馈")

# 工厂函数
def create_intelligent_cache_strategy(
    strategy_type: CacheStrategy = CacheStrategy.HYBRID,
    **kwargs
) -> IntelligentCacheStrategy:
    """创建智能缓存策略"""
    if strategy_type == CacheStrategy.USER_ADAPTIVE:
        return AdaptiveCacheStrategy(**kwargs)
    else:
        return IntelligentCacheStrategy(strategy_type=strategy_type, **kwargs) 