# LangChain 适配器设计文档

## 1. 概述

LangChain 是一个用于开发由语言模型驱动的应用程序的框架，提供了丰富的组件和工具链接能力。本文档详细描述了 LangChain 适配器的设计和实现，包括如何将 LangChain 的特性和功能映射到统一 Agent 框架的抽象接口。

## 2. LangChain 框架特性

### 2.1 核心特性

- **链式处理**：支持将多个组件链接在一起，形成复杂的处理流程
- **Agent 与工具**：支持创建能够使用工具的 Agent
- **记忆管理**：提供多种记忆组件，支持对话历史管理
- **提示模板**：灵活的提示模板系统
- **检索增强生成**：支持从外部数据源检索信息，增强生成能力

### 2.2 主要组件

- **LLMs & Chat Models**：语言模型和对话模型接口
- **Prompts**：提示模板和提示管理
- **Chains**：将组件链接在一起的链式结构
- **Agents**：能够使用工具的智能体
- **Memory**：对话历史和状态管理
- **Tools**：Agent 可以使用的工具集合
- **Retrievers**：从数据源检索信息的组件

## 3. 适配器设计

### 3.1 类图

```
+-------------------+      +----------------------+
|   BaseAdapter     |<---- |  LangChainAdapter   |
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
                           | LangChainAgentWrapper|
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
class LangChainAdapter(BaseAdapter):
    """LangChain 框架适配器"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.translator = ConceptTranslator('unified', 'langchain')
        self.optimizer = PerformanceOptimizer(self)
        self.langchain = None
        
    def initialize(self) -> bool:
        """初始化 LangChain 适配器"""
        try:
            import langchain
            self.langchain = langchain
            self.initialized = True
            logger.info("LangChain adapter initialized successfully")
            return True
        except ImportError:
            logger.error("Failed to initialize LangChain adapter: LangChain package not installed")
            return False
            
    def shutdown(self) -> bool:
        """关闭 LangChain 适配器"""
        # LangChain 没有特定的关闭操作
        self.initialized = False
        return True
        
    def get_capabilities(self) -> List[str]:
        """返回 LangChain 适配器支持的能力"""
        return [
            'agent_chains',
            'memory_management',
            'tool_use',
            'prompt_templates',
            'retrieval_augmentation',
            'sequential_chains',
            'conversational_retrieval'
        ]
        
    def create_agent(self, agent_config: dict) -> 'AgentInterface':
        """创建 LangChain Agent"""
        if not self.initialized:
            raise RuntimeError("LangChain adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 转换配置
            langchain_config = self.translator.translate_agent_config(agent_config)
            
            # 优化配置
            optimized_config = self.optimizer.optimize_agent_creation(langchain_config)
            
            # 创建 LangChain Agent
            agent_type = optimized_config.pop('agent_type', 'zero-shot-react-description')
            
            # 获取 LLM
            llm = self._get_llm(optimized_config)
            
            # 获取工具
            tools = self._get_tools(optimized_config)
            
            # 获取记忆组件
            memory = self._get_memory(optimized_config)
            
            # 创建 Agent
            from langchain.agents import initialize_agent, AgentType
            
            # 映射 agent_type 到 AgentType
            agent_type_map = {
                'zero-shot-react-description': AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                'react-docstore': AgentType.REACT_DOCSTORE,
                'self-ask-with-search': AgentType.SELF_ASK_WITH_SEARCH,
                'conversational-react-description': AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                'chat-zero-shot-react-description': AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                'chat-conversational-react-description': AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                'structured-chat-zero-shot-react-description': AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
            }
            
            agent_type_enum = agent_type_map.get(agent_type, AgentType.ZERO_SHOT_REACT_DESCRIPTION)
            
            # 创建 Agent
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=agent_type_enum,
                memory=memory,
                verbose=optimized_config.get('verbose', False),
                handle_parsing_errors=optimized_config.get('handle_parsing_errors', True)
            )
            
            # 包装为统一接口
            wrapper = LangChainAgentWrapper(agent, agent_config)
            
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time)
            
            return wrapper
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('agent_creation', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to create LangChain agent: {e}")
            raise AdapterError(f"Failed to create LangChain agent: {e}", 'langchain')
            
    def create_task(self, task_config: dict) -> 'TaskInterface':
        """创建任务"""
        if not self.initialized:
            raise RuntimeError("LangChain adapter not initialized")
            
        # 转换配置
        langchain_task_config = self.translator.translate_task_config(task_config)
        
        # 创建任务对象
        return LangChainTaskWrapper(langchain_task_config, task_config)
        
    def execute_task(self, agent: 'AgentInterface', task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        if not self.initialized:
            raise RuntimeError("LangChain adapter not initialized")
            
        start_time = time.time()
        
        try:
            # 确保是 LangChain 智能体和任务
            if not isinstance(agent, LangChainAgentWrapper):
                raise TypeError("Agent must be a LangChainAgentWrapper instance")
                
            if not isinstance(task, LangChainTaskWrapper):
                raise TypeError("Task must be a LangChainTaskWrapper instance")
                
            # 获取原始 LangChain 智能体和任务配置
            langchain_agent = agent.agent
            task_config = task.langchain_config
            
            # 根据任务类型执行不同的操作
            task_type = task_config.get('type', 'query')
            
            if task_type == 'query':
                # 查询任务
                query = task_config.get('query', '')
                
                # 执行查询
                response = langchain_agent.run(query)
                
                # 创建结果
                result = LangChainResultWrapper(response, task)
                
            elif task_type == 'chain':
                # 链式任务
                inputs = task_config.get('inputs', {})
                
                # 执行链
                response = langchain_agent(inputs)
                
                # 创建结果
                result = LangChainResultWrapper(response, task)
                
            elif task_type == 'retrieval':
                # 检索任务
                query = task_config.get('query', '')
                
                # 如果 Agent 是检索 QA 链
                if hasattr(langchain_agent, 'retriever'):
                    # 直接执行检索 QA
                    response = langchain_agent({"query": query})
                else:
                    # 创建检索 QA 链
                    from langchain.chains import RetrievalQA
                    from langchain.vectorstores import VectorStore
                    
                    # 获取检索器
                    retriever = self._get_retriever(task_config)
                    
                    if retriever:
                        retrieval_qa = RetrievalQA.from_chain_type(
                            llm=self._get_llm(task_config),
                            chain_type="stuff",
                            retriever=retriever
                        )
                        response = retrieval_qa.run(query)
                    else:
                        # 如果没有检索器，使用普通查询
                        response = langchain_agent.run(query)
                
                # 创建结果
                result = LangChainResultWrapper(response, task)
                
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self.optimizer.collect_metrics('task_execution', start_time, end_time, {'error': str(e)})
            logger.error(f"Failed to execute task with LangChain agent: {e}")
            raise AdapterError(f"Failed to execute task: {e}", 'langchain')
            
    def _get_llm(self, config: dict) -> Any:
        """获取 LLM 实例"""
        llm_config = config.get('llm_config', {})
        llm_type = llm_config.get('type', 'openai')
        
        if llm_type == 'openai':
            from langchain.llms import OpenAI
            return OpenAI(
                temperature=llm_config.get('temperature', 0.7),
                model_name=llm_config.get('model', 'gpt-3.5-turbo'),
                openai_api_key=llm_config.get('api_key')
            )
        elif llm_type == 'chat_openai':
            from langchain.chat_models import ChatOpenAI
            return ChatOpenAI(
                temperature=llm_config.get('temperature', 0.7),
                model_name=llm_config.get('model', 'gpt-3.5-turbo'),
                openai_api_key=llm_config.get('api_key')
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
            
    def _get_tools(self, config: dict) -> List[Any]:
        """获取工具列表"""
        tools_config = config.get('tools_config', [])
        tools = []
        
        for tool_config in tools_config:
            tool_type = tool_config.get('type')
            
            if tool_type == 'serpapi':
                from langchain.tools import SerpAPIWrapper
                search = SerpAPIWrapper(serpapi_api_key=tool_config.get('api_key'))
                from langchain.agents import Tool
                tools.append(
                    Tool(
                        name="Search",
                        func=search.run,
                        description="Useful for searching the internet"
                    )
                )
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
                from langchain.agents import Tool
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
        
    def _get_memory(self, config: dict) -> Optional[Any]:
        """获取记忆组件"""
        memory_config = config.get('memory_config')
        
        if not memory_config:
            return None
            
        memory_type = memory_config.get('type', 'buffer')
        
        if memory_type == 'buffer':
            from langchain.memory import ConversationBufferMemory
            return ConversationBufferMemory(
                memory_key=memory_config.get('memory_key', 'chat_history'),
                return_messages=memory_config.get('return_messages', False)
            )
        elif memory_type == 'buffer_window':
            from langchain.memory import ConversationBufferWindowMemory
            return ConversationBufferWindowMemory(
                memory_key=memory_config.get('memory_key', 'chat_history'),
                k=memory_config.get('k', 5),
                return_messages=memory_config.get('return_messages', False)
            )
        elif memory_type == 'summary':
            from langchain.memory import ConversationSummaryMemory
            return ConversationSummaryMemory(
                llm=self._get_llm(config),
                memory_key=memory_config.get('memory_key', 'chat_history')
            )
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")
            
    def _get_retriever(self, config: dict) -> Optional[Any]:
        """获取检索器"""
        retrieval_config = config.get('retrieval_config')
        
        if not retrieval_config:
            return None
            
        retriever_type = retrieval_config.get('type', 'faiss')
        
        if retriever_type == 'faiss':
            # 需要预先创建的向量存储
            # 这里简化处理，实际应用中需要更复杂的逻辑
            return None
        elif retriever_type == 'chroma':
            # 需要预先创建的向量存储
            return None
        else:
            return None
```

