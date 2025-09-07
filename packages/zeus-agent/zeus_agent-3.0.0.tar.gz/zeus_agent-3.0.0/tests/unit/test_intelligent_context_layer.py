#!/usr/bin/env python3
"""
智能上下文层基础测试

测试智能上下文层的四大核心组件功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layers.intelligent_context import IntelligentContextLayer
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.task import UniversalTask, TaskPriority


async def test_intelligent_context_layer():
    """测试智能上下文层基础功能"""
    
    print("🧩 开始测试智能上下文层...")
    
    # 1. 初始化智能上下文层
    print("\n1. 初始化智能上下文层")
    config = {
        'processing_mode': 'sequential',
        'context_engineering': {'enable_failure_detection': True},
        'rag_system': {'retrieval_strategy': 'semantic'},
        'knowledge_management': {'storage_type': 'vector_db'},
        'quality_control': {'quality_threshold': 0.7}
    }
    
    intelligent_context_layer = IntelligentContextLayer(config)
    print("✅ 智能上下文层初始化完成")
    
    # 2. 创建测试上下文
    print("\n2. 创建测试上下文")
    test_context = UniversalContext({
        'instructions': 'Complete the AI agent development task',
        'user_prompt': 'Implement the intelligent context layer',
        'state_history': ['Started project', 'Designed architecture'],
        'long_term_memory': {'project_goals': 'Build ADC framework'},
        'retrieved_info': 'Context engineering best practices',
        'available_tools': ['code_generator', 'documentation_tool']
    })
    test_context.set('context_id', 'test_context_001')
    test_context.set('created_at', '2025-08-22T10:00:00Z')
    test_context.set('priority', 'high')
    print("✅ 测试上下文创建完成")
    
    # 3. 创建测试任务
    print("\n3. 创建测试任务")
    test_task = UniversalTask(
        task_id="task_001",
        requirements=['Implement context engineering', 'Add RAG system', 'Ensure quality control'],
        priority=TaskPriority.HIGH,
        data={'task_type': 'development', 'complexity': 'high'},
        metadata={'assigned_to': 'intelligent_context_layer'}
    )
    print("✅ 测试任务创建完成")
    
    # 4. 执行智能上下文处理
    print("\n4. 执行智能上下文处理...")
    try:
        result = await intelligent_context_layer.process_context(test_context, test_task)
        
        print(f"✅ 处理完成！")
        print(f"   - 原始上下文ID: {result.original_context.get('context_id', 'unknown')}")
        print(f"   - 最终上下文ID: {result.quality_controlled_context.get('context_id', 'unknown')}")
        print(f"   - 处理时间: {result.processing_time:.3f}秒")
        print(f"   - 指标数量: {len(result.metrics)}")
        
        # 显示处理结果
        print(f"\n📊 处理指标:")
        for key, value in result.metrics.get('overall_metrics', {}).items():
            print(f"   - {key}: {value}")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False
    
    # 5. 测试组件状态
    print("\n5. 检查组件状态")
    status = intelligent_context_layer.get_status()
    print(f"✅ 层状态: {status['layer_name']}")
    print(f"   - 处理模式: {status['processing_mode']}")
    print(f"   - 已处理总数: {status['metrics']['total_processed']}")
    print(f"   - 平均处理时间: {status['metrics']['average_processing_time']:.3f}秒")
    print(f"   - 质量评分: {status['metrics']['quality_score']:.3f}")
    print(f"   - 效率评分: {status['metrics']['efficiency_score']:.3f}")
    
    # 6. 测试不同处理模式
    print("\n6. 测试并行处理模式")
    intelligent_context_layer.configure({'processing_mode': 'parallel'})
    
    try:
        parallel_result = await intelligent_context_layer.process_context(test_context, test_task)
        print(f"✅ 并行处理完成，处理时间: {parallel_result.processing_time:.3f}秒")
    except Exception as e:
        print(f"❌ 并行处理失败: {e}")
    
    # 7. 测试自适应处理模式
    print("\n7. 测试自适应处理模式")
    intelligent_context_layer.configure({'processing_mode': 'adaptive'})
    
    try:
        adaptive_result = await intelligent_context_layer.process_context(test_context, test_task)
        print(f"✅ 自适应处理完成，处理时间: {adaptive_result.processing_time:.3f}秒")
    except Exception as e:
        print(f"❌ 自适应处理失败: {e}")
    
    print("\n🎉 智能上下文层测试完成！")
    return True


async def test_individual_components():
    """测试各个组件的独立功能"""
    
    print("\n🔧 开始测试各个组件...")
    
    # 导入各个组件
    from layers.intelligent_context.context_engineering import ContextEngineering
    from layers.intelligent_context.rag_system import RAGSystem
    from layers.intelligent_context.knowledge_management import KnowledgeManagement
    from layers.intelligent_context.quality_control import QualityControl
    
    # 创建测试数据
    test_context = UniversalContext({
        'test': 'data', 
        'instructions': 'test instructions'
    })
    test_context.set('context_id', 'component_test_context')
    
    test_task = UniversalTask(
        task_id="component_test_task",
        requirements=['test requirement'],
        priority=TaskPriority.MEDIUM,
        data={},
        metadata={}
    )
    
    # 1. 测试上下文工程
    print("\n1. 测试上下文工程组件")
    try:
        context_engineering = ContextEngineering()
        engineered_context = await context_engineering.engineer_context(test_context, test_task)
        print(f"✅ 上下文工程完成: {engineered_context.get('context_id', 'unknown')}")
        print(f"   - 指标: {context_engineering.get_metrics()}")
    except Exception as e:
        print(f"❌ 上下文工程失败: {e}")
    
    # 2. 测试RAG系统
    print("\n2. 测试RAG系统组件")
    try:
        rag_system = RAGSystem()
        rag_enhanced_context = await rag_system.enhance_with_rag(test_context, test_task)
        print(f"✅ RAG增强完成: {rag_enhanced_context.get('context_id', 'unknown')}")
        print(f"   - 指标: {rag_system.get_metrics()}")
    except Exception as e:
        print(f"❌ RAG增强失败: {e}")
    
    # 3. 测试知识管理
    print("\n3. 测试知识管理组件")
    try:
        knowledge_management = KnowledgeManagement()
        managed_context = await knowledge_management.manage_knowledge(test_context, test_task)
        print(f"✅ 知识管理完成: {managed_context.get('context_id', 'unknown')}")
        print(f"   - 指标: {knowledge_management.get_metrics()}")
    except Exception as e:
        print(f"❌ 知识管理失败: {e}")
    
    # 4. 测试质量控制
    print("\n4. 测试质量控制组件")
    try:
        quality_control = QualityControl()
        controlled_context = await quality_control.control_quality(test_context, test_task)
        print(f"✅ 质量控制完成: {controlled_context.get('context_id', 'unknown')}")
        print(f"   - 指标: {quality_control.get_metrics()}")
    except Exception as e:
        print(f"❌ 质量控制失败: {e}")
    
    print("\n🎉 各组件测试完成！")


async def main():
    """主测试函数"""
    
    print("=" * 60)
    print("🚀 ADC智能上下文层测试")
    print("=" * 60)
    
    # 测试智能上下文层整体功能
    success = await test_intelligent_context_layer()
    
    if success:
        # 测试各个组件的独立功能
        await test_individual_components()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 