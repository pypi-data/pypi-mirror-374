# CrewAI 适配器设计文档

## 1. 概述

CrewAI 是一个专注于多智能体协作的框架，允许开发者创建由多个专家智能体组成的团队来协同解决复杂任务。本文档详细描述了 CrewAI 适配器的设计和实现，包括如何将 CrewAI 的特性和功能映射到统一 Agent 框架的抽象接口。

## 2. CrewAI 框架特性

### 2.1 核心特性

- **智能体团队**：支持创建由多个专家智能体组成的团队
- **任务分配**：支持将复杂任务分解并分配给不同的智能体
- **协作流程**：支持智能体之间的协作和信息共享
- **角色定义**：支持为智能体定义专业角色和背景
- **工作流管理**：支持定义和执行复杂的工作流程

### 2.2 主要组件

- **Agent**：具有特定角色和能力的智能体
- **Crew**：由多个智能体组成的团队
- **Task**：分配给智能体的任务
- **Process**：定义智能体之间协作的流程
- **Tool**：智能体可以使用的工具

## 3. 适配器设计

### 3.1 类图

```
+-------------------+      +-------------------+
|   BaseAdapter     |<---- |  CrewAIAdapter    |
+-------------------+      +-------------------+
| + initialize()    |      | + initialize()    |
| + shutdown()      |      | + shutdown()      |
| + get_capabilities()|    | + get_capabilities()|
| + create_agent()  |      | + create_agent()  |
| + create_task()   |      | + create_task()   |
| + execute_task()  |      | + execute_task()  |
+-------------------+      +-------------------+
                                     |
                                     |
                          +----------v-----------+
                          | CrewAIAgentWrapper   |
                          +----------------------+
                          | + get_id()           |
                          | + get_name()         |
                          | + get_description()  |
                          | + get_capabilities() |
                          | + execute_task()     |
                          +----------------------+
```

### 3.2 适配器实现

