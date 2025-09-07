# 对话历史管理器设计文档

## 1. 概述

对话历史管理器（ConversationHistoryManager）是智能上下文层的核心组件之一，专注于管理和处理Agent与用户或其他Agent之间的交互历史。它提供了一套完整的机制来存储、检索、搜索和分析对话历史，为Agent提供连贯的对话上下文，使其能够理解和参考先前的交互内容。

对话历史管理器不仅仅是简单的消息存储系统，它还提供了丰富的功能，如对话摘要生成、关键信息提取、对话历史压缩等，以解决大语言模型上下文窗口限制的问题，同时保持对话的连贯性和相关性。

## 2. 设计目标

对话历史管理器的设计目标包括：

1. **完整性**：准确完整地记录所有对话交互，包括消息内容、时间戳、角色信息和元数据。

2. **高效检索**：提供高效的检索机制，使Agent能够快速访问和引用先前的对话内容。

3. **智能摘要**：自动生成对话历史的摘要，提取关键信息，减少上下文长度。

4. **灵活存储**：支持多种存储后端，包括内存、文件系统、数据库等，以适应不同的应用场景。

5. **可扩展性**：设计灵活的接口和扩展点，便于添加新功能和集成不同的存储解决方案。

6. **性能优化**：优化存储和检索性能，减少延迟，提高响应速度。

7. **多模态支持**：支持文本、图像、音频等多种模态的消息内容。

## 3. 核心组件

### 3.1 消息模型（MessageModel）

消息模型定义了对话中单条消息的数据结构，包括：

- 消息ID：唯一标识符
- 会话ID：所属会话的标识符
- 角色：消息发送者的角色（如用户、助手、系统等）
- 内容：消息的实际内容（支持多模态）
- 时间戳：消息创建时间
- 元数据：附加信息（如情感、意图、实体等）

### 3.2 会话模型（ConversationModel）

会话模型定义了整个对话会话的数据结构，包括：

- 会话ID：唯一标识符
- 参与者：会话参与者信息
- 创建时间：会话创建时间
- 更新时间：会话最后更新时间
- 状态：会话状态（如活跃、已结束等）
- 元数据：会话相关的附加信息

### 3.3 存储提供者（StorageProvider）

存储提供者负责实际的消息存储和检索操作，支持多种存储后端：

- 内存存储：适用于临时会话和测试
- 文件存储：适用于持久化但不需要高并发的场景
- 数据库存储：适用于需要高并发和复杂查询的场景
- 分布式存储：适用于大规模分布式系统

### 3.4 摘要生成器（SummaryGenerator）

摘要生成器负责生成对话历史的摘要，提取关键信息，包括：

- 基本摘要：生成简单的对话摘要
- 渐进式摘要：基于现有摘要和新消息更新摘要
- 主题提取：识别和提取对话中的主要主题
- 关键信息提取：提取对话中的关键信息点

### 3.5 搜索引擎（SearchEngine）

搜索引擎负责在对话历史中搜索相关信息，支持多种搜索策略：

- 关键词搜索：基于关键词匹配
- 语义搜索：基于语义相似度
- 混合搜索：结合关键词和语义搜索
- 时间范围搜索：基于时间范围筛选

### 3.6 压缩器（Compressor）

压缩器负责压缩对话历史，以适应大语言模型的上下文窗口限制：

- 消息筛选：根据重要性筛选消息
- 内容压缩：压缩消息内容，保留关键信息
- 结构优化：优化对话结构，减少冗余

## 4. 关键接口设计

### 4.1 ConversationHistoryManager接口