### 3.3 智能体包装器

```python
class LangChainAgentWrapper(AgentInterface):
    """LangChain 智能体包装器，实现统一的 AgentInterface 接口"""
    
    def __init__(self, agent, config: dict):
        self.agent = agent  # 原始 LangChain 智能体
        self.config = config  # 原始配置
        self.id = str(uuid.uuid4())
        
    def get_id(self) -> str:
        """获取智能体 ID"""
        return self.id
        
    def get_name(self) -> str:
        """获取智能体名称"""
        return self.config.get('name', 'unnamed_agent')
        
    def get_description(self) -> str:
        """获取智能体描述"""
        return self.config.get('description', '')
        
    def get_capabilities(self) -> List[str]:
        """获取智能体能力"""
        # 根据智能体类型返回不同的能力
        capabilities = ['basic_conversation']
        
        # 检查是否有工具
        if hasattr(self.agent, 'tools') and self.agent.tools:
            capabilities.append('tool_use')
            
            # 检查特定工具类型
            tool_names = [tool.name for tool in self.agent.tools]
            if 'Search' in tool_names:
                capabilities.append('web_search')
            if 'Calculator' in tool_names:
                capabilities.append('calculation')
                
        # 检查是否有记忆组件
        if hasattr(self.agent, 'memory') and self.agent.memory:
            capabilities.append('memory_management')
            
        # 检查是否是检索 QA
        if hasattr(self.agent, 'retriever') or hasattr(self.agent, 'combine_documents_chain'):
            capabilities.append('retrieval_augmentation')
            
        return capabilities
        
    def execute_task(self, task: 'TaskInterface') -> 'ResultInterface':
        """执行任务"""
        # 获取适配器并执行任务
        from unified_agent.adapter.registry import AdapterRegistry
        
        registry = AdapterRegistry.get_instance()
        adapter = registry.get_adapter('langchain')
        
        if adapter is None:
            raise RuntimeError("LangChain adapter not found")
            
        return adapter.execute_task(self, task)
```

