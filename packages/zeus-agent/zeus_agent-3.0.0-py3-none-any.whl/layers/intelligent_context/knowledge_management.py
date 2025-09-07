"""
知识管理组件

负责知识的存储、检索、更新和维护
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.task import UniversalTask, TaskType


class KnowledgeType(Enum):
    """知识类型"""
    FACT = "fact"  # 事实
    RULE = "rule"  # 规则
    CONCEPT = "concept"  # 概念
    PROCEDURE = "procedure"  # 过程
    PATTERN = "pattern"  # 模式


class KnowledgeSource(Enum):
    """知识来源"""
    SYSTEM = "system"  # 系统内置
    USER = "user"  # 用户提供
    LEARNED = "learned"  # 学习获得
    INFERRED = "inferred"  # 推理得出


class KnowledgeStatus(Enum):
    """知识状态"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    DEPRECATED = "deprecated"  # 已弃用
    PENDING = "pending"  # 待验证


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    type: KnowledgeType
    content: Dict[str, Any]
    source: KnowledgeSource
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def update(self, content: Dict[str, Any], source: Optional[KnowledgeSource] = None):
        """更新知识项"""
        self.content = content
        if source:
            self.source = source
        self.updated_at = datetime.now()
        self.version += 1
    
    def add_tags(self, *tags: str):
        """添加标签"""
        self.tags.update(tags)
        self.updated_at = datetime.now()
    
    def remove_tags(self, *tags: str):
        """移除标签"""
        self.tags.difference_update(tags)
        self.updated_at = datetime.now()
    
    def set_status(self, status: KnowledgeStatus):
        """设置状态"""
        self.status = status
        self.updated_at = datetime.now()
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        self.metadata[key] = value
        self.updated_at = datetime.now()


