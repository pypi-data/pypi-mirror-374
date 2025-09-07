# AutoGen 适配器设计文档

## 1. 概述

AutoGen 是微软开发的一个多智能体对话框架，支持多个智能体之间的对话和协作。本文档详细描述了 AutoGen 适配器的设计和实现，包括如何将 AutoGen 的特性和功能映射到统一 Agent 框架的抽象接口。

## 2. AutoGen 框架特性

### 2.1 核心特性

- **多智能体对话**：支持多个智能体之间的对话和协作
- **自定义智能体**：支持创建自定义智能体，包括 AssistantAgent 和 UserProxyAgent
- **工具使用**：支持智能体使用工具执行任务
- **人类反馈**：支持人类在循环中提供反馈
- **代码生成与执行**：特别擅长代码生成和执行任务

### 2.2 主要组件

- **AssistantAgent**：模拟 AI 助手的智能体
- **UserProxyAgent**：代表用户的智能体，可以执行代码和使用工具
- **GroupChat**：支持多个智能体之间的群组对话
- **GroupChatManager**：管理群组对话的流程和选择发言者

## 3. 适配器设计

### 3.1 类图

```
+-------------------+      +----------------------+
|   BaseAdapter     |<---- |   AutoGenAdapter    |
+-------------------+      +----------------------+
| + initialize()    |      | + initialize()       |
| + shutdown()      |      | + shutdown()         |
| + get_capabilities()|    | + get_capabilities() |
| + create_agent()  |      | + create_agent()     |
| + create_task()   |      | + create_task()      |
| + execute_task()  |      | + execute_task()     |
+-------------------+      +----------------------+
                                      |
                                      |
                           +----------v-----------+
                           | AutoGenAgentWrapper  |
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
class AutoGenAdapter(BaseAdapter):
    """AutoGen 框架适配器"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.translator = ConceptTranslator('unified', 'autogen')
        self.optimizer = PerformanceOptimizer(self)
        self.autogen = None
        
    def initialize(self) -> bool:
        """初始化 AutoGen 适配器"""
        try:
            import autogen
            self.autogen = autogen
            self.initialized = True
            logger.info("AutoGen adapter initialized successfully")
            return True
        except ImportError:
            logger.error("Failed to initialize AutoGen adapter: AutoGen package not installed")
            return False
            
    def shutdown(self) -> bool:
        """关闭 AutoGen 适配器"""
        # AutoGen 没有特定的关闭操作
        self.initialized = False
        return True
        
    def get_capabilities(self) -> List[str]:
        """返回 AutoGen 适配器支持的能力"""
        return [
            'multi_agent_conversation',
            'tool_use',
            'human_feedback',
            'code_generation',
            'code_execution',
            'agent_customization'
        ]
        
    def create_agent(self, agent_config: dict) -> 'AgentInterface':
        """创建 AutoGen 智能体"""
        if not self.initialized:
            raise RuntimeError("AutoGen adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 转换配置
            autogen_config = self.translator.translate_agent_config(agent_config)
            
            # 优化配置
            optimized_config = self.optimizer.optimize_agent_creation(autogen_config)
            
            # 创建 AutoGen 智能体
            agent_type = optimized_config.pop('agent_type', 'assistant')
            
            if agent_type == 'assistant':
                agent = self.autogen.AssistantAgent(
                    name=optimized_config.get('name', 'assistant'),
                    system_message=optimized_config.get('system_message', ''),
                    llm_config=optimized_config.get('llm_config', {})
                )
            elif agent_type == 'user_proxy':
                agent = self.autogen.UserProxyAgent(
                    name=optimized_config.get('name', 'user_proxy'),
                    human_input_mode=optimized_config.get('human_input_mode', 'NEVER'),
                    max_consecutive_auto_reply=optimized_config.get('max_consecutive_auto_reply', 10),
                    code_execution_config=optimized_config.get('code_execution_config', {})
                )
            elif agent_type == 'group_chat':
                # 创建群组对话中的智能体
                agents = []
                for agent_conf in optimized_config.get('agents', []):
                    agent_instance = self.create_agent(agent_conf)
                    if isinstance(agent_instance, AutoGenAgentWrapper):
                        agents.append(agent_instance.agent)
                    else:
                        agents.append(agent_instance)
                        
                # 创建群组对话管理器
                agent = self.autogen.GroupChat(
                    agents=agents,
                    messages=[],
                    max_round=optimized_config.get('max_round', 10)
                )
                
                # 创建群组对话管理器
                manager = self.autogen.GroupChatManager(
                    groupchat=agent,
                    llm_config=optimized_config.get('llm_config', {})
                )
                
                # 返回管理器作为主要智能体
                agent = manager
            else:
                raise ValueError(f"Unsupported agent type: {agent_type}")
                
            # 包装为统一接口
            wrapper = AutoGenAgentWrapper(agent, agent_config)
            
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time)
            
            return wrapper
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to create AutoGen agent: {e}")
            raise AdapterError(f"Failed to create AutoGen agent: {e}", 'autogen')
            
    def create_task(self, task_config: dict) -> 'TaskInterface':
        """创建任务"""
        if not self.initialized:
            raise RuntimeError("AutoGen adapter not initialized")
            
        # 转换配置
        autogen_task_config = self.translator.translate_task_config(task_config)
        
        # 创建任务对象
        return AutoGenTaskWrapper(autogen_task_config, task_config)
        
    def execute_task(self, agent: 'AgentInterface', task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        if not self.initialized:
            raise RuntimeError("AutoGen adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 确保是 AutoGen 智能体和任务
            if not isinstance(agent, AutoGenAgentWrapper):
                raise TypeError("Agent must be an AutoGenAgentWrapper instance")
                
            if not isinstance(task, AutoGenTaskWrapper):
                raise TypeError("Task must be an AutoGenTaskWrapper instance")
                
            # 获取原始 AutoGen 智能体和任务配置
            autogen_agent = agent.agent
            task_config = task.autogen_config
            
            # 根据任务类型执行不同的操作
            task_type = task_config.get('type', 'conversation')
            
            if task_type == 'conversation':
                # 对话任务
                message = task_config.get('message', '')
                recipient = None
                
                # 如果指定了接收者，获取接收者智能体
                if 'recipient' in task_config:
                    recipient_name = task_config['recipient']
                    # 这里需要一个方法来查找接收者智能体
                    # 简化示例，实际实现可能更复杂
                    recipient = autogen_agent  # 默认发送给自己
                    
                # 执行对话
                if isinstance(autogen_agent, self.autogen.GroupChatManager):
                    # 群组对话
                    response = autogen_agent.initiate_chat(
                        message=message,
                        sender=task_config.get('sender', None)
                    )
                else:
                    # 单智能体对话
                    response = autogen_agent.initiate_chat(
                        recipient,
                        message=message
                    )
                    
                # 创建结果
                result = AutoGenResultWrapper(response, task)
                
            elif task_type == 'code_generation':
                # 代码生成任务
                prompt = task_config.get('prompt', '')
                language = task_config.get('language', 'python')
                
                # 构建代码生成提示
                code_prompt = f"Generate {language} code for: {prompt}\n"
                code_prompt += f"Only provide the code without explanations."
                
                # 执行代码生成
                if isinstance(autogen_agent, self.autogen.AssistantAgent):
                    # 使用 AssistantAgent 生成代码
                    response = autogen_agent.generate_reply(
                        messages=[{"role": "user", "content": code_prompt}],
                        sender=None
                    )
                else:
                    # 使用其他类型的智能体
                    # 这里可能需要不同的处理方式
                    response = autogen_agent.generate_reply(
                        messages=[{"role": "user", "content": code_prompt}]
                    )
                    
                # 创建结果
                result = AutoGenResultWrapper(response, task)
                
            elif task_type == 'tool_use':
                # 工具使用任务
                tool_name = task_config.get('tool_name', '')
                tool_input = task_config.get('tool_input', {})
                
                # 构建工具使用提示
                tool_prompt = f"Use the tool {tool_name} with the following input: {json.dumps(tool_input)}"
                
                # 执行工具使用
                if isinstance(autogen_agent, self.autogen.UserProxyAgent):
                    # UserProxyAgent 可以执行工具
                    response = autogen_agent.generate_reply(
                        messages=[{"role": "user", "content": tool_prompt}],
                        sender=None
                    )
                else:
                    # 其他类型的智能体可能需要不同的处理方式
                    response = autogen_agent.generate_reply(
                        messages=[{"role": "user", "content": tool_prompt}]
                    )
                    
                # 创建结果
                result = AutoGenResultWrapper(response, task)
                
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to execute task with AutoGen agent: {e}")
            raise AdapterError(f"Failed to execute task: {e}", 'autogen')
```

