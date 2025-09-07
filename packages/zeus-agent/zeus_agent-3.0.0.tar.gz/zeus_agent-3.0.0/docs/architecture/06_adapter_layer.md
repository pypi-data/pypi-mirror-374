# 04. 适配器层 (Adapter Layer)

> **多框架统一的桥梁 - 将不同AI框架适配到统一抽象接口**

## 🎯 层级概述

适配器层是Agent Development Center实现**框架无关性**的关键层级。它将各种主流AI Agent框架（AutoGen、OpenAI、LangGraph、CrewAI等）的特定概念和接口转换为我们的统一抽象，使上层应用可以透明地切换底层框架。

### 核心职责
1. **🔄 框架转换**: 将不同框架的概念映射到统一抽象
2. **⚡ 能力适配**: 适配不同框架的能力和特性
3. **🔌 接口统一**: 提供一致的调用接口
4. **🛠️ 扩展支持**: 支持新框架的快速接入
5. **📊 性能优化**: 针对不同框架进行性能优化

### 设计理念
- **透明切换**: 上层应用无感知的框架切换
- **能力映射**: 智能映射不同框架的能力
- **性能优先**: 充分利用各框架的性能特点
- **扩展友好**: 新框架可快速接入

---

## 🏗️ 适配器架构设计

### 适配器层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    框架抽象层 (上层)                          │
│   UniversalAgent │ UniversalTask │ UniversalContext │ ...   │
└─────────────────────────────────────────────────────────────┘
                              │
                    统一适配器接口
                              │
┌─────────────────────────────────────────────────────────────┐
│                    适配器层 (Adapter Layer)                  │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│  │  AutoGen   │ │   OpenAI   │ │ LangGraph  │ │   CrewAI   │ │
│  │  Adapter   │ │  Adapter   │ │  Adapter   │ │  Adapter   │ │
│  │            │ │            │ │            │ │            │ │
│  │ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │
│  │ │Concept │ │ │ │Function│ │ │ │ State  │ │ │ │ Role   │ │ │
│  │ │Mapping │ │ │ │Calling │ │ │ │Machine │ │ │ │Mapping │ │ │
│  │ └────────┘ │ │ └────────┘ │ │ └────────┘ │ │ └────────┘ │ │
│  │ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │
│  │ │Message │ │ │ │Stream  │ │ │ │ Graph  │ │ │ │Process │ │ │
│  │ │Routing │ │ │ │Handling│ │ │ │Execution│ │ │ │Mgmt    │ │ │
│  │ └────────┘ │ │ └────────┘ │ │ └────────┘ │ │ └────────┘ │ │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    框架特定接口
                              │
┌─────────────────────────────────────────────────────────────┐
│                    底层框架 (具体实现)                        │
│    AutoGen     │     OpenAI     │   LangGraph   │   CrewAI   │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件关系

1. **BaseAdapter**: 所有适配器的基础接口
2. **FrameworkCapability**: 框架能力描述和映射
3. **ConceptTranslator**: 概念转换器
4. **AdapterRegistry**: 适配器注册和管理
5. **PerformanceOptimizer**: 性能优化器

---

## 🔧 基础适配器接口

### BaseAdapter 设计

**概念**: 所有框架适配器必须实现的统一接口

**作用**:
- 定义标准的适配器契约
- 确保接口一致性
- 支持多态调用
- 提供基础功能

