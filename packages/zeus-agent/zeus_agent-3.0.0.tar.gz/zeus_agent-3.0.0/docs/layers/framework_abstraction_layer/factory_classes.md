# 框架抽象层工厂类设计

## 1. 概述

本文档详细描述了统一Agent框架中框架抽象层的工厂类设计。工厂类是框架抽象层的重要组成部分，它负责创建各种对象实例，如智能体、任务、上下文等，使上层应用能够以统一的方式创建这些对象，而不必关心具体的实现细节。

## 2. 设计原则

工厂类的设计遵循以下原则：

- **单一职责**：每个工厂类只负责创建一种类型的对象
- **依赖注入**：通过配置注入依赖，而不是硬编码
- **可扩展性**：支持添加新的对象类型和实现
- **懒加载**：只在需要时才创建对象
- **缓存机制**：对频繁创建的对象进行缓存
- **线程安全**：保证在多线程环境下的安全性

## 3. 核心工厂类

### 3.1 AgentFactory

`AgentFactory`负责创建智能体实例，它支持通过配置创建不同类型的智能体，并可以指定使用哪个适配器。

```python
from typing import Optional, Dict, Type
from unified_agent.framework.interfaces import AgentInterface

class AgentFactory:
    """智能体工厂，负责创建智能体实例"""
    
    _instance = None
    _agent_types: Dict[str, Type[AgentInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'AgentFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[AgentInterface]) -> None:
        """注册智能体类型
        
        Args:
            agent_type: 智能体类型名称
            agent_class: 智能体类
        """
        cls._agent_types[agent_type] = agent_class
    
    def create(self, config: dict, adapter_name: Optional[str] = None) -> AgentInterface:
        """创建智能体实例
        
        Args:
            config: 智能体配置
            adapter_name: 适配器名称，如果为None，则使用默认适配器
            
        Returns:
            AgentInterface: 智能体实例
            
        Raises:
            ValueError: 如果适配器不存在或创建智能体失败
        """
        # 获取适配器
        from unified_agent.adapter.registry import AdapterRegistry
        
        registry = AdapterRegistry.get_instance()
        
        if adapter_name:
            adapter = registry.get_adapter(adapter_name)
            if not adapter:
                raise ValueError(f"Adapter '{adapter_name}' not found")
        else:
            adapter = registry.get_default_adapter()
            if not adapter:
                raise ValueError("No default adapter found")
        
        # 如果配置中指定了智能体类型，则使用对应的类创建
        agent_type = config.get('type')
        if agent_type and agent_type in self._agent_types:
            agent_class = self._agent_types[agent_type]
            return agent_class(config)
        
        # 否则使用适配器创建智能体
        return adapter.create_agent(config)
    
    def create_from_template(self, template_name: str, overrides: Optional[dict] = None) -> AgentInterface:
        """从模板创建智能体实例
        
        Args:
            template_name: 模板名称
            overrides: 覆盖模板中的配置项
            
        Returns:
            AgentInterface: 智能体实例
            
        Raises:
            ValueError: 如果模板不存在或创建智能体失败
        """
        from unified_agent.framework.templates import AgentTemplates
        
        templates = AgentTemplates.get_instance()
        template = templates.get_template(template_name)
        if not template:
            raise ValueError(f"Agent template '{template_name}' not found")
        
        # 合并配置
        config = template.copy()
        if overrides:
            config.update(overrides)
        
        # 创建智能体
        return self.create(config)
```

### 3.2 TaskFactory

`TaskFactory`负责创建任务实例，它支持通过配置创建不同类型的任务，并可以指定使用哪个适配器。

