# 执行引擎 (Execution Engine)

## 1. 概述

执行引擎（Execution Engine）是认知架构中负责将抽象计划转化为实际行动的组件。它接收来自规划器的具体行动计划（Plan），并负责调用相应的工具、API或内部函数来执行这些计划中的每一个步骤。执行引擎是Agent与外部世界（包括操作系统、网络服务、硬件设备等）进行交互的最终执行者，它确保了行动的可靠、安全和可控。

## 2. 设计目标

*   **可靠执行 (Reliable Execution)**: 确保计划中的每一步都能被准确无误地执行。具备错误处理和重试机制。
*   **工具调用 (Tool Calling)**: 提供一个统一的、与工具无关的接口来调用各种类型的工具（函数、API、命令行脚本等）。
*   **沙箱环境 (Sandboxing)**: 在一个受控的、安全的环境中执行代码或命令，防止恶意代码对宿主系统造成损害。
*   **异步与并发 (Asynchrony & Concurrency)**: 能够并发地执行多个独立的行动，并支持对长时间运行的异步任务进行管理。
*   **结果监控与反馈 (Result Monitoring & Feedback)**: 监控每个行动的执行状态（成功、失败、进行中）和产出结果，并将这些信息反馈给认知核心。
*   **可扩展的工具集 (Extensible Toolset)**: 允许开发者轻松地注册和集成新的工具，扩展Agent的能力。

## 3. 核心组件

### 3.1 计划解释器 (Plan Interpreter)

负责接收并逐一解析`Planner`生成的计划中的行动。

*   **功能**: 遍历计划中的行动列表，将每个`Action`对象传递给`Tool Dispatcher`进行处理。

### 3.2 工具调度器 (Tool Dispatcher)

根据行动指令，选择并调用正确的工具。

*   **功能**: 
    *   从`Action`对象中解析出`tool_name`和`parameters`。
    *   在`Tool Registry`中查找名为`tool_name`的工具。
    *   调用找到的工具，并将`parameters`传递给它。

### 3.3 工具注册表 (Tool Registry)

维护一个所有可用工具的清单。

*   **功能**: 
    *   **注册**: 在Agent启动时，扫描并注册所有可用的工具，存储它们的名称、描述、参数模式（Schema）和执行句柄。
    *   **查询**: 提供按名称或其他属性查询工具的能力。

### 3.4 安全沙箱 (Security Sandbox)

为具有潜在风险的工具（如执行Python代码、运行shell命令）提供一个隔离的执行环境。

*   **功能**: 
    *   **环境隔离**: 使用容器（如Docker）、虚拟机或受限的进程来隔离代码执行。
    *   **权限控制**: 限制被执行代码的文件系统访问、网络访问和系统调用权限。

### 3.5 任务执行器与监视器 (Task Executor & Monitor)

管理工具的实际执行过程，特别是对于异步和长时间运行的任务。

*   **功能**: 
    *   **异步执行**: 将长时间运行的工具调用提交到一个线程池或事件循环中，避免阻塞主认知流程。
    *   **状态跟踪**: 监控异步任务的生命周期（`pending`, `running`, `succeeded`, `failed`）。
    *   **结果收集**: 任务完成后，收集其返回值或错误信息。

## 4. 关键接口设计

```python
from typing import Dict, Any, List, Protocol
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    action: 'Action' # The action that was executed
    status: str      # 'succeeded', 'failed', 'in_progress'
    output: Any
    error: str | None

class ITool(Protocol):
    """单个工具的接口"""
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    def execute(self, **kwargs) -> Any:
        """执行工具的具体逻辑"""
        ...

class ExecutionEngine:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        # Potentially a task queue and a pool of workers for async execution
        self.task_queue = []

    def execute_plan(self, plan: 'Plan', callback: callable) -> None:
        """开始执行一个完整的计划"""
        for action in plan.actions:
            self.execute_action(action, callback)

    def execute_action(self, action: 'Action', callback: callable) -> None:
        """执行单个行动，并通过callback报告结果"""
        try:
            tool = self.tool_registry.get_tool(action.tool_name)
            
            # Here you might run it in a sandbox or a separate thread
            result_output = tool.execute(**action.parameters)
            
            result = ExecutionResult(
                action=action, 
                status='succeeded', 
                output=result_output, 
                error=None
            )
        except Exception as e:
            result = ExecutionResult(
                action=action, 
                status='failed', 
                output=None, 
                error=str(e)
            )
        
        callback(result)

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ITool] = {}

    def register(self, tool: ITool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> ITool:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found.")
        return self.tools[name]
```

## 5. 与其他组件的交互

*   **输入来源**: `Execution Engine`接收来自`Planner`的`Plan`对象。
*   **输出去向**: 执行结果（`ExecutionResult`）被异步地发送回`Cognitive Core`。`Cognitive Core`会根据这些结果来：
    *   更新其内部状态。
    *   决定是继续执行计划的下一步，还是触发`Planner`进行重新规划（如果发生失败）。
    *   将执行结果传递给`Learning Engine`进行分析和学习。
*   **与感知引擎的闭环**: 某些工具的执行结果（如API调用返回的数据）可能会被`Perception Engine`的一个适配器捕获，作为新的信息输入，形成一个完整的“思考-行动-感知”循环。

## 6. 实现考量

*   **工具的定义与发现**: 工具的定义应该标准化（例如，遵循OpenAPI规范或使用JSON Schema），以便于自动发现、注册和生成用户界面。
*   **人机协作 (Human-in-the-loop)**: 对于高风险或需要用户确认的操作，执行引擎应支持暂停执行并向用户请求授权的机制。
*   **执行的回滚**: 对于某些关键任务，可能需要设计补偿事务（Compensating Transactions）来回滚一系列已经执行的行动，以应对后续步骤的失败。