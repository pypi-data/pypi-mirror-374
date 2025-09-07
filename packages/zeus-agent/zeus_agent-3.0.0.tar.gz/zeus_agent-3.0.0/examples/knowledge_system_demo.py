#!/usr/bin/env python3
"""
FPGA知识系统完整演示
展示知识库构建、智能路由决策和多源知识融合

演示内容：
1. 知识库构建流程
2. 知识路由决策机制
3. 不同查询类型的处理策略
4. 知识来源选择的智能化
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from layers.intelligent_context.knowledge_builder import KnowledgeBuilder, KnowledgeSource
from layers.intelligent_context.knowledge_router import KnowledgeRouter, get_knowledge_router
from layers.intelligent_context.integrated_knowledge_service import IntegratedKnowledgeService


async def demo_knowledge_building():
    """演示知识库构建过程"""
    print("🏗️ 知识库构建演示")
    print("=" * 50)
    
    try:
        # 1. 初始化知识服务
        knowledge_service = IntegratedKnowledgeService()
        await knowledge_service.initialize()
        
        # 2. 创建知识构建器
        builder = KnowledgeBuilder(knowledge_service)
        
        # 3. 添加不同类型的知识源
        print("\n📋 添加知识源:")
        
        # Markdown文档
        md_source = KnowledgeSource(
            name="FPGA基础概念",
            source_type="markdown",
            file_path="./workspace/agents/fpga_expert/knowledge/basic_concepts.md",
            tags=['fpga', 'concepts', 'tutorial'],
            priority=1
        )
        builder.add_source(md_source)
        print(f"   ✅ 已添加: {md_source.name} ({md_source.source_type})")
        
        # YAML结构化数据
        yaml_source = KnowledgeSource(
            name="FPGA器件数据库",
            source_type="yaml",
            file_path="./workspace/agents/fpga_expert/knowledge/fpga_devices.yaml",
            tags=['fpga', 'devices', 'specifications'],
            priority=1
        )
        builder.add_source(yaml_source)
        print(f"   ✅ 已添加: {yaml_source.name} ({yaml_source.source_type})")
        
        # Verilog代码示例
        verilog_source = KnowledgeSource(
            name="基础Verilog模块",
            source_type="verilog",
            file_path="./workspace/agents/fpga_expert/templates/basic_modules/counter.v",
            tags=['verilog', 'examples', 'modules'],
            priority=2
        )
        # 创建示例Verilog文件
        await create_sample_verilog()
        builder.add_source(verilog_source)
        print(f"   ✅ 已添加: {verilog_source.name} ({verilog_source.source_type})")
        
        # 4. 构建知识库
        print(f"\n🔨 开始构建知识库...")
        stats = await builder.build_knowledge_base()
        
        print(f"\n📊 构建结果:")
        print(f"   处理知识源: {stats['sources_processed']} 个")
        print(f"   创建知识块: {stats['chunks_created']} 个")
        print(f"   存储知识项: {stats['knowledge_items_stored']} 个")
        print(f"   处理时间: {stats['processing_time']:.2f} 秒")
        
        if stats['errors']:
            print(f"   ⚠️ 错误: {len(stats['errors'])} 个")
        
        # 5. 获取统计信息
        builder_stats = builder.get_statistics()
        print(f"\n📈 知识库统计:")
        print(f"   总知识块: {builder_stats['total_chunks']}")
        print(f"   知识源: {builder_stats['total_sources']}")
        print(f"   块类型分布: {builder_stats['chunk_types']}")
        print(f"   热门标签: {dict(builder_stats['top_tags'][:5])}")
        
        return knowledge_service
        
    except Exception as e:
        print(f"❌ 知识库构建失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def demo_knowledge_routing():
    """演示知识路由决策"""
    print("\n🧭 知识路由决策演示")
    print("=" * 50)
    
    # 获取知识路由器
    router = get_knowledge_router()
    
    # 测试不同类型的查询
    test_queries = [
        {
            "query": "什么是FPGA？请详细介绍FPGA的基本概念",
            "expected": "本地知识库（概念查询）"
        },
        {
            "query": "帮我设计一个8位计数器的Verilog代码",
            "expected": "AI训练数据（创造性任务）"
        },
        {
            "query": "Xilinx Artix-7 FPGA的技术参数是什么？",
            "expected": "本地知识库（专业数据查询）"
        },
        {
            "query": "2024年最新发布的FPGA芯片有哪些？",
            "expected": "网络搜索（最新信息）"
        },
        {
            "query": "如何优化FPGA设计的时序性能？",
            "expected": "混合模式（复杂分析）"
        }
    ]
    
    print(f"\n🧪 测试 {len(test_queries)} 个不同类型的查询:")
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}/{len(test_queries)} ---")
        print(f"查询: {test_case['query']}")
        print(f"预期: {test_case['expected']}")
        
        # 执行路由决策
        decision = await router.route_query(test_case['query'])
        
        print(f"决策: {decision.primary_source.value}")
        print(f"置信度: {decision.confidence:.2f}")
        print(f"推理: {decision.reasoning}")
        print(f"预估成本: {decision.estimated_cost:.2f}")
        print(f"预估延迟: {decision.expected_latency:.1f}s")
        
        if decision.secondary_sources:
            print(f"辅助源: {[s.value for s in decision.secondary_sources]}")
    
    # 显示知识源信息
    print(f"\n📋 知识源能力对比:")
    source_info = router.get_source_info()
    for source_name, info in source_info.items():
        print(f"\n{source_name}:")
        print(f"   优势: {', '.join(info['strengths'][:3])}...")
        print(f"   成本: {info['cost']:.1f}, 延迟: {info['latency']:.1f}s")
        print(f"   新鲜度: {info['freshness']:.1f}")


async def demo_integrated_knowledge_usage(knowledge_service):
    """演示集成知识服务的使用"""
    print("\n🔍 集成知识服务演示")
    print("=" * 50)
    
    if not knowledge_service:
        print("❌ 知识服务未初始化，跳过演示")
        return
    
    # 测试知识检索
    test_searches = [
        "FPGA基本概念",
        "Verilog状态机",
        "Artix-7技术参数",
        "时序优化方法"
    ]
    
    print(f"\n🔍 测试知识检索:")
    
    for query in test_searches:
        print(f"\n查询: {query}")
        try:
            results = await knowledge_service.search(
                query=query,
                top_k=3,
                confidence_threshold=0.3
            )
            
            print(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. 相关度: {result.score:.2f}")
                print(f"      内容: {result.content[:100]}...")
                print(f"      来源: {result.metadata.get('source', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")


async def create_sample_verilog():
    """创建示例Verilog文件"""
    verilog_dir = Path("./workspace/agents/fpga_expert/templates/basic_modules")
    verilog_dir.mkdir(parents=True, exist_ok=True)
    
    counter_code = '''// 参数化计数器模块
// 功能：可配置位宽的同步计数器
// 特性：异步复位，使能控制，溢出标志

module counter #(
    parameter WIDTH = 8
) (
    input  wire             clk,      // 时钟信号
    input  wire             rst_n,    // 异步复位（低有效）
    input  wire             enable,   // 计数使能
    input  wire             load,     // 加载使能
    input  wire [WIDTH-1:0] load_val, // 加载值
    output reg  [WIDTH-1:0] count,    // 计数输出
    output wire             overflow  // 溢出标志
);

    // 溢出检测
    assign overflow = (count == {WIDTH{1'b1}}) && enable;
    
    // 计数器主逻辑
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= {WIDTH{1'b0}};
        end else if (load) begin
            count <= load_val;
        end else if (enable) begin
            count <= count + 1'b1;
        end
    end

endmodule

// 使用示例：
// counter #(.WIDTH(16)) my_counter (
//     .clk(system_clock),
//     .rst_n(reset_n),
//     .enable(count_enable),
//     .load(load_counter),
//     .load_val(initial_value),
//     .count(counter_output),
//     .overflow(counter_overflow)
// );'''
    
    counter_file = verilog_dir / "counter.v"
    with open(counter_file, 'w', encoding='utf-8') as f:
        f.write(counter_code)


async def main():
    """主演示函数"""
    print("🚀 FPGA知识系统完整演示")
    print("展示知识库构建、智能路由和多源融合")
    print("=" * 60)
    
    # 1. 演示知识库构建
    knowledge_service = await demo_knowledge_building()
    
    # 2. 演示知识路由决策
    await demo_knowledge_routing()
    
    # 3. 演示集成知识服务
    await demo_integrated_knowledge_usage(knowledge_service)
    
    print("\n🎉 演示完成!")
    
    print("\n💡 关键要点总结:")
    print("   ✅ 知识库支持多种格式：Markdown、YAML、Verilog等")
    print("   ✅ 智能路由根据查询类型选择最优知识源")
    print("   ✅ 本地知识库：专业精确，成本低，速度快")
    print("   ✅ AI训练数据：创造性强，覆盖面广")
    print("   ✅ 网络搜索：信息最新，实时更新")
    print("   ✅ 混合策略：发挥各源优势，提供最佳答案")
    
    print("\n🎯 知识库优先架构的优势:")
    print("   1. 80%时间构建高质量知识库")
    print("   2. 20%时间编写智能路由逻辑")
    print("   3. 自动选择最适合的知识来源")
    print("   4. 成本可控，性能可预测")
    print("   5. 知识质量可管控，结果可解释")


if __name__ == "__main__":
    asyncio.run(main()) 