```python
class ConversationHistoryManager:
    def __init__(self, storage_provider=None, summary_generator=None, search_engine=None, compressor=None):
        """初始化对话历史管理器
        
        Args:
            storage_provider: 存储提供者实例
            summary_generator: 摘要生成器实例
            search_engine: 搜索引擎实例
            compressor: 压缩器实例
        """
        self.storage = storage_provider or InMemoryStorageProvider()
        self.summarizer = summary_generator or DefaultSummaryGenerator()
        self.searcher = search_engine or DefaultSearchEngine()
        self.compressor = compressor or DefaultCompressor()
    
    def create_conversation(self, participants=None, metadata=None):
        """创建新的对话会话
        
        Args:
            participants: 会话参与者列表
            metadata: 会话元数据
            
        Returns:
            str: 新创建的会话ID
        """
        pass
    
    def get_conversation(self, conversation_id):
        """获取指定ID的对话会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            ConversationModel: 会话模型实例
        """
        pass
    
    def add_message(self, conversation_id, role, content, metadata=None):
        """添加新消息到对话历史
        
        Args:
            conversation_id: 会话ID
            role: 消息发送者角色
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            str: 新创建的消息ID
        """
        pass
    
    def get_messages(self, conversation_id, limit=None, offset=0, filter_criteria=None):
        """获取对话历史消息
        
        Args:
            conversation_id: 会话ID
            limit: 返回消息的最大数量
            offset: 起始偏移量
            filter_criteria: 过滤条件
            
        Returns:
            list: 消息列表
        """
        pass
    
    def search_messages(self, conversation_id, query, limit=10, search_type="hybrid"):
        """搜索对话历史中的相关消息
        
        Args:
            conversation_id: 会话ID
            query: 搜索查询
            limit: 返回结果的最大数量
            search_type: 搜索类型（keyword, semantic, hybrid）
            
        Returns:
            list: 搜索结果列表
        """
        pass
    
    def summarize_conversation(self, conversation_id, max_length=None, focus=None):
        """生成对话历史的摘要
        
        Args:
            conversation_id: 会话ID
            max_length: 摘要的最大长度
            focus: 摘要关注点（如主题、关键信息等）
            
        Returns:
            str: 对话摘要
        """
        pass
    
    def update_progressive_summary(self, conversation_id, existing_summary, new_message_ids):
        """更新渐进式摘要
        
        Args:
            conversation_id: 会话ID
            existing_summary: 现有摘要
            new_message_ids: 新消息ID列表
            
        Returns:
            str: 更新后的摘要
        """
        pass
    
    def compress_history(self, conversation_id, max_tokens=None, strategy="balanced"):
        """压缩对话历史
        
        Args:
            conversation_id: 会话ID
            max_tokens: 压缩后的最大token数
            strategy: 压缩策略（如balanced, aggressive, conservative）
            
        Returns:
            list: 压缩后的消息列表
        """
        pass
    
    def delete_conversation(self, conversation_id):
        """删除指定的对话历史
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def delete_message(self, message_id):
        """删除指定的消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def get_conversation_statistics(self, conversation_id):
        """获取对话统计信息
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            dict: 统计信息
        """
        pass
```

### 4.2 StorageProvider接口

```python
class StorageProvider:
    def __init__(self, config=None):
        """初始化存储提供者
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def create_conversation(self, conversation_data):
        """创建新的对话会话
        
        Args:
            conversation_data: 会话数据
            
        Returns:
            str: 新创建的会话ID
        """
        pass
    
    def get_conversation(self, conversation_id):
        """获取指定ID的对话会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            dict: 会话数据
        """
        pass
    
    def update_conversation(self, conversation_id, update_data):
        """更新会话数据
        
        Args:
            conversation_id: 会话ID
            update_data: 更新数据
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def delete_conversation(self, conversation_id):
        """删除指定的对话会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def add_message(self, message_data):
        """添加新消息
        
        Args:
            message_data: 消息数据
            
        Returns:
            str: 新创建的消息ID
        """
        pass
    
    def get_message(self, message_id):
        """获取指定ID的消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            dict: 消息数据
        """
        pass
    
    def get_messages(self, conversation_id, limit=None, offset=0, filter_criteria=None):
        """获取会话的消息列表
        
        Args:
            conversation_id: 会话ID
            limit: 返回消息的最大数量
            offset: 起始偏移量
            filter_criteria: 过滤条件
            
        Returns:
            list: 消息列表
        """
        pass
    
    def update_message(self, message_id, update_data):
        """更新消息数据
        
        Args:
            message_id: 消息ID
            update_data: 更新数据
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def delete_message(self, message_id):
        """删除指定的消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def search_messages(self, conversation_id, query, limit=10):
        """搜索消息
        
        Args:
            conversation_id: 会话ID
            query: 搜索查询
            limit: 返回结果的最大数量
            
        Returns:
            list: 搜索结果列表
        """
        pass
```