```python
class CrewAIAdapter(BaseAdapter):
    """CrewAI 框架适配器"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.translator = ConceptTranslator('unified', 'crewai')
        self.optimizer = PerformanceOptimizer(self)
        self.crewai = None
        
    def initialize(self) -> bool:
        """初始化 CrewAI 适配器"""
        try:
            import crewai
            self.crewai = crewai
            self.initialized = True
            logger.info("CrewAI adapter initialized successfully")
            return True
        except ImportError:
            logger.error("Failed to initialize CrewAI adapter: CrewAI package not installed")
            return False
            
    def shutdown(self) -> bool:
        """关闭 CrewAI 适配器"""
        # CrewAI 没有特定的关闭操作
        self.initialized = False
        return True
        
    def get_capabilities(self) -> List[str]:
        """返回 CrewAI 适配器支持的能力"""
        return [
            'multi_agent_collaboration',
            'role_based_agents',
            'task_delegation',
            'sequential_workflows',
            'parallel_workflows',
            'tool_use',
            'human_feedback'
        ]
        
    def create_agent(self, agent_config: dict) -> 'AgentInterface':
        """创建 CrewAI Agent"""
        if not self.initialized:
            raise RuntimeError("CrewAI adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 转换配置
            crewai_config = self.translator.translate_agent_config(agent_config)
            
            # 优化配置
            optimized_config = self.optimizer.optimize_agent_creation(crewai_config)
            
            # 创建 CrewAI Agent
            if 'is_crew' in optimized_config and optimized_config['is_crew']:
                # 创建 Crew（多智能体团队）
                crew = self._create_crew(optimized_config)
                wrapper = CrewAIAgentWrapper(crew, agent_config, is_crew=True)
            else:
                # 创建单个 Agent
                agent = self._create_single_agent(optimized_config)
                wrapper = CrewAIAgentWrapper(agent, agent_config, is_crew=False)
            
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time)
            
            return wrapper
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to create CrewAI agent: {e}")
            raise AdapterError(f"Failed to create CrewAI agent: {e}", 'crewai')
            
    def create_task(self, task_config: dict) -> 'TaskInterface':
        """创建任务"""
        if not self.initialized:
            raise RuntimeError("CrewAI adapter not initialized")
            
        # 转换配置
        crewai_task_config = self.translator.translate_task_config(task_config)
        
        # 创建任务对象
        return CrewAITaskWrapper(crewai_task_config, task_config)
        
    def execute_task(self, agent: 'AgentInterface', task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        if not self.initialized:
            raise RuntimeError("CrewAI adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 确保是 CrewAI 智能体和任务
            if not isinstance(agent, CrewAIAgentWrapper):
                raise TypeError("Agent must be a CrewAIAgentWrapper instance")
                
            if not isinstance(task, CrewAITaskWrapper):
                raise TypeError("Task must be a CrewAITaskWrapper instance")
                
            # 获取原始 CrewAI 智能体和任务配置
            crewai_agent = agent.agent
            task_config = task.crewai_config
            
            # 根据智能体类型执行不同的操作
            if agent.is_crew:
                # 如果是 Crew，执行 Crew 任务
                result = self._execute_crew_task(crewai_agent, task_config)
            else:
                # 如果是单个 Agent，执行 Agent 任务
                result = self._execute_agent_task(crewai_agent, task_config)
                
            # 创建结果
            result_wrapper = CrewAIResultWrapper(result, task)
            
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time)
            
            return result_wrapper
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to execute task with CrewAI agent: {e}")
            raise AdapterError(f"Failed to execute task: {e}", 'crewai')
            
    def _create_single_agent(self, config: dict) -> Any:
        """创建单个 CrewAI Agent"""
        from crewai import Agent
        
        # 获取 LLM
        llm = self._get_llm(config)
        
        # 获取工具
        tools = self._get_tools(config)
        
        # 创建 Agent
        agent = Agent(
            role=config.get('role', 'Assistant'),
            goal=config.get('goal', 'Help the user with their tasks'),
            backstory=config.get('backstory', 'You are an AI assistant'),
            verbose=config.get('verbose', False),
            allow_delegation=config.get('allow_delegation', False),
            tools=tools,
            llm=llm
        )
        
        return agent
        
    def _create_crew(self, config: dict) -> Any:
        """创建 CrewAI Crew（多智能体团队）"""
        from crewai import Crew, Agent, Task, Process
        
        # 创建 Agents
        agents = []
        for agent_config in config.get('agents', []):
            agent = self._create_single_agent(agent_config)
            agents.append(agent)
            
        # 创建 Tasks
        tasks = []
        for task_config in config.get('tasks', []):
            # 获取执行该任务的 Agent
            agent_index = task_config.get('agent_index', 0)
            if 0 <= agent_index < len(agents):
                agent = agents[agent_index]
            else:
                agent = agents[0]
                
            # 创建 Task
            task = Task(
                description=task_config.get('description', ''),
                expected_output=task_config.get('expected_output', ''),
                agent=agent,
                context=task_config.get('context', ''),
                tools=self._get_tools(task_config)
            )
            tasks.append(task)
            
        # 确定流程类型
        process_type = config.get('process', 'sequential')
        if process_type == 'sequential':
            process = Process.sequential
        elif process_type == 'hierarchical':
            process = Process.hierarchical
        else:  # 默认为顺序流程
            process = Process.sequential
            
        # 创建 Crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=config.get('verbose', False),
            process=process,
            memory=config.get('memory', False)
        )
        
        return crew
        
    def _execute_agent_task(self, agent: Any, task_config: dict) -> Any:
        """执行单个 Agent 的任务"""
        # 创建 CrewAI Task
        from crewai import Task
        
        task = Task(
            description=task_config.get('description', ''),
            expected_output=task_config.get('expected_output', ''),
            agent=agent,
            context=task_config.get('context', ''),
            tools=self._get_tools(task_config)
        )
        
        # 执行任务
        return agent.execute_task(task)
        
    def _execute_crew_task(self, crew: Any, task_config: dict) -> Any:
        """执行 Crew 的任务"""
        # 对于 Crew，我们直接调用 Crew 的 kickoff 方法
        return crew.kickoff()
        
    def _get_llm(self, config: dict) -> Any:
        """获取 LLM 实例"""
        llm_config = config.get('llm_config', {})
        llm_type = llm_config.get('type', 'openai')
        
        if llm_type == 'openai':
            from langchain.chat_models import ChatOpenAI
            return ChatOpenAI(
                temperature=llm_config.get('temperature', 0.7),
                model_name=llm_config.get('model', 'gpt-3.5-turbo'),
                openai_api_key=llm_config.get('api_key')
            )
        elif llm_type == 'anthropic':
            from langchain.chat_models import ChatAnthropic
            return ChatAnthropic(
                temperature=llm_config.get('temperature', 0.7),
                model_name=llm_config.get('model', 'claude-2'),
                anthropic_api_key=llm_config.get('api_key')
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
            
    def _get_tools(self, config: dict) -> List[Any]:
        """获取工具列表"""
        tools_config = config.get('tools_config', [])
        tools = []
        
        for tool_config in tools_config:
            tool_type = tool_config.get('type')
            
            if tool_type == 'search':
                from langchain.tools import DuckDuckGoSearchRun
                tools.append(DuckDuckGoSearchRun())
            elif tool_type == 'calculator':
                from langchain.tools import Tool
                from langchain.tools.python.tool import PythonREPLTool
                tools.append(
                    Tool(
                        name="Calculator",
                        func=PythonREPLTool().run,
                        description="Useful for calculations"
                    )
                )
            elif tool_type == 'custom':
                from langchain.tools import Tool
                tools.append(
                    Tool(
                        name=tool_config.get('name', 'CustomTool'),
                        func=self._create_custom_tool_func(tool_config),
                        description=tool_config.get('description', '')
                    )
                )
                
        return tools
        
    def _create_custom_tool_func(self, tool_config: dict) -> Callable:
        """创建自定义工具函数"""
        def custom_tool(input_str: str) -> str:
            # 这里可以实现自定义工具的逻辑
            # 简单示例：返回输入字符串的反转
            return input_str[::-1]
            
        return custom_tool
```