class KnowledgeManagement:
    """
    知识管理组件
    
    负责知识的存储、检索、更新和维护
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化知识管理组件"""
        self.config = config or {}
        
        # 知识库
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        
        # 索引
        self.type_index: Dict[KnowledgeType, Set[str]] = {
            type_: set() for type_ in KnowledgeType
        }
        self.source_index: Dict[KnowledgeSource, Set[str]] = {
            source: set() for source in KnowledgeSource
        }
        self.status_index: Dict[KnowledgeStatus, Set[str]] = {
            status: set() for status in KnowledgeStatus
        }
        self.tag_index: Dict[str, Set[str]] = {}
        
        # 性能指标
        self.metrics = {
            'total_items': 0,
            'total_updates': 0,
            'total_queries': 0,
            'average_query_time': 0.0,
            'cache_hit_rate': 1.0,
            'type_distribution': {},
            'source_distribution': {},
            'status_distribution': {}
        }
        
        # 加载初始知识
        self._load_initial_knowledge()
    
    def _load_initial_knowledge(self):
        """加载初始知识"""
        # 加载系统知识
        system_knowledge = {
            'task_types': KnowledgeItem(
                id='system.task_types',
                type=KnowledgeType.CONCEPT,
                content={
                    'types': [type_.value for type_ in TaskType],
                    'descriptions': {
                        TaskType.CONVERSATION.value: '对话任务',
                        TaskType.CODE_GENERATION.value: '代码生成任务',
                        TaskType.CODE_EXECUTION.value: '代码执行任务',
                        TaskType.WEB_SEARCH.value: '网络搜索任务',
                        TaskType.FILE_OPERATION.value: '文件操作任务',
                        TaskType.CUSTOM.value: '自定义任务'
                    }
                },
                source=KnowledgeSource.SYSTEM,
                tags={'system', 'task', 'type'}
            ),
            'knowledge_types': KnowledgeItem(
                id='system.knowledge_types',
                type=KnowledgeType.CONCEPT,
                content={
                    'types': [type_.value for type_ in KnowledgeType],
                    'descriptions': {
                        KnowledgeType.FACT.value: '事实知识',
                        KnowledgeType.RULE.value: '规则知识',
                        KnowledgeType.CONCEPT.value: '概念知识',
                        KnowledgeType.PROCEDURE.value: '过程知识',
                        KnowledgeType.PATTERN.value: '模式知识'
                    }
                },
                source=KnowledgeSource.SYSTEM,
                tags={'system', 'knowledge', 'type'}
            )
        }
        
        # 添加系统知识
        for item in system_knowledge.values():
            self.add_knowledge(item)
    
    async def manage_knowledge(
        self, 
                             context: UniversalContext, 
        task: UniversalTask
    ) -> UniversalContext:
        """
        管理知识
        
        Args:
            context: 输入上下文
            task: 相关任务
            
        Returns:
            处理后的上下文
        """
        import time
        start_time = time.time()
        
        try:
            # 1. 提取知识
            knowledge = self._extract_knowledge(context, task)
            
            # 2. 存储知识
            for item in knowledge:
                self.add_knowledge(item)
            
            # 3. 检索相关知识
            relevant_knowledge = self._retrieve_knowledge(context, task)
            
            # 4. 更新上下文
            managed_context = self._update_context(context, relevant_knowledge)
            
            # 更新指标
            processing_time = time.time() - start_time
            self._update_metrics(len(knowledge), len(relevant_knowledge), processing_time)
            
            return managed_context
            
        except Exception as e:
            # 错误处理
            return context
    
    def add_knowledge(self, item: KnowledgeItem):
        """添加知识项"""
        # 更新知识库
        self.knowledge_base[item.id] = item
        
        # 更新索引
        self.type_index[item.type].add(item.id)
        self.source_index[item.source].add(item.id)
        self.status_index[item.status].add(item.id)
        
        for tag in item.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(item.id)
        
        # 更新指标
        self.metrics['total_items'] += 1
        self._update_distribution_metrics()
    
    def update_knowledge(
        self, 
        id: str, 
        content: Dict[str, Any], 
        source: Optional[KnowledgeSource] = None
    ):
        """更新知识项"""
        if id not in self.knowledge_base:
            return
        
        item = self.knowledge_base[id]
        
        # 更新索引
        if source and source != item.source:
            self.source_index[item.source].remove(id)
            self.source_index[source].add(id)
        
        # 更新知识项
        item.update(content, source)
        
        # 更新指标
        self.metrics['total_updates'] += 1
    
    def remove_knowledge(self, id: str):
        """移除知识项"""
        if id not in self.knowledge_base:
            return
        
        item = self.knowledge_base[id]
        
        # 更新索引
        self.type_index[item.type].remove(id)
        self.source_index[item.source].remove(id)
        self.status_index[item.status].remove(id)
        
        for tag in item.tags:
            if tag in self.tag_index:
                self.tag_index[tag].remove(id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        # 移除知识项
        del self.knowledge_base[id]
        
        # 更新指标
        self.metrics['total_items'] -= 1
        self._update_distribution_metrics()
    
    def get_knowledge(self, id: str) -> Optional[KnowledgeItem]:
        """获取知识项"""
        return self.knowledge_base.get(id)
    
    def search_knowledge(
        self,
        type: Optional[KnowledgeType] = None,
        source: Optional[KnowledgeSource] = None,
        status: Optional[KnowledgeStatus] = None,
        tags: Optional[Set[str]] = None
    ) -> List[KnowledgeItem]:
        """搜索知识"""
        # 获取候选集
        candidates = set(self.knowledge_base.keys())
        
        # 按类型过滤
        if type:
            candidates &= self.type_index[type]
        
        # 按来源过滤
        if source:
            candidates &= self.source_index[source]
        
        # 按状态过滤
        if status:
            candidates &= self.status_index[status]
        
        # 按标签过滤
        if tags:
            for tag in tags:
                if tag in self.tag_index:
                    candidates &= self.tag_index[tag]
                else:
                    return []
        
        # 返回结果
        return [self.knowledge_base[id] for id in candidates]
    
    def _extract_knowledge(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> List[KnowledgeItem]:
        """提取知识"""
        knowledge = []
        
        # 从任务中提取知识
        task_content = task.content
        if isinstance(task_content, dict):
            message = task_content.get('message', '')
            metadata = task_content.get('metadata', {})
            
            # 提取事实知识
            if message:
                knowledge.append(KnowledgeItem(
                    id=f'task.fact.{hash(message)}',
                    type=KnowledgeType.FACT,
                    content={'message': message},
                    source=KnowledgeSource.USER,
                    tags={'task', 'fact'}
                ))
            
            # 提取元数据知识
            if metadata:
                knowledge.append(KnowledgeItem(
                    id=f'task.metadata.{hash(str(metadata))}',
                    type=KnowledgeType.FACT,
                    content={'metadata': metadata},
                    source=KnowledgeSource.USER,
                    tags={'task', 'metadata'}
                ))
        
        # 从上下文中提取知识
        context_data = context.data
        for key, value in context_data.items():
            # 提取概念知识
            if key in ['template_name', 'enhancement_mode']:
                knowledge.append(KnowledgeItem(
                    id=f'context.concept.{key}.{hash(str(value))}',
                    type=KnowledgeType.CONCEPT,
                    content={key: value},
                    source=KnowledgeSource.SYSTEM,
                    tags={'context', 'concept', key}
                ))
            
            # 提取规则知识
            elif key in ['rules', 'constraints']:
                knowledge.append(KnowledgeItem(
                    id=f'context.rule.{key}.{hash(str(value))}',
                    type=KnowledgeType.RULE,
                    content={key: value},
                    source=KnowledgeSource.SYSTEM,
                    tags={'context', 'rule', key}
                ))
            
            # 提取过程知识
            elif key in ['steps', 'workflow']:
                knowledge.append(KnowledgeItem(
                    id=f'context.procedure.{key}.{hash(str(value))}',
                    type=KnowledgeType.PROCEDURE,
                    content={key: value},
                    source=KnowledgeSource.SYSTEM,
                    tags={'context', 'procedure', key}
                ))
            
            # 提取模式知识
            elif key in ['patterns', 'templates']:
                knowledge.append(KnowledgeItem(
                    id=f'context.pattern.{key}.{hash(str(value))}',
                    type=KnowledgeType.PATTERN,
                    content={key: value},
                    source=KnowledgeSource.SYSTEM,
                    tags={'context', 'pattern', key}
                ))
        
        return knowledge
    
    def _retrieve_knowledge(
        self, 
        context: UniversalContext, 
        task: UniversalTask
    ) -> List[KnowledgeItem]:
        """检索知识"""
        # 获取任务相关标签
        tags = {'task'}
        if isinstance(task.content, dict):
            metadata = task.content.get('metadata', {})
            tags.update(metadata.keys())
        
        # 获取上下文相关标签
        context_data = context.data
        for key in context_data.keys():
            tags.add(key)
        
        # 搜索相关知识
        all_knowledge = self.search_knowledge(
            status=KnowledgeStatus.ACTIVE,
            tags=None  # 暂时不使用标签过滤
        )
        
        # 排除系统知识
        return [
            item for item in all_knowledge
            if not (
                item.source == KnowledgeSource.SYSTEM and
                item.id.startswith('system.')
            )
        ]
    
    def _update_context(
        self, 
        context: UniversalContext, 
        knowledge: List[KnowledgeItem]
    ) -> UniversalContext:
        """更新上下文"""
        # 创建新的上下文
        managed_context = UniversalContext({})
        
        # 复制原始数据
        for key in context.data.keys():
            managed_context.set(key, context.get(key))
        
        # 添加知识
        knowledge_data = {}
        for item in knowledge:
            knowledge_data[item.id] = {
                'type': item.type.value,
                'content': item.content,
                'source': item.source.value,
                'tags': list(item.tags),
                'version': item.version,
                'updated_at': item.updated_at.isoformat()
            }
        
        managed_context.set('knowledge', knowledge_data)
        managed_context.set('knowledge_updated_at', datetime.now().isoformat())
        
        return managed_context
    
    def _update_metrics(self, extracted: int, retrieved: int, processing_time: float):
        """更新指标"""
        # 更新查询次数和时间
        self.metrics['total_queries'] += 1
        current_avg = self.metrics['average_query_time']
        total = self.metrics['total_queries']
        self.metrics['average_query_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def _update_distribution_metrics(self):
        """更新分布指标"""
        total = max(self.metrics['total_items'], 1)
        
        # 更新类型分布
        self.metrics['type_distribution'] = {
            type_.value.lower(): len(items) / total
            for type_, items in self.type_index.items()
        }
        
        # 更新来源分布
        self.metrics['source_distribution'] = {
            source.value.lower(): len(items) / total
            for source, items in self.source_index.items()
        }
        
        # 更新状态分布
        self.metrics['status_distribution'] = {
            status.value.lower(): len(items) / total
            for status, items in self.status_index.items()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.metrics.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """获取组件状态"""
        return {
            'total_items': self.metrics['total_items'],
            'total_updates': self.metrics['total_updates'],
            'total_queries': self.metrics['total_queries'],
            'type_distribution': self.metrics['type_distribution'],
            'source_distribution': self.metrics['source_distribution'],
            'status_distribution': self.metrics['status_distribution']
        }
    
    def configure(self, config: Dict[str, Any]):
        """配置组件参数"""
        self.config.update(config) 