```python
from typing import Optional, Dict, Type
from unified_agent.framework.interfaces import TaskInterface

class TaskFactory:
    """任务工厂，负责创建任务实例"""
    
    _instance = None
    _task_types: Dict[str, Type[TaskInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'TaskFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_task_type(cls, task_type: str, task_class: Type[TaskInterface]) -> None:
        """注册任务类型
        
        Args:
            task_type: 任务类型名称
            task_class: 任务类
        """
        cls._task_types[task_type] = task_class
    
    def create(self, config: dict, adapter_name: Optional[str] = None) -> TaskInterface:
        """创建任务实例
        
        Args:
            config: 任务配置
            adapter_name: 适配器名称，如果为None，则使用默认适配器
            
        Returns:
            TaskInterface: 任务实例
            
        Raises:
            ValueError: 如果适配器不存在或创建任务失败
        """
        # 获取适配器
        from unified_agent.adapter.registry import AdapterRegistry
        
        # 如果配置中指定了任务类型，则使用对应的类创建
        task_type = config.get('type')
        if task_type and task_type in self._task_types:
            task_class = self._task_types[task_type]
            return task_class(config)
        
        # 否则使用适配器创建任务
        registry = AdapterRegistry.get_instance()
        
        if adapter_name:
            adapter = registry.get_adapter(adapter_name)
            if not adapter:
                raise ValueError(f"Adapter '{adapter_name}' not found")
        else:
            adapter = registry.get_default_adapter()
            if not adapter:
                raise ValueError("No default adapter found")
        
        return adapter.create_task(config)
    
    def create_from_template(self, template_name: str, overrides: Optional[dict] = None) -> TaskInterface:
        """从模板创建任务实例
        
        Args:
            template_name: 模板名称
            overrides: 覆盖模板中的配置项
            
        Returns:
            TaskInterface: 任务实例
            
        Raises:
            ValueError: 如果模板不存在或创建任务失败
        """
        from unified_agent.framework.templates import TaskTemplates
        
        templates = TaskTemplates.get_instance()
        template = templates.get_template(template_name)
        if not template:
            raise ValueError(f"Task template '{template_name}' not found")
        
        # 合并配置
        config = template.copy()
        if overrides:
            config.update(overrides)
        
        # 创建任务
        return self.create(config)
    
    def create_conversation_task(self, content: str, **kwargs) -> TaskInterface:
        """创建对话任务
        
        Args:
            content: 对话内容
            **kwargs: 其他配置项
            
        Returns:
            TaskInterface: 对话任务实例
        """
        config = {
            'type': 'conversation',
            'content': content
        }
        config.update(kwargs)
        return self.create(config)
    
    def create_tool_task(self, tool_name: str, tool_params: dict, **kwargs) -> TaskInterface:
        """创建工具任务
        
        Args:
            tool_name: 工具名称
            tool_params: 工具参数
            **kwargs: 其他配置项
            
        Returns:
            TaskInterface: 工具任务实例
        """
        config = {
            'type': 'tool',
            'tool_name': tool_name,
            'tool_params': tool_params
        }
        config.update(kwargs)
        return self.create(config)
```

### 3.3 ContextFactory

`ContextFactory`负责创建上下文实例，它支持通过配置创建不同类型的上下文。

```python
from typing import Optional, Dict, Type
from unified_agent.framework.interfaces import ContextInterface

class ContextFactory:
    """上下文工厂，负责创建上下文实例"""
    
    _instance = None
    _context_types: Dict[str, Type[ContextInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'ContextFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_context_type(cls, context_type: str, context_class: Type[ContextInterface]) -> None:
        """注册上下文类型
        
        Args:
            context_type: 上下文类型名称
            context_class: 上下文类
        """
        cls._context_types[context_type] = context_class
    
    def create(self, config: dict) -> ContextInterface:
        """创建上下文实例
        
        Args:
            config: 上下文配置
            
        Returns:
            ContextInterface: 上下文实例
            
        Raises:
            ValueError: 如果上下文类型不存在或创建上下文失败
        """
        context_type = config.get('type', 'default')
        
        if context_type not in self._context_types:
            raise ValueError(f"Context type '{context_type}' not registered")
        
        context_class = self._context_types[context_type]
        return context_class(config)
    
    def create_conversation_context(self, history: Optional[list] = None, **kwargs) -> ContextInterface:
        """创建对话上下文
        
        Args:
            history: 对话历史
            **kwargs: 其他配置项
            
        Returns:
            ContextInterface: 对话上下文实例
        """
        config = {
            'type': 'conversation',
            'data': {
                'history': history or []
            }
        }
        config.update(kwargs)
        return self.create(config)
    
    def create_knowledge_context(self, facts: Optional[list] = None, **kwargs) -> ContextInterface:
        """创建知识上下文
        
        Args:
            facts: 知识事实
            **kwargs: 其他配置项
            
        Returns:
            ContextInterface: 知识上下文实例
        """
        config = {
            'type': 'knowledge',
            'data': {
                'facts': facts or []
            }
        }
        config.update(kwargs)
        return self.create(config)
    
    def create_empty_context(self, context_type: str = 'default', **kwargs) -> ContextInterface:
        """创建空上下文
        
        Args:
            context_type: 上下文类型
            **kwargs: 其他配置项
            
        Returns:
            ContextInterface: 空上下文实例
        """
        config = {
            'type': context_type,
            'data': {}
        }
        config.update(kwargs)
        return self.create(config)
```

