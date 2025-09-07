# 记忆系统设计文档

## 1. 概述

记忆系统（MemorySystem）是智能上下文层的核心组件之一，负责管理Agent的不同类型的记忆，使Agent能够存储、检索和利用过去的经验和知识。一个完善的记忆系统使Agent能够展现出类似人类的记忆能力，包括短期记忆、长期记忆、工作记忆等不同类型的记忆功能。

记忆系统不仅仅是简单的数据存储，它模拟了人类记忆的多层次结构和处理机制，包括记忆的编码、存储、检索和遗忘等过程。通过这些机制，Agent能够有效地管理和利用大量的信息，避免信息过载，同时保持对重要信息的长期记忆。

## 2. 设计目标

记忆系统的设计目标包括：

1. **多层次记忆**：支持不同类型的记忆，包括短期记忆、长期记忆、工作记忆、情景记忆和语义记忆等。

2. **高效检索**：提供高效的记忆检索机制，能够根据查询快速找到相关的记忆内容。

3. **记忆整合**：支持不同记忆之间的整合和关联，形成更丰富的知识网络。

4. **记忆演化**：实现记忆的自然演化过程，包括强化、衰减和遗忘等机制。

5. **个性化记忆**：支持为不同Agent或用户维护独立的记忆空间，实现个性化的记忆管理。

6. **可扩展性**：设计灵活的接口和扩展点，便于添加新的记忆类型和存储后端。

7. **性能优化**：优化记忆的存储和检索性能，减少延迟，提高响应速度。

## 3. 记忆类型

### 3.1 短期记忆（Short-term Memory）

短期记忆存储最近的交互和信息，具有容量有限、持续时间短的特点。主要用于维护当前对话或任务的即时上下文。

特点：
- 容量有限（通常7±2个项目）
- 持续时间短（通常不超过几分钟）
- 易受干扰和覆盖
- 快速访问

### 3.2 长期记忆（Long-term Memory）

长期记忆存储持久化的知识和经验，容量大，持续时间长。可以进一步分为陈述性记忆（事实和概念）和程序性记忆（技能和过程）。

特点：
- 容量大（理论上无限）
- 持续时间长（可持续数月甚至数年）
- 相对稳定，不易丢失
- 检索可能需要更多时间和线索

### 3.3 工作记忆（Working Memory）

工作记忆是短期记忆的一种特殊形式，用于临时存储和处理当前任务相关的信息。它是认知处理的核心，负责信息的临时保持和操作。

特点：
- 容量有限但可以通过组块化增加有效容量
- 用于主动处理和操作信息
- 与注意力机制密切相关
- 是复杂认知任务的基础

### 3.4 情景记忆（Episodic Memory）

情景记忆存储特定事件或经历的详细信息，包括时间、地点、相关情感等上下文信息。它使Agent能够回忆和重新体验过去的事件。

特点：
- 存储具体事件和经历
- 包含丰富的上下文信息
- 通常按时间顺序组织
- 与个人经历密切相关

### 3.5 语义记忆（Semantic Memory）

语义记忆存储概念性知识和事实，不依赖于特定的时间或地点。它是Agent理解世界和进行推理的基础。

特点：
- 存储概念、事实和一般知识
- 不依赖于特定的时间或地点
- 高度结构化和组织化
- 支持概念推理和知识应用

## 4. 核心组件

### 4.1 记忆管理器（MemoryManager）

记忆管理器是记忆系统的核心组件，负责协调和管理不同类型的记忆。主要职责包括：

- 初始化和配置不同类型的记忆
- 协调不同记忆之间的交互
- 管理记忆的生命周期
- 提供统一的记忆访问接口

### 4.2 记忆提供者（MemoryProvider）

记忆提供者负责实际的记忆存储和检索操作，支持不同类型的记忆和存储后端。每种记忆类型可以有专门的提供者实现：

- 短期记忆提供者：通常基于内存实现
- 长期记忆提供者：通常基于向量数据库或其他持久化存储
- 工作记忆提供者：通常基于高效的缓存机制
- 情景记忆提供者：通常基于时序数据库或事件存储
- 语义记忆提供者：通常基于知识图谱或结构化数据库

### 4.3 记忆编码器（MemoryEncoder）

记忆编码器负责将原始信息转换为适合存储的格式，包括：

- 文本编码：将文本转换为向量表示
- 结构化编码：将结构化数据转换为适合存储的格式
- 多模态编码：处理文本、图像、音频等多种模态的信息

### 4.4 记忆检索器（MemoryRetriever）

记忆检索器负责从记忆中检索相关信息，支持多种检索策略：

- 相似度检索：基于语义相似度
- 关键词检索：基于关键词匹配
- 时间检索：基于时间范围
- 上下文检索：基于当前上下文
- 混合检索：结合多种检索策略

### 4.5 记忆演化器（MemoryEvolver）

记忆演化器负责模拟记忆的自然演化过程，包括：

- 记忆强化：增强重要或频繁访问的记忆
- 记忆衰减：减弱不重要或长时间未访问的记忆
- 记忆整合：将相关记忆整合形成更高层次的知识
- 记忆遗忘：移除不再需要的记忆

## 5. 关键接口设计

### 5.1 MemorySystem接口

