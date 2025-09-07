"""
Memory System - 记忆系统
提供分层记忆管理：工作记忆、情景记忆、语义记忆、程序记忆
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import logging
from collections import defaultdict, deque
import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class MemoryType(Enum):
    """记忆类型枚举"""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryImportance(Enum):
    """记忆重要性等级"""
    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    MINIMAL = 0.2


@dataclass
class MemoryItem:
    """记忆项"""
    item_id: str
    content: Any
    memory_type: MemoryType
    importance: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 语义嵌入支持
    embedding: Optional[np.ndarray] = field(default=None, repr=False)
    embedding_model: Optional[str] = field(default=None)
    semantic_keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


@dataclass
class EpisodicMemory:
    """情景记忆项"""
    episode_id: str
    event: str
    context: Dict[str, Any]
    participants: List[str]
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_valence: float = 0.0  # -1.0 to 1.0
    importance: float = 0.5
    related_episodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticMemory:
    """语义记忆项"""
    concept_id: str
    concept: str
    definition: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 1.0
    source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProceduralMemory:
    """程序记忆项"""
    procedure_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    success_rate: float = 1.0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SemanticEmbeddingManager:
    """语义嵌入管理器 - 处理文本的语义向量化和相似性计算"""
    
    def __init__(self, model_type: str = "tfidf"):
        self.model_type = model_type
        self.vectorizer = None
        self.vocabulary = set()
        self.embedding_cache = {}
        self.training_texts = []  # 用于累积训练文本
        
        if model_type == "tfidf":
            self.vectorizer = TfidfVectorizer(
                max_features=200,  # 进一步减少特征数量
                stop_words=None,   # 不过滤停用词，支持中文
                ngram_range=(1, 1), # 只使用单词，不使用n-gram
                lowercase=True,
                min_df=1,          # 最小文档频率：至少出现1次
                max_df=1.0,        # 最大文档频率：可以出现在所有文档中
                sublinear_tf=True  # 使用sublinear tf scaling
            )
            self.is_fitted = False
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        if not isinstance(text, str):
            text = str(text)
        
        # 保留中文字符和英文字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)  # 保留中文
        text = re.sub(r'\s+', ' ', text)      # 合并空格
        text = text.lower().strip()
        
        return text
    
    def _extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
        processed_text = self._preprocess_text(text)
        
        # 分词：简单按空格分割（可以扩展为更复杂的中文分词）
        words = []
        for word in processed_text.split():
            if len(word) > 1:  # 过滤单字符
                words.append(word)
                # 对于中文，也尝试提取单个字符作为词
                if any('\u4e00' <= char <= '\u9fff' for char in word):
                    for char in word:
                        if '\u4e00' <= char <= '\u9fff':
                            words.append(char)
        
        # 词频统计
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序并返回top_k
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    async def generate_embedding(self, content: Any) -> Tuple[np.ndarray, List[str]]:
        """生成语义嵌入和关键词"""
        text = self._preprocess_text(str(content))
        
        if not text.strip():
            return np.zeros(100), []
        
        # 检查缓存
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            if self.model_type == "tfidf":
                embedding = await self._generate_tfidf_embedding(text)
            else:
                # 可以扩展其他嵌入模型
                embedding = await self._generate_simple_embedding(text)
            
            # 提取关键词
            keywords = self._extract_keywords(text)
            
            # 缓存结果
            result = (embedding, keywords)
            self.embedding_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"生成嵌入失败: {e}")
            return np.random.random(100), []
    
    async def _generate_tfidf_embedding(self, text: str) -> np.ndarray:
        """生成TF-IDF嵌入"""
        # 将新文本添加到训练集
        if text not in self.training_texts:
            self.training_texts.append(text)
        
        # 如果训练集足够大，重新训练vectorizer
        if len(self.training_texts) >= 5 or not self.is_fitted:
            try:
                self.vectorizer.fit(self.training_texts)
                self.is_fitted = True
            except Exception as e:
                self.logger.warning(f"TF-IDF训练失败: {e}")
                return await self._generate_simple_embedding(text)
        
        try:
            # 生成TF-IDF向量
            tfidf_matrix = self.vectorizer.transform([text])
            embedding = tfidf_matrix.toarray()[0]
            
            # 确保向量不为空
            if len(embedding) == 0:
                return await self._generate_simple_embedding(text)
            
            return embedding
            
        except Exception as e:
            self.logger.warning(f"TF-IDF转换失败: {e}")
            return await self._generate_simple_embedding(text)
    
    async def _generate_simple_embedding(self, text: str) -> np.ndarray:
        """生成简单的词袋嵌入（备用方案）"""
        words = text.split()
        
        # 简单的词向量化：基于词的特征
        if not words:
            return np.zeros(100)
        
        embedding = np.zeros(100)
        
        for i, word in enumerate(words[:50]):  # 限制词数
            if len(word) > 0:
                # 基于词的多个特征生成嵌入
                word_hash = hash(word) % 100
                char_sum = sum(ord(c) for c in word[:5]) % 100
                word_len = min(len(word), 20)
                
                # 分布到不同的维度
                embedding[word_hash] += 1.0
                embedding[char_sum] += 0.5
                embedding[word_len] += 0.3
                
                # 添加位置信息
                pos_feature = (i * 7) % 100
                embedding[pos_feature] += 0.2
        
        # L2归一化
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    async def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """计算两个嵌入的相似性"""
        try:
            # 确保向量不为空且维度相同
            if len(embedding1) == 0 or len(embedding2) == 0:
                return 0.0
            
            if len(embedding1) != len(embedding2):
                # 如果维度不同，填充或截断到相同长度
                max_len = max(len(embedding1), len(embedding2))
                padded_emb1 = np.zeros(max_len)
                padded_emb2 = np.zeros(max_len)
                
                padded_emb1[:len(embedding1)] = embedding1
                padded_emb2[:len(embedding2)] = embedding2
                
                embedding1, embedding2 = padded_emb1, padded_emb2
            
            # 使用余弦相似性
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            # 处理NaN值
            if np.isnan(similarity):
                return 0.0
                
            return max(0.0, min(1.0, similarity))  # 确保在[0,1]范围内
            
        except Exception as e:
            self.logger.warning(f"相似性计算失败: {e}")
            return 0.0
    
    async def find_similar_items(self, query_embedding: np.ndarray, 
                               item_embeddings: List[Tuple[str, np.ndarray]], 
                               threshold: float = 0.1, 
                               top_k: int = 5) -> List[Tuple[str, float]]:
        """找到相似的项目"""
        similarities = []
        
        for item_id, embedding in item_embeddings:
            similarity = await self.calculate_similarity(query_embedding, embedding)
            if similarity >= threshold:
                similarities.append((item_id, similarity))
        
        # 按相似性排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def update_vocabulary(self, texts: List[str]):
        """更新词汇表"""
        if self.model_type == "tfidf" and texts:
            try:
                # 添加到训练文本
                for text in texts:
                    processed_text = self._preprocess_text(text)
                    if processed_text and processed_text not in self.training_texts:
                        self.training_texts.append(processed_text)
                
                # 重新训练
                if len(self.training_texts) > 0:
                    self.vectorizer.fit(self.training_texts)
                    self.is_fitted = True
                    
            except Exception as e:
                self.logger.error(f"更新词汇表失败: {e}")


class BaseMemory(ABC):
    """记忆基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def store(self, item: Any) -> str:
        """存储记忆项"""
        pass
    
    @abstractmethod
    async def retrieve(self, query: Any) -> List[Any]:
        """检索记忆项"""
        pass
    
    @abstractmethod
    async def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆项"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """删除记忆项"""
        pass
    
    def _generate_id(self, content: Any) -> str:
        """生成记忆项ID"""
        content_str = str(content) if not isinstance(content, str) else content
        return hashlib.md5(content_str.encode()).hexdigest()[:16]


class WorkingMemory(BaseMemory):
    """工作记忆 - 短期记忆，容量有限"""
    
    def __init__(self, capacity: int = 7, config: Optional[Dict[str, Any]] = None):
        # 支持直接传入capacity参数或通过config传入
        if config is None:
            config = {"capacity": capacity}
        elif "capacity" not in config:
            config["capacity"] = capacity
            
        super().__init__(config)
        self.capacity = capacity if capacity != 7 else self.config.get("capacity", 7)
        self.decay_time = self.config.get("decay_time", 300)  # 5 minutes
        self.items = {}  # 改为字典以支持按ID访问
        self._item_order = deque(maxlen=self.capacity)  # 保持插入顺序
        
        # 增强的注意力机制
        self.attention_weights = {}  # 注意力权重映射
        self.activation_levels = {}  # 激活水平映射
        self.attention_history = []  # 注意力历史记录
        self.decay_factor = self.config.get("decay_factor", 0.95)  # 激活衰减因子
        self.attention_threshold = self.config.get("attention_threshold", 0.3)  # 注意力阈值
        
        # 语义嵌入支持
        self.embedding_manager = SemanticEmbeddingManager(
            model_type=self.config.get("embedding_model", "tfidf")
        )
        self.semantic_search_enabled = self.config.get("semantic_search", True)
    
    @property
    def current_size(self) -> int:
        """当前存储的项目数量"""
        return len(self.items)
    
    async def store(self, item: Union[MemoryItem, Any], importance: float = 0.5, attention_weight: float = 1.0) -> Union[bool, str]:
        """存储到工作记忆"""
        # 处理None值
        if item is None:
            return False
        
        # 如果传入的是MemoryItem对象
        if isinstance(item, MemoryItem):
            memory_item = item
            item_id = item.item_id
            # 更新重要性和注意力权重
            memory_item.importance = max(memory_item.importance, importance)
        else:
            # 如果传入的是内容，创建MemoryItem
            item_id = self._generate_id(item)
            memory_item = MemoryItem(
                item_id=item_id,
                content=item,
                memory_type=MemoryType.WORKING,
                importance=importance
            )
        
        # 生成语义嵌入（如果启用且尚未生成）
        if self.semantic_search_enabled and memory_item.embedding is None:
            try:
                embedding, keywords = await self.embedding_manager.generate_embedding(memory_item.content)
                memory_item.embedding = embedding
                memory_item.semantic_keywords = keywords
                memory_item.embedding_model = self.embedding_manager.model_type
            except Exception as e:
                self.logger.warning(f"生成语义嵌入失败: {e}")
        
        # 如果已存在，更新访问信息和注意力
        if item_id in self.items:
            existing_item = self.items[item_id]
            existing_item.access_count += 1
            existing_item.last_accessed = datetime.now()
            # 更新注意力权重
            await self.update_attention_weight(item_id, attention_weight)
            return True
        
        # 检查容量限制
        if len(self.items) >= self.capacity:
            # 移除注意力权重最低的项目
            await self.evict_least_attended_item()
        
        # 添加新项目
        self.items[item_id] = memory_item
        self._item_order.append(item_id)
        
        # 初始化注意力和激活信息
        self.attention_weights[item_id] = attention_weight
        self.activation_levels[item_id] = attention_weight
        
        # 记录注意力历史
        self.attention_history.append({
            'timestamp': datetime.now(),
            'action': 'store',
            'item_id': item_id,
            'attention_weight': attention_weight
        })
        
        # 更新其他项目的激活水平
        await self.update_activation_levels()
        
        return True if isinstance(item, MemoryItem) else item_id
    
    async def update_attention_weight(self, item_id: str, new_weight: float):
        """更新注意力权重"""
        if item_id in self.attention_weights:
            old_weight = self.attention_weights[item_id]
            self.attention_weights[item_id] = new_weight
            self.activation_levels[item_id] = new_weight
            
            # 更新对应记忆项的重要性
            if item_id in self.items:
                self.items[item_id].importance = max(self.items[item_id].importance, new_weight)
                self.items[item_id].last_accessed = datetime.now()
            
            # 记录注意力变化历史
            self.attention_history.append({
                'timestamp': datetime.now(),
                'action': 'update_attention',
                'item_id': item_id,
                'old_weight': old_weight,
                'new_weight': new_weight
            })
            
            # 更新所有项目的激活水平
            await self.update_activation_levels()
    
    async def update_activation_levels(self):
        """更新所有记忆项的激活水平"""
        current_time = datetime.now()
        
        for item_id in list(self.items.keys()):
            if item_id in self.activation_levels:
                # 计算时间衰减
                item = self.items[item_id]
                time_since_access = (current_time - item.last_accessed).total_seconds()
                time_decay = self.decay_factor ** (time_since_access / 60)  # 每分钟衰减
                
                # 更新激活水平
                base_activation = self.attention_weights.get(item_id, 0.5)
                self.activation_levels[item_id] = base_activation * time_decay
    
    async def get_attention_focus(self, top_k: int = 3) -> List[MemoryItem]:
        """获取当前注意力焦点项目"""
        await self.update_activation_levels()
        
        # 按激活水平排序
        focus_items = []
        for item_id, activation in self.activation_levels.items():
            if activation >= self.attention_threshold and item_id in self.items:
                focus_items.append((self.items[item_id], activation))
        
        # 按激活水平降序排序
        focus_items.sort(key=lambda x: x[1], reverse=True)
        
        # 更新访问计数
        result_items = []
        for item, activation in focus_items[:top_k]:
            item.access_count += 1
            item.last_accessed = datetime.now()
            result_items.append(item)
        
        return result_items
    
    async def evict_least_attended_item(self):
        """移除注意力权重最低的项目"""
        if not self.items:
            return
        
        await self.update_activation_levels()
        
        # 找到激活水平最低的项目
        min_activation = float('inf')
        least_attended_id = None
        
        for item_id, activation in self.activation_levels.items():
            if activation < min_activation:
                min_activation = activation
                least_attended_id = item_id
        
        # 移除该项目
        if least_attended_id:
            await self.delete(least_attended_id)
            
            # 记录移除历史
            self.attention_history.append({
                'timestamp': datetime.now(),
                'action': 'evict',
                'item_id': least_attended_id,
                'activation_level': min_activation
            })
    
    async def get_attention_statistics(self) -> Dict[str, Any]:
        """获取注意力统计信息"""
        await self.update_activation_levels()
        
        total_attention = sum(self.attention_weights.values())
        avg_attention = total_attention / len(self.attention_weights) if self.attention_weights else 0
        
        high_attention_items = sum(1 for w in self.attention_weights.values() if w > 0.7)
        focused_items = sum(1 for a in self.activation_levels.values() if a >= self.attention_threshold)
        
        return {
            'total_items': len(self.items),
            'total_attention': total_attention,
            'average_attention': avg_attention,
            'high_attention_items': high_attention_items,
            'focused_items': focused_items,
            'attention_distribution': dict(self.attention_weights),
            'activation_distribution': dict(self.activation_levels),
            'recent_attention_changes': self.attention_history[-10:]  # 最近10次变化
        }
    
    async def retrieve(self, query: Union[str, Any]) -> Optional[MemoryItem]:
        """从工作记忆检索单个项目"""
        current_time = datetime.now()
        
        # 如果query是item_id，直接返回
        if isinstance(query, str) and query in self.items:
            item = self.items[query]
            # 检查是否过期
            if (current_time - item.last_accessed).total_seconds() <= self.decay_time:
                item.access_count += 1
                item.last_accessed = current_time
                return item
            else:
                # 过期项目，移除
                del self.items[query]
                if query in self._item_order:
                    self._item_order.remove(query)
                return None
        
        # 搜索匹配的项目
        for item_id, item in self.items.items():
            # 检查是否过期
            if (current_time - item.last_accessed).total_seconds() > self.decay_time:
                continue
            
            # 简单的匹配逻辑
            if self._matches_query(item.content, query):
                item.access_count += 1
                item.last_accessed = current_time
                return item
        
        return None
    
    async def search(self, query: Optional[Any] = None, tags: Optional[List[str]] = None, 
                    importance_threshold: Optional[float] = None) -> List[MemoryItem]:
        """搜索工作记忆中的项目"""
        current_time = datetime.now()
        results = []
        
        for item_id, item in list(self.items.items()):
            # 检查是否过期
            if (current_time - item.last_accessed).total_seconds() > self.decay_time:
                del self.items[item_id]
                if item_id in self._item_order:
                    self._item_order.remove(item_id)
                continue
            
            # 应用过滤条件
            if tags and not any(tag in item.tags for tag in tags):
                continue
                
            if importance_threshold and item.importance < importance_threshold:
                continue
                
            if query and not self._matches_query(item.content, query):
                continue
            
            # 更新访问信息
            item.access_count += 1
            item.last_accessed = current_time
            results.append(item)
        
        return sorted(results, key=lambda x: x.importance, reverse=True)
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新工作记忆项"""
        if item_id in self.items:
            item = self.items[item_id]
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            item.last_accessed = datetime.now()
            return True
        return False
    
    async def delete(self, item_id: str) -> bool:
        """删除工作记忆项"""
        if item_id in self.items:
            del self.items[item_id]
            if item_id in self._item_order:
                self._item_order.remove(item_id)
            
            # 清理注意力相关数据
            if item_id in self.attention_weights:
                del self.attention_weights[item_id]
            if item_id in self.activation_levels:
                del self.activation_levels[item_id]
            
            # 记录删除历史
            self.attention_history.append({
                'timestamp': datetime.now(),
                'action': 'delete',
                'item_id': item_id
            })
            
            return True
        return False
    
    def _matches_query(self, content: Any, query: Any) -> bool:
        """检查内容是否匹配查询"""
        if query is None:
            return True
            
        content_str = str(content).lower()
        query_str = str(query).lower()
        
        return query_str in content_str
    
    async def get_active_items(self) -> List[MemoryItem]:
        """获取当前活跃的记忆项"""
        current_time = datetime.now()
        active_items = []
        
        for item_id, item in self.items.items():
            if (current_time - item.last_accessed).total_seconds() <= self.decay_time:
                active_items.append(item)
        
        return active_items
    
    async def get_all_items(self) -> List[MemoryItem]:
        """获取所有记忆项（包括过期的）"""
        return list(self.items.values())
    
    @property
    def decay_rate(self) -> float:
        """获取衰减率（为了兼容性）"""
        return 1.0 / self.decay_time if self.decay_time > 0 else 0.0
    
    async def semantic_search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> List[MemoryItem]:
        """基于语义相似性搜索记忆项"""
        if not self.semantic_search_enabled or not query.strip():
            return []
        
        try:
            # 生成查询的语义嵌入
            query_embedding, _ = await self.embedding_manager.generate_embedding(query)
            
            # 收集所有有嵌入的记忆项
            item_embeddings = []
            for item_id, item in self.items.items():
                if item.embedding is not None:
                    item_embeddings.append((item_id, item.embedding))
            
            if not item_embeddings:
                return []
            
            # 找到相似的项目
            similar_items = await self.embedding_manager.find_similar_items(
                query_embedding, item_embeddings, similarity_threshold, top_k
            )
            
            # 构建结果列表
            results = []
            current_time = datetime.now()
            
            for item_id, similarity_score in similar_items:
                if item_id in self.items:
                    item = self.items[item_id]
                    
                    # 检查是否过期
                    if (current_time - item.last_accessed).total_seconds() <= self.decay_time:
                        # 更新访问信息
                        item.access_count += 1
                        item.last_accessed = current_time
                        
                        # 添加相似性分数到元数据
                        item.metadata['similarity_score'] = similarity_score
                        results.append(item)
            
            return results
            
        except Exception as e:
            self.logger.error(f"语义搜索失败: {e}")
            return []
    
    async def hybrid_search(self, query: str, tags: Optional[List[str]] = None, 
                           top_k: int = 5, semantic_weight: float = 0.7) -> List[MemoryItem]:
        """混合搜索：结合关键词匹配和语义相似性"""
        # 关键词搜索结果
        keyword_results = await self.search(query, tags)
        
        # 语义搜索结果
        semantic_results = await self.semantic_search(query, top_k * 2)  # 获取更多候选
        
        # 合并和重新排序结果
        combined_results = {}
        
        # 处理关键词搜索结果
        for item in keyword_results:
            score = (1 - semantic_weight) * item.importance
            combined_results[item.item_id] = {
                'item': item,
                'score': score,
                'keyword_match': True,
                'semantic_match': False
            }
        
        # 处理语义搜索结果
        for item in semantic_results:
            semantic_score = item.metadata.get('similarity_score', 0.0)
            score = semantic_weight * semantic_score
            
            if item.item_id in combined_results:
                # 已存在，合并分数
                combined_results[item.item_id]['score'] += score
                combined_results[item.item_id]['semantic_match'] = True
            else:
                combined_results[item.item_id] = {
                    'item': item,
                    'score': score,
                    'keyword_match': False,
                    'semantic_match': True
                }
        
        # 按综合分数排序
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # 返回top_k结果
        final_results = []
        for result in sorted_results[:top_k]:
            item = result['item']
            item.metadata['hybrid_score'] = result['score']
            item.metadata['keyword_match'] = result['keyword_match']
            item.metadata['semantic_match'] = result['semantic_match']
            final_results.append(item)
        
        return final_results
    
    async def get_semantic_neighbors(self, item_id: str, top_k: int = 3) -> List[Tuple[MemoryItem, float]]:
        """获取指定记忆项的语义邻居"""
        if item_id not in self.items or not self.semantic_search_enabled:
            return []
        
        target_item = self.items[item_id]
        if target_item.embedding is None:
            return []
        
        try:
            # 收集其他记忆项的嵌入
            other_embeddings = []
            for other_id, other_item in self.items.items():
                if other_id != item_id and other_item.embedding is not None:
                    other_embeddings.append((other_id, other_item.embedding))
            
            if not other_embeddings:
                return []
            
            # 找到最相似的项目
            similar_items = await self.embedding_manager.find_similar_items(
                target_item.embedding, other_embeddings, threshold=0.1, top_k=top_k
            )
            
            # 构建结果
            neighbors = []
            for other_id, similarity in similar_items:
                if other_id in self.items:
                    neighbors.append((self.items[other_id], similarity))
            
            return neighbors
            
        except Exception as e:
            self.logger.error(f"获取语义邻居失败: {e}")
            return []