**实现示例**:
```python
class BaseAdapter(ABC):
    """框架适配器基础接口"""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.framework_name = self.get_framework_name()
        self.capabilities = self.get_framework_capabilities()
        self.performance_optimizer = PerformanceOptimizer(self.framework_name)
        
    @abstractmethod
    def get_framework_name(self) -> str:
        """获取框架名称"""
        pass
    
    @abstractmethod
    def get_framework_capabilities(self) -> List[FrameworkCapability]:
        """获取框架支持的能力列表"""
        pass
    
    @abstractmethod
    async def translate_context(self, context: UniversalContext) -> Any:
        """将UniversalContext转换为目标框架的上下文格式"""
        pass
    
    @abstractmethod
    async def translate_task(self, task: UniversalTask) -> Any:
        """将UniversalTask转换为目标框架的任务格式"""
        pass
    
    @abstractmethod
    async def translate_result(self, framework_result: Any) -> UniversalResult:
        """将框架结果转换为UniversalResult"""
        pass
    
    @abstractmethod
    async def execute_task(self, 
                         task: UniversalTask, 
                         context: UniversalContext) -> UniversalResult:
        """执行任务 - 完整的适配流程"""
        pass
    
    async def validate_compatibility(self, task: UniversalTask) -> CompatibilityResult:
        """验证任务与框架的兼容性"""
        
        required_capabilities = task.get_required_capabilities()
        supported_capabilities = [cap.name for cap in self.capabilities]
        
        missing_capabilities = [
            cap for cap in required_capabilities 
            if cap not in supported_capabilities
        ]
        
        compatibility_score = (
            len(required_capabilities) - len(missing_capabilities)
        ) / len(required_capabilities) if required_capabilities else 1.0
        
        return CompatibilityResult(
            is_compatible=len(missing_capabilities) == 0,
            compatibility_score=compatibility_score,
            missing_capabilities=missing_capabilities,
            supported_capabilities=supported_capabilities,
            recommendations=self.generate_compatibility_recommendations(missing_capabilities)
        )
    
    async def optimize_for_task(self, task: UniversalTask) -> OptimizationConfig:
        """为特定任务优化适配器配置"""
        return await self.performance_optimizer.optimize(task, self.config)
```

### 能力映射系统

**概念**: 将不同框架的能力映射到统一的能力模型

**作用**:
- 统一能力描述标准
- 支持能力发现和匹配
- 实现能力等级评估
- 提供能力替代建议

**实现示例**:
```python
class CapabilityMapper:
    """能力映射器"""
    
    def __init__(self):
        self.capability_registry = CapabilityRegistry()
        self.mapping_rules = self.load_mapping_rules()
        
    async def map_framework_capabilities(self, 
                                       framework_name: str,
                                       native_capabilities: List[Any]) -> List[FrameworkCapability]:
        """映射框架原生能力到统一能力模型"""
        
        mapped_capabilities = []
        
        for native_cap in native_capabilities:
            # 查找映射规则
            mapping_rule = self.find_mapping_rule(framework_name, native_cap)
            
            if mapping_rule:
                # 应用映射规则
                universal_capability = await self.apply_mapping_rule(
                    native_capability=native_cap,
                    mapping_rule=mapping_rule
                )
                mapped_capabilities.append(universal_capability)
            else:
                # 创建新的映射规则
                new_mapping = await self.create_new_mapping(
                    framework_name=framework_name,
                    native_capability=native_cap
                )
                mapped_capabilities.append(new_mapping.universal_capability)
        
        return mapped_capabilities
    
    def find_mapping_rule(self, framework_name: str, native_capability: Any) -> MappingRule:
        """查找适用的映射规则"""
        
        for rule in self.mapping_rules:
            if (rule.framework_name == framework_name and 
                rule.matches_native_capability(native_capability)):
                return rule
        
        return None
    
    async def apply_mapping_rule(self, 
                               native_capability: Any, 
                               mapping_rule: MappingRule) -> FrameworkCapability:
        """应用映射规则"""
        
        return FrameworkCapability(
            name=mapping_rule.universal_name,
            description=mapping_rule.universal_description,
            capability_type=mapping_rule.capability_type,
            parameters=await mapping_rule.map_parameters(native_capability),
            constraints=await mapping_rule.map_constraints(native_capability),
            performance_metrics=await mapping_rule.estimate_performance(native_capability),
            native_capability=native_capability,
            framework_name=mapping_rule.framework_name
        )
```

---

## 🤖 AutoGen适配器

### 概念映射

**AutoGen核心概念**:
- `ConversableAgent`: 可对话的Agent
- `GroupChat`: 多Agent群聊
- `UserProxyAgent`: 用户代理Agent
- `AssistantAgent`: 助手Agent

