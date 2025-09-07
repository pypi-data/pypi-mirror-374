"""
Embedding服务
集成sentence-transformers，提供文本向量化能力
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import pickle
import os
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Embedding配置"""
    model_name: str = "all-MiniLM-L6-v2"  # 默认轻量级模型
    cache_dir: str = "./data/embeddings_cache"
    max_sequence_length: int = 512
    batch_size: int = 32
    device: str = "auto"  # auto, cpu, cuda
    normalize_embeddings: bool = True


@dataclass
class EmbeddingResult:
    """Embedding结果"""
    text: str
    embedding: List[float]
    model_name: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmbeddingService:
    """
    Embedding服务
    
    提供文本向量化功能，支持多种模型和缓存机制
    """
    
    # 支持的模型配置
    SUPPORTED_MODELS = {
        # 通用英文模型
        "all-MiniLM-L6-v2": {
            "description": "轻量级通用模型，384维",
            "dimensions": 384,
            "max_seq_length": 256,
            "language": "en",
            "size": "80MB"
        },
        "all-mpnet-base-v2": {
            "description": "高质量通用模型，768维",
            "dimensions": 768,
            "max_seq_length": 384,
            "language": "en", 
            "size": "420MB"
        },
        # 多语言模型
        "paraphrase-multilingual-MiniLM-L12-v2": {
            "description": "多语言轻量级模型，384维",
            "dimensions": 384,
            "max_seq_length": 128,
            "language": "multilingual",
            "size": "420MB"
        },
        "paraphrase-multilingual-mpnet-base-v2": {
            "description": "多语言高质量模型，768维", 
            "dimensions": 768,
            "max_seq_length": 256,
            "language": "multilingual",
            "size": "970MB"
        },
        # 中文优化模型
        "shibing624/text2vec-base-chinese": {
            "description": "中文优化模型，768维",
            "dimensions": 768,
            "max_seq_length": 256,
            "language": "zh",
            "size": "400MB"
        }
    }
    
    def __init__(self, config: EmbeddingConfig = None):
        """初始化Embedding服务"""
        self.config = config or EmbeddingConfig()
        
        # 确保缓存目录存在
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化模型
        self.model = None
        self.current_model_name = None
        
        # 缓存
        self._embedding_cache = {}
        self._cache_file = os.path.join(self.config.cache_dir, "embedding_cache.pkl")
        self._load_cache()
        
        # 统计信息
        self.stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_texts_processed": 0,
            "average_embedding_time": 0.0
        }
        
        # 不在构造函数中自动加载模型，等待显式初始化
    
    async def initialize(self, model_name: str = None) -> bool:
        """初始化嵌入服务，加载指定模型"""
        model_name = model_name or self.config.model_name
        return await self._load_model(model_name)
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """生成缓存键"""
        content = f"{model_name}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_cache(self):
        """加载缓存"""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'rb') as f:
                    self._embedding_cache = pickle.load(f)
                logger.info(f"✅ 已加载 {len(self._embedding_cache)} 个缓存embedding")
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
            self._embedding_cache = {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self._cache_file, 'wb') as f:
                pickle.dump(self._embedding_cache, f)
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    async def _load_model(self, model_name: str) -> bool:
        """加载模型"""
        try:
            if self.current_model_name == model_name and self.model is not None:
                return True
            
            logger.info(f"🔄 正在加载embedding模型: {model_name}")
            
            # 确定设备
            device = self.config.device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # 加载模型
            self.model = SentenceTransformer(
                model_name,
                device=device,
                cache_folder=os.path.join(self.config.cache_dir, "models")
            )
            
            # 设置最大序列长度
            if hasattr(self.model, 'max_seq_length'):
                self.model.max_seq_length = self.config.max_sequence_length
            
            self.current_model_name = model_name
            
            logger.info(f"✅ 模型加载成功: {model_name} (设备: {device})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            return False
    
    async def embed_text(self, 
                        text: str, 
                        model_name: str = None,
                        use_cache: bool = True) -> EmbeddingResult:
        """
        对单个文本进行向量化
        
        Args:
            text: 输入文本
            model_name: 模型名称，如果不指定则使用默认模型
            use_cache: 是否使用缓存
            
        Returns:
            Embedding结果
        """
        if not text.strip():
            raise ValueError("输入文本不能为空")
        
        model_name = model_name or self.config.model_name
        
        # 检查缓存
        cache_key = self._get_cache_key(text, model_name)
        if use_cache and cache_key in self._embedding_cache:
            self.stats["cache_hits"] += 1
            cached_result = self._embedding_cache[cache_key]
            logger.debug(f"🎯 缓存命中: {text[:50]}...")
            return EmbeddingResult(
                text=text,
                embedding=cached_result["embedding"],
                model_name=model_name,
                metadata={"from_cache": True}
            )
        
        # 确保模型已加载
        if not await self._load_model(model_name):
            raise RuntimeError(f"无法加载模型: {model_name}")
        
        try:
            start_time = datetime.now()
            
            # 生成embedding
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.config.normalize_embeddings,
                convert_to_tensor=False
            )
            
            # 转换为列表格式
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计信息
            self.stats["embeddings_generated"] += 1
            self.stats["cache_misses"] += 1
            self.stats["total_texts_processed"] += 1
            
            # 更新平均处理时间
            total_time = (self.stats["average_embedding_time"] * (self.stats["embeddings_generated"] - 1) + processing_time)
            self.stats["average_embedding_time"] = total_time / self.stats["embeddings_generated"]
            
            # 创建结果
            result = EmbeddingResult(
                text=text,
                embedding=embedding,
                model_name=model_name,
                metadata={
                    "processing_time": processing_time,
                    "dimensions": len(embedding),
                    "from_cache": False
                }
            )
            
            # 缓存结果
            if use_cache:
                self._embedding_cache[cache_key] = {
                    "embedding": embedding,
                    "created_at": datetime.now().isoformat()
                }
                
                # 定期保存缓存
                if len(self._embedding_cache) % 100 == 0:
                    self._save_cache()
            
            logger.debug(f"✅ Embedding生成完成: {text[:50]}... ({processing_time:.3f}s)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Embedding生成失败: {e}")
            raise
    
    async def embed_texts(self, 
                         texts: List[str], 
                         model_name: str = None,
                         use_cache: bool = True) -> List[EmbeddingResult]:
        """
        批量文本向量化
        
        Args:
            texts: 文本列表
            model_name: 模型名称
            use_cache: 是否使用缓存
            
        Returns:
            Embedding结果列表
        """
        if not texts:
            return []
        
        model_name = model_name or self.config.model_name
        results = []
        
        # 分离缓存命中和未命中的文本
        cached_results = {}
        texts_to_process = []
        
        if use_cache:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text, model_name)
                if cache_key in self._embedding_cache:
                    cached_results[i] = self._embedding_cache[cache_key]
                    self.stats["cache_hits"] += 1
                else:
                    texts_to_process.append((i, text))
                    self.stats["cache_misses"] += 1
        else:
            texts_to_process = list(enumerate(texts))
        
        # 处理未缓存的文本
        if texts_to_process:
            # 确保模型已加载
            if not await self._load_model(model_name):
                raise RuntimeError(f"无法加载模型: {model_name}")
            
            try:
                start_time = datetime.now()
                
                # 批量生成embedding
                batch_texts = [text for _, text in texts_to_process]
                embeddings = self.model.encode(
                    batch_texts,
                    batch_size=self.config.batch_size,
                    normalize_embeddings=self.config.normalize_embeddings,
                    convert_to_tensor=False,
                    show_progress_bar=len(batch_texts) > 10
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # 处理结果
                for (original_idx, text), embedding in zip(texts_to_process, embeddings):
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    
                    # 缓存结果
                    if use_cache:
                        cache_key = self._get_cache_key(text, model_name)
                        self._embedding_cache[cache_key] = {
                            "embedding": embedding,
                            "created_at": datetime.now().isoformat()
                        }
                    
                    # 存储到结果中
                    cached_results[original_idx] = {
                        "embedding": embedding,
                        "processing_time": processing_time / len(texts_to_process)
                    }
                
                # 更新统计信息
                self.stats["embeddings_generated"] += len(texts_to_process)
                self.stats["total_texts_processed"] += len(texts_to_process)
                
                logger.info(f"✅ 批量生成 {len(texts_to_process)} 个embedding ({processing_time:.3f}s)")
                
            except Exception as e:
                logger.error(f"❌ 批量embedding生成失败: {e}")
                raise
        
        # 按原始顺序构建结果
        for i, text in enumerate(texts):
            cached_data = cached_results.get(i, {})
            results.append(EmbeddingResult(
                text=text,
                embedding=cached_data["embedding"],
                model_name=model_name,
                metadata={
                    "processing_time": cached_data.get("processing_time", 0),
                    "dimensions": len(cached_data["embedding"]),
                    "from_cache": i not in [idx for idx, _ in texts_to_process]
                }
            ))
        
        # 保存缓存
        if use_cache and texts_to_process:
            self._save_cache()
        
        return results
    
    async def get_similarity(self, 
                            text1: str, 
                            text2: str, 
                            model_name: str = None) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本  
            model_name: 模型名称
            
        Returns:
            相似度分数 (0-1)
        """
        # 生成embeddings
        results = await self.embed_texts([text1, text2], model_name)
        
        # 计算余弦相似度
        emb1 = np.array(results[0].embedding)
        emb2 = np.array(results[1].embedding)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """获取模型信息"""
        model_name = model_name or self.config.model_name
        
        if model_name in self.SUPPORTED_MODELS:
            info = self.SUPPORTED_MODELS[model_name].copy()
            info["is_loaded"] = (self.current_model_name == model_name and self.model is not None)
            return info
        
        return {"error": f"不支持的模型: {model_name}"}
    
    def list_supported_models(self) -> Dict[str, Dict[str, Any]]:
        """列出所有支持的模型"""
        return self.SUPPORTED_MODELS.copy()
    
    async def switch_model(self, model_name: str) -> bool:
        """切换模型"""
        if model_name not in self.SUPPORTED_MODELS:
            logger.error(f"不支持的模型: {model_name}")
            return False
        
        success = await self._load_model(model_name)
        if success:
            self.config.model_name = model_name
            logger.info(f"✅ 已切换到模型: {model_name}")
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "cache_size": len(self._embedding_cache),
            "current_model": self.current_model_name,
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
        }
    
    def clear_cache(self) -> int:
        """清空缓存"""
        cache_size = len(self._embedding_cache)
        self._embedding_cache.clear()
        
        # 删除缓存文件
        if os.path.exists(self._cache_file):
            os.remove(self._cache_file)
        
        logger.info(f"✅ 已清空 {cache_size} 个缓存embedding")
        return cache_size
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试embedding生成
            test_text = "This is a health check test."
            result = await self.embed_text(test_text, use_cache=False)
            
            return {
                "status": "healthy",
                "model_loaded": self.model is not None,
                "current_model": self.current_model_name,
                "test_embedding_dimensions": len(result.embedding),
                "cache_size": len(self._embedding_cache),
                "stats": self.get_stats()
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": self.model is not None
            }


# 单例实例
_embedding_service_instance = None

def get_embedding_service(config: EmbeddingConfig = None) -> EmbeddingService:
    """获取Embedding服务单例实例"""
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(config)
    return _embedding_service_instance 