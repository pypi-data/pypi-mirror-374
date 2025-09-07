"""
高级知识管理器
实现知识库细化、多源融合、智能领域匹配等高级功能

核心特性：
1. 知识库模块化管理
2. 多源知识融合策略
3. 智能领域匹配（基于FastText）
4. 置信度模糊处理
5. 知识质量评估
6. 动态知识更新
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeSubDomain(Enum):
    """知识子领域"""
    # FPGA设计相关
    FPGA_ARCHITECTURE = "fpga_architecture"
    HDL_DESIGN = "hdl_design"
    SYNTHESIS_OPTIMIZATION = "synthesis_optimization"
    TIMING_ANALYSIS = "timing_analysis"
    VERIFICATION = "verification"
    
    # 硬件设计相关
    DIGITAL_DESIGN = "digital_design"
    ANALOG_DESIGN = "analog_design"
    PCB_DESIGN = "pcb_design"
    SIGNAL_INTEGRITY = "signal_integrity"
    
    # 系统级相关
    EMBEDDED_SYSTEMS = "embedded_systems"
    SYSTEM_INTEGRATION = "system_integration"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    
    # 工具和流程
    EDA_TOOLS = "eda_tools"
    DEBUG_METHODS = "debug_methods"
    BEST_PRACTICES = "best_practices"


class KnowledgeSourcePriority(Enum):
    """知识源优先级"""
    OFFICIAL_DOCS = 1      # 官方文档 - 最高权威性
    EXPERT_KNOWLEDGE = 2   # 专家知识 - 高权威性
    COMMUNITY_PRACTICES = 3 # 社区最佳实践 - 中等权威性
    CODE_EXAMPLES = 4      # 代码示例 - 实用性高
    TUTORIALS = 5          # 教程文档 - 学习友好


class FusionStrategy(Enum):
    """融合策略"""
    WEIGHTED_COMBINATION = "weighted_combination"    # 加权组合
    HIERARCHICAL_SELECTION = "hierarchical_selection" # 分层选择
    CONSENSUS_BASED = "consensus_based"              # 共识驱动
    CONFIDENCE_THRESHOLD = "confidence_threshold"    # 置信度阈值
    DOMAIN_SPECIFIC = "domain_specific"              # 领域特定


@dataclass
class KnowledgeModule:
    """知识模块"""
    module_id: str
    name: str
    subdomain: KnowledgeSubDomain
    priority: KnowledgeSourcePriority
    content_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.8
    last_updated: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    success_rate: float = 0.8


@dataclass
class KnowledgeItem:
    """知识项"""
    item_id: str
    content: str
    title: str
    module_id: str
    subdomain: KnowledgeSubDomain
    keywords: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    quality_score: float = 0.8
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FusionResult:
    """融合结果"""
    fused_content: str
    source_items: List[KnowledgeItem]
    fusion_strategy: FusionStrategy
    confidence_score: float
    quality_metrics: Dict[str, float]
    reasoning: str


class DomainClassifier:
    """领域分类器（简化版FastText实现）"""
    
    def __init__(self):
        """初始化领域分类器"""
        # 简化的关键词映射（实际应该使用训练好的FastText模型）
        self.domain_keywords = {
            KnowledgeSubDomain.FPGA_ARCHITECTURE: [
                "fpga", "逻辑块", "clb", "slice", "lut", "查找表", "触发器", 
                "互连", "routing", "架构", "fabric"
            ],
            KnowledgeSubDomain.HDL_DESIGN: [
                "verilog", "systemverilog", "vhdl", "hdl", "模块", "module",
                "always", "assign", "wire", "reg", "端口", "port"
            ],
            KnowledgeSubDomain.TIMING_ANALYSIS: [
                "时序", "timing", "时钟", "clock", "建立时间", "setup", "保持时间", 
                "hold", "延迟", "delay", "约束", "constraint"
            ],
            KnowledgeSubDomain.VERIFICATION: [
                "验证", "verification", "testbench", "仿真", "simulation",
                "uvm", "覆盖率", "coverage", "断言", "assertion"
            ],
            KnowledgeSubDomain.SYNTHESIS_OPTIMIZATION: [
                "综合", "synthesis", "优化", "optimization", "面积", "area",
                "功耗", "power", "频率", "frequency", "资源", "resource"
            ],
            KnowledgeSubDomain.DEBUG_METHODS: [
                "调试", "debug", "排查", "troubleshoot", "错误", "error",
                "问题", "issue", "诊断", "diagnosis"
            ],
            KnowledgeSubDomain.BEST_PRACTICES: [
                "最佳实践", "best practice", "建议", "recommend", "经验", 
                "experience", "技巧", "tip", "指南", "guide"
            ]
        }
        
        # 预计算关键词权重
        self._compute_keyword_weights()
        
        logger.info("🧠 领域分类器初始化完成")
    
    def _compute_keyword_weights(self):
        """计算关键词权重"""
        # 简化的TF-IDF权重计算
        self.keyword_weights = {}
        all_keywords = []
        
        for domain, keywords in self.domain_keywords.items():
            all_keywords.extend(keywords)
        
        keyword_freq = defaultdict(int)
        for keyword in all_keywords:
            keyword_freq[keyword] += 1
        
        # 计算权重（IDF简化版）
        total_domains = len(self.domain_keywords)
        for domain, keywords in self.domain_keywords.items():
            domain_weights = {}
            for keyword in keywords:
                # 简化的IDF计算
                idf = np.log(total_domains / keyword_freq[keyword])
                domain_weights[keyword] = idf
            self.keyword_weights[domain] = domain_weights
    
    async def classify_domain(self, text: str) -> Tuple[KnowledgeSubDomain, float]:
        """分类文本的领域"""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0.0
            matched_keywords = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    weight = self.keyword_weights[domain].get(keyword, 1.0)
                    # 考虑关键词在文本中的频率
                    frequency = text_lower.count(keyword)
                    score += weight * frequency
                    matched_keywords += 1
            
            # 归一化得分
            if matched_keywords > 0:
                score = score / len(keywords)  # 归一化
                domain_scores[domain] = score
        
        if not domain_scores:
            return KnowledgeSubDomain.BEST_PRACTICES, 0.1  # 默认领域
        
        # 返回得分最高的领域
        best_domain = max(domain_scores, key=domain_scores.get)
        confidence = min(domain_scores[best_domain], 1.0)
        
        return best_domain, confidence
    
    async def classify_multiple_domains(self, text: str, top_k: int = 3) -> List[Tuple[KnowledgeSubDomain, float]]:
        """返回多个可能的领域"""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    weight = self.keyword_weights[domain].get(keyword, 1.0)
                    frequency = text_lower.count(keyword)
                    score += weight * frequency
            
            if score > 0:
                domain_scores[domain] = score / len(keywords)
        
        # 排序并返回前k个
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_domains[:top_k]


class AdvancedKnowledgeManager:
    """
    高级知识管理器
    
    核心功能：
    1. 模块化知识库管理
    2. 智能领域匹配
    3. 多源知识融合
    4. 质量评估和优化
    5. 动态更新机制
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化高级知识管理器"""
        self.config = config or {}
        
        # 知识模块存储
        self.knowledge_modules: Dict[str, KnowledgeModule] = {}
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        
        # 领域分类器
        self.domain_classifier = DomainClassifier()
        
        # 融合策略配置
        self.fusion_strategies = {
            FusionStrategy.WEIGHTED_COMBINATION: self._weighted_combination_fusion,
            FusionStrategy.HIERARCHICAL_SELECTION: self._hierarchical_selection_fusion,
            FusionStrategy.CONSENSUS_BASED: self._consensus_based_fusion,
            FusionStrategy.CONFIDENCE_THRESHOLD: self._confidence_threshold_fusion,
            FusionStrategy.DOMAIN_SPECIFIC: self._domain_specific_fusion
        }
        
        # 质量评估指标
        self.quality_metrics = {
            'relevance': 0.4,      # 相关性
            'accuracy': 0.3,       # 准确性
            'completeness': 0.2,   # 完整性
            'freshness': 0.1       # 新鲜度
        }
        
        # 置信度阈值配置
        self.confidence_thresholds = {
            'high_confidence': 0.8,
            'medium_confidence': 0.6,
            'low_confidence': 0.4,
            'fusion_threshold': 0.15  # 置信度差异阈值
        }
        
        logger.info("🔧 高级知识管理器初始化完成")
    
    async def register_knowledge_module(self, module: KnowledgeModule):
        """注册知识模块"""
        self.knowledge_modules[module.module_id] = module
        logger.info(f"📋 注册知识模块: {module.name} ({module.subdomain.value})")
    
    async def add_knowledge_item(self, item: KnowledgeItem):
        """添加知识项"""
        # 自动分类领域（如果未指定）
        if not item.subdomain:
            domain, confidence = await self.domain_classifier.classify_domain(item.content)
            item.subdomain = domain
            item.confidence = confidence
        
        # 评估质量
        item.quality_score = await self._assess_item_quality(item)
        
        self.knowledge_items[item.item_id] = item
        logger.debug(f"📝 添加知识项: {item.title} (领域: {item.subdomain.value})")
    
    async def intelligent_search(
        self, 
        query: str, 
        target_domains: List[KnowledgeSubDomain] = None,
        fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_COMBINATION,
        max_results: int = 5
    ) -> FusionResult:
        """智能知识搜索和融合"""
        
        # 1. 查询领域分类
        if not target_domains:
            query_domains = await self.domain_classifier.classify_multiple_domains(query, top_k=3)
            target_domains = [domain for domain, _ in query_domains]
        
        # 2. 检索相关知识项
        relevant_items = await self._retrieve_relevant_items(query, target_domains, max_results * 2)
        
        # 3. 评估置信度差异
        if len(relevant_items) >= 2:
            confidence_delta = relevant_items[0].confidence - relevant_items[1].confidence
            
            # 如果置信度差异小，使用融合策略
            if confidence_delta < self.confidence_thresholds['fusion_threshold']:
                fusion_result = await self._execute_fusion_strategy(
                    query, relevant_items[:max_results], fusion_strategy
                )
                return fusion_result
        
        # 4. 单源结果（置信度差异大）
        if relevant_items:
            return FusionResult(
                fused_content=relevant_items[0].content,
                source_items=relevant_items[:1],
                fusion_strategy=FusionStrategy.CONFIDENCE_THRESHOLD,
                confidence_score=relevant_items[0].confidence,
                quality_metrics={'single_source_quality': relevant_items[0].quality_score},
                reasoning=f"单源结果，置信度: {relevant_items[0].confidence:.3f}"
            )
        
        # 5. 无结果
        return FusionResult(
            fused_content="未找到相关知识",
            source_items=[],
            fusion_strategy=fusion_strategy,
            confidence_score=0.0,
            quality_metrics={},
            reasoning="未找到匹配的知识项"
        )
    
    async def _retrieve_relevant_items(
        self, 
        query: str, 
        target_domains: List[KnowledgeSubDomain],
        max_results: int
    ) -> List[KnowledgeItem]:
        """检索相关知识项"""
        
        relevant_items = []
        query_lower = query.lower()
        
        for item in self.knowledge_items.values():
            # 领域匹配
            if item.subdomain not in target_domains:
                continue
            
            # 简单的相关性计算（实际应该使用向量相似度）
            relevance_score = 0.0
            
            # 关键词匹配
            for keyword in item.keywords:
                if keyword.lower() in query_lower:
                    relevance_score += 0.3
            
            # 标题匹配
            title_words = item.title.lower().split()
            query_words = query_lower.split()
            title_match = len(set(title_words) & set(query_words)) / max(len(title_words), 1)
            relevance_score += title_match * 0.4
            
            # 内容匹配（简化）
            content_words = item.content.lower().split()
            content_match = len(set(content_words) & set(query_words)) / max(len(content_words), 1)
            relevance_score += content_match * 0.3
            
            if relevance_score > 0.1:  # 最低相关性阈值
                item.confidence = min(relevance_score * item.quality_score, 1.0)
                relevant_items.append(item)
        
        # 按置信度排序
        relevant_items.sort(key=lambda x: x.confidence, reverse=True)
        return relevant_items[:max_results]
    
    async def _execute_fusion_strategy(
        self, 
        query: str, 
        items: List[KnowledgeItem], 
        strategy: FusionStrategy
    ) -> FusionResult:
        """执行融合策略"""
        
        fusion_func = self.fusion_strategies.get(strategy)
        if not fusion_func:
            raise ValueError(f"不支持的融合策略: {strategy}")
        
        return await fusion_func(query, items)
    
    async def _weighted_combination_fusion(
        self, 
        query: str, 
        items: List[KnowledgeItem]
    ) -> FusionResult:
        """加权组合融合"""
        
        if not items:
            return FusionResult("", [], FusionStrategy.WEIGHTED_COMBINATION, 0.0, {}, "无知识项")
        
        # 计算权重
        total_confidence = sum(item.confidence for item in items)
        weights = [item.confidence / total_confidence for item in items]
        
        # 融合内容
        fused_parts = []
        for i, item in enumerate(items):
            weight_info = f"(权重: {weights[i]:.2f})"
            fused_parts.append(f"【来源{i+1} {weight_info}】\n{item.content[:200]}...")
        
        fused_content = "\n\n".join(fused_parts)
        
        # 计算融合置信度
        fusion_confidence = sum(w * item.confidence for w, item in zip(weights, items))
        
        # 质量指标
        quality_metrics = {
            'weighted_confidence': fusion_confidence,
            'source_count': len(items),
            'diversity_score': len(set(item.subdomain for item in items)) / len(items)
        }
        
        reasoning = f"加权融合{len(items)}个来源，融合置信度: {fusion_confidence:.3f}"
        
        return FusionResult(
            fused_content=fused_content,
            source_items=items,
            fusion_strategy=FusionStrategy.WEIGHTED_COMBINATION,
            confidence_score=fusion_confidence,
            quality_metrics=quality_metrics,
            reasoning=reasoning
        )
    
    async def _hierarchical_selection_fusion(
        self, 
        query: str, 
        items: List[KnowledgeItem]
    ) -> FusionResult:
        """分层选择融合"""
        
        if not items:
            return FusionResult("", [], FusionStrategy.HIERARCHICAL_SELECTION, 0.0, {}, "无知识项")
        
        # 按模块优先级分层
        priority_groups = defaultdict(list)
        for item in items:
            module = self.knowledge_modules.get(item.module_id)
            if module:
                priority_groups[module.priority].append(item)
        
        # 选择最高优先级组
        if priority_groups:
            highest_priority = min(priority_groups.keys())  # 数字越小优先级越高
            selected_items = priority_groups[highest_priority]
        else:
            selected_items = items
        
        # 在同优先级内按置信度选择
        selected_items.sort(key=lambda x: x.confidence, reverse=True)
        best_item = selected_items[0]
        
        quality_metrics = {
            'selected_priority': highest_priority.value if priority_groups else 'unknown',
            'confidence': best_item.confidence,
            'alternatives_count': len(items) - 1
        }
        
        reasoning = f"分层选择：优先级{highest_priority.value}，置信度{best_item.confidence:.3f}"
        
        return FusionResult(
            fused_content=best_item.content,
            source_items=[best_item],
            fusion_strategy=FusionStrategy.HIERARCHICAL_SELECTION,
            confidence_score=best_item.confidence,
            quality_metrics=quality_metrics,
            reasoning=reasoning
        )
    
    async def _consensus_based_fusion(
        self, 
        query: str, 
        items: List[KnowledgeItem]
    ) -> FusionResult:
        """共识驱动融合"""
        
        if not items:
            return FusionResult("", [], FusionStrategy.CONSENSUS_BASED, 0.0, {}, "无知识项")
        
        # 简化的共识算法：找到内容相似度高的项
        consensus_items = []
        
        # 如果只有一个或两个项，直接使用
        if len(items) <= 2:
            consensus_items = items
        else:
            # 计算内容相似度（简化版）
            for i, item1 in enumerate(items):
                agreement_count = 0
                for j, item2 in enumerate(items):
                    if i != j:
                        # 简单的词汇重叠度计算
                        words1 = set(item1.content.lower().split())
                        words2 = set(item2.content.lower().split())
                        overlap = len(words1 & words2) / max(len(words1 | words2), 1)
                        if overlap > 0.3:  # 相似度阈值
                            agreement_count += 1
                
                # 如果有足够的共识，加入结果
                if agreement_count >= len(items) * 0.4:  # 40%共识阈值
                    consensus_items.append(item1)
        
        if not consensus_items:
            consensus_items = [items[0]]  # 降级到最高置信度项
        
        # 融合共识内容
        if len(consensus_items) == 1:
            fused_content = consensus_items[0].content
        else:
            fused_content = "基于多源共识的融合结果：\n\n"
            for i, item in enumerate(consensus_items):
                fused_content += f"【共识来源{i+1}】\n{item.content[:150]}...\n\n"
        
        consensus_confidence = sum(item.confidence for item in consensus_items) / len(consensus_items)
        
        quality_metrics = {
            'consensus_ratio': len(consensus_items) / len(items),
            'consensus_confidence': consensus_confidence,
            'total_sources': len(items)
        }
        
        reasoning = f"共识融合：{len(consensus_items)}/{len(items)}项达成共识"
        
        return FusionResult(
            fused_content=fused_content,
            source_items=consensus_items,
            fusion_strategy=FusionStrategy.CONSENSUS_BASED,
            confidence_score=consensus_confidence,
            quality_metrics=quality_metrics,
            reasoning=reasoning
        )
    
    async def _confidence_threshold_fusion(
        self, 
        query: str, 
        items: List[KnowledgeItem]
    ) -> FusionResult:
        """置信度阈值融合"""
        
        if not items:
            return FusionResult("", [], FusionStrategy.CONFIDENCE_THRESHOLD, 0.0, {}, "无知识项")
        
        # 过滤高置信度项
        high_conf_items = [
            item for item in items 
            if item.confidence >= self.confidence_thresholds['high_confidence']
        ]
        
        if not high_conf_items:
            # 降级到中等置信度
            medium_conf_items = [
                item for item in items
                if item.confidence >= self.confidence_thresholds['medium_confidence']
            ]
            selected_items = medium_conf_items or items[:1]
            threshold_used = "medium"
        else:
            selected_items = high_conf_items
            threshold_used = "high"
        
        # 使用加权组合融合高置信度项
        return await self._weighted_combination_fusion(query, selected_items)
    
    async def _domain_specific_fusion(
        self, 
        query: str, 
        items: List[KnowledgeItem]
    ) -> FusionResult:
        """领域特定融合"""
        
        if not items:
            return FusionResult("", [], FusionStrategy.DOMAIN_SPECIFIC, 0.0, {}, "无知识项")
        
        # 按领域分组
        domain_groups = defaultdict(list)
        for item in items:
            domain_groups[item.subdomain].append(item)
        
        # 选择最相关的领域
        query_domains = await self.domain_classifier.classify_multiple_domains(query, top_k=2)
        primary_domain = query_domains[0][0] if query_domains else list(domain_groups.keys())[0]
        
        # 优先使用主要领域的知识
        if primary_domain in domain_groups:
            selected_items = domain_groups[primary_domain]
        else:
            # 降级到最高置信度项
            selected_items = sorted(items, key=lambda x: x.confidence, reverse=True)[:2]
        
        # 领域内加权融合
        fusion_result = await self._weighted_combination_fusion(query, selected_items)
        fusion_result.fusion_strategy = FusionStrategy.DOMAIN_SPECIFIC
        fusion_result.reasoning = f"领域特定融合：{primary_domain.value}领域"
        
        return fusion_result
    
    async def _assess_item_quality(self, item: KnowledgeItem) -> float:
        """评估知识项质量"""
        
        quality_score = 0.0
        
        # 1. 相关性评估（基于关键词密度）
        if item.keywords:
            keyword_density = len(item.keywords) / max(len(item.content.split()), 1)
            relevance_score = min(keyword_density * 10, 1.0)  # 归一化
        else:
            relevance_score = 0.5
        
        quality_score += relevance_score * self.quality_metrics['relevance']
        
        # 2. 准确性评估（基于模块优先级）
        module = self.knowledge_modules.get(item.module_id)
        if module:
            accuracy_score = (6 - module.priority.value) / 5  # 转换为0-1分数
        else:
            accuracy_score = 0.6
        
        quality_score += accuracy_score * self.quality_metrics['accuracy']
        
        # 3. 完整性评估（基于内容长度）
        content_length = len(item.content)
        if content_length > 500:
            completeness_score = 1.0
        elif content_length > 200:
            completeness_score = 0.8
        elif content_length > 100:
            completeness_score = 0.6
        else:
            completeness_score = 0.4
        
        quality_score += completeness_score * self.quality_metrics['completeness']
        
        # 4. 新鲜度评估（基于创建时间）
        days_old = (datetime.now() - item.created_at).days
        if days_old < 30:
            freshness_score = 1.0
        elif days_old < 90:
            freshness_score = 0.8
        elif days_old < 365:
            freshness_score = 0.6
        else:
            freshness_score = 0.4
        
        quality_score += freshness_score * self.quality_metrics['freshness']
        
        return min(quality_score, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识管理器统计信息"""
        
        # 模块统计
        module_stats = defaultdict(int)
        for module in self.knowledge_modules.values():
            module_stats[module.subdomain.value] += 1
        
        # 知识项统计
        item_stats = defaultdict(int)
        quality_scores = []
        confidence_scores = []
        
        for item in self.knowledge_items.values():
            item_stats[item.subdomain.value] += 1
            quality_scores.append(item.quality_score)
            confidence_scores.append(item.confidence)
        
        return {
            'total_modules': len(self.knowledge_modules),
            'total_items': len(self.knowledge_items),
            'module_distribution': dict(module_stats),
            'item_distribution': dict(item_stats),
            'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'supported_domains': len(set(item.subdomain for item in self.knowledge_items.values())),
            'fusion_strategies': list(self.fusion_strategies.keys())
        }


# 全局高级知识管理器实例
_advanced_knowledge_manager: Optional[AdvancedKnowledgeManager] = None


def get_advanced_knowledge_manager() -> AdvancedKnowledgeManager:
    """获取高级知识管理器单例"""
    global _advanced_knowledge_manager
    
    if _advanced_knowledge_manager is None:
        _advanced_knowledge_manager = AdvancedKnowledgeManager()
    
    return _advanced_knowledge_manager 