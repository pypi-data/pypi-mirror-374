"""
Business Capability Layer Communication Manager - 业务能力层通信管理器
集成层间通信协议，为业务能力层提供通信能力
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from ..framework.abstractions.layer_communication import (
    LayerCommunicationManager,
    LayerMessage,
    LayerMessageType,
    LayerMessageStatus,
    LayerMessagePriority,
    LayerMessageHandler,
    LayerMessageRouter,
    LayerMessageQueue,
    LayerMessageFilter,
    LayerMessageTransformer,
    LayerMessageValidator,
    LayerMessageLogger
)

logger = logging.getLogger(__name__)


class BusinessCommunicationManager:
    """业务能力层通信管理器"""
    
    def __init__(self):
        # 创建层间通信组件
        self.router = LayerMessageRouter()
        self.queue = LayerMessageQueue()
        self.filter = LayerMessageFilter()
        self.transformer = LayerMessageTransformer()
        self.validator = LayerMessageValidator()
        self.message_logger = LayerMessageLogger()
        
        # 设置队列的路由器
        self.queue.set_router(self.router)
        
        # 创建层间通信管理器
        self.layer_comm = LayerCommunicationManager(
            router=self.router,
            queue=self.queue,
            filter=self.filter,
            transformer=self.transformer,
            validator=self.validator,
            logger=self.message_logger
        )
        
        self._register_handlers()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def _register_handlers(self):
        """注册业务能力层的消息处理器"""
        # 注册各种业务功能的处理器
        self.router.register_handler("create_project", self._handle_create_project)
        self.router.register_handler("manage_workflow", self._handle_manage_workflow)
        self.router.register_handler("coordinate_team", self._handle_coordinate_team)
        self.router.register_handler("execute_business_logic", self._handle_execute_business_logic)
        self.router.register_handler("manage_resources", self._handle_manage_resources)
        self.router.register_handler("generate_report", self._handle_generate_report)
        self.router.register_handler("handle_business_event", self._handle_business_event)
    
    async def _handle_create_project(self, message: LayerMessage) -> LayerMessage:
        """处理项目创建请求"""
        try:
            project_config = message.content.get("project_config", {})
            project_name = message.content.get("project_name")
            project_type = message.content.get("project_type", "default")
            
            # 模拟项目创建结果
            project_result = {
                "project_id": f"proj_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "project_name": project_name,
                "project_type": project_type,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Project created successfully: {project_name}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "project_result": project_result,
                    "project_name": project_name,
                    "project_type": project_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            # 返回错误响应
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_manage_workflow(self, message: LayerMessage) -> LayerMessage:
        """处理工作流管理请求"""
        try:
            from .workflows.workflow_engine import WorkflowEngine
            
            workflow_id = message.content.get('workflow_id')
            action = message.content.get('action', 'execute')
            workflow_config = message.content.get('config', {})
            
            # 创建工作流引擎
            workflow_engine = WorkflowEngine()
            
            # 执行工作流操作
            if action == 'execute':
                workflow_result = await workflow_engine.execute_workflow(workflow_id, workflow_config)
            elif action == 'pause':
                workflow_result = await workflow_engine.pause_workflow(workflow_id)
            elif action == 'resume':
                workflow_result = await workflow_engine.resume_workflow(workflow_id)
            elif action == 'stop':
                workflow_result = await workflow_engine.stop_workflow(workflow_id)
            else:
                raise ValueError(f"Unknown workflow action: {action}")
            
            self.logger.info(f"Workflow {action} completed for: {workflow_id}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "workflow_result": workflow_result,
                    "workflow_id": workflow_id,
                    "action": action
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to manage workflow: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_coordinate_team(self, message: LayerMessage) -> LayerMessage:
        """处理团队协调请求"""
        try:
            from .teams.collaboration_manager import CollaborationManager
            
            team_id = message.content.get('team_id')
            coordination_type = message.content.get('coordination_type', 'task_assignment')
            coordination_data = message.content.get('data', {})
            
            # 创建协作管理器
            collaboration_manager = CollaborationManager()
            
            # 执行团队协调
            coordination_result = await collaboration_manager.coordinate_team(
                team_id, coordination_type, coordination_data
            )
            
            self.logger.info(f"Team coordination completed: {coordination_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "coordination_result": coordination_result,
                    "team_id": team_id,
                    "coordination_type": coordination_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to coordinate team: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_execute_business_logic(self, message: LayerMessage) -> LayerMessage:
        """处理业务逻辑执行请求"""
        try:
            logic_type = message.content.get('logic_type')
            logic_params = message.content.get('params', {})
            context = message.content.get('context', {})
            
            # 根据业务逻辑类型执行相应操作
            if logic_type == 'validation':
                result = await self._execute_validation_logic(logic_params, context)
            elif logic_type == 'calculation':
                result = await self._execute_calculation_logic(logic_params, context)
            elif logic_type == 'decision':
                result = await self._execute_decision_logic(logic_params, context)
            else:
                raise ValueError(f"Unknown business logic type: {logic_type}")
            
            self.logger.info(f"Business logic executed: {logic_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "logic_result": result,
                    "logic_type": logic_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to execute business logic: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_manage_resources(self, message: LayerMessage) -> LayerMessage:
        """处理资源管理请求"""
        try:
            resource_type = message.content.get('resource_type')
            action = message.content.get('action', 'allocate')
            resource_data = message.content.get('data', {})
            
            # 执行资源管理操作
            if action == 'allocate':
                result = await self._allocate_resource(resource_type, resource_data)
            elif action == 'deallocate':
                result = await self._deallocate_resource(resource_type, resource_data)
            elif action == 'monitor':
                result = await self._monitor_resource(resource_type, resource_data)
            else:
                raise ValueError(f"Unknown resource action: {action}")
            
            self.logger.info(f"Resource {action} completed: {resource_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "resource_result": result,
                    "resource_type": resource_type,
                    "action": action
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to manage resources: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_generate_report(self, message: LayerMessage) -> LayerMessage:
        """处理报告生成请求"""
        try:
            report_type = message.content.get('report_type')
            report_params = message.content.get('params', {})
            output_format = message.content.get('format', 'json')
            
            # 生成报告
            report_result = await self._generate_business_report(
                report_type, report_params, output_format
            )
            
            self.logger.info(f"Report generated: {report_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "report_result": report_result,
                    "report_type": report_type,
                    "format": output_format
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    async def _handle_business_event(self, message: LayerMessage) -> LayerMessage:
        """处理业务事件"""
        try:
            event_type = message.content.get('event_type')
            event_data = message.content.get('data', {})
            
            # 处理业务事件
            event_result = await self._process_business_event(event_type, event_data)
            
            self.logger.info(f"Business event processed: {event_type}")
            
            # 创建响应消息
            response_message = LayerMessage(
                id=f"response_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={
                    "event_result": event_result,
                    "event_type": event_type
                },
                status=LayerMessageStatus.COMPLETED,
                
            )
            
            return response_message
            
        except Exception as e:
            self.logger.error(f"Failed to handle business event: {e}")
            error_message = LayerMessage(
                id=f"error_{message.id}",
                type=LayerMessageType.RESPONSE,
                source="business",
                target=message.source,
                content={"error": str(e)},
                status=LayerMessageStatus.FAILED,
                
            )
            return error_message
    
    # 辅助方法
    async def _execute_validation_logic(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行验证逻辑"""
        # 简化的验证逻辑实现
        return {"validation_result": True, "message": "Validation passed"}
    
    async def _execute_calculation_logic(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行计算逻辑"""
        # 简化的计算逻辑实现
        return {"calculation_result": 100, "message": "Calculation completed"}
    
    async def _execute_decision_logic(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行决策逻辑"""
        # 简化的决策逻辑实现
        return {"decision": "approve", "confidence": 0.8, "message": "Decision made"}
    
    async def _allocate_resource(self, resource_type: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """分配资源"""
        return {"resource_id": f"{resource_type}_001", "status": "allocated"}
    
    async def _deallocate_resource(self, resource_type: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """释放资源"""
        return {"resource_id": resource_data.get('resource_id'), "status": "deallocated"}
    
    async def _monitor_resource(self, resource_type: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """监控资源"""
        return {"resource_status": "healthy", "usage": "70%"}
    
    async def _generate_business_report(self, report_type: str, params: Dict[str, Any], output_format: str) -> Dict[str, Any]:
        """生成业务报告"""
        return {
            "report_id": f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": f"Sample {report_type} report",
            "format": output_format,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _process_business_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理业务事件"""
        return {
            "event_processed": True,
            "event_type": event_type,
            "processed_at": datetime.now().isoformat()
        }
    
    async def send_message(self, message: LayerMessage) -> LayerMessage:
        """发送消息到其他层"""
        return await self.layer_comm.send_message(message)
    
    async def process_message(self, message: LayerMessage) -> LayerMessage:
        """处理接收到的消息"""
        return await self.layer_comm.process_message(message)
    
    def get_status(self) -> Dict[str, Any]:
        """获取通信管理器状态"""
        return {
            "component": "BusinessCommunicationManager",
            "layer": "business",
            "handlers_registered": len(self.router.handlers) if hasattr(self.router, "handlers") else 0,
            "queue_size": self.queue.size(),
            "layer_comm_status": self.layer_comm.get_status() if hasattr(self.layer_comm, 'get_status') else {}
        } 