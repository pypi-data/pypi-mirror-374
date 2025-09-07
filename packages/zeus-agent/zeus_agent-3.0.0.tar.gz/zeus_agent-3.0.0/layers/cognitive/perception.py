"""
Perception Module
感知模块 - 实现多模态感知能力

该模块负责处理和分析各种输入数据，包括文本、图像、音频等，
将原始数据转换为结构化的感知信息。
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class PerceptionType(Enum):
    """感知类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"
    STRUCTURED_DATA = "structured_data"


class SentimentType(Enum):
    """情感类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class PerceptionResult:
    """感知结果"""
    perception_type: PerceptionType
    content: Any
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "perception_type": self.perception_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TextPerceptionResult(PerceptionResult):
    """文本感知结果"""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: SentimentType = SentimentType.NEUTRAL
    sentiment_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    language: str = "unknown"
    
    def __post_init__(self):
        self.perception_type = PerceptionType.TEXT


class BasePerceptor(ABC):
    """基础感知器抽象类"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.config = {}
    
    @abstractmethod
    async def perceive(self, data: Any) -> PerceptionResult:
        """感知方法"""
        pass
    
    @abstractmethod
    def can_handle(self, data: Any) -> bool:
        """检查是否可以处理给定数据"""
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置感知器"""
        self.config.update(config)


class TextPerceptor(BasePerceptor):
    """文本感知器"""
    
    def __init__(self):
        super().__init__("TextPerceptor")
        self.emotion_keywords = {
            SentimentType.POSITIVE: [
                "good", "great", "excellent", "amazing", "wonderful", "fantastic",
                "love", "like", "enjoy", "happy", "pleased", "satisfied",
                "好", "棒", "优秀", "很棒", "喜欢", "满意", "开心"
            ],
            SentimentType.NEGATIVE: [
                "bad", "terrible", "awful", "horrible", "hate", "dislike",
                "angry", "frustrated", "disappointed", "sad", "upset",
                "糟糕", "不好", "讨厌", "失望", "生气", "难过"
            ]
        }
    
    def can_handle(self, data: Any) -> bool:
        """检查是否可以处理文本数据"""
        return isinstance(data, str) and len(data.strip()) > 0
    
    async def perceive(self, data: str) -> TextPerceptionResult:
        """感知文本内容"""
        if not self.can_handle(data):
            raise ValueError("TextPerceptor can only handle non-empty strings")
        
        result = TextPerceptionResult(
            perception_type=PerceptionType.TEXT,
            content=data,
            confidence=0.8
        )
        
        # 实体识别（简单的基于规则的方法）
        result.entities = self._extract_entities(data)
        
        # 情感分析
        result.sentiment, result.sentiment_score = self._analyze_sentiment(data)
        
        # 关键词提取
        result.keywords = self._extract_keywords(data)
        
        # 主题识别
        result.topics = self._identify_topics(data)
        
        # 语言检测（简单的启发式方法）
        result.language = self._detect_language(data)
        
        # 元数据
        result.metadata = {
            "length": len(data),
            "word_count": len(data.split()),
            "sentence_count": len([s for s in data.split('.') if s.strip()]),
            "has_question": '?' in data,
            "has_exclamation": '!' in data,
            "complexity_score": self._calculate_complexity(data)
        }
        
        return result
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """提取实体（简单的基于正则表达式的方法）"""
        entities = []
        
        # 邮箱地址
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                "type": "email",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
        
        # URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        for match in re.finditer(url_pattern, text):
            entities.append({
                "type": "url",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
        
        # 数字
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        for match in re.finditer(number_pattern, text):
            entities.append({
                "type": "number",
                "value": float(match.group()) if '.' in match.group() else int(match.group()),
                "start": match.start(),
                "end": match.end()
            })
        
        # 日期（简单格式）
        date_pattern = r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b'
        for match in re.finditer(date_pattern, text):
            entities.append({
                "type": "date",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> Tuple[SentimentType, float]:
        """分析情感（基于关键词的简单方法）"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.emotion_keywords[SentimentType.POSITIVE] 
                           if word in text_lower)
        negative_count = sum(1 for word in self.emotion_keywords[SentimentType.NEGATIVE] 
                           if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            score = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        elif positive_count > 0 and negative_count > 0:
            sentiment = SentimentType.MIXED
            score = 0.6
        else:
            sentiment = SentimentType.NEUTRAL
            score = 0.5
        
        return sentiment, score
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：去除停用词后的高频词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            '的', '了', '在', '是', '我', '你', '他', '她', '它', '们', '这', '那'
        }
        
        # 分词并过滤
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 计算词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回高频词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:max_keywords]]
    
    def _identify_topics(self, text: str) -> List[str]:
        """识别主题"""
        topics = []
        text_lower = text.lower()
        
        # 基于关键词的主题识别
        topic_keywords = {
            "technology": ["ai", "artificial intelligence", "machine learning", "computer", "software", "algorithm"],
            "business": ["company", "market", "sales", "revenue", "profit", "customer", "strategy"],
            "science": ["research", "study", "experiment", "data", "analysis", "hypothesis"],
            "education": ["learn", "teach", "student", "school", "university", "knowledge"],
            "health": ["medical", "health", "doctor", "patient", "treatment", "medicine"],
            "sports": ["game", "team", "player", "score", "match", "competition"],
            "entertainment": ["movie", "music", "show", "actor", "singer", "entertainment"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _detect_language(self, text: str) -> str:
        """检测语言（简单的启发式方法）"""
        # 检查中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        
        if chinese_chars / total_chars > 0.3:
            return "zh"
        else:
            return "en"
    
    def _calculate_complexity(self, text: str) -> float:
        """计算文本复杂度"""
        words = text.split()
        if not words:
            return 0.0
        
        # 平均词长
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # 句子长度
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # 复杂度分数（0-1）
        complexity = min(1.0, (avg_word_length / 10 + avg_sentence_length / 20) / 2)
        return complexity


class StructuredDataPerceptor(BasePerceptor):
    """结构化数据感知器"""
    
    def __init__(self):
        super().__init__("StructuredDataPerceptor")
    
    def can_handle(self, data: Any) -> bool:
        """检查是否可以处理结构化数据"""
        return isinstance(data, (dict, list))
    
    async def perceive(self, data: Union[Dict, List]) -> PerceptionResult:
        """感知结构化数据"""
        if not self.can_handle(data):
            raise ValueError("StructuredDataPerceptor can only handle dict or list data")
        
        result = PerceptionResult(
            perception_type=PerceptionType.STRUCTURED_DATA,
            content=data,
            confidence=0.9
        )
        
        # 分析数据结构
        if isinstance(data, dict):
            result.metadata = {
                "type": "dictionary",
                "keys": list(data.keys()),
                "key_count": len(data),
                "nested_depth": self._calculate_depth(data),
                "data_types": self._analyze_data_types(data)
            }
        elif isinstance(data, list):
            result.metadata = {
                "type": "list",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data)),
                "nested_depth": self._calculate_depth(data)
            }
        
        return result
    
    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """计算数据结构的嵌套深度"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_depth(value, current_depth + 1) for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth
    
    def _analyze_data_types(self, data: Dict) -> Dict[str, str]:
        """分析字典中各键的数据类型"""
        return {key: type(value).__name__ for key, value in data.items()}


class PerceptionEngine:
    """感知引擎 - 管理多个感知器"""
    
    def __init__(self):
        self.perceptors: Dict[str, BasePerceptor] = {}
        self.perception_history: List[PerceptionResult] = []
        self.max_history = 1000
        
        # 注册默认感知器
        self.register_perceptor(TextPerceptor())
        self.register_perceptor(StructuredDataPerceptor())
    
    async def initialize(self) -> None:
        """初始化感知引擎"""
        # 初始化所有感知器
        for perceptor in self.perceptors.values():
            if hasattr(perceptor, 'initialize'):
                await perceptor.initialize()
    
    async def cleanup(self) -> None:
        """清理感知引擎"""
        # 清理所有感知器
        for perceptor in self.perceptors.values():
            if hasattr(perceptor, 'cleanup'):
                await perceptor.cleanup()
    
    def register_perceptor(self, perceptor: BasePerceptor) -> None:
        """注册感知器"""
        self.perceptors[perceptor.name] = perceptor
    
    def unregister_perceptor(self, name: str) -> bool:
        """注销感知器"""
        if name in self.perceptors:
            del self.perceptors[name]
            return True
        return False
    
    def get_perceptor(self, name: str) -> Optional[BasePerceptor]:
        """获取感知器"""
        return self.perceptors.get(name)
    
    def list_perceptors(self) -> List[str]:
        """列出所有感知器"""
        return list(self.perceptors.keys())
    
    async def perceive(self, data: Any, preferred_perceptor: str = None) -> PerceptionResult:
        """执行感知"""
        # 如果指定了首选感知器
        if preferred_perceptor and preferred_perceptor in self.perceptors:
            perceptor = self.perceptors[preferred_perceptor]
            if perceptor.can_handle(data) and perceptor.enabled:
                result = await perceptor.perceive(data)
                self._add_to_history(result)
                return result
        
        # 自动选择合适的感知器
        for perceptor in self.perceptors.values():
            if perceptor.can_handle(data) and perceptor.enabled:
                result = await perceptor.perceive(data)
                self._add_to_history(result)
                return result
        
        # 如果没有合适的感知器，返回基础感知结果
        result = PerceptionResult(
            perception_type=PerceptionType.TEXT,  # 默认类型
            content=str(data),
            confidence=0.1,
            metadata={"fallback": True, "original_type": type(data).__name__}
        )
        self._add_to_history(result)
        return result
    
    def _add_to_history(self, result: PerceptionResult) -> None:
        """添加到感知历史"""
        self.perception_history.append(result)
        
        # 限制历史记录大小
        if len(self.perception_history) > self.max_history:
            self.perception_history = self.perception_history[-self.max_history:]
    
    def get_recent_perceptions(self, count: int = 10) -> List[PerceptionResult]:
        """获取最近的感知结果"""
        return self.perception_history[-count:]
    
    def get_perception_stats(self) -> Dict[str, Any]:
        """获取感知统计信息"""
        if not self.perception_history:
            return {"total": 0}
        
        # 统计各类型感知的数量
        type_counts = {}
        confidence_scores = []
        
        for result in self.perception_history:
            perception_type = result.perception_type.value
            type_counts[perception_type] = type_counts.get(perception_type, 0) + 1
            confidence_scores.append(result.confidence)
        
        return {
            "total": len(self.perception_history),
            "type_distribution": type_counts,
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "perceptors_count": len(self.perceptors),
            "enabled_perceptors": sum(1 for p in self.perceptors.values() if p.enabled)
        }
    
    def clear_history(self) -> None:
        """清空感知历史"""
        self.perception_history.clear()
    
    async def batch_perceive(self, data_list: List[Any]) -> List[PerceptionResult]:
        """批量感知"""
        results = []
        for data in data_list:
            try:
                result = await self.perceive(data)
                results.append(result)
            except Exception as e:
                # 创建错误结果
                error_result = PerceptionResult(
                    perception_type=PerceptionType.TEXT,
                    content=f"Error: {str(e)}",
                    confidence=0.0,
                    metadata={"error": True, "original_data": str(data)}
                )
                results.append(error_result)
        
        return results 