### 3.3 智能体包装器

```python
class AutoGenAgentWrapper(AgentInterface):
    """AutoGen 智能体包装器，实现统一的 AgentInterface 接口"""
    
    def __init__(self, agent, config: dict):
        self.agent = agent  # 原始 AutoGen 智能体
        self.config = config  # 原始配置
        self.id = str(uuid.uuid4())
        
    def get_id(self) -> str:
        """获取智能体 ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取智能体名称"""
        if hasattr(self.agent, 'name'):
            return self.agent.name
        return self.config.get('name', 'unnamed_agent')
        
    def get_description(self) -> str:
        """获取智能体描述"""
        return self.config.get('description', '')
        
    def get_capabilities(self) -> List[str]:
        """获取智能体能力"""
        # 根据智能体类型返回不同的能力
        import autogen
        
        capabilities = ['basic_conversation']
        
        if isinstance(self.agent, autogen.AssistantAgent):
            capabilities.extend([
                'text_generation',
                'reasoning',
                'conversation'
            ])
            
        elif isinstance(self.agent, autogen.UserProxyAgent):
            capabilities.extend([
                'code_execution',
                'tool_use',
                'human_feedback'
            ])
            
            # 检查是否启用了代码执行
            if hasattr(self.agent, 'code_execution_config') and self.agent.code_execution_config:
                capabilities.append('code_execution')
                
        elif isinstance(self.agent, autogen.GroupChat) or isinstance(self.agent, autogen.GroupChatManager):
            capabilities.extend([
                'multi_agent_conversation',
                'agent_selection',
                'conversation_management'
            ])
            
        return capabilities
        
    def execute_task(self, task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        # 获取适配器并执行任务
        from unified_agent.adapter.registry import AdapterRegistry
        
        registry = AdapterRegistry.get_instance()
        adapter = registry.get_adapter('autogen')
        
        if adapter is None:
            raise RuntimeError("AutoGen adapter not found")
            
        return adapter.execute_task(self, task)
```

