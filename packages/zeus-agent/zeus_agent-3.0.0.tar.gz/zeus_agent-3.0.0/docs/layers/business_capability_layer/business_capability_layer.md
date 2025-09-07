# 业务能力层 (Business Capability Layer)

## 1. 概述

业务能力层（Business Capability Layer）是统一Agent框架中承载具体业务逻辑和领域知识的核心层。它建立在认知架构层之上，将底层的认知能力（如推理、规划）封装和编排成面向特定业务场景的、可复用的高级能力。这一层使得Agent能够执行复杂的、多步骤的业务流程，并与特定的业务系统进行深度集成。

## 2. 设计理念

*   **能力即服务 (Capability as a Service)**: 将每个业务能力封装为独立、可独立部署和调用的服务。开发者可以像调用API一样，组合和使用这些能力。
*   **领域驱动设计 (Domain-Driven Design)**: 围绕核心业务领域和限界上下文（Bounded Context）来组织能力，确保能力模型与业务模型的一致性。
*   **可编排与可组合 (Orchestratable and Composable)**: 提供强大的工作流和编排引擎，允许将多个原子能力（Atomic Capabilities）组合成复杂的业务流程（Business Process）。
*   **知识密集型 (Knowledge-Intensive)**: 业务能力与领域知识库（如产品手册、业务规则库、API文档）紧密集成，使其具备执行专业任务所需的知识。
*   **高可扩展性 (High Extensibility)**: 框架应提供清晰的规范和SDK，使开发者能够轻松地为Agent开发、注册和部署新的业务能力。

## 3. 核心组件

### 3.1 能力注册表 (Capability Registry)

一个集中式的服务注册与发现中心，用于管理所有可用的业务能力。

*   **功能**: 
    *   存储每个能力的元数据，包括：名称、描述、输入/输出模式（Schema）、依赖关系、版本号和所属领域。
    *   提供能力的动态注册、注销和查询接口。
    *   支持基于能力名称、标签或领域的服务发现。
*   **实现**: 可以基于Consul、Etcd等服务发现工具，或在数据库中实现。

### 3.2 能力定义模型 (Capability Definition Model)

定义了一个业务能力的标准化结构。

*   **原子能力 (Atomic Capability)**: 代表一个不可再分的最小业务操作。通常直接映射到一个或多个工具/API的调用。
    *   `name`: 唯一的标识符。
    *   `description`: 自然语言描述，供LLM理解和调用。
    *   `input_schema`: 输入参数的JSON Schema。
    *   `output_schema`: 输出结果的JSON Schema。
    *   `handler`: 指向实现该能力的具体代码（如一个函数或类方法）。
*   **组合能力 (Composite Capability)**: 由多个原子能力或其他组合能力通过工作流编排而成，代表一个完整的业务流程。
    *   `name`: 唯一的标识符。
    *   `description`: 流程的自然语言描述。
    *   `workflow_definition`: 描述能力执行流程的定义（如使用YAML、JSON或专门的DSL）。

### 3.3 工作流引擎 (Workflow Engine)

负责解析和执行组合能力的编排逻辑。

*   **功能**: 
    *   解析工作流定义，构建执行图（Execution Graph）。
    *   根据图中定义的顺序、条件和并行逻辑，调度和执行原子能力。
    *   管理流程的上下文和状态（如变量传递、错误处理、重试机制）。
    *   支持长时间运行的、可中断和恢复的业务流程。
*   **实现**: 可以基于现有的工作流引擎（如Temporal, Camunda）或自研一个轻量级的流程调度器。

### 3.4 领域知识库 (Domain Knowledge Base)

为业务能力提供所需的专业知识和数据。

*   **功能**: 
    *   存储特定领域的结构化和非结构化知识，如：
        *   **业务规则**: 以规则引擎（如Drools）或DMN（Decision Model and Notation）格式存储。
        *   **API文档/SDK**: 供Agent理解如何调用外部系统。
        *   **产品信息/FAQs**: 作为RAG系统的知识源。
    *   提供高效的知识检索接口。
*   **集成**: 与智能上下文层的`Knowledge Graph`和`Memory System`深度集成。

### 3.5 能力开发套件 (Capability SDK)

为开发者提供一套工具和库，以简化新能力的开发、测试和部署。

*   **功能**: 
    *   提供用于定义能力（原子和组合）的装饰器或基类。
    *   包含用于与`Capability Registry`和`Workflow Engine`交互的客户端库。
    *   提供本地测试和调试工具。

## 4. 关键接口设计

```python
from typing import Dict, Any, Callable
from dataclasses import dataclass

# 能力定义
@dataclass
class AtomicCapability:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable[..., Any]

# 能力注册表示例
class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, AtomicCapability] = {}

    def register(self, cap: AtomicCapability):
        self._capabilities[cap.name] = cap

    def discover(self, name: str) -> AtomicCapability:
        return self._capabilities.get(name)

# 业务流程定义 (简化示例)
workflow_definition = {
    'name': 'process_customer_order',
    'steps': [
        {'capability': 'check_inventory', 'input': {'item_id': '${order.item_id}'}},
        {'capability': 'process_payment', 'input': {'amount': '${order.amount}'}},
        {'capability': 'ship_product', 'input': {'address': '${order.address}'}}
    ]
}

# 工作流引擎接口
class WorkflowEngine:
    def execute(self, workflow_name: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Load workflow definition
        # 2. Execute steps sequentially/parallelly
        # 3. Manage context and data passing
        # 4. Return final result
        pass
```

## 5. 与其他层的交互

*   **认知层驱动**: `Cognitive Core`根据`Planner`的计划，决定调用哪个业务能力。它不关心能力的内部实现，只负责触发调用并接收结果。
*   **使用上下文层**: 业务能力在执行过程中，会频繁查询`Memory System`和`Knowledge Graph`以获取必要的上下文和领域知识。
*   **通过适配器层与外部交互**: 当一个原子能力需要与外部系统（如数据库、API）交互时，它会通过`Adapter Layer`中的相应适配器来执行。

## 6. 实现考量

*   **能力粒度**: 需要仔细设计能力的粒度。粒度太粗，复用性差；粒度太细，编排成本高。
*   **事务与补偿**: 对于涉及多个步骤和外部系统调用的长流程，需要设计事务管理和补偿机制（如Saga模式），以确保数据一致性。
*   **版本控制**: 业务能力和流程会不断演化，需要有完善的版本控制策略，以处理兼容性问题。
*   **安全性**: 需要对能力的调用进行严格的权限控制，确保只有授权的Agent或用户才能执行敏感操作。