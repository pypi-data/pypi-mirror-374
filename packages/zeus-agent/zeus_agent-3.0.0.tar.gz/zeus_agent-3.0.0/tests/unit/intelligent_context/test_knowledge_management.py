"""
知识管理组件测试
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.intelligent_context.knowledge_management import (
    KnowledgeManagement,
    KnowledgeItem,
    KnowledgeType,
    KnowledgeSource,
    KnowledgeStatus
)


@pytest.mark.asyncio
class TestKnowledgeManagement:
    """测试知识管理组件"""
    
    @pytest_asyncio.fixture
    async def knowledge_management(self):
        """创建知识管理组件"""
        return KnowledgeManagement()
    
    async def test_initialization(self, knowledge_management):
        """测试初始化"""
        # 验证知识库
        assert len(knowledge_management.knowledge_base) > 0
        
        # 验证索引
        for type_ in KnowledgeType:
            assert type_ in knowledge_management.type_index
        for source in KnowledgeSource:
            assert source in knowledge_management.source_index
        for status in KnowledgeStatus:
            assert status in knowledge_management.status_index
        
        # 验证指标
        assert knowledge_management.metrics['total_items'] > 0
        assert knowledge_management.metrics['total_updates'] == 0
        assert knowledge_management.metrics['total_queries'] == 0
        assert knowledge_management.metrics['average_query_time'] == 0.0
        assert knowledge_management.metrics['cache_hit_rate'] == 1.0
        assert 'type_distribution' in knowledge_management.metrics
        assert 'source_distribution' in knowledge_management.metrics
        assert 'status_distribution' in knowledge_management.metrics
    
    async def test_initial_knowledge(self, knowledge_management):
        """测试初始知识"""
        # 验证系统知识
        task_types = knowledge_management.get_knowledge('system.task_types')
        assert task_types is not None
        assert task_types.type == KnowledgeType.CONCEPT
        assert task_types.source == KnowledgeSource.SYSTEM
        assert task_types.status == KnowledgeStatus.ACTIVE
        assert 'system' in task_types.tags
        assert 'task' in task_types.tags
        assert 'type' in task_types.tags
        
        knowledge_types = knowledge_management.get_knowledge('system.knowledge_types')
        assert knowledge_types is not None
        assert knowledge_types.type == KnowledgeType.CONCEPT
        assert knowledge_types.source == KnowledgeSource.SYSTEM
        assert knowledge_types.status == KnowledgeStatus.ACTIVE
        assert 'system' in knowledge_types.tags
        assert 'knowledge' in knowledge_types.tags
        assert 'type' in knowledge_types.tags
    
    async def test_knowledge_operations(self, knowledge_management):
        """测试知识操作"""
        # 创建测试知识
        test_item = KnowledgeItem(
            id='test.item',
            type=KnowledgeType.FACT,
            content={'fact': 'test fact'},
            source=KnowledgeSource.USER,
            tags={'test', 'fact'}
        )
        
        # 添加知识
        knowledge_management.add_knowledge(test_item)
        assert 'test.item' in knowledge_management.knowledge_base
        assert 'test.item' in knowledge_management.type_index[KnowledgeType.FACT]
        assert 'test.item' in knowledge_management.source_index[KnowledgeSource.USER]
        assert 'test.item' in knowledge_management.status_index[KnowledgeStatus.ACTIVE]
        assert 'test.item' in knowledge_management.tag_index['test']
        assert 'test.item' in knowledge_management.tag_index['fact']
        
        # 更新知识
        knowledge_management.update_knowledge(
            'test.item',
            {'fact': 'updated fact'},
            KnowledgeSource.LEARNED
        )
        updated_item = knowledge_management.get_knowledge('test.item')
        assert updated_item.content['fact'] == 'updated fact'
        assert updated_item.source == KnowledgeSource.LEARNED
        assert updated_item.version == 2
        
        # 移除知识
        knowledge_management.remove_knowledge('test.item')
        assert 'test.item' not in knowledge_management.knowledge_base
        assert 'test.item' not in knowledge_management.type_index[KnowledgeType.FACT]
        assert 'test.item' not in knowledge_management.source_index[KnowledgeSource.LEARNED]
        assert 'test.item' not in knowledge_management.status_index[KnowledgeStatus.ACTIVE]
        assert 'test' not in knowledge_management.tag_index or 'test.item' not in knowledge_management.tag_index['test']
        assert 'fact' not in knowledge_management.tag_index or 'test.item' not in knowledge_management.tag_index['fact']
    
    async def test_knowledge_search(self, knowledge_management):
        """测试知识搜索"""
        # 创建测试知识
        items = [
            KnowledgeItem(
                id='test.fact.1',
                type=KnowledgeType.FACT,
                content={'fact': 'test fact 1'},
                source=KnowledgeSource.USER,
                tags={'test', 'fact', 'group1'}
            ),
            KnowledgeItem(
                id='test.fact.2',
                type=KnowledgeType.FACT,
                content={'fact': 'test fact 2'},
                source=KnowledgeSource.USER,
                tags={'test', 'fact', 'group2'}
            ),
            KnowledgeItem(
                id='test.rule.1',
                type=KnowledgeType.RULE,
                content={'rule': 'test rule'},
                source=KnowledgeSource.SYSTEM,
                tags={'test', 'rule', 'group1'}
            )
        ]
        
        for item in items:
            knowledge_management.add_knowledge(item)
        
        # 按类型搜索
        facts = knowledge_management.search_knowledge(type=KnowledgeType.FACT)
        assert len(facts) == 2
        assert all(item.type == KnowledgeType.FACT for item in facts)
        
        # 按来源搜索
        user_items = knowledge_management.search_knowledge(source=KnowledgeSource.USER)
        assert len(user_items) == 2
        assert all(item.source == KnowledgeSource.USER for item in user_items)
        
        # 按标签搜索
        group1_items = knowledge_management.search_knowledge(tags={'test', 'group1'})
        assert len(group1_items) == 2
        assert all('group1' in item.tags for item in group1_items)
        
        # 组合搜索
        fact_group1_items = knowledge_management.search_knowledge(
            type=KnowledgeType.FACT,
            tags={'group1'}
        )
        assert len(fact_group1_items) == 1
        assert fact_group1_items[0].id == 'test.fact.1'
    
    async def test_knowledge_extraction(self, knowledge_management):
        """测试知识提取"""
        # 创建测试数据
        context = UniversalContext({
            'template_name': 'test_template',
            'rules': ['rule1', 'rule2'],
            'steps': ['step1', 'step2'],
            'patterns': ['pattern1', 'pattern2']
        })
        task = UniversalTask(
            content={
                'message': 'test message',
                'metadata': {'key1': 'value1', 'key2': 'value2'}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 提取知识
        knowledge = knowledge_management._extract_knowledge(context, task)
        
        # 验证结果
        assert len(knowledge) > 0
        
        # 验证任务知识
        task_facts = [item for item in knowledge if item.source == KnowledgeSource.USER]
        assert len(task_facts) == 2  # message和metadata
        assert all(item.type == KnowledgeType.FACT for item in task_facts)
        
        # 验证上下文知识
        context_items = [item for item in knowledge if item.source == KnowledgeSource.SYSTEM]
        assert len(context_items) == 4  # template_name, rules, steps, patterns
        
        concept_items = [item for item in context_items if item.type == KnowledgeType.CONCEPT]
        assert len(concept_items) == 1  # template_name
        
        rule_items = [item for item in context_items if item.type == KnowledgeType.RULE]
        assert len(rule_items) == 1  # rules
        
        procedure_items = [item for item in context_items if item.type == KnowledgeType.PROCEDURE]
        assert len(procedure_items) == 1  # steps
        
        pattern_items = [item for item in context_items if item.type == KnowledgeType.PATTERN]
        assert len(pattern_items) == 1  # patterns
    
    async def test_knowledge_retrieval(self, knowledge_management):
        """测试知识检索"""
        # 创建测试数据
        context = UniversalContext({
            'template_name': 'test_template',
            'key1': 'value1'
        })
        task = UniversalTask(
            content={
                'message': 'test message',
                'metadata': {'key2': 'value2'}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 添加测试知识
        items = [
            KnowledgeItem(
                id='test.task',
                type=KnowledgeType.FACT,
                content={'fact': 'task fact'},
                source=KnowledgeSource.USER,
                tags={'task', 'key2'}
            ),
            KnowledgeItem(
                id='test.template',
                type=KnowledgeType.CONCEPT,
                content={'concept': 'template concept'},
                source=KnowledgeSource.SYSTEM,
                tags={'template_name', 'key1'}
            ),
            KnowledgeItem(
                id='test.inactive',
                type=KnowledgeType.FACT,
                content={'fact': 'inactive fact'},
                source=KnowledgeSource.USER,
                tags={'task', 'key1'},
                status=KnowledgeStatus.INACTIVE
            )
        ]
        
        for item in items:
            knowledge_management.add_knowledge(item)
        
        # 检索知识
        retrieved = knowledge_management._retrieve_knowledge(context, task)
        
        # 验证结果
        assert len(retrieved) == 2  # 只有活跃的知识
        assert all(item.status == KnowledgeStatus.ACTIVE for item in retrieved)
        assert any(item.id == 'test.task' for item in retrieved)
        assert any(item.id == 'test.template' for item in retrieved)
    
    async def test_context_update(self, knowledge_management):
        """测试上下文更新"""
        # 创建测试数据
        context = UniversalContext({
            'original_key': 'original_value'
        })
        knowledge = [
            KnowledgeItem(
                id='test.item.1',
                type=KnowledgeType.FACT,
                content={'fact': 'test fact'},
                source=KnowledgeSource.USER,
                tags={'test', 'fact'}
            ),
            KnowledgeItem(
                id='test.item.2',
                type=KnowledgeType.CONCEPT,
                content={'concept': 'test concept'},
                source=KnowledgeSource.SYSTEM,
                tags={'test', 'concept'}
            )
        ]
        
        # 更新上下文
        managed_context = knowledge_management._update_context(context, knowledge)
        
        # 验证结果
        assert managed_context.get('original_key') == 'original_value'
        assert 'knowledge' in managed_context.data
        assert 'knowledge_updated_at' in managed_context.data
        
        knowledge_data = managed_context.get('knowledge')
        assert len(knowledge_data) == 2
        assert 'test.item.1' in knowledge_data
        assert 'test.item.2' in knowledge_data
        
        item1_data = knowledge_data['test.item.1']
        assert item1_data['type'] == KnowledgeType.FACT.value
        assert item1_data['content'] == {'fact': 'test fact'}
        assert item1_data['source'] == KnowledgeSource.USER.value
        assert set(item1_data['tags']) == {'test', 'fact'}
        assert item1_data['version'] == 1
        
        item2_data = knowledge_data['test.item.2']
        assert item2_data['type'] == KnowledgeType.CONCEPT.value
        assert item2_data['content'] == {'concept': 'test concept'}
        assert item2_data['source'] == KnowledgeSource.SYSTEM.value
        assert set(item2_data['tags']) == {'test', 'concept'}
        assert item2_data['version'] == 1
    
    async def test_metrics_update(self, knowledge_management):
        """测试指标更新"""
        # 记录初始指标
        initial_total = knowledge_management.metrics['total_items']
        initial_updates = knowledge_management.metrics['total_updates']
        initial_queries = knowledge_management.metrics['total_queries']
        
        # 添加知识
        test_item = KnowledgeItem(
            id='test.metrics',
            type=KnowledgeType.FACT,
            content={'fact': 'test fact'},
            source=KnowledgeSource.USER,
            tags={'test', 'metrics'}
        )
        knowledge_management.add_knowledge(test_item)
        
        # 验证添加指标
        assert knowledge_management.metrics['total_items'] == initial_total + 1
        assert 'fact' in knowledge_management.metrics['type_distribution']
        assert 'user' in knowledge_management.metrics['source_distribution']
        assert 'active' in knowledge_management.metrics['status_distribution']
        
        # 更新知识
        knowledge_management.update_knowledge(
            'test.metrics',
            {'fact': 'updated fact'}
        )
        
        # 验证更新指标
        assert knowledge_management.metrics['total_updates'] == initial_updates + 1
        
        # 执行查询
        knowledge_management._update_metrics(2, 1, 0.1)
        
        # 验证查询指标
        assert knowledge_management.metrics['total_queries'] == initial_queries + 1
        assert knowledge_management.metrics['average_query_time'] > 0
    
    async def test_error_handling(self, knowledge_management):
        """测试错误处理"""
        # 创建测试数据
        context = UniversalContext({})
        task = UniversalTask(
            content={
                'message': 'test message',
                'metadata': {}
            },
            task_type=TaskType.CONVERSATION
        )
        
        # 模拟错误
        with patch.object(knowledge_management, '_extract_knowledge', side_effect=Exception('Test error')):
            result = await knowledge_management.manage_knowledge(context, task)
            
            # 验证结果
            assert result == context  # 返回原始上下文
    
    async def test_configuration(self, knowledge_management):
        """测试配置更新"""
        # 创建配置
        config = {
            'key1': 'value1',
            'key2': 'value2'
        }
        
        # 更新配置
        knowledge_management.configure(config)
        
        # 验证配置
        assert knowledge_management.config['key1'] == 'value1'
        assert knowledge_management.config['key2'] == 'value2'
    
    async def test_status_reporting(self, knowledge_management):
        """测试状态报告"""
        # 获取状态
        status = knowledge_management.get_status()
        
        # 验证状态
        assert status['total_items'] == knowledge_management.metrics['total_items']
        assert status['total_updates'] == knowledge_management.metrics['total_updates']
        assert status['total_queries'] == knowledge_management.metrics['total_queries']
        assert 'type_distribution' in status
        assert 'source_distribution' in status
        assert 'status_distribution' in status 