```python
class MemorySystem:
    def __init__(self, config=None):
        """初始化记忆系统
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
        self.memory_manager = MemoryManager(config)
    
    def initialize(self):
        """初始化记忆系统
        
        Returns:
            bool: 初始化是否成功
        """
        return self.memory_manager.initialize()
    
    def store(self, memory_type, data, metadata=None):
        """存储记忆
        
        Args:
            memory_type: 记忆类型（如short_term, long_term, working, episodic, semantic）
            data: 记忆数据
            metadata: 记忆元数据
            
        Returns:
            str: 记忆ID
        """
        return self.memory_manager.store(memory_type, data, metadata)
    
    def retrieve(self, memory_type, query, limit=10, filter_criteria=None):
        """检索记忆
        
        Args:
            memory_type: 记忆类型
            query: 检索查询
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 检索结果列表
        """
        return self.memory_manager.retrieve(memory_type, query, limit, filter_criteria)
    
    def retrieve_all_types(self, query, type_weights=None, limit=10, filter_criteria=None):
        """从所有类型的记忆中检索
        
        Args:
            query: 检索查询
            type_weights: 不同记忆类型的权重字典
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 检索结果列表
        """
        return self.memory_manager.retrieve_all_types(query, type_weights, limit, filter_criteria)
    
    def update(self, memory_id, data, metadata=None):
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            data: 更新的数据
            metadata: 更新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        return self.memory_manager.update(memory_id, data, metadata)
    
    def delete(self, memory_id):
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        return self.memory_manager.delete(memory_id)
    
    def forget(self, memory_type=None, filter_criteria=None, before_timestamp=None):
        """遗忘记忆
        
        Args:
            memory_type: 记忆类型（如果为None，则应用于所有类型）
            filter_criteria: 过滤条件
            before_timestamp: 指定时间戳之前的记忆
            
        Returns:
            int: 遗忘的记忆数量
        """
        return self.memory_manager.forget(memory_type, filter_criteria, before_timestamp)
    
    def get_memory_by_id(self, memory_id):
        """通过ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            dict: 记忆数据
        """
        return self.memory_manager.get_memory_by_id(memory_id)
    
    def get_memory_types(self):
        """获取支持的记忆类型
        
        Returns:
            list: 记忆类型列表
        """
        return self.memory_manager.get_memory_types()
    
    def get_statistics(self):
        """获取记忆统计信息
        
        Returns:
            dict: 统计信息
        """
        return self.memory_manager.get_statistics()
    
    def clear(self, memory_type=None):
        """清除记忆
        
        Args:
            memory_type: 记忆类型（如果为None，则清除所有类型）
            
        Returns:
            bool: 清除是否成功
        """
        return self.memory_manager.clear(memory_type)
```

### 5.2 MemoryManager接口

