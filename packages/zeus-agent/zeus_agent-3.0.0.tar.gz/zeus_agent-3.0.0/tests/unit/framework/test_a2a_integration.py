"""
A2A Protocol Integration Tests
测试A2A协议与适配器的集成功能
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import pytest_asyncio

from layers.framework.abstractions.a2a_protocol import (
    A2AMessageType,
    A2ACapabilityType,
    A2AProtocolVersion,
    A2ACapability,
    A2AAgentProfile,
    A2AMessage,
    A2AHTTPTransport,
    A2AProtocolHandler,
    create_a2a_capability,
    create_a2a_agent_profile
)
from layers.framework.abstractions.a2a_integration import (
    A2AIntegrationManager,
    A2AAdapterBridge,
    A2AMessageRouter
)
from layers.framework.abstractions.task import TaskType, UniversalTask
from layers.framework.abstractions.result import ResultStatus, UniversalResult
from layers.framework.abstractions.context import UniversalContext


class MockAdapter:
    """模拟适配器"""
    def __init__(self, name="mock_adapter"):
        self.name = name
        self.info = {
            "name": name,
            "version": "1.0",
            "capabilities": ["text_processing", "code_generation", "task_coordination"]
        }
    
    def get_info(self):
        return Mock(**self.info)
    
    async def execute_task(self, task, context):
        return UniversalResult(
            content={"reply": "Mock response"},
            status=ResultStatus.SUCCESS,
            result_type=TaskType.CONVERSATION
        )


@pytest.mark.asyncio
class TestA2AIntegration:
    """测试A2A协议与适配器的集成"""
    
    @pytest_asyncio.fixture
    async def integration_setup(self):
        """设置集成测试环境"""
        # 创建模拟适配器
        adapter = MockAdapter()
        
        # 创建A2A协议处理器
        capability = create_a2a_capability(A2ACapabilityType.TEXT_PROCESSING)
        profile = create_a2a_agent_profile(
            agent_id="test_agent",
            agent_name="Test Agent",
            capabilities=[capability]
        )
        transport = A2AHTTPTransport()
        protocol_handler = A2AProtocolHandler(profile, transport)
        
        # 创建集成管理器
        integration_manager = A2AIntegrationManager()
        
        # 创建适配器桥接器
        adapter_bridge = A2AAdapterBridge(adapter, protocol_handler)
        
        # 创建消息路由器
        message_router = A2AMessageRouter()
        
        # 注册组件
        integration_manager.register_adapter_bridge(adapter_bridge)
        integration_manager.register_message_router(message_router)
        
        # 注册测试用的授权Agent
        integration_manager._authorized_agents.add("agent1")
        integration_manager._authorized_agents.add("test_agent")
        
        await transport.connect("http://test-endpoint")
        yield {
            "adapter": adapter,
            "protocol_handler": protocol_handler,
            "integration_manager": integration_manager,
            "adapter_bridge": adapter_bridge,
            "message_router": message_router
        }
        await transport.disconnect()
    
    async def test_adapter_bridge_initialization(self, integration_setup):
        """测试适配器桥接器初始化"""
        bridge = integration_setup["adapter_bridge"]
        
        assert bridge.adapter is not None
        assert bridge.protocol_handler is not None
        assert bridge.is_ready()
        
        # 验证能力映射
        capabilities = bridge.get_mapped_capabilities()
        assert len(capabilities) > 0
        assert any(cap.capability_type == A2ACapabilityType.TEXT_PROCESSING for cap in capabilities)
    
    async def test_message_routing(self, integration_setup):
        """测试消息路由"""
        router = integration_setup["message_router"]
        protocol_handler = integration_setup["protocol_handler"]
        
        # 创建测试消息
        message = A2AMessage(
            message_id="test_route",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.TASK_REQUEST,
            sender_id="agent1",
            receiver_id="agent2",
            timestamp=datetime.now(),
            payload={"task": "test routing"}
        )
        
        # 注册路由处理器
        async def test_handler(msg):
            return A2AMessage(
                message_id="response",
                protocol_version=A2AProtocolVersion.V2_0,
                message_type=A2AMessageType.TASK_RESPONSE,
                sender_id="agent2",
                receiver_id="agent1",
                timestamp=datetime.now(),
                correlation_id=msg.message_id,
                payload={"result": "routed"}
            )
        
        router.register_handler(A2AMessageType.TASK_REQUEST, test_handler)
        
        # 测试路由
        response = await router.route_message(message)
        assert response is not None
        assert response.message_type == A2AMessageType.TASK_RESPONSE
        assert response.correlation_id == "test_route"
    
    async def test_task_execution_through_bridge(self, integration_setup):
        """测试通过桥接器执行任务"""
        bridge = integration_setup["adapter_bridge"]
        
        # 创建任务请求消息
        task_message = A2AMessage(
            message_id="test_task",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.TASK_REQUEST,
            sender_id="agent1",
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={
                "task_type": "conversation",
                "content": "Hello, how are you?",
                "parameters": {}
            }
        )
        
        # 执行任务
        result = await bridge.execute_task(task_message)
        
        assert result is not None
        assert result.message_type == A2AMessageType.TASK_RESPONSE
        assert result.correlation_id == "test_task"
        assert "reply" in result.payload
    
    async def test_capability_mapping(self, integration_setup):
        """测试能力映射"""
        bridge = integration_setup["adapter_bridge"]
        
        # 获取适配器能力
        adapter_capabilities = bridge.adapter.get_info().capabilities
        
        # 获取映射后的A2A能力
        a2a_capabilities = bridge.get_mapped_capabilities()
        
        # 验证映射关系
        assert len(adapter_capabilities) > 0
        assert len(a2a_capabilities) > 0
        
        # 验证核心能力是否正确映射
        core_capabilities = {
            "text_processing": A2ACapabilityType.TEXT_PROCESSING,
            "code_generation": A2ACapabilityType.CODE_GENERATION,
            "task_coordination": A2ACapabilityType.TASK_COORDINATION
        }
        
        for adapter_cap in adapter_capabilities:
            if adapter_cap in core_capabilities:
                assert any(cap.capability_type == core_capabilities[adapter_cap] 
                         for cap in a2a_capabilities)
    
    async def test_integration_manager_coordination(self, integration_setup):
        """测试集成管理器的协调功能"""
        manager = integration_setup["integration_manager"]
        
        # 创建测试消息
        message = A2AMessage(
            message_id="test_coordination",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.COLLABORATION_INVITE,
            sender_id="agent1",
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={
                "collaboration_type": "team_task",
                "task": "Solve this problem together",
                "participants": ["agent1", "test_agent"],
                "collaboration_id": "test_coordination"  # 显式设置ID
            }
        )
        
        # 测试消息处理和协调
        result = await manager.handle_message(message)
        
        assert result is not None
        assert result.message_type == A2AMessageType.COLLABORATION_ACCEPT
        assert result.correlation_id == "test_coordination"
        
        # 验证协作状态
        collaboration = manager.get_active_collaboration("test_coordination")
        assert collaboration is not None
        assert collaboration["status"] == "active"
        assert len(collaboration["participants"]) == 2
    
    async def test_error_handling_and_recovery(self, integration_setup):
        """测试错误处理和恢复机制"""
        bridge = integration_setup["adapter_bridge"]
        manager = integration_setup["integration_manager"]
        
        # 模拟错误情况
        with patch.object(bridge.adapter, 'execute_task', 
                         side_effect=Exception("Simulated error")):
            
            # 创建任务消息
            message = A2AMessage(
                message_id="test_error",
                protocol_version=A2AProtocolVersion.V2_0,
                message_type=A2AMessageType.TASK_REQUEST,
                sender_id="agent1",
                receiver_id="test_agent",
                timestamp=datetime.now(),
                payload={"task": "This will fail"}
            )
            
            # 测试错误处理
            result = await manager.handle_message(message)
            
            assert result is not None
            assert result.message_type == A2AMessageType.ERROR_REPORT
            assert result.payload["error_type"] == "execution_error"
            assert "Simulated error" in result.payload["error_message"]
            
            # 验证错误恢复
            assert manager.is_healthy()
            assert bridge.is_ready()
    
    async def test_message_validation_and_security(self, integration_setup):
        """测试消息验证和安全机制"""
        manager = integration_setup["integration_manager"]
        
        # 测试无效消息
        invalid_message = A2AMessage(
            message_id="test_invalid",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.TASK_REQUEST,
            sender_id="unknown_agent",  # 未注册的发送者
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={"task": "Invalid request"}
        )
        
        # 验证消息处理
        result = await manager.handle_message(invalid_message)
        
        assert result is not None
        assert result.message_type == A2AMessageType.ERROR_REPORT
        assert result.payload["error_type"] == "unauthorized"
        
        # 测试消息完整性
        tampered_message = A2AMessage(
            message_id="test_tampered",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.TASK_REQUEST,
            sender_id="agent1",  # 使用授权的发送者
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={"task": "Tampered request"},
            signature="invalid_signature"  # 无效签名
        )
        
        result = await manager.handle_message(tampered_message)
        
        assert result is not None
        assert result.message_type == A2AMessageType.ERROR_REPORT
        assert result.payload["error_type"] == "integrity_error" 