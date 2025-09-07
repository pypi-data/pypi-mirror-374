"""
集成语义缓存的增强知识路由器

将语义缓存系统集成到增强知识路由器中，实现智能缓存和路由的协同工作。
在路由决策前先检查缓存，在生成响应后智能缓存，大幅提升性能和降低成本。

Author: ADC Team
Date: 2024-12-19
Version: 2.1.0
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .enhanced_knowledge_router import (
    EnhancedKnowledgeRouter, UserProfile, ConversationContext,
    KnowledgeSourceDecision, QueryAnalysis
)
from .semantic_cache import SemanticCache, CacheHitResult, CachePriority
from .intelligent_cache_strategy import (
    IntelligentCacheStrategy, CacheDecisionContext, CacheStrategy
)

logger = logging.getLogger(__name__)

class CacheEnhancedKnowledgeRouter(EnhancedKnowledgeRouter):
    """集成语义缓存的增强知识路由器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # 初始化语义缓存系统
        self.semantic_cache = SemanticCache(
            similarity_threshold=config.get('cache_similarity_threshold', 0.85),
            max_cache_size=config.get('max_cache_size', 10000)
        )
        
        # 初始化智能缓存策略
        cache_strategy_type = config.get('cache_strategy', 'hybrid')
        self.cache_strategy = IntelligentCacheStrategy(
            strategy_type=CacheStrategy(cache_strategy_type),
            cost_threshold=config.get('cache_cost_threshold', 0.1),
            quality_threshold=config.get('cache_quality_threshold', 0.6)
        )
        
        # 缓存统计
        self.cache_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cost_saved': 0.0,
            'total_time_saved': 0.0
        }
        
        logger.info("🎯 缓存增强知识路由器初始化完成")
    
    async def initialize(self):
        """初始化路由器"""
        await super().initialize()
        await self.semantic_cache.initialize()
        logger.info("✅ 缓存增强知识路由器初始化成功")
    
    async def route_query(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        context: Optional[ConversationContext] = None
    ) -> KnowledgeSourceDecision:
        """路由查询（集成缓存）"""
        start_time = datetime.now()
        self.cache_stats['total_queries'] += 1
        
        try:
            # 🎯 步骤1: 检查语义缓存
            cache_result = await self._check_semantic_cache(query, user_profile)
            
            if cache_result.hit:
                # 缓存命中，直接返回缓存结果
                decision = await self._create_cached_decision(cache_result, query)
                
                # 更新统计
                self.cache_stats['cache_hits'] += 1
                self.cache_stats['total_cost_saved'] += cache_result.cost_saved
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                self.cache_stats['total_time_saved'] += max(0, 2000 - execution_time)  # 假设正常路由需要2秒
                
                logger.info(f"🎯 缓存命中: {query[:50]}... (节省成本: ${cache_result.cost_saved:.3f})")
                return decision
            
            # 🔍 步骤2: 缓存未命中，执行正常路由
            self.cache_stats['cache_misses'] += 1
            decision = await super().route_query(query, user_profile, context)
            
            # 🗃️ 步骤3: 智能缓存决策
            await self._intelligent_cache_response(query, decision, user_profile, start_time)
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ 缓存增强路由失败: {e}")
            # 降级到基础路由
            return await super().route_query(query, user_profile, context)
    
    async def _check_semantic_cache(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None
    ) -> CacheHitResult:
        """检查语义缓存"""
        try:
            user_role = user_profile.role if user_profile else None
            if user_role is None:
                return CacheHitResult(hit=False, reason="用户角色未知")
            
            return await self.semantic_cache.get_cached_response(query, user_role)
            
        except Exception as e:
            logger.error(f"❌ 缓存检查失败: {e}")
            return CacheHitResult(hit=False, reason=f"缓存检查错误: {e}")
    
    async def _create_cached_decision(
        self,
        cache_result: CacheHitResult,
        query: str
    ) -> KnowledgeSourceDecision:
        """基于缓存结果创建决策"""
        from .knowledge_router import KnowledgeSourceType
        
        return KnowledgeSourceDecision(
            primary_source=KnowledgeSourceType.CACHE,  # 需要添加缓存源类型
            secondary_sources=[],
            reasoning=f"缓存命中 (相似度: {cache_result.similarity_score:.3f}) - {cache_result.entry.original_query[:50]}...",
            confidence=min(0.95, cache_result.similarity_score + 0.1),
            estimated_cost=0.001,  # 缓存成本极低
            expected_latency=0.1,
            metadata={
                'cache_hit': True,
                'original_query': cache_result.entry.original_query,
                'cache_entry_id': cache_result.entry.entry_id,
                'similarity_score': cache_result.similarity_score,
                'cached_response': cache_result.entry.response,
                'cache_timestamp': cache_result.entry.timestamp.isoformat(),
                'access_count': cache_result.entry.access_count
            }
        )
    
    async def _intelligent_cache_response(
        self,
        query: str,
        decision: KnowledgeSourceDecision,
        user_profile: Optional[UserProfile],
        start_time: datetime
    ):
        """智能缓存响应"""
        try:
            if not user_profile:
                logger.debug("🚫 用户画像缺失，跳过缓存")
                return
            
            # 模拟获取响应内容（在实际实现中，这应该从决策执行结果获取）
            response_content = decision.metadata.get('generated_response', '')
            if not response_content:
                logger.debug("🚫 响应内容为空，跳过缓存")
                return
            
            # 计算响应时间和质量分数
            response_time = (datetime.now() - start_time).total_seconds()
            quality_score = min(decision.confidence * 1.1, 1.0)  # 基于置信度估算质量
            
            # 创建缓存决策上下文
            cache_context = CacheDecisionContext(
                query=query,
                response=response_content,
                user_role=user_profile.role,
                generation_cost=decision.estimated_cost,
                quality_score=quality_score,
                response_time=response_time,
                user_satisfaction=None,  # 暂时未知
                metadata={
                    'decision_confidence': decision.confidence,
                    'primary_source': decision.primary_source.value,
                    'reasoning': decision.reasoning
                }
            )
            
            # 使用智能策略决定是否缓存
            cache_decision = await self.cache_strategy.make_cache_decision(cache_context)
            
            if cache_decision.should_cache:
                # 执行缓存
                success = await self.semantic_cache.cache_response(
                    query=query,
                    response=response_content,
                    user_role=user_profile.role,
                    cost_saved=cache_decision.expected_value,
                    quality_score=quality_score,
                    priority=cache_decision.priority,
                    ttl_seconds=cache_decision.ttl_seconds,
                    metadata={
                        'decision_reasoning': cache_decision.reasoning,
                        'decision_confidence': cache_decision.confidence,
                        'original_decision': decision.__dict__
                    }
                )
                
                if success:
                    logger.info(f"✅ 智能缓存成功: {query[:50]}... (优先级: {cache_decision.priority.value})")
                else:
                    logger.warning(f"⚠️ 缓存失败: {query[:50]}...")
            else:
                logger.debug(f"🚫 跳过缓存: {query[:50]}... - {cache_decision.reasoning}")
                
        except Exception as e:
            logger.error(f"❌ 智能缓存处理失败: {e}")
    
    async def provide_cache_feedback(
        self,
        query: str,
        user_satisfaction: float,
        user_profile: Optional[UserProfile] = None
    ):
        """提供缓存反馈"""
        try:
            # 这里可以实现缓存质量的反馈学习
            # 根据用户满意度调整缓存策略
            
            if user_satisfaction < 0.3:
                # 用户不满意，可能需要调整缓存策略
                logger.info(f"📉 收到负面反馈，用户满意度: {user_satisfaction}")
                
                # 如果是缓存响应导致的不满意，可以考虑无效化相关缓存
                if user_profile:
                    await self.semantic_cache.invalidate_cache(
                        query_pattern=query[:20],  # 部分查询模式
                        user_role=user_profile.role
                    )
            
            elif user_satisfaction > 0.8:
                # 用户满意，可以提高相似查询的缓存优先级
                logger.info(f"📈 收到正面反馈，用户满意度: {user_satisfaction}")
            
        except Exception as e:
            logger.error(f"❌ 缓存反馈处理失败: {e}")
    
    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """获取缓存性能报告"""
        try:
            # 获取缓存统计
            cache_stats = await self.semantic_cache.get_cache_stats()
            
            # 计算性能指标
            hit_rate = self.cache_stats['cache_hits'] / max(self.cache_stats['total_queries'], 1)
            cost_efficiency = self.cache_stats['total_cost_saved'] / max(self.cache_stats['total_queries'], 1)
            time_efficiency = self.cache_stats['total_time_saved'] / max(self.cache_stats['total_queries'], 1)
            
            return {
                'cache_performance': {
                    'hit_rate': hit_rate,
                    'total_queries': self.cache_stats['total_queries'],
                    'cache_hits': self.cache_stats['cache_hits'],
                    'cache_misses': self.cache_stats['cache_misses'],
                    'cost_efficiency': cost_efficiency,
                    'time_efficiency': time_efficiency,
                    'total_cost_saved': self.cache_stats['total_cost_saved'],
                    'total_time_saved_seconds': self.cache_stats['total_time_saved'] / 1000
                },
                'cache_storage': {
                    'total_entries': cache_stats.total_entries,
                    'active_entries': cache_stats.active_entries,
                    'expired_entries': cache_stats.expired_entries,
                    'cache_size_mb': cache_stats.cache_size_mb,
                    'average_similarity': cache_stats.average_similarity
                },
                'cost_analysis': {
                    'cost_per_query_without_cache': 0.85,  # 假设值
                    'cost_per_query_with_cache': cost_efficiency,
                    'cost_reduction_percentage': (1 - cost_efficiency / 0.85) * 100,
                    'monthly_cost_savings': self.cache_stats['total_cost_saved'] * 30  # 假设月度
                },
                'recommendations': await self._generate_cache_recommendations(hit_rate, cost_efficiency)
            }
            
        except Exception as e:
            logger.error(f"❌ 生成缓存性能报告失败: {e}")
            return {'error': str(e)}
    
    async def _generate_cache_recommendations(
        self,
        hit_rate: float,
        cost_efficiency: float
    ) -> List[str]:
        """生成缓存优化建议"""
        recommendations = []
        
        if hit_rate < 0.3:
            recommendations.append("命中率较低，建议降低相似度阈值从0.85到0.80")
            recommendations.append("考虑增加缓存时间，提高缓存利用率")
        
        if cost_efficiency < 0.1:
            recommendations.append("成本效率较低，建议提高高成本查询的缓存优先级")
            recommendations.append("考虑实施更激进的缓存策略")
        
        if hit_rate > 0.7:
            recommendations.append("缓存性能良好，可以考虑扩大缓存容量")
        
        if cost_efficiency > 0.5:
            recommendations.append("成本节省显著，建议维持当前缓存策略")
        
        return recommendations
    
    async def optimize_cache_strategy(self) -> Dict[str, Any]:
        """优化缓存策略"""
        try:
            # 获取性能数据
            performance_report = await self.get_cache_performance_report()
            cache_performance = performance_report.get('cache_performance', {})
            
            # 使用智能策略进行优化
            optimization_result = await self.cache_strategy.optimize_strategy(cache_performance)
            
            # 优化语义缓存
            cache_optimization = await self.semantic_cache.optimize_cache()
            
            return {
                'strategy_optimization': optimization_result,
                'cache_optimization': cache_optimization,
                'timestamp': datetime.now().isoformat(),
                'next_optimization': (datetime.now().timestamp() + 3600 * 24)  # 24小时后
            }
            
        except Exception as e:
            logger.error(f"❌ 缓存策略优化失败: {e}")
            return {'error': str(e)}
    
    def get_router_info(self) -> Dict[str, Any]:
        """获取路由器信息（扩展版）"""
        base_info = super().get_router_info()
        
        # 添加缓存相关信息
        cache_info = {
            'cache_enabled': True,
            'cache_similarity_threshold': self.semantic_cache.similarity_threshold,
            'cache_max_size': self.semantic_cache.max_cache_size,
            'cache_strategy': self.cache_strategy.strategy_type.value,
            'cache_stats': self.cache_stats
        }
        
        base_info.update(cache_info)
        base_info['version'] = '2.1.0'  # 更新版本号
        base_info['features'].append('semantic_cache')
        base_info['features'].append('intelligent_cache_strategy')
        
        return base_info

# 工厂函数
def create_cache_enhanced_router(config: Optional[Dict] = None) -> CacheEnhancedKnowledgeRouter:
    """创建缓存增强知识路由器"""
    default_config = {
        'cache_similarity_threshold': 0.85,
        'max_cache_size': 10000,
        'cache_strategy': 'hybrid',
        'cache_cost_threshold': 0.1,
        'cache_quality_threshold': 0.6
    }
    
    if config:
        default_config.update(config)
    
    return CacheEnhancedKnowledgeRouter(default_config) 