```python
class MemoryManager:
    def __init__(self, config=None):
        """初始化记忆管理器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
        self.providers = {}
        self.encoder = None
        self.retriever = None
        self.evolver = None
    
    def initialize(self):
        """初始化记忆管理器
        
        Returns:
            bool: 初始化是否成功
        """
        # 初始化各种记忆提供者
        self._initialize_providers()
        
        # 初始化编码器、检索器和演化器
        self._initialize_encoder()
        self._initialize_retriever()
        self._initialize_evolver()
        
        return True
    
    def _initialize_providers(self):
        """初始化记忆提供者"""
        # 根据配置初始化不同类型的记忆提供者
        memory_types = self.config.get("memory_types", ["short_term", "long_term", "working", "episodic", "semantic"])
        
        for memory_type in memory_types:
            provider_config = self.config.get(f"{memory_type}_provider", {})
            provider_class = self._get_provider_class(memory_type)
            self.providers[memory_type] = provider_class(provider_config)
    
    def _initialize_encoder(self):
        """初始化记忆编码器"""
        encoder_config = self.config.get("encoder", {})
        encoder_class = self._get_encoder_class()
        self.encoder = encoder_class(encoder_config)
    
    def _initialize_retriever(self):
        """初始化记忆检索器"""
        retriever_config = self.config.get("retriever", {})
        retriever_class = self._get_retriever_class()
        self.retriever = retriever_class(retriever_config)
    
    def _initialize_evolver(self):
        """初始化记忆演化器"""
        evolver_config = self.config.get("evolver", {})
        evolver_class = self._get_evolver_class()
        self.evolver = evolver_class(evolver_config)
    
    def _get_provider_class(self, memory_type):
        """获取记忆提供者类
        
        Args:
            memory_type: 记忆类型
            
        Returns:
            class: 记忆提供者类
        """
        # 根据记忆类型返回对应的提供者类
        provider_mapping = {
            "short_term": ShortTermMemoryProvider,
            "long_term": LongTermMemoryProvider,
            "working": WorkingMemoryProvider,
            "episodic": EpisodicMemoryProvider,
            "semantic": SemanticMemoryProvider
        }
        
        return provider_mapping.get(memory_type, BaseMemoryProvider)
    
    def _get_encoder_class(self):
        """获取记忆编码器类
        
        Returns:
            class: 记忆编码器类
        """
        encoder_type = self.config.get("encoder_type", "default")
        encoder_mapping = {
            "default": DefaultMemoryEncoder,
            "text": TextMemoryEncoder,
            "multimodal": MultiModalMemoryEncoder
        }
        
        return encoder_mapping.get(encoder_type, DefaultMemoryEncoder)
    
    def _get_retriever_class(self):
        """获取记忆检索器类
        
        Returns:
            class: 记忆检索器类
        """
        retriever_type = self.config.get("retriever_type", "default")
        retriever_mapping = {
            "default": DefaultMemoryRetriever,
            "similarity": SimilarityMemoryRetriever,
            "hybrid": HybridMemoryRetriever
        }
        
        return retriever_mapping.get(retriever_type, DefaultMemoryRetriever)
    
    def _get_evolver_class(self):
        """获取记忆演化器类
        
        Returns:
            class: 记忆演化器类
        """
        evolver_type = self.config.get("evolver_type", "default")
        evolver_mapping = {
            "default": DefaultMemoryEvolver,
            "adaptive": AdaptiveMemoryEvolver,
            "reinforcement": ReinforcementMemoryEvolver
        }
        
        return evolver_mapping.get(evolver_type, DefaultMemoryEvolver)
    
    def store(self, memory_type, data, metadata=None):
        """存储记忆
        
        Args:
            memory_type: 记忆类型
            data: 记忆数据
            metadata: 记忆元数据
            
        Returns:
            str: 记忆ID
        """
        if memory_type not in self.providers:
            raise ValueError(f"Unsupported memory type: {memory_type}")
        
        # 编码数据
        encoded_data = self.encoder.encode(data, memory_type)
        
        # 准备元数据
        full_metadata = metadata or {}
        full_metadata["timestamp"] = datetime.now().isoformat()
        full_metadata["memory_type"] = memory_type
        
        # 存储记忆
        memory_id = self.providers[memory_type].store(encoded_data, full_metadata)
        
        # 触发记忆演化
        self.evolver.on_memory_stored(memory_id, memory_type, encoded_data, full_metadata)
        
        return memory_id
    
    def retrieve(self, memory_type, query, limit=10, filter_criteria=None):
        """检索记忆
        
        Args:
            memory_type: 记忆类型
            query: 检索查询
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 检索结果列表
        """
        if memory_type not in self.providers:
            raise ValueError(f"Unsupported memory type: {memory_type}")
        
        # 编码查询
        encoded_query = self.encoder.encode(query, memory_type)
        
        # 检索记忆
        results = self.retriever.retrieve(
            self.providers[memory_type],
            encoded_query,
            limit,
            filter_criteria
        )
        
        # 触发记忆演化
        for result in results:
            self.evolver.on_memory_retrieved(result["id"], memory_type, result["data"], result["metadata"])
        
        return results
    
    def retrieve_all_types(self, query, type_weights=None, limit=10, filter_criteria=None):
        """从所有类型的记忆中检索
        
        Args:
            query: 检索查询
            type_weights: 不同记忆类型的权重字典
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 检索结果列表
        """
        # 默认权重
        default_weights = {
            "short_term": 1.0,
            "long_term": 0.8,
            "working": 1.0,
            "episodic": 0.7,
            "semantic": 0.6
        }
        
        weights = type_weights or default_weights
        
        # 从各类型记忆中检索
        all_results = []
        for memory_type, provider in self.providers.items():
            if memory_type not in weights:
                continue
                
            # 编码查询
            encoded_query = self.encoder.encode(query, memory_type)
            
            # 检索记忆
            results = self.retriever.retrieve(
                provider,
                encoded_query,
                limit * 2,  # 检索更多结果，后面会合并和排序
                filter_criteria
            )
            
            # 添加记忆类型和权重
            for result in results:
                result["memory_type"] = memory_type
                result["weight"] = weights[memory_type]
                all_results.append(result)
        
        # 合并和排序结果
        sorted_results = sorted(
            all_results,
            key=lambda x: x["score"] * x["weight"],
            reverse=True
        )[:limit]
        
        # 触发记忆演化
        for result in sorted_results:
            self.evolver.on_memory_retrieved(
                result["id"],
                result["memory_type"],
                result["data"],
                result["metadata"]
            )
        
        return sorted_results
    
    def update(self, memory_id, data, metadata=None):
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            data: 更新的数据
            metadata: 更新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        # 查找记忆所属的提供者
        for memory_type, provider in self.providers.items():
            memory = provider.get_by_id(memory_id)
            if memory:
                # 编码数据
                encoded_data = self.encoder.encode(data, memory_type)
                
                # 准备元数据
                full_metadata = metadata or {}
                full_metadata["updated_at"] = datetime.now().isoformat()
                
                # 更新记忆
                success = provider.update(memory_id, encoded_data, full_metadata)
                
                # 触发记忆演化
                if success:
                    self.evolver.on_memory_updated(memory_id, memory_type, encoded_data, full_metadata)
                
                return success
        
        return False
    
    def delete(self, memory_id):
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        # 查找记忆所属的提供者
        for memory_type, provider in self.providers.items():
            memory = provider.get_by_id(memory_id)
            if memory:
                # 删除记忆
                success = provider.delete(memory_id)
                
                # 触发记忆演化
                if success:
                    self.evolver.on_memory_deleted(memory_id, memory_type)
                
                return success
        
        return False
    
    def forget(self, memory_type=None, filter_criteria=None, before_timestamp=None):
        """遗忘记忆
        
        Args:
            memory_type: 记忆类型（如果为None，则应用于所有类型）
            filter_criteria: 过滤条件
            before_timestamp: 指定时间戳之前的记忆
            
        Returns:
            int: 遗忘的记忆数量
        """
        # 准备过滤条件
        full_filter = filter_criteria or {}
        if before_timestamp:
            full_filter["timestamp"] = {"$lt": before_timestamp}
        
        # 确定要处理的记忆类型
        target_types = [memory_type] if memory_type else list(self.providers.keys())
        
        # 遗忘记忆
        total_forgotten = 0
        for type_name in target_types:
            if type_name not in self.providers:
                continue
                
            # 获取要遗忘的记忆ID列表
            memories_to_forget = self.providers[type_name].query(full_filter)
            
            # 遗忘记忆
            forgotten_count = 0
            for memory in memories_to_forget:
                if self.providers[type_name].delete(memory["id"]):
                    # 触发记忆演化
                    self.evolver.on_memory_forgotten(memory["id"], type_name)
                    forgotten_count += 1
            
            total_forgotten += forgotten_count
        
        return total_forgotten
    
    def get_memory_by_id(self, memory_id):
        """通过ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            dict: 记忆数据
        """
        # 查找记忆所属的提供者
        for memory_type, provider in self.providers.items():
            memory = provider.get_by_id(memory_id)
            if memory:
                # 触发记忆演化
                self.evolver.on_memory_retrieved(
                    memory_id,
                    memory_type,
                    memory["data"],
                    memory["metadata"]
                )
                
                return memory
        
        return None
    
    def get_memory_types(self):
        """获取支持的记忆类型
        
        Returns:
            list: 记忆类型列表
        """
        return list(self.providers.keys())
    
    def get_statistics(self):
        """获取记忆统计信息
        
        Returns:
            dict: 统计信息
        """
        stats = {}
        for memory_type, provider in self.providers.items():
            stats[memory_type] = provider.get_statistics()
        return stats
    
    def clear(self, memory_type=None):
        """清除记忆
        
        Args:
            memory_type: 记忆类型（如果为None，则清除所有类型）
            
        Returns:
            bool: 清除是否成功
        """
        if memory_type:
            if memory_type not in self.providers:
                return False
            return self.providers[memory_type].clear()
        else:
            success = True
            for provider in self.providers.values():
                if not provider.clear():
                    success = False
            return success
```

