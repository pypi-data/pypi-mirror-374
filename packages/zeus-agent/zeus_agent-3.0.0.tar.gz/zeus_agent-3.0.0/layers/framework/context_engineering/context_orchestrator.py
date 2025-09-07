"""
Context Orchestrator - 上下文编排器
负责协调整个上下文工程流程，管理上下文生命周期
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .context_collectors import ContextCollectorRegistry
from .context_optimizers import ContextOptimizerRegistry
from .context_analyzers import ContextAnalyzerRegistry
from .context_stores import ContextStoreRegistry
from .context_learners import ContextLearnerRegistry
from ..abstractions.task import UniversalTask
from ..abstractions.agent import UniversalAgent

logger = logging.getLogger(__name__)


class ContextBundle:
    """上下文包"""
    
    def __init__(self, 
                 contexts: List[Dict[str, Any]],
                 metadata: Dict[str, Any],
                 created_at: datetime = None):
        self.contexts = contexts
        self.metadata = metadata
        self.created_at = created_at or datetime.now()
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "contexts": self.contexts,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "version": self.version
        }
    
    def get_total_tokens(self) -> int:
        """获取总token数量"""
        return sum(ctx.get("estimated_tokens", 0) for ctx in self.contexts)
    
    def get_context_count(self) -> int:
        """获取上下文数量"""
        return len(self.contexts)


class ContextOrchestrator:
    """上下文编排器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 初始化子组件
        self.collectors = ContextCollectorRegistry()
        self.optimizers = ContextOptimizerRegistry()
        self.analyzers = ContextAnalyzerRegistry()
        self.stores = ContextStoreRegistry()
        self.learners = ContextLearnerRegistry()
        
        # 配置参数
        self.max_context_size = self.config.get("max_context_size", 8000)
        self.relevance_threshold = self.config.get("relevance_threshold", 0.3)
        self.optimization_level = self.config.get("optimization_level", "basic")
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def orchestrate_context_building(self, 
                                         task: UniversalTask,
                                         agent: UniversalAgent,
                                         user_context: Dict[str, Any]) -> ContextBundle:
        """编排上下文构建流程"""
        
        try:
            self.logger.info(f"Starting context orchestration for task: {task.content[:100]}...")
            
            # 1. 收集上下文
            raw_contexts = await self._collect_all_contexts(task, agent, user_context)
            self.logger.info(f"Collected {len(raw_contexts)} raw contexts")
            
            # 2. 分析上下文
            context_analysis = await self._analyze_contexts(raw_contexts, task)
            self.logger.info(f"Context analysis completed with {len(context_analysis)} insights")
            
            # 3. 优化上下文
            optimized_contexts = await self._optimize_contexts(raw_contexts, context_analysis)
            self.logger.info(f"Optimized to {len(optimized_contexts)} contexts")
            
            # 4. 构建上下文包
            context_bundle = await self._build_context_bundle(optimized_contexts, task)
            self.logger.info(f"Context bundle created with {context_bundle.get_total_tokens()} tokens")
            
            # 5. 学习上下文使用
            await self._learn_context_usage(context_bundle, task)
            
            # 6. 存储上下文包
            await self._store_context_bundle(context_bundle, task)
            
            self.logger.info("Context orchestration completed successfully")
            return context_bundle
            
        except Exception as e:
            self.logger.error(f"Context orchestration failed: {e}")
            # 返回基础上下文包
            return await self._create_fallback_context_bundle(task, agent)
    
    async def _collect_all_contexts(self, 
                                  task: UniversalTask,
                                  agent: UniversalAgent,
                                  user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """收集所有上下文"""
        
        contexts = []
        
        # 并行收集不同类型的上下文
        collection_tasks = [
            self.collectors.collect_user_context(task, user_context),
            self.collectors.collect_system_context(task, agent),
            self.collectors.collect_domain_context(task),
            self.collectors.collect_temporal_context(),
            self.collectors.collect_task_context(task),
            self.collectors.collect_agent_context(agent)
        ]
        
        # 执行收集任务
        collection_results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # 处理结果
        for result in collection_results:
            if isinstance(result, Exception):
                self.logger.warning(f"Context collection failed: {result}")
                continue
            
            if result and isinstance(result, list):
                contexts.extend(result)
        
        return contexts
    
    async def _analyze_contexts(self, 
                              contexts: List[Dict[str, Any]], 
                              task: UniversalTask) -> Dict[str, Any]:
        """分析上下文"""
        
        analysis_results = {}
        
        # 相关性分析
        relevance_analysis = await self.analyzers.analyze_relevance(contexts, task)
        analysis_results["relevance"] = relevance_analysis
        
        # 重要性分析
        importance_analysis = await self.analyzers.analyze_importance(contexts, task)
        analysis_results["importance"] = importance_analysis
        
        # 质量分析
        quality_analysis = await self.analyzers.analyze_quality(contexts)
        analysis_results["quality"] = quality_analysis
        
        # 冲突分析
        conflict_analysis = await self.analyzers.analyze_conflicts(contexts)
        analysis_results["conflicts"] = conflict_analysis
        
        return analysis_results
    
    async def _optimize_contexts(self, 
                               contexts: List[Dict[str, Any]], 
                               analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """优化上下文"""
        
        # 根据优化级别选择优化策略
        if self.optimization_level == "basic":
            return await self._basic_optimization(contexts, analysis)
        elif self.optimization_level == "advanced":
            return await self._advanced_optimization(contexts, analysis)
        else:
            return await self._intelligent_optimization(contexts, analysis)
    
    async def _basic_optimization(self, 
                                contexts: List[Dict[str, Any]], 
                                analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基础优化"""
        
        # 过滤低相关性上下文
        relevance_threshold = analysis.get("relevance", {}).get("threshold", self.relevance_threshold)
        filtered_contexts = [
            ctx for ctx in contexts 
            if ctx.get("relevance_score", 0) >= relevance_threshold
        ]
        
        # 按重要性排序
        filtered_contexts.sort(
            key=lambda x: x.get("importance_score", 0), 
            reverse=True
        )
        
        # 限制大小
        total_tokens = 0
        optimized_contexts = []
        
        for context in filtered_contexts:
            context_tokens = context.get("estimated_tokens", 0)
            if total_tokens + context_tokens <= self.max_context_size:
                optimized_contexts.append(context)
                total_tokens += context_tokens
            else:
                break
        
        return optimized_contexts
    
    async def _advanced_optimization(self, 
                                   contexts: List[Dict[str, Any]], 
                                   analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """高级优化"""
        
        # 使用优化器进行高级优化
        return await self.optimizers.optimize_contexts(
            contexts=contexts,
            analysis=analysis,
            max_tokens=self.max_context_size,
            optimization_strategy="advanced"
        )
    
    async def _intelligent_optimization(self, 
                                      contexts: List[Dict[str, Any]], 
                                      analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """智能优化"""
        
        # 使用机器学习模型进行智能优化
        return await self.optimizers.intelligent_optimize(
            contexts=contexts,
            analysis=analysis,
            max_tokens=self.max_context_size,
            learning_model=self.learners.get_optimization_model()
        )
    
    async def _build_context_bundle(self, 
                                  contexts: List[Dict[str, Any]], 
                                  task: UniversalTask) -> ContextBundle:
        """构建上下文包"""
        
        # 计算元数据
        metadata = {
            "task_id": task.id,
            "task_type": task.task_type.value,
            "context_count": len(contexts),
            "total_tokens": sum(ctx.get("estimated_tokens", 0) for ctx in contexts),
            "optimization_level": self.optimization_level,
            "relevance_threshold": self.relevance_threshold,
            "created_at": datetime.now().isoformat()
        }
        
        # 创建上下文包
        context_bundle = ContextBundle(
            contexts=contexts,
            metadata=metadata
        )
        
        return context_bundle
    
    async def _learn_context_usage(self, 
                                 context_bundle: ContextBundle, 
                                 task: UniversalTask):
        """学习上下文使用"""
        
        try:
            # 记录上下文使用模式
            await self.learners.record_usage_pattern(
                context_bundle=context_bundle,
                task=task,
                usage_metadata={
                    "timestamp": datetime.now().isoformat(),
                    "bundle_size": context_bundle.get_context_count(),
                    "total_tokens": context_bundle.get_total_tokens()
                }
            )
            
            # 更新学习模型
            await self.learners.update_learning_model(context_bundle, task)
            
        except Exception as e:
            self.logger.warning(f"Context learning failed: {e}")
    
    async def _store_context_bundle(self, 
                                  context_bundle: ContextBundle, 
                                  task: UniversalTask):
        """存储上下文包"""
        
        try:
            await self.stores.store_context_bundle(
                bundle_id=f"bundle_{task.id}_{int(datetime.now().timestamp())}",
                context_bundle=context_bundle,
                task=task
            )
        except Exception as e:
            self.logger.warning(f"Context bundle storage failed: {e}")
    
    async def _create_fallback_context_bundle(self, 
                                            task: UniversalTask, 
                                            agent: UniversalAgent) -> ContextBundle:
        """创建回退上下文包"""
        
        fallback_contexts = [
            {
                "type": "system",
                "content": f"You are a {agent.name} assistant.",
                "relevance_score": 1.0,
                "importance_score": 1.0,
                "estimated_tokens": 10
            },
            {
                "type": "task",
                "content": task.content,
                "relevance_score": 1.0,
                "importance_score": 1.0,
                "estimated_tokens": len(task.content.split())
            }
        ]
        
        metadata = {
            "task_id": task.id,
            "fallback": True,
            "context_count": len(fallback_contexts),
            "total_tokens": sum(ctx.get("estimated_tokens", 0) for ctx in fallback_contexts),
            "created_at": datetime.now().isoformat()
        }
        
        return ContextBundle(
            contexts=fallback_contexts,
            metadata=metadata
        )
    
    async def get_context_analytics(self) -> Dict[str, Any]:
        """获取上下文分析数据"""
        
        analytics = {
            "orchestration_stats": await self._get_orchestration_stats(),
            "collection_stats": await self.collectors.get_collection_stats(),
            "optimization_stats": await self.optimizers.get_optimization_stats(),
            "learning_stats": await self.learners.get_learning_stats(),
            "storage_stats": await self.stores.get_storage_stats()
        }
        
        return analytics
    
    async def _get_orchestration_stats(self) -> Dict[str, Any]:
        """获取编排统计"""
        
        return {
            "total_orchestrations": getattr(self, '_total_orchestrations', 0),
            "successful_orchestrations": getattr(self, '_successful_orchestrations', 0),
            "average_context_count": getattr(self, '_average_context_count', 0),
            "average_tokens_per_bundle": getattr(self, '_average_tokens_per_bundle', 0),
            "optimization_level_usage": {
                "basic": getattr(self, '_basic_optimizations', 0),
                "advanced": getattr(self, '_advanced_optimizations', 0),
                "intelligent": getattr(self, '_intelligent_optimizations', 0)
            }
        }
    
    async def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        
        self.config.update(new_config)
        
        # 更新相关参数
        if "max_context_size" in new_config:
            self.max_context_size = new_config["max_context_size"]
        
        if "relevance_threshold" in new_config:
            self.relevance_threshold = new_config["relevance_threshold"]
        
        if "optimization_level" in new_config:
            self.optimization_level = new_config["optimization_level"]
        
        self.logger.info(f"Configuration updated: {new_config}")
    
    async def shutdown(self):
        """关闭编排器"""
        
        try:
            # 关闭子组件
            await self.collectors.shutdown()
            await self.optimizers.shutdown()
            await self.analyzers.shutdown()
            await self.stores.shutdown()
            await self.learners.shutdown()
            
            self.logger.info("Context orchestrator shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error shutting down context orchestrator: {e}") 