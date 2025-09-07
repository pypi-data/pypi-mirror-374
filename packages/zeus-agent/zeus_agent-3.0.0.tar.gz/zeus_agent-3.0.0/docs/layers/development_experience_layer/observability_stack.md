# 可观测性堆栈 (Observability Stack)

## 1. 概述

在生产环境中，对Agent应用进行有效的监控、故障排查和性能优化至关重要。可观测性（Observability）不仅仅是传统的监控（Monitoring），它更强调系统能够通过其外部输出（如日志、指标、追踪）来被理解和诊断的能力。一个强大的可观测性堆栈是保障Agent应用在生产环境中稳定、可靠、高效运行的基石。

本设计旨在为统一Agent框架提供一个集成的、开箱即用的可观测性解决方案，遵循业界公认的三大支柱：日志（Logging）、指标（Metrics）和追踪（Tracing）。

## 2. 设计目标

*   **全面覆盖**: 自动地、无侵入地覆盖框架的所有核心组件和Agent应用的关键路径。
*   **标准化**: 采用业界开放标准（如OpenTelemetry），避免厂商锁定，并与主流的可观测性平台（如Prometheus, Grafana, Jaeger, Datadog）兼容。
*   **关联性**: 能够将日志、指标和追踪数据关联起来。例如，从一个异常的指标图表，能够直接跳转到相关的追踪和日志，快速定位问题根源。
*   **低开销**: 可观测性数据采集对应用性能的影响应尽可能小。
*   **易于使用**: 开发者无需复杂的配置即可获得基本的观测能力，同时提供高级API用于自定义监控。

## 3. 可观测性的三大支柱

### 3.1 结构化日志 (Structured Logging)

*   **是什么**: 记录离散的、带有时间戳的事件。日志应为机器可读的结构化格式（如JSON），而不是纯文本字符串。
*   **核心功能**:
    *   **自动上下文注入**: 框架自动在所有日志中注入关键的上下文信息，如`trace_id`, `span_id`, `task_id`, `user_id`等。这使得可以轻松地筛选和关联来自同一次请求的所有日志。
    *   **日志级别控制**: 支持标准的日志级别（DEBUG, INFO, WARNING, ERROR），并允许在运行时动态调整。
    *   **日志输出**: 支持将日志输出到控制台、文件或集中的日志聚合系统（如ELK Stack, Loki, Splunk）。
*   **示例日志条目**:
    ```json
    {
      "timestamp": "2023-10-27T10:00:00Z",
      "level": "INFO",
      "message": "Tool 'get_weather' called successfully",
      "trace_id": "abc-123-xyz-789",
      "span_id": "span-456",
      "task_id": "task-abc",
      "capability": "get_weather_capability",
      "tool_name": "get_weather",
      "tool_input": {"city": "beijing"},
      "duration_ms": 150
    }
    ```

### 3.2 指标 (Metrics)

*   **是什么**: 可聚合的、用于衡量系统在一段时间内行为的数值。例如，请求速率、错误率、延迟等。
*   **核心功能**:
    *   **自动仪表化 (Auto-instrumentation)**: 框架自动暴露一系列核心指标，无需开发者手动添加。这些指标被称为“黄金四指标”：
        *   **延迟 (Latency)**: 请求处理时间的分布（如P99, P95, P50）。
        *   **流量 (Traffic)**: 每秒请求数（RPS）。
        *   **错误 (Errors)**: 每秒失败的请求数。
        *   **饱和度 (Saturation)**: 系统资源的使用情况（如CPU、内存、队列深度）。
    *   **自定义指标**: SDK提供API，允许开发者在自己的能力代码中定义和记录业务相关的指标。
    *   **暴露格式**: 指标以Prometheus Exposition Format进行暴露，便于Prometheus抓取。
*   **示例自定义指标**:
    ```python
    from agent_sdk.metrics import counter

    @capability(name="process_order")
    def process_order(order):
        # ... 业务逻辑 ...
        # 记录一个自定义指标
        counter("orders_processed_total", labels={"type": order.type}).inc()
    ```

### 3.3 分布式追踪 (Distributed Tracing)

*   **是什么**: 记录单个请求在分布式系统中所经过的完整路径。每个路径是一个“追踪”（Trace），由多个“跨度”（Span）组成，形成一个树状结构。
*   **核心功能**:
    *   **自动追踪**: 框架自动为每个进入系统的请求创建一个Trace，并在内部的各个组件和服务之间传播追踪上下文（Trace Context）。
    *   **Span创建**: 框架为关键操作（如API调用、工具执行、LLM查询、数据库访问）自动创建Span，并记录其耗时和元数据。
    *   **SDK集成**: 开发者可以使用SDK提供的API在自己的代码中创建自定义的Span，以追踪更细粒度的业务逻辑。
*   **可视化**: 追踪数据可以被发送到兼容OpenTelemetry的后端，如Jaeger或Zipkin，进行可视化展示，清晰地看到每个请求的调用链、耗时瓶颈和服务依赖关系。

## 4. 技术实现 (基于OpenTelemetry)

[OpenTelemetry (OTel)](https://opentelemetry.io/) 是CNCF下的一个开源项目，它提供了一套标准的API、SDK和工具，用于仪表化、生成、收集和导出遥测数据（指标、日志和追踪）。

*   **实现流程**:
    1.  **集成OTel SDK**: 在Agent框架的核心中集成OpenTelemetry Python SDK。
    2.  **自动仪表化库**: 使用OTel提供的自动仪表化库（如`opentelemetry-instrumentation-fastapi`）来自动追踪Web请求。
    3.  **手动仪表化**: 在框架的关键位置（如Planner, Tool Caller）使用OTel API进行手动埋点，创建Span和记录事件。
    4.  **配置导出器 (Exporter)**: 框架提供配置选项，允许开发者将收集到的遥测数据导出到不同的后端。例如：
        *   **追踪**: OTLP Exporter -> Jaeger / Datadog Agent
        *   **指标**: Prometheus Exporter -> Prometheus
        *   **日志**: OTLP Exporter -> Loki / ELK

## 5. 与调试工具的关系

可观测性堆栈和调试工具是互补的。

*   **调试工具**主要用于**开发阶段**，提供深度、交互式的诊断能力，但通常开销较大。
*   **可观测性堆栈**主要用于**生产环境**，提供宏观、聚合的系统视图，帮助发现和定位问题，开销较低。

从可观测性系统（如Grafana, Jaeger）中发现的问题，往往需要回到开发环境，使用调试工具进行更深入的根源分析和复现。