### 3.4 CapabilityFactory

`CapabilityFactory`负责创建能力实例，它支持通过配置创建不同类型的能力。

```python
from typing import Optional, Dict, Type, List
from unified_agent.framework.interfaces import CapabilityInterface

class CapabilityFactory:
    """能力工厂，负责创建能力实例"""
    
    _instance = None
    _capability_types: Dict[str, Type[CapabilityInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'CapabilityFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_capability_type(cls, capability_type: str, capability_class: Type[CapabilityInterface]) -> None:
        """注册能力类型
        
        Args:
            capability_type: 能力类型名称
            capability_class: 能力类
        """
        cls._capability_types[capability_type] = capability_class
    
    def create(self, config: dict) -> CapabilityInterface:
        """创建能力实例
        
        Args:
            config: 能力配置
            
        Returns:
            CapabilityInterface: 能力实例
            
        Raises:
            ValueError: 如果能力类型不存在或创建能力失败
        """
        capability_type = config.get('type')
        if not capability_type:
            raise ValueError("Capability type not specified in config")
        
        if capability_type not in self._capability_types:
            raise ValueError(f"Capability type '{capability_type}' not registered")
        
        capability_class = self._capability_types[capability_type]
        return capability_class(config)
    
    def create_multiple(self, configs: List[dict]) -> Dict[str, CapabilityInterface]:
        """创建多个能力实例
        
        Args:
            configs: 能力配置列表
            
        Returns:
            Dict[str, CapabilityInterface]: 能力实例字典，键为能力ID，值为能力实例
        """
        capabilities = {}
        for config in configs:
            capability = self.create(config)
            capabilities[capability.get_id()] = capability
        return capabilities
    
    def get_available_capability_types(self) -> List[str]:
        """获取可用的能力类型
        
        Returns:
            List[str]: 可用的能力类型列表
        """
        return list(self._capability_types.keys())
```

### 3.5 MemoryFactory

`MemoryFactory`负责创建记忆实例，它支持通过配置创建不同类型的记忆。

```python
from typing import Optional, Dict, Type
from unified_agent.framework.interfaces import MemoryInterface

class MemoryFactory:
    """记忆工厂，负责创建记忆实例"""
    
    _instance = None
    _memory_types: Dict[str, Type[MemoryInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'MemoryFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_memory_type(cls, memory_type: str, memory_class: Type[MemoryInterface]) -> None:
        """注册记忆类型
        
        Args:
            memory_type: 记忆类型名称
            memory_class: 记忆类
        """
        cls._memory_types[memory_type] = memory_class
    
    def create(self, config: dict) -> MemoryInterface:
        """创建记忆实例
        
        Args:
            config: 记忆配置
            
        Returns:
            MemoryInterface: 记忆实例
            
        Raises:
            ValueError: 如果记忆类型不存在或创建记忆失败
        """
        memory_type = config.get('type', 'default')
        
        if memory_type not in self._memory_types:
            raise ValueError(f"Memory type '{memory_type}' not registered")
        
        memory_class = self._memory_types[memory_type]
        return memory_class(config)
    
    def create_default_memory(self, **kwargs) -> MemoryInterface:
        """创建默认记忆
        
        Args:
            **kwargs: 其他配置项
            
        Returns:
            MemoryInterface: 默认记忆实例
        """
        config = {
            'type': 'default'
        }
        config.update(kwargs)
        return self.create(config)
    
    def create_vector_memory(self, vector_store_config: Optional[dict] = None, **kwargs) -> MemoryInterface:
        """创建向量记忆
        
        Args:
            vector_store_config: 向量存储配置
            **kwargs: 其他配置项
            
        Returns:
            MemoryInterface: 向量记忆实例
        """
        config = {
            'type': 'vector',
            'vector_store': vector_store_config or {}
        }
        config.update(kwargs)
        return self.create(config)
```

