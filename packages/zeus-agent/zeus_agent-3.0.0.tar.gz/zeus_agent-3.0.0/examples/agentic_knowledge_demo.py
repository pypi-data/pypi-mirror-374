#!/usr/bin/env python3
"""
Agentic Knowledge Base Demo
演示如何构建和使用面向Agentic RAG的FPGA知识库
"""

import asyncio
import logging
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from workspace.agents.ares.knowledge_expansion.agentic_knowledge_builder import (
    AgenticKnowledgeBuilder,
    KnowledgeType,
    KnowledgeDomain,
    KnowledgeLevel
)

class AgenticKnowledgeDemo:
    """Agentic知识库演示"""
    
    def __init__(self):
        self.demo_path = Path("demo_agentic_knowledge")
        self.demo_path.mkdir(exist_ok=True)
    
    async def run_complete_demo(self):
        """运行完整演示"""
        print("🚀 Agentic FPGA知识库演示开始")
        print("="*60)
        
        try:
            # 1. 构建知识库
            await self.demo_knowledge_building()
            
            # 2. 演示知识查询
            await self.demo_knowledge_querying()
            
            # 3. 演示关系发现
            await self.demo_relationship_discovery()
            
            # 4. 演示质量评估
            await self.demo_quality_assessment()
            
            # 5. 演示Agentic优化
            await self.demo_agentic_optimization()
            
            print("\n🎉 所有演示完成！")
            
        except Exception as e:
            logger.error(f"演示过程中出现错误: {e}")
            raise
    
    async def demo_knowledge_building(self):
        """演示知识库构建"""
        print("\n📚 1. 知识库构建演示")
        print("-" * 40)
        
        # 创建构建器
        builder = AgenticKnowledgeBuilder(
            base_path=str(self.demo_path),
            config={
                'chunk_size': 300,
                'similarity_threshold': 0.7,
                'min_quality_threshold': 0.6
            }
        )
        
        print("构建配置:")
        print(f"  - 块大小: {builder.config['chunk_size']}")
        print(f"  - 相似度阈值: {builder.config['similarity_threshold']}")
        print(f"  - 质量阈值: {builder.config['min_quality_threshold']}")
        
        # 构建知识库
        await builder.build_agentic_knowledge_base()
        
        # 显示构建结果
        print(f"\n✅ 构建完成!")
        print(f"  - 知识项: {builder.stats['total_items']}")
        print(f"  - 知识块: {builder.stats['total_chunks']}")
        print(f"  - 关系数: {builder.stats['total_relationships']}")
        print(f"  - 平均质量: {builder.stats['avg_quality_score']:.3f}")
        print(f"  - 构建时间: {builder.stats['build_time']:.2f}秒")
        
        # 保存构建器实例供后续使用
        self.builder = builder
    
    async def demo_knowledge_querying(self):
        """演示知识查询"""
        print("\n🔍 2. 知识查询演示")
        print("-" * 40)
        
        if not hasattr(self, 'builder'):
            print("⚠️ 需要先运行知识库构建")
            return
        
        # 演示不同类型的查询
        queries = [
            ("什么是FPGA？", "简单概念查询"),
            ("如何设计状态机？", "设计方法查询"),
            ("跨时钟域问题解决", "复杂技术查询"),
            ("时序约束优化技巧", "最佳实践查询")
        ]
        
        for query, description in queries:
            print(f"\n查询: {query} ({description})")
            
            # 模拟智能查询处理
            relevant_items = await self._find_relevant_knowledge(query)
            
            print(f"找到 {len(relevant_items)} 个相关知识项:")
            for item in relevant_items[:3]:  # 显示前3个
                print(f"  📄 {item['title']} (相关度: {item['relevance']:.2f})")
                print(f"     类型: {item['type']}, 领域: {item['domain']}")
    
    async def _find_relevant_knowledge(self, query: str) -> list:
        """模拟智能知识查询"""
        relevant_items = []
        
        query_lower = query.lower()
        
        for node in self.builder.knowledge_graph.nodes.values():
            # 简单的相关性计算
            relevance = 0.0
            
            # 标题匹配
            if any(word in node.metadata.title.lower() for word in query_lower.split()):
                relevance += 0.5
            
            # 标签匹配
            matching_tags = sum(1 for tag in node.metadata.tags 
                              if any(word in tag.lower() for word in query_lower.split()))
            relevance += matching_tags * 0.2
            
            # 内容匹配
            for chunk in node.chunks:
                if any(word in chunk.content.lower() for word in query_lower.split()):
                    relevance += 0.1
                    break
            
            if relevance > 0.3:  # 相关性阈值
                relevant_items.append({
                    'title': node.metadata.title,
                    'type': node.metadata.knowledge_type.value,
                    'domain': node.metadata.domain.value,
                    'relevance': relevance,
                    'node': node
                })
        
        # 按相关性排序
        relevant_items.sort(key=lambda x: x['relevance'], reverse=True)
        return relevant_items
    
    async def demo_relationship_discovery(self):
        """演示关系发现"""
        print("\n🔗 3. 知识关系发现演示")
        print("-" * 40)
        
        if not hasattr(self, 'builder'):
            print("⚠️ 需要先运行知识库构建")
            return
        
        print("知识关系网络:")
        
        # 显示关系统计
        total_nodes = len(self.builder.knowledge_graph.nodes)
        total_edges = sum(len(edges) for edges in self.builder.knowledge_graph.edges.values()) // 2
        
        print(f"  - 节点数: {total_nodes}")
        print(f"  - 边数: {total_edges}")
        print(f"  - 平均连接度: {total_edges * 2 / total_nodes:.2f}")
        
        # 显示一些关系示例
        print("\n关系示例:")
        relationship_count = 0
        for node_id, edges in self.builder.knowledge_graph.edges.items():
            if relationship_count >= 3:  # 只显示3个示例
                break
            
            node = self.builder.knowledge_graph.nodes[node_id]
            print(f"\n📄 {node.metadata.title}")
            
            # 显示相关知识
            related_items = []
            for related_id, weight in edges.items():
                related_node = self.builder.knowledge_graph.nodes[related_id]
                related_items.append((related_node.metadata.title, weight))
            
            # 按权重排序并显示前3个
            related_items.sort(key=lambda x: x[1], reverse=True)
            for title, weight in related_items[:3]:
                print(f"  🔗 {title} (权重: {weight:.2f})")
            
            relationship_count += 1
    
    async def demo_quality_assessment(self):
        """演示质量评估"""
        print("\n⭐ 4. 知识质量评估演示")
        print("-" * 40)
        
        if not hasattr(self, 'builder'):
            print("⚠️ 需要先运行知识库构建")
            return
        
        # 质量分布统计
        quality_ranges = {
            '优秀 (>0.8)': 0,
            '良好 (0.6-0.8)': 0,
            '待改进 (<0.6)': 0
        }
        
        quality_scores = []
        for node in self.builder.knowledge_graph.nodes.values():
            score = node.metadata.quality_score
            quality_scores.append(score)
            
            if score > 0.8:
                quality_ranges['优秀 (>0.8)'] += 1
            elif score >= 0.6:
                quality_ranges['良好 (0.6-0.8)'] += 1
            else:
                quality_ranges['待改进 (<0.6)'] += 1
        
        print("质量分布:")
        for range_name, count in quality_ranges.items():
            percentage = count / len(quality_scores) * 100 if quality_scores else 0
            print(f"  {range_name}: {count} 项 ({percentage:.1f}%)")
        
        # 显示质量最高的知识项
        print("\n质量最高的知识项:")
        sorted_nodes = sorted(
            self.builder.knowledge_graph.nodes.values(),
            key=lambda x: x.metadata.quality_score,
            reverse=True
        )
        
        for i, node in enumerate(sorted_nodes[:3]):
            print(f"  {i+1}. {node.metadata.title} (质量: {node.metadata.quality_score:.3f})")
            
            # 显示质量评估详情
            validation = node.validation_results
            if validation:
                print(f"     验证通过: {'✅' if validation.get('passed_checks', False) else '❌'}")
    
    async def demo_agentic_optimization(self):
        """演示Agentic优化特性"""
        print("\n🧠 5. Agentic优化特性演示")
        print("-" * 40)
        
        if not hasattr(self, 'builder'):
            print("⚠️ 需要先运行知识库构建")
            return
        
        # 演示针对不同查询复杂度的优化
        complexity_scenarios = [
            {
                'query': '什么是FPGA',
                'complexity': 'SIMPLE',
                'description': '简单概念查询',
                'expected_types': ['concept', 'reference'],
                'max_chunks': 2
            },
            {
                'query': '如何设计一个计数器模块',
                'complexity': 'MODERATE',
                'description': '中等复杂度设计查询',
                'expected_types': ['pattern', 'example'],
                'max_chunks': 4
            },
            {
                'query': '分析FPGA时序优化策略并提供最佳实践',
                'complexity': 'COMPLEX',
                'description': '复杂分析查询',
                'expected_types': ['best_practice', 'troubleshooting'],
                'max_chunks': 8
            }
        ]
        
        for scenario in complexity_scenarios:
            print(f"\n场景: {scenario['description']}")
            print(f"查询: {scenario['query']}")
            print(f"复杂度: {scenario['complexity']}")
            
            # 模拟Agentic优化选择
            optimized_items = await self._agentic_knowledge_selection(
                scenario['query'],
                scenario['expected_types'],
                scenario['max_chunks']
            )
            
            print(f"优化选择结果 ({len(optimized_items)} 项):")
            for item in optimized_items:
                print(f"  📚 {item['title']}")
                print(f"     类型: {item['type']}, 块数: {item['chunks']}")
        
        # 演示多跳推理支持
        print(f"\n🔄 多跳推理演示:")
        await self._demo_multi_hop_reasoning()
    
    async def _agentic_knowledge_selection(self, query: str, preferred_types: list, max_chunks: int) -> list:
        """模拟Agentic知识选择优化"""
        selected_items = []
        
        # 首先找到相关知识
        relevant_items = await self._find_relevant_knowledge(query)
        
        # 按类型偏好和块数限制进行优化选择
        for item in relevant_items:
            if len(selected_items) >= 5:  # 限制返回数量
                break
                
            node = item['node']
            
            # 类型匹配加分
            type_bonus = 0.2 if node.metadata.knowledge_type.value in preferred_types else 0.0
            
            # 计算优化后的相关性
            optimized_relevance = item['relevance'] + type_bonus
            
            # 选择合适数量的块
            selected_chunks = min(len(node.chunks), max_chunks)
            
            selected_items.append({
                'title': node.metadata.title,
                'type': node.metadata.knowledge_type.value,
                'chunks': selected_chunks,
                'optimized_relevance': optimized_relevance
            })
        
        # 按优化后的相关性排序
        selected_items.sort(key=lambda x: x['optimized_relevance'], reverse=True)
        return selected_items
    
    async def _demo_multi_hop_reasoning(self):
        """演示多跳推理"""
        print("从 'FPGA基础概念' 开始的知识路径:")
        
        # 找到起始节点
        start_node = None
        for node in self.builder.knowledge_graph.nodes.values():
            if 'FPGA基础概念' in node.metadata.title:
                start_node = node
                break
        
        if not start_node:
            print("  未找到起始节点")
            return
        
        # 执行多跳遍历
        visited = set()
        current_level = [(start_node.metadata.id, start_node.metadata.title, 0)]
        max_hops = 2
        
        while current_level and max_hops > 0:
            next_level = []
            
            for node_id, title, hop in current_level:
                if node_id in visited:
                    continue
                
                visited.add(node_id)
                print(f"  {'  ' * hop}🔗 {title} (跳数: {hop})")
                
                # 找到相关节点
                if node_id in self.builder.knowledge_graph.edges:
                    for related_id, weight in self.builder.knowledge_graph.edges[node_id].items():
                        if related_id not in visited and weight > 0.7:  # 高权重关系
                            related_node = self.builder.knowledge_graph.nodes[related_id]
                            next_level.append((related_id, related_node.metadata.title, hop + 1))
                
                if len(next_level) >= 3:  # 限制每层的节点数
                    break
            
            current_level = next_level[:3]  # 只保留前3个
            max_hops -= 1
    
    def cleanup(self):
        """清理演示文件"""
        import shutil
        if self.demo_path.exists():
            shutil.rmtree(self.demo_path)
            print(f"🗑️  清理演示文件: {self.demo_path}")


async def main():
    """主函数"""
    demo = AgenticKnowledgeDemo()
    
    try:
        await demo.run_complete_demo()
        
        # 询问是否清理
        print("\n" + "="*60)
        cleanup = input("是否清理演示文件? (y/N): ").strip().lower()
        if cleanup == 'y':
            demo.cleanup()
        else:
            print(f"演示文件保留在: {demo.demo_path.absolute()}")
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        logger.error(f"演示失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 