**映射到统一抽象**:
- `ConversableAgent` → `UniversalAgent`
- `GroupChat` → `UniversalTeam` + `CommunicationManager`
- `Message` → `UniversalContext.ContextEntry`

### 实现示例

```python
class AutoGenAdapter(BaseAdapter):
    """AutoGen框架适配器"""
    
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.autogen_config = self.load_autogen_config()
        self.agent_registry = AutoGenAgentRegistry()
        self.group_chat_manager = GroupChatManager()
        
    def get_framework_name(self) -> str:
        return "AutoGen"
    
    def get_framework_capabilities(self) -> List[FrameworkCapability]:
        return [
            FrameworkCapability(
                name="multi_agent_conversation",
                description="Multi-agent conversational workflow",
                capability_type=CapabilityType.COLLABORATION,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="code_execution",
                description="Code execution with user proxy",
                capability_type=CapabilityType.TOOL_EXECUTION,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="human_in_loop",
                description="Human-in-the-loop interaction",
                capability_type=CapabilityType.HUMAN_INTERACTION,
                performance_level=PerformanceLevel.HIGH
            )
        ]
    
    async def translate_context(self, context: UniversalContext) -> List[Dict[str, Any]]:
        """将UniversalContext转换为AutoGen消息格式"""
        
        messages = []
        
        for entry in context.entries:
            if entry.key.startswith("message_"):
                # 转换为AutoGen消息格式
                autogen_message = {
                    "role": entry.metadata.get("role", "user"),
                    "content": entry.content,
                    "name": entry.metadata.get("sender_name", "user")
                }
                
                # 添加AutoGen特有字段
                if "tool_calls" in entry.metadata:
                    autogen_message["tool_calls"] = entry.metadata["tool_calls"]
                
                if "function_call" in entry.metadata:
                    autogen_message["function_call"] = entry.metadata["function_call"]
                
                messages.append(autogen_message)
        
        return messages
    
    async def translate_task(self, task: UniversalTask) -> AutoGenTaskConfig:
        """将UniversalTask转换为AutoGen任务配置"""
        
        # 分析任务类型
        if task.task_type == TaskType.MULTI_AGENT_COLLABORATION:
            return await self.create_group_chat_config(task)
        elif task.task_type == TaskType.CODE_GENERATION:
            return await self.create_code_gen_config(task)
        else:
            return await self.create_single_agent_config(task)
    
    async def create_group_chat_config(self, task: UniversalTask) -> AutoGenTaskConfig:
        """创建群聊任务配置"""
        
        # 分析需要的Agent角色
        required_roles = await self.analyze_required_roles(task)
        
        # 创建AutoGen Agents
        agents = []
        for role in required_roles:
            agent_config = {
                "name": role.name,
                "system_message": role.system_message,
                "llm_config": self.get_llm_config_for_role(role),
                "human_input_mode": role.human_input_mode,
                "max_consecutive_auto_reply": role.max_auto_reply
            }
            
            if role.type == "assistant":
                agent = autogen.AssistantAgent(**agent_config)
            elif role.type == "user_proxy":
                agent = autogen.UserProxyAgent(**agent_config)
            else:
                agent = autogen.ConversableAgent(**agent_config)
            
            agents.append(agent)
        
        # 创建GroupChat
        group_chat = autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=task.metadata.get("max_rounds", 10),
            speaker_selection_method=task.metadata.get("selection_method", "auto")
        )
        
        # 创建GroupChatManager
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=self.get_manager_llm_config()
        )
        
        return AutoGenTaskConfig(
            task_type="group_chat",
            agents=agents,
            group_chat=group_chat,
            manager=manager,
            initial_message=task.content
        )
    
    async def execute_task(self, 
                         task: UniversalTask, 
                         context: UniversalContext) -> UniversalResult:
        """执行AutoGen任务"""
        
        try:
            # 转换任务配置
            autogen_config = await self.translate_task(task)
            
            # 转换上下文
            messages = await self.translate_context(context)
            
            # 执行任务
            if autogen_config.task_type == "group_chat":
                result = await self.execute_group_chat(autogen_config, messages)
            else:
                result = await self.execute_single_agent(autogen_config, messages)
            
            # 转换结果
            return await self.translate_result(result)
            
        except Exception as e:
            return UniversalResult(
                content=f"AutoGen execution error: {str(e)}",
                status=ResultStatus.FAILURE,
                metadata={"error_type": type(e).__name__, "framework": "AutoGen"}
            )
    
    async def execute_group_chat(self, 
                               config: AutoGenTaskConfig, 
                               messages: List[Dict]) -> AutoGenResult:
        """执行群聊任务"""
        
        # 设置初始消息历史
        if messages:
            config.group_chat.messages = messages
        
        # 启动群聊
        chat_result = await config.manager.a_initiate_chat(
            config.group_chat,
            message=config.initial_message,
            clear_history=len(messages) == 0
        )
        
        return AutoGenResult(
            messages=config.group_chat.messages,
            final_message=chat_result.summary if hasattr(chat_result, 'summary') else None,
            participants=[agent.name for agent in config.agents],
            total_rounds=len(config.group_chat.messages),
            execution_metadata={
                "chat_terminated": chat_result.chat_terminated,
                "termination_reason": getattr(chat_result, 'termination_reason', None)
            }
        )
```

