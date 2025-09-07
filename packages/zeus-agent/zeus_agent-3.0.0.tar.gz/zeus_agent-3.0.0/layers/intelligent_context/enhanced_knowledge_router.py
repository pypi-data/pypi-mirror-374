"""
增强版知识路由器
实现动态权重、用户画像、反馈学习、决策审计等高级功能

新增特性：
1. 动态权重与上下文感知
2. 用户画像与角色识别
3. 反馈学习与持续优化
4. 决策审计日志
5. 降级策略与故障转移
6. 抽象路由器接口
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import json
import hashlib
from pathlib import Path

from .knowledge_router import (
    KnowledgeSourceType, QueryComplexity, QueryDomain, 
    QueryAnalysis, KnowledgeSourceDecision, KnowledgeSourceCapability
)

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """用户角色"""
    BEGINNER = "beginner"      # 初学者
    INTERMEDIATE = "intermediate"  # 中级用户
    EXPERT = "expert"          # 专家
    RESEARCHER = "researcher"  # 研究者


class ContextType(Enum):
    """对话上下文类型"""
    STANDALONE = "standalone"      # 独立查询
    FOLLOW_UP = "follow_up"       # 后续问题
    DEEP_DIVE = "deep_dive"       # 深入探讨
    TROUBLESHOOTING = "troubleshooting"  # 问题排查


class FeedbackType(Enum):
    """反馈类型"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    FOLLOW_UP_QUESTION = "follow_up_question"
    SATISFACTION_RATING = "satisfaction_rating"


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    role: UserRole = UserRole.INTERMEDIATE
    expertise_domains: List[str] = field(default_factory=list)
    preferred_detail_level: str = "medium"  # low, medium, high
    cost_sensitivity: float = 0.5  # 0-1, 越高越在意成本
    speed_preference: float = 0.5  # 0-1, 越高越在意速度
    interaction_history: List[Dict] = field(default_factory=list)
    feedback_score: float = 0.8  # 历史反馈平均分
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationContext:
    """对话上下文"""
    conversation_id: str
    context_type: ContextType = ContextType.STANDALONE
    previous_queries: List[str] = field(default_factory=list)
    previous_decisions: List[KnowledgeSourceDecision] = field(default_factory=list)
    topic_thread: Optional[str] = None  # 当前讨论的主题
    knowledge_domain_focus: Optional[QueryDomain] = None
    session_cost_used: float = 0.0
    session_start: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionAuditLog:
    """决策审计日志"""
    log_id: str
    timestamp: datetime
    user_id: str
    query: str
    query_analysis: QueryAnalysis
    all_source_scores: Dict[KnowledgeSourceType, float]
    final_decision: KnowledgeSourceDecision
    router_type: str
    router_version: str
    execution_time_ms: float
    context: Optional[ConversationContext] = None
    user_profile: Optional[UserProfile] = None
    feedback: Optional[Dict] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class RoutingFeedback:
    """路由反馈"""
    decision_id: str
    feedback_type: FeedbackType
    rating: Optional[float] = None  # 1-5
    comment: Optional[str] = None
    implicit_signals: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AbstractRouter(ABC):
    """抽象路由器接口"""
    
    @abstractmethod
    async def route_query(
        self, 
        query: str, 
        user_profile: Optional[UserProfile] = None,
        context: Optional[ConversationContext] = None
    ) -> KnowledgeSourceDecision:
        """路由查询到最适合的知识源"""
        pass
    
    @abstractmethod
    def get_router_info(self) -> Dict[str, Any]:
        """获取路由器信息"""
        pass


