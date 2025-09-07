"""
Agentic RAG系统
基于现有RAG系统升级，添加Agentic能力：反思、规划、迭代改进
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import json

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask
from layers.intelligent_context.rag_system import (
    RAGSystem, RetrievalStrategy, AugmentationMethod, GenerationMode,
    RetrievalResult, AugmentationResult, GenerationResult, RAGMetrics
)

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """查询复杂度级别"""
    SIMPLE = "simple"           # 简单查询（概念、定义）
    MODERATE = "moderate"       # 中等查询（方法、示例）
    COMPLEX = "complex"         # 复杂查询（分析、设计）
    MULTI_HOP = "multi_hop"     # 多跳推理查询
    CREATIVE = "creative"       # 创造性查询（生成、创新）


@dataclass
class ReflectionResult:
    """反思评估结果"""
    is_satisfactory: bool                           # 是否满足质量要求
    confidence: float                               # 总体置信度
    quality_dimensions: Dict[str, float]            # 各维度质量评分
    improvement_suggestions: List[str] = field(default_factory=list)  # 改进建议
    reflection_metadata: Dict[str, Any] = field(default_factory=dict) # 反思元数据


@dataclass
class RetrievalPlan:
    """检索执行计划"""
    max_iterations: int                             # 最大迭代次数
    strategies: List[RetrievalStrategy]             # 检索策略序列
    quality_threshold: float                        # 质量阈值
    plan_metadata: Dict[str, Any] = field(default_factory=dict)  # 计划元数据


@dataclass
class SimpleRetrievalPlan(RetrievalPlan):
    """简单检索计划"""
    def __init__(self):
        super().__init__(
            max_iterations=1,
            strategies=[RetrievalStrategy.SEMANTIC],
            quality_threshold=0.7,
            plan_metadata={'type': 'simple', 'description': '单次语义检索'}
        )


@dataclass
class MultiHopRetrievalPlan(RetrievalPlan):
    """多跳检索计划"""
    sub_queries: List[str] = field(default_factory=list)  # 子查询列表
    
    def __init__(self, sub_queries: List[str] = None):
        super().__init__(
            max_iterations=3,
            strategies=[RetrievalStrategy.SEMANTIC, RetrievalStrategy.GRAPH, RetrievalStrategy.CONTEXTUAL],
            quality_threshold=0.8,
            plan_metadata={'type': 'multi_hop', 'description': '多跳推理检索'}
        )
        self.sub_queries = sub_queries or []


@dataclass
class CreativeRetrievalPlan(RetrievalPlan):
    """创造性检索计划"""
    creative_requirements: Dict[str, Any] = field(default_factory=dict)  # 创造性需求
    
    def __init__(self, creative_requirements: Dict[str, Any] = None):
        super().__init__(
            max_iterations=5,
            strategies=[RetrievalStrategy.HYBRID, RetrievalStrategy.CONTEXTUAL],
            quality_threshold=0.85,
            plan_metadata={'type': 'creative', 'description': '创造性任务检索'}
        )
        self.creative_requirements = creative_requirements or {}


@dataclass
class RAGContext:
    """RAG处理上下文"""
    query: str                                      # 原始查询
    plan: RetrievalPlan                            # 执行计划
    iteration: int = 0                             # 当前迭代次数
    accumulated_knowledge: List[Dict] = field(default_factory=list)  # 累积知识
    context_metadata: Dict[str, Any] = field(default_factory=dict)   # 上下文元数据


@dataclass
class AgenticResponse:
    """Agentic RAG响应结果"""
    content: str                                    # 生成内容
    confidence: float                              # 置信度
    iterations_used: int                           # 使用的迭代次数
    quality_dimensions: Dict[str, float]           # 质量维度评分
    sources: List[Dict] = field(default_factory=list)  # 知识源
    metadata: Dict[str, Any] = field(default_factory=dict)  # 响应元数据


class ReflectionEngine:
    """
    反思评估引擎 - Agentic RAG的质量控制核心
    
    提供多维度的质量评估和改进建议
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'quality_threshold': 0.8,
            'relevance_weight': 0.3,
            'accuracy_weight': 0.25,
            'completeness_weight': 0.25,
            'clarity_weight': 0.2
        }
        
        # 反思历史记录
        self.reflection_history: List[ReflectionResult] = []
    
    async def reflect(self, context: RAGContext, result: GenerationResult) -> ReflectionResult:
        """
        对生成结果进行全面反思评估
        
        Args:
            context: RAG处理上下文
            result: 生成结果
            
        Returns:
            反思评估结果
        """
        try:
            logger.info(f"开始反思评估，查询: {context.query[:50]}...")
            
            # 多维度质量评估
            quality_dimensions = await self._evaluate_quality_dimensions(context, result)
            
            # 计算总体置信度
            overall_quality = self._calculate_overall_quality(quality_dimensions)
            
            # 判断是否满足质量要求
            is_satisfactory = overall_quality >= self.config['quality_threshold']
            
            # 生成改进建议（如果需要）
            improvement_suggestions = []
            if not is_satisfactory:
                improvement_suggestions = await self._generate_improvement_suggestions(
                    context, result, quality_dimensions
                )
            
            reflection_result = ReflectionResult(
                is_satisfactory=is_satisfactory,
                confidence=overall_quality,
                quality_dimensions=quality_dimensions,
                improvement_suggestions=improvement_suggestions,
                reflection_metadata={
                    'timestamp': datetime.now().isoformat(),
                    'iteration': context.iteration,
                    'query_length': len(context.query),
                    'response_length': len(result.generated_content),
                    'threshold_used': self.config['quality_threshold']
                }
            )
            
            # 记录反思历史
            self.reflection_history.append(reflection_result)
            
            logger.info(f"反思评估完成，总体质量: {overall_quality:.3f}, 满足要求: {is_satisfactory}")
            return reflection_result
            
        except Exception as e:
            logger.error(f"反思评估失败: {e}")
            # 返回默认的低质量评估
            return ReflectionResult(
                is_satisfactory=False,
                confidence=0.3,
                quality_dimensions={'error': 0.3},
                improvement_suggestions=['系统错误，需要重新处理'],
                reflection_metadata={'error': str(e)}
            )
    
    async def _evaluate_quality_dimensions(self, context: RAGContext, result: GenerationResult) -> Dict[str, float]:
        """评估各个质量维度"""
        dimensions = {}
        
        # 1. 相关性评估
        dimensions['relevance'] = await self._assess_relevance(context.query, result.generated_content)
        
        # 2. 准确性评估
        dimensions['accuracy'] = await self._verify_accuracy(result.generated_content, result.generation_metadata.get('sources', []))
        
        # 3. 完整性评估
        dimensions['completeness'] = await self._check_completeness(context.query, result.generated_content)
        
        # 4. 清晰度评估
        dimensions['clarity'] = await self._evaluate_clarity(result.generated_content)
        
        # 5. 一致性评估（与累积知识的一致性）
        if context.accumulated_knowledge:
            dimensions['consistency'] = await self._check_consistency(
                result.generated_content, context.accumulated_knowledge
            )
        
        return dimensions
    
    async def _assess_relevance(self, query: str, response: str) -> float:
        """评估响应与查询的相关性"""
        if not query or not response:
            return 0.0
        
        # 词汇重叠分析
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        if not query_words:
            return 0.5
        
        # 计算Jaccard相似度
        intersection = len(query_words.intersection(response_words))
        union = len(query_words.union(response_words))
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # 查询关键词覆盖率
        coverage = intersection / len(query_words)
        
        # 综合评分
        relevance_score = (jaccard_similarity * 0.4 + coverage * 0.6)
        
        # 添加语义相关性检查（简化版）
        semantic_boost = 0.0
        if any(word in response.lower() for word in query.lower().split() if len(word) > 3):
            semantic_boost = 0.1
        
        return min(relevance_score + semantic_boost, 1.0)
    
    async def _verify_accuracy(self, content: str, sources: List[Dict]) -> float:
        """验证内容准确性"""
        if not content:
            return 0.0
        
        # 基础准确性检查
        accuracy_score = 0.7  # 基础分数
        
        # 如果有源文档支持，提高准确性评分
        if sources:
            source_support = min(len(sources) / 3, 1.0)  # 最多3个源文档给满分
            accuracy_score += source_support * 0.2
        
        # 检查是否有明显的错误模式
        error_patterns = ['我不知道', '无法确定', '可能错误', '不确定']
        for pattern in error_patterns:
            if pattern in content:
                accuracy_score -= 0.1
        
        # 检查内容长度合理性
        if len(content) < 50:  # 内容过短可能不够准确
            accuracy_score -= 0.1
        elif len(content) > 2000:  # 内容过长可能包含无关信息
            accuracy_score -= 0.05
        
        return max(0.0, min(accuracy_score, 1.0))
    
    async def _check_completeness(self, query: str, response: str) -> float:
        """检查回答完整性"""
        if not query or not response:
            return 0.0
        
        # 基于查询复杂度评估完整性需求
        query_complexity = await self._estimate_query_complexity(query)
        
        # 响应长度与复杂度匹配度
        response_length = len(response)
        
        if query_complexity == QueryComplexity.SIMPLE:
            expected_length = 100  # 简单查询期望较短回答
            completeness = min(response_length / expected_length, 1.0)
        elif query_complexity == QueryComplexity.MODERATE:
            expected_length = 300
            completeness = min(response_length / expected_length, 1.0)
        elif query_complexity in [QueryComplexity.COMPLEX, QueryComplexity.MULTI_HOP]:
            expected_length = 500
            completeness = min(response_length / expected_length, 1.0)
        else:  # CREATIVE
            expected_length = 400
            completeness = min(response_length / expected_length, 1.0)
        
        # 结构化内容检查
        structure_bonus = 0.0
        if any(marker in response for marker in ['1.', '2.', '•', '-', '**']):
            structure_bonus = 0.1
        
        return min(completeness + structure_bonus, 1.0)
    
    async def _evaluate_clarity(self, content: str) -> float:
        """评估内容清晰度"""
        if not content:
            return 0.0
        
        clarity_score = 0.7  # 基础清晰度分数
        
        # 句子长度分析
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # 理想句子长度15-25词
            if 15 <= avg_sentence_length <= 25:
                clarity_score += 0.1
            elif avg_sentence_length > 35:  # 句子过长影响清晰度
                clarity_score -= 0.1
        
        # 段落结构检查
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            clarity_score += 0.1  # 有段落结构更清晰
        
        # 专业术语密度检查
        words = content.split()
        if words:
            # 简化的专业术语检测
            technical_terms = [w for w in words if len(w) > 8 and w.isupper()]
            term_density = len(technical_terms) / len(words)
            
            if term_density > 0.1:  # 专业术语过多可能影响清晰度
                clarity_score -= 0.05
        
        return max(0.0, min(clarity_score, 1.0))
    
    async def _check_consistency(self, content: str, accumulated_knowledge: List[Dict]) -> float:
        """检查与累积知识的一致性"""
        if not content or not accumulated_knowledge:
            return 0.8  # 默认一致性分数
        
        # 简化的一致性检查
        consistency_score = 0.8
        
        # 检查是否与之前的知识有明显冲突
        content_words = set(content.lower().split())
        
        for knowledge_item in accumulated_knowledge[-3:]:  # 只检查最近3个知识项
            if 'content' in knowledge_item:
                knowledge_words = set(knowledge_item['content'].lower().split())
                
                # 计算词汇重叠
                overlap = len(content_words.intersection(knowledge_words))
                if overlap > 0:
                    # 有重叠说明有一定相关性，提高一致性分数
                    consistency_score += 0.05
        
        return min(consistency_score, 1.0)
    
    def _calculate_overall_quality(self, quality_dimensions: Dict[str, float]) -> float:
        """计算总体质量分数"""
        if not quality_dimensions:
            return 0.0
        
        # 加权平均
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dimension, score in quality_dimensions.items():
            weight = self.config.get(f'{dimension}_weight', 0.2)  # 默认权重0.2
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _generate_improvement_suggestions(self, 
                                              context: RAGContext, 
                                              result: GenerationResult, 
                                              quality_dimensions: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于各维度分数生成具体建议
        for dimension, score in quality_dimensions.items():
            if score < 0.6:  # 低分维度需要改进
                if dimension == 'relevance':
                    suggestions.append("提高内容与查询的相关性，重新检索更相关的文档")
                elif dimension == 'accuracy':
                    suggestions.append("验证信息准确性，寻找更权威的信息源")
                elif dimension == 'completeness':
                    suggestions.append("补充更多详细信息，确保回答的完整性")
                elif dimension == 'clarity':
                    suggestions.append("改善表达清晰度，优化句子结构和段落组织")
                elif dimension == 'consistency':
                    suggestions.append("检查与先前信息的一致性，解决可能的冲突")
        
        # 基于迭代次数的建议
        if context.iteration >= 2:
            suggestions.append("尝试不同的检索策略或调整查询方式")
        
        # 基于查询复杂度的建议
        query_complexity = await self._estimate_query_complexity(context.query)
        if query_complexity in [QueryComplexity.MULTI_HOP, QueryComplexity.CREATIVE]:
            suggestions.append("对于复杂查询，考虑分解为多个子问题逐步处理")
        
        return suggestions[:3]  # 最多返回3个建议
    
    async def _estimate_query_complexity(self, query: str) -> QueryComplexity:
        """估算查询复杂度"""
        if not query:
            return QueryComplexity.SIMPLE
        
        query_lower = query.lower()
        
        # 创造性查询关键词
        creative_keywords = ['设计', '创建', '生成', '开发', '构建', '实现', '创新']
        if any(keyword in query_lower for keyword in creative_keywords):
            return QueryComplexity.CREATIVE
        
        # 多跳推理查询关键词
        multi_hop_keywords = ['比较', '分析', '关系', '影响', '为什么', '如何实现']
        if any(keyword in query_lower for keyword in multi_hop_keywords):
            return QueryComplexity.MULTI_HOP
        
        # 复杂查询关键词
        complex_keywords = ['优化', '解决', '调试', '故障', '性能', '算法']
        if any(keyword in query_lower for keyword in complex_keywords):
            return QueryComplexity.COMPLEX
        
        # 中等复杂度查询关键词
        moderate_keywords = ['方法', '步骤', '流程', '过程', '示例', '案例']
        if any(keyword in query_lower for keyword in moderate_keywords):
            return QueryComplexity.MODERATE
        
        # 简单查询（定义、概念等）
        simple_keywords = ['什么是', '定义', '含义', '概念', '是什么']
        if any(keyword in query_lower for keyword in simple_keywords):
            return QueryComplexity.SIMPLE
        
        # 基于查询长度判断
        word_count = len(query.split())
        if word_count <= 3:
            return QueryComplexity.SIMPLE
        elif word_count <= 8:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX
    
    def get_reflection_statistics(self) -> Dict[str, Any]:
        """获取反思统计信息"""
        if not self.reflection_history:
            return {'total_reflections': 0}
        
        recent_reflections = self.reflection_history[-10:]  # 最近10次反思
        
        avg_confidence = sum(r.confidence for r in recent_reflections) / len(recent_reflections)
        satisfaction_rate = sum(1 for r in recent_reflections if r.is_satisfactory) / len(recent_reflections)
        
        # 各维度平均分数
        dimension_averages = {}
        for reflection in recent_reflections:
            for dimension, score in reflection.quality_dimensions.items():
                if dimension not in dimension_averages:
                    dimension_averages[dimension] = []
                dimension_averages[dimension].append(score)
        
        for dimension in dimension_averages:
            dimension_averages[dimension] = sum(dimension_averages[dimension]) / len(dimension_averages[dimension])
        
        return {
            'total_reflections': len(self.reflection_history),
            'recent_avg_confidence': avg_confidence,
            'satisfaction_rate': satisfaction_rate,
            'dimension_averages': dimension_averages,
            'config': self.config
        }


class RAGPlanningEngine:
    """
    RAG任务规划引擎
    
    基于查询复杂度和上下文创建最优的检索执行计划
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'max_iterations': 5,
            'default_quality_threshold': 0.8,
            'enable_adaptive_planning': True
        }
        
        # 规划历史记录
        self.planning_history: List[Dict[str, Any]] = []
    
    async def create_retrieval_plan(self, query: str, context: UniversalContext = None) -> RetrievalPlan:
        """
        基于查询创建检索计划
        
        Args:
            query: 用户查询
            context: 上下文信息
            
        Returns:
            检索执行计划
        """
        try:
            logger.info(f"开始创建检索计划，查询: {query[:50]}...")
            
            # 分析查询复杂度
            complexity = await self._analyze_query_complexity(query)
            
            # 基于复杂度创建计划
            if complexity == QueryComplexity.SIMPLE:
                plan = SimpleRetrievalPlan()
            elif complexity == QueryComplexity.MULTI_HOP:
                sub_queries = await self._decompose_query(query)
                plan = MultiHopRetrievalPlan(sub_queries)
            elif complexity == QueryComplexity.CREATIVE:
                creative_requirements = await self._extract_creative_requirements(query)
                plan = CreativeRetrievalPlan(creative_requirements)
            else:  # MODERATE, COMPLEX
                plan = RetrievalPlan(
                    max_iterations=3,
                    strategies=[RetrievalStrategy.HYBRID, RetrievalStrategy.CONTEXTUAL],
                    quality_threshold=0.75,
                    plan_metadata={'type': complexity.value, 'description': f'{complexity.value}查询计划'}
                )
            
            # 记录规划历史
            self.planning_history.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'complexity': complexity.value,
                'plan_type': plan.plan_metadata.get('type', 'unknown'),
                'max_iterations': plan.max_iterations,
                'strategies': [s.value for s in plan.strategies]
            })
            
            logger.info(f"检索计划创建完成，类型: {plan.plan_metadata.get('type')}, 最大迭代: {plan.max_iterations}")
            return plan
            
        except Exception as e:
            logger.error(f"创建检索计划失败: {e}")
            # 返回默认的简单计划
            return SimpleRetrievalPlan()
    
    async def _analyze_query_complexity(self, query: str) -> QueryComplexity:
        """分析查询复杂度"""
        if not query:
            return QueryComplexity.SIMPLE
        
        query_lower = query.lower()
        
        # 创造性查询检测
        creative_patterns = [
            '设计', '创建', '生成', '开发', '构建', '实现', '创新', 
            '写一个', '帮我做', '制作', '建立'
        ]
        if any(pattern in query_lower for pattern in creative_patterns):
            return QueryComplexity.CREATIVE
        
        # 多跳推理查询检测
        multi_hop_patterns = [
            '比较', '分析', '关系', '影响', '为什么', '如何实现',
            '区别', '联系', '原理', '机制', '过程'
        ]
        if any(pattern in query_lower for pattern in multi_hop_patterns):
            return QueryComplexity.MULTI_HOP
        
        # 复杂查询检测
        complex_patterns = [
            '优化', '解决', '调试', '故障', '性能', '算法',
            '问题', '错误', '改进', '提升'
        ]
        if any(pattern in query_lower for pattern in complex_patterns):
            return QueryComplexity.COMPLEX
        
        # 中等复杂度检测
        moderate_patterns = [
            '方法', '步骤', '流程', '过程', '示例', '案例',
            '如何', '怎样', '方式', '途径'
        ]
        if any(pattern in query_lower for pattern in moderate_patterns):
            return QueryComplexity.MODERATE
        
        # 简单查询检测
        simple_patterns = [
            '什么是', '定义', '含义', '概念', '是什么', '介绍'
        ]
        if any(pattern in query_lower for pattern in simple_patterns):
            return QueryComplexity.SIMPLE
        
        # 基于查询长度和结构判断
        word_count = len(query.split())
        question_marks = query.count('?')
        
        if word_count <= 3 and question_marks <= 1:
            return QueryComplexity.SIMPLE
        elif word_count <= 8:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX
    
    async def _decompose_query(self, query: str) -> List[str]:
        """分解复杂查询为子查询"""
        # 简化的查询分解逻辑
        sub_queries = []
        
        # 检测连接词并分解
        connectors = ['和', '以及', '还有', '另外', '同时', '并且']
        
        current_query = query
        for connector in connectors:
            if connector in current_query:
                parts = current_query.split(connector)
                sub_queries.extend([part.strip() for part in parts if part.strip()])
                break
        
        # 如果没有找到连接词，尝试基于标点符号分解
        if not sub_queries:
            if '，' in query:
                parts = query.split('，')
                sub_queries.extend([part.strip() for part in parts if part.strip()])
            elif '；' in query:
                parts = query.split('；')
                sub_queries.extend([part.strip() for part in parts if part.strip()])
        
        # 如果仍然没有分解出子查询，创建相关的子查询
        if not sub_queries:
            # 基于查询内容生成相关子查询
            if '设计' in query:
                sub_queries = [
                    query.replace('设计', '原理'),
                    query.replace('设计', '方法'),
                    query  # 原查询
                ]
            elif '实现' in query:
                sub_queries = [
                    query.replace('实现', '理论'),
                    query.replace('实现', '步骤'),
                    query  # 原查询
                ]
            else:
                sub_queries = [query]  # 无法分解时返回原查询
        
        return sub_queries[:3]  # 最多返回3个子查询
    
    async def _extract_creative_requirements(self, query: str) -> Dict[str, Any]:
        """提取创造性任务的需求"""
        requirements = {
            'creativity_level': 'medium',
            'output_format': 'text',
            'domain_specific': False,
            'examples_needed': True
        }
        
        query_lower = query.lower()
        
        # 判断创造性级别
        if any(word in query_lower for word in ['创新', '独特', '新颖', '原创']):
            requirements['creativity_level'] = 'high'
        elif any(word in query_lower for word in ['简单', '基础', '基本']):
            requirements['creativity_level'] = 'low'
        
        # 判断输出格式
        if any(word in query_lower for word in ['代码', '程序', '脚本']):
            requirements['output_format'] = 'code'
        elif any(word in query_lower for word in ['图表', '图形', '可视化']):
            requirements['output_format'] = 'visual'
        elif any(word in query_lower for word in ['列表', '清单']):
            requirements['output_format'] = 'list'
        
        # 判断是否需要领域特定知识
        domain_keywords = ['fpga', 'verilog', '硬件', '电路', '芯片', '时序']
        if any(keyword in query_lower for keyword in domain_keywords):
            requirements['domain_specific'] = True
            requirements['domain'] = 'fpga'
        
        return requirements
    
    def get_planning_statistics(self) -> Dict[str, Any]:
        """获取规划统计信息"""
        if not self.planning_history:
            return {'total_plans': 0}
        
        recent_plans = self.planning_history[-10:]
        
        # 复杂度分布
        complexity_distribution = {}
        for plan in recent_plans:
            complexity = plan['complexity']
            complexity_distribution[complexity] = complexity_distribution.get(complexity, 0) + 1
        
        # 平均迭代次数
        avg_iterations = sum(plan['max_iterations'] for plan in recent_plans) / len(recent_plans)
        
        # 最常用的策略
        strategy_usage = {}
        for plan in recent_plans:
            for strategy in plan['strategies']:
                strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
        
        return {
            'total_plans': len(self.planning_history),
            'complexity_distribution': complexity_distribution,
            'avg_max_iterations': avg_iterations,
            'strategy_usage': strategy_usage,
            'config': self.config
        }


class AgenticRAGProcessor:
    """
    Agentic RAG处理器 - 核心处理引擎
    
    基于现有RAG系统升级，添加反思、规划、迭代改进等Agentic能力
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # 基础RAG系统（复用现有实现）
        self.base_rag_system = RAGSystem()
        
        # Agentic核心组件
        self.reflection_engine = ReflectionEngine(config.get('reflection', {}) if config else {})
        self.planning_engine = RAGPlanningEngine(config.get('planning', {}) if config else {})
        
        # 配置参数
        default_config = {
            'max_iterations': 5,
            'quality_threshold': 0.8,
            'enable_reflection': True,
            'enable_planning': True,
            'enable_learning': True
        }
        if config:
            default_config.update(config)
        self.config = default_config
        
        # 处理历史记录
        self.processing_history: List[Dict[str, Any]] = []
        
        logger.info("AgenticRAGProcessor初始化完成")
    
    async def process(self, query: str, context: UniversalContext = None) -> AgenticResponse:
        """
        Agentic RAG主处理流程
        
        Args:
            query: 用户查询
            context: 上下文信息
            
        Returns:
            Agentic响应结果
        """
        try:
            start_time = datetime.now()
            logger.info(f"开始Agentic RAG处理，查询: {query[:50]}...")
            
            # 1. 创建检索计划
            plan = await self.planning_engine.create_retrieval_plan(query, context)
            
            # 2. 初始化RAG上下文
            rag_context = RAGContext(
                query=query,
                plan=plan,
                iteration=0,
                accumulated_knowledge=[],
                context_metadata={
                    'start_time': start_time.isoformat(),
                    'original_context': context.data if context else {}
                }
            )
            
            # 3. 迭代执行循环
            final_result = await self._iterative_processing_loop(rag_context, context)
            
            # 4. 记录处理历史
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.processing_history.append({
                'timestamp': end_time.isoformat(),
                'query': query,
                'iterations_used': final_result.iterations_used,
                'final_confidence': final_result.confidence,
                'processing_time': processing_time,
                'plan_type': plan.plan_metadata.get('type', 'unknown'),
                'success': final_result.confidence >= self.config['quality_threshold']
            })
            
            logger.info(f"Agentic RAG处理完成，迭代次数: {final_result.iterations_used}, "
                       f"置信度: {final_result.confidence:.3f}, 耗时: {processing_time:.3f}s")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Agentic RAG处理失败: {e}")
            # 返回默认响应
            return AgenticResponse(
                content=f"处理过程中发生错误: {str(e)}",
                confidence=0.3,
                iterations_used=0,
                quality_dimensions={'error': 0.3},
                sources=[],
                metadata={'error': str(e), 'timestamp': datetime.now().isoformat()}
            )
    
    async def _iterative_processing_loop(self, rag_context: RAGContext, original_context: UniversalContext) -> AgenticResponse:
        """迭代处理循环 - Agentic RAG的核心"""
        
        best_result = None
        best_confidence = 0.0
        
        for iteration in range(rag_context.plan.max_iterations):
            rag_context.iteration = iteration
            logger.info(f"开始第 {iteration + 1} 次迭代")
            
            try:
                # 执行单次RAG处理
                step_result = await self._execute_single_rag_step(rag_context, original_context)
                
                # 反思评估
                if self.config['enable_reflection']:
                    reflection = await self.reflection_engine.reflect(rag_context, step_result)
                    
                    # 更新累积知识
                    rag_context.accumulated_knowledge.append({
                        'iteration': iteration,
                        'content': step_result.generated_content,
                        'confidence': step_result.confidence_score,
                        'reflection': reflection.quality_dimensions,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # 记录最佳结果
                    if reflection.confidence > best_confidence:
                        best_confidence = reflection.confidence
                        best_result = AgenticResponse(
                            content=step_result.generated_content,
                            confidence=reflection.confidence,
                            iterations_used=iteration + 1,
                            quality_dimensions=reflection.quality_dimensions,
                            sources=step_result.generation_metadata.get('sources', []),
                            metadata={
                                'final_iteration': iteration + 1,
                                'reflection_metadata': reflection.reflection_metadata,
                                'improvement_suggestions': reflection.improvement_suggestions,
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                    
                    # 如果质量满足要求，提前结束
                    if reflection.is_satisfactory:
                        logger.info(f"质量满足要求，在第 {iteration + 1} 次迭代后结束")
                        return best_result
                    
                    # 基于反思调整上下文
                    rag_context = await self._adjust_context_based_on_reflection(
                        rag_context, step_result, reflection
                    )
                
                else:
                    # 不启用反思时的简单处理
                    return AgenticResponse(
                        content=step_result.generated_content,
                        confidence=step_result.confidence_score,
                        iterations_used=iteration + 1,
                        quality_dimensions={'basic': step_result.confidence_score},
                        sources=step_result.generation_metadata.get('sources', []),
                        metadata={'timestamp': datetime.now().isoformat()}
                    )
                
            except Exception as e:
                logger.error(f"第 {iteration + 1} 次迭代失败: {e}")
                # 继续下一次迭代
                continue
        
        # 达到最大迭代次数，返回最佳结果
        if best_result:
            best_result.metadata['warning'] = 'max_iterations_reached'
            best_result.metadata['max_iterations'] = rag_context.plan.max_iterations
            logger.info(f"达到最大迭代次数 {rag_context.plan.max_iterations}，返回最佳结果")
            return best_result
        else:
            # 没有任何成功的结果
            logger.warning("所有迭代都失败，返回默认结果")
            return AgenticResponse(
                content="抱歉，无法生成满意的回答，请尝试重新表述您的问题。",
                confidence=0.3,
                iterations_used=rag_context.plan.max_iterations,
                quality_dimensions={'failure': 0.3},
                sources=[],
                metadata={
                    'error': 'all_iterations_failed',
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _execute_single_rag_step(self, rag_context: RAGContext, original_context: UniversalContext) -> GenerationResult:
        """执行单次RAG处理步骤"""
        
        # 选择当前迭代的检索策略
        strategy_index = rag_context.iteration % len(rag_context.plan.strategies)
        current_strategy = rag_context.plan.strategies[strategy_index]
        
        logger.info(f"使用检索策略: {current_strategy.value}")
        
        # 根据计划类型调整查询
        current_query = await self._adapt_query_for_iteration(rag_context)
        
        # 创建任务对象（适配现有RAG系统接口）
        task = UniversalTask(content=current_query, task_type="agentic_rag_query")
        
        # 使用基础RAG系统进行处理
        enhanced_context = await self.base_rag_system.enhance_with_rag(
            context=original_context or UniversalContext(),
            task=task,
            retrieval_strategy=current_strategy
        )
        
        # 提取RAG处理结果
        rag_content = enhanced_context.get('rag_enhanced_content', '')
        rag_metadata = enhanced_context.get('rag_metadata', {})
        
        # 构建生成结果
        generation_result = GenerationResult(
            generated_content=rag_content,
            confidence_score=rag_metadata.get('quality_score', 0.7),
            generation_metadata={
                'sources': rag_metadata.get('retrieval_scores', []),
                'strategy_used': current_strategy.value,
                'processing_info': rag_metadata.get('rag_processing_info', {}),
                'iteration': rag_context.iteration
            },
            mode_used=GenerationMode.GUIDED
        )
        
        return generation_result
    
    async def _adapt_query_for_iteration(self, rag_context: RAGContext) -> str:
        """根据迭代情况调整查询"""
        base_query = rag_context.query
        
        # 对于多跳查询，使用子查询
        if isinstance(rag_context.plan, MultiHopRetrievalPlan) and rag_context.plan.sub_queries:
            sub_query_index = rag_context.iteration % len(rag_context.plan.sub_queries)
            adapted_query = rag_context.plan.sub_queries[sub_query_index]
            logger.info(f"使用子查询 {sub_query_index + 1}: {adapted_query}")
            return adapted_query
        
        # 基于迭代次数调整查询
        if rag_context.iteration > 0:
            # 从累积知识中提取关键词来改进查询
            if rag_context.accumulated_knowledge:
                last_knowledge = rag_context.accumulated_knowledge[-1]
                last_content = last_knowledge.get('content', '')
                
                # 简单的关键词提取和查询增强
                if len(last_content) > 50:
                    # 如果上次结果较长，尝试更具体的查询
                    adapted_query = f"{base_query} 详细解释"
                else:
                    # 如果上次结果较短，尝试更广泛的查询
                    adapted_query = f"{base_query} 完整信息"
                
                logger.info(f"调整查询: {adapted_query}")
                return adapted_query
        
        return base_query
    
    async def _adjust_context_based_on_reflection(self, 
                                                 rag_context: RAGContext, 
                                                 step_result: GenerationResult, 
                                                 reflection: ReflectionResult) -> RAGContext:
        """基于反思结果调整上下文"""
        
        # 更新上下文元数据
        rag_context.context_metadata.update({
            f'iteration_{rag_context.iteration}_reflection': {
                'confidence': reflection.confidence,
                'satisfactory': reflection.is_satisfactory,
                'suggestions': reflection.improvement_suggestions
            }
        })
        
        # 基于改进建议调整策略
        if reflection.improvement_suggestions:
            for suggestion in reflection.improvement_suggestions:
                if "检索策略" in suggestion or "重新检索" in suggestion:
                    # 调整检索策略顺序
                    current_strategies = rag_context.plan.strategies.copy()
                    if len(current_strategies) > 1:
                        # 将当前策略移到末尾，尝试其他策略
                        current_strategy = current_strategies[rag_context.iteration % len(current_strategies)]
                        current_strategies.remove(current_strategy)
                        current_strategies.append(current_strategy)
                        rag_context.plan.strategies = current_strategies
                
                elif "分解" in suggestion or "子问题" in suggestion:
                    # 如果建议分解查询，但当前不是多跳计划，转换为多跳计划
                    if not isinstance(rag_context.plan, MultiHopRetrievalPlan):
                        sub_queries = await self.planning_engine._decompose_query(rag_context.query)
                        rag_context.plan = MultiHopRetrievalPlan(sub_queries)
        
        return rag_context
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        if not self.processing_history:
            return {'total_processed': 0}
        
        recent_processing = self.processing_history[-20:]  # 最近20次处理
        
        # 计算统计指标
        avg_iterations = sum(p['iterations_used'] for p in recent_processing) / len(recent_processing)
        avg_confidence = sum(p['final_confidence'] for p in recent_processing) / len(recent_processing)
        avg_processing_time = sum(p['processing_time'] for p in recent_processing) / len(recent_processing)
        success_rate = sum(1 for p in recent_processing if p['success']) / len(recent_processing)
        
        # 计划类型分布
        plan_type_distribution = {}
        for processing in recent_processing:
            plan_type = processing['plan_type']
            plan_type_distribution[plan_type] = plan_type_distribution.get(plan_type, 0) + 1
        
        return {
            'total_processed': len(self.processing_history),
            'avg_iterations': avg_iterations,
            'avg_confidence': avg_confidence,
            'avg_processing_time': avg_processing_time,
            'success_rate': success_rate,
            'plan_type_distribution': plan_type_distribution,
            'reflection_stats': self.reflection_engine.get_reflection_statistics(),
            'planning_stats': self.planning_engine.get_planning_statistics(),
            'config': self.config
        } 