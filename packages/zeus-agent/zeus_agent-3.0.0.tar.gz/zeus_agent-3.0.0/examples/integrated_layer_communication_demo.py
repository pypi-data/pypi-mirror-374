"""
Integrated Layer Communication Demo - 完整层间通信集成演示
演示7层架构间的完整通信流程
"""

import asyncio
import logging
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

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
from layers.adapter.communication_manager import adapter_communication_manager
from layers.framework.communication_manager import framework_communication_manager
from layers.cognitive.communication_manager import cognitive_communication_manager
from layers.business.communication_manager import business_communication_manager
from layers.application.communication_manager import application_communication_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GlobalEventMonitor(LayerEventHandler):
    """全局事件监控器 - 监听所有层间事件"""
    
    def __init__(self):
        self.events_received = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def handle_event(self, event, context: ExecutionContext) -> None:
        """处理层间事件"""
        event_info = {
            "timestamp": datetime.now().isoformat(),
            "source_layer": event.source_layer,
            "event_type": event.payload.get("event_type"),
            "data": event.payload.get("data", {}),
            "trace_id": event.trace_id
        }
        self.events_received.append(event_info)
        self.logger.info(f"🌐 Global Event: {event.source_layer} -> {event.payload.get('event_type')}")


class LayerCommunicationDemo:
    """层间通信演示类"""
    
    def __init__(self):
        self.event_monitor = GlobalEventMonitor()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # 订阅所有层的事件
        self._subscribe_to_all_events()
    
    def _subscribe_to_all_events(self):
        """订阅所有层的事件"""
        managers = [
            infrastructure_communication_manager,
            adapter_communication_manager,
            framework_communication_manager,
            cognitive_communication_manager,
            business_communication_manager,
            application_communication_manager
        ]
        
        for manager in managers:
            manager.subscribe_to_events("*", self.event_monitor)
    
    async def demo_complete_agent_creation_flow(self):
        """演示完整的Agent创建流程"""
        self.logger.info("🚀 === 完整Agent创建流程演示 ===")
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id=f"agent_creation_{int(time.time())}",
            user_id="demo_user",
            session_id="demo_session",
            project_id="demo_project"
        )
        
        # 步骤1: 应用层接收用户请求
        self.logger.info("📱 步骤1: 应用层接收用户创建Agent请求")
        user_request = {
            "type": "create_agent",
            "data": {
                "agent_type": "openai",
                "name": "智能助手",
                "capabilities": ["conversation", "code_generation"],
                "requirements": {
                    "cpu_cores": 2,
                    "memory_mb": 4096
                }
            }
        }
        
        app_response = await application_communication_manager.communicator.send_request(
            "application",
            LayerRequest(operation="handle_user_request", parameters=user_request),
            context
        )
        
        self.logger.info(f"✅ 应用层处理结果: {app_response.data}")
        
        # 步骤2: 框架抽象层创建Agent
        self.logger.info("🎯 步骤2: 框架抽象层创建Agent")
        framework_response = await framework_communication_manager.communicator.send_request(
            "framework",
            LayerRequest(operation="create_agent", parameters=user_request["data"]),
            context
        )
        
        self.logger.info(f"✅ 框架抽象层处理结果: {framework_response.data}")
        
        # 步骤3: 适配器层创建具体Agent实例
        self.logger.info("🔌 步骤3: 适配器层创建具体Agent实例")
        adapter_response = await adapter_communication_manager.communicator.send_request(
            "adapter",
            LayerRequest(operation="create_agent_instance", parameters={
                "adapter_type": "openai",
                "agent_config": user_request["data"]
            }),
            context
        )
        
        self.logger.info(f"✅ 适配器层处理结果: {adapter_response.data}")
        
        # 步骤4: 基础设施层分配资源
        self.logger.info("🏗️ 步骤4: 基础设施层分配资源")
        infra_response = await infrastructure_communication_manager.communicator.send_request(
            "infrastructure",
            LayerRequest(operation="allocate_resources", parameters={
                "resource_type": "agent_instance",
                "requirements": user_request["data"]["requirements"]
            }),
            context
        )
        
        self.logger.info(f"✅ 基础设施层处理结果: {infra_response.data}")
        
        return {
            "agent_creation_flow": "completed",
            "agent_id": framework_response.data.get("agent_id"),
            "allocated_resources": infra_response.data
        }
    
    async def demo_workflow_execution_flow(self):
        """演示工作流执行流程"""
        self.logger.info("⚙️ === 工作流执行流程演示 ===")
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id=f"workflow_execution_{int(time.time())}",
            user_id="demo_user",
            session_id="demo_session",
            project_id="demo_project"
        )
        
        # 步骤1: 应用层编排工作流
        self.logger.info("📱 步骤1: 应用层编排工作流")
        workflow_config = {
            "name": "数据分析工作流",
            "steps": [
                {"name": "数据收集", "type": "agent_task", "agent_id": "agent_001"},
                {"name": "数据清洗", "type": "agent_task", "agent_id": "agent_002"},
                {"name": "数据分析", "type": "agent_task", "agent_id": "agent_003"},
                {"name": "报告生成", "type": "agent_task", "agent_id": "agent_004"}
            ],
            "input_data": {"dataset": "sample_data.csv"}
        }
        
        app_response = await application_communication_manager.communicator.send_request(
            "application",
            LayerRequest(operation="orchestrate_workflow", parameters=workflow_config),
            context
        )
        
        self.logger.info(f"✅ 应用层编排结果: {app_response.data}")
        
        # 步骤2: 业务能力层创建工作流
        self.logger.info("💼 步骤2: 业务能力层创建工作流")
        business_response = await business_communication_manager.communicator.send_request(
            "business",
            LayerRequest(operation="create_workflow", parameters=workflow_config),
            context
        )
        
        self.logger.info(f"✅ 业务能力层处理结果: {business_response.data}")
        
        # 步骤3: 执行工作流
        self.logger.info("🔄 步骤3: 执行工作流")
        execution_response = await business_communication_manager.communicator.send_request(
            "business",
            LayerRequest(operation="execute_workflow", parameters={
                "workflow_id": business_response.data["workflow_id"],
                "input_data": workflow_config["input_data"]
            }),
            context
        )
        
        self.logger.info(f"✅ 工作流执行结果: {execution_response.data}")
        
        return {
            "workflow_execution_flow": "completed",
            "workflow_id": business_response.data["workflow_id"],
            "execution_result": execution_response.data
        }
    
    async def demo_collaboration_flow(self):
        """演示协作流程"""
        self.logger.info("🤝 === 协作流程演示 ===")
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id=f"collaboration_{int(time.time())}",
            user_id="demo_user",
            session_id="demo_session",
            project_id="demo_project"
        )
        
        # 步骤1: 业务能力层执行协作
        self.logger.info("💼 步骤1: 业务能力层执行协作")
        collaboration_config = {
            "pattern": "expert_consultation",
            "participants": ["data_analyst", "domain_expert", "report_writer"],
            "task": "分析销售数据并提供改进建议"
        }
        
        business_response = await business_communication_manager.communicator.send_request(
            "business",
            LayerRequest(operation="execute_collaboration", parameters=collaboration_config),
            context
        )
        
        self.logger.info(f"✅ 业务能力层协作结果: {business_response.data}")
        
        # 步骤2: 认知架构层分析协作
        self.logger.info("🧠 步骤2: 认知架构层分析协作")
        cognitive_response = await cognitive_communication_manager.communicator.send_request(
            "cognitive",
            LayerRequest(operation="analyze_collaboration", parameters={
                "pattern": collaboration_config["pattern"],
                "participants": collaboration_config["participants"]
            }),
            context
        )
        
        self.logger.info(f"✅ 认知架构层分析结果: {cognitive_response.data}")
        
        return {
            "collaboration_flow": "completed",
            "collaboration_id": business_response.data["collaboration_id"],
            "analysis_result": cognitive_response.data
        }
    
    async def demo_system_health_check(self):
        """演示系统健康检查"""
        self.logger.info("🏥 === 系统健康检查演示 ===")
        
        # 创建执行上下文
        context = ExecutionContext(
            request_id=f"health_check_{int(time.time())}",
            user_id="system",
            session_id="system_session",
            project_id="system"
        )
        
        # 步骤1: 应用层获取系统状态
        self.logger.info("📱 步骤1: 应用层获取系统状态")
        app_response = await application_communication_manager.communicator.send_request(
            "application",
            LayerRequest(operation="get_application_status", parameters={}),
            context
        )
        
        self.logger.info(f"✅ 应用层状态: {app_response.data}")
        
        # 步骤2: 基础设施层健康检查
        self.logger.info("🏗️ 步骤2: 基础设施层健康检查")
        infra_response = await infrastructure_communication_manager.communicator.send_request(
            "infrastructure",
            LayerRequest(operation="get_system_health", parameters={}),
            context
        )
        
        self.logger.info(f"✅ 基础设施层健康状态: {infra_response.data}")
        
        # 步骤3: 获取性能指标
        self.logger.info("📊 步骤3: 获取性能指标")
        perf_response = await infrastructure_communication_manager.communicator.send_request(
            "infrastructure",
            LayerRequest(operation="get_performance_metrics", parameters={}),
            context
        )
        
        self.logger.info(f"✅ 性能指标: {perf_response.data}")
        
        return {
            "system_health_check": "completed",
            "application_status": app_response.data,
            "infrastructure_health": infra_response.data,
            "performance_metrics": perf_response.data
        }
    
    async def demo_event_monitoring(self):
        """演示事件监控"""
        self.logger.info("👁️ === 事件监控演示 ===")
        
        # 显示接收到的事件
        self.logger.info(f"📈 总共接收到 {len(self.event_monitor.events_received)} 个事件:")
        
        for i, event in enumerate(self.event_monitor.events_received, 1):
            self.logger.info(f"  {i}. {event['timestamp']}: {event['source_layer']} -> {event['event_type']}")
        
        # 按层统计事件
        layer_events = {}
        for event in self.event_monitor.events_received:
            layer = event['source_layer']
            if layer not in layer_events:
                layer_events[layer] = 0
            layer_events[layer] += 1
        
        self.logger.info("📊 各层事件统计:")
        for layer, count in layer_events.items():
            self.logger.info(f"  {layer}: {count} 个事件")
        
        return {
            "event_monitoring": "completed",
            "total_events": len(self.event_monitor.events_received),
            "layer_statistics": layer_events
        }
    
    async def run_complete_demo(self):
        """运行完整演示"""
        self.logger.info("🎬 === 开始完整层间通信演示 ===")
        
        try:
            # 演示1: Agent创建流程
            agent_result = await self.demo_complete_agent_creation_flow()
            
            # 演示2: 工作流执行流程
            workflow_result = await self.demo_workflow_execution_flow()
            
            # 演示3: 协作流程
            collaboration_result = await self.demo_collaboration_flow()
            
            # 演示4: 系统健康检查
            health_result = await self.demo_system_health_check()
            
            # 演示5: 事件监控
            event_result = await self.demo_event_monitoring()
            
            # 总结
            self.logger.info("🎉 === 演示完成 ===")
            self.logger.info(f"✅ Agent创建: {agent_result['agent_creation_flow']}")
            self.logger.info(f"✅ 工作流执行: {workflow_result['workflow_execution_flow']}")
            self.logger.info(f"✅ 协作流程: {collaboration_result['collaboration_flow']}")
            self.logger.info(f"✅ 系统健康检查: {health_result['system_health_check']}")
            self.logger.info(f"✅ 事件监控: {event_result['event_monitoring']}")
            
            return {
                "demo_status": "completed",
                "results": {
                    "agent_creation": agent_result,
                    "workflow_execution": workflow_result,
                    "collaboration": collaboration_result,
                    "system_health": health_result,
                    "event_monitoring": event_result
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ 演示过程中发生错误: {e}")
            raise


async def main():
    """主函数"""
    demo = LayerCommunicationDemo()
    result = await demo.run_complete_demo()
    return result


if __name__ == "__main__":
    asyncio.run(main()) 