class EnhancedKnowledgeRouter(AbstractRouter):
    """
    增强版知识路由器
    
    核心增强功能：
    1. 动态权重调整
    2. 用户画像感知
    3. 上下文连续性
    4. 成本预算控制
    5. 决策审计日志
    6. 反馈学习循环
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化增强路由器"""
        self.config = config or {}
        
        # 基础权重配置（可动态调整）
        self.base_weights = {
            'domain_match': 0.40,
            'complexity_match': 0.25,
            'special_requirements': 0.20,
            'cost_efficiency': 0.10,
            'response_speed': 0.05
        }
        
        # 用户角色权重调整
        self.role_weight_adjustments = {
            UserRole.BEGINNER: {
                'domain_match': 0.45,      # 更重视领域匹配
                'complexity_match': 0.15,  # 降低复杂度权重
                'cost_efficiency': 0.20,   # 更在意成本
                'response_speed': 0.15     # 更在意速度
            },
            UserRole.EXPERT: {
                'domain_match': 0.35,      # 稍降领域匹配
                'complexity_match': 0.35,  # 大幅提升复杂度权重
                'special_requirements': 0.25,  # 更重视特殊需求
                'cost_efficiency': 0.05    # 不太在意成本
            },
            UserRole.RESEARCHER: {
                'domain_match': 0.30,
                'complexity_match': 0.30,
                'special_requirements': 0.30,  # 最重视特殊需求
                'cost_efficiency': 0.05,
                'response_speed': 0.05
            }
        }
        
        # 上下文类型权重调整
        self.context_weight_adjustments = {
            ContextType.FOLLOW_UP: {
                'consistency_bonus': 0.3  # 与之前决策保持一致的奖励
            },
            ContextType.DEEP_DIVE: {
                'domain_match': 0.50,     # 更重视领域匹配
                'consistency_bonus': 0.2
            },
            ContextType.TROUBLESHOOTING: {
                'special_requirements': 0.30,  # 更重视精确性
                'response_speed': 0.15     # 更在意速度
            }
        }
        
        # 成本控制配置
        self.cost_budget = {
            'daily_limit': 10.0,    # 每日预算
            'monthly_limit': 200.0, # 每月预算
            'emergency_threshold': 0.9  # 紧急阈值
        }
        
        # 知识源能力（继承基础配置）
        self.source_capabilities = self._load_source_capabilities()
        
        # 决策日志存储
        self.audit_logs: List[DecisionAuditLog] = []
        self.audit_log_file = Path("logs/routing_decisions.jsonl")
        self.audit_log_file.parent.mkdir(exist_ok=True)
        
        # 反馈学习数据
        self.feedback_data: List[RoutingFeedback] = []
        self.learned_weights = self.base_weights.copy()
        
        # 降级策略配置
        self.fallback_strategies = self._init_fallback_strategies()
        
        logger.info("🧠 增强版知识路由器初始化完成")
    
    async def route_query(
        self, 
        query: str, 
        user_profile: Optional[UserProfile] = None,
        context: Optional[ConversationContext] = None
    ) -> KnowledgeSourceDecision:
        """增强版查询路由"""
        
        start_time = datetime.now()
        log_id = self._generate_log_id(query)
        
        try:
            # 1. 查询分析（增强版）
            analysis = await self._enhanced_query_analysis(query, user_profile, context)
            
            # 2. 动态权重计算
            weights = await self._calculate_dynamic_weights(user_profile, context, analysis)
            
            # 3. 成本预算检查
            await self._check_cost_budget(user_profile, context)
            
            # 4. 知识源评估（考虑上下文）
            source_scores = await self._enhanced_source_evaluation(
                analysis, weights, user_profile, context
            )
            
            # 5. 智能决策（带降级策略）
            decision = await self._make_enhanced_decision(
                analysis, source_scores, user_profile, context
            )
            
            # 6. 记录审计日志
            await self._log_decision(
                log_id, query, analysis, source_scores, decision,
                user_profile, context, start_time, True
            )
            
            return decision
            
        except Exception as e:
            # 错误处理和降级
            logger.error(f"❌ 路由决策失败: {e}")
            
            fallback_decision = await self._execute_fallback_strategy(
                query, user_profile, context, str(e)
            )
            
            await self._log_decision(
                log_id, query, None, {}, fallback_decision,
                user_profile, context, start_time, False, str(e)
            )
            
            return fallback_decision
    
    async def _enhanced_query_analysis(
        self, 
        query: str, 
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext]
    ) -> QueryAnalysis:
        """增强版查询分析"""
        
        # 基础分析
        analysis = await self._basic_query_analysis(query)
        
        # 用户画像增强
        if user_profile:
            analysis = await self._enhance_with_user_profile(analysis, user_profile)
        
        # 上下文增强
        if context:
            analysis = await self._enhance_with_context(analysis, context)
        
        return analysis
    
    async def _calculate_dynamic_weights(
        self,
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext],
        analysis: QueryAnalysis
    ) -> Dict[str, float]:
        """计算动态权重"""
        
        weights = self.learned_weights.copy()
        
        # 用户角色调整
        if user_profile and user_profile.role in self.role_weight_adjustments:
            role_adj = self.role_weight_adjustments[user_profile.role]
            for key, adjustment in role_adj.items():
                if key in weights:
                    weights[key] = adjustment
        
        # 上下文类型调整
        if context and context.context_type in self.context_weight_adjustments:
            ctx_adj = self.context_weight_adjustments[context.context_type]
            for key, adjustment in ctx_adj.items():
                if key in weights:
                    weights[key] = adjustment
        
        # 成本敏感度调整
        if user_profile and user_profile.cost_sensitivity > 0.7:
            weights['cost_efficiency'] *= 1.5
            weights['domain_match'] *= 0.9
        
        # 速度偏好调整
        if user_profile and user_profile.speed_preference > 0.7:
            weights['response_speed'] *= 2.0
            weights['complexity_match'] *= 0.8
        
        # 归一化权重
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}
    
    async def _enhanced_source_evaluation(
        self,
        analysis: QueryAnalysis,
        weights: Dict[str, float],
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext]
    ) -> Dict[KnowledgeSourceType, float]:
        """增强版知识源评估"""
        
        scores = {}
        
        for source_type, capability in self.source_capabilities.items():
            score = 0.0
            
            # 基础评分
            score += self._calculate_domain_match(analysis, capability) * weights.get('domain_match', 0.4)
            score += self._calculate_complexity_match(analysis, capability) * weights.get('complexity_match', 0.25)
            score += self._calculate_special_match(analysis, capability) * weights.get('special_requirements', 0.2)
            score += self._calculate_cost_efficiency(capability) * weights.get('cost_efficiency', 0.1)
            score += self._calculate_speed_score(capability) * weights.get('response_speed', 0.05)
            
            # 上下文连续性奖励
            if context and context.previous_decisions:
                consistency_bonus = self._calculate_consistency_bonus(
                    source_type, context.previous_decisions
                )
                score += consistency_bonus * weights.get('consistency_bonus', 0.0)
            
            # 用户历史偏好
            if user_profile:
                preference_bonus = self._calculate_preference_bonus(
                    source_type, user_profile
                )
                score += preference_bonus * 0.1
            
            scores[source_type] = max(0.0, min(1.0, score))
        
        return scores
    
    async def _make_enhanced_decision(
        self,
        analysis: QueryAnalysis,
        scores: Dict[KnowledgeSourceType, float],
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext]
    ) -> KnowledgeSourceDecision:
        """增强版决策制定"""
        
        # 排序得分
        sorted_sources = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 检查置信度差异
        if len(sorted_sources) >= 2:
            top_score = sorted_sources[0][1]
            second_score = sorted_sources[1][1]
            confidence_delta = top_score - second_score
            
            # 如果差异很小，考虑融合策略
            if confidence_delta < 0.15 and self._should_use_fusion(user_profile):
                return await self._create_fusion_decision(
                    analysis, sorted_sources[:2], user_profile, context
                )
        
        # 常规单源决策
        primary_source = sorted_sources[0][0]
        primary_score = sorted_sources[0][1]
        
        # 选择辅助源
        secondary_sources = [
            source for source, score in sorted_sources[1:3] 
            if score > 0.6
        ]
        
        # 生成推理
        reasoning = self._generate_enhanced_reasoning(
            analysis, primary_source, primary_score, user_profile, context
        )
        
        # 估算成本和延迟
        capability = self.source_capabilities[primary_source]
        estimated_cost = capability.cost_per_query
        expected_latency = capability.avg_latency
        
        # 应用用户偏好调整
        if user_profile:
            if user_profile.speed_preference > 0.8:
                expected_latency *= 0.8  # 优化延迟
            if user_profile.cost_sensitivity > 0.8:
                estimated_cost *= 0.9   # 成本优化
        
        return KnowledgeSourceDecision(
            primary_source=primary_source,
            secondary_sources=secondary_sources,
            reasoning=reasoning,
            confidence=primary_score,
            estimated_cost=estimated_cost,
            expected_latency=expected_latency
        )
    
    async def add_feedback(self, feedback: RoutingFeedback):
        """添加用户反馈"""
        self.feedback_data.append(feedback)
        
        # 触发学习更新
        if len(self.feedback_data) % 10 == 0:  # 每10个反馈学习一次
            await self._update_learned_weights()
        
        logger.info(f"📝 收到反馈: {feedback.feedback_type.value}")
    
    async def _update_learned_weights(self):
        """基于反馈更新学习权重"""
        
        # 简单的反馈学习算法
        positive_feedback = [f for f in self.feedback_data[-50:] 
                           if f.feedback_type == FeedbackType.THUMBS_UP]
        negative_feedback = [f for f in self.feedback_data[-50:] 
                           if f.feedback_type == FeedbackType.THUMBS_DOWN]
        
        if len(positive_feedback) + len(negative_feedback) < 10:
            return
        
        # 计算反馈比例
        success_rate = len(positive_feedback) / (len(positive_feedback) + len(negative_feedback))
        
        # 根据成功率调整权重
        if success_rate < 0.7:  # 如果成功率低于70%
            # 增加保守策略的权重
            self.learned_weights['cost_efficiency'] *= 1.1
            self.learned_weights['domain_match'] *= 1.1
            self.learned_weights['complexity_match'] *= 0.9
        elif success_rate > 0.9:  # 如果成功率高于90%
            # 可以更激进一些
            self.learned_weights['complexity_match'] *= 1.1
            self.learned_weights['special_requirements'] *= 1.1
        
        # 重新归一化
        total = sum(self.learned_weights.values())
        self.learned_weights = {k: v/total for k, v in self.learned_weights.items()}
        
        logger.info(f"🧠 权重学习更新完成，成功率: {success_rate:.2%}")
    
    async def _execute_fallback_strategy(
        self,
        query: str,
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext],
        error: str
    ) -> KnowledgeSourceDecision:
        """执行降级策略"""
        
        logger.warning(f"⚠️ 执行降级策略，原因: {error}")
        
        # 降级策略1：如果知识库不可用，使用AI训练数据
        if "knowledge_base" in error.lower():
            return KnowledgeSourceDecision(
                primary_source=KnowledgeSourceType.AI_TRAINING_DATA,
                secondary_sources=[],
                reasoning=f"知识库不可用，降级到AI训练数据。原因: {error}",
                confidence=0.6,
                estimated_cost=1.0,
                expected_latency=2.0
            )
        
        # 降级策略2：如果网络搜索失败，使用本地知识库
        elif "web_search" in error.lower():
            return KnowledgeSourceDecision(
                primary_source=KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE,
                secondary_sources=[KnowledgeSourceType.AI_TRAINING_DATA],
                reasoning=f"网络搜索失败，降级到本地知识库。原因: {error}",
                confidence=0.7,
                estimated_cost=0.1,
                expected_latency=0.2
            )
        
        # 默认降级：使用最稳定的本地知识库
        return KnowledgeSourceDecision(
            primary_source=KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE,
            secondary_sources=[],
            reasoning=f"系统异常，使用默认降级策略。原因: {error}",
            confidence=0.5,
            estimated_cost=0.1,
            expected_latency=0.2
        )
    
    async def _log_decision(
        self,
        log_id: str,
        query: str,
        analysis: Optional[QueryAnalysis],
        source_scores: Dict[KnowledgeSourceType, float],
        decision: KnowledgeSourceDecision,
        user_profile: Optional[UserProfile],
        context: Optional[ConversationContext],
        start_time: datetime,
        success: bool,
        error_message: Optional[str] = None
    ):
        """记录决策审计日志"""
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        audit_log = DecisionAuditLog(
            log_id=log_id,
            timestamp=datetime.now(),
            user_id=user_profile.user_id if user_profile else "anonymous",
            query=query,
            query_analysis=analysis,
            all_source_scores=source_scores,
            final_decision=decision,
            router_type="EnhancedKnowledgeRouter",
            router_version="2.0.0",
            execution_time_ms=execution_time,
            context=context,
            user_profile=user_profile,
            success=success,
            error_message=error_message
        )
        
        self.audit_logs.append(audit_log)
        
        # 写入文件
        await self._write_audit_log(audit_log)
        
        logger.debug(f"📊 决策日志已记录: {log_id}")
    
    def get_router_info(self) -> Dict[str, Any]:
        """获取路由器信息"""
        return {
            "router_type": "EnhancedKnowledgeRouter",
            "version": "2.0.0",
            "features": [
                "dynamic_weights",
                "user_profiling", 
                "context_awareness",
                "feedback_learning",
                "decision_audit",
                "fallback_strategies"
            ],
            "base_weights": self.base_weights,
            "learned_weights": self.learned_weights,
            "total_decisions": len(self.audit_logs),
            "feedback_count": len(self.feedback_data),
            "supported_user_roles": [role.value for role in UserRole],
            "supported_context_types": [ctx.value for ctx in ContextType]
        }
    
    # 辅助方法实现
    def _load_source_capabilities(self) -> Dict[KnowledgeSourceType, KnowledgeSourceCapability]:
        """加载知识源能力配置"""
        # 这里可以从配置文件或数据库加载
        # 暂时返回基础配置
        from .knowledge_router import get_knowledge_router
        basic_router = get_knowledge_router()
        return basic_router.source_capabilities
    
    def _generate_log_id(self, query: str) -> str:
        """生成日志ID"""
        content = f"{query}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def _basic_query_analysis(self, query: str) -> QueryAnalysis:
        """基础查询分析"""
        # 复用原有的查询分析逻辑
        from .knowledge_router import get_knowledge_router
        basic_router = get_knowledge_router()
        return await basic_router._analyze_query(query, {})
    
    # 更多辅助方法...
    async def _enhance_with_user_profile(self, analysis: QueryAnalysis, profile: UserProfile) -> QueryAnalysis:
        """基于用户画像增强分析"""
        # 根据用户角色调整复杂度判断
        if profile.role == UserRole.EXPERT:
            if analysis.complexity == QueryComplexity.SIMPLE:
                analysis.complexity = QueryComplexity.MODERATE
        elif profile.role == UserRole.BEGINNER:
            if analysis.complexity == QueryComplexity.COMPLEX:
                analysis.complexity = QueryComplexity.MODERATE
        
        return analysis
    
    async def _enhance_with_context(self, analysis: QueryAnalysis, context: ConversationContext) -> QueryAnalysis:
        """基于对话上下文增强分析"""
        # 如果是后续问题，继承之前的领域焦点
        if context.context_type == ContextType.FOLLOW_UP and context.knowledge_domain_focus:
            analysis.domain = context.knowledge_domain_focus
        
        return analysis
    
    def _calculate_consistency_bonus(
        self, 
        source_type: KnowledgeSourceType, 
        previous_decisions: List[KnowledgeSourceDecision]
    ) -> float:
        """计算上下文一致性奖励"""
        if not previous_decisions:
            return 0.0
        
        # 如果最近的决策都是同一个源，给予一致性奖励
        recent_sources = [d.primary_source for d in previous_decisions[-3:]]
        if all(s == source_type for s in recent_sources):
            return 0.2
        
        return 0.0
    
    def _calculate_preference_bonus(
        self, 
        source_type: KnowledgeSourceType, 
        user_profile: UserProfile
    ) -> float:
        """计算用户偏好奖励"""
        # 基于用户历史交互计算偏好
        if not user_profile.interaction_history:
            return 0.0
        
        # 统计用户对不同源的满意度
        source_satisfaction = {}
        for interaction in user_profile.interaction_history[-20:]:  # 最近20次交互
            source = interaction.get('source')
            satisfaction = interaction.get('satisfaction', 0.5)
            if source:
                source_satisfaction[source] = source_satisfaction.get(source, []) + [satisfaction]
        
        if source_type.value in source_satisfaction:
            avg_satisfaction = sum(source_satisfaction[source_type.value]) / len(source_satisfaction[source_type.value])
            return (avg_satisfaction - 0.5) * 0.4  # 转换为-0.2到0.2的奖励
        
        return 0.0
    
    async def _write_audit_log(self, audit_log: DecisionAuditLog):
        """写入审计日志到文件"""
        try:
            log_dict = {
                "log_id": audit_log.log_id,
                "timestamp": audit_log.timestamp.isoformat(),
                "user_id": audit_log.user_id,
                "query": audit_log.query,
                "decision": audit_log.final_decision.primary_source.value,
                "confidence": audit_log.final_decision.confidence,
                "execution_time_ms": audit_log.execution_time_ms,
                "success": audit_log.success,
                "error_message": audit_log.error_message
            }
            
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_dict, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"❌ 写入审计日志失败: {e}")