class EpisodicMemoryManager(BaseMemory):
    """情景记忆管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.episodes = {}
        self.time_index = defaultdict(list)  # 按时间索引
        self.participant_index = defaultdict(list)  # 按参与者索引
        self.location_index = defaultdict(list)  # 按位置索引
    
    async def store(self, episode_data: Dict[str, Any]) -> str:
        """存储情景记忆"""
        episode_id = self._generate_id(f"{episode_data.get('event', '')}{datetime.now()}")
        
        episode = EpisodicMemory(
            episode_id=episode_id,
            event=episode_data.get("event", ""),
            context=episode_data.get("context", {}),
            participants=episode_data.get("participants", []),
            location=episode_data.get("location"),
            emotional_valence=episode_data.get("emotional_valence", 0.0),
            importance=episode_data.get("importance", 0.5),
            metadata=episode_data.get("metadata", {})
        )
        
        # 存储主记录
        self.episodes[episode_id] = episode
        
        # 更新索引
        date_key = episode.timestamp.date().isoformat()
        self.time_index[date_key].append(episode_id)
        
        for participant in episode.participants:
            self.participant_index[participant].append(episode_id)
        
        if episode.location:
            self.location_index[episode.location].append(episode_id)
        
        return episode_id
    
    async def retrieve(self, query: Dict[str, Any]) -> List[EpisodicMemory]:
        """检索情景记忆"""
        candidate_ids = set()
        
        # 按时间范围检索
        if "time_range" in query:
            start_date, end_date = query["time_range"]
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.isoformat()
                candidate_ids.update(self.time_index.get(date_key, []))
                current_date += timedelta(days=1)
        
        # 按参与者检索
        if "participants" in query:
            for participant in query["participants"]:
                candidate_ids.update(self.participant_index.get(participant, []))
        
        # 按位置检索
        if "location" in query:
            candidate_ids.update(self.location_index.get(query["location"], []))
        
        # 如果没有特定条件，返回所有记忆
        if not candidate_ids:
            candidate_ids = set(self.episodes.keys())
        
        # 过滤和排序
        matching_episodes = []
        for episode_id in candidate_ids:
            episode = self.episodes.get(episode_id)
            if episode and self._matches_episode_query(episode, query):
                matching_episodes.append(episode)
        
        # 按重要性和时间排序
        return sorted(matching_episodes, 
                     key=lambda x: (x.importance, x.timestamp), 
                     reverse=True)
    
    async def update(self, episode_id: str, updates: Dict[str, Any]) -> bool:
        """更新情景记忆"""
        if episode_id in self.episodes:
            episode = self.episodes[episode_id]
            for key, value in updates.items():
                if hasattr(episode, key):
                    setattr(episode, key, value)
            episode.updated_at = datetime.now()
            return True
        return False
    
    async def delete(self, episode_id: str) -> bool:
        """删除情景记忆"""
        if episode_id in self.episodes:
            episode = self.episodes[episode_id]
            
            # 从索引中移除
            date_key = episode.timestamp.date().isoformat()
            if date_key in self.time_index:
                self.time_index[date_key].remove(episode_id)
            
            for participant in episode.participants:
                if participant in self.participant_index:
                    self.participant_index[participant].remove(episode_id)
            
            if episode.location and episode.location in self.location_index:
                self.location_index[episode.location].remove(episode_id)
            
            # 删除主记录
            del self.episodes[episode_id]
            return True
        return False
    
    def _matches_episode_query(self, episode: EpisodicMemory, query: Dict[str, Any]) -> bool:
        """检查情景是否匹配查询"""
        if "event_keywords" in query:
            event_text = episode.event.lower()
            for keyword in query["event_keywords"]:
                if keyword.lower() not in event_text:
                    return False
        
        if "importance_threshold" in query:
            if episode.importance < query["importance_threshold"]:
                return False
        
        if "emotional_range" in query:
            min_val, max_val = query["emotional_range"]
            if not (min_val <= episode.emotional_valence <= max_val):
                return False
        
        return True
    
    async def get_related_episodes(self, episode_id: str, max_results: int = 10) -> List[EpisodicMemory]:
        """获取相关情景"""
        if episode_id not in self.episodes:
            return []
        
        target_episode = self.episodes[episode_id]
        related_episodes = []
        
        # 查找相关情景（简化实现）
        for other_id, other_episode in self.episodes.items():
            if other_id == episode_id:
                continue
            
            # 计算相关性
            relevance_score = self._calculate_episode_relevance(target_episode, other_episode)
            if relevance_score > 0.3:  # 相关性阈值
                related_episodes.append((other_episode, relevance_score))
        
        # 按相关性排序
        related_episodes.sort(key=lambda x: x[1], reverse=True)
        return [episode for episode, score in related_episodes[:max_results]]
    
    def _calculate_episode_relevance(self, episode1: EpisodicMemory, episode2: EpisodicMemory) -> float:
        """计算两个情景的相关性"""
        relevance = 0.0
        
        # 参与者重叠
        common_participants = set(episode1.participants) & set(episode2.participants)
        if common_participants:
            relevance += 0.3 * len(common_participants) / max(len(episode1.participants), len(episode2.participants))
        
        # 位置相同
        if episode1.location and episode2.location and episode1.location == episode2.location:
            relevance += 0.2
        
        # 时间接近
        time_diff = abs((episode1.timestamp - episode2.timestamp).total_seconds())
        if time_diff < 3600:  # 1小时内
            relevance += 0.3
        elif time_diff < 86400:  # 1天内
            relevance += 0.2
        
        # 情感相似
        emotional_similarity = 1.0 - abs(episode1.emotional_valence - episode2.emotional_valence) / 2.0
        relevance += 0.2 * emotional_similarity
        
        return min(relevance, 1.0)


class SemanticMemoryManager(BaseMemory):
    """语义记忆管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.concepts = {}
        self.concept_index = defaultdict(set)  # 概念索引
        self.relationship_graph = defaultdict(dict)  # 关系图
    
    async def store(self, concept_data: Dict[str, Any]) -> str:
        """存储语义记忆"""
        concept_id = self._generate_id(concept_data.get("concept", ""))
        
        concept = SemanticMemory(
            concept_id=concept_id,
            concept=concept_data.get("concept", ""),
            definition=concept_data.get("definition", ""),
            properties=concept_data.get("properties", {}),
            relationships=concept_data.get("relationships", {}),
            confidence=concept_data.get("confidence", 1.0),
            source=concept_data.get("source"),
            metadata=concept_data.get("metadata", {})
        )
        
        # 存储主记录
        self.concepts[concept_id] = concept
        
        # 更新概念索引
        concept_words = concept.concept.lower().split()
        for word in concept_words:
            self.concept_index[word].add(concept_id)
        
        # 更新关系图
        for relation_type, related_concepts in concept.relationships.items():
            if concept_id not in self.relationship_graph:
                self.relationship_graph[concept_id] = {}
            self.relationship_graph[concept_id][relation_type] = related_concepts
        
        return concept_id
    
    async def retrieve(self, query: Union[str, Dict[str, Any]]) -> List[SemanticMemory]:
        """检索语义记忆"""
        if isinstance(query, str):
            query = {"concept": query}
        
        candidate_ids = set()
        
        # 按概念名称检索
        if "concept" in query:
            query_words = query["concept"].lower().split()
            for word in query_words:
                candidate_ids.update(self.concept_index.get(word, set()))
        
        # 按属性检索
        if "properties" in query:
            for concept_id, concept in self.concepts.items():
                if self._matches_properties(concept.properties, query["properties"]):
                    candidate_ids.add(concept_id)
        
        # 如果没有候选项，返回所有概念
        if not candidate_ids:
            candidate_ids = set(self.concepts.keys())
        
        # 过滤和排序
        matching_concepts = []
        for concept_id in candidate_ids:
            concept = self.concepts.get(concept_id)
            if concept and self._matches_concept_query(concept, query):
                matching_concepts.append(concept)
        
        # 按置信度排序
        return sorted(matching_concepts, key=lambda x: x.confidence, reverse=True)
    
    async def update(self, concept_id: str, updates: Dict[str, Any]) -> bool:
        """更新语义记忆"""
        if concept_id in self.concepts:
            concept = self.concepts[concept_id]
            for key, value in updates.items():
                if hasattr(concept, key):
                    setattr(concept, key, value)
            concept.updated_at = datetime.now()
            return True
        return False
    
    async def delete(self, concept_id: str) -> bool:
        """删除语义记忆"""
        if concept_id in self.concepts:
            concept = self.concepts[concept_id]
            
            # 从概念索引中移除
            concept_words = concept.concept.lower().split()
            for word in concept_words:
                if word in self.concept_index:
                    self.concept_index[word].discard(concept_id)
            
            # 从关系图中移除
            if concept_id in self.relationship_graph:
                del self.relationship_graph[concept_id]
            
            # 删除主记录
            del self.concepts[concept_id]
            return True
        return False
    
    def _matches_properties(self, concept_props: Dict[str, Any], query_props: Dict[str, Any]) -> bool:
        """检查属性是否匹配"""
        for key, value in query_props.items():
            if key not in concept_props or concept_props[key] != value:
                return False
        return True
    
    def _matches_concept_query(self, concept: SemanticMemory, query: Dict[str, Any]) -> bool:
        """检查概念是否匹配查询"""
        if "confidence_threshold" in query:
            if concept.confidence < query["confidence_threshold"]:
                return False
        
        if "definition_keywords" in query:
            definition_text = concept.definition.lower()
            for keyword in query["definition_keywords"]:
                if keyword.lower() not in definition_text:
                    return False
        
        return True
    
    async def get_related_concepts(self, concept_id: str, relation_type: Optional[str] = None) -> List[SemanticMemory]:
        """获取相关概念"""
        if concept_id not in self.concepts:
            return []
        
        related_concepts = []
        
        if concept_id in self.relationship_graph:
            relationships = self.relationship_graph[concept_id]
            
            if relation_type:
                # 获取特定关系类型的概念
                related_ids = relationships.get(relation_type, [])
                for related_id in related_ids:
                    if related_id in self.concepts:
                        related_concepts.append(self.concepts[related_id])
            else:
                # 获取所有相关概念
                for relation_type, related_ids in relationships.items():
                    for related_id in related_ids:
                        if related_id in self.concepts:
                            related_concepts.append(self.concepts[related_id])
        
        return related_concepts


