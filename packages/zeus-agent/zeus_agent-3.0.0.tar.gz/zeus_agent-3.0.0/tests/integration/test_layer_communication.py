#!/usr/bin/env python3
"""
Layer Communication Test - 层间通信协议测试
验证层间通信协议是否正常工作
"""

import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_basic_communication():
    """测试基本通信功能"""
    logger.info("🧪 === 测试基本层间通信功能 ===")
    
    try:
        # 导入层间通信协议
        from layers.framework.abstractions.layer_communication import (
            LayerCommunicationManager,
            LayerRequest,
            LayerResponse,
            ExecutionContext,
            MessageType
        )
        
        # 导入各层通信管理器
        from layers.infrastructure.communication_manager import infrastructure_communication_manager
        from layers.adapter.communication_manager import adapter_communication_manager
        from layers.framework.communication_manager import framework_communication_manager
        from layers.cognitive.communication_manager import cognitive_communication_manager
        from layers.business.communication_manager import business_communication_manager
        from layers.application.communication_manager import application_communication_manager
        
        logger.info("✅ 成功导入层间通信协议和通信管理器")
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id="test_request_001",
            user_id="test_user",
            session_id="test_session",
            project_id="test_project"
        )
        
        logger.info("✅ 成功创建执行上下文")
        
        # 测试基础设施层通信
        logger.info("🏗️ 测试基础设施层通信...")
        infra_request = LayerRequest(
            operation="get_system_health",
            parameters={}
        )
        
        infra_response = await infrastructure_communication_manager.communicator.send_request(
            "infrastructure",
            infra_request,
            context
        )
        
        if infra_response.success:
            logger.info(f"✅ 基础设施层通信成功: {infra_response.data}")
        else:
            logger.error(f"❌ 基础设施层通信失败: {infra_response.error}")
            return False
        
        # 测试框架抽象层通信
        logger.info("🎯 测试框架抽象层通信...")
        framework_request = LayerRequest(
            operation="get_agent_capabilities",
            parameters={"agent_type": "openai"}
        )
        
        framework_response = await framework_communication_manager.communicator.send_request(
            "framework",
            framework_request,
            context
        )
        
        if framework_response.success:
            logger.info(f"✅ 框架抽象层通信成功: {framework_response.data}")
        else:
            logger.error(f"❌ 框架抽象层通信失败: {framework_response.error}")
            return False
        
        # 测试业务能力层通信
        logger.info("💼 测试业务能力层通信...")
        business_request = LayerRequest(
            operation="create_workflow",
            parameters={
                "name": "测试工作流",
                "steps": [{"name": "测试步骤", "type": "test"}]
            }
        )
        
        business_response = await business_communication_manager.communicator.send_request(
            "business",
            business_request,
            context
        )
        
        if business_response.success:
            logger.info(f"✅ 业务能力层通信成功: {business_response.data}")
        else:
            logger.error(f"❌ 业务能力层通信失败: {business_response.error}")
            return False
        
        # 测试应用编排层通信
        logger.info("📱 测试应用编排层通信...")
        app_request = LayerRequest(
            operation="get_application_status",
            parameters={}
        )
        
        app_response = await application_communication_manager.communicator.send_request(
            "application",
            app_request,
            context
        )
        
        if app_response.success:
            logger.info(f"✅ 应用编排层通信成功: {app_response.data}")
        else:
            logger.error(f"❌ 应用编排层通信失败: {app_response.error}")
            return False
        
        logger.info("🎉 === 所有层间通信测试通过 ===")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        return False


async def test_event_system():
    """测试事件系统"""
    logger.info("📡 === 测试事件系统 ===")
    
    try:
        from layers.framework.abstractions.layer_communication import (
            ExecutionContext,
            LayerEventHandler
        )
        from layers.infrastructure.communication_manager import infrastructure_communication_manager
        
        # 创建事件处理器
        class TestEventHandler(LayerEventHandler):
            def __init__(self):
                self.events_received = []
                self.logger = logging.getLogger("TestEventHandler")
            
            async def handle_event(self, event, context):
                self.events_received.append({
                    "source_layer": event.source_layer,
                    "event_type": event.payload.get("event_type"),
                    "data": event.payload.get("data", {})
                })
                self.logger.info(f"📨 收到事件: {event.source_layer} -> {event.payload.get('event_type')}")
        
        # 创建事件处理器实例
        event_handler = TestEventHandler()
        
        # 订阅事件
        infrastructure_communication_manager.subscribe_to_events("*", event_handler)
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id="event_test_001",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 发布测试事件
        await infrastructure_communication_manager.publish_infrastructure_event(
            "test_event",
            {"message": "这是一个测试事件"},
            context
        )
        
        # 等待事件处理
        await asyncio.sleep(0.2)
        
        if len(event_handler.events_received) > 0:
            logger.info(f"✅ 事件系统测试成功，收到 {len(event_handler.events_received)} 个事件:")
            for i, event in enumerate(event_handler.events_received, 1):
                logger.info(f"  {i}. {event['source_layer']} -> {event['event_type']}")
            return True
        else:
            logger.error("❌ 事件系统测试失败，没有收到事件")
            return False
            
    except Exception as e:
        logger.error(f"❌ 事件系统测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("🚀 === 开始层间通信协议测试 ===")
    
    # 测试1: 基本通信功能
    basic_test_result = await test_basic_communication()
    
    # 测试2: 事件系统
    event_test_result = await test_event_system()
    
    # 总结
    logger.info("📊 === 测试结果总结 ===")
    logger.info(f"基本通信功能: {'✅ 通过' if basic_test_result else '❌ 失败'}")
    logger.info(f"事件系统: {'✅ 通过' if event_test_result else '❌ 失败'}")
    
    if basic_test_result and event_test_result:
        logger.info("🎉 === 所有测试通过！层间通信协议工作正常 ===")
        return True
    else:
        logger.error("❌ === 部分测试失败，请检查层间通信协议实现 ===")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 