### 3.4 任务包装器

```python
class AutoGenTaskWrapper(TaskInterface):
    """AutoGen 任务包装器，实现统一的 TaskInterface 接口"""
    
    def __init__(self, autogen_config: dict, original_config: dict):
        self.autogen_config = autogen_config  # AutoGen 特定配置
        self.original_config = original_config  # 原始配置
        self.id = str(uuid.uuid4())
        self.created_at = time.time()
        
    def get_id(self) -> str:
        """获取任务 ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取任务类型"""
        return self.original_config.get('type', 'conversation')
        
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
class AutoGenResultWrapper(ResultInterface):
    """AutoGen 结果包装器，实现统一的 ResultInterface 接口"""
    
    def __init__(self, result, task: 'TaskInterface'):
        self.result = result  # 原始 AutoGen 结果
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
        return self.result
        
    def get_created_time(self) -> float:
        """获取结果创建时间"""
        return self.created_at
        
    def is_success(self) -> bool:
        """检查任务是否成功"""
        # AutoGen 没有明确的成功/失败标志
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
class AutoGenConceptTranslator(ConceptTranslator):
    """AutoGen 概念转换器，负责在统一模型和 AutoGen 模型之间转换"""
    
    def __init__(self):
        super().__init__('unified', 'autogen')
        
    def translate_agent_config(self, config: dict) -> dict:
        """将统一的 Agent 配置转换为 AutoGen 配置"""
        autogen_config = {}
        
        # 基本属性转换
        autogen_config['name'] = config.get('name', 'agent')
        
        # 确定 Agent 类型
        agent_type = config.get('type', 'assistant').lower()
        autogen_config['agent_type'] = agent_type
        
        if agent_type == 'assistant':
            # AssistantAgent 特定配置
            autogen_config['system_message'] = config.get('system_message', '')
            
            # LLM 配置转换
            if 'llm' in config:
                llm_config = self._translate_llm_config(config['llm'])
                autogen_config['llm_config'] = llm_config
                
        elif agent_type == 'user_proxy':
            # UserProxyAgent 特定配置
            autogen_config['human_input_mode'] = config.get('human_input_mode', 'NEVER')
            autogen_config['max_consecutive_auto_reply'] = config.get('max_consecutive_auto_reply', 10)
            
            # 代码执行配置
            if 'code_execution' in config:
                code_exec_config = {
                    'work_dir': config['code_execution'].get('work_dir', './tmp'),
                    'use_docker': config['code_execution'].get('use_docker', False),
                }
                autogen_config['code_execution_config'] = code_exec_config
                
        elif agent_type == 'group_chat':
            # GroupChat 特定配置
            autogen_config['max_round'] = config.get('max_round', 10)
            
            # 转换子智能体配置
            if 'agents' in config:
                autogen_config['agents'] = []
                for agent_conf in config['agents']:
                    autogen_config['agents'].append(self.translate_agent_config(agent_conf))
                    
            # LLM 配置（用于 GroupChatManager）
            if 'llm' in config:
                llm_config = self._translate_llm_config(config['llm'])
                autogen_config['llm_config'] = llm_config
                
        return autogen_config
        
    def translate_task_config(self, config: dict) -> dict:
        """将统一的任务配置转换为 AutoGen 任务配置"""
        autogen_config = {}
        
        # 基本属性转换
        task_type = config.get('type', 'conversation').lower()
        autogen_config['type'] = task_type
        
        if task_type == 'conversation':
            # 对话任务
            autogen_config['message'] = config.get('message', config.get('content', ''))
            
            # 如果指定了接收者
            if 'recipient' in config:
                autogen_config['recipient'] = config['recipient']
                
            # 如果指定了发送者
            if 'sender' in config:
                autogen_config['sender'] = config['sender']
                
        elif task_type == 'code_generation':
            # 代码生成任务
            autogen_config['prompt'] = config.get('prompt', config.get('description', ''))
            autogen_config['language'] = config.get('language', 'python')
            
        elif task_type == 'tool_use':
            # 工具使用任务
            autogen_config['tool_name'] = config.get('tool_name', '')
            autogen_config['tool_input'] = config.get('tool_input', {})
            
        return autogen_config
        
    def translate_result(self, result: Any) -> 'ResultInterface':
        """将 AutoGen 结果转换为统一结果接口"""
        # 这个方法在 AutoGenResultWrapper 中实现
        pass
        
    def _translate_llm_config(self, llm_config: dict) -> dict:
        """转换 LLM 配置"""
        autogen_llm_config = {}
        
        # 模型名称
        if 'model' in llm_config:
            autogen_llm_config['model'] = llm_config['model']
            
        # 温度
        if 'temperature' in llm_config:
            autogen_llm_config['temperature'] = llm_config['temperature']
            
        # API 密钥
        if 'api_key' in llm_config:
            autogen_llm_config['api_key'] = llm_config['api_key']
            
        # 其他参数
        for key in ['max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']:
            if key in llm_config:
                autogen_llm_config[key] = llm_config[key]
                
        return autogen_llm_config
```

