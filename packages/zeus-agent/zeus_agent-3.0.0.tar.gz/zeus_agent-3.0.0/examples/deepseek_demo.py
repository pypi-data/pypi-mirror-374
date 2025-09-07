"""
DeepSeek适配器使用示例
演示如何使用DeepSeek API进行Agent开发
"""

import asyncio
import os
from datetime import datetime

# 导入我们的框架组件
from layers.adapter.deepseek import create_deepseek_adapter
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.cognitive.cognitive_agent import CognitiveAgent, AgentIdentity


async def basic_deepseek_demo():
    """基础DeepSeek API使用示例"""
    
    print("🚀 DeepSeek适配器基础演示")
    print("=" * 50)
    
    # 1. 创建DeepSeek适配器
    api_key = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    
    if api_key == 'your_api_key_here':
        print("⚠️  请设置 DEEPSEEK_API_KEY 环境变量")
        print("   export DEEPSEEK_API_KEY='your_actual_api_key'")
        return
    
    adapter = create_deepseek_adapter(
        api_key=api_key,
        model="deepseek-chat",
        temperature=0.7
    )
    
    # 2. 初始化适配器
    print("🔧 初始化DeepSeek适配器...")
    success = await adapter.initialize()
    
    if not success:
        print("❌ 适配器初始化失败")
        return
    
    print("✅ 适配器初始化成功")
    print(f"📊 适配器状态: {adapter.get_status_info()}")
    
    # 3. 创建简单任务
    tasks = [
        UniversalTask(
            content="你好，请介绍一下你自己",
            task_type=TaskType.CONVERSATION
        ),
        UniversalTask(
            content="请用Python写一个计算斐波那契数列的函数",
            task_type=TaskType.CODE_GENERATION
        ),
        UniversalTask(
            content="解释一下什么是机器学习",
            task_type=TaskType.QUESTION_ANSWERING
        )
    ]
    
    # 4. 执行任务
    context = UniversalContext()
    
    for i, task in enumerate(tasks, 1):
        print(f"\n📝 任务 {i}: {task.content}")
        print("-" * 40)
        
        try:
            start_time = datetime.now()
            result = await adapter.execute(task, context)
            end_time = datetime.now()
            
            if result.status.value == "success":
                print(f"✅ 执行成功")
                print(f"📄 回答: {result.content[:200]}...")
                print(f"⏱️  执行时间: {(end_time - start_time).total_seconds():.2f}秒")
                
                if 'total_tokens' in result.metadata:
                    print(f"🔢 Token使用: {result.metadata['total_tokens']}")
                    
            else:
                print(f"❌ 执行失败: {result.content}")
                
        except Exception as e:
            print(f"💥 执行异常: {str(e)}")
    
    print(f"\n📊 最终适配器状态:")
    status_info = adapter.get_status_info()
    for key, value in status_info.items():
        print(f"   {key}: {value}")


async def cognitive_agent_with_deepseek():
    """使用DeepSeek的认知Agent示例"""
    
    print("\n🧠 认知Agent + DeepSeek演示")
    print("=" * 50)
    
    # 1. 创建Agent身份
    identity = AgentIdentity(
        agent_id="deepseek_cognitive_001",
        name="DeepSeek认知助手",
        role="智能助手",
        expertise_domains=["对话", "编程", "分析"],
        description="基于DeepSeek API的认知Agent"
    )
    
    # 2. 创建认知Agent
    agent = CognitiveAgent(identity)
    
    # 3. 配置DeepSeek适配器
    api_key = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    if api_key == 'your_api_key_here':
        print("⚠️  请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    # 这里可以集成DeepSeek适配器到认知Agent中
    # (需要在认知Agent中添加适配器支持)
    
    print("🎯 认知Agent创建成功")
    print(f"🆔 Agent ID: {identity.agent_id}")
    print(f"📛 Agent名称: {identity.name}")
    print(f"🎭 角色: {identity.role}")
    print(f"🧠 专业领域: {', '.join(identity.expertise_domains)}")


async def tool_calling_demo():
    """工具调用演示"""
    
    print("\n🛠️ DeepSeek工具调用演示")
    print("=" * 50)
    
    api_key = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    if api_key == 'your_api_key_here':
        print("⚠️  请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    adapter = create_deepseek_adapter(api_key=api_key)
    await adapter.initialize()
    
    # 创建需要工具调用的任务
    tool_tasks = [
        UniversalTask(
            content="请搜索一下今天的天气情况",
            task_type=TaskType.TOOL_CALLING
        ),
        UniversalTask(
            content="帮我执行这段代码：print('Hello, DeepSeek!')",
            task_type=TaskType.CODE_EXECUTION
        )
    ]
    
    context = UniversalContext()
    
    for task in tool_tasks:
        print(f"\n🔧 工具任务: {task.content}")
        print("-" * 40)
        
        result = await adapter.execute(task, context)
        print(f"📄 结果: {result.content}")
        
        if 'tool_calls' in result.metadata:
            print(f"🛠️ 工具调用: {len(result.metadata['tool_calls'])}个")


async def performance_test():
    """性能测试"""
    
    print("\n⚡ DeepSeek性能测试")
    print("=" * 50)
    
    api_key = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    if api_key == 'your_api_key_here':
        print("⚠️  请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    adapter = create_deepseek_adapter(api_key=api_key)
    await adapter.initialize()
    
    # 创建测试任务
    test_tasks = [
        UniversalTask(content=f"请回答：1+{i}等于多少？", task_type=TaskType.QUESTION_ANSWERING)
        for i in range(5)
    ]
    
    print(f"🧪 开始测试 {len(test_tasks)} 个任务...")
    
    start_time = datetime.now()
    
    # 串行执行
    results = []
    for task in test_tasks:
        result = await adapter.execute(task, UniversalContext())
        results.append(result)
    
    end_time = datetime.now()
    
    # 统计结果
    successful = sum(1 for r in results if r.status.value == "success")
    total_time = (end_time - start_time).total_seconds()
    avg_time = total_time / len(test_tasks)
    
    print(f"✅ 成功任务: {successful}/{len(test_tasks)}")
    print(f"⏱️  总时间: {total_time:.2f}秒")
    print(f"📊 平均时间: {avg_time:.2f}秒/任务")
    print(f"🚀 吞吐量: {len(test_tasks)/total_time:.2f}任务/秒")
    
    # 显示Token统计
    total_tokens = sum(
        r.metadata.get('total_tokens', 0) 
        for r in results 
        if 'total_tokens' in r.metadata
    )
    print(f"🔢 总Token使用: {total_tokens}")


async def main():
    """主函数"""
    
    print("🎯 DeepSeek适配器完整演示")
    print("🔗 基于现有Agent Development Center架构")
    print("=" * 60)
    
    try:
        # 1. 基础功能演示
        await basic_deepseek_demo()
        
        # 2. 认知Agent演示
        await cognitive_agent_with_deepseek()
        
        # 3. 工具调用演示
        await tool_calling_demo()
        
        # 4. 性能测试
        await performance_test()
        
        print("\n🎉 演示完成！")
        
    except Exception as e:
        print(f"💥 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 