### 3.3 智能体包装器

```python
class CrewAIAgentWrapper(AgentInterface):
    """CrewAI 智能体包装器，实现统一的 AgentInterface 接口"""
    
    def __init__(self, agent, config: dict, is_crew: bool = False):
        self.agent = agent  # 原始 CrewAI 智能体或 Crew
        self.config = config  # 原始配置
        self.is_crew = is_crew  # 是否是 Crew（多智能体团队）
        self.id = str(uuid.uuid4())
        
    def get_id(self) -> str:
        """获取智能体 ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取智能体名称"""
        return self.config.get('name', 'unnamed_agent')
        
    def get_description(self) -> str:
        """获取智能体描述"""
        if self.is_crew:
            return self.config.get('description', 'A team of AI agents')
        else:
            return self.config.get('description', self.agent.backstory if hasattr(self.agent, 'backstory') else '')
        
    def get_capabilities(self) -> List[str]:
        """获取智能体能力"""
        # 根据智能体类型返回不同的能力
        capabilities = ['basic_conversation']
        
        if self.is_crew:
            capabilities.extend([
                'multi_agent_collaboration',
                'task_delegation',
                'sequential_workflows'
            ])
            
            # 检查流程类型
            if self.config.get('process') == 'hierarchical':
                capabilities.append('hierarchical_workflows')
                
        # 检查是否有工具
        if hasattr(self.agent, 'tools') and self.agent.tools:
            capabilities.append('tool_use')
            
            # 检查特定工具类型
            for tool in self.agent.tools:
                if 'search' in tool.name.lower():
                    capabilities.append('web_search')
                if 'calculator' in tool.name.lower():
                    capabilities.append('calculation')
                    
        # 检查是否允许委派任务
        if not self.is_crew and hasattr(self.agent, 'allow_delegation') and self.agent.allow_delegation:
            capabilities.append('task_delegation')
            
        return capabilities
        
    def execute_task(self, task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        # 获取适配器并执行任务
        from unified_agent.adapter.registry import AdapterRegistry
        
        registry = AdapterRegistry.get_instance()
        adapter = registry.get_adapter('crewai')
        
        if adapter is None:
            raise RuntimeError("CrewAI adapter not found")
            
        return adapter.execute_task(self, task)
```