## 5. 性能优化

### 5.1 缓存优化

```python
class AutoGenPerformanceOptimizer(PerformanceOptimizer):
    """AutoGen 性能优化器"""
    
    def __init__(self, adapter: 'AutoGenAdapter'):
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
        for key in list(optimized_config.keys()):
            if key not in ['name', 'agent_type', 'system_message', 'llm_config', 
                          'human_input_mode', 'max_consecutive_auto_reply', 
                          'code_execution_config', 'max_round', 'agents']:
                optimized_config.pop(key, None)
                
        # 优化 2: 设置合理的默认值
        if 'llm_config' in optimized_config and 'cache_seed' not in optimized_config['llm_config']:
            # 添加缓存种子以启用 LLM 响应缓存
            optimized_config['llm_config']['cache_seed'] = 42
            
        # 缓存优化后的配置
        self.config_cache.set(config_key, optimized_config)
        
        return optimized_config
        
    def optimize_task_execution(self, agent: 'AgentInterface', task: 'TaskInterface') -> tuple:
        """优化任务执行过程"""
        # 检查是否可以从缓存获取结果
        if isinstance(task, AutoGenTaskWrapper):
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
        logger.debug(f"AutoGen {operation} took {duration:.4f} seconds")
        
        # 如果操作时间过长，记录警告
        if operation == 'task_execution' and duration > 5.0:
            logger.warning(f"AutoGen task execution took {duration:.4f} seconds, which is longer than expected")
            
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

### 6.1 基本使用

```python
from unified_agent.adapter.registry import AdapterRegistry

