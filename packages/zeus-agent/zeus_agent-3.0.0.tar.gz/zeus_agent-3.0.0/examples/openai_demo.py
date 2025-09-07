#!/usr/bin/env python3
"""
OpenAI Adapter Demo
演示OpenAI适配器的使用
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from layers.adapter.openai.adapter import OpenAIAdapter
from layers.adapter.openai.agent_wrapper import OpenAIAgentWrapper
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.agent import AgentCapability


async def main():
    """主演示函数"""
    print("🚀 OpenAI Adapter Demo")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    try:
        # 1. 创建和初始化OpenAI适配器
        print("\n1️⃣ 初始化OpenAI适配器...")
        adapter = OpenAIAdapter("openai-demo")
        
        config = {
            "api_key": api_key,
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        await adapter.initialize(config)
        print(f"✅ 适配器初始化成功")
        print(f"   框架: {adapter.get_framework_name()} v{adapter.get_framework_version()}")
        print(f"   能力: {[cap.value for cap in adapter.get_framework_capabilities()]}")
        
        # 2. 测试基础对话功能
        print("\n2️⃣ 测试基础对话...")
        task = UniversalTask(
            content="Hello! Please introduce yourself briefly.",
            task_type=TaskType.CONVERSATION
        )
        
        context = UniversalContext()
        result = await adapter.execute_task(task, context)
        
        if result.is_successful():
            print(f"✅ 对话成功")
            print(f"   回复: {result.content}")
            if result.metadata and result.metadata.token_usage:
                print(f"   Token使用: {result.metadata.token_usage}")
        else:
            print(f"❌ 对话失败: {result.error.error_message if result.error else 'Unknown error'}")
        
        # 3. 测试代码生成功能
        print("\n3️⃣ 测试代码生成...")
        code_task = UniversalTask(
            content="Create a simple Python function to calculate fibonacci numbers",
            task_type=TaskType.CODE_GENERATION
        )
        
        code_context = UniversalContext()
        code_context.set("language", "python")
        
        code_result = await adapter.execute_task(code_task, code_context)
        
        if code_result.is_successful() and isinstance(code_result.content, dict):
            print(f"✅ 代码生成成功")
            print(f"   代码:\n{code_result.content.get('code', 'No code generated')}")
            print(f"   说明: {code_result.content.get('explanation', 'No explanation')}")
        else:
            print(f"❌ 代码生成失败: {code_result.error.error_message if code_result.error else 'Unknown error'}")
        
        # 4. 测试Agent包装器
        print("\n4️⃣ 测试Agent包装器...")
        agent = OpenAIAgentWrapper(
            name="OpenAI Assistant",
            adapter=adapter,
            description="A helpful AI assistant powered by OpenAI",
            capabilities=[
                AgentCapability.CONVERSATION,
                AgentCapability.CODE_GENERATION,
                AgentCapability.REASONING
            ],
            config={
                "system_message": "You are a helpful and friendly AI assistant.",
                "model_config": "default"
            }
        )
        
        # 测试简化的聊天接口
        response = await agent.chat("What's the weather like today?")
        print(f"✅ Agent聊天测试")
        print(f"   用户: What's the weather like today?")
        print(f"   助手: {response}")
        
        # 测试代码生成接口
        code_result = await agent.generate_code("Create a function to sort a list", "python")
        print(f"✅ Agent代码生成测试")
        print(f"   请求: Create a function to sort a list")
        if not code_result.get("error"):
            print(f"   生成的代码:\n{code_result.get('code', 'No code')}")
        else:
            print(f"   错误: {code_result.get('explanation', 'Unknown error')}")
        
        # 5. 显示性能统计
        print("\n5️⃣ 性能统计")
        adapter_info = adapter.get_info()
        print(f"   适配器状态: {adapter_info.status.value}")
        print(f"   成功操作: {adapter.metadata.successful_operations}")
        print(f"   失败操作: {adapter.metadata.failed_operations}")
        print(f"   成功率: {adapter.metadata.success_rate:.2%}")
        
        agent_metrics = agent.get_performance_metrics()
        print(f"   Agent总任务: {agent_metrics['total_tasks']}")
        print(f"   Agent成功任务: {agent_metrics['successful_tasks']}")
        print(f"   Agent成功率: {agent_metrics['success_rate']:.2%}")
        print(f"   平均响应时间: {agent_metrics['average_response_time']:.2f}s")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        if 'adapter' in locals():
            adapter.cleanup()
            print("\n🧹 资源清理完成")


if __name__ == "__main__":
    print("请确保设置了OPENAI_API_KEY环境变量")
    print("运行命令: export OPENAI_API_KEY='your-api-key-here'")
    print()
    
    asyncio.run(main()) 