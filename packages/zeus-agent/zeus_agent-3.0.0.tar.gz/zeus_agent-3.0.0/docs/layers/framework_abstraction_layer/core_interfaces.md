# 框架抽象层核心接口设计

## 1. 概述

本文档详细描述了统一Agent框架中框架抽象层的核心接口设计。框架抽象层的核心接口是整个框架的基础，它定义了智能体、任务、上下文等核心概念的标准接口，使上层应用能够以统一的方式与不同的底层框架交互。

## 2. 设计原则

核心接口的设计遵循以下原则：

- **简洁性**：接口应该简洁明了，只包含必要的方法
- **一致性**：接口之间应该保持一致的设计风格和命名规范
- **完备性**：接口应该覆盖所有必要的功能
- **可扩展性**：接口应该支持未来的扩展
- **类型安全**：接口应该提供类型安全的方法
- **文档完善**：接口应该有完善的文档和注释

## 3. 核心接口定义

### 3.1 AgentInterface

`AgentInterface`是智能体的核心接口，定义了智能体的基本属性和行为。

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict

class AgentInterface(ABC):
    """智能体接口，定义智能体的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取智能体ID
        
        Returns:
            str: 智能体的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """获取智能体名称
        
        Returns:
            str: 智能体的名称
        """
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """获取智能体描述
        
        Returns:
            str: 智能体的描述信息
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取智能体能力列表
        
        Returns:
            List[str]: 智能体支持的能力列表
        """
        pass
        
    @abstractmethod
    def execute_task(self, task: 'TaskInterface', context: Optional['ContextInterface'] = None) -> 'ResultInterface':
        """执行任务
        
        Args:
            task: 要执行的任务
            context: 执行任务的上下文，如果为None，则使用默认上下文
            
        Returns:
            ResultInterface: 任务执行结果
        """
        pass
        
    @abstractmethod
    def has_capability(self, capability: str) -> bool:
        """检查智能体是否具有指定能力
        
        Args:
            capability: 能力名称
            
        Returns:
            bool: 是否具有指定能力
        """
        pass
        
    @abstractmethod
    def get_config(self) -> dict:
        """获取智能体配置
        
        Returns:
            dict: 智能体的配置信息
        """
        pass
        
    @abstractmethod
    def get_memory(self) -> Optional['MemoryInterface']:
        """获取智能体记忆
        
        Returns:
            MemoryInterface: 智能体的记忆，如果没有则返回None
        """
        pass
        
    @abstractmethod
    def set_memory(self, memory: 'MemoryInterface') -> None:
        """设置智能体记忆
        
        Args:
            memory: 智能体的记忆
        """
        pass
```

### 3.2 TaskInterface

`TaskInterface`是任务的核心接口，定义了任务的基本属性和行为。

```python
class TaskInterface(ABC):
    """任务接口，定义任务的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取任务ID
        
        Returns:
            str: 任务的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_type(self) -> str:
        """获取任务类型
        
        Returns:
            str: 任务的类型
        """
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """获取任务描述
        
        Returns:
            str: 任务的描述信息
        """
        pass
        
    @abstractmethod
    def get_content(self) -> Any:
        """获取任务内容
        
        Returns:
            Any: 任务的内容
        """
        pass
        
    @abstractmethod
    def get_config(self) -> dict:
        """获取任务配置
        
        Returns:
            dict: 任务的配置信息
        """
        pass
        
    @abstractmethod
    def get_created_time(self) -> float:
        """获取任务创建时间
        
        Returns:
            float: 任务的创建时间（Unix时间戳）
        """
        pass
        
    @abstractmethod
    def get_deadline(self) -> Optional[float]:
        """获取任务截止时间
        
        Returns:
            float: 任务的截止时间（Unix时间戳），如果没有则返回None
        """
        pass
        
    @abstractmethod
    def get_priority(self) -> int:
        """获取任务优先级
        
        Returns:
            int: 任务的优先级，数值越大优先级越高
        """
        pass
        
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """获取任务依赖
        
        Returns:
            List[str]: 任务依赖的其他任务ID列表
        """
        pass
        
    @abstractmethod
    def is_completed(self) -> bool:
        """检查任务是否已完成
        
        Returns:
            bool: 任务是否已完成
        """
        pass
        
    @abstractmethod
    def set_completed(self, completed: bool = True) -> None:
        """设置任务完成状态
        
        Args:
            completed: 是否完成
        """
        pass
