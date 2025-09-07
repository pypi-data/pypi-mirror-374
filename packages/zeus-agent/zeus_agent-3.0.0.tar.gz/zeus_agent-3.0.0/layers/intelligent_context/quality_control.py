"""
智能上下文层 - 质量控制组件

实现智能上下文处理的质量保证机制：
- 上下文质量评估
- 内容一致性检查
- 准确性验证
- 完整性检查
- 质量指标监控
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from datetime import datetime

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask
from layers.framework.abstractions.result import UniversalResult, ResultStatus

logger = logging.getLogger(__name__)

class QualityMetric(Enum):
    """质量指标类型"""
    ACCURACY = "accuracy"           # 准确性
    COMPLETENESS = "completeness"   # 完整性
    CONSISTENCY = "consistency"     # 一致性
    RELEVANCE = "relevance"         # 相关性
    CLARITY = "clarity"             # 清晰度
    COHERENCE = "coherence"         # 连贯性
    FACTUALITY = "factuality"       # 事实性
    COVERAGE = "coverage"           # 覆盖度

class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"         # 优秀 (90-100)
    GOOD = "good"                  # 良好 (75-89)
    ACCEPTABLE = "acceptable"       # 可接受 (60-74)
    POOR = "poor"                  # 较差 (40-59)
    UNACCEPTABLE = "unacceptable"   # 不可接受 (0-39)

class QualityCheckType(Enum):
    """质量检查类型"""
    BASIC = "basic"                # 基础检查
    COMPREHENSIVE = "comprehensive" # 全面检查
    DOMAIN_SPECIFIC = "domain_specific" # 领域特定检查
    CUSTOM = "custom"              # 自定义检查

@dataclass
class QualityMetricResult:
    """质量指标结果"""
    metric: QualityMetric
    score: float                    # 0.0 - 1.0
    level: QualityLevel
    details: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class QualityAssessment:
    """质量评估结果"""
    overall_score: float            # 总体评分
    overall_level: QualityLevel     # 总体等级
    metric_results: Dict[QualityMetric, QualityMetricResult] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    assessment_type: QualityCheckType = QualityCheckType.BASIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_metric_score(self, metric: QualityMetric) -> float:
        """获取特定指标的分数"""
        if metric in self.metric_results:
            return self.metric_results[metric].score
        return 0.0
    
    def get_all_issues(self) -> List[str]:
        """获取所有问题"""
        all_issues = []
        for result in self.metric_results.values():
            all_issues.extend(result.issues)
        return all_issues
    
    def get_all_recommendations(self) -> List[str]:
        """获取所有建议"""
        all_recommendations = []
        for result in self.metric_results.values():
            all_recommendations.extend(result.recommendations)
        return all_recommendations
    
    def get_quality_level(self) -> QualityLevel:
        """获取质量等级"""
        return self.overall_level

class QualityControl:
    """
    质量控制组件
    
    负责智能上下文处理的质量保证：
    1. 多维度质量评估
    2. 自动质量检查
    3. 质量改进建议
    4. 质量趋势监控
    5. 质量标准管理
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.quality_history: List[QualityAssessment] = []
        self.quality_standards: Dict[str, Dict[QualityMetric, float]] = self._load_quality_standards()
        self.custom_checks: Dict[str, callable] = {}
        
        # 质量统计
        self.metrics = {
            'total_assessments': 0,
            'passed_assessments': 0,
            'failed_assessments': 0,
            'average_scores': {},
            'quality_trends': {}
        }
        
        logger.info("QualityControl component initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'min_acceptable_score': 0.6,
            'enable_auto_fix': True,
            'enable_detailed_analysis': True,
            'quality_check_timeout': 30,
            'max_issues_per_metric': 10,
            'enable_trend_analysis': True
        }
    
    def _load_quality_standards(self) -> Dict[str, Dict[QualityMetric, float]]:
        """加载质量标准"""
        return {
            'general': {
                QualityMetric.ACCURACY: 0.8,
                QualityMetric.COMPLETENESS: 0.7,
                QualityMetric.CONSISTENCY: 0.75,
                QualityMetric.RELEVANCE: 0.8,
                QualityMetric.CLARITY: 0.7,
                QualityMetric.COHERENCE: 0.75,
                QualityMetric.FACTUALITY: 0.85,
                QualityMetric.COVERAGE: 0.7
            },
            'technical': {
                QualityMetric.ACCURACY: 0.9,
                QualityMetric.COMPLETENESS: 0.85,
                QualityMetric.CONSISTENCY: 0.8,
                QualityMetric.RELEVANCE: 0.85,
                QualityMetric.CLARITY: 0.75,
                QualityMetric.COHERENCE: 0.8,
                QualityMetric.FACTUALITY: 0.95,
                QualityMetric.COVERAGE: 0.8
            },
            'creative': {
                QualityMetric.ACCURACY: 0.7,
                QualityMetric.COMPLETENESS: 0.6,
                QualityMetric.CONSISTENCY: 0.65,
                QualityMetric.RELEVANCE: 0.75,
                QualityMetric.CLARITY: 0.8,
                QualityMetric.COHERENCE: 0.85,
                QualityMetric.FACTUALITY: 0.7,
                QualityMetric.COVERAGE: 0.65
            }
        }
    
    async def assess_quality(self, 
                           context: UniversalContext, 
                           task: Optional[UniversalTask] = None,
                           check_type: QualityCheckType = QualityCheckType.BASIC,
                           domain: str = 'general') -> QualityAssessment:
        """
        评估上下文质量
        
        Args:
            context: 要评估的上下文
            task: 相关任务（可选）
            check_type: 检查类型
            domain: 领域类型
            
        Returns:
            质量评估结果
        """
        try:
            logger.info(f"Starting quality assessment for {check_type.value} check in {domain} domain")
            
            # 获取质量标准
            standards = self.quality_standards.get(domain, self.quality_standards['general'])
            
            # 执行各项质量检查
            metric_results = {}
            
            if check_type in [QualityCheckType.BASIC, QualityCheckType.COMPREHENSIVE]:
                # 基础质量检查
                metric_results[QualityMetric.COMPLETENESS] = await self._check_completeness(context, task)
                metric_results[QualityMetric.CONSISTENCY] = await self._check_consistency(context)
                metric_results[QualityMetric.RELEVANCE] = await self._check_relevance(context, task)
                metric_results[QualityMetric.CLARITY] = await self._check_clarity(context)
                
            if check_type == QualityCheckType.COMPREHENSIVE:
                # 全面质量检查
                metric_results[QualityMetric.ACCURACY] = await self._check_accuracy(context, task)
                metric_results[QualityMetric.COHERENCE] = await self._check_coherence(context)
                metric_results[QualityMetric.FACTUALITY] = await self._check_factuality(context)
                metric_results[QualityMetric.COVERAGE] = await self._check_coverage(context, task)
            
            if check_type == QualityCheckType.DOMAIN_SPECIFIC:
                # 领域特定检查
                metric_results.update(await self._domain_specific_checks(context, task, domain))
            
            if check_type == QualityCheckType.CUSTOM:
                # 自定义检查
                metric_results.update(await self._custom_checks_execution(context, task))
            
            # 计算总体评分
            overall_score = self._calculate_overall_score(metric_results, standards)
            overall_level = self._score_to_level(overall_score)
            
            # 创建评估结果
            assessment = QualityAssessment(
                overall_score=overall_score,
                overall_level=overall_level,
                metric_results=metric_results,
                assessment_type=check_type,
                metadata={
                    'domain': domain,
                    'context_size': len(str(context.data)),
                    'task_type': task.task_type.value if task else None,
                    'standards_used': domain
                }
            )
            
            # 记录评估历史
            self.quality_history.append(assessment)
            self._update_metrics(assessment)
            
            logger.info(f"Quality assessment completed: {overall_level.value} ({overall_score:.2f})")
            return assessment
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            # 返回默认评估结果
            return QualityAssessment(
                overall_score=0.0,
                overall_level=QualityLevel.UNACCEPTABLE,
                metadata={'error': str(e)}
            )
    
    async def _check_completeness(self, context: UniversalContext, task: Optional[UniversalTask]) -> QualityMetricResult:
        """检查完整性"""
        issues = []
        recommendations = []
        
        # 检查上下文是否为空
        if not context.data:
            issues.append("Context is empty")
            recommendations.append("Provide meaningful context data")
            return QualityMetricResult(
                metric=QualityMetric.COMPLETENESS,
                score=0.0,
                level=QualityLevel.UNACCEPTABLE,
                issues=issues,
                recommendations=recommendations
            )
        
        # 检查关键字段
        score = 0.5  # 基础分
        required_fields = ['content', 'message', 'data', 'information']
        has_content = any(field in context.data for field in required_fields)
        
        if has_content:
            score += 0.3
        else:
            issues.append("No content fields found")
            recommendations.append("Add content, message, or data fields")
        
        # 检查内容长度
        content_length = sum(len(str(v)) for v in context.data.values())
        if content_length > 100:
            score += 0.2
        elif content_length < 10:
            issues.append("Content is too short")
            recommendations.append("Provide more detailed information")
        
        return QualityMetricResult(
            metric=QualityMetric.COMPLETENESS,
            score=min(score, 1.0),
            level=self._score_to_level(score),
            details={'content_length': content_length, 'fields_count': len(context.data)},
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_consistency(self, context: UniversalContext) -> QualityMetricResult:
        """检查一致性"""
        issues = []
        recommendations = []
        score = 0.8  # 默认较高分数
        
        # 检查数据类型一致性
        type_consistency = self._check_type_consistency(context.data)
        if not type_consistency['consistent']:
            score -= 0.2
            issues.extend(type_consistency['issues'])
            recommendations.append("Ensure consistent data types")
        
        # 检查命名一致性
        naming_consistency = self._check_naming_consistency(context.data)
        if not naming_consistency['consistent']:
            score -= 0.1
            issues.extend(naming_consistency['issues'])
            recommendations.append("Use consistent naming conventions")
        
        return QualityMetricResult(
            metric=QualityMetric.CONSISTENCY,
            score=max(score, 0.0),
            level=self._score_to_level(score),
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_relevance(self, context: UniversalContext, task: Optional[UniversalTask]) -> QualityMetricResult:
        """检查相关性"""
        issues = []
        recommendations = []
        
        if not task:
            # 没有任务时，默认相关性为中等
            return QualityMetricResult(
                metric=QualityMetric.RELEVANCE,
                score=0.7,
                level=QualityLevel.GOOD,
                details={'note': 'No task provided for relevance check'}
            )
        
        # 检查上下文与任务的相关性
        task_content = str(task.content).lower() if hasattr(task, 'content') else ""
        context_content = str(context.data).lower()
        
        # 简单的关键词匹配
        relevance_score = self._calculate_text_similarity(task_content, context_content)
        
        if relevance_score < 0.3:
            issues.append("Low relevance between context and task")
            recommendations.append("Ensure context is related to the task")
        
        return QualityMetricResult(
            metric=QualityMetric.RELEVANCE,
            score=relevance_score,
            level=self._score_to_level(relevance_score),
            details={'similarity_score': relevance_score},
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_clarity(self, context: UniversalContext) -> QualityMetricResult:
        """检查清晰度"""
        issues = []
        recommendations = []
        score = 0.7  # 默认分数
        
        # 检查文本内容的清晰度
        text_content = self._extract_text_content(context.data)
        
        if text_content:
            # 检查句子长度
            sentences = re.split(r'[.!?]+', text_content)
            avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
            
            if avg_sentence_length > 30:
                score -= 0.1
                issues.append("Sentences are too long")
                recommendations.append("Use shorter, clearer sentences")
            
            # 检查复杂词汇
            complex_words = len([w for w in text_content.split() if len(w) > 10])
            total_words = len(text_content.split())
            
            if total_words > 0 and complex_words / total_words > 0.3:
                score -= 0.1
                issues.append("Too many complex words")
                recommendations.append("Use simpler vocabulary when possible")
        
        return QualityMetricResult(
            metric=QualityMetric.CLARITY,
            score=max(score, 0.0),
            level=self._score_to_level(score),
            details={'avg_sentence_length': avg_sentence_length if 'avg_sentence_length' in locals() else 0},
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_accuracy(self, context: UniversalContext, task: Optional[UniversalTask]) -> QualityMetricResult:
        """检查准确性"""
        # 这是一个简化的准确性检查
        # 实际实现可能需要外部知识库或事实检查服务
        return QualityMetricResult(
            metric=QualityMetric.ACCURACY,
            score=0.8,  # 默认假设准确性较高
            level=QualityLevel.GOOD,
            details={'note': 'Simplified accuracy check'}
        )
    
    async def _check_coherence(self, context: UniversalContext) -> QualityMetricResult:
        """检查连贯性"""
        issues = []
        recommendations = []
        score = 0.75  # 默认分数
        
        text_content = self._extract_text_content(context.data)
        
        if text_content:
            # 检查逻辑连接词
            connectors = ['however', 'therefore', 'moreover', 'furthermore', 'consequently', 'additionally']
            connector_count = sum(text_content.lower().count(c) for c in connectors)
            
            if len(text_content.split()) > 50 and connector_count == 0:
                score -= 0.2
                issues.append("Lack of logical connectors")
                recommendations.append("Use connecting words to improve flow")
        
        return QualityMetricResult(
            metric=QualityMetric.COHERENCE,
            score=max(score, 0.0),
            level=self._score_to_level(score),
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_factuality(self, context: UniversalContext) -> QualityMetricResult:
        """检查事实性"""
        # 简化的事实性检查
        return QualityMetricResult(
            metric=QualityMetric.FACTUALITY,
            score=0.8,
            level=QualityLevel.GOOD,
            details={'note': 'Simplified factuality check'}
        )
    
    async def _check_coverage(self, context: UniversalContext, task: Optional[UniversalTask]) -> QualityMetricResult:
        """检查覆盖度"""
        if not task:
            return QualityMetricResult(
                metric=QualityMetric.COVERAGE,
                score=0.7,
                level=QualityLevel.GOOD,
                details={'note': 'No task provided for coverage check'}
            )
        
        # 简化的覆盖度检查
        score = 0.7
        return QualityMetricResult(
            metric=QualityMetric.COVERAGE,
            score=score,
            level=self._score_to_level(score),
            details={'note': 'Simplified coverage check'}
        )
    
    async def _domain_specific_checks(self, context: UniversalContext, task: Optional[UniversalTask], domain: str) -> Dict[QualityMetric, QualityMetricResult]:
        """领域特定检查"""
        # 这里可以根据不同领域实现特定的检查逻辑
        return {}
    
    async def _custom_checks_execution(self, context: UniversalContext, task: Optional[UniversalTask]) -> Dict[QualityMetric, QualityMetricResult]:
        """执行自定义检查"""
        results = {}
        for check_name, check_func in self.custom_checks.items():
            try:
                result = await check_func(context, task)
                if isinstance(result, QualityMetricResult):
                    results[result.metric] = result
            except Exception as e:
                logger.error(f"Custom check {check_name} failed: {str(e)}")
        return results
    
    def _calculate_overall_score(self, metric_results: Dict[QualityMetric, QualityMetricResult], standards: Dict[QualityMetric, float]) -> float:
        """计算总体评分"""
        if not metric_results:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, result in metric_results.items():
            weight = standards.get(metric, 1.0)
            total_score += result.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """将分数转换为质量等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.4:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _check_type_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """检查数据类型一致性"""
        issues = []
        
        # 检查相似键的值类型是否一致
        type_groups = {}
        for key, value in data.items():
            value_type = type(value).__name__
            if value_type not in type_groups:
                type_groups[value_type] = []
            type_groups[value_type].append(key)
        
        # 这里可以添加更复杂的类型一致性检查逻辑
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }
    
    def _check_naming_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """检查命名一致性"""
        issues = []
        keys = list(data.keys())
        
        # 检查命名风格
        snake_case_count = sum(1 for key in keys if '_' in key and key.islower())
        camel_case_count = sum(1 for key in keys if any(c.isupper() for c in key[1:]) and '_' not in key)
        
        if snake_case_count > 0 and camel_case_count > 0:
            issues.append("Mixed naming conventions (snake_case and camelCase)")
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似性"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的词汇重叠计算
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """提取文本内容"""
        text_parts = []
        
        def extract_text(obj):
            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(data)
        return ' '.join(text_parts)
    
    def _update_metrics(self, assessment: QualityAssessment):
        """更新质量统计指标"""
        self.metrics['total_assessments'] += 1
        
        if assessment.overall_level in [QualityLevel.EXCELLENT, QualityLevel.GOOD, QualityLevel.ACCEPTABLE]:
            self.metrics['passed_assessments'] += 1
        else:
            self.metrics['failed_assessments'] += 1
        
        # 更新平均分数
        for metric, result in assessment.metric_results.items():
            metric_name = metric.value
            if metric_name not in self.metrics['average_scores']:
                self.metrics['average_scores'][metric_name] = []
            self.metrics['average_scores'][metric_name].append(result.score)
    
    def add_custom_check(self, name: str, check_function: callable):
        """添加自定义检查"""
        self.custom_checks[name] = check_function
        logger.info(f"Added custom quality check: {name}")
    
    def remove_custom_check(self, name: str):
        """移除自定义检查"""
        if name in self.custom_checks:
            del self.custom_checks[name]
            logger.info(f"Removed custom quality check: {name}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取质量控制指标"""
        # 计算平均分数
        avg_scores = {}
        for metric, scores in self.metrics['average_scores'].items():
            avg_scores[metric] = sum(scores) / len(scores) if scores else 0.0
        
        return {
            'total_assessments': self.metrics['total_assessments'],
            'passed_assessments': self.metrics['passed_assessments'],
            'failed_assessments': self.metrics['failed_assessments'],
            'pass_rate': self.metrics['passed_assessments'] / max(self.metrics['total_assessments'], 1),
            'average_scores': avg_scores,
            'recent_assessments': len([a for a in self.quality_history[-10:] if a]),
            'quality_standards_count': len(self.quality_standards),
            'custom_checks_count': len(self.custom_checks)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取组件状态"""
        return {
            'component': 'QualityControl',
            'configuration': self.config,
            'quality_standards': list(self.quality_standards.keys()),
            'supported_metrics': [metric.value for metric in QualityMetric],
            'supported_levels': [level.value for level in QualityLevel],
            'check_types': [check_type.value for check_type in QualityCheckType],
            'metrics': self.get_metrics(),
            'history_size': len(self.quality_history),
            'custom_checks': list(self.custom_checks.keys())
        }
    
    def configure(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)
        logger.info("QualityControl configuration updated") 