---

## 🔗 OpenAI适配器

### 概念映射

**OpenAI核心概念**:
- `ChatCompletion`: 聊天完成API
- `Function Calling`: 函数调用
- `Assistant API`: 助手API
- `Tools`: 工具集成

**映射到统一抽象**:
- `ChatCompletion` → `UniversalAgent.execute()`
- `Function` → `AgentCapability`
- `Assistant` → `UniversalAgent`
- `Thread` → `UniversalContext`

### 实现示例

```python
class OpenAIAdapter(BaseAdapter):
    """OpenAI框架适配器"""
    
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=config.api_key)
        self.function_registry = FunctionRegistry()
        self.assistant_manager = AssistantManager()
        
    def get_framework_name(self) -> str:
        return "OpenAI"
    
    def get_framework_capabilities(self) -> List[FrameworkCapability]:
        return [
            FrameworkCapability(
                name="function_calling",
                description="Advanced function calling with JSON schema",
                capability_type=CapabilityType.TOOL_EXECUTION,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="streaming_response",
                description="Real-time streaming responses",
                capability_type=CapabilityType.STREAMING,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="vision_understanding",
                description="Image and visual content understanding",
                capability_type=CapabilityType.MULTIMODAL,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="code_interpreter",
                description="Built-in code execution environment",
                capability_type=CapabilityType.CODE_EXECUTION,
                performance_level=PerformanceLevel.MEDIUM
            )
        ]
    
    async def translate_capabilities_to_functions(self, 
                                                capabilities: List[AgentCapability]) -> List[Dict]:
        """将Agent能力转换为OpenAI Function定义"""
        
        functions = []
        
        for capability in capabilities:
            if capability == AgentCapability.WEB_SEARCH:
                functions.append({
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for current information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string", 
                                    "description": "Search query string"
                                },
                                "max_results": {
                                    "type": "integer", 
                                    "default": 5,
                                    "description": "Maximum number of results to return"
                                },
                                "time_range": {
                                    "type": "string",
                                    "enum": ["day", "week", "month", "year", "all"],
                                    "default": "all",
                                    "description": "Time range for search results"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                })
            
            elif capability == AgentCapability.CODE_EXECUTION:
                functions.append({
                    "type": "function",
                    "function": {
                        "name": "execute_code",
                        "description": "Execute Python code in a secure environment",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "Python code to execute"
                                },
                                "timeout": {
                                    "type": "integer",
                                    "default": 30,
                                    "description": "Execution timeout in seconds"
                                },
                                "environment": {
                                    "type": "string",
                                    "enum": ["python3", "jupyter"],
                                    "default": "python3",
                                    "description": "Execution environment"
                                }
                            },
                            "required": ["code"]
                        }
                    }
                })
            
            elif capability == AgentCapability.FILE_OPERATIONS:
                functions.append({
                    "type": "function",
                    "function": {
                        "name": "file_operations",
                        "description": "Perform file system operations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "enum": ["read", "write", "list", "delete", "create_dir"],
                                    "description": "File operation to perform"
                                },
                                "path": {
                                    "type": "string",
                                    "description": "File or directory path"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Content for write operations"
                                }
                            },
                            "required": ["operation", "path"]
                        }
                    }
                })
        
        return functions
    
    async def execute_with_function_calling(self, 
                                          messages: List[Dict], 
                                          functions: List[Dict],
                                          stream: bool = False) -> UniversalResult:
        """使用Function Calling执行任务"""
        
        try:
            # 构建请求参数
            request_params = {
                "model": self.config.model or "gpt-4o",
                "messages": messages,
                "tools": functions,
                "tool_choice": "auto" if functions else None,
                "stream": stream,
                "temperature": self.config.temperature or 0.7,
                "max_tokens": self.config.max_tokens
            }
            
            # 执行请求
            if stream:
                return await self.execute_streaming_request(request_params)
            else:
                return await self.execute_standard_request(request_params)
                
        except Exception as e:
            return UniversalResult(
                content=f"OpenAI API error: {str(e)}",
                status=ResultStatus.FAILURE,
                metadata={"error_type": type(e).__name__, "framework": "OpenAI"}
            )
    
    async def execute_standard_request(self, params: Dict) -> UniversalResult:
        """执行标准请求"""
        
        response = await self.client.chat.completions.create(**params)
        
        # 处理函数调用
        message = response.choices[0].message
        function_results = []
        
        if message.tool_calls:
            # 执行函数调用
            for tool_call in message.tool_calls:
                function_result = await self.execute_function_call(tool_call)
                function_results.append(function_result)
                
                # 添加函数结果到消息历史
                params["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result.result)
                })
            
            # 获取最终响应
            final_response = await self.client.chat.completions.create(**params)
            final_message = final_response.choices[0].message
        else:
            final_message = message
            final_response = response
        
        return UniversalResult(
            content=final_message.content,
            status=ResultStatus.SUCCESS,
            metadata={
                "model": final_response.model,
                "tokens_used": final_response.usage.total_tokens,
                "function_calls": len(function_results),
                "function_results": [fr.to_dict() for fr in function_results],
                "finish_reason": final_response.choices[0].finish_reason
            }
        )
    
    async def execute_function_call(self, tool_call) -> FunctionResult:
        """执行函数调用"""
        
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # 查找并执行函数
        function_handler = self.function_registry.get_handler(function_name)
        
        if function_handler:
            result = await function_handler.execute(function_args)
            return FunctionResult(
                function_name=function_name,
                arguments=function_args,
                result=result,
                success=True,
                execution_time=result.get("execution_time", 0)
            )
        else:
            return FunctionResult(
                function_name=function_name,
                arguments=function_args,
                result={"error": f"Function {function_name} not found"},
                success=False,
                execution_time=0
            )
```