```

### 3.3 ContextInterface

`ContextInterface`是上下文的核心接口，定义了上下文的基本属性和行为。

```python
class ContextInterface(ABC):
    """上下文接口，定义上下文的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取上下文ID
        
        Returns:
            str: 上下文的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_type(self) -> str:
        """获取上下文类型
        
        Returns:
            str: 上下文的类型
        """
        pass
        
    @abstractmethod
    def get_data(self) -> Any:
        """获取上下文数据
        
        Returns:
            Any: 上下文的数据
        """
        pass
        
    @abstractmethod
    def set_data(self, data: Any) -> None:
        """设置上下文数据
        
        Args:
            data: 上下文的数据
        """
        pass
        
    @abstractmethod
    def merge(self, context: 'ContextInterface') -> 'ContextInterface':
        """合并上下文
        
        Args:
            context: 要合并的上下文
            
        Returns:
            ContextInterface: 合并后的上下文
        """
        pass
        
    @abstractmethod
    def get_created_time(self) -> float:
        """获取上下文创建时间
        
        Returns:
            float: 上下文的创建时间（Unix时间戳）
        """
        pass
        
    @abstractmethod
    def get_updated_time(self) -> float:
        """获取上下文更新时间
        
        Returns:
            float: 上下文的最后更新时间（Unix时间戳）
        """
        pass
        
    @abstractmethod
    def get_metadata(self) -> dict:
        """获取上下文元数据
        
        Returns:
            dict: 上下文的元数据
        """
        pass
        
    @abstractmethod
    def set_metadata(self, metadata: dict) -> None:
        """设置上下文元数据
        
        Args:
            metadata: 上下文的元数据
        """
        pass
```

### 3.4 ResultInterface

`ResultInterface`是结果的核心接口，定义了任务执行结果的基本属性和行为。

```python
class ResultInterface(ABC):
    """结果接口，定义任务执行结果的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取结果ID
        
        Returns:
            str: 结果的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_task_id(self) -> str:
        """获取关联的任务ID
        
        Returns:
            str: 关联的任务ID
        """
        pass
        
    @abstractmethod
    def get_agent_id(self) -> str:
        """获取执行任务的智能体ID
        
        Returns:
            str: 执行任务的智能体ID
        """
        pass
        
    @abstractmethod
    def get_content(self) -> Any:
        """获取结果内容
        
        Returns:
            Any: 结果的内容
        """
        pass
        
    @abstractmethod
    def get_created_time(self) -> float:
        """获取结果创建时间
        
        Returns:
            float: 结果的创建时间（Unix时间戳）
        """
        pass
        
    @abstractmethod
    def is_success(self) -> bool:
        """检查任务是否成功
        
        Returns:
            bool: 任务是否成功
        """
        pass
        
    @abstractmethod
    def get_error(self) -> Optional[str]:
        """获取错误信息（如果有）
        
        Returns:
            str: 错误信息，如果没有则返回None
        """
        pass
        
    @abstractmethod
    def get_metrics(self) -> dict:
        """获取结果指标
        
        Returns:
            dict: 结果的指标，如执行时间、资源消耗等
        """
        pass