### 3.6 ResultFactory

`ResultFactory`负责创建结果实例，它支持通过配置创建不同类型的结果。

```python
from typing import Optional, Dict, Type, Any
from unified_agent.framework.interfaces import ResultInterface

class ResultFactory:
    """结果工厂，负责创建结果实例"""
    
    _instance = None
    _result_types: Dict[str, Type[ResultInterface]] = {}
    
    @classmethod
    def get_instance(cls) -> 'ResultFactory':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_result_type(cls, result_type: str, result_class: Type[ResultInterface]) -> None:
        """注册结果类型
        
        Args:
            result_type: 结果类型名称
            result_class: 结果类
        """
        cls._result_types[result_type] = result_class
    
    def create(self, config: dict) -> ResultInterface:
        """创建结果实例
        
        Args:
            config: 结果配置
            
        Returns:
            ResultInterface: 结果实例
            
        Raises:
            ValueError: 如果结果类型不存在或创建结果失败
        """
        result_type = config.get('type', 'default')
        
        if result_type not in self._result_types:
            raise ValueError(f"Result type '{result_type}' not registered")
        
        result_class = self._result_types[result_type]
        return result_class(config)
    
    def create_success_result(self, task_id: str, agent_id: str, content: Any, metrics: Optional[dict] = None) -> ResultInterface:
        """创建成功结果
        
        Args:
            task_id: 任务ID
            agent_id: 智能体ID
            content: 结果内容
            metrics: 结果指标
            
        Returns:
            ResultInterface: 成功结果实例
        """
        config = {
            'type': 'default',
            'task_id': task_id,
            'agent_id': agent_id,
            'content': content,
            'success': True,
            'error': None,
            'metrics': metrics or {}
        }
        return self.create(config)
    
    def create_error_result(self, task_id: str, agent_id: str, error: str, metrics: Optional[dict] = None) -> ResultInterface:
        """创建错误结果
        
        Args:
            task_id: 任务ID
            agent_id: 智能体ID
            error: 错误信息
            metrics: 结果指标
            
        Returns:
            ResultInterface: 错误结果实例
        """
        config = {
            'type': 'default',
            'task_id': task_id,
            'agent_id': agent_id,
            'content': None,
            'success': False,
            'error': error,
            'metrics': metrics or {}
        }
        return self.create(config)
```

## 4. 工厂类注册机制

为了支持动态扩展，框架抽象层提供了工厂类注册机制，开发者可以注册自定义的类型和实现。

### 4.1 注册智能体类型

```python
from unified_agent.framework.factories import AgentFactory
from unified_agent.framework.interfaces import AgentInterface

# 自定义智能体类
class CustomAgent(AgentInterface):
    # 实现接口方法
    pass

# 注册智能体类型
AgentFactory.register_agent_type('custom', CustomAgent)

# 使用自定义智能体类型创建智能体
agent_factory = AgentFactory.get_instance()
agent = agent_factory.create({'type': 'custom', 'name': 'my_agent'})
```

### 4.2 注册任务类型

```python
from unified_agent.framework.factories import TaskFactory
from unified_agent.framework.interfaces import TaskInterface

# 自定义任务类
class CustomTask(TaskInterface):
    # 实现接口方法
    pass

# 注册任务类型
TaskFactory.register_task_type('custom', CustomTask)

# 使用自定义任务类型创建任务
task_factory = TaskFactory.get_instance()
task = task_factory.create({'type': 'custom', 'content': 'my_task'})
```

