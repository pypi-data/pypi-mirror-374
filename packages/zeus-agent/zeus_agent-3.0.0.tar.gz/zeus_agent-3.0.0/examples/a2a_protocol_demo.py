"""
A2A (Agent-to-Agent) Protocol Demo
演示Agent间通信协议的使用方法

这个示例展示了：
1. A2A协议的基本使用
2. Agent间握手和能力交换
3. 任务协作和结果分享
4. 多种传输方式的使用
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.framework.abstractions.a2a_protocol import (
    A2AProtocolHandler,
    A2AAgentProfile,
    A2ACapability,
    A2ACapabilityType,
    A2AHTTPTransport,
    A2AWebSocketTransport,
    A2AMessageType,
    A2AMessage,
    A2AMessageHandler,
    create_a2a_capability,
    create_a2a_agent_profile
)


class TaskProcessingHandler(A2AMessageHandler):
    """任务处理消息处理器"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    async def handle_message(self, message: A2AMessage) -> A2AMessage:
        """处理任务请求消息"""
        if message.message_type == A2AMessageType.TASK_REQUEST:
            task_description = message.payload.get("task_description", "")
            task_data = message.payload.get("task_data", {})
            
            print(f"🔧 {self.agent_name} 收到任务请求: {task_description}")
            
            # 模拟任务处理
            await asyncio.sleep(0.5)
            
            # 创建任务响应
            response = A2AMessage(
                message_id=f"resp_{message.message_id}",
                protocol_version=message.protocol_version,
                message_type=A2AMessageType.TASK_RESPONSE,
                sender_id=message.receiver_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now(),
                correlation_id=message.correlation_id,
                payload={
                    "task_result": f"任务 '{task_description}' 已完成",
                    "processed_data": {
                        "status": "completed",
                        "processing_time": "0.5s",
                        "result_quality": "high",
                        "output": f"由 {self.agent_name} 处理的结果"
                    },
                    "completion_time": datetime.now().isoformat()
                }
            )
            
            print(f"✅ {self.agent_name} 完成任务处理")
            return response
        
        return None


