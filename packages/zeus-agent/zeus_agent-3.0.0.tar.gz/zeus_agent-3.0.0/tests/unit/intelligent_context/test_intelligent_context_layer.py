"""
智能上下文层测试
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.intelligent_context.intelligent_context_layer import (
    IntelligentContextLayer,
    ProcessingMode,
    IntelligentContextResult
)


@pytest.mark.asyncio
class TestIntelligentContextLayer:
    """测试智能上下文层"""
    
    @pytest_asyncio.fixture
    async def context_engineering(self):
        """创建上下文工程组件"""
        mock = Mock()
        mock.engineer_context = AsyncMock()
        mock.get_metrics = Mock(return_value={'metric1': 1.0})
        mock.get_status = Mock(return_value={'status': 'ready'})
        mock.configure = Mock()
        return mock
    
    @pytest_asyncio.fixture
    async def rag_system(self):
        """创建RAG系统组件"""
        mock = Mock()
        mock.enhance_with_rag = AsyncMock()
        mock.get_metrics = Mock(return_value={'metric2': 2.0})
        mock.get_status = Mock(return_value={'status': 'ready'})
        mock.configure = Mock()
        return mock
    
    @pytest_asyncio.fixture
    async def knowledge_management(self):
        """创建知识管理组件"""
        mock = Mock()
        mock.manage_knowledge = AsyncMock()
        mock.get_metrics = Mock(return_value={'metric3': 3.0})
        mock.get_status = Mock(return_value={'status': 'ready'})
        mock.configure = Mock()
        return mock
    
    @pytest_asyncio.fixture
    async def quality_control(self):
        """创建质量控制组件"""
        mock = Mock()
        mock.assess_quality = AsyncMock()
        mock.get_metrics = Mock(return_value={'metric4': 4.0})
        mock.get_status = Mock(return_value={'status': 'ready'})
        mock.configure = Mock()
        return mock
    
    @pytest_asyncio.fixture
    async def layer(self, context_engineering, rag_system, knowledge_management, quality_control):
        """创建智能上下文层"""
        with patch('layers.intelligent_context.context_engineering.ContextEngineering', return_value=context_engineering), \
             patch('layers.intelligent_context.rag_system.RAGSystem', return_value=rag_system), \
             patch('layers.intelligent_context.knowledge_management.KnowledgeManagement', return_value=knowledge_management), \
             patch('layers.intelligent_context.quality_control.QualityControl', return_value=quality_control):
            layer = IntelligentContextLayer()
            return layer
    
    async def test_initialization(self, layer):
        """测试初始化"""
        assert layer.processing_mode == ProcessingMode.SEQUENTIAL
        assert layer.metrics['total_processed'] == 0
        assert layer.metrics['average_processing_time'] == 0.0
        assert layer.metrics['quality_score'] == 0.0
        assert layer.metrics['efficiency_score'] == 0.0
    
    async def test_sequential_processing(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试顺序处理模式"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content="Test task",
            task_type=TaskType.CONVERSATION
        )
        
        # 设置组件返回值
        engineered_context = UniversalContext({'engineered': True})
        rag_enhanced_context = UniversalContext({'rag_enhanced': True})
        knowledge_managed_context = UniversalContext({'knowledge_managed': True})
        quality_assessment = Mock(
            overall_score=0.8,
            get_quality_level=Mock(return_value=Mock(name='HIGH')),
            metric_scores={'metric1': 0.9},
            failure_risks={'risk1': 0.1},
            recommendations=['recommendation1']
        )
        
        context_engineering.engineer_context.return_value = engineered_context
        rag_system.enhance_with_rag.return_value = rag_enhanced_context
        knowledge_management.manage_knowledge.return_value = knowledge_managed_context
        quality_control.assess_quality.return_value = quality_assessment
        
        # 执行处理
        result = await layer.process_context(context, task)
        
        # 验证结果
        assert isinstance(result, IntelligentContextResult)
        assert result.original_context == context
        assert result.engineered_context == engineered_context
        assert result.rag_enhanced_context == rag_enhanced_context
        assert result.knowledge_managed_context == knowledge_managed_context
        assert result.quality_controlled_context == knowledge_managed_context
        assert result.processing_time > 0
        
        # 验证组件调用
        context_engineering.engineer_context.assert_called_once_with(context, task)
        rag_system.enhance_with_rag.assert_called_once_with(engineered_context, task)
        knowledge_management.manage_knowledge.assert_called_once_with(rag_enhanced_context, task)
        quality_control.assess_quality.assert_called_once_with(knowledge_managed_context, task)
    
    async def test_parallel_processing(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试并行处理模式"""
        # 设置并行处理模式
        layer.processing_mode = ProcessingMode.PARALLEL
        
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content="Test task",
            task_type=TaskType.CONVERSATION
        )
        
        # 设置组件返回值
        engineered_context = UniversalContext({'engineered': True})
        rag_enhanced_context = UniversalContext({'rag_enhanced': True})
        knowledge_managed_context = UniversalContext({'knowledge_managed': True})
        quality_assessment = Mock(
            overall_score=0.8,
            get_quality_level=Mock(return_value=Mock(name='HIGH')),
            metric_scores={'metric1': 0.9},
            failure_risks={'risk1': 0.1},
            recommendations=['recommendation1']
        )
        
        context_engineering.engineer_context.return_value = engineered_context
        rag_system.enhance_with_rag.return_value = rag_enhanced_context
        knowledge_management.manage_knowledge.return_value = knowledge_managed_context
        quality_control.assess_quality.return_value = quality_assessment
        
        # 执行处理
        result = await layer.process_context(context, task)
        
        # 验证结果
        assert isinstance(result, IntelligentContextResult)
        assert result.original_context == context
        assert result.engineered_context == engineered_context
        assert result.rag_enhanced_context == rag_enhanced_context
        assert result.knowledge_managed_context == knowledge_managed_context
        assert result.quality_controlled_context == knowledge_managed_context
        assert result.processing_time > 0
        
        # 验证组件调用
        context_engineering.engineer_context.assert_called_once_with(context, task)
        rag_system.enhance_with_rag.assert_called_once_with(context, task)
        knowledge_management.manage_knowledge.assert_called_once()
        quality_control.assess_quality.assert_called_once()
    
    async def test_adaptive_processing(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试自适应处理模式"""
        # 设置自适应处理模式
        layer.processing_mode = ProcessingMode.ADAPTIVE
        
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content={
                "message": "Complex code generation with multiple requirements" * 10,
                "metadata": {'requirement1': 'value1', 'requirement2': 'value2'}
            },
            task_type=TaskType.CODE_GENERATION  # 高复杂度任务
        )
        
        # 设置组件返回值
        engineered_context = UniversalContext({'engineered': True})
        rag_enhanced_context = UniversalContext({'rag_enhanced': True})
        knowledge_managed_context = UniversalContext({'knowledge_managed': True})
        quality_assessment = Mock(
            overall_score=0.8,
            get_quality_level=Mock(return_value=Mock(name='HIGH')),
            metric_scores={'metric1': 0.9},
            failure_risks={'risk1': 0.1},
            recommendations=['recommendation1']
        )
        
        context_engineering.engineer_context.return_value = engineered_context
        rag_system.enhance_with_rag.return_value = rag_enhanced_context
        knowledge_management.manage_knowledge.return_value = knowledge_managed_context
        quality_control.assess_quality.return_value = quality_assessment
        
        # 执行处理
        result = await layer.process_context(context, task)
        
        # 验证结果
        assert isinstance(result, IntelligentContextResult)
        assert result.original_context == context
        assert result.engineered_context == engineered_context
        assert result.rag_enhanced_context == rag_enhanced_context
        assert result.knowledge_managed_context == knowledge_managed_context
        assert result.quality_controlled_context == knowledge_managed_context
        assert result.processing_time > 0
        
        # 验证组件调用
        context_engineering.engineer_context.assert_called_once()
        rag_system.enhance_with_rag.assert_called_once()
        knowledge_management.manage_knowledge.assert_called_once()
        quality_control.assess_quality.assert_called_once()
    
    async def test_error_handling(self, layer, context_engineering):
        """测试错误处理"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content="Test task",
            task_type=TaskType.CONVERSATION
        )
        
        # 设置组件抛出异常
        error_message = "Test error"
        context_engineering.engineer_context.side_effect = Exception(error_message)
        
        # 执行处理
        result = await layer.process_context(context, task)
        
        # 验证结果
        assert isinstance(result, IntelligentContextResult)
        assert result.original_context == context
        assert result.engineered_context == context  # 降级为原始上下文
        assert result.rag_enhanced_context == context
        assert result.knowledge_managed_context == context
        assert result.quality_controlled_context == context
        assert result.metrics['error'] == error_message
        assert result.processing_time == 0.0
    
    async def test_context_merging(self, layer):
        """测试上下文合并"""
        # 创建测试数据
        context1 = UniversalContext({})
        context1.set('key1', 'value1')
        context1.set('key2', {'nested1': 'value1'})
        context1.set('key3', [1, 2, 3])
        context1.set('context_id', 'ctx1')
        
        context2 = UniversalContext({})
        context2.set('key2', {'nested2': 'value2'})
        context2.set('key3', [4, 5, 6])
        context2.set('key4', 'value4')
        context2.set('context_id', 'ctx2')
        
        # 执行合并
        merged_context = layer._merge_contexts(context1, context2)
        
        # 验证结果
        assert merged_context.get('key1') == 'value1'
        assert merged_context.get('key2') == {'nested1': 'value1', 'nested2': 'value2'}
        assert merged_context.get('key3') == [1, 2, 3, 4, 5, 6]
        assert merged_context.get('key4') == 'value4'
        assert merged_context.get('context_id') == 'ctx1_merged_ctx2'
        assert merged_context.get('merged_from') == ['ctx1', 'ctx2']
        assert merged_context.get('merge_timestamp') is not None
    
    async def test_task_complexity_analysis(self, layer):
        """测试任务复杂度分析"""
        # 创建测试数据
        tasks = [
            UniversalTask(
                content={
                    "message": "Simple conversation",
                    "metadata": {}
                },
                task_type=TaskType.CONVERSATION
            ),
            UniversalTask(
                content={
                    "message": "Complex code generation with multiple requirements" * 10,
                    "metadata": {'requirement1': 'value1', 'requirement2': 'value2'}
                },
                task_type=TaskType.CODE_GENERATION
            ),
            UniversalTask(
                content={
                    "message": "Web search task",
                    "metadata": {'query': 'complex query', 'filters': {'type': 'advanced'}}
                },
                task_type=TaskType.WEB_SEARCH
            )
        ]
        
        # 分析复杂度
        complexities = [layer._analyze_task_complexity(task) for task in tasks]
        
        # 验证结果
        assert complexities[0] < complexities[1]  # 代码生成比对话更复杂
        assert complexities[1] > 0.6  # 复杂任务的复杂度应该较高
        assert 0.0 <= min(complexities) <= 1.0  # 复杂度应该在0到1之间
        assert 0.0 <= max(complexities) <= 1.0
    
    async def test_metrics_collection(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试指标收集"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content={
                "message": "Test task",
                "metadata": {}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 设置组件返回值
        engineered_context = UniversalContext({'engineered': True})
        rag_enhanced_context = UniversalContext({'rag_enhanced': True})
        knowledge_managed_context = UniversalContext({'knowledge_managed': True})
        quality_assessment = Mock(
            overall_score=0.8,
            get_quality_level=Mock(return_value=Mock(name='HIGH')),
            metric_scores={'metric1': 0.9},
            failure_risks={'risk1': 0.1},
            recommendations=['recommendation1']
        )
        
        context_engineering.engineer_context.return_value = engineered_context
        rag_system.enhance_with_rag.return_value = rag_enhanced_context
        knowledge_management.manage_knowledge.return_value = knowledge_managed_context
        quality_control.assess_quality.return_value = quality_assessment
        
        # 执行处理
        result = await layer.process_context(context, task)
        
        # 验证指标
        metrics = result.metrics
        assert 'context_engineering_metrics' in metrics
        assert 'rag_system_metrics' in metrics
        assert 'knowledge_management_metrics' in metrics
        assert 'quality_control_metrics' in metrics
        assert 'overall_metrics' in metrics
        
        assert metrics['context_engineering_metrics']['metric1'] == 1.0
        assert metrics['rag_system_metrics']['metric2'] == 2.0
        assert metrics['knowledge_management_metrics']['metric3'] == 3.0
        assert metrics['quality_control_metrics']['metric4'] == 4.0
        
        assert metrics['overall_metrics']['total_processed'] == 1
        assert metrics['overall_metrics']['average_processing_time'] >= 0.0
        assert 0.0 <= metrics['overall_metrics']['quality_score'] <= 1.0
        assert 0.0 <= metrics['overall_metrics']['efficiency_score'] <= 1.0
    
    async def test_configuration(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试配置更新"""
        # 创建配置
        config = {
            'processing_mode': 'parallel',
            'context_engineering': {'param1': 'value1'},
            'rag_system': {'param2': 'value2'},
            'knowledge_management': {'param3': 'value3'},
            'quality_control': {'param4': 'value4'}
        }
        
        # 更新配置
        layer.configure(config)
        
        # 验证配置更新
        assert layer.processing_mode == ProcessingMode.PARALLEL
        context_engineering.configure.assert_called_once_with({'param1': 'value1'})
        rag_system.configure.assert_called_once_with({'param2': 'value2'})
        knowledge_management.configure.assert_called_once_with({'param3': 'value3'})
        quality_control.configure.assert_called_once_with({'param4': 'value4'})
    
    async def test_status_reporting(self, layer, context_engineering, rag_system, knowledge_management, quality_control):
        """测试状态报告"""
        # 获取状态
        status = layer.get_status()
        
        # 验证状态
        assert status['layer_name'] == 'IntelligentContextLayer'
        assert status['processing_mode'] == ProcessingMode.SEQUENTIAL.value
        assert 'metrics' in status
        assert 'components_status' in status
        
        components_status = status['components_status']
        assert components_status['context_engineering']['status'] == 'ready'
        assert components_status['rag_system']['status'] == 'ready'
        assert components_status['knowledge_management']['status'] == 'ready'
        assert components_status['quality_control']['status'] == 'ready' 