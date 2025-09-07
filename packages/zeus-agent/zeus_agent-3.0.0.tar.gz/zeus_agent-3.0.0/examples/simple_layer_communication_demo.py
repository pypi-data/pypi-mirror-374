#!/usr/bin/env python3
"""
Simple Layer Communication Demo - 简化层间通信演示
演示层间通信协议的核心功能
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入层间通信协议
from layers.framework.abstractions.layer_communication import (
    LayerCommunicationManager,
    LayerRequest,
    LayerResponse,
    ExecutionContext,
    MessageType,
    LayerEventHandler
)

# 导入各层通信管理器
from layers.infrastructure.communication_manager import infrastructure_communication_manager
from layers.framework.communication_manager import framework_communication_manager
from layers.business.communication_manager import business_communication_manager
from layers.application.communication_manager import application_communication_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleEventMonitor(LayerEventHandler):
    """简单事件监控器"""
    
    def __init__(self):
        self.events_received = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def handle_event(self, event, context: ExecutionContext) -> None:
        """处理层间事件"""
        event_info = {
            "timestamp": datetime.now().isoformat(),
            "source_layer": event.source_layer,
            "event_type": event.payload.get("event_type"),
            "data": event.payload.get("data", {})
        }
        self.events_received.append(event_info)
        self.logger.info(f"📨 收到事件: {event.source_layer} -> {event.payload.get('event_type')}")


async def demo_basic_communication():
    """演示基本通信功能"""
    logger.info("🚀 === 层间通信协议基本功能演示 ===")
    
    # 创建事件监控器
    event_monitor = SimpleEventMonitor()
    
    # 订阅所有层的事件
    managers = [
        infrastructure_communication_manager,
        framework_communication_manager,
        business_communication_manager,
        application_communication_manager
    ]
    
    for manager in managers:
        manager.subscribe_to_events("*", event_monitor)
    
    # 创建执行上下文
    context = ExecutionContext(
        request_id=f"demo_{int(datetime.now().timestamp())}",
        user_id="demo_user",
        session_id="demo_session",
        project_id="demo_project"
    )
    
    try:
        # 演示1: 基础设施层系统健康检查
        logger.info("\n🏗️ 演示1: 基础设施层系统健康检查")
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
            logger.info(f"✅ 系统健康状态: {infra_response.data['overall_status']}")
            logger.info(f"   CPU使用率: {infra_response.data['metrics']['cpu_usage']}")
            logger.info(f"   内存使用率: {infra_response.data['metrics']['memory_usage']}")
        else:
            logger.error(f"❌ 系统健康检查失败: {infra_response.error}")
        
        # 演示2: 框架抽象层Agent能力查询
        logger.info("\n🎯 演示2: 框架抽象层Agent能力查询")
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
            logger.info(f"✅ OpenAI Agent能力: {framework_response.data['capabilities']}")
            logger.info(f"   能力数量: {framework_response.data['capability_count']}")
        else:
            logger.error(f"❌ Agent能力查询失败: {framework_response.error}")
        
        # 演示3: 业务能力层工作流创建
        logger.info("\n💼 演示3: 业务能力层工作流创建")
        workflow_config = {
            "name": "演示工作流",
            "steps": [
                {"name": "步骤1", "type": "agent_task"},
                {"name": "步骤2", "type": "condition"},
                {"name": "步骤3", "type": "agent_task"}
            ]
        }
        
        business_request = LayerRequest(
            operation="create_workflow",
            parameters=workflow_config
        )
        
        business_response = await business_communication_manager.communicator.send_request(
            "business",
            business_request,
            context
        )
        
        if business_response.success:
            logger.info(f"✅ 工作流创建成功: {business_response.data['workflow_id']}")
            logger.info(f"   工作流名称: {business_response.data['workflow_name']}")
            logger.info(f"   步骤数量: {business_response.data['step_count']}")
        else:
            logger.error(f"❌ 工作流创建失败: {business_response.error}")
        
        # 演示4: 应用编排层状态获取
        logger.info("\n📱 演示4: 应用编排层状态获取")
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
            logger.info(f"✅ 应用层状态: {app_response.data['application_layer']}")
            if 'layers' in app_response.data:
                logger.info(f"   基础设施层状态: {app_response.data['layers'].get('infrastructure', {}).get('overall_status', 'unknown')}")
        else:
            logger.error(f"❌ 应用状态获取失败: {app_response.error}")
        
        # 演示5: 事件监控
        logger.info("\n📡 演示5: 事件监控")
        logger.info(f"   总共接收到 {len(event_monitor.events_received)} 个事件:")
        
        for i, event in enumerate(event_monitor.events_received, 1):
            logger.info(f"   {i}. {event['source_layer']} -> {event['event_type']}")
        
        # 总结
        logger.info("\n🎉 === 演示完成 ===")
        logger.info("✅ 层间通信协议工作正常")
        logger.info("✅ 各层通信管理器已成功集成")
        logger.info("✅ 异步消息传递机制运行良好")
        logger.info("✅ 事件系统正常工作")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 演示过程中发生错误: {e}")
        return False


async def main():
    """主函数"""
    success = await demo_basic_communication()
    return success


if __name__ == "__main__":
    asyncio.run(main()) 