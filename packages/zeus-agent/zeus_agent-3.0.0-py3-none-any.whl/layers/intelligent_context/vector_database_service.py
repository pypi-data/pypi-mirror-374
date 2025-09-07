"""
向量数据库服务
集成ChromaDB，提供向量存储和检索能力
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

import chromadb
from chromadb.config import Settings
from chromadb.api.types import EmbeddingFunction
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """向量文档"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """搜索结果"""
    document: VectorDocument
    distance: float
    score: float  # 1 - distance，分数越高越相关


class VectorDatabaseService:
    """
    向量数据库服务
    
    基于ChromaDB实现向量存储和检索功能
    """
    
    def __init__(self, 
                 persist_directory: str = "./data/chroma_db",
                 collection_name: str = "agent_knowledge"):
        """初始化向量数据库服务"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合（禁用默认embedding函数，我们使用自己的）
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"✅ 已连接到现有集合: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Agent知识库向量存储"},
                embedding_function=None  # 禁用默认embedding，使用我们自己的
            )
            logger.info(f"✅ 已创建新集合: {collection_name}")
        
        # 统计信息
        self.stats = {
            "documents_count": 0,
            "queries_count": 0,
            "last_updated": datetime.now()
        }
        
        self._update_stats()
    
    def _update_stats(self):
        """更新统计信息"""
        try:
            count = self.collection.count()
            self.stats.update({
                "documents_count": count,
                "last_updated": datetime.now()
            })
        except Exception as e:
            logger.warning(f"更新统计信息失败: {e}")
    
    def _generate_doc_id(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """生成文档ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if metadata:
            metadata_str = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:8]
            return f"{content_hash}_{metadata_hash}"
        return content_hash
    
    async def add_document(self, 
                          content: str, 
                          metadata: Dict[str, Any] = None,
                          doc_id: str = None,
                          embedding: List[float] = None) -> str:
        """
        添加文档到向量数据库
        
        Args:
            content: 文档内容
            metadata: 文档元数据
            doc_id: 文档ID，如果不提供则自动生成
            embedding: 预计算的向量，如果不提供则需要外部生成
            
        Returns:
            文档ID
        """
        try:
            if not doc_id:
                doc_id = self._generate_doc_id(content, metadata)
            
            metadata = metadata or {}
            metadata.update({
                "created_at": datetime.now().isoformat(),
                "content_length": len(content)
            })
            
            # 添加文档到ChromaDB
            add_params = {
                "documents": [content],
                "metadatas": [metadata],
                "ids": [doc_id]
            }
            
            # 如果提供了embedding，则使用它
            if embedding is not None:
                add_params["embeddings"] = [embedding]
            
            self.collection.add(**add_params)
            
            self._update_stats()
            logger.debug(f"✅ 已添加文档: {doc_id[:16]}...")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            raise
    
    async def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """
        批量添加文档
        
        Args:
            documents: 向量文档列表
            
        Returns:
            文档ID列表
        """
        if not documents:
            return []
        
        try:
            # 准备批量数据
            doc_ids = []
            contents = []
            metadatas = []
            embeddings = []
            
            for doc in documents:
                # 生成ID如果没有提供
                doc_id = doc.id or self._generate_doc_id(doc.content, doc.metadata)
                doc_ids.append(doc_id)
                contents.append(doc.content)
                metadatas.append(doc.metadata)
                if doc.embedding:
                    embeddings.append(doc.embedding)
            
            # 批量添加到ChromaDB
            add_params = {
                "documents": contents,
                "metadatas": metadatas,
                "ids": doc_ids
            }
            
            # 如果所有文档都有embedding，则使用它们
            if len(embeddings) == len(documents):
                add_params["embeddings"] = embeddings
            
            self.collection.add(**add_params)
            
            self._update_stats()
            logger.debug(f"✅ 已批量添加 {len(doc_ids)} 个文档")
            return doc_ids
            
        except Exception as e:
            logger.error(f"❌ 批量添加文档失败: {e}")
            raise
    
    async def search(self, 
                    query: str, 
                    top_k: int = 10,
                    filters: Dict[str, Any] = None,
                    query_embedding: List[float] = None) -> List[SearchResult]:
        """
        向量搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
            query_embedding: 查询向量，如果不提供则需要外部生成
            
        Returns:
            搜索结果列表
        """
        try:
            self.stats["queries_count"] += 1
            
            # 构建where条件
            where_condition = filters if filters else None
            
            # 执行搜索
            if query_embedding is not None:
                # 使用提供的embedding进行搜索
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_condition
                )
            else:
                # 使用文本搜索（需要collection有embedding函数）
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_condition
                )
            
            # 转换结果格式
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc_content in enumerate(results['documents'][0]):
                    doc_id = results['ids'][0][i]
                    metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'][0] else 0.0
                    
                    # 创建文档对象
                    doc = VectorDocument(
                        id=doc_id,
                        content=doc_content,
                        metadata=metadata
                    )
                    
                    # 计算相关性分数 (1 - distance)
                    score = max(0.0, 1.0 - distance)
                    
                    search_results.append(SearchResult(
                        document=doc,
                        distance=distance,
                        score=score
                    ))
            
            logger.debug(f"🔍 搜索完成，返回 {len(search_results)} 个结果")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ 向量搜索失败: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """
        获取指定文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档对象，如果不存在则返回None
        """
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if results['documents'] and results['documents'][0]:
                return VectorDocument(
                    id=doc_id,
                    content=results['documents'][0],
                    metadata=results['metadatas'][0] if results['metadatas'] else {}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取文档失败: {e}")
            return None
    
    async def update_document(self, 
                             doc_id: str, 
                             content: str = None,
                             metadata: Dict[str, Any] = None) -> bool:
        """
        更新文档
        
        Args:
            doc_id: 文档ID
            content: 新的文档内容
            metadata: 新的元数据
            
        Returns:
            更新是否成功
        """
        try:
            # 获取现有文档
            existing_doc = await self.get_document(doc_id)
            if not existing_doc:
                logger.warning(f"文档不存在: {doc_id}")
                return False
            
            # 准备更新数据
            update_data = {}
            
            if content is not None:
                update_data['documents'] = [content]
            
            if metadata is not None:
                # 合并元数据
                new_metadata = existing_doc.metadata.copy()
                new_metadata.update(metadata)
                new_metadata['updated_at'] = datetime.now().isoformat()
                update_data['metadatas'] = [new_metadata]
            
            if update_data:
                update_data['ids'] = [doc_id]
                self.collection.update(**update_data)
                logger.debug(f"✅ 已更新文档: {doc_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 更新文档失败: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            删除是否成功
        """
        try:
            self.collection.delete(ids=[doc_id])
            self._update_stats()
            logger.debug(f"✅ 已删除文档: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            return False
    
    async def delete_documents(self, doc_ids: List[str]) -> int:
        """
        批量删除文档
        
        Args:
            doc_ids: 文档ID列表
            
        Returns:
            成功删除的文档数量
        """
        try:
            self.collection.delete(ids=doc_ids)
            self._update_stats()
            logger.info(f"✅ 已批量删除 {len(doc_ids)} 个文档")
            return len(doc_ids)
            
        except Exception as e:
            logger.error(f"❌ 批量删除文档失败: {e}")
            return 0
    
    async def clear_collection(self) -> bool:
        """
        清空集合
        
        Returns:
            清空是否成功
        """
        try:
            # 删除现有集合
            self.client.delete_collection(name=self.collection_name)
            
            # 重新创建集合
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Agent知识库向量存储"}
            )
            
            self._update_stats()
            logger.info(f"✅ 已清空集合: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 清空集合失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        self._update_stats()
        return self.stats.copy()
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试基本操作
            test_doc_id = "health_check_test"
            test_content = "This is a health check test document."
            
            # 添加测试文档
            await self.add_document(test_content, {"test": True}, test_doc_id)
            
            # 搜索测试
            results = await self.search("health check test", top_k=1)
            
            # 删除测试文档
            await self.delete_document(test_doc_id)
            
            return {
                "status": "healthy",
                "database_accessible": True,
                "search_working": len(results) > 0,
                "collection_info": self.get_collection_info(),
                "stats": self.get_stats()
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_accessible": False
            }


# 单例实例
_vector_db_instance = None

def get_vector_database(persist_directory: str = "./data/chroma_db",
                       collection_name: str = "agent_knowledge") -> VectorDatabaseService:
    """获取向量数据库单例实例"""
    global _vector_db_instance
    if _vector_db_instance is None:
        _vector_db_instance = VectorDatabaseService(persist_directory, collection_name)
    return _vector_db_instance 