### 4.3 注册上下文类型

```python
from unified_agent.framework.factories import ContextFactory
from unified_agent.framework.interfaces import ContextInterface

# 自定义上下文类
class CustomContext(ContextInterface):
    # 实现接口方法
    pass

# 注册上下文类型
ContextFactory.register_context_type('custom', CustomContext)

# 使用自定义上下文类型创建上下文
context_factory = ContextFactory.get_instance()
context = context_factory.create({'type': 'custom', 'data': {'key': 'value'}})
```

### 4.4 注册能力类型

```python
from unified_agent.framework.factories import CapabilityFactory
from unified_agent.framework.interfaces import CapabilityInterface

# 自定义能力类
class CustomCapability(CapabilityInterface):
    # 实现接口方法
    pass

# 注册能力类型
CapabilityFactory.register_capability_type('custom', CustomCapability)

# 使用自定义能力类型创建能力
capability_factory = CapabilityFactory.get_instance()
capability = capability_factory.create({'type': 'custom', 'name': 'my_capability'})
```

### 4.5 注册记忆类型

```python
from unified_agent.framework.factories import MemoryFactory
from unified_agent.framework.interfaces import MemoryInterface

# 自定义记忆类
class CustomMemory(MemoryInterface):
    # 实现接口方法
    pass

# 注册记忆类型
MemoryFactory.register_memory_type('custom', CustomMemory)

# 使用自定义记忆类型创建记忆
memory_factory = MemoryFactory.get_instance()
memory = memory_factory.create({'type': 'custom'})
```

### 4.6 注册结果类型

```python
from unified_agent.framework.factories import ResultFactory
from unified_agent.framework.interfaces import ResultInterface

# 自定义结果类
class CustomResult(ResultInterface):
    # 实现接口方法
    pass

# 注册结果类型
ResultFactory.register_result_type('custom', CustomResult)

# 使用自定义结果类型创建结果
result_factory = ResultFactory.get_instance()
result = result_factory.create({'type': 'custom', 'task_id': 'task_1', 'agent_id': 'agent_1', 'content': 'result'})
```

## 5. 工厂类使用示例

### 5.1 创建智能体

```python
from unified_agent.framework.factories import AgentFactory

# 创建智能体工厂
agent_factory = AgentFactory.get_instance()

# 从配置创建智能体
agent_config = {
    'name': 'assistant',
    'description': 'A helpful assistant',
    'capabilities': ['conversation', 'tool_use'],
    'llm': {
        'type': 'openai',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7
    }
}

# 使用AutoGen适配器创建智能体
agent = agent_factory.create(agent_config, adapter_name='autogen')

# 从模板创建智能体
assistant_agent = agent_factory.create_from_template('assistant', {
    'name': 'my_assistant',
    'llm': {
        'model': 'gpt-4'
    }
})
```

### 5.2 创建任务

```python
from unified_agent.framework.factories import TaskFactory

# 创建任务工厂
task_factory = TaskFactory.get_instance()

# 创建对话任务
conversation_task = task_factory.create_conversation_task(
    content="What is the capital of France?",
    priority=1
)

# 创建工具任务
tool_task = task_factory.create_tool_task(
    tool_name="calculator",
    tool_params={"expression": "2 + 2"},
    description="Calculate 2 + 2"
)

# 从模板创建任务
qa_task = task_factory.create_from_template('qa', {
    'content': 'What is the capital of France?'
})
```

### 5.3 创建上下文

```python
from unified_agent.framework.factories import ContextFactory

# 创建上下文工厂
context_factory = ContextFactory.get_instance()

# 创建对话上下文
conversation_context = context_factory.create_conversation_context(
    history=[
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there! How can I help you today?'}
    ]
)

# 创建知识上下文
knowledge_context = context_factory.create_knowledge_context(
    facts=[
        {'topic': 'weather', 'content': 'It is sunny today with a high of 75°F.'}
    ]
)

# 创建空上下文
empty_context = context_factory.create_empty_context()
```

### 5.4 创建能力

