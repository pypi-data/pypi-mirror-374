# 业务抽象层设计 - 处理框架差异性

## 🎯 设计原则

业务抽象层需要在**通用性**和**框架特异性**之间找到平衡。

## 🏗️ 分层设计

### 1. 核心业务抽象 (Core Business Abstractions)
**位置**: `layers/business/core/`

**特点**: 
- 所有框架都支持的基础概念
- 最小公约数原则
- 保证跨框架兼容性

**包含**:
```
core/
├── agent_manager.py      # Agent管理 (所有框架都有)
├── task_scheduler.py     # 任务调度 (通用概念)
├── result_aggregator.py  # 结果聚合 (通用功能)
└── execution_context.py  # 执行上下文 (通用)
```

### 2. 扩展业务功能 (Extended Business Features)
**位置**: `layers/business/extensions/`

**特点**:
- 框架特定的高级功能
- 可选性组件
- 按需加载

**包含**:
```
extensions/
├── team_collaboration/   # 团队协作 (AutoGen, CrewAI支持)
│   ├── multi_agent.py
│   ├── communication.py
│   └── consensus.py
├── workflow_orchestration/ # 工作流编排 (LangGraph特长)
│   ├── graph_workflow.py
│   ├── state_machine.py
│   └── pipeline.py
├── tool_integration/     # 工具集成 (各框架差异很大)
│   ├── function_calling.py
│   ├── code_execution.py
│   └── external_apis.py
└── advanced_reasoning/   # 高级推理 (框架特定)
    ├── chain_of_thought.py
    ├── planning.py
    └── reflection.py
```

## 🔧 实现策略

### 1. 能力检测机制

```python
class BusinessCapability(Enum):
    """业务能力枚举"""
    BASIC_AGENT_MANAGEMENT = "basic_agent_management"  # 所有框架
    TASK_SCHEDULING = "task_scheduling"                # 所有框架
    RESULT_AGGREGATION = "result_aggregation"          # 所有框架
    
    # 扩展能力 - 框架特定
    MULTI_AGENT_COLLABORATION = "multi_agent_collaboration"  # AutoGen, CrewAI
    GRAPH_WORKFLOW = "graph_workflow"                         # LangGraph
    FUNCTION_CALLING = "function_calling"                     # OpenAI, AutoGen
    CODE_EXECUTION = "code_execution"                         # AutoGen
    SWARM_INTELLIGENCE = "swarm_intelligence"                 # AutoGen
```

### 2. 适配器能力声明

```python
# AutoGen适配器
class AutoGenAdapter(BaseAdapter):
    def get_business_capabilities(self) -> List[BusinessCapability]:
        return [
            BusinessCapability.BASIC_AGENT_MANAGEMENT,
            BusinessCapability.TASK_SCHEDULING,
            BusinessCapability.RESULT_AGGREGATION,
            BusinessCapability.MULTI_AGENT_COLLABORATION,  # ✅ 支持
            BusinessCapability.FUNCTION_CALLING,           # ✅ 支持
            BusinessCapability.CODE_EXECUTION,             # ✅ 支持
            BusinessCapability.SWARM_INTELLIGENCE,         # ✅ 支持
        ]

# OpenAI适配器
class OpenAIAdapter(BaseAdapter):
    def get_business_capabilities(self) -> List[BusinessCapability]:
        return [
            BusinessCapability.BASIC_AGENT_MANAGEMENT,
            BusinessCapability.TASK_SCHEDULING,
            BusinessCapability.RESULT_AGGREGATION,
            BusinessCapability.FUNCTION_CALLING,           # ✅ 支持
            # 注意：不支持团队协作
        ]
```

### 3. 动态业务层构建

```python
class BusinessLayerFactory:
    """业务层工厂 - 根据适配器能力动态构建"""
    
    def create_business_layer(self, adapter: BaseAdapter) -> BusinessLayer:
        capabilities = adapter.get_business_capabilities()
        
        # 核心组件 - 总是包含
        core_components = [
            AgentManager(adapter),
            TaskScheduler(adapter),
            ResultAggregator(adapter),
        ]
        
        # 扩展组件 - 按需添加
        extensions = []
        
        if BusinessCapability.MULTI_AGENT_COLLABORATION in capabilities:
            extensions.append(TeamCollaborationManager(adapter))
            
        if BusinessCapability.GRAPH_WORKFLOW in capabilities:
            extensions.append(WorkflowOrchestrator(adapter))
            
        if BusinessCapability.FUNCTION_CALLING in capabilities:
            extensions.append(ToolIntegrationManager(adapter))
        
        return BusinessLayer(core_components, extensions)
```

## 🎯 具体实现示例

### Team概念的处理

```python
# 核心业务层 - 最小化团队概念
class BasicAgentGroup:
    """基础Agent组 - 所有框架都支持"""
    def __init__(self, agents: List[UniversalAgent]):
        self.agents = agents
    
    async def execute_sequential(self, task: UniversalTask) -> UniversalResult:
        """顺序执行 - 所有框架都能实现"""
        results = []
        for agent in self.agents:
            result = await agent.execute(task, context)
            results.append(result)
        return self.aggregate_results(results)

# 扩展业务层 - 框架特定
class AdvancedTeamCollaboration:
    """高级团队协作 - 只有支持的框架才有"""
    def __init__(self, adapter: BaseAdapter):
        if not self.adapter.has_capability(BusinessCapability.MULTI_AGENT_COLLABORATION):
            raise UnsupportedOperationError("Framework doesn't support team collaboration")
    
    async def execute_round_robin(self, task: UniversalTask) -> UniversalResult:
        """轮询执行 - AutoGen特有"""
        # 实现AutoGen的RoundRobin逻辑
        pass
    
    async def execute_swarm(self, task: UniversalTask) -> UniversalResult:
        """群体智能 - AutoGen特有"""
        # 实现AutoGen的Swarm逻辑
        pass
```

## 🚀 优势

### 1. **渐进式增强**
- 基础功能：所有框架都能用
- 高级功能：有能力的框架才提供

### 2. **框架公平性**
- 不强制所有框架实现不支持的功能
- 每个框架都能发挥自己的优势

### 3. **用户友好**
```python
# 用户代码 - 自动适配
business_layer = BusinessLayerFactory.create(adapter)

# 基础功能 - 总是可用
agent_manager = business_layer.get_agent_manager()
task_scheduler = business_layer.get_task_scheduler()

# 高级功能 - 按需使用
if business_layer.supports(BusinessCapability.MULTI_AGENT_COLLABORATION):
    team_manager = business_layer.get_team_manager()
    result = await team_manager.execute_collaboration(task)
else:
    # 降级到基础功能
    result = await agent_manager.execute_sequential(task)
```

## 📋 实施计划

### 阶段1: 重构现有业务层
1. 将现有的team.py拆分为core和extension
2. 创建能力检测机制
3. 实现动态业务层构建

### 阶段2: 适配器能力声明
1. 为每个适配器添加能力声明
2. 实现能力检测和验证
3. 创建降级策略

### 阶段3: 用户接口优化
1. 提供统一的业务层接口
2. 自动能力检测和功能启用
3. 优雅的功能降级

## 🎯 结论

这种设计既保证了**通用性**（核心功能），又保留了**框架特异性**（扩展功能），是一个更加合理和可扩展的架构。

你觉得这个方案怎么样？我们可以先从重构现有的team.py开始实施。 