```

### 3.5 CapabilityInterface

`CapabilityInterface`是能力的核心接口，定义了智能体能力的基本属性和行为。

```python
class CapabilityInterface(ABC):
    """能力接口，定义智能体能力的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取能力ID
        
        Returns:
            str: 能力的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """获取能力名称
        
        Returns:
            str: 能力的名称
        """
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """获取能力描述
        
        Returns:
            str: 能力的描述信息
        """
        pass
        
    @abstractmethod
    def get_parameters(self) -> dict:
        """获取能力参数
        
        Returns:
            dict: 能力的参数定义
        """
        pass
        
    @abstractmethod
    def execute(self, agent: 'AgentInterface', parameters: dict) -> Any:
        """执行能力
        
        Args:
            agent: 执行能力的智能体
            parameters: 执行能力的参数
            
        Returns:
            Any: 执行结果
        """
        pass
        
    @abstractmethod
    def validate_parameters(self, parameters: dict) -> bool:
        """验证参数是否有效
        
        Args:
            parameters: 要验证的参数
            
        Returns:
            bool: 参数是否有效
        """
        pass
        
    @abstractmethod
    def get_required_permissions(self) -> List[str]:
        """获取所需权限
        
        Returns:
            List[str]: 执行能力所需的权限列表
        """
        pass
```

### 3.6 MemoryInterface

`MemoryInterface`是记忆的核心接口，定义了智能体记忆的基本属性和行为。

```python
class MemoryInterface(ABC):
    """记忆接口，定义智能体记忆的基本属性和行为"""
    
    @abstractmethod
    def get_id(self) -> str:
        """获取记忆ID
        
        Returns:
            str: 记忆的唯一标识符
        """
        pass
        
    @abstractmethod
    def get_type(self) -> str:
        """获取记忆类型
        
        Returns:
            str: 记忆的类型
        """
        pass
        
    @abstractmethod
    def add(self, key: str, value: Any, metadata: Optional[dict] = None) -> None:
        """添加记忆
        
        Args:
            key: 记忆的键
            value: 记忆的值
            metadata: 记忆的元数据
        """
        pass
        
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取记忆
        
        Args:
            key: 记忆的键
            
        Returns:
            Any: 记忆的值，如果不存在则返回None
        """
        pass
        
    @abstractmethod
    def remove(self, key: str) -> bool:
        """删除记忆
        
        Args:
            key: 记忆的键
            
        Returns:
            bool: 是否成功删除
        """
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """清空记忆"""
        pass
        
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆
        
        Args:
            query: 搜索查询
            limit: 返回结果的最大数量
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表，每个结果包含键、值和相关性分数
        """
        pass
        
    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """获取所有记忆
        
        Returns:
            Dict[str, Any]: 所有记忆的字典，键为记忆的键，值为记忆的值
        """
        pass
        
    @abstractmethod
    def get_metadata(self, key: str) -> Optional[dict]:
        """获取记忆元数据
        
        Args:
            key: 记忆的键
            
        Returns:
            dict: 记忆的元数据，如果不存在则返回None
        """
        pass
```

## 4. 接口实现基类

为了方便开发者实现上述接口，框架抽象层提供了一系列基类，这些基类实现了接口的通用功能，开发者只需要继承这些基类并实现特定的方法即可。

### 4.1 BaseAgent

```python
import uuid
import time
from typing import List, Optional, Any, Dict

class BaseAgent(AgentInterface):
    """智能体基类，提供AgentInterface的默认实现"""
    
    def __init__(self, config: dict):
        """初始化
        
        Args:
            config: 智能体配置
        """
        self.id = config.get('id', str(uuid.uuid4()))
        self.config = config
        self.name = config.get('name', 'unnamed_agent')
        self.description = config.get('description', '')
        self.capabilities = config.get('capabilities', [])
        self.memory = None
        
    def get_id(self) -> str:
        """获取智能体ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取智能体名称"""
        return self.name
        
    def get_description(self) -> str:
        """获取智能体描述"""
        return self.description
        
    def get_capabilities(self) -> List[str]:
        """获取智能体能力列表"""
        return self.capabilities.copy()
        
    def has_capability(self, capability: str) -> bool:
        """检查智能体是否具有指定能力"""
        return capability in self.capabilities
        
    def get_config(self) -> dict:
        """获取智能体配置"""
        return self.config.copy()
        
    def get_memory(self) -> Optional['MemoryInterface']:
        """获取智能体记忆"""
        return self.memory
        
    def set_memory(self, memory: 'MemoryInterface') -> None:
        """设置智能体记忆"""
        self.memory = memory
        
    def execute_task(self, task: 'TaskInterface', context: Optional['ContextInterface'] = None) -> 'ResultInterface':
        """执行任务
        
        这是一个抽象方法，子类必须实现
        """
        raise NotImplementedError("Subclasses must implement execute_task()")
```

### 4.2 BaseTask

```python
class BaseTask(TaskInterface):
    """任务基类，提供TaskInterface的默认实现"""
    
    def __init__(self, config: dict):
        """初始化
        
        Args:
            config: 任务配置
        """
        self.id = config.get('id', str(uuid.uuid4()))
        self.config = config
        self.type = config.get('type', 'default')
        self.description = config.get('description', '')
        self.content = config.get('content')
        self.created_at = config.get('created_at', time.time())
        self.deadline = config.get('deadline')
        self.priority = config.get('priority', 0)
        self.dependencies = config.get('dependencies', [])
        self.completed = config.get('completed', False)
        
    def get_id(self) -> str:
        """获取任务ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取任务类型"""
        return self.type
        
    def get_description(self) -> str:
        """获取任务描述"""
        return self.description
        
    def get_content(self) -> Any:
        """获取任务内容"""
        return self.content
        
    def get_config(self) -> dict:
        """获取任务配置"""
        return self.config.copy()
        
    def get_created_time(self) -> float:
        """获取任务创建时间"""
        return self.created_at
        
    def get_deadline(self) -> Optional[float]:
        """获取任务截止时间"""
        return self.deadline
        
    def get_priority(self) -> int:
        """获取任务优先级"""
        return self.priority
        
    def get_dependencies(self) -> List[str]:
        """获取任务依赖"""
        return self.dependencies.copy()
        
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        return self.completed
        
    def set_completed(self, completed: bool = True) -> None:
        """设置任务完成状态"""
        self.completed = completed
```

### 4.3 BaseContext

```python
import copy

class BaseContext(ContextInterface):
    """上下文基类，提供ContextInterface的默认实现"""
    
    def __init__(self, config: dict):
        """初始化
        
        Args:
            config: 上下文配置
        """
        self.id = config.get('id', str(uuid.uuid4()))
        self.config = config
        self.type = config.get('type', 'default')
        self.data = config.get('data', {})
        self.created_at = config.get('created_at', time.time())
        self.updated_at = self.created_at
        self.metadata = config.get('metadata', {})
        
    def get_id(self) -> str:
        """获取上下文ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取上下文类型"""
        return self.type
        
    def get_data(self) -> Any:
        """获取上下文数据"""
        return copy.deepcopy(self.data)
        
    def set_data(self, data: Any) -> None:
        """设置上下文数据"""
        self.data = copy.deepcopy(data)
        self.updated_at = time.time()
        
    def get_created_time(self) -> float:
        """获取上下文创建时间"""
        return self.created_at
        
    def get_updated_time(self) -> float:
        """获取上下文更新时间"""
        return self.updated_at
        
    def get_metadata(self) -> dict:
        """获取上下文元数据"""
        return copy.deepcopy(self.metadata)
        
    def set_metadata(self, metadata: dict) -> None:
        """设置上下文元数据"""
        self.metadata = copy.deepcopy(metadata)
        self.updated_at = time.time()
        
    def merge(self, context: 'ContextInterface') -> 'ContextInterface':
        """合并上下文
        
        这是一个抽象方法，子类必须实现
        """
        raise NotImplementedError("Subclasses must implement merge()")
```

### 4.4 BaseResult

```python
class BaseResult(ResultInterface):
    """结果基类，提供ResultInterface的默认实现"""
    
    def __init__(self, task_id: str, agent_id: str, content: Any, success: bool = True, error: str = None, metrics: dict = None):
        """初始化
        
        Args:
            task_id: 关联的任务ID
            agent_id: 执行任务的智能体ID
            content: 结果内容
            success: 是否成功
            error: 错误信息（如果有）
            metrics: 结果指标
        """
        self.id = str(uuid.uuid4())
        self.task_id = task_id
        self.agent_id = agent_id
        self.content = content
        self.success = success
        self.error = error
        self.created_at = time.time()
        self.metrics = metrics or {}
        
    def get_id(self) -> str:
        """获取结果ID"""
        return self.id
        
    def get_task_id(self) -> str:
        """获取关联的任务ID"""
        return self.task_id
        
    def get_agent_id(self) -> str:
        """获取执行任务的智能体ID"""
        return self.agent_id
        
    def get_content(self) -> Any:
        """获取结果内容"""
        return self.content
        
    def get_created_time(self) -> float:
        """获取结果创建时间"""
        return self.created_at
        
    def is_success(self) -> bool:
        """检查任务是否成功"""
        return self.success
        
    def get_error(self) -> Optional[str]:
        """获取错误信息（如果有）"""
        return self.error
        
    def get_metrics(self) -> dict:
        """获取结果指标"""
        return self.metrics.copy()
```

### 4.5 BaseCapability

```python
class BaseCapability(CapabilityInterface):
    """能力基类，提供CapabilityInterface的默认实现"""
    
    def __init__(self, config: dict):
        """初始化
        
        Args:
            config: 能力配置
        """
        self.id = config.get('id', str(uuid.uuid4()))
        self.name = config.get('name', 'unnamed_capability')
        self.description = config.get('description', '')
        self.parameters = config.get('parameters', {})
        self.required_permissions = config.get('required_permissions', [])
        
    def get_id(self) -> str:
        """获取能力ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取能力名称"""
        return self.name
        
    def get_description(self) -> str:
        """获取能力描述"""
        return self.description
        
    def get_parameters(self) -> dict:
        """获取能力参数"""
        return self.parameters.copy()
        
    def get_required_permissions(self) -> List[str]:
        """获取所需权限"""
        return self.required_permissions.copy()
        
    def validate_parameters(self, parameters: dict) -> bool:
        """验证参数是否有效
        
        默认实现：检查所有必需参数是否存在
        
        Args:
            parameters: 要验证的参数
            
        Returns:
            bool: 参数是否有效
        """
        required_params = [k for k, v in self.parameters.items() if v.get('required', False)]
        return all(param in parameters for param in required_params)
        
    def execute(self, agent: 'AgentInterface', parameters: dict) -> Any:
        """执行能力
        
        这是一个抽象方法，子类必须实现
        """
        raise NotImplementedError("Subclasses must implement execute()")
```

### 4.6 BaseMemory

```python
class BaseMemory(MemoryInterface):
    """记忆基类，提供MemoryInterface的默认实现"""
    
    def __init__(self, config: dict):
        """初始化
        
        Args:
            config: 记忆配置
        """
        self.id = config.get('id', str(uuid.uuid4()))
        self.type = config.get('type', 'default')
        self.data = {}
        self.metadata = {}
        
    def get_id(self) -> str:
        """获取记忆ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取记忆类型"""
        return self.type
        
    def add(self, key: str, value: Any, metadata: Optional[dict] = None) -> None:
        """添加记忆"""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        
    def get(self, key: str) -> Optional[Any]:
        """获取记忆"""
        return self.data.get(key)
        
    def remove(self, key: str) -> bool:
        """删除记忆"""
        if key in self.data:
            del self.data[key]
            if key in self.metadata:
                del self.metadata[key]
            return True
        return False
        
    def clear(self) -> None:
        """清空记忆"""
        self.data.clear()
        self.metadata.clear()
        
    def get_all(self) -> Dict[str, Any]:
        """获取所有记忆"""
        return self.data.copy()
        
    def get_metadata(self, key: str) -> Optional[dict]:
        """获取记忆元数据"""
        return self.metadata.get(key)
        
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆
        
        这是一个简单的实现，只是按照键的包含关系进行搜索
        子类可以实现更复杂的搜索逻辑，如向量搜索
        
        Args:
            query: 搜索查询
            limit: 返回结果的最大数量
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表，每个结果包含键、值和相关性分数
        """
        results = []
        for key, value in self.data.items():
            if query.lower() in key.lower():
                results.append({
                    'key': key,
                    'value': value,
                    'score': 1.0  # 简单实现，所有匹配的分数都是1.0
                })
                if len(results) >= limit:
                    break
        return results