### 4.3 SummaryGenerator接口

```python
class SummaryGenerator:
    def __init__(self, config=None):
        """初始化摘要生成器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def generate_summary(self, messages, max_length=None, focus=None):
        """生成对话摘要
        
        Args:
            messages: 消息列表
            max_length: 摘要的最大长度
            focus: 摘要关注点
            
        Returns:
            str: 对话摘要
        """
        pass
    
    def update_summary(self, existing_summary, new_messages, max_length=None):
        """更新现有摘要
        
        Args:
            existing_summary: 现有摘要
            new_messages: 新消息列表
            max_length: 摘要的最大长度
            
        Returns:
            str: 更新后的摘要
        """
        pass
    
    def extract_key_points(self, messages):
        """提取关键信息点
        
        Args:
            messages: 消息列表
            
        Returns:
            list: 关键信息点列表
        """
        pass
    
    def extract_topics(self, messages):
        """提取对话主题
        
        Args:
            messages: 消息列表
            
        Returns:
            list: 主题列表
        """
        pass
```

### 4.4 SearchEngine接口

```python
class SearchEngine:
    def __init__(self, config=None):
        """初始化搜索引擎
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def search(self, messages, query, limit=10, search_type="hybrid"):
        """搜索消息
        
        Args:
            messages: 消息列表
            query: 搜索查询
            limit: 返回结果的最大数量
            search_type: 搜索类型
            
        Returns:
            list: 搜索结果列表
        """
        pass
    
    def keyword_search(self, messages, query, limit=10):
        """关键词搜索
        
        Args:
            messages: 消息列表
            query: 搜索查询
            limit: 返回结果的最大数量
            
        Returns:
            list: 搜索结果列表
        """
        pass
    
    def semantic_search(self, messages, query, limit=10):
        """语义搜索
        
        Args:
            messages: 消息列表
            query: 搜索查询
            limit: 返回结果的最大数量
            
        Returns:
            list: 搜索结果列表
        """
        pass
    
    def hybrid_search(self, messages, query, limit=10, keyword_weight=0.3, semantic_weight=0.7):
        """混合搜索
        
        Args:
            messages: 消息列表
            query: 搜索查询
            limit: 返回结果的最大数量
            keyword_weight: 关键词搜索权重
            semantic_weight: 语义搜索权重
            
        Returns:
            list: 搜索结果列表
        """
        pass
```

### 4.5 Compressor接口

```python
class Compressor:
    def __init__(self, config=None):
        """初始化压缩器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def compress(self, messages, max_tokens=None, strategy="balanced"):
        """压缩消息列表
        
        Args:
            messages: 消息列表
            max_tokens: 压缩后的最大token数
            strategy: 压缩策略
            
        Returns:
            list: 压缩后的消息列表
        """
        pass
    
    def filter_messages(self, messages, importance_threshold=0.5):
        """根据重要性筛选消息
        
        Args:
            messages: 消息列表
            importance_threshold: 重要性阈值
            
        Returns:
            list: 筛选后的消息列表
        """
        pass
    
    def compress_content(self, message, max_tokens=None):
        """压缩单条消息内容
        
        Args:
            message: 消息
            max_tokens: 压缩后的最大token数
            
        Returns:
            dict: 压缩后的消息
        """
        pass
    
    def get_available_strategies(self):
        """获取可用的压缩策略
        
        Returns:
            dict: 压缩策略信息
        """
        pass
```

## 5. 实现示例

### 5.1 内存存储提供者实现

