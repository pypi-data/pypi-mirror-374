# 05. 框架抽象层 (Framework Abstraction Layer)

> **统一抽象的核心 - UniversalAgent、Task、Context、Result 和能力管理**

## 🎯 层级概述

框架抽象层是Agent Development Center的**抽象核心**，定义了框架无关的通用接口和数据模型。它是连接上层业务逻辑和下层具体实现的关键桥梁，确保整个系统具有高度的**灵活性和可扩展性**。

### 核心职责
1. **🎭 通用抽象**: 定义框架无关的Agent、任务、上下文抽象
2. **📊 数据模型**: 统一的数据结构和类型定义
3. **🔧 接口规范**: 标准化的接口和协议定义
4. **⚡ 能力管理**: 动态能力发现、注册、匹配机制
5. **🔄 生命周期**: Agent和任务的生命周期管理
6. **🔍 上下文工程**: 支持智能上下文管理和优化
7. **📦 任务分块**: 支持任务分解和复杂度评估

### 设计理念
- **最小抽象**: 保持接口的简洁性，避免过度抽象
- **强类型**: 使用强类型定义，提供编译时检查
- **扩展友好**: 为未来功能扩展预留接口
- **向后兼容**: 确保接口的向后兼容性
- **上下文感知**: 支持智能上下文管理和优化
- **任务优化**: 基于人类完成时间优化任务设计

---

## 🎭 UniversalAgent - 通用Agent抽象

> **所有Agent的统一接口 - 框架无关的Agent抽象基础**

### 概念和作用

UniversalAgent是所有Agent实现必须遵循的**核心抽象接口**，它定义了Agent的基本行为和能力，使得上层应用可以以统一的方式操作不同框架的Agent。

**核心作用**:
- **统一接口**: 为所有Agent提供一致的操作接口
- **能力声明**: 声明Agent具备的能力和特性
- **生命周期管理**: 管理Agent的创建、执行、销毁
- **状态维护**: 维护Agent的内部状态和上下文

### 核心设计

#### Agent身份和元数据
```python
@dataclass
class AgentIdentity:
    """Agent身份信息"""
    
    agent_id: str                    # 唯一标识符
    name: str                        # Agent名称
    version: str                     # Agent版本
    description: str                 # Agent描述
    
    # 分类信息
    agent_type: AgentType           # Agent类型
    role: str                       # Agent角色
    expertise_domains: List[str]    # 专业领域
    
    # 创建信息
    created_at: datetime            # 创建时间
    created_by: str                 # 创建者
    
    # 配置信息
    configuration: Dict[str, Any]   # Agent配置
    metadata: Dict[str, Any]        # 扩展元数据

class AgentType(Enum):
    """Agent类型枚举"""
    
    CONVERSATIONAL = "conversational"      # 对话型Agent
    TASK_ORIENTED = "task_oriented"        # 任务型Agent
    ANALYTICAL = "analytical"              # 分析型Agent
    CREATIVE = "creative"                  # 创意型Agent
    COLLABORATIVE = "collaborative"       # 协作型Agent
    SPECIALIZED = "specialized"           # 专业型Agent

class AgentStatus(Enum):
    """Agent状态枚举"""
    
    IDLE = "idle"                         # 空闲状态
    BUSY = "busy"                         # 忙碌状态
    PROCESSING = "processing"             # 处理中
    WAITING = "waiting"                   # 等待中
    ERROR = "error"                       # 错误状态
    OFFLINE = "offline"                   # 离线状态
```

#### 核心Agent接口
```python
class UniversalAgent(ABC):
    """通用Agent抽象接口"""
    
    def __init__(self, identity: AgentIdentity):
        self.identity = identity
        self.status = AgentStatus.IDLE
        self.capabilities: List[AgentCapability] = []
        self.performance_metrics = PerformanceMetrics()
        
    @abstractmethod
    async def execute(self, 
                     task: UniversalTask, 
                     context: UniversalContext) -> UniversalResult:
        """执行任务 - 所有Agent必须实现的核心方法"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """获取Agent能力列表 - 用于动态路由和匹配"""
        pass
    
    @abstractmethod
    async def validate_task(self, task: UniversalTask) -> TaskValidationResult:
        """验证任务是否可以执行"""
        pass
    
    # 可选实现的方法
    async def initialize(self) -> None:
        """初始化Agent - 可选实现"""
        self.status = AgentStatus.IDLE
        await self.load_capabilities()
        await self.setup_resources()
    
    async def shutdown(self) -> None:
        """关闭Agent - 可选实现"""
        await self.cleanup_resources()
        self.status = AgentStatus.OFFLINE
    
    async def get_status(self) -> AgentStatus:
        """获取Agent当前状态"""
        return self.status
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        return self.performance_metrics
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """更新Agent配置"""
        try:
            self.identity.configuration.update(config)
            await self.apply_configuration_changes()
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
```

