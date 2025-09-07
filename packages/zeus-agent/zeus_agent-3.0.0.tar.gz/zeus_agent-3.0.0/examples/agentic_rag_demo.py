#!/usr/bin/env python3
"""
Agentic RAG系统使用示例

展示如何配置和使用Zeus架构中的Agentic RAG系统
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.intelligent_context import (
    IntelligentContextLayer, 
    RAGProcessingMode,
    AGENTIC_RAG_AVAILABLE
)

class AgenticRAGDemo:
    """Agentic RAG系统演示"""
    
    def __init__(self):
        # 配置Agentic RAG系统
        self.agentic_config = {
            'rag_processing_mode': 'agentic',
            'processing_mode': 'sequential',
            'agentic_rag': {
                'max_iterations': 3,
                'quality_threshold': 0.8,
                'enable_reflection': True,
                'enable_planning': True,
                'enable_learning': True,
                'reflection': {
                    'quality_threshold': 0.8,
                    'relevance_weight': 0.3,
                    'accuracy_weight': 0.25,
                    'completeness_weight': 0.25,
                    'clarity_weight': 0.2
                },
                'planning': {
                    'max_iterations': 5,
                    'default_quality_threshold': 0.8,
                    'enable_adaptive_planning': True
                }
            }
        }
        
        # 传统RAG配置（对比用）
        self.traditional_config = {
            'rag_processing_mode': 'traditional',
            'processing_mode': 'sequential'
        }
    
    async def demo_simple_query(self):
        """演示简单查询处理"""
        print("\n" + "="*60)
        print("🔍 简单查询演示")
        print("="*60)
        
        # 创建简单查询任务
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'demo_session_001'
        })
        
        task = UniversalTask(
            content="什么是FPGA？",
            task_type=TaskType.CONVERSATION
        )
        
        if AGENTIC_RAG_AVAILABLE:
            # 使用Agentic RAG处理
            print("📊 使用Agentic RAG处理...")
            agentic_layer = IntelligentContextLayer(self.agentic_config)
            agentic_result = await agentic_layer.process_context(context, task)
            
            print(f"✅ Agentic RAG结果:")
            print(f"   处理时间: {agentic_result.processing_time:.3f}s")
            print(f"   质量评估: {agentic_result.quality_controlled_context.get('quality_assessment', {}).get('overall_score', 'N/A')}")
            
            # 显示Agentic特有信息
            agentic_metadata = agentic_result.quality_controlled_context.get('quality_assessment', {}).get('agentic_metadata', {})
            if agentic_metadata:
                print(f"   迭代次数: {agentic_metadata.get('iterations_used', 'N/A')}")
                print(f"   置信度: {agentic_metadata.get('confidence', 'N/A'):.3f}")
                print(f"   质量维度: {agentic_metadata.get('quality_dimensions', {})}")
        else:
            print("⚠️ Agentic RAG不可用，跳过演示")
        
        # 使用传统RAG处理（对比）
        print("\n📊 使用传统RAG处理（对比）...")
        traditional_layer = IntelligentContextLayer(self.traditional_config)
        traditional_result = await traditional_layer.process_context(context, task)
        
        print(f"✅ 传统RAG结果:")
        print(f"   处理时间: {traditional_result.processing_time:.3f}s")
        print(f"   质量评估: {traditional_result.quality_controlled_context.get('quality_assessment', {}).get('overall_score', 'N/A')}")
    
    async def demo_complex_query(self):
        """演示复杂查询处理"""
        print("\n" + "="*60)
        print("🧠 复杂查询演示（多跳推理）")
        print("="*60)
        
        # 创建复杂查询任务
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'demo_session_002',
            'domain': 'fpga_design',
            'expertise_level': 'intermediate'
        })
        
        task = UniversalTask(
            content="比较FPGA和ASIC的设计流程，分析它们在时序约束和优化方面的区别",
            task_type=TaskType.ANALYSIS
        )
        
        if AGENTIC_RAG_AVAILABLE:
            print("📊 使用Agentic RAG处理复杂查询...")
            agentic_layer = IntelligentContextLayer(self.agentic_config)
            
            start_time = datetime.now()
            agentic_result = await agentic_layer.process_context(context, task)
            end_time = datetime.now()
            
            print(f"✅ Agentic RAG复杂查询结果:")
            print(f"   总处理时间: {(end_time - start_time).total_seconds():.3f}s")
            print(f"   系统处理时间: {agentic_result.processing_time:.3f}s")
            
            # 详细的Agentic信息
            quality_assessment = agentic_result.quality_controlled_context.get('quality_assessment', {})
            print(f"   质量评估: {quality_assessment.get('overall_score', 'N/A')}")
            
            agentic_metadata = quality_assessment.get('agentic_metadata', {})
            if agentic_metadata:
                print(f"   迭代次数: {agentic_metadata.get('iterations_used', 'N/A')}")
                print(f"   置信度: {agentic_metadata.get('confidence', 'N/A'):.3f}")
                print(f"   源文档数: {agentic_metadata.get('sources_count', 'N/A')}")
                
                quality_dims = agentic_metadata.get('quality_dimensions', {})
                if quality_dims:
                    print("   质量维度详情:")
                    for dim, score in quality_dims.items():
                        print(f"     {dim}: {score:.3f}")
            
            # 显示生成的内容片段
            rag_content = agentic_result.rag_enhanced_context.get('rag_enhanced_content', '')
            if rag_content:
                print(f"   生成内容预览: {rag_content[:200]}...")
        else:
            print("⚠️ Agentic RAG不可用，跳过复杂查询演示")
    
    async def demo_creative_query(self):
        """演示创造性查询处理"""
        print("\n" + "="*60)
        print("🎨 创造性查询演示")
        print("="*60)
        
        # 创建创造性查询任务
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'demo_session_003',
            'domain': 'fpga_design',
            'task_context': 'design_assistance',
            'output_requirements': {
                'format': 'code',
                'language': 'verilog',
                'complexity': 'intermediate'
            }
        })
        
        task = UniversalTask(
            content="设计一个FPGA上的高性能计数器模块，包含异步复位、使能控制和溢出检测功能",
            task_type=TaskType.GENERATION
        )
        
        if AGENTIC_RAG_AVAILABLE:
            print("📊 使用Agentic RAG处理创造性任务...")
            
            # 使用更高的迭代次数配置用于创造性任务
            creative_config = self.agentic_config.copy()
            creative_config['agentic_rag']['max_iterations'] = 5
            creative_config['agentic_rag']['quality_threshold'] = 0.85
            
            agentic_layer = IntelligentContextLayer(creative_config)
            
            start_time = datetime.now()
            agentic_result = await agentic_layer.process_context(context, task)
            end_time = datetime.now()
            
            print(f"✅ Agentic RAG创造性任务结果:")
            print(f"   总处理时间: {(end_time - start_time).total_seconds():.3f}s")
            
            # 获取质量评估信息
            quality_assessment = agentic_result.quality_controlled_context.get('quality_assessment', {})
            agentic_metadata = quality_assessment.get('agentic_metadata', {})
            
            if agentic_metadata:
                print(f"   迭代次数: {agentic_metadata.get('iterations_used', 'N/A')}")
                print(f"   最终置信度: {agentic_metadata.get('confidence', 'N/A'):.3f}")
                
                # 显示质量维度
                quality_dims = agentic_metadata.get('quality_dimensions', {})
                if quality_dims:
                    print("   创造性任务质量评估:")
                    for dim, score in quality_dims.items():
                        status = "✓" if score >= 0.7 else "⚠"
                        print(f"     {status} {dim}: {score:.3f}")
            
            # 显示生成内容
            rag_content = agentic_result.rag_enhanced_context.get('rag_enhanced_content', '')
            if rag_content:
                print(f"\n   生成的内容:")
                print(f"   {'-'*40}")
                print(f"   {rag_content[:300]}...")
                print(f"   {'-'*40}")
        else:
            print("⚠️ Agentic RAG不可用，跳过创造性查询演示")
    
    async def demo_performance_comparison(self):
        """演示性能对比"""
        print("\n" + "="*60)
        print("📈 性能对比演示")
        print("="*60)
        
        test_queries = [
            "FPGA的基本概念",
            "如何优化FPGA设计的时序性能",
            "设计一个简单的状态机"
        ]
        
        results = {
            'traditional': {'times': [], 'qualities': []},
            'agentic': {'times': [], 'qualities': []}
        }
        
        for i, query in enumerate(test_queries):
            print(f"\n测试查询 {i+1}: {query}")
            
            context = UniversalContext({'test_id': f'perf_test_{i+1}'})
            task = UniversalTask(content=query, task_type=TaskType.CONVERSATION)
            
            # 传统RAG测试
            traditional_layer = IntelligentContextLayer(self.traditional_config)
            traditional_result = await traditional_layer.process_context(context, task)
            
            traditional_quality = traditional_result.quality_controlled_context.get(
                'quality_assessment', {}
            ).get('overall_score', 0.0)
            
            results['traditional']['times'].append(traditional_result.processing_time)
            results['traditional']['qualities'].append(traditional_quality)
            
            print(f"   传统RAG: {traditional_result.processing_time:.3f}s, 质量: {traditional_quality:.3f}")
            
            # Agentic RAG测试（如果可用）
            if AGENTIC_RAG_AVAILABLE:
                agentic_layer = IntelligentContextLayer(self.agentic_config)
                agentic_result = await agentic_layer.process_context(context, task)
                
                agentic_quality = agentic_result.quality_controlled_context.get(
                    'quality_assessment', {}
                ).get('overall_score', 0.0)
                
                results['agentic']['times'].append(agentic_result.processing_time)
                results['agentic']['qualities'].append(agentic_quality)
                
                agentic_metadata = agentic_result.quality_controlled_context.get(
                    'quality_assessment', {}
                ).get('agentic_metadata', {})
                
                iterations = agentic_metadata.get('iterations_used', 'N/A')
                confidence = agentic_metadata.get('confidence', 0.0)
                
                print(f"   Agentic RAG: {agentic_result.processing_time:.3f}s, 质量: {agentic_quality:.3f}, 迭代: {iterations}, 置信度: {confidence:.3f}")
            else:
                print("   Agentic RAG: 不可用")
        
        # 显示总结
        print(f"\n📊 性能总结:")
        print(f"传统RAG - 平均时间: {sum(results['traditional']['times'])/len(results['traditional']['times']):.3f}s, "
              f"平均质量: {sum(results['traditional']['qualities'])/len(results['traditional']['qualities']):.3f}")
        
        if AGENTIC_RAG_AVAILABLE and results['agentic']['times']:
            print(f"Agentic RAG - 平均时间: {sum(results['agentic']['times'])/len(results['agentic']['times']):.3f}s, "
                  f"平均质量: {sum(results['agentic']['qualities'])/len(results['agentic']['qualities']):.3f}")
    
    async def demo_mode_switching(self):
        """演示动态模式切换"""
        print("\n" + "="*60)
        print("🔄 动态模式切换演示")
        print("="*60)
        
        if not AGENTIC_RAG_AVAILABLE:
            print("⚠️ Agentic RAG不可用，跳过模式切换演示")
            return
        
        # 创建智能上下文层实例
        context_layer = IntelligentContextLayer(self.traditional_config)
        
        print(f"初始模式: {context_layer.rag_processing_mode.value}")
        print(f"支持的模式: {context_layer.get_supported_rag_modes()}")
        
        # 切换到Agentic模式
        print("\n🔄 切换到Agentic模式...")
        await context_layer.switch_rag_mode(RAGProcessingMode.AGENTIC)
        print(f"当前模式: {context_layer.rag_processing_mode.value}")
        
        # 测试Agentic模式
        context = UniversalContext({'test': 'mode_switch'})
        task = UniversalTask(content="测试模式切换", task_type=TaskType.CONVERSATION)
        
        result = await context_layer.process_context(context, task)
        print(f"Agentic模式处理结果: 质量={result.quality_controlled_context.get('quality_assessment', {}).get('overall_score', 'N/A')}")
        
        # 切换回传统模式
        print("\n🔄 切换回传统模式...")
        await context_layer.switch_rag_mode(RAGProcessingMode.TRADITIONAL)
        print(f"当前模式: {context_layer.rag_processing_mode.value}")
        
        # 测试传统模式
        result = await context_layer.process_context(context, task)
        print(f"传统模式处理结果: 质量={result.quality_controlled_context.get('quality_assessment', {}).get('overall_score', 'N/A')}")
    
    async def run_all_demos(self):
        """运行所有演示"""
        print("🚀 Agentic RAG系统演示开始")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Agentic RAG可用性: {'✅ 可用' if AGENTIC_RAG_AVAILABLE else '❌ 不可用'}")
        
        try:
            await self.demo_simple_query()
            await self.demo_complex_query()
            await self.demo_creative_query()
            await self.demo_performance_comparison()
            await self.demo_mode_switching()
            
            print("\n" + "="*60)
            print("🎉 所有演示完成！")
            print("="*60)
            
        except Exception as e:
            logger.error(f"演示过程中出现错误: {e}", exc_info=True)
            print(f"\n❌ 演示失败: {e}")


async def main():
    """主函数"""
    demo = AgenticRAGDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main()) 