class ProceduralMemoryManager(BaseMemory):
    """程序记忆管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.procedures = {}
        self.name_index = defaultdict(list)
        self.skill_index = defaultdict(list)
    
    async def store(self, procedure_data: Dict[str, Any]) -> str:
        """存储程序记忆"""
        procedure_id = self._generate_id(procedure_data.get("name", ""))
        
        procedure = ProceduralMemory(
            procedure_id=procedure_id,
            name=procedure_data.get("name", ""),
            description=procedure_data.get("description", ""),
            steps=procedure_data.get("steps", []),
            preconditions=procedure_data.get("preconditions", []),
            postconditions=procedure_data.get("postconditions", []),
            metadata=procedure_data.get("metadata", {})
        )
        
        # 存储主记录
        self.procedures[procedure_id] = procedure
        
        # 更新索引
        name_words = procedure.name.lower().split()
        for word in name_words:
            self.name_index[word].append(procedure_id)
        
        # 技能分类索引
        skill_category = procedure.metadata.get("category", "general")
        self.skill_index[skill_category].append(procedure_id)
        
        return procedure_id
    
    async def retrieve(self, query: Union[str, Dict[str, Any]]) -> List[ProceduralMemory]:
        """检索程序记忆"""
        if isinstance(query, str):
            query = {"name": query}
        
        candidate_ids = set()
        
        # 按名称检索
        if "name" in query:
            query_words = query["name"].lower().split()
            for word in query_words:
                candidate_ids.update(self.name_index.get(word, []))
        
        # 按技能类别检索
        if "category" in query:
            candidate_ids.update(self.skill_index.get(query["category"], []))
        
        # 如果没有候选项，返回所有程序
        if not candidate_ids:
            candidate_ids = set(self.procedures.keys())
        
        # 过滤和排序
        matching_procedures = []
        for procedure_id in candidate_ids:
            procedure = self.procedures.get(procedure_id)
            if procedure and self._matches_procedure_query(procedure, query):
                matching_procedures.append(procedure)
        
        # 按成功率和使用次数排序
        return sorted(matching_procedures, 
                     key=lambda x: (x.success_rate, x.usage_count), 
                     reverse=True)
    
    async def update(self, procedure_id: str, updates: Dict[str, Any]) -> bool:
        """更新程序记忆"""
        if procedure_id in self.procedures:
            procedure = self.procedures[procedure_id]
            for key, value in updates.items():
                if hasattr(procedure, key):
                    setattr(procedure, key, value)
            return True
        return False
    
    async def delete(self, procedure_id: str) -> bool:
        """删除程序记忆"""
        if procedure_id in self.procedures:
            procedure = self.procedures[procedure_id]
            
            # 从名称索引中移除
            name_words = procedure.name.lower().split()
            for word in name_words:
                if word in self.name_index:
                    self.name_index[word].remove(procedure_id)
            
            # 从技能索引中移除
            skill_category = procedure.metadata.get("category", "general")
            if skill_category in self.skill_index:
                self.skill_index[skill_category].remove(procedure_id)
            
            # 删除主记录
            del self.procedures[procedure_id]
            return True
        return False
    
    def _matches_procedure_query(self, procedure: ProceduralMemory, query: Dict[str, Any]) -> bool:
        """检查程序是否匹配查询"""
        if "success_rate_threshold" in query:
            if procedure.success_rate < query["success_rate_threshold"]:
                return False
        
        if "description_keywords" in query:
            description_text = procedure.description.lower()
            for keyword in query["description_keywords"]:
                if keyword.lower() not in description_text:
                    return False
        
        return True
    
    async def execute_procedure(self, procedure_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行程序（模拟）"""
        if procedure_id not in self.procedures:
            return {"success": False, "error": "Procedure not found"}
        
        procedure = self.procedures[procedure_id]
        
        # 检查前置条件
        for precondition in procedure.preconditions:
            if not self._check_condition(precondition, context):
                return {"success": False, "error": f"Precondition not met: {precondition}"}
        
        # 更新使用统计
        procedure.usage_count += 1
        procedure.last_used = datetime.now()
        
        # 模拟执行
        execution_result = {
            "success": True,
            "procedure_id": procedure_id,
            "steps_executed": len(procedure.steps),
            "execution_time": datetime.now(),
            "context": context
        }
        
        return execution_result
    
    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """检查条件是否满足（简化实现）"""
        # 简单的条件检查
        return condition.lower() in str(context).lower()