#### Agent能力模型
```python
class AgentCapability(Enum):
    """Agent能力枚举"""
    
    # 基础能力
    TEXT_PROCESSING = "text_processing"
    IMAGE_UNDERSTANDING = "image_understanding"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_ANALYSIS = "video_analysis"
    
    # 工具能力
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATIONS = "file_operations"
    API_CALLING = "api_calling"
    DATABASE_ACCESS = "database_access"
    
    # 认知能力
    REASONING = "reasoning"
    PLANNING = "planning"
    LEARNING = "learning"
    MEMORY_MANAGEMENT = "memory_management"
    
    # 交互能力
    CONVERSATION = "conversation"
    COLLABORATION = "collaboration"
    HUMAN_INTERACTION = "human_interaction"
    
    # 专业能力
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"
    PROBLEM_SOLVING = "problem_solving"
    DECISION_MAKING = "decision_making"

@dataclass
class CapabilityDescription:
    """能力详细描述"""
    
    capability: AgentCapability      # 能力类型
    level: CapabilityLevel          # 能力等级
    confidence: float               # 能力置信度 (0-1)
    description: str                # 能力描述
    
    # 性能指标
    average_latency: float          # 平均延迟(秒)
    success_rate: float             # 成功率 (0-1)
    quality_score: float            # 质量评分 (0-1)
    
    # 约束条件
    max_input_size: Optional[int]   # 最大输入大小
    supported_formats: List[str]    # 支持的格式
    limitations: List[str]          # 限制条件
    
    # 元数据
    last_updated: datetime          # 最后更新时间
    benchmark_results: Dict[str, Any]  # 基准测试结果

class CapabilityLevel(Enum):
    """能力等级"""
    
    BASIC = "basic"                 # 基础级别
    INTERMEDIATE = "intermediate"   # 中级级别
    ADVANCED = "advanced"           # 高级级别
    EXPERT = "expert"               # 专家级别
```

### Agent实现示例

#### 基础Agent实现
```python
class BasicUniversalAgent(UniversalAgent):
    """基础通用Agent实现"""
    
    def __init__(self, identity: AgentIdentity, config: AgentConfig):
        super().__init__(identity)
        self.config = config
        self.execution_engine = ExecutionEngine()
        self.capability_manager = CapabilityManager()
        
    async def execute(self, 
                     task: UniversalTask, 
                     context: UniversalContext) -> UniversalResult:
        """执行任务的基础实现"""
        
        # 1. 任务验证
        validation_result = await self.validate_task(task)
        if not validation_result.is_valid:
            return UniversalResult(
                content=f"Task validation failed: {validation_result.error_message}",
                status=ResultStatus.VALIDATION_FAILED,
                metadata={"validation_errors": validation_result.errors}
            )
        
        # 2. 更新状态
        self.status = AgentStatus.PROCESSING
        
        try:
            # 3. 执行任务
            execution_result = await self.execution_engine.execute(
                agent=self,
                task=task,
                context=context
            )
            
            # 4. 更新性能指标
            await self.update_performance_metrics(task, execution_result)
            
            # 5. 返回结果
            self.status = AgentStatus.IDLE
            return execution_result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Task execution failed: {e}")
            
            return UniversalResult(
                content=f"Execution error: {str(e)}",
                status=ResultStatus.EXECUTION_FAILED,
                metadata={
                    "error_type": type(e).__name__,
                    "error_details": str(e),
                    "agent_id": self.identity.agent_id
                }
            )
    
    def get_capabilities(self) -> List[AgentCapability]:
        """获取Agent能力"""
        return self.capability_manager.get_available_capabilities()
    
    async def validate_task(self, task: UniversalTask) -> TaskValidationResult:
        """验证任务"""
        
        # 检查任务类型支持
        if not self.supports_task_type(task.task_type):
            return TaskValidationResult(
                is_valid=False,
                error_message=f"Unsupported task type: {task.task_type}",
                errors=["UNSUPPORTED_TASK_TYPE"]
            )
        
        # 检查所需能力
        required_capabilities = task.get_required_capabilities()
        available_capabilities = self.get_capabilities()
        
        missing_capabilities = [
            cap for cap in required_capabilities 
            if cap not in available_capabilities
        ]
        
        if missing_capabilities:
            return TaskValidationResult(
                is_valid=False,
                error_message=f"Missing capabilities: {missing_capabilities}",
                errors=["MISSING_CAPABILITIES"],
                missing_capabilities=missing_capabilities
            )
        
        # 检查资源限制
        resource_check = await self.check_resource_constraints(task)
        if not resource_check.sufficient:
            return TaskValidationResult(
                is_valid=False,
                error_message="Insufficient resources",
                errors=["INSUFFICIENT_RESOURCES"],
                resource_requirements=resource_check.requirements
            )
        
        return TaskValidationResult(is_valid=True)
```