```python
class InMemoryStorageProvider(StorageProvider):
    def __init__(self, config=None):
        super().__init__(config)
        self.conversations = {}
        self.messages = {}
    
    def create_conversation(self, conversation_data):
        conversation_id = str(uuid.uuid4())
        conversation_data["id"] = conversation_id
        conversation_data["created_at"] = datetime.now().isoformat()
        conversation_data["updated_at"] = conversation_data["created_at"]
        self.conversations[conversation_id] = conversation_data
        return conversation_id
    
    def get_conversation(self, conversation_id):
        return self.conversations.get(conversation_id)
    
    def update_conversation(self, conversation_id, update_data):
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        for key, value in update_data.items():
            conversation[key] = value
        
        conversation["updated_at"] = datetime.now().isoformat()
        return True
    
    def delete_conversation(self, conversation_id):
        if conversation_id not in self.conversations:
            return False
        
        # 删除会话相关的所有消息
        message_ids_to_delete = []
        for message_id, message in self.messages.items():
            if message.get("conversation_id") == conversation_id:
                message_ids_to_delete.append(message_id)
        
        for message_id in message_ids_to_delete:
            del self.messages[message_id]
        
        # 删除会话
        del self.conversations[conversation_id]
        return True
    
    def add_message(self, message_data):
        message_id = str(uuid.uuid4())
        message_data["id"] = message_id
        message_data["created_at"] = datetime.now().isoformat()
        
        # 更新会话的更新时间
        conversation_id = message_data.get("conversation_id")
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["updated_at"] = message_data["created_at"]
        
        self.messages[message_id] = message_data
        return message_id
    
    def get_message(self, message_id):
        return self.messages.get(message_id)
    
    def get_messages(self, conversation_id, limit=None, offset=0, filter_criteria=None):
        # 获取指定会话的所有消息
        conversation_messages = []
        for message in self.messages.values():
            if message.get("conversation_id") == conversation_id:
                # 应用过滤条件
                if filter_criteria and not self._match_filter(message, filter_criteria):
                    continue
                conversation_messages.append(message)
        
        # 按时间排序
        conversation_messages.sort(key=lambda x: x.get("created_at", ""))
        
        # 应用分页
        if offset > 0:
            conversation_messages = conversation_messages[offset:]
        if limit is not None:
            conversation_messages = conversation_messages[:limit]
        
        return conversation_messages
    
    def update_message(self, message_id, update_data):
        if message_id not in self.messages:
            return False
        
        message = self.messages[message_id]
        for key, value in update_data.items():
            message[key] = value
        
        return True
    
    def delete_message(self, message_id):
        if message_id not in self.messages:
            return False
        
        del self.messages[message_id]
        return True
    
    def search_messages(self, conversation_id, query, limit=10):
        # 简单的关键词匹配搜索
        results = []
        for message in self.messages.values():
            if message.get("conversation_id") == conversation_id:
                content = message.get("content", "")
                if query.lower() in content.lower():
                    results.append(message)
                    if len(results) >= limit:
                        break
        
        return results
    
    def _match_filter(self, message, filter_criteria):
        for key, value in filter_criteria.items():
            if key not in message or message[key] != value:
                return False
        return True
```

### 5.2 LLM摘要生成器实现