```

## 5. 接口扩展

框架抽象层的核心接口设计支持扩展，开发者可以通过以下方式扩展接口：

### 5.1 继承基类

开发者可以继承基类并重写方法，以实现自定义功能。例如：

```python
class CustomAgent(BaseAgent):
    """自定义智能体"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        # 添加自定义属性
        self.custom_attribute = config.get('custom_attribute')
        
    def execute_task(self, task: TaskInterface, context: Optional[ContextInterface] = None) -> ResultInterface:
        """执行任务"""
        # 实现自定义任务执行逻辑
        # ...
        return BaseResult(
            task_id=task.get_id(),
            agent_id=self.get_id(),
            content="Task executed by CustomAgent",
            success=True
        )
        
    # 添加自定义方法
    def custom_method(self) -> str:
        """自定义方法"""
        return f"Custom method of {self.get_name()}"
```

### 5.2 组合接口

开发者可以组合多个接口，以实现更复杂的功能。例如：

```python
class AdvancedAgent(BaseAgent):
    """高级智能体，组合了多个接口"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        # 创建并设置记忆
        memory_config = config.get('memory', {})
        self.set_memory(BaseMemory(memory_config))
        
        # 创建能力列表
        self.capability_instances = {}
        for capability_name in self.capabilities:
            capability_config = config.get('capability_configs', {}).get(capability_name, {})
            capability_config['name'] = capability_name
            self.capability_instances[capability_name] = self._create_capability(capability_config)
            
    def _create_capability(self, config: dict) -> CapabilityInterface:
        """创建能力实例"""
        capability_type = config.get('type', 'default')
        if capability_type == 'default':
            return BaseCapability(config)
        # 可以根据类型创建不同的能力实例
        # ...
        
    def execute_task(self, task: TaskInterface, context: Optional[ContextInterface] = None) -> ResultInterface:
        """执行任务"""
        # 使用记忆和能力执行任务
        # ...
        return BaseResult(
            task_id=task.get_id(),
            agent_id=self.get_id(),
            content="Task executed by AdvancedAgent",
            success=True
        )
        
    def get_capability_instance(self, capability_name: str) -> Optional[CapabilityInterface]:
        """获取能力实例"""
        return self.capability_instances.get(capability_name)
