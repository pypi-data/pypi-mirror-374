"""
上下文工程组件测试
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.intelligent_context.context_engineering import (
    ContextEngineering,
    ContextEngineeringMode,
    ContextEngineeringStrategy,
    ContextTemplate,
    ContextRule
)


@pytest.mark.asyncio
class TestContextEngineering:
    """测试上下文工程组件"""
    
    @pytest_asyncio.fixture
    async def context_engineering(self):
        """创建上下文工程组件"""
        return ContextEngineering()
    
    async def test_initialization(self, context_engineering):
        """测试初始化"""
        assert context_engineering.mode == ContextEngineeringMode.BASIC
        assert context_engineering.strategy == ContextEngineeringStrategy.TEMPLATE_BASED
        assert len(context_engineering.templates) > 0
        assert len(context_engineering.rules) > 0
        assert context_engineering.metrics['total_processed'] == 0
        assert context_engineering.metrics['average_processing_time'] == 0.0
        assert context_engineering.metrics['success_rate'] == 1.0
        assert context_engineering.metrics['template_usage'] == {}
        assert context_engineering.metrics['rule_usage'] == {}
    
    async def test_template_loading(self, context_engineering):
        """测试模板加载"""
        # 验证基础模板
        assert 'conversation' in context_engineering.templates
        assert 'code_generation' in context_engineering.templates
        assert 'web_search' in context_engineering.templates
        
        # 验证模板结构
        conversation_template = context_engineering.templates['conversation']
        assert isinstance(conversation_template, ContextTemplate)
        assert conversation_template.name == 'conversation'
        assert 'message' in conversation_template.structure
        assert 'speaker' in conversation_template.structure
        assert 'timestamp' in conversation_template.structure
        assert 'metadata' in conversation_template.structure
        
        # 验证模板规则
        assert 'message_not_empty' in conversation_template.rules
        assert 'speaker_valid' in conversation_template.rules
        assert 'timestamp_valid' in conversation_template.rules
    
    async def test_rule_loading(self, context_engineering):
        """测试规则加载"""
        # 验证基础规则
        assert 'message_not_empty' in context_engineering.rules
        assert 'speaker_valid' in context_engineering.rules
        assert 'timestamp_valid' in context_engineering.rules
        
        # 验证规则结构
        message_rule = context_engineering.rules['message_not_empty']
        assert isinstance(message_rule, ContextRule)
        assert message_rule.name == 'message_not_empty'
        assert message_rule.condition == 'len(message) > 0'
        assert message_rule.action == 'validate_message_length'
        assert message_rule.priority == 1
        assert message_rule.enabled is True
    
    async def test_template_selection(self, context_engineering):
        """测试模板选择"""
        # 创建测试任务
        tasks = [
            UniversalTask(
                content={
                    "message": "Hello",
                    "metadata": {}
                },
                task_type=TaskType.CONVERSATION
            ),
            UniversalTask(
                content={
                    "message": "Generate code",
                    "metadata": {}
                },
                task_type=TaskType.CODE_GENERATION
            ),
            UniversalTask(
                content={
                    "message": "Search web",
                    "metadata": {}
                },
                task_type=TaskType.WEB_SEARCH
            )
        ]
        
        # 验证模板选择
        templates = [context_engineering._select_template(task) for task in tasks]
        
        assert templates[0].name == 'conversation'
        assert templates[1].name == 'code_generation'
        assert templates[2].name == 'web_search'
    
    async def test_template_application(self, context_engineering):
        """测试模板应用"""
        # 创建测试数据
        context = UniversalContext({
            'message': 'Hello',
            'speaker': 'user'
        })
        template = context_engineering.templates['conversation']
        
        # 应用模板
        engineered_context = context_engineering._apply_template(context, template)
        
        # 验证结果
        assert engineered_context.get('message') == 'Hello'
        assert engineered_context.get('speaker') == 'user'
        assert engineered_context.get('timestamp') is None  # 必需字段但未提供
        assert engineered_context.get('template_name') == 'conversation'
        assert engineered_context.get('template_applied_at') is not None
    
    async def test_rule_application(self, context_engineering):
        """测试规则应用"""
        # 创建测试数据
        context = UniversalContext({
            'message': 'Hello',
            'speaker': 'user',
            'timestamp': datetime.now().isoformat()
        })
        rules = ['message_not_empty', 'speaker_valid', 'timestamp_valid']
        
        # 应用规则
        engineered_context = context_engineering._apply_rules(context, rules)
        
        # 验证结果 - 由于规则引擎未实现，上下文应保持不变
        assert engineered_context.get('message') == 'Hello'
        assert engineered_context.get('speaker') == 'user'
        assert engineered_context.get('timestamp') is not None
    
    async def test_context_enhancement(self, context_engineering):
        """测试上下文增强"""
        # 创建测试数据
        context = UniversalContext({
            'message': 'Hello',
            'speaker': 'user'
        })
        task = UniversalTask(
            content={
                "message": "Hello",
                "metadata": {}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 测试基础模式
        context_engineering.mode = ContextEngineeringMode.BASIC
        basic_context = context_engineering._enhance_context(context, task)
        assert basic_context.get('enhancement_mode') == 'basic'
        assert basic_context.get('enhanced_at') is not None
        
        # 测试增强模式
        context_engineering.mode = ContextEngineeringMode.ENHANCED
        enhanced_context = context_engineering._enhance_context(context, task)
        assert enhanced_context.get('enhancement_mode') == 'enhanced'
        assert enhanced_context.get('enhancement_features') == ['metadata', 'validation']
        
        # 测试高级模式
        context_engineering.mode = ContextEngineeringMode.ADVANCED
        advanced_context = context_engineering._enhance_context(context, task)
        assert advanced_context.get('enhancement_mode') == 'advanced'
        assert advanced_context.get('enhancement_features') == ['metadata', 'validation', 'optimization']
    
    async def test_metrics_collection(self, context_engineering):
        """测试指标收集"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content={
                "message": "Hello",
                "metadata": {}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 执行处理
        result = await context_engineering.engineer_context(context, task)
        
        # 验证指标
        metrics = context_engineering.get_metrics()
        assert metrics['total_processed'] == 1
        assert metrics['average_processing_time'] > 0
        assert metrics['success_rate'] == 1.0
        assert 'conversation' in metrics['template_usage']
        assert metrics['template_usage']['conversation'] == 1
    
    async def test_error_handling(self, context_engineering):
        """测试错误处理"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content={
                "message": "Hello",
                "metadata": {}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 模拟错误
        with patch.object(context_engineering, '_select_template', side_effect=Exception('Test error')):
            result = await context_engineering.engineer_context(context, task)
            
            # 验证结果
            assert result == context  # 返回原始上下文
            metrics = context_engineering.get_metrics()
            assert metrics['success_rate'] < 1.0
    
    async def test_configuration(self, context_engineering):
        """测试配置更新"""
        # 创建配置
        config = {
            'mode': 'enhanced',
            'strategy': 'rule_based',
            'templates': {
                'custom_template': ContextTemplate(
                    name='custom_template',
                    description='Custom template',
                    structure={
                        'field1': {'type': 'str', 'required': True}
                    },
                    rules=['rule1']
                )
            },
            'rules': {
                'rule1': ContextRule(
                    name='rule1',
                    description='Custom rule',
                    condition='field1 is not None',
                    action='validate_field1'
                )
            }
        }
        
        # 更新配置
        context_engineering.configure(config)
        
        # 验证配置更新
        assert context_engineering.mode == ContextEngineeringMode.ENHANCED
        assert context_engineering.strategy == ContextEngineeringStrategy.RULE_BASED
        assert 'custom_template' in context_engineering.templates
        assert 'rule1' in context_engineering.rules
    
    async def test_status_reporting(self, context_engineering):
        """测试状态报告"""
        # 获取状态
        status = context_engineering.get_status()
        
        # 验证状态
        assert status['mode'] == ContextEngineeringMode.BASIC.value
        assert status['strategy'] == ContextEngineeringStrategy.TEMPLATE_BASED.value
        assert status['templates'] > 0
        assert status['rules'] > 0
        assert 'metrics' in status 