---

## 🕸️ LangGraph适配器

### 概念映射

**LangGraph核心概念**:
- `StateGraph`: 状态图工作流
- `Node`: 图中的节点
- `Edge`: 节点间的连接
- `State`: 图的状态

**映射到统一抽象**:
- `StateGraph` → `CognitiveAgent` 的认知流程
- `Node` → 认知模块的处理步骤
- `State` → `UniversalContext`
- `Edge` → 认知流程的控制逻辑

### 实现示例

```python
class LangGraphAdapter(BaseAdapter):
    """LangGraph框架适配器"""
    
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.graph_builder = GraphBuilder()
        self.state_manager = StateManager()
        self.node_registry = NodeRegistry()
        
    def get_framework_name(self) -> str:
        return "LangGraph"
    
    def get_framework_capabilities(self) -> List[FrameworkCapability]:
        return [
            FrameworkCapability(
                name="state_machine_workflow",
                description="Complex state machine based workflows",
                capability_type=CapabilityType.WORKFLOW,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="conditional_routing",
                description="Dynamic conditional flow routing",
                capability_type=CapabilityType.CONTROL_FLOW,
                performance_level=PerformanceLevel.HIGH
            ),
            FrameworkCapability(
                name="parallel_execution",
                description="Parallel node execution support",
                capability_type=CapabilityType.PARALLEL_PROCESSING,
                performance_level=PerformanceLevel.MEDIUM
            ),
            FrameworkCapability(
                name="checkpointing",
                description="State checkpointing and recovery",
                capability_type=CapabilityType.PERSISTENCE,
                performance_level=PerformanceLevel.MEDIUM
            )
        ]
    
    async def translate_context(self, context: UniversalContext) -> Dict[str, Any]:
        """将UniversalContext转换为LangGraph的State"""
        
        state = {
            "messages": [],
            "context_data": {},
            "intermediate_steps": [],
            "agent_scratchpad": "",
            "current_step": "start",
            "metadata": {}
        }
        
        # 转换上下文条目
        for entry in context.entries:
            if entry.key.startswith("message_"):
                state["messages"].append({
                    "role": entry.metadata.get("role", "user"),
                    "content": entry.content,
                    "timestamp": entry.timestamp,
                    "metadata": entry.metadata
                })
            elif entry.key.startswith("step_"):
                state["intermediate_steps"].append({
                    "step_id": entry.key,
                    "content": entry.content,
                    "metadata": entry.metadata
                })
            else:
                state["context_data"][entry.key] = entry.content
        
        # 添加全局元数据
        state["metadata"] = {
            "context_id": context.context_id,
            "created_at": context.created_at,
            "total_entries": len(context.entries)
        }
        
        return state
    
    async def create_cognitive_workflow_graph(self, 
                                            agent_config: Dict[str, Any]) -> StateGraph:
        """创建认知工作流图"""
        
        # 定义状态结构
        from langgraph import StateGraph
        from typing_extensions import TypedDict
        
        class AgentState(TypedDict):
            messages: List[Dict]
            context_data: Dict[str, Any]
            intermediate_steps: List[Dict]
            agent_scratchpad: str
            current_step: str
            perception_result: Dict
            reasoning_result: Dict
            action_plan: Dict
            execution_result: Dict
            metadata: Dict
        
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加认知节点
        workflow.add_node("perceive", self.perception_node)
        workflow.add_node("reason", self.reasoning_node)
        workflow.add_node("plan", self.planning_node)
        workflow.add_node("act", self.action_node)
        workflow.add_node("reflect", self.reflection_node)
        workflow.add_node("learn", self.learning_node)
        
        # 添加边和条件路由
        workflow.add_edge(START, "perceive")
        workflow.add_edge("perceive", "reason")
        
        # 条件路由：根据推理结果决定下一步
        workflow.add_conditional_edges(
            "reason",
            self.should_plan_or_act,
            {
                "plan": "plan",
                "act": "act",
                "reflect": "reflect"
            }
        )
        
        workflow.add_edge("plan", "act")
        workflow.add_edge("act", "reflect")
        
        # 反思后的条件路由
        workflow.add_conditional_edges(
            "reflect",
            self.should_continue_or_end,
            {
                "reason": "reason",
                "learn": "learn",
                "end": END
            }
        )
        
        workflow.add_edge("learn", END)
        
        return workflow.compile(checkpointer=self.create_checkpointer())
    
    async def perception_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """感知节点"""
        
        # 获取最新消息
        latest_message = state["messages"][-1] if state["messages"] else None
        
        if latest_message:
            # 执行多模态感知
            perception_engine = PerceptionEngine()
            perception_result = await perception_engine.perceive(
                input_data=latest_message["content"],
                context=state["context_data"]
            )
            
            # 更新状态
            state["perception_result"] = {
                "input_analysis": perception_result.input_analysis,
                "intent": perception_result.intent,
                "entities": perception_result.entities,
                "confidence": perception_result.confidence
            }
            
            state["current_step"] = "perception_complete"
            state["agent_scratchpad"] += f"感知结果: {perception_result.summary}\n"
        
        return state
    
    async def reasoning_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """推理节点"""
        
        reasoning_engine = ReasoningEngine()
        
        # 基于感知结果进行推理
        reasoning_result = await reasoning_engine.reason(
            perception_input=state.get("perception_result", {}),
            context=state["context_data"],
            previous_steps=state["intermediate_steps"]
        )
        
        # 更新状态
        state["reasoning_result"] = {
            "reasoning_type": reasoning_result.reasoning_type,
            "conclusion": reasoning_result.conclusion,
            "confidence": reasoning_result.confidence,
            "reasoning_chain": reasoning_result.reasoning_chain
        }
        
        state["current_step"] = "reasoning_complete"
        state["agent_scratchpad"] += f"推理结果: {reasoning_result.conclusion}\n"
        
        return state
    
    def should_plan_or_act(self, state: Dict[str, Any]) -> str:
        """决定是否需要制定计划"""
        
        reasoning_result = state.get("reasoning_result", {})
        
        # 如果推理结果表明需要复杂行动，则先制定计划
        if reasoning_result.get("complexity", "simple") == "complex":
            return "plan"
        elif reasoning_result.get("confidence", 0) < 0.7:
            return "reflect"
        else:
            return "act"
    
    def should_continue_or_end(self, state: Dict[str, Any]) -> str:
        """决定是否继续或结束"""
        
        reflection_result = state.get("reflection_result", {})
        
        if reflection_result.get("should_retry", False):
            return "reason"
        elif reflection_result.get("needs_learning", False):
            return "learn"
        else:
            return "end"
    
    async def execute_task(self, 
                         task: UniversalTask, 
                         context: UniversalContext) -> UniversalResult:
        """执行LangGraph任务"""
        
        try:
            # 创建工作流图
            workflow_graph = await self.create_cognitive_workflow_graph({
                "task_type": task.task_type,
                "complexity": task.metadata.get("complexity", "medium")
            })
            
            # 转换初始状态
            initial_state = await self.translate_context(context)
            initial_state["task"] = {
                "content": task.content,
                "type": task.task_type.value,
                "goal": task.goal
            }
            
            # 执行工作流
            final_state = await workflow_graph.ainvoke(initial_state)
            
            # 转换结果
            return await self.translate_result(final_state)
            
        except Exception as e:
            return UniversalResult(
                content=f"LangGraph execution error: {str(e)}",
                status=ResultStatus.FAILURE,
                metadata={"error_type": type(e).__name__, "framework": "LangGraph"}
            )
```