# 获取适配器注册表
registry = AdapterRegistry.get_instance()

# 获取 AutoGen 适配器
autogen_adapter = registry.get_adapter('autogen')

# 创建 Assistant Agent
assistant_config = {
    'name': 'assistant',
    'type': 'assistant',
    'system_message': 'You are a helpful AI assistant.',
    'llm': {
        'model': 'gpt-4',
        'temperature': 0.7
    }
}

assistant = autogen_adapter.create_agent(assistant_config)

# 创建 User Proxy Agent
user_proxy_config = {
    'name': 'user_proxy',
    'type': 'user_proxy',
    'human_input_mode': 'NEVER',
    'code_execution': {
        'work_dir': './tmp',
        'use_docker': False
    }
}

user_proxy = autogen_adapter.create_agent(user_proxy_config)

# 创建对话任务
task_config = {
    'type': 'conversation',
    'message': 'Write a Python function to calculate the Fibonacci sequence.',
    'recipient': 'assistant'
}

task = autogen_adapter.create_task(task_config)

# 执行任务
result = autogen_adapter.execute_task(user_proxy, task)

# 获取结果
print(result.get_content())
```

### 6.2 多智能体对话

```python
# 创建多智能体群组对话
group_chat_config = {
    'name': 'code_team',
    'type': 'group_chat',
    'agents': [
        {
            'name': 'architect',
            'type': 'assistant',
            'system_message': 'You are a software architect who designs high-level solutions.'
        },
        {
            'name': 'coder',
            'type': 'assistant',
            'system_message': 'You are a programmer who implements solutions based on requirements.'
        },
        {
            'name': 'tester',
            'type': 'assistant',
            'system_message': 'You are a QA engineer who tests code for bugs and issues.'
        },
        {
            'name': 'user_proxy',
            'type': 'user_proxy',
            'human_input_mode': 'NEVER',
            'code_execution': {
                'work_dir': './tmp'
            }
        }
    ],
    'llm': {
        'model': 'gpt-4',
        'temperature': 0.2
    },
    'max_round': 15
}

group_chat = autogen_adapter.create_agent(group_chat_config)

# 创建任务
task_config = {
    'type': 'conversation',
    'message': 'Create a web scraper that extracts product information from an e-commerce website.',
    'sender': 'user_proxy'
}

task = autogen_adapter.create_task(task_config)

# 执行任务
result = autogen_adapter.execute_task(group_chat, task)

# 获取结果
print(result.get_content())
```

## 7. 错误处理

### 7.1 常见错误及处理

```python
class AutoGenErrorHandler:
    @staticmethod
    def handle_initialization_error(error: Exception) -> str:
        """处理初始化错误"""
        if isinstance(error, ImportError):
            return "AutoGen 框架未安装，请使用 'pip install pyautogen' 安装"
        return f"AutoGen 适配器初始化失败: {error}"
        
    @staticmethod
    def handle_agent_creation_error(error: Exception, config: dict) -> str:
        """处理 Agent 创建错误"""
        if 'agent_type' in config:
            agent_type = config['agent_type']
            if agent_type not in ['assistant', 'user_proxy', 'group_chat']:
                return f"不支持的 Agent 类型: {agent_type}"
                
        if 'llm_config' in config and isinstance(error, KeyError):
            return f"LLM 配置错误: {error}"
            
        return f"创建 AutoGen Agent 失败: {error}"
        
    @staticmethod
    def handle_task_execution_error(error: Exception, task_config: dict) -> str:
        """处理任务执行错误"""
        if 'type' in task_config:
            task_type = task_config['type']
            if task_type not in ['conversation', 'code_generation', 'tool_use']:
                return f"不支持的任务类型: {task_type}"
                
        return f"执行 AutoGen 任务失败: {error}"