```python
from unified_agent.framework.factories import CapabilityFactory

# 创建能力工厂
capability_factory = CapabilityFactory.get_instance()

# 创建计算能力
calculation_capability = capability_factory.create({
    'type': 'calculation',
    'name': 'calculation',
    'description': 'Perform mathematical calculations',
    'parameters': {
        'expression': {
            'type': 'string',
            'description': 'The mathematical expression to evaluate',
            'required': True
        }
    }
})

# 创建多个能力
capabilities = capability_factory.create_multiple([
    {
        'type': 'calculation',
        'name': 'calculation',
        'description': 'Perform mathematical calculations'
    },
    {
        'type': 'web_search',
        'name': 'web_search',
        'description': 'Search the web for information'
    }
])

# 获取可用的能力类型
available_capability_types = capability_factory.get_available_capability_types()
print(f"Available capability types: {available_capability_types}")
```

### 5.5 创建记忆

```python
from unified_agent.framework.factories import MemoryFactory

# 创建记忆工厂
memory_factory = MemoryFactory.get_instance()

# 创建默认记忆
default_memory = memory_factory.create_default_memory()

# 创建向量记忆
vector_memory = memory_factory.create_vector_memory(
    vector_store_config={
        'type': 'faiss',
        'dimension': 1536,
        'metric': 'cosine'
    }
)

# 创建自定义记忆
custom_memory = memory_factory.create({
    'type': 'custom',
    'storage': {
        'type': 'redis',
        'host': 'localhost',
        'port': 6379
    }
})
```

### 5.6 创建结果

```python
from unified_agent.framework.factories import ResultFactory

# 创建结果工厂
result_factory = ResultFactory.get_instance()

# 创建成功结果
success_result = result_factory.create_success_result(
    task_id='task_1',
    agent_id='agent_1',
    content='The capital of France is Paris.',
    metrics={
        'execution_time': 0.5,
        'tokens_used': 15
    }
)

# 创建错误结果
error_result = result_factory.create_error_result(
    task_id='task_2',
    agent_id='agent_1',
    error='Failed to execute task: API rate limit exceeded',
    metrics={
        'execution_time': 0.2,
        'error_code': 429
    }
)
```

## 6. 工厂类性能优化

为了提高工厂类的性能，框架抽象层采用了以下优化策略：

### 6.1 缓存机制

工厂类可以缓存频繁创建的对象，避免重复创建相同的对象。

```python
class CachedAgentFactory(AgentFactory):
    """带缓存的智能体工厂"""
    
    def __init__(self):
        super().__init__()
        self._cache = {}
        
    def create(self, config: dict, adapter_name: Optional[str] = None) -> AgentInterface:
        """创建智能体实例，如果缓存中存在则直接返回"""
        # 生成缓存键
        cache_key = self._generate_cache_key(config, adapter_name)
        
        # 如果缓存中存在，则直接返回
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 否则创建新的实例并缓存
        agent = super().create(config, adapter_name)
        self._cache[cache_key] = agent
        return agent
        
    def _generate_cache_key(self, config: dict, adapter_name: Optional[str]) -> str:
        """生成缓存键"""
        import hashlib
        import json
        
        # 将配置和适配器名称序列化为JSON字符串
        key_data = {
            'config': config,
            'adapter_name': adapter_name
        }
        key_str = json.dumps(key_data, sort_keys=True)
        
        # 计算哈希值作为缓存键
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        
    def remove_from_cache(self, cache_key: str) -> bool:
        """从缓存中移除指定的对象"""
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False
```

### 6.2 懒加载

工厂类可以采用懒加载策略，只在需要时才加载和初始化组件。