### 3.4 任务包装器

```python
class CrewAITaskWrapper(TaskInterface):
    """CrewAI 任务包装器，实现统一的 TaskInterface 接口"""
    
    def __init__(self, crewai_config: dict, original_config: dict):
        self.crewai_config = crewai_config  # CrewAI 特定配置
        self.original_config = original_config  # 原始配置
        self.id = str(uuid.uuid4())
        self.created_at = time.time()
        
    def get_id(self) -> str:
        """获取任务 ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取任务类型"""
        return self.original_config.get('type', 'standard')
        
    def get_description(self) -> str:
        """获取任务描述"""
        return self.original_config.get('description', '')
        
    def get_config(self) -> dict:
        """获取任务配置"""
        return self.original_config
        
    def get_created_time(self) -> float:
        """获取任务创建时间"""
        return self.created_at
```

### 3.5 结果包装器

```python
class CrewAIResultWrapper(ResultInterface):
    """CrewAI 结果包装器，实现统一的 ResultInterface 接口"""
    
    def __init__(self, result, task: 'TaskInterface'):
        self.result = result  # 原始 CrewAI 结果
        self.task = task  # 关联的任务
        self.id = str(uuid.uuid4())
        self.created_at = time.time()
        
    def get_id(self) -> str:
        """获取结果 ID"""
        return self.id
        
    def get_task_id(self) -> str:
        """获取关联的任务 ID"""
        return self.task.get_id()
        
    def get_content(self) -> Any:
        """获取结果内容"""
        # CrewAI 的结果通常是字符串
        return self.result
        
    def get_created_time(self) -> float:
        """获取结果创建时间"""
        return self.created_at
        
    def is_success(self) -> bool:
        """检查任务是否成功"""
        # CrewAI 没有明确的成功/失败标志
        # 这里简单地检查结果是否存在
        return self.result is not None
        
    def get_error(self) -> Optional[str]:
        """获取错误信息（如果有）"""
        # 如果任务失败，返回错误信息
        if not self.is_success() and isinstance(self.result, Exception):
            return str(self.result)
        return None
```

## 4. 概念转换器

### 4.1 配置转换

