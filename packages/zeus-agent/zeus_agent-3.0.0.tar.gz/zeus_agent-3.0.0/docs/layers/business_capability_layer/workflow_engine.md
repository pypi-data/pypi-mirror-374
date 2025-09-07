# 工作流引擎 (Workflow Engine)

## 1. 概述

工作流引擎（Workflow Engine）是业务能力层的核心调度与执行组件。它负责解析和执行“组合能力”（Composite Capabilities）中定义的业务流程。组合能力将多个原子能力（Atomic Capabilities）或其他组合能力串联起来，形成一个复杂的、有状态的、可能长时间运行的业务逻辑。工作流引擎使得Agent能够可靠地执行这些结构化的流程，处理其中的数据流、并发、条件分支和错误恢复。

## 2. 设计目标

*   **可靠执行 (Reliable Execution)**: 确保工作流即使在遇到临时故障（如网络中断、服务不可用）时也能够继续执行。支持持久化和状态恢复。
*   **可观测性 (Observability)**: 提供对正在运行和已完成工作流的深入洞察，包括每一步的状态、输入/输出数据和执行历史，便于调试和监控。
*   **灵活性与表现力 (Flexibility & Expressiveness)**: 支持复杂的流程模式，包括顺序执行、并行执行（fork-join）、条件分支、循环，以及事件驱动的流程。
*   **可扩展性 (Scalability)**: 能够水平扩展以处理大量并发的工作流实例。
*   **开发者友好 (Developer-Friendly)**: 提供简单的DSL（领域特定语言）或SDK来定义工作流，隐藏底层的复杂性。

## 3. 核心组件

### 3.1 工作流定义 (Workflow Definition)

一种用于描述业务流程逻辑的结构化格式。通常使用YAML或JSON，也可以是图形化表示。

*   **核心元素**: 
    *   `name`: 工作流的唯一标识。
    *   `input_schema`: 定义启动工作流所需的输入参数。
    *   `tasks` or `steps`: 工作流的主要部分，一个任务列表。
    *   **任务类型**: 
        *   `capability_task`: 调用一个已在`Capability Registry`中注册的原子能力。
        *   `sub_workflow_task`: 调用另一个工作流，实现流程的嵌套和复用。
        *   `control_flow_task`: 控制流程逻辑，如`if`（条件分支）、`for_each`（循环）、`parallel`（并行）。
    *   `data_flow`: 定义数据如何在任务之间传递（例如，将任务A的输出映射为任务B的输入）。

**示例 (YAML DSL)**:

```yaml
name: process_loan_application
input_schema:
  properties:
    applicant_id: { type: string }
    amount: { type: number }
tasks:
  - id: fetch_applicant_data
    type: capability_task
    capability_name: db_query_applicant
    input:
      id: "${workflow.input.applicant_id}"

  - id: credit_check
    type: capability_task
    capability_name: third_party_credit_check
    input:
      social_security_number: "${tasks.fetch_applicant_data.output.ssn}"

  - id: risk_assessment
    type: parallel
    branches:
      - tasks:
        - id: internal_risk_model
          type: capability_task
          capability_name: run_internal_risk_model
      - tasks:
        - id: fraud_detection
          type: capability_task
          capability_name: check_fraud_database

  - id: final_decision
    type: capability_task
    capability_name: make_loan_decision
    input:
      credit_score: "${tasks.credit_check.output.score}"
      internal_risk: "${tasks.internal_risk_model.output.risk_level}"
      fraud_score: "${tasks.fraud_detection.output.score}"
```

### 3.2 工作流解析器 (Workflow Parser)

负责在工作流执行前，读取并验证工作流定义的语法和语义。

*   **功能**: 
    *   将DSL（如YAML）解析成内部的、可执行的图结构（如DAG - 有向无环图）。
    *   验证任务定义是否正确，依赖关系是否存在循环。
    *   检查所需的能力是否都在`Capability Registry`中注册。

### 3.3 任务调度器 (Task Scheduler)

工作流引擎的大脑，决定下一个要执行的任务。

*   **功能**: 
    *   维护一个待执行任务的队列。
    *   当一个任务完成后，根据工作流图的定义，确定哪些后续任务的依赖已满足，并将它们放入队列。
    *   处理并行任务的分发。

### 3.4 任务执行器 (Task Executor)

负责实际执行队列中的任务。

*   **功能**: 
    *   从调度器接收任务。
    *   根据任务类型，执行相应操作：
        *   对于`capability_task`，通过`Capability Registry`发现能力，并调用其`handler`。
        *   对于`sub_workflow_task`，创建一个新的子工作流实例。
    *   处理任务的重试和超时逻辑。

### 3.5 状态管理器 (State Manager)

负责持久化工作流实例的当前状态。

*   **功能**: 
    *   在每个任务执行前后，保存工作流的完整状态，包括任务的完成情况、所有变量和数据。
    *   确保工作流可以从上一个检查点恢复，实现可靠性。
*   **实现**: 通常使用数据库（如PostgreSQL, MySQL）或专门的持久化存储。

## 4. 关键接口设计

```python
from typing import Dict, Any, Optional

class WorkflowEngine:

    def __init__(self, state_manager, task_scheduler, task_executor):
        self.state_manager = state_manager
        self.scheduler = task_scheduler
        self.executor = task_executor

    def start_workflow(self, workflow_name: str, inputs: Dict[str, Any]) -> str:
        """启动一个新的工作流实例，并返回唯一的实例ID"""
        # 1. Parse workflow definition
        # 2. Create a new workflow instance record in the state manager
        # 3. Schedule the first task(s)
        # 4. Return instance_id
        pass

    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """查询工作流实例的当前状态"""
        # Retrieve status from the state manager
        pass

    def signal_workflow(self, instance_id: str, signal_name: str, data: Any) -> None:
        """向一个正在等待的流程实例发送外部事件或信号"""
        # e.g., for human-in-the-loop approval
        pass

    def get_workflow_result(self, instance_id: str, timeout_seconds: int) -> Dict[str, Any]:
        """获取已完成工作流的最终结果"""
        pass
```

## 5. 与其他组件的交互

*   **由认知核心调用**: `Cognitive Core`或`Planner`决定启动一个业务流程时，会调用`WorkflowEngine.start_workflow()`。
*   **与能力注册表交互**: `Task Executor`在执行`capability_task`时，需要查询`Capability Registry`来找到能力的具体实现。
*   **与外部世界交互**: 工作流中的原子能力通过`Adapter Layer`与外部API、数据库等进行交互。

## 6. 实现考量

*   **构建 vs. 购买 (Build vs. Buy)**: 工作流引擎是一个复杂系统。可以考虑基于成熟的开源项目（如Temporal, Netflix Conductor, Camunda Zeebe）进行构建，而不是完全从零开始。
*   **数据流管理**: 需要设计一套强大的表达式语言（如JSONPath）来处理任务之间复杂的数据映射和转换。
*   **异步与事件驱动**: 对于长时间运行的流程，引擎的核心应该是异步和事件驱动的，以避免阻塞和资源浪费。任务的完成、失败等都应作为事件来驱动调度器。
*   **人机交互 (Human-in-the-Loop)**: 对于需要人工审批或干预的流程，引擎需要支持暂停（`wait`）和接收外部信号（`signal`）的能力。