```

### 5.3 接口适配

开发者可以使用适配器模式，将第三方框架的对象适配为框架抽象层的接口。例如：

```python
class ThirdPartyAgentAdapter(AgentInterface):
    """第三方智能体适配器"""
    
    def __init__(self, third_party_agent):
        """初始化
        
        Args:
            third_party_agent: 第三方框架的智能体对象
        """
        self.third_party_agent = third_party_agent
        self.id = str(uuid.uuid4())
        
    def get_id(self) -> str:
        """获取智能体ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取智能体名称"""
        # 适配第三方智能体的名称获取方法
        return getattr(self.third_party_agent, 'name', 'unnamed_agent')
        
    # 实现其他接口方法
    # ...
```

## 6. 接口使用示例

### 6.1 创建和使用智能体

```python
# 创建智能体配置
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

# 创建智能体
from unified_agent.framework import BaseAgent

class AssistantAgent(BaseAgent):
    def execute_task(self, task: TaskInterface, context: Optional[ContextInterface] = None) -> ResultInterface:
        # 实现任务执行逻辑
        task_content = task.get_content()
        # 处理任务内容...
        response = f"Assistant response to: {task_content}"
        
        return BaseResult(
            task_id=task.get_id(),
            agent_id=self.get_id(),
            content=response,
            success=True
        )

