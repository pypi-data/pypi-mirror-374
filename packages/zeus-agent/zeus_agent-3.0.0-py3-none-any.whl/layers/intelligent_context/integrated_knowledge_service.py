"""
集成知识库服务
结合向量数据库和Embedding服务，提供完整的知识存储和检索能力
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .vector_database_service import VectorDatabaseService, VectorDocument, SearchResult
from .embedding_service import EmbeddingService, EmbeddingConfig

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """知识项"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeSearchResult:
    """知识搜索结果"""
    content: str
    metadata: Dict[str, Any]
    score: float
    doc_id: str
    distance: float


class IntegratedKnowledgeService:
    """
    集成知识库服务
    
    结合向量数据库和Embedding服务，提供：
    - 智能文本向量化
    - 向量存储和检索
    - 语义相似度搜索
    - 知识管理和维护
    """
    
    def __init__(self, 
                 vector_db_config: Dict[str, Any] = None,
                 embedding_config: EmbeddingConfig = None):
        """初始化集成知识库服务"""
        
        # 初始化向量数据库
        db_config = vector_db_config or {}
        self.vector_db = VectorDatabaseService(
            persist_directory=db_config.get("persist_directory", "./data/chroma_db"),
            collection_name=db_config.get("collection_name", "knowledge_base")
        )
        
        # 初始化Embedding服务
        self.embedding_service = EmbeddingService(embedding_config)
        
        # 统计信息
        self.stats = {
            "total_documents": 0,
            "total_searches": 0,
            "average_search_time": 0.0,
            "cache_hit_rate": 0.0
        }
        
        logger.info("✅ 集成知识库服务初始化完成")
    
    async def add_knowledge(self, 
                           content: str, 
                           metadata: Dict[str, Any] = None,
                           doc_id: str = None,
                           model_name: str = None) -> str:
        """
        添加知识到知识库
        
        Args:
            content: 知识内容
            metadata: 元数据
            doc_id: 文档ID
            model_name: 使用的embedding模型
            
        Returns:
            文档ID
        """
        try:
            # 1. 生成embedding
            embedding_result = await self.embedding_service.embed_text(
                content, model_name=model_name
            )
            
            # 2. 准备元数据
            metadata = metadata or {}
            metadata.update({
                "embedding_model": embedding_result.model_name,
                "embedding_dimensions": len(embedding_result.embedding),
                "content_length": len(content),
                "added_at": datetime.now().isoformat()
            })
            
            # 3. 存储到向量数据库
            doc_id = await self.vector_db.add_document(
                content=content,
                metadata=metadata,
                doc_id=doc_id,
                embedding=embedding_result.embedding
            )
            
            # 4. 更新统计
            self.stats["total_documents"] += 1
            
            logger.debug(f"✅ 已添加知识: {doc_id[:16]}... (长度: {len(content)})")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ 添加知识失败: {e}")
            raise
    
    async def add_knowledge_batch(self, 
                                 knowledge_items: List[KnowledgeItem],
                                 model_name: str = None) -> List[str]:
        """
        批量添加知识
        
        Args:
            knowledge_items: 知识项列表
            model_name: 使用的embedding模型
            
        Returns:
            文档ID列表
        """
        if not knowledge_items:
            return []
        
        try:
            # 1. 批量生成embeddings
            texts = [item.content for item in knowledge_items]
            embedding_results = await self.embedding_service.embed_texts(
                texts, model_name=model_name
            )
            
            # 2. 准备向量文档
            vector_documents = []
            for item, embedding_result in zip(knowledge_items, embedding_results):
                # 更新元数据
                metadata = item.metadata.copy()
                metadata.update({
                    "embedding_model": embedding_result.model_name,
                    "embedding_dimensions": len(embedding_result.embedding),
                    "content_length": len(item.content),
                    "added_at": item.created_at.isoformat()
                })
                
                # 创建向量文档
                vector_doc = VectorDocument(
                    id=item.doc_id or "",
                    content=item.content,
                    metadata=metadata,
                    embedding=embedding_result.embedding,
                    created_at=item.created_at
                )
                vector_documents.append(vector_doc)
            
            # 3. 批量存储到向量数据库
            doc_ids = await self.vector_db.add_documents(vector_documents)
            
            # 4. 更新统计
            self.stats["total_documents"] += len(doc_ids)
            
            logger.info(f"✅ 已批量添加 {len(doc_ids)} 个知识项")
            return doc_ids
            
        except Exception as e:
            logger.error(f"❌ 批量添加知识失败: {e}")
            raise
    
    async def search_knowledge(self, 
                              query: str, 
                              top_k: int = 10,
                              filters: Dict[str, Any] = None,
                              min_score: float = 0.0) -> List[KnowledgeSearchResult]:
        """
        搜索知识
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
            min_score: 最小相关性分数
            
        Returns:
            搜索结果列表
        """
        try:
            start_time = datetime.now()
            
            # 1. 生成查询向量
            query_embedding_result = await self.embedding_service.embed_text(query)
            
            # 2. 向量搜索
            search_results = await self.vector_db.search(
                query, 
                top_k=top_k, 
                filters=filters,
                query_embedding=query_embedding_result.embedding
            )
            
            # 3. 过滤低分结果
            filtered_results = [
                result for result in search_results 
                if result.score >= min_score
            ]
            
            # 4. 转换结果格式
            knowledge_results = []
            for result in filtered_results:
                knowledge_results.append(KnowledgeSearchResult(
                    content=result.document.content,
                    metadata=result.document.metadata,
                    score=result.score,
                    doc_id=result.document.id,
                    distance=result.distance
                ))
            
            # 5. 更新统计
            search_time = (datetime.now() - start_time).total_seconds()
            self.stats["total_searches"] += 1
            
            # 更新平均搜索时间
            total_time = (self.stats["average_search_time"] * (self.stats["total_searches"] - 1) + search_time)
            self.stats["average_search_time"] = total_time / self.stats["total_searches"]
            
            logger.debug(f"🔍 知识搜索完成: {len(knowledge_results)} 个结果 ({search_time:.3f}s)")
            return knowledge_results
            
        except Exception as e:
            logger.error(f"❌ 知识搜索失败: {e}")
            raise
    
    async def get_knowledge(self, doc_id: str) -> Optional[KnowledgeItem]:
        """
        获取指定知识
        
        Args:
            doc_id: 文档ID
            
        Returns:
            知识项，如果不存在则返回None
        """
        try:
            doc = await self.vector_db.get_document(doc_id)
            if doc:
                return KnowledgeItem(
                    content=doc.content,
                    metadata=doc.metadata,
                    doc_id=doc.id,
                    created_at=doc.created_at
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取知识失败: {e}")
            return None
    
    async def update_knowledge(self, 
                              doc_id: str, 
                              content: str = None,
                              metadata: Dict[str, Any] = None,
                              model_name: str = None) -> bool:
        """
        更新知识
        
        Args:
            doc_id: 文档ID
            content: 新内容
            metadata: 新元数据
            model_name: embedding模型
            
        Returns:
            更新是否成功
        """
        try:
            # 如果更新了内容，需要重新生成embedding
            if content is not None:
                embedding_result = await self.embedding_service.embed_text(
                    content, model_name=model_name
                )
                
                # 更新元数据
                if metadata is None:
                    metadata = {}
                metadata.update({
                    "embedding_model": embedding_result.model_name,
                    "embedding_dimensions": len(embedding_result.embedding),
                    "content_length": len(content),
                    "updated_at": datetime.now().isoformat()
                })
                
                # 由于ChromaDB的限制，我们需要删除旧文档并添加新文档
                await self.vector_db.delete_document(doc_id)
                await self.vector_db.add_document(
                    content=content,
                    metadata=metadata,
                    doc_id=doc_id,
                    embedding=embedding_result.embedding
                )
            else:
                # 只更新元数据
                success = await self.vector_db.update_document(doc_id, metadata=metadata)
                return success
            
            logger.debug(f"✅ 已更新知识: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新知识失败: {e}")
            return False
    
    async def delete_knowledge(self, doc_id: str) -> bool:
        """
        删除知识
        
        Args:
            doc_id: 文档ID
            
        Returns:
            删除是否成功
        """
        try:
            success = await self.vector_db.delete_document(doc_id)
            if success:
                self.stats["total_documents"] = max(0, self.stats["total_documents"] - 1)
            return success
            
        except Exception as e:
            logger.error(f"❌ 删除知识失败: {e}")
            return False
    
    async def clear_knowledge_base(self) -> bool:
        """清空知识库"""
        try:
            success = await self.vector_db.clear_collection()
            if success:
                self.stats["total_documents"] = 0
            return success
            
        except Exception as e:
            logger.error(f"❌ 清空知识库失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        # 获取各组件的统计信息
        vector_db_stats = self.vector_db.get_stats()
        embedding_stats = self.embedding_service.get_stats()
        
        return {
            **self.stats,
            "vector_db": vector_db_stats,
            "embedding_service": embedding_stats,
            "cache_hit_rate": embedding_stats.get("cache_hit_rate", 0.0)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查各组件健康状态
            vector_db_health = await self.vector_db.health_check()
            embedding_health = await self.embedding_service.health_check()
            
            # 测试完整流程
            test_content = "这是一个健康检查测试"
            test_doc_id = await self.add_knowledge(test_content, {"test": True})
            
            # 搜索测试
            search_results = await self.search_knowledge("健康检查", top_k=1)
            
            # 清理测试数据
            await self.delete_knowledge(test_doc_id)
            
            return {
                "status": "healthy",
                "integrated_workflow": len(search_results) > 0,
                "vector_db_health": vector_db_health,
                "embedding_health": embedding_health,
                "stats": self.get_stats()
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# 单例实例
_knowledge_service_instance = None

def get_knowledge_service(vector_db_config: Dict[str, Any] = None,
                         embedding_config: EmbeddingConfig = None) -> IntegratedKnowledgeService:
    """获取集成知识库服务单例实例"""
    global _knowledge_service_instance
    if _knowledge_service_instance is None:
        _knowledge_service_instance = IntegratedKnowledgeService(vector_db_config, embedding_config)
    return _knowledge_service_instance 