```python
class CrewAIConceptTranslator(ConceptTranslator):
    """CrewAI 概念转换器，负责在统一模型和 CrewAI 模型之间转换"""
    
    def __init__(self):
        super().__init__('unified', 'crewai')
        
    def translate_agent_config(self, config: dict) -> dict:
        """将统一的 Agent 配置转换为 CrewAI 配置"""
        crewai_config = {}
        
        # 基本属性转换
        crewai_config['name'] = config.get('name', 'agent')
        
        # 检查是否是 Crew（多智能体团队）
        if 'agents' in config:
            crewai_config['is_crew'] = True
            
            # 转换 Agents 配置
            agents_config = []
            for agent in config['agents']:
                agent_config = self._translate_single_agent_config(agent)
                agents_config.append(agent_config)
                
            crewai_config['agents'] = agents_config
            
            # 转换 Tasks 配置
            if 'tasks' in config:
                tasks_config = []
                for task in config['tasks']:
                    task_config = {
                        'description': task.get('description', ''),
                        'expected_output': task.get('expected_output', ''),
                        'agent_index': task.get('agent_index', 0),
                        'context': task.get('context', ''),
                    }
                    
                    # 转换工具配置
                    if 'tools' in task:
                        tools_config = self._translate_tools_config(task['tools'])
                        task_config['tools_config'] = tools_config
                        
                    tasks_config.append(task_config)
                    
                crewai_config['tasks'] = tasks_config
                
            # 流程类型
            crewai_config['process'] = config.get('process', 'sequential')
            
            # 其他配置
            crewai_config['verbose'] = config.get('verbose', False)
            crewai_config['memory'] = config.get('memory', False)
            
        else:
            # 单个 Agent 配置
            crewai_config['is_crew'] = False
            single_agent_config = self._translate_single_agent_config(config)
            crewai_config.update(single_agent_config)
            
        return crewai_config
        
    def _translate_single_agent_config(self, config: dict) -> dict:
        """转换单个 Agent 配置"""
        agent_config = {}
        
        # 基本属性
        agent_config['role'] = config.get('role', 'Assistant')
        agent_config['goal'] = config.get('goal', 'Help the user with their tasks')
        agent_config['backstory'] = config.get('backstory', 'You are an AI assistant')
        agent_config['verbose'] = config.get('verbose', False)
        agent_config['allow_delegation'] = config.get('allow_delegation', False)
        
        # 转换 LLM 配置
        if 'llm' in config:
            llm_config = self._translate_llm_config(config['llm'])
            agent_config['llm_config'] = llm_config
            
        # 转换工具配置
        if 'tools' in config:
            tools_config = self._translate_tools_config(config['tools'])
            agent_config['tools_config'] = tools_config
            
        return agent_config
        
    def translate_task_config(self, config: dict) -> dict:
        """将统一的任务配置转换为 CrewAI 任务配置"""
        crewai_config = {}
        
        # 基本属性转换
        crewai_config['description'] = config.get('description', '')
        crewai_config['expected_output'] = config.get('expected_output', '')
        crewai_config['context'] = config.get('context', '')
        
        # 转换工具配置
        if 'tools' in config:
            tools_config = self._translate_tools_config(config['tools'])
            crewai_config['tools_config'] = tools_config
            
        return crewai_config
        
    def translate_result(self, result: Any) -> 'ResultInterface':
        """将 CrewAI 结果转换为统一结果接口"""
        # 这个方法在 CrewAIResultWrapper 中实现
        pass
        
    def _translate_llm_config(self, llm_config: dict) -> dict:
        """转换 LLM 配置"""
        crewai_llm_config = {}
        
        # 确定 LLM 类型
        model_type = llm_config.get('type', 'openai').lower()
        crewai_llm_config['type'] = model_type
            
        # 模型名称
        if 'model' in llm_config:
            crewai_llm_config['model'] = llm_config['model']
            
        # 温度
        if 'temperature' in llm_config:
            crewai_llm_config['temperature'] = llm_config['temperature']
            
        # API 密钥
        if 'api_key' in llm_config:
            crewai_llm_config['api_key'] = llm_config['api_key']
            
        return crewai_llm_config
        
    def _translate_tools_config(self, tools: List[dict]) -> List[dict]:
        """转换工具配置"""
        tools_config = []
        
        for tool in tools:
            tool_config = {
                'type': tool.get('type'),
                'name': tool.get('name'),
                'description': tool.get('description')
            }
            tools_config.append(tool_config)
            
        return tools_config
```

## 5. 性能优化

### 5.1 缓存优化

