# 能力定义模型 (Capability Definition Model)

## 1. 概述

能力定义模型（Capability Definition Model）是业务能力层的核心规范，它提供了一套标准化的结构和模式，用于描述和定义Agent可以执行的各种业务能力。这个模型是连接自然语言理解、计划制定与实际代码执行之间的桥梁。一个清晰、一致且富有表现力的定义模型，是实现能力可发现、可组合和可复用的前提。

## 2. 设计目标

*   **标准化 (Standardization)**: 为所有业务能力提供一个统一的、与实现无关的描述格式。
*   **人机友好 (Human & Machine Readability)**: 定义应既能被开发者轻松读写，也能被机器（特别是LLM）准确解析和理解。
*   **表现力 (Expressiveness)**: 能够描述从简单的单步操作到复杂的多步流程等各种能力。
*   **可验证性 (Verifiability)**: 能力的定义应包含足够的模式（Schema）信息，以便在注册和调用时进行静态和动态的验证。
*   **可扩展性 (Extensibility)**: 模型应允许添加自定义的元数据和属性，以适应未来发展的需要。

## 3. 核心能力类型

能力定义模型主要包含两种基本类型：原子能力和组合能力。

### 3.1 原子能力 (Atomic Capability)

原子能力是业务逻辑的最小、不可再分的执行单元。它通常直接封装了对一个或多个底层工具、API或内部函数的调用。原子能力是构建所有复杂业务流程的基础。

**核心属性**:

*   `name` (string, required): 能力的唯一标识符，通常采用`domain.verb_noun`的格式，例如`finance.get_stock_price`。
*   `description` (string, required): 对能力功能的详细、清晰的自然语言描述。**这是至关重要的字段**，因为它将作为LLM（如Planner）理解和选择此能力的主要依据。描述应清楚说明能力“做什么”、“需要什么输入”以及“返回什么结果”。
*   `input_schema` (JSON Schema, required): 使用JSON Schema格式精确定义能力所需的输入参数。包括参数名称、类型、描述、是否必需等信息。
*   `output_schema` (JSON Schema, required): 使用JSON Schema格式精确定义能力成功执行后返回的数据结构。
*   `handler` (Handler, required): 定义了能力的具体实现。这可以是一个函数引用、一个API端点、或是一个gRPC服务地址。
*   `tags` (List[string], optional): 一组用于分类和过滤的标签，例如`["finance", "external_api", "real-time"]`。
*   `version` (string, optional): 能力的版本号，遵循语义化版本（如`1.2.0`）。

**示例 (YAML)**:

```yaml
name: finance.get_stock_price
description: "Retrieves the latest stock price for a given stock symbol from the public market data API."
version: "1.0.0"
tags: ["finance", "stock", "api"]
input_schema:
  type: object
  properties:
    symbol:
      type: string
      description: "The stock ticker symbol, e.g., 'AAPL' for Apple Inc."
  required:
    - symbol
output_schema:
  type: object
  properties:
    symbol:
      type: string
    price:
      type: number
    currency:
      type: string
      default: "USD"
  required:
    - symbol
    - price
handler:
  type: api
  endpoint: "https://api.example.com/stocks/{symbol}"
  method: "GET"
```

### 3.2 组合能力 (Composite Capability)

组合能力（或称业务流程）是通过编排多个原子能力或其他组合能力而形成的更高级的能力。它定义了一个完整的、有状态的业务流程。

**核心属性**:

*   `name` (string, required): 组合能力的唯一标识符，例如`e-commerce.process_new_order`。
*   `description` (string, required): 对整个业务流程的高层次描述。
*   `input_schema` (JSON Schema, required): 启动整个流程所需的初始输入。
*   `output_schema` (JSON Schema, required): 流程成功完成后最终返回的结果。
*   `workflow_definition` (Workflow, required): 对流程内部逻辑的详细定义。这部分通常由`Workflow Engine`负责解析和执行。其定义语言可以是YAML, JSON, 或其他DSL，描述了任务的执行顺序、数据流、条件分支等。
*   `version` (string, optional): 流程定义的版本。

**示例 (YAML, 引用工作流定义)**:

```yaml
name: e-commerce.process_new_order
description: "Handles a new customer order by checking inventory, processing payment, and scheduling shipment."
version: "1.1.0"
input_schema:
  type: object
  properties:
    order_details: { $ref: "#/components/schemas/Order" }
output_schema:
  type: object
  properties:
    order_id: { type: string }
    status: { type: string }
    estimated_delivery_date: { type: string, format: date }
# The actual workflow logic is defined in a separate file or section
# managed by the Workflow Engine.
workflow_definition:
  type: temporal_workflow # or camunda, argo, etc.
  name: ProcessNewOrderWorkflow
  version: "v1.1"
```

## 4. 与其他组件的关系

*   **能力注册表**: 所有定义好的能力（原子和组合）的元数据都将被发布到`Capability Registry`中。注册表是这些定义模型的“活字典”。
*   **工作流引擎**: `Workflow Engine`是组合能力定义中`workflow_definition`部分的消费者。它负责解释和执行这部分定义的复杂逻辑。
*   **认知核心/规划器**: `Cognitive Core`和`Planner`是能力定义的主要使用者。它们通过搜索`Capability Registry`，利用`description`来理解和选择合适的能力，并利用`input_schema`来生成调用参数。
*   **能力开发套件 (SDK)**: `Capability SDK`为开发者提供了工具和库（如装饰器、基类），使其能够方便地按照本模型规范创建和打包能力定义。

## 5. 实现考量

*   **Schema的复用**: 对于通用的数据结构（如`Address`, `Customer`），应该定义可复用的Schema组件，并通过`$ref`进行引用，以提高一致性和可维护性。
*   **验证**: 必须建立严格的验证流程。在能力注册时进行静态验证（检查所有必填字段和Schema格式），在能力调用时进行动态验证（检查传入的参数是否符合`input_schema`）。
*   **工具化**: 提供可视化工具来创建和编辑能力定义，特别是对于复杂的组合能力，可以极大地提升开发效率。