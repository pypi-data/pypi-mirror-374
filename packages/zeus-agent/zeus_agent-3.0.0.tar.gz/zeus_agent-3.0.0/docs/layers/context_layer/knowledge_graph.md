# 知识图谱 (Knowledge Graph)

## 1. 概述

知识图谱是智能上下文层的核心组件之一，负责以结构化的方式存储和管理实体、概念及其之间的关系。它为Agent提供了深度的知识理解和推理能力，是实现高级认知功能的基础。

与向量数据库的相似性搜索不同，知识图谱能够捕捉实体之间明确的、语义丰富的关系，从而支持更复杂的查询和推理，例如多跳查询、路径发现、关系推断等。

## 2. 设计目标

*   **知识结构化**: 将非结构化和半结构化的信息（如文本、对话历史）转化为结构化的知识图谱。
*   **高效的图查询**: 支持高效的图遍历和模式匹配查询，快速检索相关知识。
*   **知识推理**: 能够基于图谱中的现有知识，推断出新的、隐含的关系。
*   **动态演化**: 知识图谱应能随着新的信息输入而动态地更新和扩展。
*   **可扩展性**: 能够支持大规模的知识图谱，并能方便地与其他知识源（如外部知识库）集成。
*   **多模态支持**: 支持存储和查询多模态信息（如文本、图片、链接）的节点和关系。

## 3. 核心组件

*   **GraphDBProvider**: 知识图谱的底层存储提供者，负责与具体的图数据库（如Neo4j, JanusGraph）进行交互。
*   **KnowledgeExtractor**: 知识提取器，负责从各种数据源（如文本、网页、对话）中提取实体、关系和属性。
*   **GraphBuilder**: 图谱构建器，将提取出的知识（三元组）加载到知识图谱中，处理节点的创建、更新和关系的连接。
*   **GraphQuerier**: 图谱查询器，提供统一的接口来查询知识图谱，支持模式匹配、路径查找等复杂查询。
*   **GraphEvolver**: 图谱演化器，负责知识图谱的动态更新、冲突解决和知识融合。

## 4. 关键接口设计

### 4.1 KnowledgeGraphManager接口

```python
from typing import List, Dict, Any

class KnowledgeGraphManager:
    def __init__(self, config: Dict[str, Any]):
        """初始化知识图谱管理器"""
        self.provider = self._initialize_provider(config.get("provider"))
        self.extractor = self._initialize_extractor(config.get("extractor"))
        self.builder = GraphBuilder(self.provider)
        self.querier = GraphQuerier(self.provider)
        self.evolver = GraphEvolver(self.provider)

    def _initialize_provider(self, provider_config: Dict[str, Any]):
        """初始化图数据库提供者"""
        # 根据配置动态加载Provider
        pass

    def _initialize_extractor(self, extractor_config: Dict[str, Any]):
        """初始化知识提取器"""
        # 根据配置动态加载Extractor
        pass

    def add_triples(self, triples: List[Dict[str, Any]]):
        """向图谱中添加三元组"""
        self.builder.add_triples(triples)

    def extract_and_add(self, source_data: Any, source_type: str):
        """从数据源中提取知识并添加到图谱中"""
        triples = self.extractor.extract(source_data, source_type)
        self.add_triples(triples)

    def query(self, query_pattern: str, query_lang: str = "cypher") -> List[Dict[str, Any]]:
        """查询知识图谱"""
        return self.querier.query(query_pattern, query_lang)

    def find_path(self, start_node: str, end_node: str, relation_type: str = None, max_hops: int = 3) -> List[List[Dict[str, Any]]]:
        """查找两个节点之间的路径"""
        return self.querier.find_path(start_node, end_node, relation_type, max_hops)

    def evolve_graph(self, new_data: Any):
        """演化知识图谱"""
        self.evolver.evolve(new_data)
```

### 4.2 GraphDBProvider接口

```python
class GraphDBProvider:
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行图查询"""
        raise NotImplementedError

    def add_node(self, label: str, properties: Dict[str, Any]) -> str:
        """添加节点"""
        raise NotImplementedError

    def add_edge(self, source_node_id: str, target_node_id: str, relation_type: str, properties: Dict[str, Any] = None):
        """添加边"""
        raise NotImplementedError

    def update_node(self, node_id: str, properties: Dict[str, Any]):
        """更新节点属性"""
        raise NotImplementedError
```

### 4.3 KnowledgeExtractor接口

```python
class KnowledgeExtractor:
    def extract(self, data: Any, source_type: str) -> List[Dict[str, Any]]:
        """从数据中提取知识三元组

        Args:
            data: 源数据 (文本, URL, etc.)
            source_type: 数据源类型 ('text', 'web', 'dialogue')

        Returns:
            一个三元组列表, e.g., [{'subject': 'PersonA', 'relation': 'knows', 'object': 'PersonB'}]
        """
        raise NotImplementedError
```

## 5. 实现示例

### 5.1 Neo4jGraphDBProvider

```python
from neo4j import GraphDatabase

class Neo4jGraphDBProvider(GraphDBProvider):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]

    # ... 其他接口的实现
```

### 5.2 LLMKnowledgeExtractor

使用大型语言模型（LLM）从非结构化文本中提取知识三元组。

```python
class LLMKnowledgeExtractor(KnowledgeExtractor):
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def extract(self, text: str, source_type: str) -> List[Dict[str, Any]]:
        prompt = f"""
        从以下文本中提取知识三元组 (主语, 关系, 宾语)。
        请将结果以JSON格式的列表返回，每个对象包含 'subject', 'relation', 'object' 三个键。
        文本: "{text}"
        """
        response = self.llm_client.generate(prompt)
        try:
            triples = json.loads(response)
            return triples
        except json.JSONDecodeError:
            return []
```

## 6. 知识图谱处理流程

1.  **知识提取**: `KnowledgeExtractor` 从输入数据（如用户对话、文档）中提取实体和关系。
2.  **图谱构建**: `GraphBuilder` 接收提取的三元组，对它们进行标准化处理（如实体对齐），然后调用 `GraphDBProvider` 将节点和边添加到图数据库中。
3.  **知识查询**: 当Agent需要特定知识时，`GraphQuerier` 将自然语言问题或查询模式转换为图查询语言（如Cypher），并从 `GraphDBProvider` 获取结果。
4.  **知识推理与演化**: `GraphEvolver` 定期或在事件触发时，分析图谱结构，进行知识推理（如链接预测），并融合新的知识，保持图谱的一致性和时效性。

## 7. 与其他组件的集成

*   **与MemorySystem的集成**: 知识图谱可以作为一种特殊的长期记忆。`MemorySystem`可以查询知识图谱来检索结构化知识，并可以将非结构化记忆通过`KnowledgeExtractor`转化为结构化知识存入图谱。
*   **与RAG系统的集成**: 在RAG流程中，知识图谱可以作为除向量数据库之外的另一个重要知识源。检索阶段可以同时查询向量库和知识图谱，将检索到的文本片段和结构化知识一起提供给生成模型，以产生更准确、更具深度的回答。