```python
class CrewAIPerformanceOptimizer(PerformanceOptimizer):
    """CrewAI 性能优化器"""
    
    def __init__(self, adapter: 'CrewAIAdapter'):
        super().__init__(adapter)
        self.config_cache = AdapterCache(max_size=100)
        self.response_cache = AdapterCache(max_size=50)
        
    def optimize_agent_creation(self, config: dict) -> dict:
        """优化 Agent 创建过程"""
        # 检查缓存中是否有相同配置
        config_key = self._get_config_hash(config)
        cached_config = self.config_cache.get(config_key)
        
        if cached_config:
            return cached_config
            
        # 应用优化
        optimized_config = config.copy()
        
        # 优化 1: 移除不必要的配置项
        if optimized_config.get('is_crew', False):
            # Crew 配置优化
            for key in list(optimized_config.keys()):
                if key not in ['name', 'is_crew', 'agents', 'tasks', 'process', 'verbose', 'memory']:
                    optimized_config.pop(key, None)
        else:
            # 单个 Agent 配置优化
            for key in list(optimized_config.keys()):
                if key not in ['name', 'is_crew', 'role', 'goal', 'backstory', 
                              'verbose', 'allow_delegation', 'llm_config', 'tools_config']:
                    optimized_config.pop(key, None)
                    
        # 缓存优化后的配置
        self.config_cache.set(config_key, optimized_config)
        
        return optimized_config
        
    def optimize_task_execution(self, agent: 'AgentInterface', task: 'TaskInterface') -> tuple:
        """优化任务执行过程"""
        # 检查是否可以从缓存获取结果
        if isinstance(task, CrewAITaskWrapper):
            task_key = self._get_task_hash(task.original_config)
            cached_result = self.response_cache.get(task_key)
            
            if cached_result:
                return cached_result, True  # 返回缓存结果和缓存命中标志
                
        return (agent, task), False  # 返回原始参数和缓存未命中标志
        
    def collect_metrics(self, operation: str, start_time: float, end_time: float, metadata: dict = None):
        """收集性能指标"""
        duration = end_time - start_time
        
        if operation not in self.metrics:
            self.metrics[operation] = []
            
        metric_entry = {
            'duration': duration,
            'timestamp': end_time,
        }
        
        if metadata:
            metric_entry.update(metadata)
            
        self.metrics[operation].append(metric_entry)
        
        # 记录到日志
        logger.debug(f"CrewAI {operation} took {duration:.4f} seconds")
        
        # 如果操作时间过长，记录警告
        if operation == 'task_execution' and duration > 10.0:
            logger.warning(f"CrewAI task execution took {duration:.4f} seconds, which is longer than expected")
            
    def _get_config_hash(self, config: dict) -> str:
        """获取配置的哈希值，用于缓存键"""
        # 将配置转换为规范化的 JSON 字符串
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
        
    def _get_task_hash(self, task_config: dict) -> str:
        """获取任务配置的哈希值，用于缓存键"""
        # 将任务配置转换为规范化的 JSON 字符串
        config_str = json.dumps(task_config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
```

## 6. 使用示例

### 6.1 单个智能体

```python
from unified_agent.adapter.registry import AdapterRegistry

# 获取适配器注册表
registry = AdapterRegistry.get_instance()

# 获取 CrewAI 适配器
crewai_adapter = registry.get_adapter('crewai')

# 创建单个 Agent
agent_config = {
    'name': 'research_assistant',
    'role': 'Research Assistant',
    'goal': 'Find accurate information and summarize it concisely',
    'backstory': 'You are an expert research assistant with a talent for finding and summarizing information.',
    'llm': {
        'type': 'openai',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.2
    },
    'tools': [
        {
            'type': 'search',
            'name': 'Search',
            'description': 'Useful for searching the internet'
        },
        {
            'type': 'calculator',
            'name': 'Calculator',
            'description': 'Useful for calculations'
        }
    ],
    'verbose': True
}

agent = crewai_adapter.create_agent(agent_config)

# 创建任务
task_config = {
    'type': 'standard',
    'description': 'Research the latest advancements in quantum computing and summarize the key findings.',
    'expected_output': 'A concise summary of the latest advancements in quantum computing.'
}

task = crewai_adapter.create_task(task_config)

# 执行任务
result = crewai_adapter.execute_task(agent, task)

# 获取结果
print(result.get_content())
```

### 6.2 多智能体团队

