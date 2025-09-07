#!/usr/bin/env python3
"""
真正的自动化聊天功能测试
实际调用AI API进行多轮对话测试
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_deepseek_chat():
    """测试DeepSeek的真实聊天功能"""
    print("🤖 开始DeepSeek真实聊天测试...")
    
    try:
        from layers.adapter.deepseek.adapter import DeepSeekAdapter
        from layers.framework.abstractions.task import UniversalTask, TaskType
        
        # 检查API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ 没有可用的API密钥")
            return False
        
        print(f"✅ 找到API密钥: {api_key[:10]}...")
        
        # 创建适配器实例
        adapter = DeepSeekAdapter(name="test_deepseek_adapter", config={
            "api_key": api_key,
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 1000
        })
        
        await adapter.initialize({"api_key": api_key})
        
        # 创建一个聊天Agent
        agent_id = await adapter.create_agent({
            "agent_id": "chatbot_001",
            "name": "Test Chatbot",
            "system_message": "你是一个友好的AI助手，请用中文回答用户的问题。回答要简洁明了。",
            "api_key": api_key
        })
        
        print(f"✅ 创建了聊天Agent: {agent_id}")
        
        # 定义测试对话
        test_conversations = [
            "你好，请简单介绍一下你自己",
            "什么是人工智能？请用一句话概括",
            "谢谢你的回答，再见"
        ]
        
        chat_success = True
        for i, message in enumerate(test_conversations, 1):
            print(f"\n🔄 第{i}轮对话:")
            print(f"👤 用户: {message}")
            
            # 创建任务
            task = UniversalTask(
                content=message,
                task_type=TaskType.CONVERSATION
            )
            
            try:
                # 创建上下文
                from layers.framework.abstractions.context import UniversalContext
                context = UniversalContext(
                    data={
                        "agent_id": agent_id,
                        "conversation_turn": i
                    }
                )
                
                # 执行真实的API调用
                result = await adapter.execute_task(task, context)
                
                if result and result.status.value == "success" and result.data:
                    # 从data中获取AI回复
                    if "reply" in result.data:
                        ai_response = result.data["reply"].strip()
                    elif "content" in result.data:
                        ai_response = result.data["content"].strip()
                    else:
                        ai_response = str(result.data).strip()
                    
                    print(f"🤖 AI回复: {ai_response}")
                    
                    # 验证回复是否合理
                    if len(ai_response) > 5 and "error" not in ai_response.lower():
                        print(f"✅ 第{i}轮对话成功")
                    else:
                        print(f"⚠️ 第{i}轮对话回复异常: {ai_response}")
                        chat_success = False
                else:
                    print(f"❌ 第{i}轮对话无回复或失败")
                    if result:
                        print(f"   状态: {result.status.value}")
                        print(f"   数据: {result.data}")
                    chat_success = False
                    
            except Exception as e:
                print(f"❌ 第{i}轮对话失败: {str(e)}")
                chat_success = False
            
            # 等待一下，避免请求过快
            await asyncio.sleep(1)
        
        return chat_success
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ DeepSeek聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_api_call():
    """测试简单的API调用"""
    print("\n🔍 测试简单的API调用...")
    
    try:
        import httpx
        
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ 没有API密钥")
            return False
        
        # 直接调用DeepSeek API
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个友好的AI助手"},
                    {"role": "user", "content": "请说'你好，测试成功'"}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            print("📡 发送API请求...")
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    print(f"🤖 AI回复: {ai_response}")
                    print("✅ 直接API调用成功")
                    return True
                else:
                    print(f"❌ API响应格式异常: {result}")
                    return False
            else:
                print(f"❌ API调用失败: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 简单API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_conversation_flow():
    """测试完整的对话流程"""
    print("\n💬 测试完整对话流程...")
    
    try:
        # 先测试简单API调用
        simple_test = await test_simple_api_call()
        if not simple_test:
            print("❌ 简单API测试失败，跳过对话流程测试")
            return False
        
        # 测试适配器对话
        adapter_test = await test_deepseek_chat()
        
        return adapter_test
        
    except Exception as e:
        print(f"❌ 对话流程测试失败: {e}")
        return False

async def run_automated_chat_test():
    """运行自动化聊天测试"""
    print("🚀 开始自动化聊天功能测试")
    print("🔥 这是真正的API调用测试！")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # 检查必要的依赖
    try:
        import httpx
        print("✅ httpx库可用")
    except ImportError:
        print("❌ 缺少httpx库，请安装: pip install httpx")
        return False
    
    # 检查API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 没有可用的API密钥")
        print("请设置环境变量: DEEPSEEK_API_KEY 或 ARK_API_KEY 或 OPENAI_API_KEY")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    # 确定API类型
    if api_key.startswith("sk-") and len(api_key) > 20:
        api_type = "DeepSeek/OpenAI"
        print(f"🔑 检测到 {api_type} 格式的API密钥")
    else:
        api_type = "ARK"
        print(f"🔑 检测到 {api_type} 格式的API密钥")
    
    # 执行真实的聊天测试
    success = await test_conversation_flow()
    
    # 生成测试报告
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("📊 自动化聊天测试报告")
    print("=" * 50)
    
    if success:
        print("✅ 聊天功能测试: 成功")
        print("🎉 恭喜！真正的AI聊天功能正常工作！")
        print("🔥 这证明了ADC系统能够:")
        print("   - 成功连接到DeepSeek API")
        print("   - 进行真实的多轮对话")
        print("   - 正确处理请求和响应")
        print("   - 适配器层工作正常")
    else:
        print("❌ 聊天功能测试: 失败")
        print("⚠️ 需要检查:")
        print("   - API密钥是否正确")
        print("   - 网络连接是否正常") 
        print("   - 适配器实现是否有问题")
    
    print(f"\n⏱️ 测试执行时间: {duration:.2f}秒")
    
    return success

if __name__ == "__main__":
    print("⚠️ 警告：这个测试会进行真实的API调用！")
    print("🔥 这将消耗您的API额度并可能产生费用")
    print("💡 确保您的API密钥有足够的余额")
    print()
    
    # 运行自动化聊天测试
    try:
        success = asyncio.run(run_automated_chat_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 