---

## 📋 UniversalTask - 通用任务抽象

> **任务的统一表示 - 框架无关的任务定义和管理**

### 概念和作用

UniversalTask定义了所有任务的**统一数据结构**，它封装了任务的内容、类型、要求、约束等信息，使得不同的Agent可以以标准化的方式理解和处理任务。

**核心作用**:
- **任务标准化**: 提供统一的任务表示格式
- **需求声明**: 声明任务的能力需求和约束条件
- **元数据管理**: 管理任务的优先级、时限等元数据
- **生命周期跟踪**: 跟踪任务的执行状态和历史

### 核心设计

#### 任务基础结构
```python
@dataclass
class UniversalTask:
    """通用任务定义"""
    
    # 基础信息
    task_id: str                     # 任务唯一标识
    content: str                     # 任务内容描述
    task_type: TaskType             # 任务类型
    
    # 目标和要求
    goal: str                       # 任务目标
    requirements: TaskRequirements  # 任务要求
    constraints: List[TaskConstraint] # 约束条件
    
    # 优先级和时限
    priority: TaskPriority          # 任务优先级
    deadline: Optional[datetime]    # 截止时间
    estimated_duration: Optional[timedelta]  # 预估执行时间
    
    # 上下文和依赖
    parent_task_id: Optional[str]   # 父任务ID
    dependencies: List[str]         # 依赖任务ID列表
    context_requirements: List[str] # 上下文要求
    
    # 元数据
    created_at: datetime            # 创建时间
    created_by: str                 # 创建者
    tags: List[str]                 # 任务标签
    metadata: Dict[str, Any]        # 扩展元数据
    
    def get_required_capabilities(self) -> List[AgentCapability]:
        """获取任务所需的能力"""
        capability_mapping = {
            TaskType.TEXT_GENERATION: [AgentCapability.TEXT_PROCESSING],
            TaskType.CODE_GENERATION: [AgentCapability.CODE_EXECUTION],
            TaskType.DATA_ANALYSIS: [AgentCapability.DATA_ANALYSIS],
            TaskType.WEB_SEARCH: [AgentCapability.WEB_SEARCH],
            TaskType.IMAGE_ANALYSIS: [AgentCapability.IMAGE_UNDERSTANDING],
            TaskType.MULTI_AGENT_COLLABORATION: [AgentCapability.COLLABORATION],
        }
        
        base_capabilities = capability_mapping.get(self.task_type, [])
        
        # 添加需求中指定的能力
        if self.requirements.required_capabilities:
            base_capabilities.extend(self.requirements.required_capabilities)
        
        return list(set(base_capabilities))  # 去重
    
    def is_expired(self) -> bool:
        """检查任务是否过期"""
        if self.deadline:
            return datetime.now() > self.deadline
        return False
    
    def get_complexity_score(self) -> float:
        """计算任务复杂度评分"""
        score = 0.0
        
        # 基于任务类型的基础复杂度
        type_complexity = {
            TaskType.TEXT_GENERATION: 0.3,
            TaskType.CODE_GENERATION: 0.7,
            TaskType.DATA_ANALYSIS: 0.8,
            TaskType.MULTI_AGENT_COLLABORATION: 0.9,
            TaskType.CREATIVE_WRITING: 0.6,
            TaskType.PROBLEM_SOLVING: 0.8
        }
        
        score += type_complexity.get(self.task_type, 0.5)
        
        # 基于内容长度
        content_complexity = min(len(self.content) / 1000, 0.5)
        score += content_complexity
        
        # 基于约束数量
        constraint_complexity = len(self.constraints) * 0.1
        score += constraint_complexity
        
        # 基于依赖数量
        dependency_complexity = len(self.dependencies) * 0.1
        score += dependency_complexity
        
        return min(score, 1.0)  # 限制在0-1之间
    
    def get_human_completion_time(self) -> timedelta:
        """估算人类完成该任务所需时间（基于METR研究）"""
        
        # 基于复杂度的基础时间估算
        base_time_minutes = {
            TaskType.TEXT_GENERATION: 5,
            TaskType.CODE_GENERATION: 15,
            TaskType.DATA_ANALYSIS: 20,
            TaskType.MULTI_AGENT_COLLABORATION: 30,
            TaskType.CREATIVE_WRITING: 10,
            TaskType.PROBLEM_SOLVING: 25
        }
        
        base_minutes = base_time_minutes.get(self.task_type, 10)
        
        # 根据复杂度调整
        complexity_factor = self.get_complexity_score()
        adjusted_minutes = base_minutes * (1 + complexity_factor)
        
        # 限制在10-15分钟范围内（基于最佳实践）
        final_minutes = max(5, min(15, adjusted_minutes))
        
        return timedelta(minutes=final_minutes)
    
    def should_be_chunked(self) -> bool:
        """判断任务是否需要分块（基于10-15分钟原则）"""
        estimated_time = self.get_human_completion_time()
        return estimated_time.total_seconds() / 60 > 15  # 超过15分钟需要分块
    
    def get_chunking_strategy(self) -> TaskChunkingStrategy:
        """获取任务分块策略"""
        if not self.should_be_chunked():
            return TaskChunkingStrategy.NO_CHUNKING
        
        # 基于任务类型的分块策略
        chunking_strategies = {
            TaskType.DATA_ANALYSIS: TaskChunkingStrategy.SEQUENTIAL,
            TaskType.CODE_GENERATION: TaskChunkingStrategy.MODULAR,
            TaskType.CREATIVE_WRITING: TaskChunkingStrategy.ITERATIVE,
            TaskType.PROBLEM_SOLVING: TaskChunkingStrategy.HIERARCHICAL
        }
        
        return chunking_strategies.get(self.task_type, TaskChunkingStrategy.SEQUENTIAL)

class TaskChunkingStrategy(Enum):
    """任务分块策略枚举"""
    
    NO_CHUNKING = "no_chunking"           # 不需要分块
    SEQUENTIAL = "sequential"             # 顺序分块
    MODULAR = "modular"                   # 模块化分块
    ITERATIVE = "iterative"               # 迭代分块
    HIERARCHICAL = "hierarchical"         # 层次化分块
    PARALLEL = "parallel"                 # 并行分块

class ContextCompressionStrategy(Enum):
    """上下文压缩策略枚举"""
    
    NO_COMPRESSION = "no_compression"     # 不压缩
    SUMMARIZATION = "summarization"       # 摘要压缩
    SELECTION = "selection"               # 选择压缩
    TRIM = "trim"                         # 修剪压缩
    DEDUPLICATION = "deduplication"       # 去重压缩

class TaskType(Enum):
    """任务类型枚举"""
    
    # 基础任务类型
    TEXT_GENERATION = "text_generation"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_TRANSLATION = "text_translation"
    TEXT_CLASSIFICATION = "text_classification"
    
    # 代码相关
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_DEBUGGING = "code_debugging"
    CODE_OPTIMIZATION = "code_optimization"
    
    # 分析相关
    DATA_ANALYSIS = "data_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TREND_ANALYSIS = "trend_analysis"
    
    # 交互相关
    QUESTION_ANSWERING = "question_answering"
    CONVERSATION = "conversation"
    CONSULTATION = "consultation"
    
    # 创意相关
    CREATIVE_WRITING = "creative_writing"
    CONTENT_CREATION = "content_creation"
    BRAINSTORMING = "brainstorming"
    
    # 工具相关
    WEB_SEARCH = "web_search"
    FILE_OPERATIONS = "file_operations"
    API_INTEGRATION = "api_integration"
    
    # 协作相关
    MULTI_AGENT_COLLABORATION = "multi_agent_collaboration"
    TEAM_COORDINATION = "team_coordination"
    WORKFLOW_EXECUTION = "workflow_execution"
    
    # 专业任务
    PROBLEM_SOLVING = "problem_solving"
    DECISION_MAKING = "decision_making"
    PLANNING = "planning"

class TaskPriority(Enum):
    """任务优先级"""
    
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5

@dataclass
class TaskRequirements:
    """任务要求定义"""
    
    # 能力要求
    required_capabilities: List[AgentCapability]
    preferred_capabilities: List[AgentCapability]
    
    # 质量要求
    min_quality_score: float        # 最低质量要求
    accuracy_threshold: float       # 准确度阈值
    
    # 性能要求
    max_response_time: Optional[timedelta]  # 最大响应时间
    max_token_usage: Optional[int]  # 最大Token使用量
    
    # 格式要求
    output_format: str              # 输出格式要求
    language: str                   # 语言要求
    style: Optional[str]            # 风格要求
    
    # 安全要求
    security_level: SecurityLevel   # 安全等级
    data_sensitivity: DataSensitivity  # 数据敏感性

@dataclass
class TaskConstraint:
    """任务约束定义"""
    
    constraint_type: ConstraintType
    description: str
    value: Any
    is_hard_constraint: bool        # 是否为硬约束
    
class ConstraintType(Enum):
    """约束类型"""
    
    TIME_LIMIT = "time_limit"       # 时间限制
    RESOURCE_LIMIT = "resource_limit"  # 资源限制
    CONTENT_FILTER = "content_filter"  # 内容过滤
    FORMAT_REQUIREMENT = "format_requirement"  # 格式要求
    QUALITY_THRESHOLD = "quality_threshold"  # 质量阈值
    BUDGET_LIMIT = "budget_limit"   # 预算限制
```