```python
# 创建多智能体团队
crew_config = {
    'name': 'research_team',
    'agents': [
        {
            'role': 'Research Analyst',
            'goal': 'Find accurate information on the topic',
            'backstory': 'You are an expert researcher with a talent for finding information.',
            'llm': {
                'type': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.2
            },
            'tools': [
                {
                    'type': 'search',
                    'name': 'Search',
                    'description': 'Useful for searching the internet'
                }
            ]
        },
        {
            'role': 'Technical Writer',
            'goal': 'Summarize information in a clear and concise manner',
            'backstory': 'You are an expert technical writer with a talent for explaining complex topics.',
            'llm': {
                'type': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.3
            }
        },
        {
            'role': 'Fact Checker',
            'goal': 'Verify the accuracy of information',
            'backstory': 'You are an expert fact checker with a talent for verifying information.',
            'llm': {
                'type': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.1
            },
            'tools': [
                {
                    'type': 'search',
                    'name': 'Search',
                    'description': 'Useful for searching the internet'
                }
            ]
        }
    ],
    'tasks': [
        {
            'description': 'Research the latest advancements in quantum computing.',
            'expected_output': 'A list of the latest advancements in quantum computing.',
            'agent_index': 0,  # Research Analyst
            'context': 'Focus on developments from the last 2 years.'
        },
        {
            'description': 'Summarize the research findings in a clear and concise manner.',
            'expected_output': 'A concise summary of the latest advancements in quantum computing.',
            'agent_index': 1,  # Technical Writer
            'context': 'The summary should be accessible to a non-technical audience.'
        },
        {
            'description': 'Verify the accuracy of the information in the summary.',
            'expected_output': 'A verified summary with any corrections noted.',
            'agent_index': 2,  # Fact Checker
            'context': 'Check for any factual errors or misrepresentations.'
        }
    ],
    'process': 'sequential',
    'verbose': True,
    'memory': True
}

crew = crewai_adapter.create_agent(crew_config)

# 创建任务
crew_task_config = {
    'type': 'crew',
    'description': 'Research, summarize, and verify information about quantum computing advancements.'
}

crew_task = crewai_adapter.create_task(crew_task_config)

# 执行任务
result = crewai_adapter.execute_task(crew, crew_task)

# 获取结果
print(result.get_content())
```

## 7. 错误处理

### 7.1 常见错误及处理

```python
class CrewAIErrorHandler:
    @staticmethod
    def handle_initialization_error(error: Exception) -> str:
        """处理初始化错误"""
        if isinstance(error, ImportError):
            return "CrewAI 框架未安装，请使用 'pip install crewai' 安装"
        return f"CrewAI 适配器初始化失败: {error}"
        
    @staticmethod
    def handle_agent_creation_error(error: Exception, config: dict) -> str:
        """处理 Agent 创建错误"""
        if 'is_crew' in config and config['is_crew']:
            if 'agents' not in config or not config['agents']:
                return "创建 Crew 失败: 没有指定 agents"
            if 'tasks' not in config or not config['tasks']:
                return "创建 Crew 失败: 没有指定 tasks"
                
        if 'llm_config' in config and isinstance(error, KeyError):
            return f"LLM 配置错误: {error}"
            
        return f"创建 CrewAI Agent 失败: {error}"
        
    @staticmethod
    def handle_task_execution_error(error: Exception, task_config: dict) -> str:
        """处理任务执行错误"""
        if 'type' in task_config:
            task_type = task_config['type']
            if task_type not in ['standard', 'crew']:
                return f"不支持的任务类型: {task_type}"
                
        return f"执行 CrewAI 任务失败: {error}"
```

## 8. 测试

### 8.1 单元测试

