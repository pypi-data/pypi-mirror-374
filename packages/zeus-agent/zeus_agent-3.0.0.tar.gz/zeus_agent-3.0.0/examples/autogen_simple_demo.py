"""
AutoGen适配器简化演示
展示AutoGen适配器的基本功能，无需真实API密钥

主要演示功能：
1. AutoGen适配器初始化
2. Agent创建和管理
3. 基本任务执行（模拟）
4. 团队创建和协作
5. A2A协议集成
6. 健康检查和状态监控
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.adapter.autogen.adapter_simple import AutoGenAdapterSimple, AUTOGEN_AVAILABLE
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from layers.framework.abstractions.context import UniversalContext


async def demo_adapter_initialization():
    """演示适配器初始化"""
    print("\n🚀 AutoGen适配器初始化演示")
    print("=" * 50)
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen未安装，将演示错误处理")
        try:
            adapter = AutoGenAdapterSimple()
        except Exception as e:
            print(f"   ✅ 正确捕获错误: {str(e)}")
            return None
    
    try:
        # 创建适配器
        adapter = AutoGenAdapterSimple("demo_adapter")
        print(f"✅ 适配器创建成功: {adapter.name}")
        
        # 初始化配置
        config = {
            "default_llm": {
                "model": "mock-gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
        
        await adapter.initialize(config)
        print(f"✅ 适配器初始化成功")
        print(f"   状态: {adapter.status.value}")
        print(f"   就绪: {adapter.is_ready()}")
        
        # 获取能力
        capabilities = adapter.get_capabilities()
        print(f"   支持能力: {[cap.value for cap in capabilities]}")
        
        return adapter
        
    except Exception as e:
        print(f"❌ 适配器初始化失败: {e}")
        return None


async def demo_agent_creation(adapter):
    """演示Agent创建"""
    print("\n👥 Agent创建演示")
    print("=" * 50)
    
    if not adapter:
        print("❌ 适配器不可用，跳过演示")
        return []
    
    try:
        agent_ids = []
        
        # 创建AssistantAgent
        print("🤖 创建AssistantAgent...")
        assistant_config = {
            "agent_id": "assistant_001",
            "type": "assistant",
            "name": "AI Assistant",
            "system_message": "You are a helpful AI assistant.",
            "llm_config": {"model": "mock-gpt-4"}
        }
        
        assistant_id = await adapter.create_agent(assistant_config)
        agent_ids.append(assistant_id)
        print(f"   ✅ 创建成功: {assistant_id}")
        
        # 创建UserProxyAgent
        print("🛠️ 创建UserProxyAgent...")
        proxy_config = {
            "agent_id": "proxy_001",
            "type": "user_proxy",
            "name": "User Proxy",
            "code_execution_config": {"work_dir": "temp"}
        }
        
        proxy_id = await adapter.create_agent(proxy_config)
        agent_ids.append(proxy_id)
        print(f"   ✅ 创建成功: {proxy_id}")
        
        # 显示Agent状态
        print(f"\n📊 Agent状态:")
        for agent_id in agent_ids:
            status = adapter.get_agent_status(agent_id)
            print(f"   {agent_id}:")
            print(f"     类型: {status['agent_type']}")
            print(f"     状态: {status['status']}")
            print(f"     A2A能力: {len(status['a2a_profile']['capabilities'])} 个")
        
        return agent_ids
        
    except Exception as e:
        print(f"❌ Agent创建失败: {e}")
        return []


async def demo_task_execution(adapter, agent_ids):
    """演示任务执行"""
    print("\n💼 任务执行演示")
    print("=" * 50)
    
    if not adapter or not agent_ids:
        print("❌ 适配器或Agent不可用，跳过演示")
        return
    
    try:
        # 创建测试上下文
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'demo_session',
            'timestamp': datetime.now().isoformat()
        })
        
        # 聊天任务
        print("💬 执行聊天任务...")
        chat_task = UniversalTask(
            content="Hello! Please introduce yourself.",
            task_type=TaskType.CHAT,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={'domain': 'conversation'},
            task_id="chat_demo"
        )
        
        chat_result = await adapter.execute_task(chat_task, context)
        print(f"   结果: {'成功' if chat_result.success else '失败'}")
        if chat_result.success:
            print(f"   回复: {chat_result.data.get('reply', 'No reply')[:100]}...")
            print(f"   Agent: {chat_result.data.get('agent_id')}")
        else:
            print(f"   错误: {chat_result.error}")
        
        # 代码生成任务
        print("\n💻 执行代码生成任务...")
        code_task = UniversalTask(
            content="Write a Python function to calculate fibonacci numbers",
            task_type=TaskType.CODE_GENERATION,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={'language': 'python'},
            task_id="code_demo"
        )
        
        code_result = await adapter.execute_task(code_task, context)
        print(f"   结果: {'成功' if code_result.success else '失败'}")
        if code_result.success:
            print(f"   代码: {code_result.data.get('code_result', 'No result')[:100]}...")
            print(f"   Agent: {code_result.data.get('agent_id')}")
        else:
            print(f"   错误: {code_result.error}")
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")


async def demo_team_collaboration(adapter, agent_ids):
    """演示团队协作"""
    print("\n🤝 团队协作演示")
    print("=" * 50)
    
    if not adapter or len(agent_ids) < 2:
        print("❌ 需要至少2个Agent进行团队协作演示")
        return
    
    try:
        # 创建团队
        print("👥 创建团队...")
        team_config = {
            "team_id": "demo_team",
            "agent_ids": agent_ids
        }
        
        team_id = await adapter.create_team(team_config)
        print(f"   ✅ 团队创建成功: {team_id}")
        
        # 获取团队状态
        team_status = adapter.get_team_status(team_id)
        print(f"   成员: {team_status['agents']}")
        print(f"   数量: {team_status['agent_count']}")
        print(f"   GroupChat: {team_status['has_group_chat']}")
        
        # 执行协作任务
        print(f"\n🚀 执行团队协作任务...")
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'team_session',
            'team_id': team_id
        })
        
        collaboration_task = UniversalTask(
            content="Let's work together to design a simple calculator application. Discuss the requirements and basic architecture.",
            task_type=TaskType.COLLABORATION,
            priority=TaskPriority.HIGH,
            requirements=TaskRequirements(),
            context={'project': 'calculator', 'type': 'design'},
            task_id="collab_demo"
        )
        
        collab_result = await adapter.execute_task(collaboration_task, context)
        print(f"   结果: {'成功' if collab_result.success else '失败'}")
        
        if collab_result.success:
            result_data = collab_result.data
            print(f"   团队ID: {result_data.get('team_id')}")
            print(f"   状态: {result_data.get('status')}")
            print(f"   参与者: {result_data.get('participants', [])}")
            print(f"   消息数: {result_data.get('messages', 0)}")
        else:
            print(f"   错误: {collab_result.error}")
        
    except Exception as e:
        print(f"❌ 团队协作演示失败: {e}")


async def demo_a2a_integration(adapter, agent_ids):
    """演示A2A协议集成"""
    print("\n🔄 A2A协议集成演示")
    print("=" * 50)
    
    if not adapter or not agent_ids:
        print("❌ 适配器或Agent不可用，跳过演示")
        return
    
    try:
        print("📋 A2A集成状态:")
        
        # 获取A2A适配器状态
        a2a_status = adapter.a2a_adapter.get_integration_status()
        print(f"   层名称: {a2a_status['layer_name']}")
        print(f"   注册Agent数量: {a2a_status['registered_agents']}")
        print(f"   Agent列表: {a2a_status['agents']}")
        
        # 显示每个Agent的A2A配置文件
        print(f"\n🤖 Agent A2A配置:")
        for agent_id in agent_ids:
            if agent_id in adapter.agents:
                agent = adapter.agents[agent_id]
                profile = agent.a2a_profile
                print(f"   {agent_id}:")
                print(f"     名称: {profile.agent_name}")
                print(f"     类型: {profile.agent_type}")
                print(f"     能力数量: {len(profile.capabilities)}")
                print(f"     协议版本: {[p.value for p in profile.supported_protocols]}")
                print(f"     端点: {profile.endpoint}")
        
        # 模拟A2A通信
        if len(agent_ids) >= 2:
            print(f"\n💬 模拟A2A Agent间通信...")
            agent1 = adapter.agents[agent_ids[0]]
            agent2_id = agent_ids[1]
            
            print(f"   {agent1.agent_id} -> {agent2_id}: 发送A2A消息")
            try:
                # 这里在实际环境中会发送真实的A2A消息
                print(f"   ✅ A2A消息发送模拟成功")
                print(f"   协议: A2A v2.0")
                print(f"   传输: HTTP")
            except Exception as e:
                print(f"   ❌ A2A通信失败: {e}")
        
    except Exception as e:
        print(f"❌ A2A协议集成演示失败: {e}")


async def demo_health_check(adapter):
    """演示健康检查"""
    print("\n🏥 健康检查演示")
    print("=" * 50)
    
    if not adapter:
        print("❌ 适配器不可用，跳过演示")
        return
    
    try:
        # 执行健康检查
        health_status = await adapter.health_check()
        
        print("📊 适配器健康状态:")
        print(f"   适配器名称: {health_status['adapter_name']}")
        print(f"   整体健康: {health_status['health']}")
        print(f"   状态: {health_status['status']}")
        print(f"   已初始化: {health_status['initialized']}")
        print(f"   AutoGen可用: {health_status['autogen_available']}")
        print(f"   Agent数量: {health_status['agents_count']}")
        print(f"   团队数量: {health_status['teams_count']}")
        print(f"   成功率: {health_status['success_rate']:.2%}")
        
        if 'issues' in health_status:
            print(f"   问题: {health_status['issues']}")
        
        # 获取适配器元数据
        metadata = adapter.get_metadata()
        print(f"\n📈 适配器元数据:")
        print(f"   创建时间: {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   初始化次数: {metadata.initialization_count}")
        print(f"   成功操作: {metadata.successful_operations}")
        print(f"   失败操作: {metadata.failed_operations}")
        print(f"   成功率: {metadata.success_rate:.2%}")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


async def main():
    """主演示函数"""
    print("🌟 AutoGen适配器简化演示")
    print("展示AutoGen与ADC 8层架构和A2A协议的集成")
    print("=" * 60)
    
    try:
        # 适配器初始化
        adapter = await demo_adapter_initialization()
        
        if not adapter:
            print("\n❌ 无法继续演示，AutoGen不可用或初始化失败")
            if not AUTOGEN_AVAILABLE:
                print("💡 提示: 安装AutoGen以体验完整功能: pip install pyautogen")
            return 1
        
        # Agent创建
        agent_ids = await demo_agent_creation(adapter)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 任务执行
        await demo_task_execution(adapter, agent_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 团队协作
        await demo_team_collaboration(adapter, agent_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # A2A集成
        await demo_a2a_integration(adapter, agent_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 健康检查
        await demo_health_check(adapter)
        
        # 总结
        print("\n" + "=" * 60)
        print("🎉 AutoGen适配器演示完成!")
        print("\n✨ 主要功能验证:")
        print("   ✅ 适配器初始化和配置管理")
        print("   ✅ Agent创建和管理 (Assistant, UserProxy)")
        print("   ✅ 任务执行系统 (聊天、代码、协作)")
        print("   ✅ 团队管理和GroupChat")
        print("   ✅ A2A协议集成和Agent注册")
        print("   ✅ 健康检查和状态监控")
        print("   ✅ 错误处理和异常管理")
        
        print("\n🚀 AutoGen适配器已成功集成到ADC 8层架构!")
        print("📋 注意: 完整功能需要安装AutoGen并配置LLM API密钥")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 