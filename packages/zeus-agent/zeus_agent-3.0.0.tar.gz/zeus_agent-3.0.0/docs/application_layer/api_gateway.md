# API网关 (API Gateway)

## 1. 概述

API网关是应用层的统一入口，是整个Agent系统的“前门”。它负责接收来自不同渠道（如Web、移动应用、即时通讯工具、第三方服务）的所有传入请求，并对这些请求进行标准化的处理，然后将它们安全、可靠地路由到内部的任务处理系统。网关是实现多渠道接入、保障系统安全和解耦前端与后端的关键组件。

## 2. 设计目标

*   **统一入口 (Unified Entry Point)**: 为所有外部交互提供一个单一、稳定的接入点，简化客户端的配置和系统的网络拓扑。
*   **协议转换 (Protocol Translation)**: 将各种外部协议（如HTTP, WebSocket, Webhook）转换为统一的、内部能够理解的事件或任务格式。
*   **请求路由 (Request Routing)**: 能够基于请求的路径、域名、头部信息或内容，智能地将其分发到不同的后端服务或任务队列。
*   **安全与认证 (Security & Authentication)**: 集中处理认证、授权、API密钥管理和TLS终止，保护后端服务免受未授权访问。
*   **横切关注点 (Cross-cutting Concerns)**: 统一处理日志记录、指标监控、速率限制和请求/响应转换，避免在每个后端服务中重复实现。
*   **高可扩展性与高可用性 (Scalability & High Availability)**: 网关本身必须是无状态的、可水平扩展的，并且具备容错能力，以应对高并发流量。

## 3. 核心组件

### 3.1 渠道适配器 (Channel Adapter)

负责处理特定渠道的协议和数据格式。这是一个可插拔的组件体系。

*   **HTTP/S Adapter**: 处理标准的RESTful API请求。这是最常见的适配器。
*   **WebSocket Adapter**: 支持双向、实时的通信，适用于交互式聊天会话。
*   **Webhook Adapter**: 接收来自第三方服务（如GitHub, Stripe）的事件通知。
*   **Messaging Adapter**: 对接即时通讯平台，如Slack (RTM/Events API), Microsoft Teams (Bots Framework), Discord等。
*   **功能**: 每个适配器负责将渠道特定的数据包（如一个HTTP POST请求体，一个WebSocket消息）解析并转换为一个标准化的内部`Task`对象。

### 3.2 路由引擎 (Routing Engine)

根据预定义的规则，决定请求的去向。

*   **功能**: 
    *   解析请求的目标（如URL路径` /api/v1/chat`）。
    *   匹配路由规则表。
    *   将请求转发到目标后端，通常是一个`Task Queue`的主题（Topic）或是一个特定的HTTP服务。
*   **实现**: 可以使用基于路径、头部、HTTP方法的灵活路由规则。例如，`/chat/completions`路由到`chat_tasks_queue`，而`/agents/manage`路由到`admin_service`。

### 3.3 中间件管道 (Middleware Pipeline)

一系列在请求被路由之前或之后执行的处理程序（Handler）。

*   **功能**: 
    *   **认证中间件 (Authentication)**: 验证API密钥、JWT（JSON Web Token）或OAuth令牌。
    *   **授权中间件 (Authorization)**: 检查用户或应用是否有权限执行请求的操作。
    *   **日志中间件 (Logging)**: 记录所有请求和响应的元数据。
    *   **指标中间件 (Metrics)**: 收集请求延迟、状态码等监控指标。
    *   **速率限制中间件 (Rate Limiting)**: 基于IP、用户或API密钥限制请求频率。
    *   **请求/响应转换中间件**: 修改请求头、请求体或转换响应格式。

### 3.4 配置管理器 (Configuration Manager)

负责加载和管理网关的所有配置，包括路由规则、中间件设置和渠道适配器参数。

*   **功能**: 
    *   支持从文件（YAML, JSON）或配置中心（如Consul, Etcd）动态加载配置。
    *   支持配置的热重载（Hot-reloading），无需重启服务即可应用变更。

## 4. 关键接口与数据流

**数据流**: 

1.  外部客户端通过某个渠道（如HTTPS）向API网关发送请求。
2.  相应的`Channel Adapter`（HTTP Adapter）接收请求。
3.  请求进入`Middleware Pipeline`，依次通过认证、日志、速率限制等中间件。
4.  `Routing Engine`根据请求路径（如`/tasks/image_generation`）匹配路由规则。
5.  路由规则指向一个任务队列的主题`image_gen_tasks`。
6.  网关将请求体和元数据封装成一个标准的`Task`对象。
7.  `Task`对象被发布到`Task Queue`中。
8.  网关立即向客户端返回一个`202 Accepted`响应，其中包含一个任务ID，客户端后续可凭此ID查询任务状态。

**标准化Task对象 (示例)**:

```json
{
  "task_id": "uuid-v4-generated-by-gateway",
  "source_channel": "http",
  "correlation_id": "client-provided-request-id",
  "timestamp": "2023-10-27T10:00:00Z",
  "metadata": {
    "user_id": "user-123",
    "ip_address": "203.0.113.1"
  },
  "payload": {
    "agent_id": "image-generation-agent-v2",
    "inputs": {
      "prompt": "A photo of an astronaut riding a horse on Mars.",
      "style": "cinematic"
    }
  }
}
```

## 5. 实现考量

*   **技术选型**: 
    *   **自研**: 使用高性能网络框架（如Go的`net/http`, Python的`FastAPI`, Java的`Netty`）构建。优点是灵活可控，缺点是开发成本高。
    *   **基于现有网关**: 采用成熟的开源API网关项目（如Kong, Traefik, APISIX），并通过插件机制扩展自定义逻辑。这是推荐的方式，可以重用大量成熟功能。
*   **无状态设计**: 网关本身应设计为无状态的，以便于水平扩展和负载均衡。所有状态信息（如会话、速率限制计数器）应存储在外部系统（如Redis, 数据库）中。
*   **安全性**: 安全是API网关的首要职责。必须实施严格的输入验证、防止注入攻击，并确保所有管理端点都受到保护。
*   **可观测性**: 必须与集中式日志系统（如ELK Stack, Loki）、指标监控系统（如Prometheus, Grafana）和分布式追踪系统（如Jaeger, Zipkin）深度集成。