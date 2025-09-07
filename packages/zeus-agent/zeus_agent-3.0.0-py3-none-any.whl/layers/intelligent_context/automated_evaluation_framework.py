"""
自动化评估框架 - 系统性能自动化测试与优化

实现完整的自动化评估系统，包括基准测试、性能监控、
质量评估、趋势分析和自动化优化建议。

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
import json
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import logging
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

class EvaluationMetricType(Enum):
    """评估指标类型"""
    ROUTE_ACCURACY = "route_accuracy"
    RESPONSE_QUALITY = "response_quality"
    COST_EFFICIENCY = "cost_efficiency"
    USER_SATISFACTION = "user_satisfaction"
    SYSTEM_PERFORMANCE = "system_performance"
    CACHE_PERFORMANCE = "cache_performance"

class BenchmarkCategory(Enum):
    """基准测试类别"""
    FPGA_BASICS = "fpga_basics"
    ADVANCED_DESIGN = "advanced_design"
    TROUBLESHOOTING = "troubleshooting"
    CREATIVE_TASKS = "creative_tasks"
    MIXED_COMPLEXITY = "mixed_complexity"

class TestResult(Enum):
    """测试结果状态"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class BenchmarkQuestion:
    """基准测试问题"""
    question_id: str
    category: BenchmarkCategory
    query: str
    expected_source: str
    expected_confidence_min: float
    expected_cost_max: float
    expected_latency_max: float
    user_role: str
    complexity_level: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """评估结果"""
    question_id: str
    query: str
    actual_source: str
    expected_source: str
    actual_confidence: float
    expected_confidence_min: float
    actual_cost: float
    expected_cost_max: float
    actual_latency: float
    expected_latency_max: float
    result_status: TestResult
    score: float
    reasoning: List[str]
    timestamp: datetime

@dataclass
class MetricResult:
    """指标结果"""
    metric_type: EvaluationMetricType
    value: float
    target: float
    status: TestResult
    trend: str  # "improving", "stable", "degrading"
    details: Dict[str, Any]

@dataclass
class EvaluationReport:
    """评估报告"""
    report_id: str
    timestamp: datetime
    overall_score: float
    test_results: List[EvaluationResult]
    metric_results: List[MetricResult]
    performance_trends: Dict[str, List[float]]
    recommendations: List[str]
    next_evaluation_time: datetime
    summary: Dict[str, Any]

class EvaluationMetric(ABC):
    """评估指标抽象基类"""
    
    @abstractmethod
    async def calculate(self, test_results: List[EvaluationResult]) -> MetricResult:
        """计算指标"""
        pass
    
    @abstractmethod
    def get_target_value(self) -> float:
        """获取目标值"""
        pass

class RouteAccuracyMetric(EvaluationMetric):
    """路由准确性指标"""
    
    async def calculate(self, test_results: List[EvaluationResult]) -> MetricResult:
        if not test_results:
            return MetricResult(
                metric_type=EvaluationMetricType.ROUTE_ACCURACY,
                value=0.0,
                target=self.get_target_value(),
                status=TestResult.FAIL,
                trend="unknown",
                details={"total_tests": 0}
            )
        
        correct_routes = sum(1 for result in test_results 
                           if result.actual_source == result.expected_source)
        accuracy = correct_routes / len(test_results)
        
        status = TestResult.PASS if accuracy >= self.get_target_value() else TestResult.FAIL
        
        return MetricResult(
            metric_type=EvaluationMetricType.ROUTE_ACCURACY,
            value=accuracy,
            target=self.get_target_value(),
            status=status,
            trend="stable",  # 需要历史数据来计算趋势
            details={
                "total_tests": len(test_results),
                "correct_routes": correct_routes,
                "accuracy_percentage": accuracy * 100
            }
        )
    
    def get_target_value(self) -> float:
        return 0.85  # 85%准确率目标