### 任务生命周期管理

#### 任务状态跟踪
```python
class TaskStatus(Enum):
    """任务状态"""
    
    CREATED = "created"             # 已创建
    QUEUED = "queued"              # 队列中
    ASSIGNED = "assigned"          # 已分配
    IN_PROGRESS = "in_progress"    # 执行中
    PAUSED = "paused"              # 暂停
    COMPLETED = "completed"        # 已完成
    FAILED = "failed"              # 失败
    CANCELLED = "cancelled"        # 已取消
    EXPIRED = "expired"            # 已过期

@dataclass
class TaskExecution:
    """任务执行记录"""
    
    task: UniversalTask
    assigned_agent: Optional[str]   # 分配的Agent ID
    status: TaskStatus
    
    # 执行时间
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_duration: Optional[timedelta]
    
    # 执行结果
    result: Optional[UniversalResult]
    error_message: Optional[str]
    
    # 性能指标
    token_usage: Optional[int]
    cost: Optional[float]
    quality_score: Optional[float]
    
    # 执行历史
    status_history: List[TaskStatusChange]
    execution_log: List[ExecutionLogEntry]

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.task_registry = TaskRegistry()
        self.execution_tracker = ExecutionTracker()
        self.scheduler = TaskScheduler()
    
    async def create_task(self, task_definition: Dict[str, Any]) -> UniversalTask:
        """创建新任务"""
        
        task = UniversalTask(
            task_id=self.generate_task_id(),
            content=task_definition["content"],
            task_type=TaskType(task_definition["task_type"]),
            goal=task_definition.get("goal", ""),
            requirements=self.parse_requirements(task_definition.get("requirements", {})),
            constraints=self.parse_constraints(task_definition.get("constraints", [])),
            priority=TaskPriority(task_definition.get("priority", TaskPriority.MEDIUM)),
            created_at=datetime.now(),
            created_by=task_definition.get("created_by", "system"),
            tags=task_definition.get("tags", []),
            metadata=task_definition.get("metadata", {})
        )
        
        # 注册任务
        await self.task_registry.register_task(task)
        
        # 创建执行记录
        execution = TaskExecution(
            task=task,
            status=TaskStatus.CREATED,
            status_history=[TaskStatusChange(
                from_status=None,
                to_status=TaskStatus.CREATED,
                timestamp=datetime.now(),
                reason="Task created"
            )],
            execution_log=[]
        )
        
        await self.execution_tracker.track_execution(execution)
        
        return task
    
    async def assign_task(self, task_id: str, agent: UniversalAgent) -> bool:
        """分配任务给Agent"""
        
        task = await self.task_registry.get_task(task_id)
        if not task:
            return False
        
        # 验证Agent能力
        validation_result = await agent.validate_task(task)
        if not validation_result.is_valid:
            logger.warning(f"Agent {agent.identity.agent_id} cannot handle task {task_id}: {validation_result.error_message}")
            return False
        
        # 更新执行记录
        execution = await self.execution_tracker.get_execution(task_id)
        execution.assigned_agent = agent.identity.agent_id
        execution.status = TaskStatus.ASSIGNED
        
        await self.execution_tracker.update_execution(execution)
        
        return True
    
    async def execute_task(self, task_id: str) -> UniversalResult:
        """执行任务"""
        
        execution = await self.execution_tracker.get_execution(task_id)
        if not execution or not execution.assigned_agent:
            raise TaskExecutionError(f"Task {task_id} not properly assigned")
        
        # 获取Agent
        agent = await self.get_agent(execution.assigned_agent)
        
        # 更新状态
        execution.status = TaskStatus.IN_PROGRESS
        execution.started_at = datetime.now()
        await self.execution_tracker.update_execution(execution)
        
        try:
            # 执行任务
            context = await self.build_task_context(execution.task)
            result = await agent.execute(execution.task, context)
            
            # 更新执行结果
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.execution_duration = execution.completed_at - execution.started_at
            execution.result = result
            
            await self.execution_tracker.update_execution(execution)
            
            return result
            
        except Exception as e:
            # 处理执行失败
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            await self.execution_tracker.update_execution(execution)
            
            raise TaskExecutionError(f"Task execution failed: {str(e)}")
```

