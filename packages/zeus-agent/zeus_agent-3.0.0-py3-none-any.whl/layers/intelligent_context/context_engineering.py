"""
上下文工程组件

负责上下文的预处理、增强和优化
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.task import UniversalTask, TaskType


class ContextEngineeringMode(Enum):
    """上下文工程模式"""
    BASIC = "basic"  # 基础模式
    ENHANCED = "enhanced"  # 增强模式
    ADVANCED = "advanced"  # 高级模式


class ContextEngineeringStrategy(Enum):
    """上下文工程策略"""
    TEMPLATE_BASED = "template_based"  # 基于模板
    RULE_BASED = "rule_based"  # 基于规则
    LEARNING_BASED = "learning_based"  # 基于学习


@dataclass
class ContextTemplate:
    """上下文模板"""
    name: str
    description: str
    structure: Dict[str, Any]
    rules: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContextRule:
    """上下文规则"""
    name: str
    description: str
    condition: str
    action: str
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ContextEngineering:
    """
    上下文工程组件
    
    负责上下文的预处理、增强和优化
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化上下文工程组件"""
        self.config = config or {}
        self.mode = ContextEngineeringMode(
            self.config.get('mode', 'basic')
        )
        self.strategy = ContextEngineeringStrategy(
            self.config.get('strategy', 'template_based')
        )
        
        # 加载模板和规则
        self.templates = self._load_templates()
        self.rules = self._load_rules()
        
        # 性能指标
        self.metrics = {
            'total_processed': 0,
            'average_processing_time': 0.0,
            'success_rate': 1.0,
            'template_usage': {},
            'rule_usage': {}
        }
    
    def _load_templates(self) -> Dict[str, ContextTemplate]:
        """加载上下文模板"""
        # 基础模板
        templates = {
            'conversation': ContextTemplate(
                name='conversation',
                description='对话上下文模板',
                structure={
                    'message': {'type': 'str', 'required': True},
                    'speaker': {'type': 'str', 'required': True},
                    'timestamp': {'type': 'datetime', 'required': True},
                    'metadata': {'type': 'dict', 'required': False}
                },
                rules=[
                    'message_not_empty',
                    'speaker_valid',
                    'timestamp_valid'
                ]
            ),
            'code_generation': ContextTemplate(
                name='code_generation',
                description='代码生成上下文模板',
                structure={
                    'requirements': {'type': 'list', 'required': True},
                    'language': {'type': 'str', 'required': True},
                    'framework': {'type': 'str', 'required': False},
                    'constraints': {'type': 'list', 'required': False},
                    'metadata': {'type': 'dict', 'required': False}
                },
                rules=[
                    'requirements_not_empty',
                    'language_supported',
                    'framework_valid'
                ]
            ),
            'web_search': ContextTemplate(
                name='web_search',
                description='网络搜索上下文模板',
                structure={
                    'query': {'type': 'str', 'required': True},
                    'filters': {'type': 'dict', 'required': False},
                    'sort': {'type': 'str', 'required': False},
                    'metadata': {'type': 'dict', 'required': False}
                },
                rules=[
                    'query_not_empty',
                    'filters_valid',
                    'sort_valid'
                ]
            )
        }
        
        # 添加自定义模板
        custom_templates = self.config.get('templates', {})
        templates.update(custom_templates)
        
        return templates
    
    def _load_rules(self) -> Dict[str, ContextRule]:
        """加载上下文规则"""
        # 基础规则
        rules = {
            'message_not_empty': ContextRule(
                name='message_not_empty',
                description='消息不能为空',
                condition='len(message) > 0',
                action='validate_message_length',
                priority=1
            ),
            'speaker_valid': ContextRule(
                name='speaker_valid',
                description='说话者必须有效',
                condition='speaker in valid_speakers',
                action='validate_speaker',
                priority=1
            ),
            'timestamp_valid': ContextRule(
                name='timestamp_valid',
                description='时间戳必须有效',
                condition='timestamp <= now',
                action='validate_timestamp',
                priority=1
            ),
            'requirements_not_empty': ContextRule(
                name='requirements_not_empty',
                description='需求不能为空',
                condition='len(requirements) > 0',
                action='validate_requirements',
                priority=1
            ),
            'language_supported': ContextRule(
                name='language_supported',
                description='编程语言必须支持',
                condition='language in supported_languages',
                action='validate_language',
                priority=1
            ),
            'framework_valid': ContextRule(
                name='framework_valid',
                description='框架必须有效',
                condition='framework in supported_frameworks',
                action='validate_framework',
                priority=2
            ),
            'query_not_empty': ContextRule(
                name='query_not_empty',
                description='查询不能为空',
                condition='len(query) > 0',
                action='validate_query',
                priority=1
            ),
            'filters_valid': ContextRule(
                name='filters_valid',
                description='过滤器必须有效',
                condition='all(f in valid_filters for f in filters)',
                action='validate_filters',
                priority=2
            ),
            'sort_valid': ContextRule(
                name='sort_valid',
                description='排序必须有效',
                condition='sort in valid_sort_options',
                action='validate_sort',
                priority=2
            )
        }
        
        # 添加自定义规则
        custom_rules = self.config.get('rules', {})
        rules.update(custom_rules)
        
        return rules
    
    async def engineer_context(
        self, 
                             context: UniversalContext, 
        task: UniversalTask
    ) -> UniversalContext:
        """
        工程化上下文
        
        Args:
            context: 输入上下文
            task: 相关任务
            
        Returns:
            工程化后的上下文
        """
        import time
        start_time = time.time()
        
        try:
            # 1. 选择模板
            template = self._select_template(task)
            
            # 2. 应用模板
            engineered_context = self._apply_template(context, template)
            
            # 3. 应用规则
            engineered_context = self._apply_rules(engineered_context, template.rules)
            
            # 4. 增强上下文
            engineered_context = self._enhance_context(engineered_context, task)
            
            # 更新指标
            processing_time = time.time() - start_time
            self._update_metrics(template.name, processing_time, success=True)
            
            return engineered_context
            
        except Exception as e:
            # 错误处理
            processing_time = time.time() - start_time
            self._update_metrics('unknown', processing_time, success=False)
            return context  # 返回原始上下文作为降级方案
    
    def _select_template(self, task: UniversalTask) -> ContextTemplate:
        """选择上下文模板"""
        # 基于任务类型选择模板
        type_to_template = {
            TaskType.CONVERSATION: 'conversation',
            TaskType.CODE_GENERATION: 'code_generation',
            TaskType.WEB_SEARCH: 'web_search'
        }
        
        template_name = type_to_template.get(task.task_type, 'conversation')
        return self.templates[template_name]
    
    def _apply_template(
        self, 
        context: UniversalContext, 
        template: ContextTemplate
    ) -> UniversalContext:
        """应用上下文模板"""
        # 创建新的上下文
        engineered_context = UniversalContext({})
        
        # 复制原始数据
        for key in context.data.keys():
            engineered_context.set(key, context.get(key))
        
        # 应用模板结构
        for key, spec in template.structure.items():
            if spec['required'] and key not in engineered_context.data:
                engineered_context.set(key, None)  # 设置占位符
        
        # 添加模板元数据
        engineered_context.set('template_name', template.name)
        engineered_context.set('template_applied_at', datetime.now().isoformat())
        
        return engineered_context
    
    def _apply_rules(
        self, 
        context: UniversalContext, 
        rule_names: List[str]
    ) -> UniversalContext:
        """应用上下文规则"""
        # 按优先级排序规则
        sorted_rules = sorted(
            [self.rules[name] for name in rule_names],
            key=lambda r: r.priority
        )
        
        # 应用规则
        for rule in sorted_rules:
            if rule.enabled:
                # 这里简化了规则应用逻辑
                # 实际应用中需要实现规则引擎
                pass
        
        return context
    
    def _enhance_context(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> UniversalContext:
        """增强上下文"""
        # 基于模式选择增强策略
        if self.mode == ContextEngineeringMode.BASIC:
            return self._basic_enhancement(context)
        elif self.mode == ContextEngineeringMode.ENHANCED:
            return self._enhanced_enhancement(context)
        else:  # ADVANCED
            return self._advanced_enhancement(context)
    
    def _basic_enhancement(self, context: UniversalContext) -> UniversalContext:
        """基础增强"""
        # 添加基本元数据
        context.set('enhanced_at', datetime.now().isoformat())
        context.set('enhancement_mode', 'basic')
        return context
    
    def _enhanced_enhancement(self, context: UniversalContext) -> UniversalContext:
        """增强模式增强"""
        # 添加增强元数据
        context.set('enhanced_at', datetime.now().isoformat())
        context.set('enhancement_mode', 'enhanced')
        context.set('enhancement_features', ['metadata', 'validation'])
        return context
    
    def _advanced_enhancement(self, context: UniversalContext) -> UniversalContext:
        """高级增强"""
        # 添加高级元数据
        context.set('enhanced_at', datetime.now().isoformat())
        context.set('enhancement_mode', 'advanced')
        context.set('enhancement_features', ['metadata', 'validation', 'optimization'])
        return context
    
    def _update_metrics(self, template_name: str, processing_time: float, success: bool):
        """更新性能指标"""
        self.metrics['total_processed'] += 1
        
        # 更新平均处理时间
        current_avg = self.metrics['average_processing_time']
        total = self.metrics['total_processed']
        self.metrics['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # 更新成功率
        if not success:
            self.metrics['success_rate'] = (
                (self.metrics['success_rate'] * (total - 1) + 0) / total
            )
        
        # 更新模板使用情况
        if template_name not in self.metrics['template_usage']:
            self.metrics['template_usage'][template_name] = 0
        self.metrics['template_usage'][template_name] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.metrics.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """获取组件状态"""
        return {
            'mode': self.mode.value,
            'strategy': self.strategy.value,
            'templates': len(self.templates),
            'rules': len(self.rules),
            'metrics': self.metrics.copy()
        }
    
    def configure(self, config: Dict[str, Any]):
        """配置组件参数"""
        self.config.update(config)
        
        # 更新模式和策略
        if 'mode' in config:
            self.mode = ContextEngineeringMode(config['mode'])
        if 'strategy' in config:
            self.strategy = ContextEngineeringStrategy(config['strategy'])
        
        # 重新加载模板和规则
        if 'templates' in config or 'rules' in config:
            self.templates = self._load_templates()
            self.rules = self._load_rules() 