### 3.4 任务包装器

```python
class LangChainTaskWrapper(TaskInterface):
    """LangChain 任务包装器，实现统一的 TaskInterface 接口"""
    
    def __init__(self, langchain_config: dict, original_config: dict):
        self.langchain_config = langchain_config  # LangChain 特定配置
        self.original_config = original_config  # 原始配置
        self.id = str(uuid.uuid4())
        self.created_at = time.time()
        
    def get_id(self) -> str:
        """获取任务 ID"""
        return self.id
        
    def get_type(self) -> str:
        """获取任务类型"""
        return self.original_config.get('type', 'query')
        
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
class LangChainResultWrapper(ResultInterface):
    """LangChain 结果包装器，实现统一的 ResultInterface 接口"""
    
    def __init__(self, result, task: 'TaskInterface'):
        self.result = result  # 原始 LangChain 结果
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
        # 处理不同类型的结果
        if isinstance(self.result, dict) and 'output' in self.result:
            return self.result['output']
        elif isinstance(self.result, dict) and 'answer' in self.result:
            return self.result['answer']
        elif isinstance(self.result, str):
            return self.result
        else:
            return str(self.result)
        
    def get_created_time(self) -> float:
        """获取结果创建时间"""
        return self.created_at
        
    def is_success(self) -> bool:
        """检查任务是否成功"""
        # LangChain 没有明确的成功/失败标志
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
class LangChainConceptTranslator(ConceptTranslator):
    """LangChain 概念转换器，负责在统一模型和 LangChain 模型之间转换"""
    
    def __init__(self):
        super().__init__('unified', 'langchain')
        
    def translate_agent_config(self, config: dict) -> dict:
        """将统一的 Agent 配置转换为 LangChain 配置"""
        langchain_config = {}
        
        # 基本属性转换
        langchain_config['name'] = config.get('name', 'agent')
        
        # 确定 Agent 类型
        agent_type = config.get('agent_type', 'zero-shot-react-description').lower()
        langchain_config['agent_type'] = agent_type
        
        # 转换 LLM 配置
        if 'llm' in config:
            llm_config = self._translate_llm_config(config['llm'])
            langchain_config['llm_config'] = llm_config
            
        # 转换工具配置
        if 'tools' in config:
            tools_config = []
            for tool in config['tools']:
                tool_config = {
                    'type': tool.get('type'),
                    'name': tool.get('name'),
                    'description': tool.get('description'),
                    'api_key': tool.get('api_key')
                }
                tools_config.append(tool_config)
            langchain_config['tools_config'] = tools_config
            
        # 转换记忆配置
        if 'memory' in config:
            memory_config = {
                'type': config['memory'].get('type', 'buffer'),
                'memory_key': config['memory'].get('key', 'chat_history'),
                'return_messages': config['memory'].get('return_messages', False)
            }
            
            # 特定记忆类型的参数
            if memory_config['type'] == 'buffer_window':
                memory_config['k'] = config['memory'].get('window_size', 5)
                
            langchain_config['memory_config'] = memory_config
            
        # 其他配置
        langchain_config['verbose'] = config.get('verbose', False)
        langchain_config['handle_parsing_errors'] = config.get('handle_parsing_errors', True)
        
        return langchain_config
        
    def translate_task_config(self, config: dict) -> dict:
        """将统一的任务配置转换为 LangChain 任务配置"""
        langchain_config = {}
        
        # 基本属性转换
        task_type = config.get('type', 'query').lower()
        langchain_config['type'] = task_type
        
        if task_type == 'query':
            # 查询任务
            langchain_config['query'] = config.get('query', config.get('content', ''))
            
        elif task_type == 'chain':
            # 链式任务
            langchain_config['inputs'] = config.get('inputs', {})
            
        elif task_type == 'retrieval':
            # 检索任务
            langchain_config['query'] = config.get('query', config.get('content', ''))
            
            # 检索配置
            if 'retrieval' in config:
                retrieval_config = {
                    'type': config['retrieval'].get('type', 'faiss'),
                    'k': config['retrieval'].get('k', 4),
                    'search_type': config['retrieval'].get('search_type', 'similarity')
                }
                langchain_config['retrieval_config'] = retrieval_config
                
        return langchain_config
        
    def translate_result(self, result: Any) -> 'ResultInterface':
        """将 LangChain 结果转换为统一结果接口"""
        # 这个方法在 LangChainResultWrapper 中实现
        pass
        
    def _translate_llm_config(self, llm_config: dict) -> dict:
        """转换 LLM 配置"""
        langchain_llm_config = {}
        
        # 确定 LLM 类型
        model_type = llm_config.get('type', 'openai').lower()
        if model_type == 'chat':
            langchain_llm_config['type'] = 'chat_openai'
        else:
            langchain_llm_config['type'] = 'openai'
            
        # 模型名称
        if 'model' in llm_config:
            langchain_llm_config['model'] = llm_config['model']
            
        # 温度
        if 'temperature' in llm_config:
            langchain_llm_config['temperature'] = llm_config['temperature']
            
        # API 密钥
        if 'api_key' in llm_config:
            langchain_llm_config['api_key'] = llm_config['api_key']
            
        # 其他参数
        for key in ['max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']:
            if key in llm_config:
                langchain_llm_config[key] = llm_config[key]
                
        return langchain_llm_config
```