---

## 🗂️ UniversalContext - 通用上下文抽象

> **上下文的统一管理 - 任务执行的环境和状态**

### 概念和作用

UniversalContext管理任务执行过程中的**上下文信息**，包括历史记录、中间状态、共享数据等，为Agent提供执行任务所需的环境信息。

**核心作用**:
- **状态维护**: 维护任务执行的状态和历史
- **信息共享**: 在不同组件间共享上下文信息
- **会话管理**: 管理长期对话和交互历史
- **数据传递**: 在处理流程中传递中间数据
- **上下文工程**: 支持智能上下文管理和优化
- **质量监控**: 监控上下文质量和健康度

### 核心设计

```python
@dataclass
class ContextEntry:
    """上下文条目"""
    
    key: str                        # 条目键
    content: Any                    # 条目内容
    entry_type: ContextEntryType   # 条目类型
    timestamp: datetime             # 时间戳
    source: str                     # 来源
    metadata: Dict[str, Any]        # 元数据
    
    # 生命周期
    ttl: Optional[timedelta]        # 生存时间
    expires_at: Optional[datetime]  # 过期时间
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

class ContextEntryType(Enum):
    """上下文条目类型"""
    
    MESSAGE = "message"             # 消息
    STATE = "state"                 # 状态
    RESULT = "result"               # 结果
    METADATA = "metadata"           # 元数据
    MEMORY = "memory"               # 记忆
    TOOL_RESULT = "tool_result"     # 工具结果
    INSTRUCTION = "instruction"     # 指令
    KNOWLEDGE = "knowledge"         # 知识
    TOOL = "tool"                   # 工具

class UniversalContext:
    """通用上下文管理器"""
    
    def __init__(self, context_id: str = None):
        self.context_id = context_id or self.generate_context_id()
        self.entries: List[ContextEntry] = []
        self.shared_state: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # 索引和查找
        self.entry_index: Dict[str, List[ContextEntry]] = defaultdict(list)
        self.type_index: Dict[ContextEntryType, List[ContextEntry]] = defaultdict(list)
    
    def add_entry(self, entry: ContextEntry) -> None:
        """添加上下文条目"""
        
        self.entries.append(entry)
        self.entry_index[entry.key].append(entry)
        self.type_index[entry.entry_type].append(entry)
        self.last_updated = datetime.now()
        
        # 设置过期时间
        if entry.ttl:
            entry.expires_at = datetime.now() + entry.ttl
    
    def get_entries_by_key(self, key: str) -> List[ContextEntry]:
        """根据键获取条目"""
        return [entry for entry in self.entry_index[key] if not entry.is_expired()]
    
    def get_entries_by_type(self, entry_type: ContextEntryType) -> List[ContextEntry]:
        """根据类型获取条目"""
        return [entry for entry in self.type_index[entry_type] if not entry.is_expired()]
    
    def get_latest_entry(self, key: str) -> Optional[ContextEntry]:
        """获取最新的条目"""
        entries = self.get_entries_by_key(key)
        return max(entries, key=lambda x: x.timestamp) if entries else None
    
    def set_shared_state(self, key: str, value: Any) -> None:
        """设置共享状态"""
        self.shared_state[key] = value
        self.last_updated = datetime.now()
    
    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """获取共享状态"""
        return self.shared_state.get(key, default)
    
    def cleanup_expired_entries(self) -> int:
        """清理过期条目"""
        
        expired_count = 0
        
        # 清理主列表
        original_count = len(self.entries)
        self.entries = [entry for entry in self.entries if not entry.is_expired()]
        expired_count = original_count - len(self.entries)
        
        # 重建索引
        self.rebuild_indexes()
        
        return expired_count
    
    def rebuild_indexes(self) -> None:
        """重建索引"""
        
        self.entry_index.clear()
        self.type_index.clear()
        
        for entry in self.entries:
            if not entry.is_expired():
                self.entry_index[entry.key].append(entry)
                self.type_index[entry.entry_type].append(entry)
    
    def get_context_quality_score(self) -> float:
        """获取上下文质量评分"""
        score = 0.0
        
        # 基于条目数量的评分
        total_entries = len(self.entries)
        if total_entries == 0:
            return 0.0
        
        # 条目多样性评分
        unique_types = len(set(entry.entry_type for entry in self.entries))
        diversity_score = min(unique_types / 6, 1.0)  # 最多6种类型
        score += diversity_score * 0.3
        
        # 条目新鲜度评分
        recent_entries = [entry for entry in self.entries 
                         if (datetime.now() - entry.timestamp).total_seconds() < 3600]
        freshness_score = len(recent_entries) / total_entries
        score += freshness_score * 0.3
        
        # 条目相关性评分（基于键的语义相似性）
        relevance_score = self.calculate_relevance_score()
        score += relevance_score * 0.4
        
        return min(score, 1.0)
    
    def calculate_relevance_score(self) -> float:
        """计算上下文相关性评分"""
        if not self.entries:
            return 0.0
        
        # 简单的相关性计算（基于键的相似性）
        keys = [entry.key for entry in self.entries]
        unique_keys = len(set(keys))
        total_keys = len(keys)
        
        # 重复键越多，相关性越低
        if total_keys == 0:
            return 0.0
        
        return unique_keys / total_keys
    
    def should_be_compressed(self) -> bool:
        """判断上下文是否需要压缩"""
        total_entries = len(self.entries)
        return total_entries > 50  # 超过50个条目时压缩
    
    def get_compression_strategy(self) -> ContextCompressionStrategy:
        """获取上下文压缩策略"""
        if not self.should_be_compressed():
            return ContextCompressionStrategy.NO_COMPRESSION
        
        # 基于条目类型的压缩策略
        message_entries = len(self.get_entries_by_type(ContextEntryType.MESSAGE))
        result_entries = len(self.get_entries_by_type(ContextEntryType.RESULT))
        
        if message_entries > result_entries:
            return ContextCompressionStrategy.SUMMARIZATION
        else:
            return ContextCompressionStrategy.SELECTION
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "context_id": self.context_id,
            "entries": [
                {
                    "key": entry.key,
                    "content": entry.content,
                    "entry_type": entry.entry_type.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "source": entry.source,
                    "metadata": entry.metadata
                }
                for entry in self.entries if not entry.is_expired()
            ],
            "shared_state": self.shared_state,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
```