### 5.3 MemoryProvider接口

```python
class MemoryProvider:
    def __init__(self, config=None):
        """初始化记忆提供者
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def store(self, data, metadata=None):
        """存储记忆
        
        Args:
            data: 记忆数据
            metadata: 记忆元数据
            
        Returns:
            str: 记忆ID
        """
        pass
    
    def get_by_id(self, memory_id):
        """通过ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            dict: 记忆数据
        """
        pass
    
    def query(self, filter_criteria=None, limit=None):
        """查询记忆
        
        Args:
            filter_criteria: 过滤条件
            limit: 返回结果的最大数量
            
        Returns:
            list: 查询结果列表
        """
        # 实现基于元数据的查询
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            query_str = "SELECT data FROM memory_metadata"
            params = []
            
            if filter_criteria:
                query_str += " WHERE " + " AND ".join([f"{k} = ?" for k in filter_criteria.keys()])
                params.extend(filter_criteria.values())
            
            if limit:
                query_str += " LIMIT ?"
                params.append(limit)
                
            cursor = self.metadata_db.cursor()
            cursor.execute(query_str, params)
            results = [json.loads(row[0]) for row in cursor.fetchall()]
            return results

        elif db_type == "mongodb":
            query = self.metadata_db.find(filter_criteria)
            if limit:
                query = query.limit(limit)
            return list(query)
            
        else:
            # 内存存储
            results = []
            for item in self.metadata_db.values():
                match = True
                if filter_criteria:
                    for key, value in filter_criteria.items():
                        if item.get(key) != value:
                            match = False
                            break
                if match:
                    results.append(item)
                if limit and len(results) >= limit:
                    break
            return results

    def search(self, query, limit=10, filter_criteria=None):
        """搜索记忆 (向量相似度搜索)
        
        Args:
            query: 搜索查询 (向量表示)
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 搜索结果列表
        """
        db_type = self.config.get("vector_db_type", "pinecone")

        if db_type == "pinecone":
            results = self.vector_db.query(
                vector=query,
                top_k=limit,
                filter=filter_criteria,
                include_metadata=True
            )
            return [{"id": r.id, "score": r.score, "metadata": r.metadata} for r in results.matches]

        elif db_type == "milvus":
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.vector_db.search(
                data=[query],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=filter_criteria
            )
            # 处理Milvus返回的结果
            return [{"id": hit.id, "score": hit.distance, "metadata": {}} for hit in results[0]]

        elif db_type == "qdrant":
            client = self.vector_db["client"]
            collection = self.vector_db["collection"]
            
            hits = client.search(
                collection_name=collection,
                query_vector=query,
                query_filter=filter_criteria,
                limit=limit
            )
            return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in hits]
            
        else:
            # 内存向量存储
            return self.vector_db.search(query, limit, filter_criteria)

    def update(self, memory_id, data, metadata=None):
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            data: 更新的数据 (向量表示)
            metadata: 更新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        # 获取旧的元数据
        old_metadata = self._get_metadata(memory_id)
        if not old_metadata:
            return False
            
        # 准备新的元数据
        full_metadata = metadata or {}
        full_metadata["updated_at"] = datetime.now().isoformat()
        
        # 更新向量
        self._store_vector(memory_id, data, full_metadata)
        
        # 更新元数据
        self._update_metadata(memory_id, full_metadata)
        
        return True

    def _update_metadata(self, memory_id, metadata):
        """更新元数据
        
        Args:
            memory_id: 记忆ID
            metadata: 元数据
        """
        db_type = self.config.get("metadata_db_type", "sqlite")

        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute(
                "UPDATE memory_metadata SET data = ?, updated_at = ? WHERE id = ?",
                (json.dumps(metadata), metadata["updated_at"], memory_id)
            )
            self.metadata_db.commit()

        elif db_type == "mongodb":
            self.metadata_db.update_one({"id": memory_id}, {"$set": metadata})
            
        else:
            # 内存存储
            if memory_id in self.metadata_db:
                self.metadata_db[memory_id].update(metadata)

    def delete(self, memory_id):
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        # 删除向量
        self._delete_vector(memory_id)
        
        # 删除元数据
        self._delete_metadata(memory_id)
        
        return True

    def _delete_vector(self, memory_id):
        """删除向量
        
        Args:
            memory_id: 记忆ID
        """
        db_type = self.config.get("vector_db_type", "pinecone")

        if db_type == "pinecone":
            self.vector_db.delete(ids=[memory_id])

        elif db_type == "milvus":
            self.vector_db.delete(f"id in ['{memory_id}']")

        elif db_type == "qdrant":
            client = self.vector_db["client"]
            collection = self.vector_db["collection"]
            client.delete(collection_name=collection, points_selector=[memory_id])
            
        else:
            # 内存向量存储
            self.vector_db.delete(memory_id)

    def _delete_metadata(self, memory_id):
        """删除元数据
        
        Args:
            memory_id: 记忆ID
        """
        db_type = self.config.get("metadata_db_type", "sqlite")

        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute("DELETE FROM memory_metadata WHERE id = ?", (memory_id,))
            self.metadata_db.commit()

        elif db_type == "mongodb":
            self.metadata_db.delete_one({"id": memory_id})
            
        else:
            # 内存存储
            if memory_id in self.metadata_db:
                del self.metadata_db[memory_id]

    def clear(self):
        """清除所有记忆
        
        Returns:
            bool: 清除是否成功
        """
        # 清除向量数据库
        db_type = self.config.get("vector_db_type", "pinecone")
        if db_type == "pinecone":
            self.vector_db.delete(delete_all=True)
        # ... 其他向量数据库的清除逻辑
        
        # 清除元数据数据库
        meta_db_type = self.config.get("metadata_db_type", "sqlite")
        if meta_db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute("DELETE FROM memory_metadata")
            self.metadata_db.commit()
        elif meta_db_type == "mongodb":
            self.metadata_db.delete_many({})
        else:
            self.metadata_db.clear()
            
        return True

    def get_statistics(self):
        """获取统计信息
        
        Returns:
            dict: 统计信息
        """
        # 实现统计信息获取
        count = 0
        meta_db_type = self.config.get("metadata_db_type", "sqlite")
        if meta_db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_metadata")
            count = cursor.fetchone()[0]
        elif meta_db_type == "mongodb":
            count = self.metadata_db.count_documents({})
        else:
            count = len(self.metadata_db)
            
        return {"total_memories": count}

## 7. 记忆处理流程

### 7.1 记忆存储流程

1.  **接收请求**: `MemorySystem`接收到外部存储记忆的请求，包含数据和可选的元数据。
2.  **编码**: `MemoryManager`调用`MemoryEncoder`对数据进行编码，转换成适合存储的格式（如向量）。
3.  **选择Provider**: `MemoryManager`根据记忆类型（如`long_term`）选择对应的`MemoryProvider`。
4.  **存储**: `MemoryProvider`将编码后的数据和元数据存入底层数据库（向量数据库和元数据数据库）。
5.  **演化**: `MemoryManager`通知`MemoryEvolver`有新的记忆被存储，触发记忆演化逻辑（如更新权重、建立关联）。

### 7.2 记忆检索流程

1.  **接收请求**: `MemorySystem`接收到外部检索记忆的请求，包含查询和过滤条件。
2.  **编码查询**: `MemoryManager`调用`MemoryEncoder`对查询进行编码。
3.  **选择Provider**: `MemoryManager`根据指定的记忆类型或所有类型选择一个或多个`MemoryProvider`。
4.  **检索**: `MemoryRetriever`调用`MemoryProvider`的搜索或查询接口，从底层数据库中检索相关记忆。
5.  **排序和过滤**: `MemoryRetriever`对检索结果进行排序、合并和过滤，返回最相关的结果。
6.  **演化**: `MemoryManager`通知`MemoryEvolver`相关的记忆被检索，触发记忆演化逻辑（如更新访问频率、调整重要性）。

## 8. 性能考虑

*   **缓存**: 对于频繁访问的记忆，可以在`MemoryManager`层面增加缓存，减少对底层数据库的访问。
*   **批量操作**: `MemoryProvider`应支持批量存储、更新和删除操作，以提高I/O效率。
*   **索引优化**: 优化向量数据库和元数据数据库的索引策略，加快检索速度。
*   **异步处理**: 对于非核心的记忆演化任务，可以采用异步处理，避免阻塞主流程。

## 9. 可扩展性

*   **自定义Provider**: 用户可以实现自己的`MemoryProvider`来对接不同的存储后端。
*   **自定义Encoder/Retriever/Evolver**: 用户可以根据业务需求，实现自定义的编码、检索和演化逻辑。
*   **插件化机制**: 通过工厂模式和注册机制，可以动态地加载和使用自定义的组件。

## 10. 与其他组件的集成

*   **与上下文管理器的集成**: `ContextManager`在构建上下文时，会调用`MemorySystem`来检索相关记忆，丰富上下文内容。
*   **与认知核心的集成**: Agent的认知循环（如思考、学习）会与`MemorySystem`进行交互，实现记忆的存储、更新和应用。


        pass
    
    def search(self, query, limit=10, filter_criteria=None):
        """搜索记忆
        
        Args:
            query: 搜索查询
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 搜索结果列表
        """
        pass
    
    def update(self, memory_id, data, metadata=None):
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            data: 更新的数据
            metadata: 更新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    def delete(self, memory_id):
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    def clear(self):
        """清除所有记忆
        
        Returns:
            bool: 清除是否成功
        """
        pass
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            dict: 统计信息
        """
        pass
```