## 5. 性能优化

### 5.1 缓存优化

```python
class LangChainPerformanceOptimizer(PerformanceOptimizer):
    """LangChain 性能优化器"""
    
    def __init__(self, adapter: 'LangChainAdapter'):
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
            if key not in ['name', 'agent_type', 'llm_config', 'tools_config', 
                          'memory_config', 'verbose', 'handle_parsing_errors']:
                optimized_config.pop(key, None)
                
        # 优化 2: LLM 缓存
        if 'llm_config' in optimized_config:
            llm_config = optimized_config['llm_config']
            
            # 添加缓存配置
            if 'type' in llm_config and llm_config['type'] in ['openai', 'chat_openai']:
                # 在实际应用中，可以添加 LangChain 的缓存配置
                pass
                
        # 缓存优化后的配置
        self.config_cache.set(config_key, optimized_config)
        
        return optimized_config
        
    def optimize_task_execution(self, agent: 'AgentInterface', task: 'TaskInterface') -> tuple:
        """优化任务执行过程"""
        # 检查是否可以从缓存获取结果
        if isinstance(task, LangChainTaskWrapper):
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
        logger.debug(f"LangChain {operation} took {duration:.4f} seconds")
        
        # 如果操作时间过长，记录警告
        if operation == 'task_execution' and duration > 5.0:
            logger.warning(f"LangChain task execution took {duration:.4f} seconds, which is longer than expected")
            
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

# 获取 LangChain 适配器
langchain_adapter = registry.get_adapter('langchain')

# 创建 Agent
agent_config = {
    'name': 'research_assistant',
    'agent_type': 'zero-shot-react-description',
    'llm': {
        'type': 'chat',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.2
    },
    'tools': [
        {
            'type': 'serpapi',
            'name': 'Search',
            'description': 'Useful for searching the internet',
            'api_key': 'your-serpapi-key'
        },
        {
            'type': 'calculator',
            'name': 'Calculator',
            'description': 'Useful for calculations'
        }
    ],
    'memory': {
        'type': 'buffer',
        'key': 'chat_history',
        'return_messages': True
    },
    'verbose': True
}

agent = langchain_adapter.create_agent(agent_config)

# 创建查询任务
task_config = {
    'type': 'query',
    'query': 'What is the population of France and what is its GDP per capita?'
}

task = langchain_adapter.create_task(task_config)

# 执行任务
result = langchain_adapter.execute_task(agent, task)

# 获取结果
print(result.get_content())
```