---

## 📊 UniversalResult - 通用结果抽象

> **结果的统一表示 - 标准化的执行结果和反馈**

### 概念和作用

UniversalResult定义了任务执行结果的**统一格式**，包含执行状态、输出内容、元数据等信息，为结果处理和分析提供标准化接口。

### 核心设计

```python
@dataclass
class UniversalResult:
    """通用结果定义"""
    
    # 基础信息
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""               # 主要输出内容
    status: ResultStatus = ResultStatus.SUCCESS
    
    # 结果类型和格式
    result_type: ResultType = ResultType.TEXT
    format: str = "text/plain"      # MIME类型
    
    # 质量和性能指标
    confidence: float = 1.0         # 结果置信度 (0-1)
    quality_score: float = 1.0      # 质量评分 (0-1)
    
    # 执行信息
    execution_time: Optional[float] = None  # 执行时间(秒)
    token_usage: Optional[int] = None       # Token使用量
    cost: Optional[float] = None            # 执行成本
    
    # 错误信息
    error_info: Optional[ErrorInfo] = None
    
    # 附加数据
    attachments: List[ResultAttachment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_successful(self) -> bool:
        """检查结果是否成功"""
        return self.status == ResultStatus.SUCCESS
    
    def has_error(self) -> bool:
        """检查是否有错误"""
        return self.error_info is not None
    
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.error_info.message if self.error_info else ""

class ResultStatus(Enum):
    """结果状态"""
    
    SUCCESS = "success"             # 成功
    PARTIAL_SUCCESS = "partial_success"  # 部分成功
    FAILURE = "failure"             # 失败
    ERROR = "error"                 # 错误
    TIMEOUT = "timeout"             # 超时
    CANCELLED = "cancelled"         # 取消
    VALIDATION_FAILED = "validation_failed"  # 验证失败
    EXECUTION_FAILED = "execution_failed"    # 执行失败

class ResultType(Enum):
    """结果类型"""
    
    TEXT = "text"                   # 文本结果
    JSON = "json"                   # JSON数据
    IMAGE = "image"                 # 图片
    AUDIO = "audio"                 # 音频
    VIDEO = "video"                 # 视频
    FILE = "file"                   # 文件
    STRUCTURED_DATA = "structured_data"  # 结构化数据

@dataclass
class ErrorInfo:
    """错误信息"""
    
    error_code: str                 # 错误代码
    message: str                    # 错误消息
    error_type: str                 # 错误类型
    stack_trace: Optional[str] = None  # 堆栈跟踪
    recovery_suggestions: List[str] = field(default_factory=list)  # 恢复建议

@dataclass
class ResultAttachment:
    """结果附件"""
    
    name: str                       # 附件名称
    content: bytes                  # 附件内容
    content_type: str               # 内容类型
    size: int                       # 大小(字节)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## ⚡ 能力管理系统

> **动态能力发现和匹配 - 智能的能力管理机制**

### 能力注册中心

```python
class CapabilityRegistry:
    """能力注册中心"""
    
    def __init__(self):
        self.capabilities: Dict[AgentCapability, List[CapabilityProvider]] = defaultdict(list)
        self.provider_index: Dict[str, CapabilityProvider] = {}
        self.performance_tracker = CapabilityPerformanceTracker()
    
    async def register_capability(self, 
                                provider_id: str,
                                capability: AgentCapability,
                                description: CapabilityDescription) -> bool:
        """注册能力提供者"""
        
        provider = CapabilityProvider(
            provider_id=provider_id,
            capability=capability,
            description=description,
            registered_at=datetime.now()
        )
        
        self.capabilities[capability].append(provider)
        self.provider_index[provider_id] = provider
        
        # 启动性能监控
        await self.performance_tracker.start_monitoring(provider)
        
        return True
    
    async def find_providers(self, 
                           capability: AgentCapability,
                           requirements: Optional[CapabilityRequirements] = None) -> List[CapabilityProvider]:
        """查找能力提供者"""
        
        providers = self.capabilities.get(capability, [])
        
        if requirements:
            # 根据要求过滤提供者
            filtered_providers = []
            
            for provider in providers:
                if await self.meets_requirements(provider, requirements):
                    filtered_providers.append(provider)
            
            providers = filtered_providers
        
        # 根据性能排序
        providers.sort(key=lambda p: self.performance_tracker.get_score(p.provider_id), reverse=True)
        
        return providers