```python
class LLMSummaryGenerator(SummaryGenerator):
    def __init__(self, llm_service, config=None):
        super().__init__(config)
        self.llm = llm_service
    
    def generate_summary(self, messages, max_length=100, focus=None):
        # 准备消息格式
        formatted_messages = self._format_messages(messages)
        
        # 构建提示
        prompt = f"""请总结以下对话，突出关键信息和主要讨论点。摘要不应超过{max_length}个token。

对话内容：
{formatted_messages}

"""
        
        # 添加特定关注点
        if focus:
            prompt += f"请特别关注与'{focus}'相关的内容。\n"
        
        prompt += "摘要："
        
        # 调用LLM生成摘要
        summary = self.llm.generate(prompt, max_tokens=max_length)
        return summary.strip()
    
    def update_summary(self, existing_summary, new_messages, max_length=100):
        # 准备新消息格式
        formatted_messages = self._format_messages(new_messages)
        
        # 构建提示
        prompt = f"""以下是之前对话的摘要，以及新的对话消息。请更新摘要以包含新信息，保持摘要简洁且不超过{max_length}个token。

现有摘要：
{existing_summary}

新消息：
{formatted_messages}

更新后的摘要："""
        
        # 调用LLM更新摘要
        updated_summary = self.llm.generate(prompt, max_tokens=max_length)
        return updated_summary.strip()
    
    def extract_key_points(self, messages):
        # 准备消息格式
        formatted_messages = self._format_messages(messages)
        
        # 构建提示
        prompt = f"""请从以下对话中提取5-10个关键信息点，每个信息点应简洁明了。

对话内容：
{formatted_messages}

关键信息点：
1. """
        
        # 调用LLM提取关键点
        response = self.llm.generate(prompt, max_tokens=300)
        
        # 解析结果
        key_points = []
        for line in response.strip().split("\n"):
            if line.strip() and line.strip()[0].isdigit():
                # 移除序号和点
                point = re.sub(r'^\d+\.\s*', '', line).strip()
                if point:
                    key_points.append(point)
        
        return key_points
    
    def extract_topics(self, messages):
        # 准备消息格式
        formatted_messages = self._format_messages(messages)
        
        # 构建提示
        prompt = f"""请从以下对话中提取3-5个主要讨论主题，每个主题用简短的短语表示。

对话内容：
{formatted_messages}

主要主题：
1. """
        
        # 调用LLM提取主题
        response = self.llm.generate(prompt, max_tokens=200)
        
        # 解析结果
        topics = []
        for line in response.strip().split("\n"):
            if line.strip() and line.strip()[0].isdigit():
                # 移除序号和点
                topic = re.sub(r'^\d+\.\s*', '', line).strip()
                if topic:
                    topics.append(topic)
        
        return topics
    
    def _format_messages(self, messages):
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
```

### 5.3 混合搜索引擎实现

```python
class HybridSearchEngine(SearchEngine):
    def __init__(self, embedding_model=None, config=None):
        super().__init__(config)
        self.embedding_model = embedding_model
    
    def search(self, messages, query, limit=10, search_type="hybrid"):
        if search_type == "keyword":
            return self.keyword_search(messages, query, limit)
        elif search_type == "semantic":
            return self.semantic_search(messages, query, limit)
        else:  # hybrid
            return self.hybrid_search(messages, query, limit)
    
    def keyword_search(self, messages, query, limit=10):
        # 简单的关键词匹配搜索
        results = []
        query_terms = query.lower().split()
        
        for message in messages:
            content = message.get("content", "").lower()
            score = 0
            
            # 计算匹配分数
            for term in query_terms:
                if term in content:
                    score += 1
            
            # 如果有匹配，添加到结果
            if score > 0:
                results.append({
                    "message": message,
                    "score": score / len(query_terms)  # 归一化分数
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def semantic_search(self, messages, query, limit=10):
        if not self.embedding_model:
            raise ValueError("Embedding model is required for semantic search")
        
        # 生成查询的嵌入向量
        query_embedding = self.embedding_model.embed(query)
        
        results = []
        for message in messages:
            content = message.get("content", "")
            
            # 生成消息内容的嵌入向量
            content_embedding = self.embedding_model.embed(content)
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, content_embedding)
            
            results.append({
                "message": message,
                "score": similarity
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def hybrid_search(self, messages, query, limit=10, keyword_weight=0.3, semantic_weight=0.7):
        # 执行关键词搜索
        keyword_results = self.keyword_search(messages, query, limit=len(messages))
        keyword_scores = {self._get_message_id(r["message"]): r["score"] for r in keyword_results}
        
        # 执行语义搜索
        semantic_results = self.semantic_search(messages, query, limit=len(messages))
        semantic_scores = {self._get_message_id(r["message"]): r["score"] for r in semantic_results}
        
        # 合并结果
        combined_results = {}
        all_message_ids = set(keyword_scores.keys()) | set(semantic_scores.keys())
        
        for message_id in all_message_ids:
            # 获取两种搜索的分数，如果没有则为0
            k_score = keyword_scores.get(message_id, 0)
            s_score = semantic_scores.get(message_id, 0)
            
            # 计算加权分数
            combined_score = (k_score * keyword_weight) + (s_score * semantic_weight)
            
            # 找到对应的消息
            message = next((r["message"] for r in keyword_results if self._get_message_id(r["message"]) == message_id), None)
            if not message:
                message = next((r["message"] for r in semantic_results if self._get_message_id(r["message"]) == message_id), None)
            
            combined_results[message_id] = {
                "message": message,
                "score": combined_score
            }
        
        # 转换为列表并排序
        results = list(combined_results.values())
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1, vec2):
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        
        if norm_a == 0 or norm_b == 0:
            return 0
        
        return dot_product / (norm_a * norm_b)
    
    def _get_message_id(self, message):
        return message.get("id", str(hash(json.dumps(message, sort_keys=True))))
```