agent = AssistantAgent(agent_config)

# 创建任务
from unified_agent.framework import BaseTask

task_config = {
    'type': 'conversation',
    'description': 'Answer user question',
    'content': 'What is the capital of France?'
}

task = BaseTask(task_config)

# 执行任务
result = agent.execute_task(task)

# 输出结果
print(f"Result: {result.get_content()}")
print(f"Success: {result.is_success()}")
```

### 6.2 使用上下文

```python
# 创建上下文
from unified_agent.framework import BaseContext

class ConversationContext(BaseContext):
    def merge(self, context: ContextInterface) -> ContextInterface:
        # 实现上下文合并逻辑
        if context.get_type() != 'conversation':
            raise ValueError(f"Cannot merge context of type {context.get_type()} with conversation context")
            
        merged_data = self.get_data()
        other_data = context.get_data()
        
        # 合并历史记录
        if 'history' in merged_data and 'history' in other_data:
            merged_data['history'] = merged_data['history'] + other_data['history']
        elif 'history' in other_data:
            merged_data['history'] = other_data['history']
            
        # 创建新的上下文
        merged_context = ConversationContext({
            'type': 'conversation',
            'data': merged_data
        })
        
        return merged_context

context_config = {
    'type': 'conversation',
    'data': {
        'history': [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there! How can I help you today?'}
        ]
    }
}

context = ConversationContext(context_config)

# 获取上下文数据
history = context.get_data()['history']
for message in history:
    print(f"{message['role']}: {message['content']}")
    
# 更新上下文
new_history = history + [{'role': 'user', 'content': 'What is the weather today?'}]
context.set_data({'history': new_history})

