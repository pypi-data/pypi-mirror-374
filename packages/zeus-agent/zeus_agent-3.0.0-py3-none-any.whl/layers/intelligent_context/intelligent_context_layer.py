"""
智能上下文层主类

整合上下文工程、RAG系统、知识管理、质量控制四大核心组件
提供统一的智能上下文管理接口

新增Agentic RAG处理器支持，实现简单分离架构
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.task import UniversalTask, TaskType
from ..framework.abstractions.result import UniversalResult, ResultStatus

logger = logging.getLogger(__name__)


@dataclass
class IntelligentContextResult:
    """智能上下文处理结果"""
    original_context: UniversalContext
    engineered_context: UniversalContext
    rag_enhanced_context: UniversalContext
    knowledge_managed_context: UniversalContext
    quality_controlled_context: UniversalContext
    metrics: Dict[str, Any]
    processing_time: float


class ProcessingMode(Enum):
    """处理模式"""
    SEQUENTIAL = "sequential"  # 顺序处理
    PARALLEL = "parallel"     # 并行处理
    ADAPTIVE = "adaptive"     # 自适应处理


class RAGProcessingMode(Enum):
    """RAG处理模式"""
    TRADITIONAL = "traditional"  # 传统RAG处理
    AGENTIC = "agentic"         # Agentic RAG处理
    DOCUMENT_WORKFLOW = "document_workflow"  # 文档工作流处理（未来扩展）


class IntelligentContextLayer:
    """
    智能上下文层
    
    统一管理上下文工程、RAG系统、知识管理、质量控制
    提供高质量的智能上下文处理能力
    
    新增特性：
    - 支持Agentic RAG处理器
    - 简单分离架构，用户配置选择
    - 独立的处理链路
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化智能上下文层"""
        self.config = config or {}
        self.processing_mode = ProcessingMode(
            self.config.get('processing_mode', 'sequential')
        )
        
        # 新增：RAG处理模式配置
        self.rag_processing_mode = RAGProcessingMode(
            self.config.get('rag_processing_mode', 'traditional')
        )
        
        # 初始化核心组件
        self._initialize_components()
        
        # 性能指标
        self.metrics = {
            'total_processed': 0,
            'average_processing_time': 0.0,
            'quality_score': 0.0,
            'efficiency_score': 0.0,
            'agentic_usage_ratio': 0.0,  # 新增：Agentic RAG使用比例
            'average_iterations': 0.0     # 新增：平均迭代次数
        }
        
        logger.info(f"智能上下文层初始化完成，RAG处理模式: {self.rag_processing_mode.value}")
    
    def _initialize_components(self):
        """初始化核心组件"""
        # 延迟导入避免循环依赖
        from .context_engineering import ContextEngineering
        from .rag_system import RAGSystem
        from .knowledge_management import KnowledgeManagement
        from .quality_control import QualityControl
        
        # 传统组件
        self.context_engineering = ContextEngineering()
        self.rag_system = RAGSystem()
        self.knowledge_management = KnowledgeManagement()
        self.quality_control = QualityControl()
        
        # 新增：Agentic RAG处理器（按需初始化）
        self.agentic_rag_processor = None
        if self.rag_processing_mode == RAGProcessingMode.AGENTIC:
            self._initialize_agentic_rag_processor()
    
    def _initialize_agentic_rag_processor(self):
        """初始化Agentic RAG处理器"""
        try:
            from .agentic_rag_system import AgenticRAGProcessor
            
            agentic_config = self.config.get('agentic_rag', {})
            self.agentic_rag_processor = AgenticRAGProcessor(agentic_config)
            
            logger.info("Agentic RAG处理器初始化成功")
            
        except ImportError as e:
            logger.error(f"无法导入Agentic RAG处理器: {e}")
            logger.warning("回退到传统RAG处理模式")
            self.rag_processing_mode = RAGProcessingMode.TRADITIONAL
        except Exception as e:
            logger.error(f"Agentic RAG处理器初始化失败: {e}")
            logger.warning("回退到传统RAG处理模式")
            self.rag_processing_mode = RAGProcessingMode.TRADITIONAL
    
    async def process_context(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """
        处理上下文
        
        Args:
            context: 输入上下文
            task: 相关任务
            
        Returns:
            处理结果
        """
        import time
        start_time = time.time()
        
        try:
            # 根据RAG处理模式选择处理流程
            if self.rag_processing_mode == RAGProcessingMode.AGENTIC:
                result = await self._process_with_agentic_rag(context, task)
            else:  # TRADITIONAL
                result = await self._process_with_traditional_rag(context, task)
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            # 更新指标
            self._update_metrics(result)
            
            return result
            
        except Exception as e:
            # 错误处理和降级
            return await self._handle_processing_error(context, task, e)
    
    async def _process_with_traditional_rag(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """使用传统RAG处理流程"""
        
        if self.processing_mode == ProcessingMode.SEQUENTIAL:
            return await self._process_sequential(context, task)
        elif self.processing_mode == ProcessingMode.PARALLEL:
            return await self._process_parallel(context, task)
        else:  # ADAPTIVE
            return await self._process_adaptive(context, task)
    
    async def _process_with_agentic_rag(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """使用Agentic RAG处理流程"""
        
        logger.info("使用Agentic RAG处理流程")
        
        # 1. 上下文工程（保持原有逻辑）
        engineered_context = await self.context_engineering.engineer_context(
            context, task
        )
        
        # 2. Agentic RAG处理（替换传统RAG）
        query = self._extract_query_from_task(task)
        agentic_response = await self.agentic_rag_processor.process(query, engineered_context)
        
        # 3. 将Agentic响应转换为增强上下文
        rag_enhanced_context = await self._convert_agentic_response_to_context(
            engineered_context, agentic_response
        )
        
        # 4. 知识管理（保持原有逻辑）
        knowledge_managed_context = await self.knowledge_management.manage_knowledge(
            rag_enhanced_context, task
        )
        
        # 5. 质量控制（增强版，结合Agentic质量评估）
        quality_assessment = await self._enhanced_quality_control(
            knowledge_managed_context, task, agentic_response
        )
        
        # 将质量评估结果添加到上下文
        knowledge_managed_context.set('quality_assessment', {
            'overall_score': quality_assessment.overall_score,
            'quality_level': quality_assessment.get_quality_level().name,
            'metric_scores': {metric.name: result.score for metric, result in quality_assessment.metric_results.items()},
            'failure_risks': quality_assessment.get_all_issues(),
            'recommendations': quality_assessment.get_all_recommendations(),
            'agentic_metadata': {
                'iterations_used': agentic_response.iterations_used,
                'confidence': agentic_response.confidence,
                'quality_dimensions': agentic_response.quality_dimensions,
                'sources_count': len(agentic_response.sources)
            }
        })
        
        quality_controlled_context = knowledge_managed_context
        
        return IntelligentContextResult(
            original_context=context,
            engineered_context=engineered_context,
            rag_enhanced_context=rag_enhanced_context,
            knowledge_managed_context=knowledge_managed_context,
            quality_controlled_context=quality_controlled_context,
            metrics=self._collect_agentic_metrics(agentic_response),
            processing_time=0.0  # 将在外部设置
        )
    
    def _extract_query_from_task(self, task: UniversalTask) -> str:
        """从任务中提取查询字符串"""
        # 优先使用任务内容
        if hasattr(task, 'content') and task.content:
            return task.content
        
        # 其次使用任务描述
        if hasattr(task, 'description') and task.description:
            return task.description
        
        # 最后使用任务名称
        if hasattr(task, 'name') and task.name:
            return task.name
        
        # 默认查询
        return "请提供相关信息"
    
    async def _convert_agentic_response_to_context(
        self, 
        base_context: UniversalContext, 
        agentic_response
    ) -> UniversalContext:
        """将Agentic响应转换为增强上下文"""
        
        # 复制基础上下文
        enhanced_context = UniversalContext(base_context.get_all() if hasattr(base_context, 'get_all') else {})
        
        # 添加Agentic RAG增强内容
        enhanced_context.set('rag_enhanced_content', agentic_response.content)
        enhanced_context.set('rag_metadata', {
            'processing_mode': 'agentic',
            'confidence': agentic_response.confidence,
            'iterations_used': agentic_response.iterations_used,
            'quality_dimensions': agentic_response.quality_dimensions,
            'sources': agentic_response.sources,
            'metadata': agentic_response.metadata
        })
        
        # 添加处理信息
        enhanced_context.set('rag_processing_info', {
            'processor_type': 'agentic',
            'timestamp': datetime.now().isoformat(),
            'success': agentic_response.confidence >= 0.7,
            'performance_metrics': {
                'confidence': agentic_response.confidence,
                'iterations': agentic_response.iterations_used,
                'sources_used': len(agentic_response.sources)
            }
        })
        
        return enhanced_context
    
    async def _enhanced_quality_control(
        self, 
        context: UniversalContext, 
        task: UniversalTask, 
        agentic_response
    ):
        """增强版质量控制，结合Agentic质量评估"""
        
        # 执行传统质量评估
        traditional_assessment = await self.quality_control.assess_quality(context, task)
        
        # 结合Agentic质量维度
        if agentic_response.quality_dimensions:
            # 将Agentic质量维度融入传统评估
            for dimension, score in agentic_response.quality_dimensions.items():
                # 映射Agentic质量维度到传统指标
                if dimension == 'relevance':
                    traditional_assessment.metric_scores['relevance'] = score
                elif dimension == 'accuracy':
                    traditional_assessment.metric_scores['accuracy'] = score
                elif dimension == 'completeness':
                    traditional_assessment.metric_scores['completeness'] = score
                elif dimension == 'clarity':
                    traditional_assessment.metric_scores['clarity'] = score
            
            # 更新总体分数（加权平均）
            agentic_weight = 0.6  # Agentic评估权重
            traditional_weight = 0.4  # 传统评估权重
            
            combined_score = (
                agentic_response.confidence * agentic_weight + 
                traditional_assessment.overall_score * traditional_weight
            )
            traditional_assessment.overall_score = combined_score
        
        return traditional_assessment
    
    def _collect_agentic_metrics(self, agentic_response) -> Dict[str, Any]:
        """收集Agentic相关指标"""
        base_metrics = self._collect_metrics()
        
        # 添加Agentic特有指标
        base_metrics.update({
            'agentic_confidence': agentic_response.confidence,
            'agentic_iterations': agentic_response.iterations_used,
            'agentic_sources_count': len(agentic_response.sources),
            'agentic_quality_dimensions': agentic_response.quality_dimensions,
            'processing_mode': 'agentic'
        })
        
        return base_metrics
    
    async def _process_sequential(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """顺序处理模式"""
        
        # 1. 上下文工程
        engineered_context = await self.context_engineering.engineer_context(
            context, task
        )
        
        # 2. RAG系统增强
        rag_enhanced_context = await self.rag_system.enhance_with_rag(
            engineered_context, task
        )
        
        # 3. 知识管理
        knowledge_managed_context = await self.knowledge_management.manage_knowledge(
            rag_enhanced_context, task
        )
        
        # 4. 质量控制
        quality_assessment = await self.quality_control.assess_quality(
            knowledge_managed_context, task
        )
        
        # 将质量评估结果添加到上下文
        knowledge_managed_context.set('quality_assessment', {
            'overall_score': quality_assessment.overall_score,
            'quality_level': quality_assessment.get_quality_level().name,
            'metric_scores': {metric.name: result.score for metric, result in quality_assessment.metric_results.items()},
            'failure_risks': quality_assessment.get_all_issues(),
            'recommendations': quality_assessment.get_all_recommendations()
        })
        
        quality_controlled_context = knowledge_managed_context
        
        return IntelligentContextResult(
            original_context=context,
            engineered_context=engineered_context,
            rag_enhanced_context=rag_enhanced_context,
            knowledge_managed_context=knowledge_managed_context,
            quality_controlled_context=quality_controlled_context,
            metrics=self._collect_metrics(),
            processing_time=0.0  # 将在外部设置
        )
    
    async def _process_parallel(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """并行处理模式"""
        
        # 并行执行可以并行的组件
        engineering_task = self.context_engineering.engineer_context(context, task)
        rag_task = self.rag_system.enhance_with_rag(context, task)
        
        engineered_context, rag_enhanced_context = await asyncio.gather(
            engineering_task, rag_task
        )
        
        # 合并结果
        merged_context = self._merge_contexts(
            engineered_context, rag_enhanced_context
        )
        
        # 继续处理
        knowledge_managed_context = await self.knowledge_management.manage_knowledge(
            merged_context, task
        )
        
        quality_assessment = await self.quality_control.assess_quality(
            knowledge_managed_context, task
        )
        
        # 将质量评估结果添加到上下文
        knowledge_managed_context.set('quality_assessment', {
            'overall_score': quality_assessment.overall_score,
            'quality_level': quality_assessment.get_quality_level().name,
            'metric_scores': {metric.name: result.score for metric, result in quality_assessment.metric_results.items()},
            'failure_risks': quality_assessment.get_all_issues(),
            'recommendations': quality_assessment.get_all_recommendations()
        })
        
        quality_controlled_context = knowledge_managed_context
        
        return IntelligentContextResult(
            original_context=context,
            engineered_context=engineered_context,
            rag_enhanced_context=rag_enhanced_context,
            knowledge_managed_context=knowledge_managed_context,
            quality_controlled_context=quality_controlled_context,
            metrics=self._collect_metrics(),
            processing_time=0.0
        )
    
    async def _process_adaptive(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> IntelligentContextResult:
        """自适应处理模式"""
        
        # 根据任务复杂度和上下文大小决定处理策略
        context_size = len(str(context.get_all() if hasattr(context, 'get_all') else {}))
        task_complexity = self._estimate_task_complexity(task)
        
        if context_size > 10000 or task_complexity > 0.7:
            # 复杂任务使用并行处理
            return await self._process_parallel(context, task)
        else:
            # 简单任务使用顺序处理
            return await self._process_sequential(context, task)
    
    def _estimate_task_complexity(self, task: UniversalTask) -> float:
        """估算任务复杂度"""
        complexity = 0.0
        
        # 基于任务类型
        if hasattr(task, 'task_type'):
            if task.task_type in [TaskType.ANALYSIS, TaskType.GENERATION]:
                complexity += 0.3
            elif task.task_type == TaskType.SYNTHESIS:
                complexity += 0.5
        
        # 基于内容长度
        if hasattr(task, 'content') and task.content:
            content_length = len(task.content)
            if content_length > 500:
                complexity += 0.2
            elif content_length > 1000:
                complexity += 0.4
        
        # 基于关键词
        complexity_keywords = ['分析', '设计', '优化', '创建', '生成', '比较']
        if hasattr(task, 'content') and task.content:
            for keyword in complexity_keywords:
                if keyword in task.content:
                    complexity += 0.1
        
        return min(complexity, 1.0)
    
    def _merge_contexts(
        self, 
        context1: UniversalContext, 
        context2: UniversalContext
    ) -> UniversalContext:
        """合并两个上下文"""
        # 获取两个上下文的数据
        data1 = context1.get_all() if hasattr(context1, 'get_all') else {}
        data2 = context2.get_all() if hasattr(context2, 'get_all') else {}
        
        # 合并数据
        merged_data = {**data1, **data2}
        
        # 特殊处理某些字段
        if 'metadata' in data1 and 'metadata' in data2:
            merged_data['metadata'] = {**data1['metadata'], **data2['metadata']}
        
        return UniversalContext(merged_data)
    
    async def _handle_processing_error(
        self, 
        context: UniversalContext, 
        task: UniversalTask, 
        error: Exception
    ) -> IntelligentContextResult:
        """处理错误并提供降级方案"""
        
        logger.error(f"智能上下文处理失败: {error}")
        
        # 尝试降级处理
        try:
            # 如果是Agentic RAG失败，回退到传统RAG
            if self.rag_processing_mode == RAGProcessingMode.AGENTIC:
                logger.warning("Agentic RAG处理失败，回退到传统RAG")
                self.rag_processing_mode = RAGProcessingMode.TRADITIONAL
                return await self._process_with_traditional_rag(context, task)
            
            # 传统RAG失败时的最小化处理
            engineered_context = context  # 直接使用原始上下文
            
            return IntelligentContextResult(
                original_context=context,
                engineered_context=engineered_context,
                rag_enhanced_context=engineered_context,
                knowledge_managed_context=engineered_context,
                quality_controlled_context=engineered_context,
                metrics={'error': str(error), 'fallback_used': True},
                processing_time=0.0
            )
            
        except Exception as fallback_error:
            logger.error(f"降级处理也失败: {fallback_error}")
            
            # 最后的兜底方案
            return IntelligentContextResult(
                original_context=context,
                engineered_context=context,
                rag_enhanced_context=context,
                knowledge_managed_context=context,
                quality_controlled_context=context,
                metrics={'critical_error': str(fallback_error)},
                processing_time=0.0
            )
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """收集当前指标"""
        return {
            'timestamp': datetime.now().isoformat(),
            'processing_mode': self.processing_mode.value,
            'rag_processing_mode': self.rag_processing_mode.value,
            'components_status': {
                'context_engineering': 'active',
                'rag_system': 'active',
                'knowledge_management': 'active',
                'quality_control': 'active',
                'agentic_rag': 'active' if self.agentic_rag_processor else 'inactive'
            }
        }
    
    def _update_metrics(self, result: IntelligentContextResult):
        """更新性能指标"""
        self.metrics['total_processed'] += 1
        
        # 更新平均处理时间
        current_avg = self.metrics['average_processing_time']
        total_processed = self.metrics['total_processed']
        new_avg = (current_avg * (total_processed - 1) + result.processing_time) / total_processed
        self.metrics['average_processing_time'] = new_avg
        
        # 更新质量分数
        if 'quality_assessment' in result.quality_controlled_context.get_all():
            quality_data = result.quality_controlled_context.get('quality_assessment')
            self.metrics['quality_score'] = quality_data.get('overall_score', 0.0)
            
            # 更新Agentic相关指标
            if 'agentic_metadata' in quality_data:
                agentic_data = quality_data['agentic_metadata']
                
                # 更新平均迭代次数
                current_avg_iter = self.metrics['average_iterations']
                new_avg_iter = (current_avg_iter * (total_processed - 1) + agentic_data['iterations_used']) / total_processed
                self.metrics['average_iterations'] = new_avg_iter
        
        # 更新效率分数（基于处理时间和质量）
        if result.processing_time > 0:
            efficiency = self.metrics['quality_score'] / result.processing_time
            self.metrics['efficiency_score'] = efficiency
        
        # 更新Agentic使用比例
        if self.rag_processing_mode == RAGProcessingMode.AGENTIC:
            # 简化计算，假设最近使用了Agentic
            current_ratio = self.metrics['agentic_usage_ratio']
            new_ratio = (current_ratio * (total_processed - 1) + 1.0) / total_processed
            self.metrics['agentic_usage_ratio'] = new_ratio
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            'component': 'IntelligentContextLayer',
            'version': '2.0.0',  # 升级版本号
            'processing_mode': self.processing_mode.value,
            'rag_processing_mode': self.rag_processing_mode.value,
            'metrics': self.metrics,
            'components': {
                'context_engineering': self.context_engineering.get_status() if hasattr(self.context_engineering, 'get_status') else 'active',
                'rag_system': self.rag_system.get_status() if hasattr(self.rag_system, 'get_status') else 'active',
                'knowledge_management': self.knowledge_management.get_status() if hasattr(self.knowledge_management, 'get_status') else 'active',
                'quality_control': self.quality_control.get_status() if hasattr(self.quality_control, 'get_status') else 'active'
            }
        }
        
        # 添加Agentic RAG处理器状态
        if self.agentic_rag_processor:
            status['components']['agentic_rag_processor'] = self.agentic_rag_processor.get_processing_statistics()
        else:
            status['components']['agentic_rag_processor'] = 'not_initialized'
        
        return status
    
    async def switch_rag_mode(self, new_mode: RAGProcessingMode):
        """动态切换RAG处理模式"""
        if new_mode == self.rag_processing_mode:
            logger.info(f"RAG处理模式已经是 {new_mode.value}")
            return
        
        logger.info(f"切换RAG处理模式: {self.rag_processing_mode.value} -> {new_mode.value}")
        
        old_mode = self.rag_processing_mode
        self.rag_processing_mode = new_mode
        
        # 如果切换到Agentic模式但处理器未初始化，则初始化
        if new_mode == RAGProcessingMode.AGENTIC and not self.agentic_rag_processor:
            self._initialize_agentic_rag_processor()
        
        # 更新配置
        self.config['rag_processing_mode'] = new_mode.value
        
        logger.info(f"RAG处理模式切换完成: {new_mode.value}")
    
    def get_supported_rag_modes(self) -> List[str]:
        """获取支持的RAG处理模式"""
        modes = [RAGProcessingMode.TRADITIONAL.value]
        
        # 检查Agentic模式是否可用
        try:
            from .agentic_rag_system import AgenticRAGProcessor
            modes.append(RAGProcessingMode.AGENTIC.value)
        except ImportError:
            pass
        
        return modes 