class ResponseQualityMetric(EvaluationMetric):
    """响应质量指标"""
    
    async def calculate(self, test_results: List[EvaluationResult]) -> MetricResult:
        if not test_results:
            return MetricResult(
                metric_type=EvaluationMetricType.RESPONSE_QUALITY,
                value=0.0,
                target=self.get_target_value(),
                status=TestResult.FAIL,
                trend="unknown",
                details={"total_tests": 0}
            )
        
        # 基于置信度评估质量
        confidence_scores = [result.actual_confidence for result in test_results]
        avg_confidence = statistics.mean(confidence_scores)
        
        # 检查是否满足最低置信度要求
        meets_min_confidence = sum(1 for result in test_results 
                                 if result.actual_confidence >= result.expected_confidence_min)
        confidence_compliance = meets_min_confidence / len(test_results)
        
        # 综合质量分数
        quality_score = (avg_confidence + confidence_compliance) / 2
        
        status = TestResult.PASS if quality_score >= self.get_target_value() else TestResult.FAIL
        
        return MetricResult(
            metric_type=EvaluationMetricType.RESPONSE_QUALITY,
            value=quality_score,
            target=self.get_target_value(),
            status=status,
            trend="stable",
            details={
                "average_confidence": avg_confidence,
                "confidence_compliance": confidence_compliance,
                "min_confidence": min(confidence_scores),
                "max_confidence": max(confidence_scores)
            }
        )
    
    def get_target_value(self) -> float:
        return 0.80  # 80%质量目标

class CostEfficiencyMetric(EvaluationMetric):
    """成本效率指标"""
    
    async def calculate(self, test_results: List[EvaluationResult]) -> MetricResult:
        if not test_results:
            return MetricResult(
                metric_type=EvaluationMetricType.COST_EFFICIENCY,
                value=0.0,
                target=self.get_target_value(),
                status=TestResult.FAIL,
                trend="unknown",
                details={"total_tests": 0}
            )
        
        # 计算成本合规性
        within_budget = sum(1 for result in test_results 
                          if result.actual_cost <= result.expected_cost_max)
        cost_compliance = within_budget / len(test_results)
        
        # 计算平均成本效率
        total_actual_cost = sum(result.actual_cost for result in test_results)
        total_expected_cost = sum(result.expected_cost_max for result in test_results)
        cost_efficiency = 1 - (total_actual_cost / max(total_expected_cost, 0.001))
        
        # 综合效率分数
        efficiency_score = (cost_compliance + max(0, cost_efficiency)) / 2
        
        status = TestResult.PASS if efficiency_score >= self.get_target_value() else TestResult.FAIL
        
        return MetricResult(
            metric_type=EvaluationMetricType.COST_EFFICIENCY,
            value=efficiency_score,
            target=self.get_target_value(),
            status=status,
            trend="stable",
            details={
                "cost_compliance": cost_compliance,
                "total_actual_cost": total_actual_cost,
                "total_expected_cost": total_expected_cost,
                "average_cost": total_actual_cost / len(test_results)
            }
        )
    
    def get_target_value(self) -> float:
        return 0.75  # 75%成本效率目标

class SystemPerformanceMetric(EvaluationMetric):
    """系统性能指标"""
    
    async def calculate(self, test_results: List[EvaluationResult]) -> MetricResult:
        if not test_results:
            return MetricResult(
                metric_type=EvaluationMetricType.SYSTEM_PERFORMANCE,
                value=0.0,
                target=self.get_target_value(),
                status=TestResult.FAIL,
                trend="unknown",
                details={"total_tests": 0}
            )
        
        # 计算延迟合规性
        within_latency = sum(1 for result in test_results 
                           if result.actual_latency <= result.expected_latency_max)
        latency_compliance = within_latency / len(test_results)
        
        # 计算平均性能
        latencies = [result.actual_latency for result in test_results]
        avg_latency = statistics.mean(latencies)
        expected_avg_latency = statistics.mean([result.expected_latency_max for result in test_results])
        
        # 性能分数（延迟越低越好）
        performance_ratio = min(1.0, expected_avg_latency / max(avg_latency, 0.001))
        performance_score = (latency_compliance + performance_ratio) / 2
        
        status = TestResult.PASS if performance_score >= self.get_target_value() else TestResult.FAIL
        
        return MetricResult(
            metric_type=EvaluationMetricType.SYSTEM_PERFORMANCE,
            value=performance_score,
            target=self.get_target_value(),
            status=status,
            trend="stable",
            details={
                "latency_compliance": latency_compliance,
                "average_latency": avg_latency,
                "expected_average_latency": expected_avg_latency,
                "min_latency": min(latencies),
                "max_latency": max(latencies)
            }
        )
    
    def get_target_value(self) -> float:
        return 0.85  # 85%性能目标

