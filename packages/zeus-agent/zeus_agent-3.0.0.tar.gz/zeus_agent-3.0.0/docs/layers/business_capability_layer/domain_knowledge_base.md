# 领域知识库 (Domain Knowledge Base)

## 1. 概述

领域知识库（Domain Knowledge Base）是业务能力层中专门负责管理和提供特定领域专业知识的组件。它是一个结构化和非结构化信息的集合，为Agent在执行复杂业务任务时提供必要的背景知识、规则、数据和文档。与智能上下文层中的通用`Knowledge Graph`和`Memory System`不同，领域知识库更侧重于特定业务领域的、相对静态的、权威的知识。

## 2. 设计目标

*   **知识集中化 (Knowledge Centralization)**: 将分散在各处的领域知识（如API文档、业务规则、产品手册、FAQs）进行集中管理，避免知识孤岛。
*   **多模态知识支持 (Multi-modal Knowledge Support)**: 支持存储和检索多种形式的知识，包括文本、结构化数据（如表格）、规则和半结构化数据（如JSON）。
*   **高效检索 (Efficient Retrieval)**: 提供快速、精准的知识检索接口，支持关键词搜索、语义搜索和结构化查询。
*   **与认知和执行的无缝集成 (Seamless Integration)**: 确保知识可以被`Reasoning Engine`、`Planner`和`Execution Engine`（通过原子能力）轻松访问和利用。
*   **易于维护 (Ease of Maintenance)**: 提供工具和流程，使领域专家（Domain Experts）能够方便地更新和扩展知识库。

## 3. 知识库的核心构成

领域知识库通常由以下几种类型的知识源组合而成：

### 3.1 文档库 (Document Store)

用于存储非结构化的文本知识，是RAG（Retrieval-Augmented Generation）模式的核心信息源。

*   **内容**: 
    *   产品手册、用户指南
    *   最佳实践、操作流程（SOPs）
    *   常见问题解答（FAQs）
    *   法律法规、合规性文件
*   **技术实现**: 
    *   使用向量数据库（如Weaviate, Pinecone, Milvus）对文档进行分块（Chunking）和向量化，以支持语义搜索。
    *   结合传统的全文搜索引擎（如Elasticsearch, OpenSearch）以支持关键词搜索。

### 3.2 规则库 (Rule Base)

用于存储确定性的业务规则和决策逻辑。

*   **内容**: 
    *   “如果...那么...” (IF-THEN) 形式的业务规则。
    *   决策表（Decision Tables）。
    *   计费规则、折扣策略、风险评估阈值等。
*   **技术实现**: 
    *   使用专门的规则引擎（如Drools, Camunda DMN Engine）。
    *   规则可以以DMN (Decision Model and Notation)、YAML或自定义DSL的格式存储。

### 3.3 结构化数据库 (Structured Database)

用于存储实体及其关系的结构化数据。

*   **内容**: 
    *   产品目录（Product Catalogs）
    *   客户数据（在保护隐私的前提下）
    *   配置参数表
*   **技术实现**: 
    *   关系型数据库（PostgreSQL, MySQL）。
    *   图数据库（Neo4j, NebulaGraph），特别适合存储具有复杂关系的领域知识，可以视为智能上下文层`Knowledge Graph`在特定领域的具体实例或扩展。

### 3.4 API与工具定义库 (API & Tool Definition Store)

存储关于如何使用内部和外部API及工具的详细信息。

*   **内容**: 
    *   OpenAPI (Swagger) 规范文件。
    *   gRPC的`.proto`定义文件。
    *   自然语言描述的工具使用说明和示例。
*   **技术实现**: 
    *   存储在代码仓库或专门的配置中心。
    *   这些定义是`Capability Registry`中能力元数据的重要信息来源。

## 4. 关键接口设计

领域知识库本身不一定是一个单一的服务，而是一系列服务的集合。其“接口”体现在它如何被其他组件调用。

```python
# 这是一个概念性的接口，实际实现会分布在不同服务中
class DomainKnowledgeProvider:

    def __init__(self, vector_db_client, rule_engine_client, sql_db_client):
        self.vector_db = vector_db_client
        self.rule_engine = rule_engine_client
        self.sql_db = sql_db_client

    def semantic_search_documents(self, query: str, domain: str, top_k: int = 3) -> List[str]:
        """在特定领域的文档库中进行语义搜索"""
        # Calls the vector database
        chunks = self.vector_db.search(query, filter={'domain': domain}, top_k=top_k)
        return [chunk.text for chunk in chunks]

    def execute_decision(self, decision_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行一个业务决策"""
        # Calls the rule engine
        return self.rule_engine.evaluate(decision_name, context)

    def query_structured_data(self, sql_query: str) -> List[Dict[str, Any]]:
        """查询结构化数据"""
        # Executes a query against the relational database
        return self.sql_db.execute(sql_query)

    def get_api_spec(self, api_name: str) -> Dict[str, Any]:
        """获取API的规范"""
        # Fetches the OpenAPI spec from a store
        pass
```

## 5. 与其他组件的交互

*   **为RAG提供知识**: `Document Store`是`RAG System`中`Retriever`的主要信息源。当Agent需要回答基于文档的问题时，会从这里检索相关段落。
*   **为推理提供依据**: `Rule Base`和`Structured Database`为`Reasoning Engine`提供事实和规则。例如，在进行因果推理时，可以查询已知的业务规则。
*   **为规划和执行提供信息**: 
    *   `Planner`在生成计划时，可能会查询知识库以了解某个操作的前提条件或效果。
    *   `Execution Engine`中的原子能力在执行时，会调用`DomainKnowledgeProvider`来获取完成任务所需的数据（如执行一个SQL查询，或评估一个决策表）。
*   **与能力注册表的关系**: `API & Tool Definition Store`中的信息，经过处理和封装后，被注册到`Capability Registry`中，成为可被发现和调用的能力。

## 6. 实现考量

*   **知识获取与ETL**: 如何从各种来源（文档、网页、数据库）抽取知识并加载到知识库中是一个持续的挑战。需要建立自动化的ETL（Extract, Transform, Load）管道。
*   **知识表示**: 为不同的知识类型选择合适的表示方法至关重要。这可能涉及文档分块策略、向量模型选择、图模式设计等。
*   **知识的生命周期管理**: 知识会过时。需要建立审查和更新机制，确保知识库的准确性和时效性。
*   **访问权限**: 对于敏感的领域知识，需要有精细的访问控制机制。