### 5.4 MemoryEncoder接口

```python
class MemoryEncoder:
    def __init__(self, config=None):
        """初始化记忆编码器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def encode(self, data, memory_type=None):
        """编码数据
        
        Args:
            data: 原始数据
            memory_type: 记忆类型
            
        Returns:
            object: 编码后的数据
        """
        pass
    
    def decode(self, encoded_data, memory_type=None):
        """解码数据
        
        Args:
            encoded_data: 编码后的数据
            memory_type: 记忆类型
            
        Returns:
            object: 解码后的数据
        """
        pass
```

### 5.5 MemoryRetriever接口

```python
class MemoryRetriever:
    def __init__(self, config=None):
        """初始化记忆检索器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def retrieve(self, provider, query, limit=10, filter_criteria=None):
        """检索记忆
        
        Args:
            provider: 记忆提供者
            query: 检索查询
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 检索结果列表
        """
        pass
    
    def rank(self, results, query):
        """对结果进行排序
        
        Args:
            results: 检索结果
            query: 检索查询
            
        Returns:
            list: 排序后的结果
        """
        pass
```

### 5.6 MemoryEvolver接口

```python
class MemoryEvolver:
    def __init__(self, config=None):
        """初始化记忆演化器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def on_memory_stored(self, memory_id, memory_type, data, metadata):
        """记忆存储事件处理
        
        Args:
            memory_id: 记忆ID
            memory_type: 记忆类型
            data: 记忆数据
            metadata: 记忆元数据
        """
        pass
    
    def on_memory_retrieved(self, memory_id, memory_type, data, metadata):
        """记忆检索事件处理
        
        Args:
            memory_id: 记忆ID
            memory_type: 记忆类型
            data: 记忆数据
            metadata: 记忆元数据
        """
        pass
    
    def on_memory_updated(self, memory_id, memory_type, data, metadata):
        """记忆更新事件处理
        
        Args:
            memory_id: 记忆ID
            memory_type: 记忆类型
            data: 记忆数据
            metadata: 记忆元数据
        """
        pass
    
    def on_memory_deleted(self, memory_id, memory_type):
        """记忆删除事件处理
        
        Args:
            memory_id: 记忆ID
            memory_type: 记忆类型
        """
        pass
    
    def on_memory_forgotten(self, memory_id, memory_type):
        """记忆遗忘事件处理
        
        Args:
            memory_id: 记忆ID
            memory_type: 记忆类型
        """
        pass
    
    def evolve(self):
        """执行记忆演化
        
        Returns:
            dict: 演化结果
        """
        pass
```

