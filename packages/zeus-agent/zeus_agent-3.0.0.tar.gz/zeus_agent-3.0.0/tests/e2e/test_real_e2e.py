#!/usr/bin/env python3
"""
真正的端到端测试
实际调用AI API进行完整的对话测试
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def check_api_credentials():
    """检查API凭据是否可用"""
    print("🔑 检查API凭据...")
    
    api_keys = {
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY")
    }
    
    available_apis = []
    for key, value in api_keys.items():
        if value:
            available_apis.append(key)
            print(f"✅ {key}: 已配置")
        else:
            print(f"❌ {key}: 未配置")
    
    return available_apis

async def test_deepseek_adapter():
    """测试DeepSeek适配器的真实API调用"""
    print("\n🤖 测试DeepSeek适配器...")
    
    try:
        from layers.adapter.deepseek.adapter import DeepSeekAdapter
        
        # 检查API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ 没有可用的DeepSeek API密钥，跳过测试")
            return False
        
        # 创建适配器实例
        adapter = DeepSeekAdapter()
        
        # 创建一个简单的对话任务
        from layers.framework.abstractions.task import UniversalTask, TaskType
        
        task = UniversalTask(
            content="请简单回答：什么是人工智能？",
            task_type=TaskType.CONVERSATION
        )
        
        print(f"🗣️ 发送问题: {task.content}")
        
        # 执行真实的API调用
        result = await adapter.execute(task)
        
        print(f"🤖 AI回复: {result.content[:100]}...")
        print(f"✅ DeepSeek API调用成功: {result.status}")
        
        return True
        
    except ImportError as e:
        print(f"❌ DeepSeek适配器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {e}")
        return False

async def test_openai_adapter():
    """测试OpenAI适配器的真实API调用"""
    print("\n🤖 测试OpenAI适配器...")
    
    try:
        from layers.adapter.openai.adapter import OpenAIAdapter
        
        # 检查API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ 没有可用的OpenAI API密钥，跳过测试")
            return False
        
        # 创建适配器实例
        adapter = OpenAIAdapter()
        
        # 创建一个简单的对话任务
        from layers.framework.abstractions.task import UniversalTask, TaskType
        
        task = UniversalTask(
            content="请简单回答：什么是机器学习？",
            task_type=TaskType.CONVERSATION
        )
        
        print(f"🗣️ 发送问题: {task.content}")
        
        # 执行真实的API调用
        result = await adapter.execute(task)
        
        print(f"🤖 AI回复: {result.content[:100]}...")
        print(f"✅ OpenAI API调用成功: {result.status}")
        
        return True
        
    except ImportError as e:
        print(f"❌ OpenAI适配器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ OpenAI API调用失败: {e}")
        return False

async def test_chatbot_demo():
    """测试实际的chatbot demo"""
    print("\n💬 测试Chatbot Demo...")
    
    try:
        # 切换到chatbot demo目录
        chatbot_dir = Path("workspace/examples/chatbot_demo")
        if not chatbot_dir.exists():
            print(f"❌ Chatbot demo目录不存在: {chatbot_dir}")
            return False
        
        # 导入chatbot组件
        sys.path.append(str(chatbot_dir))
        
        from agents.chatbot_agent import ChatbotAgent
        from agents.conversation_manager import ConversationManager
        
        # 创建对话管理器
        conversation_manager = ConversationManager()
        
        # 创建chatbot实例
        chatbot = ChatbotAgent(
            agent_id="test_chatbot",
            framework="autogen",  # 或其他可用框架
            personality="assistant"
        )
        
        # 模拟一次对话
        test_message = "你好，请介绍一下你自己"
        print(f"👤 用户: {test_message}")
        
        # 这里会调用实际的AI API
        response = await chatbot.process_message(test_message)
        
        print(f"🤖 Chatbot: {response.get('content', 'No response')[:100]}...")
        print("✅ Chatbot Demo测试成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ Chatbot Demo导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ Chatbot Demo测试失败: {e}")
        return False

async def test_adapter_layer_integration():
    """测试适配器层的完整集成"""
    print("\n🔌 测试适配器层集成...")
    
    try:
        # 测试适配器注册表
        from layers.adapter.registry.adapter_registry import AdapterRegistry
        
        registry = AdapterRegistry()
        
        # 检查可用的适配器
        available_adapters = registry.list_adapters()
        print(f"📋 可用适配器: {list(available_adapters.keys())}")
        
        if not available_adapters:
            print("❌ 没有可用的适配器")
            return False
        
        # 尝试获取第一个可用的适配器
        adapter_name = list(available_adapters.keys())[0]
        adapter = registry.get_adapter(adapter_name)
        
        if adapter:
            print(f"✅ 成功获取适配器: {adapter_name}")
            
            # 测试适配器的基本功能
            capabilities = adapter.get_capabilities()
            print(f"📋 适配器能力: {capabilities}")
            
            return True
        else:
            print(f"❌ 无法获取适配器: {adapter_name}")
            return False
            
    except ImportError as e:
        print(f"❌ 适配器注册表导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 适配器层测试失败: {e}")
        return False

async def run_real_e2e_test():
    """运行真正的端到端测试"""
    print("🚀 开始真正的ADC端到端测试（包含API调用）")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 检查API凭据
    available_apis = check_api_credentials()
    
    if not available_apis:
        print("\n❌ 没有可用的API密钥，无法进行真实的API测试")
        print("请设置以下环境变量之一:")
        print("- OPENAI_API_KEY")
        print("- DEEPSEEK_API_KEY") 
        return False
    
    # 测试结果收集
    results = {
        "deepseek_adapter": False,
        "openai_adapter": False,
        "chatbot_demo": False,
        "adapter_integration": False
    }
    
    # 运行各项真实测试
    if "DEEPSEEK_API_KEY" in available_apis:
        results["deepseek_adapter"] = await test_deepseek_adapter()
    
    if "OPENAI_API_KEY" in available_apis:
        results["openai_adapter"] = await test_openai_adapter()
    
    results["chatbot_demo"] = await test_chatbot_demo()
    results["adapter_integration"] = await test_adapter_layer_integration()
    
    # 生成测试报告
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("📊 真实端到端测试报告")
    print("=" * 60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    print(f"执行时间: {duration:.2f}秒")
    
    if passed_tests > 0:
        print(f"\n🎉 真实API测试完成！有{passed_tests}个测试通过了实际的AI调用")
    else:
        print(f"\n⚠️ 所有真实API测试都失败了，可能需要检查配置和网络连接")
    
    return passed_tests > 0

if __name__ == "__main__":
    print("⚠️ 警告：这个测试会进行真实的API调用，可能会产生费用！")
    print("确保您有有效的API密钥并了解相关费用。")
    
    # 运行真实的端到端测试
    success = asyncio.run(run_real_e2e_test())
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1) 