class CapabilityMatcher:
    """能力匹配器"""
    
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        self.matching_algorithms = {
            MatchingStrategy.EXACT: self.exact_match,
            MatchingStrategy.FUZZY: self.fuzzy_match,
            MatchingStrategy.SEMANTIC: self.semantic_match
        }
    
    async def match_capabilities(self, 
                               required_capabilities: List[AgentCapability],
                               matching_strategy: MatchingStrategy = MatchingStrategy.EXACT) -> CapabilityMatchResult:
        """匹配能力"""
        
        matching_algorithm = self.matching_algorithms[matching_strategy]
        return await matching_algorithm(required_capabilities)
    
    async def exact_match(self, required_capabilities: List[AgentCapability]) -> CapabilityMatchResult:
        """精确匹配"""
        
        matches = {}
        unmatched = []
        
        for capability in required_capabilities:
            providers = await self.registry.find_providers(capability)
            
            if providers:
                matches[capability] = providers
            else:
                unmatched.append(capability)
        
        return CapabilityMatchResult(
            matches=matches,
            unmatched_capabilities=unmatched,
            match_score=len(matches) / len(required_capabilities) if required_capabilities else 1.0
        )
```

---

*框架抽象层文档 v2.0 - 上下文工程增强版本*  
*最后更新: 2024年12月19日*  
*文档编号: ADC-ARCH-05* 