---

## 📊 适配器注册和管理

### AdapterRegistry

**概念**: 管理所有可用适配器的注册中心

**作用**:
- 适配器注册和发现
- 能力匹配和选择
- 负载均衡和故障转移
- 性能监控和优化

**实现示例**:
```python
class AdapterRegistry:
    """适配器注册中心"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseAdapter] = {}
        self.capability_index: Dict[str, List[str]] = {}
        self.performance_monitor = AdapterPerformanceMonitor()
        self.load_balancer = AdapterLoadBalancer()
        
    async def register_adapter(self, adapter: BaseAdapter):
        """注册适配器"""
        
        framework_name = adapter.get_framework_name()
        self.adapters[framework_name] = adapter
        
        # 索引能力
        capabilities = adapter.get_framework_capabilities()
        for capability in capabilities:
            if capability.name not in self.capability_index:
                self.capability_index[capability.name] = []
            self.capability_index[capability.name].append(framework_name)
        
        # 启动性能监控
        await self.performance_monitor.start_monitoring(adapter)
        
        print(f"Adapter {framework_name} registered successfully")
    
    async def select_best_adapter(self, 
                                task: UniversalTask,
                                selection_criteria: SelectionCriteria = None) -> AdapterSelection:
        """选择最佳适配器"""
        
        # 获取任务所需能力
        required_capabilities = task.get_required_capabilities()
        
        # 查找支持所需能力的适配器
        candidate_adapters = []
        
        for framework_name, adapter in self.adapters.items():
            compatibility = await adapter.validate_compatibility(task)
            
            if compatibility.is_compatible:
                candidate_adapters.append({
                    "adapter": adapter,
                    "framework_name": framework_name,
                    "compatibility_score": compatibility.compatibility_score,
                    "performance_metrics": await self.performance_monitor.get_metrics(framework_name)
                })
        
        if not candidate_adapters:
            raise NoCompatibleAdapterError(f"No adapter found for task type: {task.task_type}")
        
        # 应用选择策略
        if selection_criteria:
            best_adapter = await self.apply_selection_criteria(candidate_adapters, selection_criteria)
        else:
            # 默认选择策略：兼容性 + 性能
            best_adapter = max(candidate_adapters, key=lambda x: 
                x["compatibility_score"] * 0.6 + 
                x["performance_metrics"].average_score * 0.4
            )
        
        return AdapterSelection(
            adapter=best_adapter["adapter"],
            framework_name=best_adapter["framework_name"],
            selection_reason=f"Best match with score: {best_adapter['compatibility_score']:.2f}",
            alternatives=[c["framework_name"] for c in candidate_adapters if c != best_adapter]
        )
    
    async def execute_with_fallback(self,
                                  task: UniversalTask,
                                  context: UniversalContext,
                                  max_retries: int = 3) -> UniversalResult:
        """执行任务，支持故障转移"""
        
        adapter_selection = await self.select_best_adapter(task)
        
        for attempt in range(max_retries):
            try:
                # 尝试执行任务
                result = await adapter_selection.adapter.execute_task(task, context)
                
                # 记录成功执行
                await self.performance_monitor.record_success(
                    adapter_selection.framework_name, task, result
                )
                
                return result
                
            except Exception as e:
                # 记录失败
                await self.performance_monitor.record_failure(
                    adapter_selection.framework_name, task, e
                )
                
                if attempt < max_retries - 1:
                    # 选择备选适配器
                    if adapter_selection.alternatives:
                        fallback_name = adapter_selection.alternatives[attempt]
                        adapter_selection.adapter = self.adapters[fallback_name]
                        adapter_selection.framework_name = fallback_name
                        print(f"Falling back to {fallback_name} after error: {str(e)}")
                    else:
                        raise e
                else:
                    raise e
```