```python
import unittest
from unittest.mock import MagicMock, patch

class TestCrewAIAdapter(unittest.TestCase):
    def setUp(self):
        # 模拟 CrewAI 模块
        self.crewai_mock = MagicMock()
        self.crewai_mock.Agent = MagicMock(return_value=MagicMock())
        self.crewai_mock.Crew = MagicMock(return_value=MagicMock())
        self.crewai_mock.Task = MagicMock(return_value=MagicMock())
        self.crewai_mock.Process = MagicMock()
        self.crewai_mock.Process.sequential = 'sequential'
        self.crewai_mock.Process.hierarchical = 'hierarchical'
        
        # 创建适配器
        with patch.dict('sys.modules', {'crewai': self.crewai_mock}):
            from unified_agent.adapter.crewai import CrewAIAdapter
            self.adapter = CrewAIAdapter()
            self.adapter.initialize()
            
    def test_initialize(self):
        self.assertTrue(self.adapter.initialized)
        
    def test_get_capabilities(self):
        capabilities = self.adapter.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertIn('multi_agent_collaboration', capabilities)
        self.assertIn('role_based_agents', capabilities)
        
    def test_create_single_agent(self):
        config = {
            'name': 'test_agent',
            'role': 'Research Assistant',
            'goal': 'Find accurate information',
            'backstory': 'You are an expert researcher',
            'llm': {
                'type': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7
            },
            'tools': [
                {
                    'type': 'search',
                    'name': 'Search',
                    'description': 'Useful for searching the internet'
                }
            ],
            'verbose': True
        }
        
        agent = self.adapter.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get_name(), 'test_agent')
        self.assertFalse(agent.is_crew)
        
        # 验证 CrewAI Agent 被正确创建
        self.crewai_mock.Agent.assert_called_once()
        
    def test_create_crew(self):
        config = {
            'name': 'test_crew',
            'agents': [
                {
                    'role': 'Researcher',
                    'goal': 'Find information',
                    'backstory': 'You are a researcher'
                },
                {
                    'role': 'Writer',
                    'goal': 'Write summaries',
                    'backstory': 'You are a writer'
                }
            ],
            'tasks': [
                {
                    'description': 'Research topic',
                    'expected_output': 'Research findings',
                    'agent_index': 0
                },
                {
                    'description': 'Write summary',
                    'expected_output': 'Summary',
                    'agent_index': 1
                }
            ],
            'process': 'sequential',
            'verbose': True
        }
        
        crew = self.adapter.create_agent(config)
        self.assertIsNotNone(crew)
        self.assertEqual(crew.get_name(), 'test_crew')
        self.assertTrue(crew.is_crew)
        
        # 验证 CrewAI Crew 被正确创建
        self.crewai_mock.Crew.assert_called_once()
        
    def test_create_and_execute_task(self):
        # 创建单个 Agent
        agent_config = {
            'name': 'test_agent',
            'role': 'Assistant',
            'goal': 'Help user',
            'backstory': 'You are an assistant'
        }
        agent = self.adapter.create_agent(agent_config)
        
        # 创建任务
        task_config = {
            'type': 'standard',
            'description': 'Answer a question',
            'expected_output': 'An answer'
        }
        task = self.adapter.create_task(task_config)
        
        # 模拟 Agent 的 execute_task 方法
        agent.agent.execute_task = MagicMock(return_value="This is the answer.")
        
        # 执行任务
        result = self.adapter.execute_task(agent, task)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertTrue(result.is_success())
        self.assertEqual(result.get_content(), "This is the answer.")
        
        # 验证 execute_task 方法被正确调用
        agent.agent.execute_task.assert_called_once()
```

## 9. 总结

CrewAI 适配器实现了将 CrewAI 框架的功能和特性映射到统一 Agent 框架的抽象接口。通过这个适配器，开发者可以使用统一的接口和概念模型来创建和管理 CrewAI Agent 和 Crew，同时保留 CrewAI 框架的强大功能，如多智能体协作、角色定义、任务分配和工作流管理等。

适配器的设计遵循了模块化、可扩展性和性能优先的原则，提供了完整的生命周期管理、错误处理和性能优化功能。通过概念转换器，适配器实现了统一模型和 CrewAI 模型之间的无缝转换，使开发者能够轻松地在不同框架之间切换。

CrewAI 适配器特别适合需要多智能体协作和复杂工作流管理的应用场景，为开发者提供了强大而灵活的工具，以构建更加智能和协作的 AI 系统。