class AutomatedEvaluationFramework:
    """自动化评估框架"""
    
    def __init__(
        self,
        benchmark_file_path: Optional[str] = None,
        evaluation_interval_hours: int = 24,
        history_retention_days: int = 30
    ):
        self.benchmark_file_path = benchmark_file_path
        self.evaluation_interval_hours = evaluation_interval_hours
        self.history_retention_days = history_retention_days
        
        # 基准测试问题
        self.benchmark_questions: List[BenchmarkQuestion] = []
        
        # 评估指标
        self.evaluation_metrics = [
            RouteAccuracyMetric(),
            ResponseQualityMetric(),
            CostEfficiencyMetric(),
            SystemPerformanceMetric()
        ]
        
        # 历史数据
        self.evaluation_history: List[EvaluationReport] = []
        
        # 性能趋势
        self.performance_trends: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        
        logger.info("🔬 自动化评估框架初始化完成")
    
    async def initialize(self):
        """初始化评估框架"""
        try:
            # 加载基准测试问题
            await self._load_benchmark_questions()
            
            # 启动定期评估任务
            asyncio.create_task(self._periodic_evaluation())
            
            logger.info("✅ 自动化评估框架初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 自动化评估框架初始化失败: {e}")
            raise
    
    async def _load_benchmark_questions(self):
        """加载基准测试问题"""
        # 内置基准测试问题
        self.benchmark_questions = [
            # FPGA基础问题
            BenchmarkQuestion(
                question_id="fpga_001",
                category=BenchmarkCategory.FPGA_BASICS,
                query="什么是FPGA？",
                expected_source="local_kb",
                expected_confidence_min=0.85,
                expected_cost_max=0.2,
                expected_latency_max=1.0,
                user_role="beginner",
                complexity_level="simple",
                tags=["concept", "basic"]
            ),
            BenchmarkQuestion(
                question_id="fpga_002",
                category=BenchmarkCategory.FPGA_BASICS,
                query="FPGA和ASIC有什么区别？",
                expected_source="local_kb",
                expected_confidence_min=0.80,
                expected_cost_max=0.3,
                expected_latency_max=1.5,
                user_role="intermediate",
                complexity_level="moderate",
                tags=["comparison", "basic"]
            ),
            
            # 高级设计问题
            BenchmarkQuestion(
                question_id="fpga_003",
                category=BenchmarkCategory.ADVANCED_DESIGN,
                query="如何优化FPGA设计的时序性能？",
                expected_source="ai_training",
                expected_confidence_min=0.75,
                expected_cost_max=1.5,
                expected_latency_max=3.0,
                user_role="expert",
                complexity_level="complex",
                tags=["optimization", "timing"]
            ),
            BenchmarkQuestion(
                question_id="fpga_004",
                category=BenchmarkCategory.ADVANCED_DESIGN,
                query="设计一个高性能的8位计数器",
                expected_source="ai_training",
                expected_confidence_min=0.70,
                expected_cost_max=2.0,
                expected_latency_max=4.0,
                user_role="expert",
                complexity_level="complex",
                tags=["design", "counter"]
            ),
            
            # 故障排查问题
            BenchmarkQuestion(
                question_id="fpga_005",
                category=BenchmarkCategory.TROUBLESHOOTING,
                query="FPGA综合失败，时序不满足怎么办？",
                expected_source="local_kb",
                expected_confidence_min=0.80,
                expected_cost_max=0.5,
                expected_latency_max=2.0,
                user_role="intermediate",
                complexity_level="moderate",
                tags=["troubleshooting", "timing"]
            ),
            
            # 创造性任务
            BenchmarkQuestion(
                question_id="fpga_006",
                category=BenchmarkCategory.CREATIVE_TASKS,
                query="设计一个创新的FPGA图像处理架构",
                expected_source="ai_training",
                expected_confidence_min=0.65,
                expected_cost_max=3.0,
                expected_latency_max=5.0,
                user_role="researcher",
                complexity_level="complex",
                tags=["creative", "image_processing"]
            )
        ]
        
        logger.info(f"📚 加载了 {len(self.benchmark_questions)} 个基准测试问题")
    
    async def run_evaluation(self, router=None) -> EvaluationReport:
        """运行完整评估"""
        start_time = datetime.now()
        report_id = f"eval_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔬 开始运行评估 - {report_id}")
        
        try:
            # 运行基准测试
            test_results = await self._run_benchmark_tests(router)
            
            # 计算评估指标
            metric_results = await self._calculate_metrics(test_results)
            
            # 分析性能趋势
            performance_trends = await self._analyze_performance_trends(metric_results)
            
            # 生成优化建议
            recommendations = await self._generate_recommendations(metric_results, test_results)
            
            # 计算总体评分
            overall_score = self._calculate_overall_score(metric_results)
            
            # 生成评估报告
            report = EvaluationReport(
                report_id=report_id,
                timestamp=start_time,
                overall_score=overall_score,
                test_results=test_results,
                metric_results=metric_results,
                performance_trends=performance_trends,
                recommendations=recommendations,
                next_evaluation_time=start_time + timedelta(hours=self.evaluation_interval_hours),
                summary=self._generate_summary(metric_results, test_results)
            )
            
            # 保存到历史记录
            self.evaluation_history.append(report)
            
            # 更新性能趋势
            await self._update_performance_trends(metric_results)
            
            # 清理过期历史数据
            await self._cleanup_expired_history()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ 评估完成 - {report_id} (耗时: {execution_time:.2f}s)")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 评估运行失败: {e}")
            raise
    
    async def _run_benchmark_tests(self, router) -> List[EvaluationResult]:
        """运行基准测试"""
        test_results = []
        
        for question in self.benchmark_questions:
            try:
                # 模拟路由器调用（在实际实现中会调用真实的路由器）
                if router:
                    # 真实路由器调用
                    decision = await router.route_query(question.query)
                    actual_source = decision.primary_source.value
                    actual_confidence = decision.confidence
                    actual_cost = decision.estimated_cost
                    actual_latency = decision.expected_latency
                else:
                    # 模拟结果
                    actual_source, actual_confidence, actual_cost, actual_latency = \
                        await self._simulate_routing_decision(question)
                
                # 评估结果
                result = self._evaluate_test_result(
                    question, actual_source, actual_confidence, actual_cost, actual_latency
                )
                
                test_results.append(result)
                
                logger.debug(f"🧪 测试 {question.question_id}: {result.result_status.value}")
                
            except Exception as e:
                logger.error(f"❌ 测试 {question.question_id} 失败: {e}")
                # 创建失败的测试结果
                result = EvaluationResult(
                    question_id=question.question_id,
                    query=question.query,
                    actual_source="error",
                    expected_source=question.expected_source,
                    actual_confidence=0.0,
                    expected_confidence_min=question.expected_confidence_min,
                    actual_cost=999.0,
                    expected_cost_max=question.expected_cost_max,
                    actual_latency=999.0,
                    expected_latency_max=question.expected_latency_max,
                    result_status=TestResult.FAIL,
                    score=0.0,
                    reasoning=[f"测试执行失败: {str(e)}"],
                    timestamp=datetime.now()
                )
                test_results.append(result)
        
        return test_results
    
    async def _simulate_routing_decision(self, question: BenchmarkQuestion) -> Tuple[str, float, float, float]:
        """模拟路由决策（用于演示）"""
        import random
        
        # 基于问题复杂度模拟结果
        if question.complexity_level == "simple":
            source_options = ["local_kb", "local_kb", "ai_training"]  # 偏向local_kb
            confidence_base = 0.85
            cost_base = 0.15
            latency_base = 0.8
        elif question.complexity_level == "moderate":
            source_options = ["local_kb", "ai_training", "ai_training"]  # 偏向ai_training
            confidence_base = 0.75
            cost_base = 0.6
            latency_base = 1.5
        else:  # complex
            source_options = ["ai_training", "ai_training", "web_search"]
            confidence_base = 0.70
            cost_base = 1.2
            latency_base = 2.5
        
        # 添加随机变化
        actual_source = random.choice(source_options)
        actual_confidence = confidence_base + random.uniform(-0.1, 0.1)
        actual_cost = cost_base + random.uniform(-0.2, 0.3)
        actual_latency = latency_base + random.uniform(-0.5, 1.0)
        
        return actual_source, actual_confidence, actual_cost, actual_latency
    
    def _evaluate_test_result(
        self,
        question: BenchmarkQuestion,
        actual_source: str,
        actual_confidence: float,
        actual_cost: float,
        actual_latency: float
    ) -> EvaluationResult:
        """评估测试结果"""
        reasoning = []
        score = 0.0
        
        # 评估路由准确性 (40%)
        if actual_source == question.expected_source:
            score += 0.4
            reasoning.append("✅ 路由源正确")
        else:
            reasoning.append(f"❌ 路由源错误: 期望{question.expected_source}, 实际{actual_source}")
        
        # 评估置信度 (25%)
        if actual_confidence >= question.expected_confidence_min:
            confidence_score = min(1.0, actual_confidence / question.expected_confidence_min)
            score += 0.25 * confidence_score
            reasoning.append(f"✅ 置信度满足要求: {actual_confidence:.3f}")
        else:
            reasoning.append(f"❌ 置信度不足: 期望≥{question.expected_confidence_min}, 实际{actual_confidence:.3f}")
        
        # 评估成本 (20%)
        if actual_cost <= question.expected_cost_max:
            cost_score = max(0.0, 1.0 - actual_cost / question.expected_cost_max)
            score += 0.2 * cost_score
            reasoning.append(f"✅ 成本控制良好: ${actual_cost:.3f}")
        else:
            reasoning.append(f"❌ 成本超预算: 期望≤${question.expected_cost_max}, 实际${actual_cost:.3f}")
        
        # 评估延迟 (15%)
        if actual_latency <= question.expected_latency_max:
            latency_score = max(0.0, 1.0 - actual_latency / question.expected_latency_max)
            score += 0.15 * latency_score
            reasoning.append(f"✅ 响应时间良好: {actual_latency:.2f}s")
        else:
            reasoning.append(f"❌ 响应时间过长: 期望≤{question.expected_latency_max}s, 实际{actual_latency:.2f}s")
        
        # 确定测试状态
        if score >= 0.8:
            result_status = TestResult.PASS
        elif score >= 0.6:
            result_status = TestResult.WARNING
        else:
            result_status = TestResult.FAIL
        
        return EvaluationResult(
            question_id=question.question_id,
            query=question.query,
            actual_source=actual_source,
            expected_source=question.expected_source,
            actual_confidence=actual_confidence,
            expected_confidence_min=question.expected_confidence_min,
            actual_cost=actual_cost,
            expected_cost_max=question.expected_cost_max,
            actual_latency=actual_latency,
            expected_latency_max=question.expected_latency_max,
            result_status=result_status,
            score=score,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    async def _calculate_metrics(self, test_results: List[EvaluationResult]) -> List[MetricResult]:
        """计算评估指标"""
        metric_results = []
        
        for metric in self.evaluation_metrics:
            try:
                result = await metric.calculate(test_results)
                metric_results.append(result)
                logger.debug(f"📊 指标 {metric.__class__.__name__}: {result.value:.3f}")
            except Exception as e:
                logger.error(f"❌ 指标计算失败 {metric.__class__.__name__}: {e}")
        
        return metric_results
    
    async def _analyze_performance_trends(self, metric_results: List[MetricResult]) -> Dict[str, List[float]]:
        """分析性能趋势"""
        trends = {}
        
        for metric_result in metric_results:
            metric_name = metric_result.metric_type.value
            
            # 获取历史数据
            historical_values = []
            for report in self.evaluation_history[-10:]:  # 最近10次评估
                for historical_metric in report.metric_results:
                    if historical_metric.metric_type == metric_result.metric_type:
                        historical_values.append(historical_metric.value)
                        break
            
            # 添加当前值
            historical_values.append(metric_result.value)
            trends[metric_name] = historical_values
        
        return trends
    
    async def _generate_recommendations(
        self,
        metric_results: List[MetricResult],
        test_results: List[EvaluationResult]
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 分析各项指标
        for metric_result in metric_results:
            if metric_result.status == TestResult.FAIL:
                if metric_result.metric_type == EvaluationMetricType.ROUTE_ACCURACY:
                    recommendations.append(
                        f"路由准确性偏低 ({metric_result.value:.1%})，"
                        "建议调整路由权重或增加训练数据"
                    )
                elif metric_result.metric_type == EvaluationMetricType.RESPONSE_QUALITY:
                    recommendations.append(
                        f"响应质量需要改善 ({metric_result.value:.1%})，"
                        "建议优化知识库内容或提高置信度阈值"
                    )
                elif metric_result.metric_type == EvaluationMetricType.COST_EFFICIENCY:
                    recommendations.append(
                        f"成本效率有待提升 ({metric_result.value:.1%})，"
                        "建议增加缓存命中率或优化路由策略"
                    )
                elif metric_result.metric_type == EvaluationMetricType.SYSTEM_PERFORMANCE:
                    recommendations.append(
                        f"系统性能需要优化 ({metric_result.value:.1%})，"
                        "建议检查系统资源或优化算法"
                    )
        
        # 分析失败的测试用例
        failed_tests = [r for r in test_results if r.result_status == TestResult.FAIL]
        if len(failed_tests) > len(test_results) * 0.2:  # 超过20%失败率
            recommendations.append(
                f"测试失败率过高 ({len(failed_tests)}/{len(test_results)})，"
                "建议全面检查系统配置"
            )
        
        # 分析特定类别的问题
        category_failures = defaultdict(int)
        for result in failed_tests:
            # 找到对应的问题类别
            question = next((q for q in self.benchmark_questions 
                           if q.question_id == result.question_id), None)
            if question:
                category_failures[question.category.value] += 1
        
        for category, count in category_failures.items():
            if count >= 2:  # 某类别多次失败
                recommendations.append(
                    f"{category} 类别问题频繁失败，"
                    "建议针对性优化相关功能"
                )
        
        if not recommendations:
            recommendations.append("系统运行良好，建议继续保持当前配置")
        
        return recommendations
    
    def _calculate_overall_score(self, metric_results: List[MetricResult]) -> float:
        """计算总体评分"""
        if not metric_results:
            return 0.0
        
        # 各指标权重
        weights = {
            EvaluationMetricType.ROUTE_ACCURACY: 0.30,
            EvaluationMetricType.RESPONSE_QUALITY: 0.25,
            EvaluationMetricType.COST_EFFICIENCY: 0.20,
            EvaluationMetricType.SYSTEM_PERFORMANCE: 0.25
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric_result in metric_results:
            weight = weights.get(metric_result.metric_type, 0.0)
            total_score += metric_result.value * weight
            total_weight += weight
        
        return total_score / max(total_weight, 1.0)
    
    def _generate_summary(
        self,
        metric_results: List[MetricResult],
        test_results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """生成评估摘要"""
        passed_tests = sum(1 for r in test_results if r.result_status == TestResult.PASS)
        warning_tests = sum(1 for r in test_results if r.result_status == TestResult.WARNING)
        failed_tests = sum(1 for r in test_results if r.result_status == TestResult.FAIL)
        
        metric_summary = {}
        for metric_result in metric_results:
            metric_summary[metric_result.metric_type.value] = {
                'value': metric_result.value,
                'target': metric_result.target,
                'status': metric_result.status.value,
                'trend': metric_result.trend
            }
        
        return {
            'test_summary': {
                'total_tests': len(test_results),
                'passed': passed_tests,
                'warning': warning_tests,
                'failed': failed_tests,
                'pass_rate': passed_tests / len(test_results) if test_results else 0
            },
            'metric_summary': metric_summary,
            'evaluation_time': datetime.now().isoformat()
        }
    
    async def _update_performance_trends(self, metric_results: List[MetricResult]):
        """更新性能趋势"""
        current_time = datetime.now()
        
        for metric_result in metric_results:
            metric_name = metric_result.metric_type.value
            self.performance_trends[metric_name].append((current_time, metric_result.value))
            
            # 保持最近30天的数据
            cutoff_time = current_time - timedelta(days=30)
            self.performance_trends[metric_name] = [
                (time, value) for time, value in self.performance_trends[metric_name]
                if time >= cutoff_time
            ]
    
    async def _cleanup_expired_history(self):
        """清理过期历史数据"""
        cutoff_time = datetime.now() - timedelta(days=self.history_retention_days)
        self.evaluation_history = [
            report for report in self.evaluation_history
            if report.timestamp >= cutoff_time
        ]
    
    async def _periodic_evaluation(self):
        """定期评估任务"""
        while True:
            try:
                await asyncio.sleep(self.evaluation_interval_hours * 3600)
                
                logger.info("🕐 开始定期评估")
                report = await self.run_evaluation()
                
                # 检查是否有严重问题
                if report.overall_score < 0.5:
                    logger.warning(f"⚠️ 系统评分过低: {report.overall_score:.3f}")
                
                logger.info(f"✅ 定期评估完成，总体评分: {report.overall_score:.3f}")
                
            except Exception as e:
                logger.error(f"❌ 定期评估失败: {e}")
                # 等待1小时后重试
                await asyncio.sleep(3600)
    
    def get_latest_report(self) -> Optional[EvaluationReport]:
        """获取最新评估报告"""
        return self.evaluation_history[-1] if self.evaluation_history else None
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, List[Tuple[datetime, float]]]:
        """获取性能趋势数据"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        trends = {}
        for metric_name, data_points in self.performance_trends.items():
            trends[metric_name] = [
                (time, value) for time, value in data_points
                if time >= cutoff_time
            ]
        
        return trends
    
    async def export_report(self, report: EvaluationReport, format: str = "json") -> str:
        """导出评估报告"""
        if format == "json":
            # 序列化为JSON
            report_dict = {
                'report_id': report.report_id,
                'timestamp': report.timestamp.isoformat(),
                'overall_score': report.overall_score,
                'test_results': [
                    {
                        'question_id': r.question_id,
                        'query': r.query,
                        'actual_source': r.actual_source,
                        'expected_source': r.expected_source,
                        'score': r.score,
                        'status': r.result_status.value,
                        'reasoning': r.reasoning
                    }
                    for r in report.test_results
                ],
                'metric_results': [
                    {
                        'metric_type': m.metric_type.value,
                        'value': m.value,
                        'target': m.target,
                        'status': m.status.value,
                        'trend': m.trend
                    }
                    for m in report.metric_results
                ],
                'recommendations': report.recommendations,
                'summary': report.summary
            }
            
            return json.dumps(report_dict, indent=2, ensure_ascii=False)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")

# 工厂函数
def create_evaluation_framework(
    evaluation_interval_hours: int = 24,
    history_retention_days: int = 30
) -> AutomatedEvaluationFramework:
    """创建自动化评估框架"""
    return AutomatedEvaluationFramework(
        evaluation_interval_hours=evaluation_interval_hours,
        history_retention_days=history_retention_days
    ) 