# 具体路由器实现

class CostFirstRouter(AbstractRouter):
    """成本优先路由器"""
    
    async def route_query(
        self, 
        query: str, 
        user_profile: Optional[UserProfile] = None,
        context: Optional[ConversationContext] = None
    ) -> KnowledgeSourceDecision:
        """总是选择成本最低的知识源"""
        
        return KnowledgeSourceDecision(
            primary_source=KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE,
            secondary_sources=[],
            reasoning="成本优先策略：选择本地知识库（成本最低）",
            confidence=0.8,
            estimated_cost=0.1,
            expected_latency=0.2
        )
    
    def get_router_info(self) -> Dict[str, Any]:
        return {
            "router_type": "CostFirstRouter",
            "version": "1.0.0",
            "strategy": "always_choose_lowest_cost"
        }


class MLBasedRouter(AbstractRouter):
    """基于机器学习的路由器（占位符）"""
    
    def __init__(self):
        self.model = None  # 这里可以加载预训练的分类模型
    
    async def route_query(
        self, 
        query: str, 
        user_profile: Optional[UserProfile] = None,
        context: Optional[ConversationContext] = None
    ) -> KnowledgeSourceDecision:
        """使用ML模型进行路由决策"""
        
        # 占位符实现，实际应该使用训练好的模型
        # features = self._extract_features(query, user_profile, context)
        # prediction = self.model.predict(features)
        
        return KnowledgeSourceDecision(
            primary_source=KnowledgeSourceType.AI_TRAINING_DATA,
            secondary_sources=[],
            reasoning="ML模型预测结果（占位符实现）",
            confidence=0.75,
            estimated_cost=1.0,
            expected_latency=2.0
        )
    
    def get_router_info(self) -> Dict[str, Any]:
        return {
            "router_type": "MLBasedRouter",
            "version": "1.0.0",
            "model_type": "placeholder",
            "features": ["query_embedding", "user_profile", "context_history"]
        }


# 路由器工厂
class RouterFactory:
    """路由器工厂"""
    
    _routers = {
        "enhanced": EnhancedKnowledgeRouter,
        "cost_first": CostFirstRouter,
        "ml_based": MLBasedRouter
    }
    
    @classmethod
    def create_router(cls, router_type: str, config: Dict[str, Any] = None) -> AbstractRouter:
        """创建指定类型的路由器"""
        
        if router_type not in cls._routers:
            raise ValueError(f"不支持的路由器类型: {router_type}")
        
        router_class = cls._routers[router_type]
        
        if router_type == "enhanced":
            return router_class(config)
        else:
            return router_class()
    
    @classmethod
    def get_available_routers(cls) -> List[str]:
        """获取可用的路由器类型"""
        return list(cls._routers.keys())


# 全局增强路由器实例
_enhanced_router_instance: Optional[EnhancedKnowledgeRouter] = None


def get_enhanced_router() -> EnhancedKnowledgeRouter:
    """获取增强路由器单例"""
    global _enhanced_router_instance
    
    if _enhanced_router_instance is None:
        _enhanced_router_instance = EnhancedKnowledgeRouter()
    
    return _enhanced_router_instance 