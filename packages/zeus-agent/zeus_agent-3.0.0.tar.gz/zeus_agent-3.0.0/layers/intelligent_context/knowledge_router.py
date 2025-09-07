"""
知识路由决策系统
智能决定何时使用知识库 vs AI训练知识 vs 网络搜索

决策策略：
1. 领域专业性评估
2. 知识新鲜度要求
3. 置信度阈值
4. 查询复杂度分析
5. 成本效益考虑
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re

logger = logging.getLogger(__name__)


class KnowledgeSourceType(Enum):
    """知识源类型"""
    LOCAL_KNOWLEDGE_BASE = "local_kb"      # 本地知识库
    AI_TRAINING_DATA = "ai_training"       # AI训练数据
    WEB_SEARCH = "web_search"              # 网络搜索
    HYBRID = "hybrid"                      # 混合模式


class QueryComplexity(Enum):
    """查询复杂度"""
    SIMPLE = "simple"          # 简单查询（概念、定义）
    MODERATE = "moderate"      # 中等查询（方法、示例）
    COMPLEX = "complex"        # 复杂查询（分析、设计）
    CREATIVE = "creative"      # 创造性查询（生成、创新）


class QueryDomain(Enum):
    """查询领域"""
    FPGA_SPECIFIC = "fpga_specific"        # FPGA专业知识
    GENERAL_TECH = "general_tech"          # 通用技术知识
    CURRENT_EVENTS = "current_events"      # 时事动态
    CREATIVE_TASK = "creative_task"        # 创造性任务


@dataclass
class QueryAnalysis:
    """查询分析结果"""
    query: str
    complexity: QueryComplexity
    domain: QueryDomain
    keywords: List[str]
    requires_latest_info: bool = False
    requires_creativity: bool = False
    requires_precision: bool = True
    confidence: float = 1.0


@dataclass
class KnowledgeSourceDecision:
    """知识源决策结果"""
    primary_source: KnowledgeSourceType
    secondary_sources: List[KnowledgeSourceType] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 1.0
    estimated_cost: float = 0.0
    expected_latency: float = 0.0


@dataclass
class KnowledgeSourceCapability:
    """知识源能力描述"""
    source_type: KnowledgeSourceType
    strengths: List[str]
    weaknesses: List[str]
    cost_per_query: float  # 相对成本
    avg_latency: float     # 平均延迟（秒）
    coverage_domains: List[QueryDomain]
    freshness_score: float  # 知识新鲜度 0-1


class KnowledgeRouter:
    """
    知识路由决策系统
    
    核心功能：
    - 查询意图分析
    - 知识源能力评估
    - 智能路由决策
    - 成本效益优化
    - 多源融合策略
    """
    
    def __init__(self):
        """初始化知识路由器"""
        
        # 定义各知识源的能力特征
        self.source_capabilities = {
            KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE: KnowledgeSourceCapability(
                source_type=KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE,
                strengths=[
                    "FPGA专业知识深度",
                    "响应速度快",
                    "成本低",
                    "离线可用",
                    "知识质量可控"
                ],
                weaknesses=[
                    "知识覆盖面有限",
                    "更新频率低",
                    "缺乏最新信息",
                    "创造性有限"
                ],
                cost_per_query=0.1,
                avg_latency=0.2,
                coverage_domains=[QueryDomain.FPGA_SPECIFIC],
                freshness_score=0.6
            ),
            
            KnowledgeSourceType.AI_TRAINING_DATA: KnowledgeSourceCapability(
                source_type=KnowledgeSourceType.AI_TRAINING_DATA,
                strengths=[
                    "知识覆盖面广",
                    "推理能力强",
                    "创造性好",
                    "语言理解佳",
                    "可生成新内容"
                ],
                weaknesses=[
                    "知识截止时间限制",
                    "可能不够精确",
                    "成本较高",
                    "响应时间较长"
                ],
                cost_per_query=1.0,
                avg_latency=2.0,
                coverage_domains=[QueryDomain.FPGA_SPECIFIC, QueryDomain.GENERAL_TECH, QueryDomain.CREATIVE_TASK],
                freshness_score=0.4
            ),
            
            KnowledgeSourceType.WEB_SEARCH: KnowledgeSourceCapability(
                source_type=KnowledgeSourceType.WEB_SEARCH,
                strengths=[
                    "信息最新",
                    "覆盖面最广",
                    "实时更新",
                    "多样化来源"
                ],
                weaknesses=[
                    "质量参差不齐",
                    "需要筛选",
                    "延迟较高",
                    "需要网络连接"
                ],
                cost_per_query=0.5,
                avg_latency=3.0,
                coverage_domains=[QueryDomain.CURRENT_EVENTS, QueryDomain.GENERAL_TECH],
                freshness_score=1.0
            )
        }
        
        # 查询模式定义
        self.query_patterns = {
            # FPGA专业模式
            'fpga_specific': [
                r'verilog|systemverilog|vhdl',
                r'fpga|xilinx|altera|intel',
                r'vivado|quartus|modelsim',
                r'synthesis|simulation|timing',
                r'state\s+machine|pipeline|fifo',
                r'clock|reset|constraint'
            ],
            
            # 需要最新信息的模式
            'latest_info': [
                r'最新|latest|new|recent',
                r'2024|2025|今年|this\s+year',
                r'更新|update|upgrade',
                r'发布|release|announcement'
            ],
            
            # 创造性任务模式
            'creative': [
                r'设计|design|create|generate',
                r'帮我写|help.*write|write.*for',
                r'如何实现|how.*implement',
                r'优化|optimize|improve'
            ],
            
            # 精确性要求模式
            'precision': [
                r'具体|specific|exact',
                r'参数|parameter|specification',
                r'标准|standard|protocol',
                r'规范|specification|requirement'
            ]
        }
        
        logger.info("🧭 知识路由器初始化完成")
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> KnowledgeSourceDecision:
        """路由查询到最适合的知识源"""
        
        logger.info(f"🧭 路由查询: {query[:100]}...")
        
        # 1. 分析查询
        analysis = await self._analyze_query(query, context or {})
        
        # 2. 评估知识源适用性
        source_scores = await self._evaluate_sources(analysis)
        
        # 3. 做出决策
        decision = await self._make_decision(analysis, source_scores)
        
        logger.info(f"📍 路由决策: {decision.primary_source.value} (置信度: {decision.confidence:.2f})")
        logger.debug(f"   推理: {decision.reasoning}")
        
        return decision
    
    async def _analyze_query(self, query: str, context: Dict[str, Any]) -> QueryAnalysis:
        """分析查询特征"""
        
        query_lower = query.lower()
        
        # 分析复杂度
        complexity = self._analyze_complexity(query)
        
        # 分析领域
        domain = self._analyze_domain(query)
        
        # 提取关键词
        keywords = self._extract_keywords(query)
        
        # 分析特殊需求
        requires_latest_info = self._requires_latest_info(query)
        requires_creativity = self._requires_creativity(query)
        requires_precision = self._requires_precision(query)
        
        analysis = QueryAnalysis(
            query=query,
            complexity=complexity,
            domain=domain,
            keywords=keywords,
            requires_latest_info=requires_latest_info,
            requires_creativity=requires_creativity,
            requires_precision=requires_precision
        )
        
        logger.debug(f"📊 查询分析: 复杂度={complexity.value}, 领域={domain.value}")
        return analysis
    
    def _analyze_complexity(self, query: str) -> QueryComplexity:
        """分析查询复杂度"""
        query_lower = query.lower()
        
        # 创造性指标
        creative_indicators = ['设计', '生成', '创建', 'design', 'generate', 'create', '帮我写']
        if any(indicator in query_lower for indicator in creative_indicators):
            return QueryComplexity.CREATIVE
        
        # 复杂查询指标
        complex_indicators = ['分析', '比较', '优化', 'analyze', 'compare', 'optimize', '如何实现']
        if any(indicator in query_lower for indicator in complex_indicators):
            return QueryComplexity.COMPLEX
        
        # 中等复杂度指标
        moderate_indicators = ['示例', '方法', 'example', 'method', 'how', '怎么']
        if any(indicator in query_lower for indicator in moderate_indicators):
            return QueryComplexity.MODERATE
        
        # 简单查询（定义、概念等）
        return QueryComplexity.SIMPLE
    
    def _analyze_domain(self, query: str) -> QueryDomain:
        """分析查询领域"""
        query_lower = query.lower()
        
        # FPGA专业领域
        fpga_keywords = [
            'verilog', 'systemverilog', 'vhdl', 'fpga', 'xilinx', 'altera',
            'vivado', 'quartus', 'synthesis', 'timing', 'constraint',
            'state machine', 'pipeline', 'fifo', 'clock', 'reset'
        ]
        
        if any(keyword in query_lower for keyword in fpga_keywords):
            return QueryDomain.FPGA_SPECIFIC
        
        # 时事动态
        current_keywords = ['最新', '2024', '2025', 'latest', 'recent', 'new']
        if any(keyword in query_lower for keyword in current_keywords):
            return QueryDomain.CURRENT_EVENTS
        
        # 创造性任务
        creative_keywords = ['设计', '生成', '创建', 'design', 'generate', 'create']
        if any(keyword in query_lower for keyword in creative_keywords):
            return QueryDomain.CREATIVE_TASK
        
        return QueryDomain.GENERAL_TECH
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应该使用更复杂的NLP方法）
        words = re.findall(r'\b\w+\b', query.lower())
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', 'the', 'is', 'in', 'and', 'or', 'a', 'an'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # 限制数量
    
    def _requires_latest_info(self, query: str) -> bool:
        """判断是否需要最新信息"""
        latest_patterns = self.query_patterns['latest_info']
        return any(re.search(pattern, query, re.IGNORECASE) for pattern in latest_patterns)
    
    def _requires_creativity(self, query: str) -> bool:
        """判断是否需要创造性"""
        creative_patterns = self.query_patterns['creative']
        return any(re.search(pattern, query, re.IGNORECASE) for pattern in creative_patterns)
    
    def _requires_precision(self, query: str) -> bool:
        """判断是否需要高精确性"""
        precision_patterns = self.query_patterns['precision']
        return any(re.search(pattern, query, re.IGNORECASE) for pattern in precision_patterns)
    
    async def _evaluate_sources(self, analysis: QueryAnalysis) -> Dict[KnowledgeSourceType, float]:
        """评估各知识源的适用性得分"""
        
        scores = {}
        
        for source_type, capability in self.source_capabilities.items():
            score = 0.0
            
            # 1. 领域匹配度 (40%)
            domain_match = 0.0
            if analysis.domain in capability.coverage_domains:
                domain_match = 1.0
            elif analysis.domain == QueryDomain.GENERAL_TECH:
                domain_match = 0.7  # 通用技术知识大部分源都能处理
            
            score += domain_match * 0.4
            
            # 2. 复杂度适应性 (25%)
            complexity_match = self._evaluate_complexity_match(analysis.complexity, capability)
            score += complexity_match * 0.25
            
            # 3. 特殊需求匹配 (20%)
            special_match = self._evaluate_special_requirements(analysis, capability)
            score += special_match * 0.2
            
            # 4. 成本效益 (10%)
            cost_efficiency = max(0, 1.0 - capability.cost_per_query / 2.0)
            score += cost_efficiency * 0.1
            
            # 5. 响应速度 (5%)
            speed_score = max(0, 1.0 - capability.avg_latency / 5.0)
            score += speed_score * 0.05
            
            scores[source_type] = score
        
        return scores
    
    def _evaluate_complexity_match(self, complexity: QueryComplexity, capability: KnowledgeSourceCapability) -> float:
        """评估复杂度匹配度"""
        
        if capability.source_type == KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE:
            # 知识库适合简单到中等复杂度的查询
            if complexity in [QueryComplexity.SIMPLE, QueryComplexity.MODERATE]:
                return 1.0
            elif complexity == QueryComplexity.COMPLEX:
                return 0.6
            else:  # CREATIVE
                return 0.3
        
        elif capability.source_type == KnowledgeSourceType.AI_TRAINING_DATA:
            # AI训练数据适合所有复杂度，特别是创造性任务
            if complexity == QueryComplexity.CREATIVE:
                return 1.0
            elif complexity == QueryComplexity.COMPLEX:
                return 0.9
            else:
                return 0.8
        
        elif capability.source_type == KnowledgeSourceType.WEB_SEARCH:
            # 网络搜索适合中等到复杂的查询
            if complexity in [QueryComplexity.MODERATE, QueryComplexity.COMPLEX]:
                return 0.8
            elif complexity == QueryComplexity.SIMPLE:
                return 0.6
            else:  # CREATIVE
                return 0.4
        
        return 0.5
    
    def _evaluate_special_requirements(self, analysis: QueryAnalysis, capability: KnowledgeSourceCapability) -> float:
        """评估特殊需求匹配度"""
        score = 0.0
        requirements_count = 0
        
        # 最新信息需求
        if analysis.requires_latest_info:
            requirements_count += 1
            score += capability.freshness_score
        
        # 创造性需求
        if analysis.requires_creativity:
            requirements_count += 1
            if capability.source_type == KnowledgeSourceType.AI_TRAINING_DATA:
                score += 1.0
            elif capability.source_type == KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE:
                score += 0.3
            else:
                score += 0.5
        
        # 精确性需求
        if analysis.requires_precision:
            requirements_count += 1
            if capability.source_type == KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE:
                score += 1.0
            elif capability.source_type == KnowledgeSourceType.AI_TRAINING_DATA:
                score += 0.7
            else:
                score += 0.5
        
        return score / max(1, requirements_count)
    
    async def _make_decision(self, analysis: QueryAnalysis, scores: Dict[KnowledgeSourceType, float]) -> KnowledgeSourceDecision:
        """做出最终决策"""
        
        # 排序得分
        sorted_sources = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_source = sorted_sources[0][0]
        primary_score = sorted_sources[0][1]
        
        # 选择辅助源
        secondary_sources = []
        for source, score in sorted_sources[1:]:
            if score > 0.6:  # 阈值
                secondary_sources.append(source)
        
        # 生成推理说明
        reasoning = self._generate_reasoning(analysis, primary_source, primary_score)
        
        # 估算成本和延迟
        capability = self.source_capabilities[primary_source]
        estimated_cost = capability.cost_per_query
        expected_latency = capability.avg_latency
        
        return KnowledgeSourceDecision(
            primary_source=primary_source,
            secondary_sources=secondary_sources,
            reasoning=reasoning,
            confidence=primary_score,
            estimated_cost=estimated_cost,
            expected_latency=expected_latency
        )
    
    def _generate_reasoning(self, analysis: QueryAnalysis, source: KnowledgeSourceType, score: float) -> str:
        """生成决策推理"""
        
        capability = self.source_capabilities[source]
        
        reasons = []
        
        # 领域匹配
        if analysis.domain in capability.coverage_domains:
            reasons.append(f"领域匹配度高({analysis.domain.value})")
        
        # 特殊需求
        if analysis.requires_latest_info and capability.freshness_score > 0.8:
            reasons.append("满足最新信息需求")
        
        if analysis.requires_creativity and source == KnowledgeSourceType.AI_TRAINING_DATA:
            reasons.append("适合创造性任务")
        
        if analysis.requires_precision and source == KnowledgeSourceType.LOCAL_KNOWLEDGE_BASE:
            reasons.append("提供高精确度答案")
        
        # 成本效益
        if capability.cost_per_query < 0.5:
            reasons.append("成本效益好")
        
        if capability.avg_latency < 1.0:
            reasons.append("响应速度快")
        
        return f"选择{source.value}因为: {', '.join(reasons)} (综合得分: {score:.2f})"
    
    def get_source_info(self) -> Dict[str, Any]:
        """获取知识源信息"""
        return {
            source.value: {
                'strengths': cap.strengths,
                'weaknesses': cap.weaknesses,
                'cost': cap.cost_per_query,
                'latency': cap.avg_latency,
                'domains': [d.value for d in cap.coverage_domains],
                'freshness': cap.freshness_score
            }
            for source, cap in self.source_capabilities.items()
        }


# 全局路由器实例
_knowledge_router_instance: Optional[KnowledgeRouter] = None


def get_knowledge_router() -> KnowledgeRouter:
    """获取知识路由器单例"""
    global _knowledge_router_instance
    
    if _knowledge_router_instance is None:
        _knowledge_router_instance = KnowledgeRouter()
    
    return _knowledge_router_instance 