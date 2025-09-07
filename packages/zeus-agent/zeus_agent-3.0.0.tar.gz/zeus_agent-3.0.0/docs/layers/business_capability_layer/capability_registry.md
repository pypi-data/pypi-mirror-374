# 能力注册表 (Capability Registry)

## 1. 概述

能力注册表（Capability Registry）是业务能力层的核心基础设施，它扮演着服务注册与发现中心的角色。所有Agent可用的业务能力（无论是原子的还是组合的）都必须在此注册，以便被认知核心、规划器或其他能力动态地发现和调用。它为构建一个解耦、可扩展和动态的业务能力生态系统提供了基础。

## 2. 设计目标

*   **集中管理 (Centralized Management)**: 提供一个单一、权威的入口点来管理所有业务能力的生命周期。
*   **动态发现 (Dynamic Discovery)**: 允许Agent在运行时根据需求（如通过自然语言描述）查询和发现可用的能力，而不是在代码中硬编码。
*   **丰富的元数据 (Rich Metadata)**: 不仅存储能力的调用端点，还存储丰富的元数据，如功能描述、输入/输出模式、版本、依赖关系和非功能性属性（如成本、延迟）。
*   **高可用性 (High Availability)**: 作为系统的关键组件，注册表本身需要具备高可用性和容错能力。
*   **多租户支持 (Multi-tenancy)**: 在多Agent或多用户场景下，支持能力的隔离和权限控制。

## 3. 核心功能

### 3.1 能力注册 (Capability Registration)

*   **注册接口**: 提供API（如RESTful或gRPC）供能力开发者或部署脚本调用，以注册一个新的能力或版本。
*   **元数据验证**: 在注册时，根据预定义的模式（Schema）验证提交的能力元数据是否完整和合法。
*   **健康检查**: 注册表可以配置为定期对已注册的能力进行健康检查（Health Check），自动剔除不健康或不可用的能力实例。

### 3.2 能力发现 (Capability Discovery)

*   **精确查询**: 支持通过唯一的能力名称（ID）和版本号进行精确查找。
*   **语义查询**: 支持基于自然语言描述的语义搜索。这使得LLM（如Planner）可以直接根据任务描述来寻找最匹配的能力。这是注册表的核心高级功能。
    *   **实现**: 通常通过将能力的`description`文本进行向量化（Embedding），并存储在向量数据库中来实现。查询时，将自然语言查询同样转换为向量，进行相似度搜索。
*   **属性查询**: 支持基于标签（Tags）、所属领域（Domain）、提供者（Provider）等元数据属性进行过滤和查询。

### 3.3 能力生命周期管理 (Lifecycle Management)

*   **版本控制**: 支持同一能力的多个版本并存，允许Agent根据需要选择特定版本，也支持平滑的能力升级。
*   **状态管理**: 跟踪每个能力的状态（如：`ACTIVE`, `DEPRECATED`, `INACTIVE`）。`DEPRECATED`状态可以用来通知调用方该能力即将被移除。
*   **注销**: 提供接口来安全地从注册表中移除一个能力。

### 3.4 访问控制 (Access Control)

*   **认证与授权**: 对能力的注册和查询操作进行认证。可以实现基于角色的访问控制（RBAC），限制特定用户或Agent只能访问或操作其权限范围内的能力。

## 4. 数据模型 (Data Model)

能力注册表中存储的核心数据模型如下：

```json
{
  "id": "unique_capability_id_v1",
  "name": "query_weather",
  "version": "1.0.0",
  "description": "Get the current weather for a specific location.",
  "description_embedding": [0.12, -0.45, ..., 0.89], // For semantic search
  "domain": "life_assistant.weather",
  "tags": ["weather", "location", "api"],
  "provider": "OpenWeatherAPI",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"}
    },
    "required": ["location"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "temperature": {"type": "number"},
      "condition": {"type": "string"}
    }
  },
  "endpoint": {
    "type": "http", // or "grpc", "function_call"
    "uri": "https://api.weather.com/v1/current"
  },
  "status": "ACTIVE",
  "non_functional_properties": {
    "latency_ms_p95": 150,
    "cost_per_call_usd": 0.001
  },
  "dependencies": ["capability_geocode_v2"]
}
```

## 5. 关键接口设计

```python
from typing import List, Dict, Any, Optional

class CapabilityRegistry:

    def register(self, capability_metadata: Dict[str, Any]) -> bool:
        """注册一个新能力或更新现有能力"""
        # 1. Validate metadata against schema
        # 2. Generate and store description embedding
        # 3. Store the metadata in the backend (e.g., database, KV store)
        pass

    def deregister(self, capability_id: str) -> bool:
        """从注册表中移除一个能力"""
        pass

    def lookup(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """通过ID精确查找能力"""
        pass

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """通过自然语言描述进行语义搜索"""
        # 1. Convert query_text to an embedding vector
        # 2. Perform a vector similarity search in the registry
        # 3. Return the top_k most similar capabilities
        pass

    def filter_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """根据标签进行过滤查询"""
        pass
```

## 6. 实现考量

*   **技术选型**: 
    *   **后端存储**: 可以使用关系型数据库（如PostgreSQL，配合pgvector插件）、NoSQL数据库（如MongoDB）或专门的键值存储（如Etcd）。
    *   **向量数据库**: 对于语义搜索功能，需要集成一个向量数据库，如FAISS, Milvus, Pinecone, or Weaviate。
    *   **服务框架**: 可以使用FastAPI, gRPC等框架来暴露API。
*   **部署模式**: 
    *   可以是单体服务，也可以是部署在Kubernetes上的高可用集群。
*   **缓存**: 对于频繁的查询，可以在注册表客户端或服务端添加缓存层，以降低延迟和数据库负载。
*   **安全性**: API端点需要通过API网关进行保护，实施认证、授权、速率限制等策略。