### 5.4 智能压缩器实现

```python
class SmartCompressor(Compressor):
    def __init__(self, llm_service=None, config=None):
        super().__init__(config)
        self.llm = llm_service
        self.strategies = {
            "balanced": {
                "description": "平衡保留信息和减少长度",
                "importance_threshold": 0.5,
                "content_compression_ratio": 0.7
            },
            "aggressive": {
                "description": "最大程度减少长度，可能丢失部分信息",
                "importance_threshold": 0.7,
                "content_compression_ratio": 0.5
            },
            "conservative": {
                "description": "尽量保留完整信息，适度减少长度",
                "importance_threshold": 0.3,
                "content_compression_ratio": 0.9
            }
        }
    
    def compress(self, messages, max_tokens=None, strategy="balanced"):
        # 获取策略参数
        strategy_config = self.strategies.get(strategy, self.strategies["balanced"])
        importance_threshold = strategy_config["importance_threshold"]
        content_compression_ratio = strategy_config["content_compression_ratio"]
        
        # 步骤1: 评估消息重要性并筛选
        filtered_messages = self.filter_messages(messages, importance_threshold)
        
        # 步骤2: 如果仍然超过最大token数，压缩消息内容
        if max_tokens and self._estimate_tokens(filtered_messages) > max_tokens:
            compressed_messages = []
            for message in filtered_messages:
                compressed_message = self.compress_content(message, content_compression_ratio)
                compressed_messages.append(compressed_message)
            filtered_messages = compressed_messages
        
        # 步骤3: 如果仍然超过最大token数，进一步减少消息数量
        if max_tokens and self._estimate_tokens(filtered_messages) > max_tokens:
            # 保留最早和最新的消息，删除中间的消息
            filtered_messages = self._reduce_message_count(filtered_messages, max_tokens)
        
        return filtered_messages
    
    def filter_messages(self, messages, importance_threshold=0.5):
        if not self.llm:
            # 如果没有LLM服务，使用简单的规则筛选
            return self._rule_based_filter(messages, importance_threshold)
        
        # 使用LLM评估消息重要性
        rated_messages = []
        for message in messages:
            importance = self._evaluate_importance(message)
            if importance >= importance_threshold:
                rated_messages.append(message)
        
        return rated_messages
    
    def compress_content(self, message, compression_ratio=0.7):
        content = message.get("content", "")
        
        if not self.llm or len(content) < 100:  # 短消息不压缩
            return message
        
        # 计算目标长度
        target_length = int(len(content) * compression_ratio)
        
        # 构建提示
        prompt = f"""请压缩以下文本，保留关键信息，但使其更简洁。压缩后的文本应不超过原文的{int(compression_ratio*100)}%。

原文：
{content}

压缩后的文本："""
        
        # 调用LLM压缩内容
        compressed_content = self.llm.generate(prompt, max_tokens=target_length)
        
        # 创建新消息，保留原始消息的其他字段
        compressed_message = message.copy()
        compressed_message["content"] = compressed_content.strip()
        compressed_message["compressed"] = True
        
        return compressed_message
    
    def get_available_strategies(self):
        return self.strategies
    
    def _rule_based_filter(self, messages, importance_threshold):
        # 简单的基于规则的筛选
        filtered = []
        
        # 始终保留第一条和最后几条消息
        if messages:
            filtered.append(messages[0])  # 第一条消息
        
        # 根据阈值筛选中间消息
        middle_messages = messages[1:-3] if len(messages) > 4 else []
        for message in middle_messages:
            # 简单规则：较长消息可能更重要
            content = message.get("content", "")
            if len(content) > 100 or "?" in content or "!" in content:
                filtered.append(message)
        
        # 添加最后几条消息
        if len(messages) > 1:
            filtered.extend(messages[-3:])  # 最后三条消息
        
        return filtered
    
    def _evaluate_importance(self, message):
        content = message.get("content", "")
        role = message.get("role", "")
        
        # 构建提示
        prompt = f"""请评估以下对话消息的重要性，考虑其信息价值、独特性和对对话理解的贡献。
给出0到1之间的分数，其中0表示完全不重要，1表示极其重要。

消息角色：{role}
消息内容：{content}

重要性评分（0-1）："""
        
        # 调用LLM评估重要性
        response = self.llm.generate(prompt, max_tokens=10)
        
        # 尝试提取数值
        try:
            importance = float(response.strip())
            return max(0, min(1, importance))  # 确保在0-1范围内
        except ValueError:
            # 如果无法解析为浮点数，返回默认值
            return 0.5
    
    def _estimate_tokens(self, messages):
        # 简单估算token数量（每个单词约1.3个token）
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        return int(total_chars / 4)  # 粗略估计
    
    def _reduce_message_count(self, messages, max_tokens):
        if not messages:
            return []
        
        # 保留第一条和最后几条消息
        result = [messages[0]]  # 第一条消息
        
        # 计算剩余token预算
        first_msg_tokens = self._estimate_tokens([messages[0]])
        remaining_budget = max_tokens - first_msg_tokens
        
        # 从最新消息开始添加，直到达到预算限制
        for msg in reversed(messages[1:]):
            msg_tokens = self._estimate_tokens([msg])
            if remaining_budget >= msg_tokens:
                result.append(msg)
                remaining_budget -= msg_tokens
            else:
                break
        
        # 确保结果按原始顺序排列
        result.sort(key=lambda x: messages.index(x))
        
        return result
```