### 6.2 检索增强生成

```python
# 创建检索增强 Agent
rag_agent_config = {
    'name': 'document_assistant',
    'agent_type': 'conversational-react-description',
    'llm': {
        'type': 'chat',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.2
    },
    'memory': {
        'type': 'buffer_window',
        'key': 'chat_history',
        'window_size': 5,
        'return_messages': True
    },
    'verbose': True
}

rag_agent = langchain_adapter.create_agent(rag_agent_config)

# 创建检索任务
retrieval_task_config = {
    'type': 'retrieval',
    'query': 'What are the key features of the product?',
    'retrieval': {
        'type': 'faiss',
        'k': 3,
        'search_type': 'similarity'
    }
}

retrieval_task = langchain_adapter.create_task(retrieval_task_config)

# 执行任务
result = langchain_adapter.execute_task(rag_agent, retrieval_task)

# 获取结果
print(result.get_content())
```

## 7. 错误处理

### 7.1 常见错误及处理

```python
class LangChainErrorHandler:
    @staticmethod
    def handle_initialization_error(error: Exception) -> str:
        """处理初始化错误"""
        if isinstance(error, ImportError):
            return "LangChain 框架未安装，请使用 'pip install langchain' 安装"
        return f"LangChain 适配器初始化失败: {error}"
        
    @staticmethod
    def handle_agent_creation_error(error: Exception, config: dict) -> str:
        """处理 Agent 创建错误"""
        if 'agent_type' in config:
            agent_type = config['agent_type']
            if agent_type not in ['zero-shot-react-description', 'react-docstore', 
                                 'self-ask-with-search', 'conversational-react-description',
                                 'chat-zero-shot-react-description', 
                                 'chat-conversational-react-description',
                                 'structured-chat-zero-shot-react-description']:
                return f"不支持的 Agent 类型: {agent_type}"
                
        if 'llm_config' in config and isinstance(error, KeyError):
            return f"LLM 配置错误: {error}"
            
        return f"创建 LangChain Agent 失败: {error}"
        
    @staticmethod
    def handle_task_execution_error(error: Exception, task_config: dict) -> str:
        """处理任务执行错误"""
        if 'type' in task_config:
            task_type = task_config['type']
            if task_type not in ['query', 'chain', 'retrieval']:
                return f"不支持的任务类型: {task_type}"
                
        return f"执行 LangChain 任务失败: {error}"
```

