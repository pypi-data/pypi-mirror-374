#!/usr/bin/env python3
"""
RAG系统完整演示
展示我们的增强RAG架构如何工作

演示流程：
1. 查询分析和路由
2. 多策略知识检索
3. 智能上下文增强
4. 引导式内容生成
5. 质量评估和反馈
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from layers.intelligent_context.rag_system import RAGSystem, RetrievalStrategy, AugmentationMethod
from layers.intelligent_context.knowledge_router import get_knowledge_router
from layers.framework.abstractions.context import UniversalContext


async def demo_traditional_rag():
    """演示传统RAG流程"""
    print("📚 传统RAG流程演示")
    print("=" * 40)
    
    rag = RAGSystem()
    
    query = "什么是FPGA状态机设计的最佳实践？"
    context = UniversalContext()
    
    print(f"🔍 查询: {query}")
    
    # 1. 检索阶段
    print("\n1️⃣ 检索阶段:")
    retrieval_result = await rag.retrieve(query, context, RetrievalStrategy.HYBRID)
    print(f"   检索策略: {retrieval_result.strategy_used.value}")
    print(f"   找到文档: {len(retrieval_result.documents)} 个")
    print(f"   检索时间: {retrieval_result.retrieval_time:.3f}s")
    
    # 显示检索到的文档
    for i, doc in enumerate(retrieval_result.documents[:2], 1):
        print(f"   文档{i}: {doc.get('title', 'Unknown')[:50]}...")
        print(f"          相关度: {retrieval_result.scores[i-1]:.3f}")
    
    # 2. 增强阶段
    print("\n2️⃣ 增强阶段:")
    augmentation_result = await rag.augment(query, retrieval_result, context)
    print(f"   增强方法: {augmentation_result.method_used.value}")
    print(f"   质量评分: {augmentation_result.quality_score:.3f}")
    print(f"   增强上下文长度: {len(augmentation_result.augmented_context)} 字符")
    print(f"   上下文预览: {augmentation_result.augmented_context[:100]}...")
    
    # 3. 生成阶段
    print("\n3️⃣ 生成阶段:")
    generation_result = await rag.generate(query, augmentation_result, context)
    print(f"   生成模式: {generation_result.mode_used.value}")
    print(f"   置信度: {generation_result.confidence_score:.3f}")
    print(f"   生成内容: {generation_result.generated_content[:200]}...")
    
    return rag


async def demo_enhanced_rag():
    """演示我们的增强RAG流程"""
    print("\n🚀 增强RAG流程演示")
    print("=" * 40)
    
    # 1. 智能路由决策
    print("1️⃣ 智能路由决策:")
    router = get_knowledge_router()
    
    queries = [
        "FPGA状态机设计最佳实践",
        "生成一个8位计数器的Verilog代码", 
        "2024年最新FPGA芯片性能对比"
    ]
    
    for query in queries:
        decision = await router.route_query(query)
        print(f"   查询: {query[:30]}...")
        print(f"   路由: {decision.primary_source.value} (置信度: {decision.confidence:.2f})")
        print(f"   推理: {decision.reasoning[:50]}...")
        print()
    
    # 2. 多层RAG处理
    print("2️⃣ 多层RAG处理:")
    rag = RAGSystem()
    
    test_query = "如何在FPGA中实现高效的状态机？"
    context = UniversalContext()
    
    # 使用完整RAG流程
    result = await rag.process_query(test_query, context)
    
    print(f"   查询: {test_query}")
    print(f"   处理结果:")
    print(f"     - 检索文档: {len(result.get('source_documents', []))} 个")
    print(f"     - 生成质量: {result.get('confidence_score', 0):.3f}")
    print(f"     - 处理时间: {result.get('processing_time', 0):.3f}s")
    print(f"     - 生成内容: {result.get('generated_content', '')[:150]}...")


async def demo_rag_strategies():
    """演示不同RAG策略的效果"""
    print("\n🎯 RAG策略对比演示")
    print("=" * 40)
    
    rag = RAGSystem()
    query = "FPGA时序约束设置方法"
    context = UniversalContext()
    
    strategies = [
        RetrievalStrategy.SEMANTIC,
        RetrievalStrategy.KEYWORD,
        RetrievalStrategy.HYBRID,
        RetrievalStrategy.CONTEXTUAL
    ]
    
    print(f"🔍 测试查询: {query}")
    print("\n策略对比:")
    
    for strategy in strategies:
        result = await rag.retrieve(query, context, strategy)
        print(f"   {strategy.value:12} | 文档: {len(result.documents):2}个 | "
              f"时间: {result.retrieval_time:.3f}s | "
              f"平均分: {sum(result.scores)/len(result.scores) if result.scores else 0:.3f}")


async def demo_augmentation_methods():
    """演示不同增强方法的效果"""
    print("\n⚡ 增强方法对比演示")
    print("=" * 40)
    
    rag = RAGSystem()
    query = "FPGA功耗优化技术"
    context = UniversalContext()
    
    # 先检索
    retrieval_result = await rag.retrieve(query, context)
    
    methods = [
        AugmentationMethod.CONCATENATION,
        AugmentationMethod.INTEGRATION,
        AugmentationMethod.SUMMARIZATION,
        AugmentationMethod.FILTERING,
        AugmentationMethod.RANKING
    ]
    
    print(f"🔍 基于查询: {query}")
    print(f"📄 检索到 {len(retrieval_result.documents)} 个文档")
    print("\n增强方法对比:")
    
    for method in methods:
        result = await rag.augment(query, retrieval_result, context, method)
        print(f"   {method.value:15} | 质量: {result.quality_score:.3f} | "
              f"长度: {len(result.augmented_context):4}字符")


async def demo_rag_metrics():
    """演示RAG系统指标监控"""
    print("\n📊 RAG系统指标监控")
    print("=" * 40)
    
    rag = RAGSystem()
    
    # 获取系统指标
    metrics = await rag.get_metrics()
    
    print("📈 系统性能指标:")
    print(f"   检索精确率: {metrics.retrieval_precision:.3f}")
    print(f"   检索召回率: {metrics.retrieval_recall:.3f}")
    print(f"   增强质量: {metrics.augmentation_quality:.3f}")
    print(f"   生成相关性: {metrics.generation_relevance:.3f}")
    print(f"   端到端延迟: {metrics.end_to_end_latency:.3f}s")
    print(f"   Token效率: {metrics.token_efficiency:.3f}")
    print(f"   用户满意度: {metrics.user_satisfaction:.3f}")
    
    # 获取系统配置
    config = rag.get_system_config()
    print(f"\n🔧 系统配置:")
    print(f"   支持检索策略: {len(config['retrieval_strategies'])} 种")
    print(f"   支持增强方法: {len(config['augmentation_methods'])} 种")
    print(f"   知识库大小: {config['knowledge_base_size']} 文档")
    print(f"   缓存命中率: {config['cache_hit_rate']:.1%}")


async def main():
    """主演示函数"""
    print("🔥 RAG系统完整演示")
    print("展示增强RAG架构的核心能力")
    print("=" * 50)
    
    # 1. 传统RAG流程
    await demo_traditional_rag()
    
    # 2. 增强RAG流程
    await demo_enhanced_rag()
    
    # 3. RAG策略对比
    await demo_rag_strategies()
    
    # 4. 增强方法对比
    await demo_augmentation_methods()
    
    # 5. 系统指标监控
    await demo_rag_metrics()
    
    print("\n🎉 RAG演示完成!")
    
    print("\n💡 我们的RAG技术特点:")
    print("   ✅ 多策略智能检索（语义+关键词+混合+图谱+上下文）")
    print("   ✅ 多层次增强处理（拼接+整合+摘要+过滤+排序）")
    print("   ✅ 智能路由决策（自动选择最优知识源）")
    print("   ✅ 装饰器自动增强（@knowledge_enhanced）")
    print("   ✅ 全面指标监控（精确率+召回率+质量+延迟）")
    print("   ✅ 自适应优化（基于反馈持续改进）")
    
    print("\n🚀 相比传统RAG的优势:")
    print("   1. 智能路由：不同查询使用最优知识源")
    print("   2. 多策略融合：提高检索覆盖率和精确度")
    print("   3. 质量控制：多层增强确保生成质量")
    print("   4. 成本优化：本地知识库降低API调用成本")
    print("   5. 可解释性：提供决策推理和质量评分")


if __name__ == "__main__":
    asyncio.run(main()) 