## 6. 对话历史处理流程

### 6.1 基本流程

1. **初始化**：创建对话会话，分配唯一标识符。

2. **消息处理**：
   - 接收新消息
   - 验证消息格式和内容
   - 将消息添加到存储中
   - 更新会话状态

3. **检索和搜索**：
   - 根据需要检索历史消息
   - 执行关键词或语义搜索
   - 返回相关消息

4. **摘要生成**：
   - 定期或按需生成对话摘要
   - 更新渐进式摘要
   - 提取关键信息点和主题

5. **压缩和优化**：
   - 评估对话历史大小
   - 应用适当的压缩策略
   - 返回压缩后的对话历史

### 6.2 渐进式摘要流程

1. **初始摘要生成**：
   - 当对话达到一定长度时生成初始摘要
   - 存储摘要和最后处理的消息ID

2. **摘要更新**：
   - 当新消息累积到一定数量时
   - 获取现有摘要和新消息
   - 生成更新后的摘要
   - 更新存储的摘要和最后处理的消息ID

3. **摘要使用**：
   - 在构建上下文时，使用摘要替代早期的详细消息
   - 保留最近的详细消息
   - 组合摘要和详细消息形成完整上下文

## 7. 性能考虑

### 7.1 优化策略

1. **缓存机制**：
   - 缓存频繁访问的会话和消息
   - 缓存搜索结果和摘要
   - 实现多级缓存策略

2. **异步处理**：
   - 异步生成摘要和压缩历史
   - 后台索引和优化
   - 预计算常用查询结果