## 8. 测试

### 8.1 单元测试

```python
import unittest
from unittest.mock import MagicMock, patch

class TestLangChainAdapter(unittest.TestCase):
    def setUp(self):
        # 模拟 LangChain 模块
        self.langchain_mock = MagicMock()
        self.langchain_mock.agents = MagicMock()
        self.langchain_mock.agents.initialize_agent = MagicMock(return_value=MagicMock())
        self.langchain_mock.agents.AgentType = MagicMock()
        self.langchain_mock.agents.AgentType.ZERO_SHOT_REACT_DESCRIPTION = 'zero-shot-react-description'
        self.langchain_mock.llms = MagicMock()
        self.langchain_mock.llms.OpenAI = MagicMock(return_value=MagicMock())
        self.langchain_mock.chat_models = MagicMock()
        self.langchain_mock.chat_models.ChatOpenAI = MagicMock(return_value=MagicMock())
        self.langchain_mock.memory = MagicMock()
        self.langchain_mock.memory.ConversationBufferMemory = MagicMock(return_value=MagicMock())
        
        # 创建适配器
        with patch.dict('sys.modules', {'langchain': self.langchain_mock}):
            from unified_agent.adapter.langchain import LangChainAdapter
            self.adapter = LangChainAdapter()
            self.adapter.initialize()
            
    def test_initialize(self):
        self.assertTrue(self.adapter.initialized)
        
    def test_get_capabilities(self):
        capabilities = self.adapter.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertIn('agent_chains', capabilities)
        self.assertIn('tool_use', capabilities)
        
    def test_create_agent(self):
        config = {
            'name': 'test_agent',
            'agent_type': 'zero-shot-react-description',
            'llm': {
                'type': 'chat',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7
            },
            'tools': [
                {
                    'type': 'serpapi',
                    'name': 'Search',
                    'description': 'Useful for searching the internet'
                }
            ],
            'memory': {
                'type': 'buffer',
                'key': 'chat_history'
            },
            'verbose': True
        }
        
        agent = self.adapter.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get_name(), 'test_agent')
        
        # 验证 LangChain initialize_agent 被正确调用
        self.langchain_mock.agents.initialize_agent.assert_called_once()
        
    def test_create_and_execute_task(self):
        # 创建 Agent
        agent_config = {
            'name': 'test_agent',
            'agent_type': 'zero-shot-react-description',
            'llm': {
                'type': 'chat',
                'model': 'gpt-3.5-turbo'
            }
        }
        agent = self.adapter.create_agent(agent_config)
        
        # 创建任务
        task_config = {
            'type': 'query',
            'query': 'What is the capital of France?'
        }
        task = self.adapter.create_task(task_config)
        
        # 模拟 Agent 的 run 方法
        agent.agent.run = MagicMock(return_value="Paris is the capital of France.")
        
        # 执行任务
        result = self.adapter.execute_task(agent, task)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertTrue(result.is_success())
        self.assertEqual(result.get_content(), "Paris is the capital of France.")
        
        # 验证 run 方法被正确调用
        agent.agent.run.assert_called_once_with("What is the capital of France?")
```

## 9. 总结

LangChain 适配器实现了将 LangChain 框架的功能和特性映射到统一 Agent 框架的抽象接口。通过这个适配器，开发者可以使用统一的接口和概念模型来创建和管理 LangChain Agent，同时保留 LangChain 框架的强大功能，如链式处理、记忆管理、工具使用和检索增强生成等。

适配器的设计遵循了模块化、可扩展性和性能优先的原则，提供了完整的生命周期管理、错误处理和性能优化功能。通过概念转换器，适配器实现了统一模型和 LangChain 模型之间的无缝转换，使开发者能够轻松地在不同框架之间切换。

LangChain 适配器特别适合需要复杂链式处理、记忆管理和检索增强生成的应用场景，为开发者提供了强大而灵活的工具。