```

## 8. 测试

### 8.1 单元测试

```python
import unittest
from unittest.mock import MagicMock, patch

class TestAutoGenAdapter(unittest.TestCase):
    def setUp(self):
        # 模拟 AutoGen 模块
        self.autogen_mock = MagicMock()
        self.autogen_mock.AssistantAgent = MagicMock(return_value=MagicMock())
        self.autogen_mock.UserProxyAgent = MagicMock(return_value=MagicMock())
        self.autogen_mock.GroupChat = MagicMock(return_value=MagicMock())
        self.autogen_mock.GroupChatManager = MagicMock(return_value=MagicMock())
        
        # 创建适配器
        with patch.dict('sys.modules', {'autogen': self.autogen_mock}):
            from unified_agent.adapter.autogen import AutoGenAdapter
            self.adapter = AutoGenAdapter()
            self.adapter.initialize()
            
    def test_initialize(self):
        self.assertTrue(self.adapter.initialized)
        
    def test_get_capabilities(self):
        capabilities = self.adapter.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertIn('multi_agent_conversation', capabilities)
        
    def test_create_assistant_agent(self):
        config = {
            'name': 'test_assistant',
            'type': 'assistant',
            'system_message': 'You are a test assistant',
            'llm': {
                'model': 'gpt-4',
                'temperature': 0.7
            }
        }
        
        agent = self.adapter.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get_name(), 'test_assistant')
        
        # 验证 AutoGen AssistantAgent 被正确创建
        self.autogen_mock.AssistantAgent.assert_called_once()
        
    def test_create_user_proxy_agent(self):
        config = {
            'name': 'test_user_proxy',
            'type': 'user_proxy',
            'human_input_mode': 'NEVER'
        }
        
        agent = self.adapter.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get_name(), 'test_user_proxy')
        
        # 验证 AutoGen UserProxyAgent 被正确创建
        self.autogen_mock.UserProxyAgent.assert_called_once()
        
    def test_create_group_chat(self):
        config = {
            'name': 'test_group',
            'type': 'group_chat',
            'agents': [
                {'name': 'agent1', 'type': 'assistant'},
                {'name': 'agent2', 'type': 'user_proxy'}
            ],
            'max_round': 5
        }
        
        agent = self.adapter.create_agent(config)
        self.assertIsNotNone(agent)
        
        # 验证 AutoGen GroupChat 和 GroupChatManager 被正确创建
        self.autogen_mock.GroupChat.assert_called_once()
        self.autogen_mock.GroupChatManager.assert_called_once()
        
    def test_create_and_execute_task(self):
        # 创建 Agent
        agent_config = {
            'name': 'test_assistant',
            'type': 'assistant'
        }
        agent = self.adapter.create_agent(agent_config)
        
        # 创建任务
        task_config = {
            'type': 'conversation',
            'message': 'Hello, world!'
        }
        task = self.adapter.create_task(task_config)
        
        # 执行任务
        result = self.adapter.execute_task(agent, task)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertTrue(result.is_success())
```

## 9. 总结

AutoGen 适配器实现了将 AutoGen 框架的功能和特性映射到统一 Agent 框架的抽象接口。通过这个适配器，开发者可以使用统一的接口和概念模型来创建和管理 AutoGen 智能体，同时保留 AutoGen 框架的强大功能，如多智能体对话、代码生成和执行等。

适配器的设计遵循了模块化、可扩展性和性能优先的原则，提供了完整的生命周期管理、错误处理和性能优化功能。通过概念转换器，适配器实现了统一模型和 AutoGen 模型之间的无缝转换，使开发者能够轻松地在不同框架之间切换。