3. **批处理**：
   - 批量消息存储和检索
   - 批量嵌入生成
   - 定期批量优化

4. **索引优化**：
   - 为消息内容创建全文索引
   - 为嵌入向量创建高效索引
   - 优化时间范围查询

5. **存储分层**：
   - 热数据保存在内存或快速存储中
   - 冷数据移至慢速但成本更低的存储
   - 自动数据迁移策略

### 7.2 性能指标

1. **延迟指标**：
   - 消息存储时间
   - 消息检索时间
   - 搜索响应时间
   - 摘要生成时间

2. **吞吐量指标**：
   - 每秒处理消息数
   - 每秒检索请求数
   - 每秒搜索请求数

3. **存储指标**：
   - 每会话平均存储大小
   - 压缩率
   - 存储利用率

4. **质量指标**：
   - 摘要质量评分
   - 搜索准确率和召回率
   - 压缩信息保留率

## 8. 扩展点

### 8.1 自定义存储提供者

通过实现StorageProvider接口，可以集成各种存储后端：

```python
class CustomStorageProvider(StorageProvider):
    def __init__(self, config=None):
        super().__init__(config)
        # 初始化自定义存储
        
    def create_conversation(self, conversation_data):
        # 实现创建会话逻辑
        pass
        
    def get_conversation(self, conversation_id):
        # 实现获取会话逻辑
        pass
        
    # 实现其他必要方法...
```

### 8.2 自定义摘要生成器

通过实现SummaryGenerator接口，可以定义自定义的摘要生成策略：

```python
class CustomSummaryGenerator(SummaryGenerator):
    def __init__(self, config=None):
        super().__init__(config)
        # 初始化自定义摘要生成器
        
    def generate_summary(self, messages, max_length=None, focus=None):
        # 实现自定义摘要生成逻辑
        pass
        
    def update_summary(self, existing_summary, new_messages, max_length=None):
        # 实现自定义摘要更新逻辑
        pass
        
    # 实现其他必要方法...
```

### 8.3 自定义搜索引擎

通过实现SearchEngine接口，可以集成不同的搜索技术：

```python
class CustomSearchEngine(SearchEngine):
    def __init__(self, config=None):
        super().__init__(config)
        # 初始化自定义搜索引擎
        
    def search(self, messages, query, limit=10, search_type="custom"):
        # 实现自定义搜索逻辑
        pass
        
    # 实现其他必要方法...
```

### 8.4 自定义压缩策略

通过实现Compressor接口，可以定义自定义的压缩策略：

```python
class CustomCompressor(Compressor):
    def __init__(self, config=None):
        super().__init__(config)
        # 初始化自定义压缩器
        
    def compress(self, messages, max_tokens=None, strategy="custom"):
        # 实现自定义压缩逻辑
        pass
        
    # 实现其他必要方法...
```

## 9. 与其他组件的集成

### 9.1 与上下文管理器的集成

对话历史管理器作为上下文管理器的核心组件，提供对话历史的存储、检索和处理功能，支持上下文管理器构建完整的上下文环境。

### 9.2 与记忆系统的集成

对话历史可以作为记忆系统的输入源，提供对话内容用于记忆的生成和更新，同时记忆系统也可以为对话历史提供相关的长期记忆信息。

### 9.3 与检索引擎的集成

对话历史管理器可以利用检索引擎的能力，实现高效的对话历史搜索和相关信息检索，提高对话历史的利用效率。

## 10. 总结

对话历史管理器是智能上下文层的关键组件，负责管理和处理Agent与用户或其他Agent之间的交互历史。它提供了完整的机制来存储、检索、搜索和分析对话历史，为Agent提供连贯的对话上下文，使其能够理解和参考先前的交互内容。

通过灵活的接口设计和扩展点，对话历史管理器支持多种存储后端、摘要生成策略、搜索技术和压缩策略，能够适应不同的应用场景和需求。同时，通过与上下文管理器、记忆系统和检索引擎的紧密集成，对话历史管理器为构建具有上下文感知能力的智能Agent提供了坚实的基础。