"""
向量数据库和Embedding服务集成测试
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from layers.intelligent_context.vector_database_service import (
    VectorDatabaseService, VectorDocument, get_vector_database
)
from layers.intelligent_context.embedding_service import (
    EmbeddingService, EmbeddingConfig, get_embedding_service
)


class TestVectorDatabaseEmbeddingIntegration:
    """向量数据库和Embedding服务集成测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def vector_db(self, temp_dir):
        """向量数据库fixture"""
        db_path = Path(temp_dir) / "test_chroma_db"
        return VectorDatabaseService(
            persist_directory=str(db_path),
            collection_name="test_collection"
        )
    
    @pytest.fixture
    def embedding_service(self, temp_dir):
        """Embedding服务fixture"""
        cache_path = Path(temp_dir) / "test_embeddings_cache"
        config = EmbeddingConfig(
            model_name="all-MiniLM-L6-v2",  # 使用轻量级模型
            cache_dir=str(cache_path),
            batch_size=4
        )
        return EmbeddingService(config)
    
    @pytest.mark.asyncio
    async def test_basic_vector_db_operations(self, vector_db):
        """测试向量数据库基本操作"""
        # 添加文档
        doc_id = await vector_db.add_document(
            content="这是一个测试文档",
            metadata={"type": "test", "category": "basic"}
        )
        
        assert doc_id is not None
        
        # 获取文档
        doc = await vector_db.get_document(doc_id)
        assert doc is not None
        assert doc.content == "这是一个测试文档"
        assert doc.metadata["type"] == "test"
        
        # 搜索文档
        results = await vector_db.search("测试文档", top_k=5)
        assert len(results) > 0
        assert results[0].document.content == "这是一个测试文档"
        
        # 删除文档
        success = await vector_db.delete_document(doc_id)
        assert success
    
    @pytest.mark.asyncio 
    async def test_basic_embedding_operations(self, embedding_service):
        """测试Embedding服务基本操作"""
        # 等待模型加载
        await asyncio.sleep(2)
        
        # 单文本embedding
        result = await embedding_service.embed_text("Hello, world!")
        assert result.embedding is not None
        assert len(result.embedding) == 384  # all-MiniLM-L6-v2的维度
        assert result.model_name == "all-MiniLM-L6-v2"
        
        # 批量文本embedding
        texts = ["Hello", "World", "Test", "Embedding"]
        results = await embedding_service.embed_texts(texts)
        assert len(results) == 4
        for result in results:
            assert len(result.embedding) == 384
        
        # 相似度计算
        similarity = await embedding_service.get_similarity("Hello", "Hi")
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # 应该有一定相似度
    
    @pytest.mark.asyncio
    async def test_integrated_knowledge_storage_and_retrieval(self, vector_db, embedding_service):
        """测试知识存储和检索的完整流程"""
        # 等待模型加载
        await asyncio.sleep(2)
        
        # 准备测试知识
        knowledge_items = [
            {
                "content": "Python是一种高级编程语言，具有简洁的语法和强大的功能",
                "metadata": {"topic": "programming", "language": "python"}
            },
            {
                "content": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习",
                "metadata": {"topic": "ai", "field": "machine_learning"}
            },
            {
                "content": "向量数据库用于存储和检索高维向量数据，支持相似性搜索",
                "metadata": {"topic": "database", "type": "vector"}
            },
            {
                "content": "自然语言处理是计算机科学和人工智能的交叉领域",
                "metadata": {"topic": "ai", "field": "nlp"}
            }
        ]
        
        # 存储知识到向量数据库
        doc_ids = []
        for item in knowledge_items:
            doc_id = await vector_db.add_document(
                content=item["content"],
                metadata=item["metadata"]
            )
            doc_ids.append(doc_id)
        
        # 测试相关性搜索
        search_queries = [
            ("编程语言", "programming"),
            ("人工智能", "ai"), 
            ("数据库", "database"),
            ("机器学习算法", "machine_learning")
        ]
        
        for query, expected_topic in search_queries:
            # 搜索相关文档
            results = await vector_db.search(query, top_k=2)
            
            assert len(results) > 0, f"查询'{query}'没有返回结果"
            
            # 验证最相关的结果
            top_result = results[0]
            assert top_result.score > 0.3, f"查询'{query}'的相关性分数太低: {top_result.score}"
            
            # 验证元数据匹配
            if expected_topic in ["programming", "database"]:
                assert expected_topic in top_result.document.metadata.get("topic", "")
            elif expected_topic in ["ai", "machine_learning", "nlp"]:
                metadata_values = str(top_result.document.metadata)
                assert "ai" in metadata_values or expected_topic in metadata_values
        
        # 清理测试数据
        deleted_count = await vector_db.delete_documents(doc_ids)
        assert deleted_count == len(doc_ids)
    
    @pytest.mark.asyncio
    async def test_embedding_caching(self, embedding_service):
        """测试Embedding缓存功能"""
        # 等待模型加载
        await asyncio.sleep(2)
        
        test_text = "This is a test for caching functionality"
        
        # 第一次生成embedding（应该不是从缓存）
        result1 = await embedding_service.embed_text(test_text)
        assert not result1.metadata.get("from_cache", False)
        
        # 第二次生成embedding（应该从缓存获取）
        result2 = await embedding_service.embed_text(test_text)
        assert result2.metadata.get("from_cache", True)
        
        # 验证结果一致性
        assert result1.embedding == result2.embedding
        
        # 检查缓存统计
        stats = embedding_service.get_stats()
        assert stats["cache_hits"] > 0
        assert stats["cache_size"] > 0
    
    @pytest.mark.asyncio
    async def test_vector_db_health_check(self, vector_db):
        """测试向量数据库健康检查"""
        health_status = await vector_db.health_check()
        
        assert health_status["status"] == "healthy"
        assert health_status["database_accessible"] is True
        assert health_status["search_working"] is True
        assert "collection_info" in health_status
        assert "stats" in health_status
    
    @pytest.mark.asyncio
    async def test_embedding_service_health_check(self, embedding_service):
        """测试Embedding服务健康检查"""
        # 等待模型加载
        await asyncio.sleep(3)
        
        health_status = await embedding_service.health_check()
        
        assert health_status["status"] == "healthy"
        assert health_status["model_loaded"] is True
        assert health_status["current_model"] == "all-MiniLM-L6-v2"
        assert health_status["test_embedding_dimensions"] == 384
        assert "stats" in health_status
    
    @pytest.mark.asyncio
    async def test_batch_operations_performance(self, vector_db, embedding_service):
        """测试批量操作性能"""
        # 等待模型加载
        await asyncio.sleep(2)
        
        # 准备批量测试数据
        test_documents = []
        for i in range(20):
            test_documents.append(VectorDocument(
                id=f"test_doc_{i}",
                content=f"这是第{i}个测试文档，内容包含一些关键词和描述",
                metadata={"batch": "test", "index": i}
            ))
        
        # 批量添加文档
        doc_ids = await vector_db.add_documents(test_documents)
        assert len(doc_ids) == 20
        
        # 批量搜索测试
        search_results = await vector_db.search("测试文档", top_k=10)
        assert len(search_results) <= 10
        assert all(result.score > 0 for result in search_results)
        
        # 验证搜索结果的相关性排序
        scores = [result.score for result in search_results]
        assert scores == sorted(scores, reverse=True), "搜索结果应该按相关性降序排列"
        
        # 清理测试数据
        deleted_count = await vector_db.delete_documents(doc_ids)
        assert deleted_count == 20
    
    def test_singleton_instances(self, temp_dir):
        """测试单例实例"""
        # 测试向量数据库单例
        db1 = get_vector_database()
        db2 = get_vector_database()
        assert db1 is db2
        
        # 测试Embedding服务单例
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 