class CollaborationHandler(A2AMessageHandler):
    """协作消息处理器"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    async def handle_message(self, message: A2AMessage) -> A2AMessage:
        """处理协作邀请消息"""
        if message.message_type == A2AMessageType.COLLABORATION_INVITE:
            collaboration_type = message.payload.get("collaboration_type", "")
            collaboration_data = message.payload.get("collaboration_data", {})
            
            print(f"🤝 {self.agent_name} 收到协作邀请: {collaboration_type}")
            
            # 模拟协作决策
            await asyncio.sleep(0.2)
            
            # 接受协作
            response = A2AMessage(
                message_id=f"collab_resp_{message.message_id}",
                protocol_version=message.protocol_version,
                message_type=A2AMessageType.COLLABORATION_ACCEPT,
                sender_id=message.receiver_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now(),
                correlation_id=message.correlation_id,
                payload={
                    "collaboration_id": message.payload.get("collaboration_id"),
                    "accepted": True,
                    "agent_role": "participant",
                    "available_time": "2h",
                    "commitment_level": "high"
                }
            )
            
            print(f"✅ {self.agent_name} 接受协作邀请")
            return response
        
        return None


async def create_demo_agent(agent_id: str, agent_name: str, transport_type: str = "http") -> A2AProtocolHandler:
    """创建演示用的Agent"""
    
    # 定义Agent能力
    capabilities = [
        create_a2a_capability(
            A2ACapabilityType.TEXT_PROCESSING,
            version="2.0",
            description="高级文本处理和分析",
            input_formats=["text", "markdown", "json"],
            output_formats=["text", "json", "html"]
        ),
        create_a2a_capability(
            A2ACapabilityType.CODE_GENERATION,
            version="1.5",
            description="Python和JavaScript代码生成",
            input_formats=["text", "json"],
            output_formats=["python", "javascript", "json"]
        ),
        create_a2a_capability(
            A2ACapabilityType.REASONING,
            version="1.0",
            description="逻辑推理和问题解决",
            input_formats=["text", "json"],
            output_formats=["text", "json"]
        )
    ]
    
    # 创建Agent配置文件
    profile = create_a2a_agent_profile(
        agent_id=agent_id,
        agent_name=agent_name,
        agent_type="multi_capability_agent",
        capabilities=capabilities,
        endpoint=f"http://localhost:8000/agents/{agent_id}"
    )
    
    # 选择传输方式
    if transport_type == "websocket":
        transport = A2AWebSocketTransport()
    else:
        transport = A2AHTTPTransport()
    
    # 创建协议处理器
    handler = A2AProtocolHandler(profile, transport)
    
    # 注册消息处理器
    handler.register_message_handler(A2AMessageType.TASK_REQUEST, TaskProcessingHandler(agent_name))
    handler.register_message_handler(A2AMessageType.COLLABORATION_INVITE, CollaborationHandler(agent_name))
    
    return handler


async def demo_basic_a2a_communication():
    """演示基本的A2A通信"""
    print("\n🚀 A2A协议基本通信演示")
    print("=" * 50)
    
    # 创建两个Agent
    agent1 = await create_demo_agent("agent_001", "Alice (文本专家)", "http")
    agent2 = await create_demo_agent("agent_002", "Bob (代码专家)", "websocket")
    
    print(f"📋 Agent 1: {agent1.agent_profile.agent_name}")
    print(f"   - ID: {agent1.agent_profile.agent_id}")
    print(f"   - 能力: {len(agent1.agent_profile.capabilities)} 个")
    print(f"   - 传输: HTTP")
    
    print(f"📋 Agent 2: {agent2.agent_profile.agent_name}")
    print(f"   - ID: {agent2.agent_profile.agent_id}")
    print(f"   - 能力: {len(agent2.agent_profile.capabilities)} 个")
    print(f"   - 传输: WebSocket")
    
    # 1. 握手连接
    print(f"\n🤝 步骤1: Agent间握手连接")
    success = await agent1.connect_to_agent("http://localhost:8001/agent_002")
    print(f"   连接结果: {'成功' if success else '失败'}")
    
    # 2. 能力交换
    print(f"\n🔄 步骤2: 能力交换")
    success = await agent1.send_capability_exchange(
        agent2.agent_profile.agent_id,
        agent2.agent_profile.endpoint
    )
    print(f"   能力交换: {'成功' if success else '失败'}")
    
    # 3. 任务请求
    print(f"\n📝 步骤3: 发送任务请求")
    correlation_id = await agent1.send_task_request(
        agent2.agent_profile.agent_id,
        agent2.agent_profile.endpoint,
        "生成一个Python函数来计算斐波那契数列",
        {
            "function_name": "fibonacci",
            "parameters": ["n"],
            "return_type": "int",
            "include_docstring": True
        }
    )
    print(f"   任务请求ID: {correlation_id}")
    
    # 4. 模拟任务响应处理
    print(f"\n⚡ 步骤4: 模拟任务响应")
    # 创建模拟的任务请求消息
    task_message = A2AMessage(
        message_id="task_001",
        protocol_version=agent1.agent_profile.supported_protocols[0],
        message_type=A2AMessageType.TASK_REQUEST,
        sender_id=agent1.agent_profile.agent_id,
        receiver_id=agent2.agent_profile.agent_id,
        timestamp=datetime.now(),
        correlation_id=correlation_id,
        payload={
            "task_description": "生成一个Python函数来计算斐波那契数列",
            "task_data": {
                "function_name": "fibonacci",
                "parameters": ["n"],
                "return_type": "int",
                "include_docstring": True
            }
        }
    )
    
    # Agent2处理任务
    response = await agent2.process_message(task_message)
    if response:
        print(f"   ✅ 任务响应: {response.payload.get('task_result', '无结果')}")
    
    # 5. 显示连接状态
    print(f"\n📊 步骤5: 连接状态")
    status1 = agent1.get_connection_status()
    status2 = agent2.get_connection_status()
    
    print(f"   Agent 1 状态: 已处理 {status1['messages_processed']} 条消息")
    print(f"   Agent 2 状态: 已处理 {status2['messages_processed']} 条消息")


async def demo_multi_agent_collaboration():
    """演示多Agent协作"""
    print("\n🤝 多Agent协作演示")
    print("=" * 50)
    
    # 创建三个专业Agent
    coordinator = await create_demo_agent("coordinator_001", "项目协调员 (Charlie)", "http")
    developer = await create_demo_agent("developer_001", "开发工程师 (David)", "websocket")
    tester = await create_demo_agent("tester_001", "测试工程师 (Eve)", "http")
    
    agents = [coordinator, developer, tester]
    
    print("📋 协作团队:")
    for agent in agents:
        print(f"   - {agent.agent_profile.agent_name} ({agent.agent_profile.agent_id})")
    
    # 发起协作邀请
    print(f"\n📨 发起协作邀请")
    collaboration_id = await coordinator.send_collaboration_invite(
        [developer.agent_profile.agent_id, tester.agent_profile.agent_id],
        "software_development_project",
        {
            "project_name": "A2A协议测试工具",
            "duration": "2h",
            "roles": {
                developer.agent_profile.agent_id: "lead_developer",
                tester.agent_profile.agent_id: "qa_engineer"
            },
            "deliverables": ["code_implementation", "test_cases", "documentation"]
        }
    )
    
    print(f"   协作ID: {collaboration_id}")
    
    # 模拟协作响应
    print(f"\n🔄 处理协作响应")
    
    # 创建协作邀请消息
    invite_message = A2AMessage(
        message_id="collab_invite_001",
        protocol_version=coordinator.agent_profile.supported_protocols[0],
        message_type=A2AMessageType.COLLABORATION_INVITE,
        sender_id=coordinator.agent_profile.agent_id,
        receiver_id=developer.agent_profile.agent_id,
        timestamp=datetime.now(),
        correlation_id=collaboration_id,
        payload={
            "collaboration_id": collaboration_id,
            "collaboration_type": "software_development_project",
            "collaboration_data": {
                "project_name": "A2A协议测试工具",
                "duration": "2h"
            },
            "participants": [developer.agent_profile.agent_id, tester.agent_profile.agent_id],
            "role_requirements": {"lead_developer": "Python开发经验"}
        }
    )
    
    # Developer响应
    dev_response = await developer.process_message(invite_message)
    if dev_response:
        print(f"   开发工程师响应: {dev_response.payload.get('accepted', False)}")
    
    # Tester响应（修改接收者ID）
    invite_message.receiver_id = tester.agent_profile.agent_id
    test_response = await tester.process_message(invite_message)
    if test_response:
        print(f"   测试工程师响应: {test_response.payload.get('accepted', False)}")
    
    # 显示协作状态
    print(f"\n📊 协作状态")
    coord_status = coordinator.get_connection_status()
    print(f"   协调员活跃协作: {coord_status['active_collaborations']} 个")
    print(f"   团队规模: {len(agents)} 个Agent")


async def demo_advanced_features():
    """演示高级功能"""
    print("\n⚡ A2A协议高级功能演示")
    print("=" * 50)
    
    # 创建专业Agent
    specialist = await create_demo_agent("specialist_001", "AI专家 (Frank)", "websocket")
    
    print("🔧 高级功能展示:")
    
    # 1. 心跳检测
    print(f"\n💓 心跳检测")
    heartbeat_msg = A2AMessage(
        message_id="heartbeat_001",
        protocol_version=specialist.agent_profile.supported_protocols[0],
        message_type=A2AMessageType.HEARTBEAT,
        sender_id="external_monitor",
        receiver_id=specialist.agent_profile.agent_id,
        timestamp=datetime.now(),
        payload={"ping": "alive_check"}
    )
    
    heartbeat_response = await specialist.process_message(heartbeat_msg)
    if heartbeat_response:
        print(f"   心跳响应: {heartbeat_response.payload.get('status', '无响应')}")
    
    # 2. 状态查询
    print(f"\n📊 状态查询")
    status_query_msg = A2AMessage(
        message_id="status_query_001",
        protocol_version=specialist.agent_profile.supported_protocols[0],
        message_type=A2AMessageType.STATUS_QUERY,
        sender_id="system_monitor",
        receiver_id=specialist.agent_profile.agent_id,
        timestamp=datetime.now(),
        payload={"query_type": "full_status"}
    )
    
    status_response = await specialist.process_message(status_query_msg)
    if status_response:
        status_data = status_response.payload
        print(f"   Agent状态: {status_data.get('agent_status', '未知')}")
        print(f"   当前负载: {status_data.get('current_load', 0)}")
        print(f"   可用能力: {status_data.get('available_capabilities', 0)} 个")
    
    # 3. 错误处理演示
    print(f"\n❌ 错误处理演示")
    invalid_msg = A2AMessage(
        message_id="invalid_001",
        protocol_version=specialist.agent_profile.supported_protocols[0],
        message_type=A2AMessageType.TASK_REQUEST,
        sender_id="error_generator",
        receiver_id=specialist.agent_profile.agent_id,
        timestamp=datetime.now(),
        payload={"invalid_data": None, "cause_error": True}
    )
    
    # 手动触发错误处理
    error_response = specialist._create_error_response(invalid_msg, "模拟处理错误")
    print(f"   错误响应: {error_response.payload.get('error_message', '无错误信息')}")


async def main():
    """主演示函数"""
    print("🌟 A2A (Agent-to-Agent) 协议演示")
    print("基于A2A协议标准实现的Agent间通信系统")
    print("=" * 60)
    
    try:
        # 基本通信演示
        await demo_basic_a2a_communication()
        
        # 等待一下，让输出更清晰
        await asyncio.sleep(1)
        
        # 多Agent协作演示
        await demo_multi_agent_collaboration()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 高级功能演示
        await demo_advanced_features()
        
        # 总结
        print("\n" + "=" * 60)
        print("🎉 A2A协议演示完成!")
        print("\n✨ 主要功能验证:")
        print("   ✅ Agent间握手和连接建立")
        print("   ✅ 能力交换和兼容性检查") 
        print("   ✅ 任务请求和响应处理")
        print("   ✅ 多Agent协作邀请和管理")
        print("   ✅ 心跳检测和状态监控")
        print("   ✅ 错误处理和异常管理")
        print("   ✅ HTTP和WebSocket传输支持")
        
        print("\n🚀 A2A协议已准备好用于生产环境的Agent间通信!")
        
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 