## 6. 实现示例

### 6.1 向量数据库长期记忆提供者

```python
class VectorDBLongTermMemoryProvider(MemoryProvider):
    def __init__(self, config=None):
        super().__init__(config)
        self.vector_db = self._initialize_vector_db()
        self.metadata_db = self._initialize_metadata_db()
    
    def _initialize_vector_db(self):
        """初始化向量数据库
        
        Returns:
            object: 向量数据库连接
        """
        db_type = self.config.get("vector_db_type", "pinecone")
        
        if db_type == "pinecone":
            import pinecone
            api_key = self.config.get("pinecone_api_key")
            environment = self.config.get("pinecone_environment")
            index_name = self.config.get("pinecone_index_name")
            
            pinecone.init(api_key=api_key, environment=environment)
            return pinecone.Index(index_name)
        
        elif db_type == "milvus":
            from pymilvus import connections, Collection
            host = self.config.get("milvus_host", "localhost")
            port = self.config.get("milvus_port", 19530)
            collection_name = self.config.get("milvus_collection")
            
            connections.connect(host=host, port=port)
            return Collection(name=collection_name)
        
        elif db_type == "qdrant":
            from qdrant_client import QdrantClient
            host = self.config.get("qdrant_host", "localhost")
            port = self.config.get("qdrant_port", 6333)
            collection_name = self.config.get("qdrant_collection")
            
            client = QdrantClient(host=host, port=port)
            return {"client": client, "collection": collection_name}
        
        else:
            # 默认使用内存向量存储
            return InMemoryVectorStore()
    
    def _initialize_metadata_db(self):
        """初始化元数据数据库
        
        Returns:
            object: 元数据数据库连接
        """
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            import sqlite3
            db_path = self.config.get("sqlite_db_path", "memory.db")
            conn = sqlite3.connect(db_path)
            
            # 创建表（如果不存在）
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_metadata (
                    id TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()
            
            return conn
        
        elif db_type == "mongodb":
            from pymongo import MongoClient
            uri = self.config.get("mongodb_uri", "mongodb://localhost:27017")
            db_name = self.config.get("mongodb_db", "memory_system")
            collection_name = self.config.get("mongodb_collection", "memory_metadata")
            
            client = MongoClient(uri)
            db = client[db_name]
            return db[collection_name]
        
        else:
            # 默认使用内存存储
            return {}
    
    def store(self, data, metadata=None):
        """存储记忆
        
        Args:
            data: 记忆数据（向量表示）
            metadata: 记忆元数据
            
        Returns:
            str: 记忆ID
        """
        # 生成唯一ID
        memory_id = str(uuid.uuid4())
        
        # 准备元数据
        full_metadata = metadata or {}
        full_metadata["id"] = memory_id
        full_metadata["created_at"] = datetime.now().isoformat()
        full_metadata["updated_at"] = full_metadata["created_at"]
        
        # 存储向量数据
        self._store_vector(memory_id, data, full_metadata)
        
        # 存储元数据
        self._store_metadata(memory_id, full_metadata)
        
        return memory_id
    
    def _store_vector(self, memory_id, vector_data, metadata):
        """存储向量数据
        
        Args:
            memory_id: 记忆ID
            vector_data: 向量数据
            metadata: 元数据
        """
        db_type = self.config.get("vector_db_type", "pinecone")
        
        if db_type == "pinecone":
            self.vector_db.upsert([(memory_id, vector_data, metadata)])
        
        elif db_type == "milvus":
            # Milvus需要特定的插入格式
            self.vector_db.insert([memory_id], [vector_data], [metadata])
        
        elif db_type == "qdrant":
            client = self.vector_db["client"]
            collection = self.vector_db["collection"]
            client.upsert(
                collection_name=collection,
                points=[(memory_id, vector_data, metadata)]
            )
        
        else:
            # 内存向量存储
            self.vector_db.add(memory_id, vector_data, metadata)
    
    def _store_metadata(self, memory_id, metadata):
        """存储元数据
        
        Args:
            memory_id: 记忆ID
            metadata: 元数据
        """
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute(
                "INSERT INTO memory_metadata (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (memory_id, json.dumps(metadata), metadata["created_at"], metadata["updated_at"])
            )
            self.metadata_db.commit()
        
        elif db_type == "mongodb":
            self.metadata_db.insert_one(metadata)
        
        else:
            # 内存存储
            self.metadata_db[memory_id] = metadata
    
    def get_by_id(self, memory_id):
        """通过ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            dict: 记忆数据
        """
        # 获取元数据
        metadata = self._get_metadata(memory_id)
        if not metadata:
            return None
        
        # 获取向量数据
        vector_data = self._get_vector(memory_id)
        if vector_data is None:
            return None
        
        return {
            "id": memory_id,
            "data": vector_data,
            "metadata": metadata
        }
    
    def _get_metadata(self, memory_id):
        """获取元数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            dict: 元数据
        """
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute("SELECT data FROM memory_metadata WHERE id = ?", (memory_id,))
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            return None
        
        elif db_type == "mongodb":
            result = self.metadata_db.find_one({"id": memory_id})
            return result
        
        else:
            # 内存存储
            return self.metadata_db.get(memory_id)
    
    def _get_vector(self, memory_id):
        """获取向量数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            list: 向量数据
        """
        db_type = self.config.get("vector_db_type", "pinecone")
        
        if db_type == "pinecone":
            result = self.vector_db.fetch([memory_id])
            if result and result.get("vectors") and memory_id in result["vectors"]:
                return result["vectors"][memory_id]["values"]
            return None
        
        elif db_type == "milvus":
            result = self.vector_db.query(expr=f"id == '{memory_id}'", output_fields=["embedding"])
            if result and len(result) > 0:
                return result[0]["embedding"]
            return None
        
        elif db_type == "qdrant":
            client = self.vector_db["client"]
            collection = self.vector_db["collection"]
            result = client.retrieve(
                collection_name=collection,
                ids=[memory_id]
            )
            if result and len(result) > 0:
                return result[0].vector
            return None
        
        else:
            # 内存向量存储
            return self.vector_db.get(memory_id)
    
    def query(self, filter_criteria=None, limit=None):
        """查询记忆
        
        Args:
            filter_criteria: 过滤条件
            limit: 返回结果的最大数量
            
        Returns:
            list: 查询结果列表
        """
        # 实现基于元数据的查询
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            query = "SELECT id, data FROM memory_metadata"
            
            # 构建WHERE子句
            where_clauses = []
            params = []
            
            if filter_criteria:
                for key, value in filter_criteria.items():
                    # 简单处理，实际应用中可能需要更复杂的查询构建
                    if isinstance(value, dict) and "$lt" in value:
                        where_clauses.append(f"json_extract(data, '$.{key}') < ?")
                        params.append(value["$lt"])
                    else:
                        where_clauses.append(f"json_extract(data, '$.{key}') = ?")
                        params.append(str(value))
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            if limit is not None:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            results = []
            
            for row in cursor.fetchall():
                memory_id = row[0]
                metadata = json.loads(row[1])
                vector_data = self._get_vector(memory_id)
                
                results.append({
                    "id": memory_id,
                    "data": vector_data,
                    "metadata": metadata
                })
            
            return results
        
        elif db_type == "mongodb":
            query = filter_criteria or {}
            cursor = self.metadata_db.find(query)
            
            if limit is not None:
                cursor = cursor.limit(limit)
            
            results = []
            for doc in cursor:
                memory_id = doc["id"]
                vector_data = self._get_vector(memory_id)
                
                results.append({
                    "id": memory_id,
                    "data": vector_data,
                    "metadata": doc
                })
            
            return results
        
        else:
            # 内存存储
            results = []
            for memory_id, metadata in self.metadata_db.items():
                # 应用过滤条件
                if filter_criteria and not self._match_filter(metadata, filter_criteria):
                    continue
                
                vector_data = self._get_vector(memory_id)
                results.append({
                    "id": memory_id,
                    "data": vector_data,
                    "metadata": metadata
                })
                
                if limit is not None and len(results) >= limit:
                    break
            
            return results
    
    def _match_filter(self, metadata, filter_criteria):
        """检查元数据是否匹配过滤条件
        
        Args:
            metadata: 元数据
            filter_criteria: 过滤条件
            
        Returns:
            bool: 是否匹配
        """
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
            
            if isinstance(value, dict):
                # 处理比较操作符
                if "$lt" in value and not (metadata[key] < value["$lt"]):
                    return False
                if "$gt" in value and not (metadata[key] > value["$gt"]):
                    return False
                if "$lte" in value and not (metadata[key] <= value["$lte"]):
                    return False
                if "$gte" in value and not (metadata[key] >= value["$gte"]):
                    return False
                if "$ne" in value and metadata[key] == value["$ne"]:
                    return False
            else:
                # 直接比较
                if metadata[key] != value:
                    return False
        
        return True
    
    def search(self, query, limit=10, filter_criteria=None):
        """搜索记忆
        
        Args:
            query: 搜索查询（向量表示）
            limit: 返回结果的最大数量
            filter_criteria: 过滤条件
            
        Returns:
            list: 搜索结果列表
        """
        db_type = self.config.get("vector_db_type", "pinecone")
        
        if db_type == "pinecone":
            # 构建过滤条件
            filter_dict = {}
            if filter_criteria:
                for key, value in filter_criteria.items():
                    if isinstance(value, dict):
                        # 处理比较操作符
                        for op, val in value.items():
                            if op == "$lt":
                                filter_dict[key] = {"$lt": val}
                            elif op == "$gt":
                                filter_dict[key] = {"$gt": val}
                            elif op == "$lte":
                                filter_dict[key] = {"$lte": val}
                            elif op == "$gte":
                                filter_dict[key] = {"$gte": val}
                            elif op == "$ne":
                                filter_dict[key] = {"$ne": val}
                    else:
                        filter_dict[key] = value
            
            # 执行向量搜索
            results = self.vector_db.query(
                vector=query,
                top_k=limit,
                filter=filter_dict if filter_dict else None,
                include_metadata=True
            )
            
            # 处理结果
            search_results = []
            for match in results.get("matches", []):
                search_results.append({
                    "id": match["id"],
                    "data": match["values"],
                    "metadata": match["metadata"],
                    "score": match["score"]
                })
            
            return search_results
        
        elif db_type == "milvus":
            # 构建搜索参数
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            expr = None
            
            # 构建过滤表达式
            if filter_criteria:
                conditions = []
                for key, value in filter_criteria.items():
                    if isinstance(value, dict):
                        # 处理比较操作符
                        for op, val in value.items():
                            if op == "$lt":
                                conditions.append(f"{key} < '{val}'")
                            elif op == "$gt":
                                conditions.append(f"{key} > '{val}'")
                            elif op == "$lte":
                                conditions.append(f"{key} <= '{val}'")
                            elif op == "$gte":
                                conditions.append(f"{key} >= '{val}'")
                            elif op == "$ne":
                                conditions.append(f"{key} != '{val}'")
                    else:
                        conditions.append(f"{key} == '{value}'")
                
                if conditions:
                    expr = " and ".join(conditions)
            
            # 执行向量搜索
            results = self.vector_db.search(
                data=[query],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=["*"]
            )
            
            # 处理结果
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "id": hit.id,
                        "data": hit.embedding,
                        "metadata": {k: v for k, v in hit.entity.items() if k != "embedding"},
                        "score": hit.distance
                    })
            
            return search_results
        
        elif db_type == "qdrant":
            client = self.vector_db["client"]
            collection = self.vector_db["collection"]
            
            # 构建过滤条件
            filter_dict = None
            if filter_criteria:
                conditions = []
                for key, value in filter_criteria.items():
                    if isinstance(value, dict):
                        # 处理比较操作符
                        for op, val in value.items():
                            if op == "$lt":
                                conditions.append({"key": key, "range": {"lt": val}})
                            elif op == "$gt":
                                conditions.append({"key": key, "range": {"gt": val}})
                            elif op == "$lte":
                                conditions.append({"key": key, "range": {"lte": val}})
                            elif op == "$gte":
                                conditions.append({"key": key, "range": {"gte": val}})
                            elif op == "$ne":
                                conditions.append({"key": key, "match": {"value": val, "must_not": True}})
                    else:
                        conditions.append({"key": key, "match": {"value": value}})
                
                if conditions:
                    filter_dict = {"must": conditions}
            
            # 执行向量搜索
            results = client.search(
                collection_name=collection,
                query_vector=query,
                limit=limit,
                query_filter=filter_dict
            )
            
            # 处理结果
            search_results = []
            for hit in results:
                search_results.append({
                    "id": hit.id,
                    "data": hit.vector,
                    "metadata": hit.payload,
                    "score": hit.score
                })
            
            return search_results
        
        else:
            # 内存向量存储
            return self.vector_db.search(query, limit, filter_criteria)
    
    def update(self, memory_id, data, metadata=None):
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            data: 更新的数据
            metadata: 更新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        # 检查记忆是否存在
        existing_memory = self.get_by_id(memory_id)
        if not existing_memory:
            return False
        
        # 准备元数据
        full_metadata = existing_memory["metadata"].copy()
        if metadata:
            full_metadata.update(metadata)
        full_metadata["updated_at"] = datetime.now().isoformat()
        
        # 更新向量数据
        self._store_vector(memory_id, data, full_metadata)
        
        # 更新元数据
        self._update_metadata(memory_id, full_metadata)
        
        return True
    
    def _update_metadata(self, memory_id, metadata):
        """更新元数据
        
        Args:
            memory_id: 记忆ID
            metadata: 元数据
        """
        db_type = self.config.get("metadata_db_type", "sqlite")
        
        if db_type == "sqlite":
            cursor = self.metadata_db.cursor()
            cursor.execute(
                "UPDATE memory_metadata SET data = ?, updated_at = ? WHERE id = ?",
                (json.dumps(metadata), metadata["updated_at"], memory_id)
            )
            self.metadata_db.commit()
        
        elif db_type == "mongodb":
            self.metadata_db.update_one({"id": memory_id}, {"$set": metadata})
        
        else:
            # 内存存储
            self.metadata_db[memory_id] = metadata
    
    def delete(self, memory_id):
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        # 检查记忆是否存在
        existing_memory = self.get_by_id(memory_id)
        if not existing_memory:
            return False
        
        # 删除向量数据
        self._delete_vector(memory_id)
        
        # 删除元数