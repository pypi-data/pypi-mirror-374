#!/usr/bin/env python3
"""
ADC平台新架构演示
展示装饰器系统、KnowledgeBasedAgent和配置驱动开发
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from layers.framework.abstractions.decorators import (
    capability, knowledge_enhanced, context_aware,
    CapabilityType, KnowledgeDomain,
    list_all_capabilities, get_capability_metadata
)
from layers.infrastructure.config.yaml_config_manager import (
    YAMLConfigManager, load_agent_config
)


async def test_decorators():
    """测试装饰器系统"""
    print("🎭 测试装饰器系统")
    print("=" * 40)
    
    # 创建一个测试类
    class TestAgent:
        def __init__(self):
            self.enhanced_context = None
            self.current_context = None
        
        @capability(
            name="test_capability",
            capability_type=CapabilityType.GENERATION,
            description="测试能力",
            confidence_threshold=0.8
        )
        async def test_method(self, input_text: str) -> str:
            """测试方法"""
            return f"处理结果: {input_text}"
        
        @knowledge_enhanced(
            domains=[KnowledgeDomain.FPGA],
            retrieval_count=3
        )
        async def knowledge_method(self, query: str) -> str:
            """知识增强方法"""
            enhanced = getattr(self, 'enhanced_context', [])
            if enhanced is None:
                enhanced = []
            return f"知识增强处理: {query}, 增强项: {len(enhanced)}"
        
        @context_aware(
            enable_conversation_history=True,
            history_window_size=5
        )
        async def context_method(self, message: str) -> str:
            """上下文感知方法"""
            context = getattr(self, 'current_context', {})
            if context is None:
                context = {}
            return f"上下文处理: {message}, 上下文: {len(context)}"
    
    # 测试装饰器
    agent = TestAgent()
    
    print("📋 测试能力装饰器:")
    result = await agent.test_method("hello world")
    print(f"   结果: {result}")
    
    print("\n🧠 测试知识增强装饰器:")
    result = await agent.knowledge_method("FPGA设计问题")
    print(f"   结果: {result}")
    
    print("\n🎯 测试上下文感知装饰器:")
    result = await agent.context_method("需要上下文的消息")
    print(f"   结果: {result}")
    
    print("\n📊 能力注册表:")
    capabilities = list_all_capabilities()
    for name, metadata in capabilities.items():
        print(f"   - {name}: {metadata.description} ({metadata.capability_type.value})")


async def test_config_manager():
    """测试配置管理器"""
    print("\n🔧 测试配置管理器")
    print("=" * 40)
    
    try:
        # 创建配置管理器
        config_manager = YAMLConfigManager("./config")
        
        print("📋 可用配置:")
        configs = config_manager.list_configs()
        for config in configs:
            print(f"   - {config}")
        
        # 测试加载配置
        if "ares" in configs:
            print("\n📖 加载Ares配置:")
            ares_config = config_manager.load_config("ares", "development")
            
            print(f"   Agent名称: {ares_config.get('agent', {}).get('name')}")
            print(f"   版本: {ares_config.get('agent', {}).get('version')}")
            print(f"   AI后端: {ares_config.get('ai_backend', {}).get('provider')}")
            print(f"   能力数量: {len(ares_config.get('capabilities', {}))}")
            
            # 测试元数据
            metadata = config_manager.get_config_metadata("ares")
            if metadata:
                print(f"   配置元数据: {metadata.name} v{metadata.version}")
        
        # 测试缓存统计
        print(f"\n📊 缓存统计:")
        cache_stats = config_manager.get_cache_stats()
        for key, value in cache_stats.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")


async def test_integration():
    """测试集成功能"""
    print("\n🔗 测试集成功能")
    print("=" * 40)
    
    try:
        # 测试配置加载便利函数
        print("📖 使用便利函数加载配置:")
        config = load_agent_config("ares", "development")
        
        agent_info = config.get('agent', {})
        print(f"   名称: {agent_info.get('name', 'Unknown')}")
        print(f"   描述: {agent_info.get('description', 'No description')}")
        
        # 显示知识库配置
        kb_config = agent_info.get('knowledge_base', {})
        print(f"   知识库路径: {kb_config.get('path', 'Not set')}")
        print(f"   知识增强: {kb_config.get('enable_knowledge_enhancement', False)}")
        
        # 显示能力配置
        capabilities = config.get('capabilities', {})
        print(f"   配置的能力领域: {list(capabilities.keys())}")
        
        print("✅ 集成测试通过!")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 ADC平台新架构演示")
    print("展示装饰器系统、配置管理和集成功能")
    print("=" * 60)
    
    # 运行测试
    await test_decorators()
    await test_config_manager()
    await test_integration()
    
    print("\n🎉 演示完成!")
    print("\n💡 新架构特性:")
    print("   ✅ 装饰器驱动的能力系统")
    print("   ✅ YAML配置驱动开发")
    print("   ✅ 知识库优先架构")
    print("   ✅ 自动能力发现和注册")
    print("   ✅ 环境变量支持")
    print("   ✅ 配置缓存和热重载")


if __name__ == "__main__":
    asyncio.run(main()) 