class MemoryConsolidator:
    """记忆整合器 - 将工作记忆转移到长期记忆"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.consolidation_threshold = self.config.get("consolidation_threshold", 0.7)
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # 添加测试期望的属性
        self.consolidation_strategies = self.config.get("strategies", ["importance", "frequency", "recency"])
        
        # 增强的整合参数
        self.access_count_threshold = self.config.get("access_count_threshold", 3)
        self.age_threshold_hours = self.config.get("age_threshold_hours", 24)
        self.semantic_clustering_enabled = self.config.get("semantic_clustering", True)
        self.consolidation_batch_size = self.config.get("batch_size", 10)
    
    async def consolidate_memories(self, working_items: List[MemoryItem]) -> List[MemoryItem]:
        """整合记忆项（测试期望的方法签名）"""
        consolidated_items = []
        
        for item in working_items:
            # 根据多维度策略决定是否整合
            if await self._should_consolidate(item):
                # 创建整合后的记忆项
                consolidated_item = await self._create_consolidated_memory(item)
                consolidated_items.append(consolidated_item)
        
        # 如果启用语义聚类，对整合的记忆进行聚类
        if self.semantic_clustering_enabled and len(consolidated_items) > 1:
            consolidated_items = await self._apply_semantic_clustering(consolidated_items)
        
        return consolidated_items
    
    async def _should_consolidate(self, item: MemoryItem) -> bool:
        """判断记忆项是否应该被整合"""
        consolidation_score = 0.0
        
        # 策略1：重要性评分
        if "importance" in self.consolidation_strategies:
            if item.importance >= self.consolidation_threshold:
                consolidation_score += 0.4
        
        # 策略2：访问频率
        if "frequency" in self.consolidation_strategies:
            if item.access_count >= self.access_count_threshold:
                consolidation_score += 0.3
        
        # 策略3：时间因素（最近性）
        if "recency" in self.consolidation_strategies:
            hours_since_creation = (datetime.now() - item.created_at).total_seconds() / 3600
            if hours_since_creation >= self.age_threshold_hours:
                consolidation_score += 0.2
            
            # 最近访问的记忆更容易被整合
            hours_since_access = (datetime.now() - item.last_accessed).total_seconds() / 3600
            if hours_since_access < 1:  # 1小时内访问过
                consolidation_score += 0.1
        
        # 策略4：语义丰富度
        if hasattr(item, 'semantic_keywords') and item.semantic_keywords:
            if len(item.semantic_keywords) >= 3:
                consolidation_score += 0.1
        
        # 策略5：标签丰富度
        if item.tags and len(item.tags) >= 2:
            consolidation_score += 0.1
        
        return consolidation_score >= 0.5  # 综合评分阈值
    
    async def _create_consolidated_memory(self, item: MemoryItem) -> MemoryItem:
        """创建整合后的记忆项"""
        # 确定目标记忆类型
        target_memory_type = await self._determine_target_memory_type(item)
        
        # 增强元数据
        enhanced_metadata = {
            **item.metadata,
            "consolidated_at": datetime.now().isoformat(),
            "original_memory_type": item.memory_type.value,
            "consolidation_score": await self._calculate_consolidation_score(item),
            "consolidation_reason": await self._get_consolidation_reason(item)
        }
        
        # 创建整合后的记忆项
        consolidated_item = MemoryItem(
            item_id=f"consolidated_{item.item_id}",
            content=item.content,
            memory_type=target_memory_type,
            importance=min(item.importance * 1.1, 1.0),  # 略微提升重要性
            access_count=item.access_count,
            last_accessed=item.last_accessed,
            created_at=item.created_at,
            tags=item.tags + ["consolidated"],
            metadata=enhanced_metadata
        )
        
        # 保留语义嵌入信息
        if hasattr(item, 'embedding') and item.embedding is not None:
            consolidated_item.embedding = item.embedding
            consolidated_item.embedding_model = getattr(item, 'embedding_model', None)
            consolidated_item.semantic_keywords = getattr(item, 'semantic_keywords', [])
        
        return consolidated_item
    
    async def _determine_target_memory_type(self, item: MemoryItem) -> MemoryType:
        """确定目标记忆类型"""
        content_str = str(item.content).lower()
        
        # 基于内容特征判断记忆类型
        if any(keyword in content_str for keyword in ['步骤', '方法', '流程', '算法', '如何', 'how to']):
            return MemoryType.PROCEDURAL
        elif any(keyword in content_str for keyword in ['事件', '发生', '经历', '过程', '时间']):
            return MemoryType.EPISODIC
        elif any(keyword in content_str for keyword in ['概念', '定义', '知识', '原理', '理论']):
            return MemoryType.SEMANTIC
        else:
            # 默认转为语义记忆
            return MemoryType.SEMANTIC
    
    async def _calculate_consolidation_score(self, item: MemoryItem) -> float:
        """计算整合评分"""
        score = item.importance * 0.4
        score += min(item.access_count / 10.0, 0.3)
        
        # 时间因素
        hours_since_creation = (datetime.now() - item.created_at).total_seconds() / 3600
        age_factor = min(hours_since_creation / 24.0, 0.2)
        score += age_factor
        
        # 内容丰富度
        content_length = len(str(item.content))
        length_factor = min(content_length / 100.0, 0.1)
        score += length_factor
        
        return min(score, 1.0)
    
    async def _get_consolidation_reason(self, item: MemoryItem) -> str:
        """获取整合原因"""
        reasons = []
        
        if item.importance >= self.consolidation_threshold:
            reasons.append("高重要性")
        
        if item.access_count >= self.access_count_threshold:
            reasons.append("高访问频率")
        
        hours_since_creation = (datetime.now() - item.created_at).total_seconds() / 3600
        if hours_since_creation >= self.age_threshold_hours:
            reasons.append("达到时间阈值")
        
        if hasattr(item, 'semantic_keywords') and len(getattr(item, 'semantic_keywords', [])) >= 3:
            reasons.append("语义丰富")
        
        if len(item.tags) >= 2:
            reasons.append("标签丰富")
        
        return "、".join(reasons) if reasons else "综合评分达标"
    
    async def _apply_semantic_clustering(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """对记忆项应用语义聚类"""
        if len(items) <= 1:
            return items
        
        try:
            # 收集有嵌入的项目
            items_with_embeddings = []
            items_without_embeddings = []
            
            for item in items:
                if hasattr(item, 'embedding') and item.embedding is not None:
                    items_with_embeddings.append(item)
                else:
                    items_without_embeddings.append(item)
            
            if len(items_with_embeddings) < 2:
                return items
            
            # 简单的语义聚类：找到相似的记忆并合并相关信息
            clustered_items = []
            processed_ids = set()
            
            for i, item in enumerate(items_with_embeddings):
                if item.item_id in processed_ids:
                    continue
                
                # 找到与当前项目相似的其他项目
                similar_items = [item]
                processed_ids.add(item.item_id)
                
                for j, other_item in enumerate(items_with_embeddings[i+1:], i+1):
                    if other_item.item_id in processed_ids:
                        continue
                    
                    # 计算相似性
                    similarity = await self._calculate_embedding_similarity(item.embedding, other_item.embedding)
                    
                    if similarity > 0.6:  # 相似度阈值
                        similar_items.append(other_item)
                        processed_ids.add(other_item.item_id)
                
                # 如果找到相似项目，创建聚类记忆
                if len(similar_items) > 1:
                    clustered_item = await self._create_clustered_memory(similar_items)
                    clustered_items.append(clustered_item)
                else:
                    clustered_items.append(item)
            
            # 添加没有嵌入的项目
            clustered_items.extend(items_without_embeddings)
            
            return clustered_items
            
        except Exception as e:
            self.logger.warning(f"语义聚类失败: {e}")
            return items
    
    async def _calculate_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """计算嵌入相似性"""
        try:
            if len(emb1) != len(emb2):
                return 0.0
            
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            return max(0.0, min(1.0, similarity))
        except:
            return 0.0
    
    async def _create_clustered_memory(self, similar_items: List[MemoryItem]) -> MemoryItem:
        """创建聚类记忆项"""
        # 选择重要性最高的作为主项目
        main_item = max(similar_items, key=lambda x: x.importance)
        
        # 合并内容和标签
        all_contents = [str(item.content) for item in similar_items]
        all_tags = set()
        total_access_count = 0
        
        for item in similar_items:
            all_tags.update(item.tags)
            total_access_count += item.access_count
        
        # 创建聚类后的记忆项
        clustered_item = MemoryItem(
            item_id=f"cluster_{main_item.item_id}",
            content=main_item.content,  # 保持主要内容
            memory_type=main_item.memory_type,
            importance=min(main_item.importance * 1.2, 1.0),
            access_count=total_access_count,
            last_accessed=max(item.last_accessed for item in similar_items),
            created_at=min(item.created_at for item in similar_items),
            tags=list(all_tags) + ["clustered"],
            metadata={
                **main_item.metadata,
                "clustered_at": datetime.now().isoformat(),
                "cluster_size": len(similar_items),
                "clustered_contents": all_contents,
                "cluster_items": [item.item_id for item in similar_items]
            }
        )
        
        # 保留语义信息
        if hasattr(main_item, 'embedding'):
            clustered_item.embedding = main_item.embedding
            clustered_item.embedding_model = getattr(main_item, 'embedding_model', None)
            clustered_item.semantic_keywords = getattr(main_item, 'semantic_keywords', [])
        
        return clustered_item


class MemoryRetriever:
    """记忆检索器 - 统一的记忆检索接口"""
    
    def __init__(self, memory_system: Optional['MemorySystem'] = None):
        self.memory_system = memory_system
        # 添加测试期望的属性
        self.retrieval_strategies = {
            "similarity": "cosine",
            "keyword": "exact_match",
            "temporal": "recent_first",
            "importance": "weight_based"
        }
    
    async def retrieve_similar(self, query: str, memories: List[MemoryItem], top_k: int = 5) -> List[MemoryItem]:
        """基于相似性检索记忆项（测试期望的方法）"""
        if not memories:
            return []
        
        # 简单的相似性计算（基于关键词匹配）
        query_lower = query.lower()
        scored_memories = []
        
        for memory in memories:
            content_str = str(memory.content).lower()
            # 计算简单的相似性分数
            similarity_score = 0.0
            
            # 关键词匹配
            if query_lower in content_str:
                similarity_score += 1.0
            
            # 单词重叠
            query_words = set(query_lower.split())
            content_words = set(content_str.split())
            overlap = len(query_words.intersection(content_words))
            if len(query_words) > 0:
                similarity_score += overlap / len(query_words)
            
            # 结合重要性
            final_score = similarity_score * memory.importance
            
            if final_score > 0:
                scored_memories.append((memory, final_score))
        
        # 按分数排序并返回top_k个结果
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in scored_memories[:top_k]]
    
    async def retrieve_memories(self, 
                               query: Any, 
                               memory_types: Optional[List[MemoryType]] = None,
                               max_results: int = 10) -> Dict[str, List[Any]]:
        """跨记忆类型检索"""
        if memory_types is None:
            memory_types = [MemoryType.WORKING, MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]
        
        results = {}
        
        # 并行检索不同类型的记忆
        tasks = []
        
        if MemoryType.WORKING in memory_types:
            tasks.append(self._retrieve_working(query, max_results))
        
        if MemoryType.EPISODIC in memory_types:
            tasks.append(self._retrieve_episodic(query, max_results))
        
        if MemoryType.SEMANTIC in memory_types:
            tasks.append(self._retrieve_semantic(query, max_results))
        
        if MemoryType.PROCEDURAL in memory_types:
            tasks.append(self._retrieve_procedural(query, max_results))
        
        # 等待所有检索完成
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        memory_type_names = [mt.value for mt in memory_types]
        for i, result in enumerate(task_results):
            if not isinstance(result, Exception):
                results[memory_type_names[i]] = result
        
        return results
    
    async def _retrieve_working(self, query: Any, max_results: int) -> List[MemoryItem]:
        """检索工作记忆"""
        return await self.memory_system.working_memory.search(query)
    
    async def _retrieve_episodic(self, query: Any, max_results: int) -> List[EpisodicMemory]:
        """检索情景记忆"""
        if isinstance(query, str):
            query = {"event_keywords": [query]}
        return await self.memory_system.episodic_memory.retrieve(query)
    
    async def _retrieve_semantic(self, query: Any, max_results: int) -> List[SemanticMemory]:
        """检索语义记忆"""
        return await self.memory_system.semantic_memory.retrieve(query)
    
    async def _retrieve_procedural(self, query: Any, max_results: int) -> List[ProceduralMemory]:
        """检索程序记忆"""
        return await self.memory_system.procedural_memory.retrieve(query)


class ForgettingMechanism:
    """遗忘机制 - 管理记忆的衰减和清理"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.forgetting_curve_factor = self.config.get("forgetting_curve_factor", 0.1)
        self.cleanup_interval = self.config.get("cleanup_interval", 86400)  # 24小时
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # 添加测试期望的属性
        self.decay_rate = self.config.get("decay_rate", 0.1)
        self.forgetting_curve = self.config.get("forgetting_curve", "exponential")
    
    def calculate_decay(self, last_accessed: datetime, current_time: datetime) -> float:
        """计算记忆衰减值（测试期望的方法）"""
        time_diff = (current_time - last_accessed).total_seconds()
        # 使用指数衰减公式
        decay = 1.0 - (1.0 / (1.0 + self.decay_rate * time_diff / 3600))  # 按小时计算
        return max(0.0, min(1.0, decay))
    
    async def apply_forgetting(self, memories_or_system: Union[List[MemoryItem], 'MemorySystem']) -> Union[List[MemoryItem], Dict[str, Any]]:
        """应用遗忘机制 - 支持两种调用方式"""
        # 如果传入的是记忆项列表（测试期望的接口）
        if isinstance(memories_or_system, list):
            return await self._apply_forgetting_to_list(memories_or_system)
        
        # 如果传入的是记忆系统（原有接口）
        else:
            return await self._apply_forgetting_to_system(memories_or_system)
    
    async def _apply_forgetting_to_list(self, memories: List[MemoryItem]) -> List[MemoryItem]:
        """对记忆项列表应用遗忘机制"""
        current_time = datetime.now()
        surviving_memories = []
        
        for memory in memories:
            # 计算衰减值
            decay = self.calculate_decay(memory.last_accessed, current_time)
            
            # 根据衰减值决定是否保留记忆
            # 衰减值越高，越容易被遗忘
            if decay < 0.8:  # 衰减值小于0.8的记忆被保留
                # 更新记忆的重要性（被衰减影响）
                memory.importance = memory.importance * (1 - decay * 0.5)
                surviving_memories.append(memory)
        
        return surviving_memories
    
    async def _apply_forgetting_to_system(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """对记忆系统应用遗忘机制"""
        forgetting_stats = {
            "working_items_forgotten": 0,
            "episodic_items_forgotten": 0,
            "semantic_items_forgotten": 0,
            "procedural_items_forgotten": 0
        }
        
        # 清理过期的工作记忆
        forgotten_working = await self._cleanup_working_memory(memory_system.working_memory)
        forgetting_stats["working_items_forgotten"] = forgotten_working
        
        # 应用遗忘曲线到长期记忆
        forgotten_episodic = await self._apply_forgetting_curve_episodic(memory_system.episodic_memory)
        forgetting_stats["episodic_items_forgotten"] = forgotten_episodic
        
        return forgetting_stats
    
    async def _cleanup_working_memory(self, working_memory: WorkingMemory) -> int:
        """清理工作记忆"""
        current_time = datetime.now()
        items_to_remove = []
        
        for item_id in list(working_memory.items.keys()): # Iterate over keys to allow deletion
            item = working_memory.items[item_id]
            time_since_access = (current_time - item.last_accessed).total_seconds()
            if time_since_access > working_memory.decay_time:
                items_to_remove.append(item_id)
        
        # 移除过期项目
        for item_id in items_to_remove:
            await working_memory.delete(item_id)
        
        return len(items_to_remove)
    
    async def _apply_forgetting_curve_episodic(self, episodic_memory: EpisodicMemoryManager) -> int:
        """对情景记忆应用遗忘曲线"""
        current_time = datetime.now()
        items_to_remove = []
        
        for episode_id, episode in episodic_memory.episodes.items():
            days_since_creation = (current_time - episode.timestamp).days
            
            # 计算遗忘概率
            forgetting_probability = self._calculate_forgetting_probability(
                days_since_creation, episode.importance
            )
            
            # 简化的遗忘决策
            if forgetting_probability > 0.8 and episode.importance < 0.3:
                items_to_remove.append(episode_id)
        
        # 移除被遗忘的项目
        for episode_id in items_to_remove:
            await episodic_memory.delete(episode_id)
        
        return len(items_to_remove)
    
    def _calculate_forgetting_probability(self, days_elapsed: int, importance: float) -> float:
        """计算遗忘概率（基于Ebbinghaus遗忘曲线）"""
        import math
        
        # 重要性越高，遗忘越慢
        importance_factor = 1.0 - importance
        
        # 遗忘曲线：R = e^(-t/S)，其中t是时间，S是记忆强度
        memory_strength = 1.0 / (importance_factor * self.forgetting_curve_factor + 0.1)
        forgetting_probability = 1.0 - math.exp(-days_elapsed / memory_strength)
        
        return min(forgetting_probability, 0.95)  # 最大95%遗忘概率


class MemorySystem:
    """统一记忆系统"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 初始化各种记忆组件
        self.working_memory = WorkingMemory(self.config.get("working", {}).get("capacity", 7), self.config.get("working", {}))
        self.episodic_memory = EpisodicMemoryManager(self.config.get("episodic", {}))
        self.semantic_memory = SemanticMemoryManager(self.config.get("semantic", {}))
        self.procedural_memory = ProceduralMemoryManager(self.config.get("procedural", {}))
        
        # 初始化记忆管理组件
        self.consolidator = MemoryConsolidator(self.config.get("consolidation", {}))
        self.retriever = MemoryRetriever(self)
        self.forgetting_mechanism = ForgettingMechanism(self.config.get("forgetting", {}))
        
        # 初始化元记忆系统
        self.meta_memory = MetaMemorySystem(self, self.config.get("meta_memory", {}))
        
        # 初始化持久化管理器
        from .memory_persistence import MemoryPersistenceManager, PersistenceConfig
        persistence_config = self.config.get("persistence", {})
        self.persistence_manager = MemoryPersistenceManager(
            PersistenceConfig(**persistence_config) if persistence_config else PersistenceConfig()
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化记忆系统"""
        if self._initialized:
            return
        
        try:
            await self.persistence_manager.initialize()
            self._initialized = True
            self.logger.info("Memory system initialized with persistence")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory system: {e}")
            raise
    
    async def shutdown(self) -> None:
        """关闭记忆系统"""
        if not self._initialized:
            return
        
        try:
            await self.persistence_manager.shutdown()
            self._initialized = False
            self.logger.info("Memory system shut down")
        except Exception as e:
            self.logger.error(f"Error during memory system shutdown: {e}")
    
    async def store_memory(self, item_or_content: Union[MemoryItem, Any], memory_type: Optional[MemoryType] = None, **kwargs) -> Union[str, bool]:
        """存储记忆到指定类型的记忆系统"""
        # 确保系统已初始化
        if not self._initialized:
            await self.initialize()
        
        # 如果传入的是MemoryItem对象，从对象中获取memory_type
        if isinstance(item_or_content, MemoryItem):
            memory_type = item_or_content.memory_type
            content = item_or_content
        else:
            content = item_or_content
            if memory_type is None:
                raise ValueError("memory_type is required when storing non-MemoryItem content")
        
        # 存储到内存系统
        result = None
        if memory_type == MemoryType.WORKING:
            result = await self.working_memory.store(content, kwargs.get("importance", 0.5))
            memory_item = content if isinstance(content, MemoryItem) else None
        elif memory_type == MemoryType.EPISODIC:
            result = await self.episodic_memory.store(kwargs)
            # 创建对应的MemoryItem用于持久化
            memory_item = MemoryItem(
                item_id=str(uuid.uuid4()),
                content=kwargs.get("event", ""),
                memory_type=MemoryType.EPISODIC,
                importance=kwargs.get("importance", 0.5),
                metadata=kwargs
            )
        elif memory_type == MemoryType.SEMANTIC:
            result = await self.semantic_memory.store(kwargs)
            # 创建对应的MemoryItem用于持久化
            memory_item = MemoryItem(
                item_id=str(uuid.uuid4()),
                content=kwargs.get("concept", ""),
                memory_type=MemoryType.SEMANTIC,
                importance=kwargs.get("confidence", 1.0),
                metadata=kwargs
            )
        elif memory_type == MemoryType.PROCEDURAL:
            result = await self.procedural_memory.store(kwargs)
            # 创建对应的MemoryItem用于持久化
            memory_item = MemoryItem(
                item_id=str(uuid.uuid4()),
                content=kwargs.get("name", ""),
                memory_type=MemoryType.PROCEDURAL,
                importance=kwargs.get("success_rate", 1.0),
                metadata=kwargs
            )
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")
        
        # 持久化存储
        try:
            if memory_item:
                await self.persistence_manager.store_memory_item(memory_item)
                self.logger.debug(f"Persisted {memory_type.value} memory: {memory_item.item_id}")
        except Exception as e:
            self.logger.warning(f"Failed to persist {memory_type.value} memory: {e}")
        
        return result
    
    async def retrieve_memory(self, 
                             query: Any, 
                             memory_type: MemoryType = None,
                             memory_types: List[MemoryType] = None,
                             max_results: int = 10) -> Union[Optional[MemoryItem], Dict[str, List[MemoryItem]]]:
        """检索记忆项 - 支持单类型和多类型检索"""
        # 确保系统已初始化
        if not self._initialized:
            await self.initialize()
        
        # 处理参数
        if memory_type is not None and memory_types is not None:
            raise ValueError("Cannot specify both memory_type and memory_types")
        
        if memory_type is not None:
            memory_types = [memory_type]
            single_type = True
        elif memory_types is not None:
            single_type = False
        else:
            memory_types = list(MemoryType)
            single_type = False
        
        # 首先尝试从内存中检索
        memory_results = {}
        
        for mtype in memory_types:
            if mtype == MemoryType.WORKING:
                result = await self.working_memory.retrieve(query)
                memory_results[mtype.value] = [result] if result else []
            else:
                # 对于其他类型，使用统一检索接口
                results = await self.retriever.retrieve_memories(query, [mtype], max_results)
                memory_results[mtype.value] = results.get(mtype.value, [])
        
        # 从持久化存储中检索补充结果
        try:
            persisted_items = await self.persistence_manager.search_memory_items(
                memory_types=memory_types,
                max_results=max_results
            )
            
            # 合并结果，避免重复
            for item in persisted_items:
                mtype_name = item.memory_type.value
                if mtype_name in memory_results:
                    # 检查是否已存在（基于content hash）
                    existing_ids = {getattr(existing_item, 'item_id', None) for existing_item in memory_results[mtype_name]}
                    if item.item_id not in existing_ids:
                        memory_results[mtype_name].append(item)
                else:
                    memory_results[mtype_name] = [item]
            
            # 限制结果数量并按重要性排序
            for mtype_name in memory_results:
                memory_results[mtype_name] = sorted(
                    memory_results[mtype_name][:max_results],
                    key=lambda x: getattr(x, 'importance', 0.0),
                    reverse=True
                )
        
        except Exception as e:
            self.logger.warning(f"Failed to retrieve from persistence: {e}")
        
        # 返回结果
        if single_type:
            mtype_name = memory_types[0].value
            results = memory_results.get(mtype_name, [])
            return results[0] if results else None
        else:
            return memory_results
    
    async def search_memories(self, 
                             query: Optional[Any] = None,
                             tags: Optional[List[str]] = None,
                             memory_types: Optional[List[MemoryType]] = None,
                             max_results: int = 10) -> List[MemoryItem]:
        """搜索记忆项"""
        if memory_types is None:
            memory_types = [MemoryType.WORKING]  # 默认只搜索工作记忆
        
        all_results = []
        
        for memory_type in memory_types:
            if memory_type == MemoryType.WORKING:
                results = await self.working_memory.search(query, tags)
                all_results.extend(results)
            # TODO: 添加对其他记忆类型的搜索支持
        
        return all_results[:max_results]
    
    async def consolidate_memories(self) -> Dict[str, Any]:
        """执行记忆整合"""
        return await self.consolidator.consolidate(
            self.working_memory,
            self.episodic_memory,
            self.semantic_memory,
            self.procedural_memory
        )
    
    async def apply_forgetting(self) -> Dict[str, Any]:
        """应用遗忘机制"""
        return await self.forgetting_mechanism.apply_forgetting(self)
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "working_memory": {
                "active_items": len(await self.working_memory.get_active_items()),
                "capacity": self.working_memory.capacity
            },
            "episodic_memory": {
                "total_episodes": len(self.episodic_memory.episodes)
            },
            "semantic_memory": {
                "total_concepts": len(self.semantic_memory.concepts)
            },
            "procedural_memory": {
                "total_procedures": len(self.procedural_memory.procedures)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # 增强的记忆管理功能
    
    async def create_memory_snapshot(self, name: str = None) -> str:
        """创建记忆快照"""
        snapshot_id = name or f"memory_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not hasattr(self, '_snapshots'):
            self._snapshots = {}
        
        # 收集所有记忆系统的状态
        snapshot_data = {
            "working_memory": {
                "items": await self.working_memory.get_all_items(),
                "capacity": self.working_memory.capacity,
                "decay_rate": self.working_memory.decay_rate
            },
            "episodic_memory": {
                "episodes": [episode.to_dict() for episode in self.episodic_memory.episodes],
                "max_episodes": self.episodic_memory.max_episodes
            },
            "semantic_memory": {
                "concepts": {k: v.to_dict() for k, v in self.semantic_memory.concepts.items()},
                "relationships": [rel.to_dict() for rel in self.semantic_memory.relationships]
            },
            "procedural_memory": {
                "procedures": {k: v.to_dict() for k, v in self.procedural_memory.procedures.items()}
            },
            "timestamp": datetime.now(),
            "metadata": {
                "total_memories": await self.get_total_memory_count(),
                "memory_usage": await self.get_memory_usage_estimate()
            }
        }
        
        self._snapshots[snapshot_id] = snapshot_data
        return snapshot_id
    
    async def restore_memory_snapshot(self, snapshot_id: str) -> bool:
        """恢复记忆快照"""
        if not hasattr(self, '_snapshots') or snapshot_id not in self._snapshots:
            return False
        
        try:
            snapshot_data = self._snapshots[snapshot_id]
            
            # 恢复工作记忆
            await self.working_memory.clear()
            for item_data in snapshot_data["working_memory"]["items"]:
                await self.working_memory.add_item(
                    item_data["content"],
                    item_data.get("importance", 1.0)
                )
            
            # 恢复情景记忆
            self.episodic_memory.episodes.clear()
            for episode_data in snapshot_data["episodic_memory"]["episodes"]:
                episode = Episode.from_dict(episode_data)
                self.episodic_memory.episodes.append(episode)
            
            # 恢复语义记忆
            self.semantic_memory.concepts.clear()
            self.semantic_memory.relationships.clear()
            
            for concept_id, concept_data in snapshot_data["semantic_memory"]["concepts"].items():
                concept = Concept.from_dict(concept_data)
                self.semantic_memory.concepts[concept_id] = concept
            
            for rel_data in snapshot_data["semantic_memory"]["relationships"]:
                relationship = Relationship.from_dict(rel_data)
                self.semantic_memory.relationships.append(relationship)
            
            # 恢复程序记忆
            self.procedural_memory.procedures.clear()
            for proc_id, proc_data in snapshot_data["procedural_memory"]["procedures"].items():
                procedure = Procedure.from_dict(proc_data)
                self.procedural_memory.procedures[proc_id] = procedure
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore memory snapshot {snapshot_id}: {e}")
            return False
    
    def list_memory_snapshots(self) -> List[Dict[str, Any]]:
        """列出所有记忆快照"""
        if not hasattr(self, '_snapshots'):
            return []
        
        return [
            {
                "id": snapshot_id,
                "timestamp": snapshot["timestamp"].isoformat(),
                "total_memories": snapshot["metadata"]["total_memories"],
                "memory_usage": snapshot["metadata"]["memory_usage"]
            }
            for snapshot_id, snapshot in self._snapshots.items()
        ]
    
    async def optimize_memory(self) -> Dict[str, Any]:
        """优化记忆系统"""
        optimization_results = {
            "working_memory": {},
            "episodic_memory": {},
            "semantic_memory": {},
            "procedural_memory": {}
        }
        
        # 优化工作记忆
        initial_wm_items = len(await self.working_memory.get_active_items())
        await self.working_memory.decay_memories()
        final_wm_items = len(await self.working_memory.get_active_items())
        
        optimization_results["working_memory"] = {
            "items_before": initial_wm_items,
            "items_after": final_wm_items,
            "items_removed": initial_wm_items - final_wm_items
        }
        
        # 优化情景记忆 - 合并相似的情景
        initial_episodes = len(self.episodic_memory.episodes)
        merged_count = await self._merge_similar_episodes()
        final_episodes = len(self.episodic_memory.episodes)
        
        optimization_results["episodic_memory"] = {
            "episodes_before": initial_episodes,
            "episodes_after": final_episodes,
            "episodes_merged": merged_count
        }
        
        # 优化语义记忆 - 清理弱关系
        initial_relationships = len(self.semantic_memory.relationships)
        removed_weak_rels = await self._remove_weak_relationships()
        final_relationships = len(self.semantic_memory.relationships)
        
        optimization_results["semantic_memory"] = {
            "relationships_before": initial_relationships,
            "relationships_after": final_relationships,
            "weak_relationships_removed": removed_weak_rels
        }
        
        # 优化程序记忆 - 清理未使用的程序
        initial_procedures = len(self.procedural_memory.procedures)
        removed_unused = await self._remove_unused_procedures()
        final_procedures = len(self.procedural_memory.procedures)
        
        optimization_results["procedural_memory"] = {
            "procedures_before": initial_procedures,
            "procedures_after": final_procedures,
            "unused_procedures_removed": removed_unused
        }
        
        return optimization_results
    
    async def _merge_similar_episodes(self) -> int:
        """合并相似的情景"""
        merged_count = 0
        episodes_to_remove = []
        
        for i, episode1 in enumerate(self.episodic_memory.episodes):
            for j, episode2 in enumerate(self.episodic_memory.episodes[i+1:], i+1):
                # 计算相似度
                similarity = self._calculate_episode_similarity(episode1, episode2)
                
                # 如果相似度很高且时间接近，考虑合并
                if similarity > 0.8:
                    time_diff = abs((episode1.timestamp - episode2.timestamp).total_seconds())
                    if time_diff < 3600:  # 1小时内
                        # 合并情景
                        merged_episode = self._merge_episodes(episode1, episode2)
                        self.episodic_memory.episodes[i] = merged_episode
                        episodes_to_remove.append(j)
                        merged_count += 1
        
        # 移除被合并的情景
        for idx in sorted(episodes_to_remove, reverse=True):
            del self.episodic_memory.episodes[idx]
        
        return merged_count
    
    def _calculate_episode_similarity(self, episode1: 'Episode', episode2: 'Episode') -> float:
        """计算两个情景的相似度"""
        # 简单的相似度计算：基于内容的词汇重叠
        words1 = set(episode1.content.lower().split())
        words2 = set(episode2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_episodes(self, episode1: 'Episode', episode2: 'Episode') -> 'Episode':
        """合并两个情景"""
        # 创建新的合并情景
        merged_content = f"{episode1.content} | {episode2.content}"
        merged_context = episode1.context.copy()
        merged_context.update(episode2.context)
        
        # 合并参与者
        merged_participants = list(set(episode1.participants + episode2.participants))
        
        # 使用较早的时间戳
        earlier_time = min(episode1.timestamp, episode2.timestamp)
        
        return Episode(
            content=merged_content,
            context=merged_context,
            participants=merged_participants,
            timestamp=earlier_time,
            importance=(episode1.importance + episode2.importance) / 2
        )
    
    async def _remove_weak_relationships(self, threshold: float = 0.3) -> int:
        """移除弱关系"""
        initial_count = len(self.semantic_memory.relationships)
        
        self.semantic_memory.relationships = [
            rel for rel in self.semantic_memory.relationships 
            if rel.strength >= threshold
        ]
        
        return initial_count - len(self.semantic_memory.relationships)
    
    async def _remove_unused_procedures(self, min_usage: int = 1) -> int:
        """移除未使用的程序"""
        initial_count = len(self.procedural_memory.procedures)
        
        procedures_to_remove = []
        for proc_id, procedure in self.procedural_memory.procedures.items():
            if procedure.usage_count < min_usage:
                procedures_to_remove.append(proc_id)
        
        for proc_id in procedures_to_remove:
            del self.procedural_memory.procedures[proc_id]
        
        return len(procedures_to_remove)
    
    async def get_total_memory_count(self) -> int:
        """获取总记忆数量"""
        wm_count = len(await self.working_memory.get_active_items())
        em_count = len(self.episodic_memory.episodes)
        sm_count = len(self.semantic_memory.concepts)
        pm_count = len(self.procedural_memory.procedures)
        
        return wm_count + em_count + sm_count + pm_count
    
    async def get_memory_usage_estimate(self) -> Dict[str, int]:
        """估算记忆使用量"""
        import sys
        
        # 估算各记忆系统的内存使用
        wm_size = sys.getsizeof(await self.working_memory.get_all_items())
        em_size = sum(sys.getsizeof(ep.to_dict()) for ep in self.episodic_memory.episodes)
        sm_size = sum(sys.getsizeof(concept.to_dict()) for concept in self.semantic_memory.concepts.values())
        pm_size = sum(sys.getsizeof(proc.to_dict()) for proc in self.procedural_memory.procedures.values())
        
        return {
            "working_memory_bytes": wm_size,
            "episodic_memory_bytes": em_size,
            "semantic_memory_bytes": sm_size,
            "procedural_memory_bytes": pm_size,
            "total_bytes": wm_size + em_size + sm_size + pm_size
        }
    
    async def export_memory_data(self, format: str = "json") -> Union[str, bytes]:
        """导出记忆数据"""
        memory_data = {
            "working_memory": {
                "items": await self.working_memory.get_all_items(),
                "capacity": self.working_memory.capacity
            },
            "episodic_memory": {
                "episodes": [episode.to_dict() for episode in self.episodic_memory.episodes]
            },
            "semantic_memory": {
                "concepts": {k: v.to_dict() for k, v in self.semantic_memory.concepts.items()},
                "relationships": [rel.to_dict() for rel in self.semantic_memory.relationships]
            },
            "procedural_memory": {
                "procedures": {k: v.to_dict() for k, v in self.procedural_memory.procedures.items()}
            },
            "export_timestamp": datetime.now().isoformat(),
            "export_format": format
        }
        
        if format.lower() == "json":
            return json.dumps(memory_data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_memory_data(self, data: str, format: str = "json", merge: bool = True) -> bool:
        """导入记忆数据"""
        try:
            if format.lower() == "json":
                memory_data = json.loads(data)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            if not merge:
                # 清空现有记忆
                await self.working_memory.clear()
                self.episodic_memory.episodes.clear()
                self.semantic_memory.concepts.clear()
                self.semantic_memory.relationships.clear()
                self.procedural_memory.procedures.clear()
            
            # 导入工作记忆
            if "working_memory" in memory_data:
                for item_data in memory_data["working_memory"]["items"]:
                    await self.working_memory.add_item(
                        item_data["content"],
                        item_data.get("importance", 1.0)
                    )
            
            # 导入情景记忆
            if "episodic_memory" in memory_data:
                for episode_data in memory_data["episodic_memory"]["episodes"]:
                    episode = Episode.from_dict(episode_data)
                    self.episodic_memory.episodes.append(episode)
            
            # 导入语义记忆
            if "semantic_memory" in memory_data:
                for concept_id, concept_data in memory_data["semantic_memory"]["concepts"].items():
                    concept = Concept.from_dict(concept_data)
                    self.semantic_memory.concepts[concept_id] = concept
                
                for rel_data in memory_data["semantic_memory"]["relationships"]:
                    relationship = Relationship.from_dict(rel_data)
                    self.semantic_memory.relationships.append(relationship)
            
            # 导入程序记忆
            if "procedural_memory" in memory_data:
                for proc_id, proc_data in memory_data["procedural_memory"]["procedures"].items():
                    procedure = Procedure.from_dict(proc_data)
                    self.procedural_memory.procedures[proc_id] = procedure
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to import memory data: {e}")
            return False 

    async def create_cross_memory_associations(self) -> Dict[str, Any]:
        """创建跨记忆类型的关联"""
        association_report = {
            "associations_created": 0,
            "working_to_episodic": 0,
            "working_to_semantic": 0,
            "semantic_clusters": 0,
            "knowledge_transfers": []
        }
        
        try:
            # 获取工作记忆中的高价值项目
            high_value_items = []
            for item in self.working_memory.items.values():
                if item.importance > 0.7 or item.access_count > 3:
                    high_value_items.append(item)
            
            # 创建关联
            for item in high_value_items:
                # 基于内容类型决定关联目标
                content_str = str(item.content).lower()
                
                if any(keyword in content_str for keyword in ['事件', '发生', '经历', '过程']):
                    # 转移到情景记忆
                    episodic_data = {
                        "event": str(item.content),
                        "context": item.metadata,
                        "participants": ["user", "system"],
                        "importance": item.importance,
                        "metadata": {"source": "working_memory", "original_id": item.item_id}
                    }
                    await self.episodic_memory.store(episodic_data)
                    association_report["working_to_episodic"] += 1
                    association_report["knowledge_transfers"].append({
                        "from": "working",
                        "to": "episodic",
                        "item_id": item.item_id,
                        "content": str(item.content)[:50] + "..."
                    })
                
                elif any(keyword in content_str for keyword in ['概念', '定义', '知识', '原理']):
                    # 转移到语义记忆
                    semantic_data = {
                        "concept": str(item.content),
                        "definition": f"从工作记忆转移的概念: {item.content}",
                        "properties": {"importance": item.importance},
                        "metadata": {"source": "working_memory", "original_id": item.item_id}
                    }
                    await self.semantic_memory.store(semantic_data)
                    association_report["working_to_semantic"] += 1
                    association_report["knowledge_transfers"].append({
                        "from": "working",
                        "to": "semantic", 
                        "item_id": item.item_id,
                        "content": str(item.content)[:50] + "..."
                    })
            
            association_report["associations_created"] = len(association_report["knowledge_transfers"])
            
        except Exception as e:
            self.logger.error(f"跨记忆关联创建失败: {e}")
            association_report["error"] = str(e)
        
        return association_report
    
    async def find_related_memories(self, query: str, cross_memory: bool = True) -> Dict[str, List[Any]]:
        """跨记忆类型查找相关记忆"""
        related_memories = {
            "working": [],
            "episodic": [],
            "semantic": [],
            "procedural": [],
            "cross_associations": []
        }
        
        if not cross_memory:
            return await self.retrieve_memory(query)
        
        try:
            # 在工作记忆中搜索
            if hasattr(self.working_memory, 'semantic_search'):
                working_results = await self.working_memory.semantic_search(query, top_k=3)
                related_memories["working"] = working_results
            
            # 查找跨记忆关联
            for working_item in related_memories["working"]:
                # 检查是否有关联的长期记忆
                if "cross_references" in working_item.metadata:
                    related_memories["cross_associations"].extend(
                        working_item.metadata["cross_references"]
                    )
        
        except Exception as e:
            self.logger.error(f"跨记忆搜索失败: {e}")
        
        return related_memories


class MetaMemorySystem:
    """元记忆系统 - 管理记忆系统本身，实现记忆的自我优化"""
    
    def __init__(self, memory_system: 'MemorySystem', config: Optional[Dict[str, Any]] = None):
        self.memory_system = memory_system
        self.config = config or {}
        
        # 记忆质量评估器
        self.quality_assessor = MemoryQualityAssessor(self.config.get("quality", {}))
        
        # 检索优化器
        self.retrieval_optimizer = RetrievalOptimizer(self.config.get("retrieval", {}))
        
        # 策略学习器
        self.strategy_learner = MemoryStrategyLearner(self.config.get("learning", {}))
        
        # 性能监控器
        self.performance_monitor = MemoryPerformanceMonitor(self.config.get("monitoring", {}))
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def optimize_memory_system(self) -> Dict[str, Any]:
        """优化整个记忆系统"""
        optimization_report = {
            "timestamp": datetime.now().isoformat(),
            "quality_assessment": {},
            "retrieval_optimization": {},
            "strategy_updates": {},
            "performance_improvements": {}
        }
        
        try:
            # 1. 评估记忆质量
            quality_report = await self.assess_memory_quality()
            optimization_report["quality_assessment"] = quality_report
            
            # 2. 优化检索策略
            retrieval_report = await self.optimize_retrieval_strategies()
            optimization_report["retrieval_optimization"] = retrieval_report
            
            # 3. 学习和更新策略
            learning_report = await self.learn_and_update_strategies()
            optimization_report["strategy_updates"] = learning_report
            
            # 4. 监控性能改进
            performance_report = await self.monitor_performance_improvements()
            optimization_report["performance_improvements"] = performance_report
            
            self.logger.info("记忆系统优化完成")
            return optimization_report
            
        except Exception as e:
            self.logger.error(f"记忆系统优化失败: {e}")
            optimization_report["error"] = str(e)
            return optimization_report
    
    async def assess_memory_quality(self) -> Dict[str, Any]:
        """评估记忆质量"""
        return await self.quality_assessor.assess_system_quality(self.memory_system)
    
    async def optimize_retrieval_strategies(self) -> Dict[str, Any]:
        """优化检索策略"""
        return await self.retrieval_optimizer.optimize_retrieval(self.memory_system)
    
    async def learn_and_update_strategies(self) -> Dict[str, Any]:
        """学习和更新策略"""
        return await self.strategy_learner.learn_from_usage(self.memory_system)
    
    async def monitor_performance_improvements(self) -> Dict[str, Any]:
        """监控性能改进"""
        return await self.performance_monitor.monitor_improvements(self.memory_system)


class MemoryQualityAssessor:
    """记忆质量评估器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.quality_thresholds = {
            "relevance": self.config.get("relevance_threshold", 0.6),
            "accuracy": self.config.get("accuracy_threshold", 0.8),
            "completeness": self.config.get("completeness_threshold", 0.7),
            "consistency": self.config.get("consistency_threshold", 0.75)
        }
    
    async def assess_system_quality(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """评估整个记忆系统的质量"""
        quality_report = {
            "overall_score": 0.0,
            "component_scores": {},
            "quality_issues": [],
            "improvement_suggestions": []
        }
        
        # 评估工作记忆质量
        working_quality = await self.assess_working_memory_quality(memory_system.working_memory)
        quality_report["component_scores"]["working_memory"] = working_quality
        
        # 评估其他记忆组件质量
        # 这里可以扩展评估其他记忆类型
        
        # 计算总体质量分数
        total_score = working_quality["overall_score"]
        quality_report["overall_score"] = total_score
        
        # 生成改进建议
        if total_score < 0.7:
            quality_report["improvement_suggestions"].extend([
                "考虑调整记忆整合阈值",
                "优化语义嵌入质量",
                "增加记忆访问频率跟踪"
            ])
        
        return quality_report
    
    async def assess_working_memory_quality(self, working_memory: WorkingMemory) -> Dict[str, Any]:
        """评估工作记忆质量"""
        quality_metrics = {
            "overall_score": 0.0,
            "relevance_score": 0.0,
            "diversity_score": 0.0,
            "freshness_score": 0.0,
            "semantic_coherence": 0.0,
            "capacity_utilization": 0.0
        }
        
        if not working_memory.items:
            return quality_metrics
        
        items = list(working_memory.items.values())
        current_time = datetime.now()
        
        # 1. 相关性评分
        relevance_scores = []
        for item in items:
            # 基于重要性和访问频率计算相关性
            relevance = (item.importance * 0.6) + (min(item.access_count / 10.0, 0.4))
            relevance_scores.append(relevance)
        
        quality_metrics["relevance_score"] = sum(relevance_scores) / len(relevance_scores)
        
        # 2. 多样性评分（基于语义关键词的多样性）
        all_keywords = set()
        for item in items:
            keywords = getattr(item, 'semantic_keywords', [])
            all_keywords.update(keywords)
        
        diversity = len(all_keywords) / max(len(items) * 3, 1)  # 期望每个项目3个关键词
        quality_metrics["diversity_score"] = min(diversity, 1.0)
        
        # 3. 新鲜度评分
        freshness_scores = []
        for item in items:
            hours_since_access = (current_time - item.last_accessed).total_seconds() / 3600
            freshness = max(0, 1 - (hours_since_access / 24))  # 24小时内为新鲜
            freshness_scores.append(freshness)
        
        quality_metrics["freshness_score"] = sum(freshness_scores) / len(freshness_scores)
        
        # 4. 语义连贯性（如果有语义嵌入）
        if hasattr(working_memory, 'semantic_search_enabled') and working_memory.semantic_search_enabled:
            coherence_score = await self._calculate_semantic_coherence(items)
            quality_metrics["semantic_coherence"] = coherence_score
        
        # 5. 容量利用率
        capacity_utilization = len(items) / working_memory.capacity
        quality_metrics["capacity_utilization"] = capacity_utilization
        
        # 计算总体分数
        overall_score = (
            quality_metrics["relevance_score"] * 0.3 +
            quality_metrics["diversity_score"] * 0.2 +
            quality_metrics["freshness_score"] * 0.2 +
            quality_metrics["semantic_coherence"] * 0.2 +
            quality_metrics["capacity_utilization"] * 0.1
        )
        
        quality_metrics["overall_score"] = overall_score
        return quality_metrics
    
    async def _calculate_semantic_coherence(self, items: List[MemoryItem]) -> float:
        """计算语义连贯性"""
        try:
            embeddings = []
            for item in items:
                if hasattr(item, 'embedding') and item.embedding is not None:
                    embeddings.append(item.embedding)
            
            if len(embeddings) < 2:
                return 1.0
            
            # 计算所有嵌入之间的平均相似性
            total_similarity = 0.0
            pair_count = 0
            
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    similarity = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                    if not np.isnan(similarity):
                        total_similarity += similarity
                        pair_count += 1
            
            return total_similarity / pair_count if pair_count > 0 else 0.0
            
        except Exception:
            return 0.5  # 默认中等连贯性


class RetrievalOptimizer:
    """检索优化器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.retrieval_history = []
        self.optimization_strategies = ["semantic_weight", "threshold_adjustment", "result_ranking"]
    
    async def optimize_retrieval(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """优化检索策略"""
        optimization_report = {
            "optimizations_applied": [],
            "performance_improvements": {},
            "new_parameters": {}
        }
        
        # 分析当前检索性能
        current_performance = await self._analyze_current_performance(memory_system)
        
        # 应用优化策略
        if current_performance["semantic_search_effectiveness"] < 0.5:
            # 调整语义搜索权重
            new_weight = min(0.8, current_performance.get("optimal_semantic_weight", 0.7) + 0.1)
            optimization_report["new_parameters"]["semantic_weight"] = new_weight
            optimization_report["optimizations_applied"].append("increased_semantic_weight")
        
        if current_performance["result_relevance"] < 0.6:
            # 调整相似性阈值
            new_threshold = max(0.1, current_performance.get("optimal_threshold", 0.3) - 0.05)
            optimization_report["new_parameters"]["similarity_threshold"] = new_threshold
            optimization_report["optimizations_applied"].append("lowered_similarity_threshold")
        
        return optimization_report
    
    async def _analyze_current_performance(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """分析当前检索性能"""
        # 模拟性能分析
        return {
            "semantic_search_effectiveness": 0.6,
            "result_relevance": 0.7,
            "optimal_semantic_weight": 0.65,
            "optimal_threshold": 0.25
        }


class MemoryStrategyLearner:
    """记忆策略学习器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.usage_patterns = {}
        self.learned_strategies = {}
    
    async def learn_from_usage(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """从使用模式中学习"""
        learning_report = {
            "patterns_identified": [],
            "strategies_updated": [],
            "recommendations": []
        }
        
        # 分析使用模式
        usage_patterns = await self._analyze_usage_patterns(memory_system)
        
        # 识别优化机会
        if usage_patterns.get("high_access_items_ratio", 0) > 0.7:
            learning_report["recommendations"].append("increase_working_memory_capacity")
        
        if usage_patterns.get("semantic_search_usage", 0) < 0.3:
            learning_report["recommendations"].append("promote_semantic_search_usage")
        
        return learning_report
    
    async def _analyze_usage_patterns(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """分析使用模式"""
        patterns = {
            "total_items": memory_system.working_memory.current_size,
            "high_access_items_ratio": 0.6,
            "semantic_search_usage": 0.4,
            "average_item_age_hours": 2.5
        }
        return patterns


class MemoryPerformanceMonitor:
    """记忆性能监控器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.performance_history = []
    
    async def monitor_improvements(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """监控性能改进"""
        current_metrics = await self._collect_current_metrics(memory_system)
        
        performance_report = {
            "current_metrics": current_metrics,
            "trends": {},
            "alerts": []
        }
        
        # 检查性能警报
        if current_metrics.get("memory_utilization", 0) > 0.9:
            performance_report["alerts"].append("high_memory_utilization")
        
        if current_metrics.get("retrieval_latency", 0) > 100:  # ms
            performance_report["alerts"].append("high_retrieval_latency")
        
        return performance_report
    
    async def _collect_current_metrics(self, memory_system: 'MemorySystem') -> Dict[str, Any]:
        """收集当前性能指标"""
        return {
            "memory_utilization": memory_system.working_memory.current_size / memory_system.working_memory.capacity,
            "retrieval_latency": 50,  # 模拟延迟（毫秒）
            "consolidation_rate": 0.3,
            "quality_score": 0.75
        }