# 创建另一个上下文
class KnowledgeContext(BaseContext):
    def merge(self, context: ContextInterface) -> ContextInterface:
        # 实现上下文合并逻辑
        merged_data = self.get_data()
        other_data = context.get_data()
        
        # 合并知识
        if 'facts' in merged_data and 'facts' in other_data:
            merged_data['facts'] = merged_data['facts'] + other_data['facts']
        elif 'facts' in other_data:
            merged_data['facts'] = other_data['facts']
            
        # 创建新的上下文
        merged_context = KnowledgeContext({
            'type': 'knowledge',
            'data': merged_data
        })
        
        return merged_context

knowledge_context_config = {
    'type': 'knowledge',
    'data': {
        'facts': [
            {'topic': 'weather', 'content': 'It is sunny today with a high of 75°F.'}
        ]
    }
}

knowledge_context = KnowledgeContext(knowledge_context_config)

# 合并上下文
class MergedContext(BaseContext):
    def merge(self, context: ContextInterface) -> ContextInterface:
        # 实现上下文合并逻辑
        merged_data = self.get_data()
        other_data = context.get_data()
        
        # 合并所有数据
        for key, value in other_data.items():
            if key in merged_data and isinstance(merged_data[key], list) and isinstance(value, list):
                merged_data[key] = merged_data[key] + value
            else:
                merged_data[key] = value
                
        # 创建新的上下文
        merged_context = MergedContext({
            'type': 'merged',
            'data': merged_data
        })
        
        return merged_context

# 创建合并上下文
merged_context = MergedContext({
    'type': 'merged',
    'data': {}
})

# 合并两个上下文
merged_context = merged_context.merge(context)
merged_context = merged_context.merge(knowledge_context)

# 使用合并后的上下文
merged_data = merged_context.get_data()
print("Merged context data:")
print(f"History: {merged_data.get('history')}")
print(f"Facts: {merged_data.get('facts')}")
```

### 6.3 使用能力

```python
# 创建能力
from unified_agent.framework import BaseCapability

class CalculationCapability(BaseCapability):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = 'calculation'
        self.description = 'Perform mathematical calculations'
        self.parameters = {
            'expression': {
                'type': 'string',
                'description': 'The mathematical expression to evaluate',
                'required': True
            }
        }
        
    def execute(self, agent: AgentInterface, parameters: dict) -> Any:
        # 验证参数
        if not self.validate_parameters(parameters):
            raise ValueError("Invalid parameters")
            
        # 执行计算
        expression = parameters['expression']
        try:
            result = eval(expression)
            return result
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression: {e}")

# 创建能力实例
calculation_capability = CalculationCapability({})

# 创建智能体
class CalculatorAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.capabilities = ['calculation']
        self.capability_instances = {
            'calculation': calculation_capability
        }
        
    def execute_task(self, task: TaskInterface, context: Optional[ContextInterface] = None) -> ResultInterface:
        # 获取任务内容
        task_content = task.get_content()
        
        # 执行计算能力
        try:
            result = self.capability_instances['calculation'].execute(
                agent=self,
                parameters={'expression': task_content}
            )
            return BaseResult(
                task_id=task.get_id(),
                agent_id=self.get_id(),
                content=result,
                success=True
            )
        except Exception as e:
            return BaseResult(
                task_id=task.get_id(),
                agent_id=self.get_id(),
                content=None,
                success=False,
                error=str(e)
            )

# 创建计算器智能体
calculator_agent = CalculatorAgent({
    'name': 'calculator',
    'description': 'A calculator agent'
})

# 创建计算任务
calculation_task = BaseTask({
    'type': 'calculation',
    'description': 'Calculate 2 + 2',
    'content': '2 + 2'
})

# 执行任务
result = calculator_agent.execute_task(calculation_task)

# 输出结果
print(f"Result: {result.get_content()}")  # 输出: Result: 4
print(f"Success: {result.is_success()}")  # 输出: Success: True
```

## 7. 总结

框架抽象层的核心接口设计提供了一套统一的抽象接口和数据模型，使上层应用能够以一致的方式与不同的底层Agent框架交互。这些接口包括智能体、任务、上下文、结果、能力和记忆等核心概念，每个接口都有对应的基类实现，开发者可以通过继承这些基类来实现自定义功能。

核心接口的设计遵循了简洁性、一致性、完备性、可扩展性、类型安全和文档完善的原则，为开发者提供了一套完整的智能体开发工具链。通过这些接口，开发者可以专注于业务逻辑的实现，而不必关心底层框架的细节，从而提高开发效率和代码质量。