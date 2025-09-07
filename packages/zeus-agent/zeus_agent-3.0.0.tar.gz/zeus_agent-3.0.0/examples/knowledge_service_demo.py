"""
集成知识库服务演示
展示如何使用集成的向量数据库和embedding服务
"""

import asyncio
import tempfile
from pathlib import Path

from layers.intelligent_context.integrated_knowledge_service import (
    IntegratedKnowledgeService, KnowledgeItem, get_knowledge_service
)
from layers.intelligent_context.embedding_service import EmbeddingConfig


async def demo_basic_operations():
    """演示基本操作"""
    print("🚀 开始集成知识库服务演示...")
    
    # 使用临时目录避免冲突
    temp_dir = tempfile.mkdtemp()
    
    # 配置服务
    vector_db_config = {
        "persist_directory": str(Path(temp_dir) / "demo_chroma_db"),
        "collection_name": "demo_knowledge"
    }
    
    embedding_config = EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",  # 轻量级模型，快速测试
        cache_dir=str(Path(temp_dir) / "demo_embeddings_cache")
    )
    
    # 创建服务实例
    knowledge_service = IntegratedKnowledgeService(vector_db_config, embedding_config)
    
    try:
        # 等待模型加载
        print("📥 正在加载embedding模型...")
        await asyncio.sleep(3)
        
        # 1. 添加知识
        print("\n📚 添加知识到知识库...")
        
        knowledge_items = [
            "Python是一种高级编程语言，具有简洁的语法和强大的功能。",
            "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
            "向量数据库用于存储和检索高维向量数据，支持相似性搜索。",
            "自然语言处理是计算机科学和人工智能的交叉领域。",
            "ChromaDB是一个开源的向量数据库，专为AI应用设计。"
        ]
        
        doc_ids = []
        for i, content in enumerate(knowledge_items):
            doc_id = await knowledge_service.add_knowledge(
                content=content,
                metadata={"topic": f"tech_{i}", "category": "programming"}
            )
            doc_ids.append(doc_id)
            print(f"  ✅ 已添加: {content[:30]}... (ID: {doc_id[:8]})")
        
        # 2. 搜索知识
        print(f"\n🔍 搜索知识...")
        
        search_queries = [
            "编程语言",
            "人工智能",
            "数据库",
            "向量搜索"
        ]
        
        for query in search_queries:
            print(f"\n查询: '{query}'")
            results = await knowledge_service.search_knowledge(query, top_k=3)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. 相关性: {result.score:.3f}")
                print(f"     内容: {result.content[:50]}...")
                print(f"     元数据: {result.metadata.get('topic', 'N/A')}")
        
        # 3. 获取统计信息
        print(f"\n📊 服务统计信息:")
        stats = knowledge_service.get_stats()
        print(f"  - 总文档数: {stats['total_documents']}")
        print(f"  - 总搜索数: {stats['total_searches']}")
        print(f"  - 平均搜索时间: {stats['average_search_time']:.3f}s")
        print(f"  - 缓存命中率: {stats['cache_hit_rate']:.2%}")
        
        # 4. 健康检查
        print(f"\n🏥 健康检查...")
        health = await knowledge_service.health_check()
        print(f"  状态: {health['status']}")
        print(f"  集成工作流: {'✅' if health['integrated_workflow'] else '❌'}")
        
        # 5. 清理
        print(f"\n🧹 清理测试数据...")
        await knowledge_service.clear_knowledge_base()
        print("  ✅ 知识库已清空")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✅ 演示完成")


async def demo_batch_operations():
    """演示批量操作"""
    print("\n🚀 批量操作演示...")
    
    temp_dir = tempfile.mkdtemp()
    
    vector_db_config = {
        "persist_directory": str(Path(temp_dir) / "batch_chroma_db"),
        "collection_name": "batch_knowledge"
    }
    
    embedding_config = EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",
        cache_dir=str(Path(temp_dir) / "batch_embeddings_cache"),
        batch_size=8  # 小批量测试
    )
    
    knowledge_service = IntegratedKnowledgeService(vector_db_config, embedding_config)
    
    try:
        # 准备批量数据
        knowledge_items = []
        topics = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "Swift", "Kotlin"]
        
        for i, topic in enumerate(topics):
            knowledge_items.append(KnowledgeItem(
                content=f"{topic}是一种现代编程语言，具有独特的特性和优势。",
                metadata={"language": topic.lower(), "type": "programming", "index": i}
            ))
        
        print(f"📦 批量添加 {len(knowledge_items)} 个知识项...")
        
        # 批量添加
        doc_ids = await knowledge_service.add_knowledge_batch(knowledge_items)
        print(f"✅ 成功添加 {len(doc_ids)} 个文档")
        
        # 搜索测试
        print(f"\n🔍 搜索 '编程语言'...")
        results = await knowledge_service.search_knowledge("编程语言", top_k=5)
        
        print(f"找到 {len(results)} 个相关结果:")
        for i, result in enumerate(results, 1):
            language = result.metadata.get('language', 'unknown')
            print(f"  {i}. {language.title()}: {result.score:.3f}")
        
        # 清理
        await knowledge_service.clear_knowledge_base()
        
    except Exception as e:
        print(f"❌ 批量操作演示失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """主函数"""
    print("🌟 集成知识库服务演示")
    print("=" * 50)
    
    await demo_basic_operations()
    await demo_batch_operations()
    
    print("\n🎉 所有演示完成！")


if __name__ == "__main__":
    asyncio.run(main()) 