---

## 🎯 性能优化策略

### 框架特定优化

1. **AutoGen优化**:
   - 消息历史管理优化
   - Agent角色缓存
   - GroupChat性能调优

2. **OpenAI优化**:
   - Function Calling批量处理
   - 流式响应优化
   - Token使用优化

3. **LangGraph优化**:
   - 状态检查点优化
   - 节点执行并行化
   - 内存使用优化

### 通用优化策略

```python
class PerformanceOptimizer:
    """性能优化器"""
    
    async def optimize_for_framework(self, 
                                   framework_name: str, 
                                   task: UniversalTask) -> OptimizationConfig:
        """为特定框架优化配置"""
        
        if framework_name == "OpenAI":
            return await self.optimize_openai(task)
        elif framework_name == "AutoGen":
            return await self.optimize_autogen(task)
        elif framework_name == "LangGraph":
            return await self.optimize_langgraph(task)
        else:
            return await self.default_optimization(task)
    
    async def optimize_openai(self, task: UniversalTask) -> OptimizationConfig:
        """OpenAI特定优化"""
        
        config = OptimizationConfig()
        
        # 根据任务类型调整参数
        if task.task_type == TaskType.TEXT_GENERATION:
            config.temperature = 0.7
            config.max_tokens = 2000
        elif task.task_type == TaskType.CODE_GENERATION:
            config.temperature = 0.1
            config.max_tokens = 4000
        elif task.task_type == TaskType.ANALYSIS:
            config.temperature = 0.3
            config.max_tokens = 1500
        
        # 启用流式处理（如果支持）
        if task.metadata.get("streaming", False):
            config.stream = True
            config.chunk_size = 1024
        
        # Function calling优化
        if task.get_required_capabilities():
            config.parallel_function_calls = True
            config.function_call_timeout = 30
        
        return config
```

---

*适配器层文档 v1.0*  
*最后更新: 2024年12月19日*  
*文档编号: ADC-ARCH-04* 