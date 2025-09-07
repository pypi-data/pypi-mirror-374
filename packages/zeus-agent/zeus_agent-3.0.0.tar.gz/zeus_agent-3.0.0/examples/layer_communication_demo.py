"""
Layer Communication Demo - 层间通信协议使用示例
演示7层架构间的通信机制
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any

# 导入层间通信协议
from layers.framework.abstractions.layer_communication import (
    LayerCommunicationManager,
    LayerRequest,
    LayerResponse,
    ExecutionContext,
    MessageType,
    LayerEventHandler
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessLayerHandler:
    """业务能力层处理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("business")
        self._register_handlers()
    
    def _register_handlers(self):
        """注册请求处理器"""
        self.communicator.register_request_handler("create_workflow", self._handle_create_workflow)
        self.communicator.register_request_handler("execute_collaboration", self._handle_execute_collaboration)
    
    async def _handle_create_workflow(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理创建工作流请求"""
        logger.info(f"Business layer: Creating workflow with parameters: {payload['parameters']}")
        
        # 模拟工作流创建
        workflow_id = f"workflow_{int(time.time())}"
        
        # 发布工作流创建事件
        await self.communicator.publish_event(
            "workflow_created",
            {"workflow_id": workflow_id, "parameters": payload['parameters']},
            context
        )
        
        return {"workflow_id": workflow_id, "status": "created"}
    
    async def _handle_execute_collaboration(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理执行协作请求"""
        logger.info(f"Business layer: Executing collaboration with pattern: {payload['parameters']['pattern']}")
        
        # 调用认知架构层进行智能决策
        cognitive_request = LayerRequest(
            operation="analyze_collaboration",
            parameters={
                "pattern": payload['parameters']['pattern'],
                "participants": payload['parameters']['participants']
            }
        )
        
        response = await self.communicator.send_request(
            "cognitive",
            cognitive_request,
            context
        )
        
        if response.success:
            return {
                "collaboration_id": f"collab_{int(time.time())}",
                "analysis_result": response.data,
                "status": "executing"
            }
        else:
            return {"error": response.error}


class CognitiveLayerHandler:
    """认知架构层处理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("cognitive")
        self._register_handlers()
    
    def _register_handlers(self):
        """注册请求处理器"""
        self.communicator.register_request_handler("analyze_collaboration", self._handle_analyze_collaboration)
        self.communicator.register_request_handler("reason_about_task", self._handle_reason_about_task)
    
    async def _handle_analyze_collaboration(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理协作分析请求"""
        logger.info(f"Cognitive layer: Analyzing collaboration pattern: {payload['parameters']['pattern']}")
        
        # 模拟认知分析
        analysis_result = {
            "optimal_strategy": "sequential_execution",
            "estimated_duration": 120,
            "resource_requirements": {"cpu": 2, "memory": "4GB"},
            "confidence_score": 0.85
        }
        
        # 发布认知分析完成事件
        await self.communicator.publish_event(
            "collaboration_analyzed",
            {"analysis_result": analysis_result},
            context
        )
        
        return analysis_result
    
    async def _handle_reason_about_task(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理任务推理请求"""
        logger.info(f"Cognitive layer: Reasoning about task: {payload['parameters']['task_description']}")
        
        # 调用框架抽象层获取Agent能力
        framework_request = LayerRequest(
            operation="get_agent_capabilities",
            parameters={"agent_type": payload['parameters']['agent_type']}
        )
        
        response = await self.communicator.send_request(
            "framework",
            framework_request,
            context
        )
        
        if response.success:
            # 基于Agent能力进行推理
            reasoning_result = {
                "task_complexity": "medium",
                "required_capabilities": response.data,
                "execution_plan": ["perception", "reasoning", "action"],
                "confidence": 0.92
            }
            return reasoning_result
        else:
            return {"error": "Failed to get agent capabilities"}


class FrameworkLayerHandler:
    """框架抽象层处理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("framework")
        self._register_handlers()
    
    def _register_handlers(self):
        """注册请求处理器"""
        self.communicator.register_request_handler("get_agent_capabilities", self._handle_get_agent_capabilities)
        self.communicator.register_request_handler("create_agent", self._handle_create_agent)
    
    async def _handle_get_agent_capabilities(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理获取Agent能力请求"""
        agent_type = payload['parameters']['agent_type']
        logger.info(f"Framework layer: Getting capabilities for agent type: {agent_type}")
        
        # 模拟Agent能力查询
        capabilities = {
            "openai": ["conversation", "code_generation", "analysis"],
            "autogen": ["multi_agent_collaboration", "task_decomposition"],
            "custom": ["domain_specific", "custom_tools"]
        }
        
        return capabilities.get(agent_type, [])
    
    async def _handle_create_agent(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理创建Agent请求"""
        logger.info(f"Framework layer: Creating agent with config: {payload['parameters']}")
        
        # 调用适配器层创建具体Agent
        adapter_request = LayerRequest(
            operation="create_agent_instance",
            parameters=payload['parameters']
        )
        
        response = await self.communicator.send_request(
            "adapter",
            adapter_request,
            context
        )
        
        if response.success:
            return {
                "agent_id": response.data['agent_id'],
                "agent_type": payload['parameters']['agent_type'],
                "status": "created"
            }
        else:
            return {"error": response.error}


class AdapterLayerHandler:
    """适配器层处理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("adapter")
        self._register_handlers()
    
    def _register_handlers(self):
        """注册请求处理器"""
        self.communicator.register_request_handler("create_agent_instance", self._handle_create_agent_instance)
        self.communicator.register_request_handler("execute_task", self._handle_execute_task)
    
    async def _handle_create_agent_instance(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理创建Agent实例请求"""
        logger.info(f"Adapter layer: Creating agent instance: {payload['parameters']['agent_type']}")
        
        # 调用基础设施层获取资源
        infrastructure_request = LayerRequest(
            operation="allocate_resources",
            parameters={
                "resource_type": "agent_instance",
                "requirements": payload['parameters'].get('requirements', {})
            }
        )
        
        response = await self.communicator.send_request(
            "infrastructure",
            infrastructure_request,
            context
        )
        
        if response.success:
            agent_id = f"agent_{payload['parameters']['agent_type']}_{int(time.time())}"
            return {
                "agent_id": agent_id,
                "allocated_resources": response.data,
                "status": "ready"
            }
        else:
            return {"error": "Failed to allocate resources"}
    
    async def _handle_execute_task(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理执行任务请求"""
        logger.info(f"Adapter layer: Executing task: {payload['parameters']['task']}")
        
        # 模拟任务执行
        await asyncio.sleep(0.1)  # 模拟执行时间
        
        return {
            "task_id": f"task_{int(time.time())}",
            "result": f"Task completed: {payload['parameters']['task']}",
            "execution_time": 0.1
        }


class InfrastructureLayerHandler:
    """基础设施层处理器"""
    
    def __init__(self):
        self.communicator = LayerCommunicationManager().get_communicator("infrastructure")
        self._register_handlers()
    
    def _register_handlers(self):
        """注册请求处理器"""
        self.communicator.register_request_handler("allocate_resources", self._handle_allocate_resources)
        self.communicator.register_request_handler("get_config", self._handle_get_config)
    
    async def _handle_allocate_resources(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理资源分配请求"""
        logger.info(f"Infrastructure layer: Allocating resources: {payload['parameters']}")
        
        # 模拟资源分配
        allocated_resources = {
            "cpu_cores": 2,
            "memory_mb": 4096,
            "storage_gb": 10,
            "network_bandwidth": "100Mbps"
        }
        
        # 发布资源分配事件
        await self.communicator.publish_event(
            "resources_allocated",
            {"allocated_resources": allocated_resources},
            context
        )
        
        return allocated_resources
    
    async def _handle_get_config(self, payload: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """处理配置获取请求"""
        logger.info(f"Infrastructure layer: Getting config for: {payload['parameters']['config_key']}")
        
        # 模拟配置获取
        configs = {
            "openai": {"api_key": "***", "model": "gpt-4"},
            "database": {"url": "postgresql://localhost/adc"},
            "cache": {"redis_url": "redis://localhost:6379"}
        }
        
        config_key = payload['parameters']['config_key']
        return configs.get(config_key, {})


class EventMonitor(LayerEventHandler):
    """事件监控器 - 监听所有层间事件"""
    
    def __init__(self):
        self.events_received = []
    
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
        logger.info(f"Event received: {event_info}")


async def demo_layer_communication():
    """演示层间通信"""
    logger.info("=== 层间通信协议演示 ===")
    
    # 初始化各层处理器
    business_handler = BusinessLayerHandler()
    cognitive_handler = CognitiveLayerHandler()
    framework_handler = FrameworkLayerHandler()
    adapter_handler = AdapterLayerHandler()
    infrastructure_handler = InfrastructureLayerHandler()
    
    # 创建事件监控器
    event_monitor = EventMonitor()
    
    # 订阅事件
    for handler in [business_handler, cognitive_handler, framework_handler, adapter_handler, infrastructure_handler]:
        handler.communicator.subscribe_to_events("*", event_monitor)
    
    # 创建执行上下文
    context = ExecutionContext(
        request_id=f"req_{int(time.time())}",
        user_id="demo_user",
        session_id="demo_session",
        project_id="demo_project"
    )
    
    # 演示1: 创建协作工作流
    logger.info("\n--- 演示1: 创建协作工作流 ---")
    workflow_request = LayerRequest(
        operation="create_workflow",
        parameters={
            "name": "数据分析工作流",
            "steps": ["数据收集", "数据清洗", "数据分析", "报告生成"]
        }
    )
    
    response = await business_handler.communicator.send_request(
        "business",
        workflow_request,
        context
    )
    
    logger.info(f"工作流创建结果: {response.data}")
    
    # 演示2: 执行多Agent协作
    logger.info("\n--- 演示2: 执行多Agent协作 ---")
    collaboration_request = LayerRequest(
        operation="execute_collaboration",
        parameters={
            "pattern": "expert_consultation",
            "participants": ["data_analyst", "domain_expert", "report_writer"]
        }
    )
    
    response = await business_handler.communicator.send_request(
        "business",
        collaboration_request,
        context
    )
    
    logger.info(f"协作执行结果: {response.data}")
    
    # 演示3: 创建Agent
    logger.info("\n--- 演示3: 创建Agent ---")
    agent_request = LayerRequest(
        operation="create_agent",
        parameters={
            "agent_type": "openai",
            "name": "数据分析助手",
            "capabilities": ["data_analysis", "report_generation"]
        }
    )
    
    response = await framework_handler.communicator.send_request(
        "framework",
        agent_request,
        context
    )
    
    logger.info(f"Agent创建结果: {response.data}")
    
    # 显示事件统计
    logger.info(f"\n--- 事件统计 ---")
    logger.info(f"总共接收到 {len(event_monitor.events_received)} 个事件:")
    for event in event_monitor.events_received:
        logger.info(f"  - {event['timestamp']}: {event['source_layer']} -> {event['event_type']}")
    
    # 显示执行上下文
    logger.info(f"\n--- 执行上下文 ---")
    logger.info(f"执行栈: {' -> '.join(context.execution_stack)}")
    logger.info(f"层执行时间: {context.layer_timings}")
    logger.info(f"错误数量: {len(context.errors)}")
    logger.info(f"警告数量: {len(context.warnings)}")


if __name__ == "__main__":
    asyncio.run(demo_layer_communication()) 