```python
class LazyLoadingAgentFactory(AgentFactory):
    """懒加载的智能体工厂"""
    
    def __init__(self):
        super().__init__()
        self._adapter_registry = None
        self._templates = None
        
    def _get_adapter_registry(self):
        """获取适配器注册表，只在需要时才加载"""
        if self._adapter_registry is None:
            from unified_agent.adapter.registry import AdapterRegistry
            self._adapter_registry = AdapterRegistry.get_instance()
        return self._adapter_registry
        
    def _get_templates(self):
        """获取模板，只在需要时才加载"""
        if self._templates is None:
            from unified_agent.framework.templates import AgentTemplates
            self._templates = AgentTemplates.get_instance()
        return self._templates
        
    def create(self, config: dict, adapter_name: Optional[str] = None) -> AgentInterface:
        """创建智能体实例"""
        # 获取适配器
        registry = self._get_adapter_registry()
        
        if adapter_name:
            adapter = registry.get_adapter(adapter_name)
            if not adapter:
                raise ValueError(f"Adapter '{adapter_name}' not found")
        else:
            adapter = registry.get_default_adapter()
            if not adapter:
                raise ValueError("No default adapter found")
        
        # 如果配置中指定了智能体类型，则使用对应的类创建
        agent_type = config.get('type')
        if agent_type and agent_type in self._agent_types:
            agent_class = self._agent_types[agent_type]
            return agent_class(config)
        
        # 否则使用适配器创建智能体
        return adapter.create_agent(config)
        
    def create_from_template(self, template_name: str, overrides: Optional[dict] = None) -> AgentInterface:
        """从模板创建智能体实例"""
        templates = self._get_templates()
        template = templates.get_template(template_name)
        if not template:
            raise ValueError(f"Agent template '{template_name}' not found")
        
        # 合并配置
        config = template.copy()
        if overrides:
            config.update(overrides)
        
        # 创建智能体
        return self.create(config)
```

### 6.3 批处理

工厂类可以支持批量创建对象，减少创建对象的开销。

```python
class BatchAgentFactory(AgentFactory):
    """批处理的智能体工厂"""
    
    def create_batch(self, configs: List[dict], adapter_name: Optional[str] = None) -> List[AgentInterface]:
        """批量创建智能体实例
        
        Args:
            configs: 智能体配置列表
            adapter_name: 适配器名称，如果为None，则使用默认适配器
            
        Returns:
            List[AgentInterface]: 智能体实例列表
        """
        # 获取适配器
        from unified_agent.adapter.registry import AdapterRegistry
        
        registry = AdapterRegistry.get_instance()
        
        if adapter_name:
            adapter = registry.get_adapter(adapter_name)
            if not adapter:
                raise ValueError(f"Adapter '{adapter_name}' not found")
        else:
            adapter = registry.get_default_adapter()
            if not adapter:
                raise ValueError("No default adapter found")
        
        # 批量创建智能体
        agents = []
        for config in configs:
            # 如果配置中指定了智能体类型，则使用对应的类创建
            agent_type = config.get('type')
            if agent_type and agent_type in self._agent_types:
                agent_class = self._agent_types[agent_type]
                agents.append(agent_class(config))
            else:
                # 否则使用适配器创建智能体
                agents.append(adapter.create_agent(config))
        
        return agents
```

### 6.4 线程安全

工厂类需要保证在多线程环境下的安全性，可以使用线程锁来保护共享资源。

```python
import threading

class ThreadSafeAgentFactory(AgentFactory):
    """线程安全的智能体工厂"""
    
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        
    @classmethod
    def get_instance(cls) -> 'ThreadSafeAgentFactory':
        """获取单例实例"""
        if cls._instance is None:
            with threading.RLock():
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[AgentInterface]) -> None:
        """注册智能体类型"""
        with threading.RLock():
            cls._agent_types[agent_type] = agent_class
    
    def create(self, config: dict, adapter_name: Optional[str] = None) -> AgentInterface:
        """创建智能体实例"""
        with self._lock:
            return super().create(config, adapter_name)
```

## 7. 总结

框架抽象层的工厂类设计提供了一套统一的对象创建机制，使上层应用能够以一致的方式创建各种对象，而不必关心具体的实现细节。工厂类的设计遵循了单一职责、依赖注入、可扩展性、懒加载、缓存机制和线程安全的原则，为开发者提供了一套完整的对象创建工具链。

通过工厂类，开发者可以轻松创建智能体、任务、上下文、能力、记忆和结果等对象，并且可以通过注册机制扩展框架的功能。工厂类还提供了性能优化策略，如缓存机制、懒加载、批处理和线程安全，以提高框架的性能和可靠性。