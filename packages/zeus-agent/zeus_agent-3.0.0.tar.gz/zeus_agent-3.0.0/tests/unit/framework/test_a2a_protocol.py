"""
A2A Protocol Tests
测试A2A协议的基本功能和消息处理
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
    A2AWebSocketTransport,
    A2AProtocolHandler,
    create_a2a_capability,
    create_a2a_agent_profile
)


class TestA2ADataStructures:
    """测试A2A协议的基本数据结构"""
    
    def test_capability_creation(self):
        """测试能力创建"""
        capability = create_a2a_capability(
            capability_type=A2ACapabilityType.TEXT_PROCESSING,
            version="1.0",
            description="Test capability",
            input_formats=["text"],
            output_formats=["json"]
        )
        
        assert capability.capability_type == A2ACapabilityType.TEXT_PROCESSING
        assert capability.version == "1.0"
        assert capability.description == "Test capability"
        assert capability.input_formats == ["text"]
        assert capability.output_formats == ["json"]
        assert isinstance(capability.parameters, dict)
        assert isinstance(capability.constraints, dict)
        assert isinstance(capability.performance_metrics, dict)
    
    def test_agent_profile_creation(self):
        """测试Agent配置文件创建"""
        capability = create_a2a_capability(A2ACapabilityType.TEXT_PROCESSING)
        profile = create_a2a_agent_profile(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            capabilities=[capability]
        )
        
        assert profile.agent_id == "test_agent"
        assert profile.agent_name == "Test Agent"
        assert profile.agent_type == "test"
        assert profile.version == "1.0"
        assert len(profile.capabilities) == 1
        assert profile.supported_protocols == [A2AProtocolVersion.V2_0]
        assert "test_agent" in profile.endpoint
    
    def test_message_creation(self):
        """测试消息创建和序列化"""
        message = A2AMessage(
            message_id="test_msg_1",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.HANDSHAKE,
            sender_id="agent1",
            receiver_id="agent2",
            timestamp=datetime.now(),
            payload={"test": "data"}
        )
        
        # 测试基本属性
        assert message.message_id == "test_msg_1"
        assert message.protocol_version == A2AProtocolVersion.V2_0
        assert message.message_type == A2AMessageType.HANDSHAKE
        assert message.sender_id == "agent1"
        assert message.receiver_id == "agent2"
        assert isinstance(message.timestamp, datetime)
        assert message.payload == {"test": "data"}
        
        # 测试序列化
        message_dict = message.to_dict()
        assert isinstance(message_dict, dict)
        assert message_dict["message_id"] == "test_msg_1"
        assert message_dict["protocol_version"] == "2.0"
        assert message_dict["message_type"] == "handshake"
        
        # 测试反序列化
        restored_message = A2AMessage.from_dict(message_dict)
        assert restored_message.message_id == message.message_id
        assert restored_message.protocol_version == message.protocol_version
        assert restored_message.message_type == message.message_type


class TestA2ATransport:
    """测试A2A传输层实现"""
    
    @pytest.mark.asyncio
    async def test_http_transport(self):
        """测试HTTP传输"""
        transport = A2AHTTPTransport()
        
        # 测试连接
        success = await transport.connect("http://test-endpoint")
        assert success
        assert "http://test-endpoint" in transport.connections
        
        # 测试消息发送
        message = A2AMessage(
            message_id="test_msg",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.HANDSHAKE,
            sender_id="agent1",
            receiver_id="agent2",
            timestamp=datetime.now(),
            payload={"test": "data"}
        )
        
        success = await transport.send_message(message, "http://test-endpoint")
        assert success
        
        # 测试断开连接
        success = await transport.disconnect()
        assert success
        assert len(transport.connections) == 0
    
    @pytest.mark.asyncio
    async def test_websocket_transport(self):
        """测试WebSocket传输"""
        transport = A2AWebSocketTransport()
        
        # 测试连接
        success = await transport.connect("ws://test-endpoint")
        assert success
        assert "ws://test-endpoint" in transport.websockets
        
        # 测试消息发送
        message = A2AMessage(
            message_id="test_msg",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.HANDSHAKE,
            sender_id="agent1",
            receiver_id="agent2",
            timestamp=datetime.now(),
            payload={"test": "data"}
        )
        
        success = await transport.send_message(message, "ws://test-endpoint")
        assert success
        
        # 测试断开连接
        success = await transport.disconnect()
        assert success
        assert len(transport.websockets) == 0


@pytest.mark.asyncio
class TestA2AProtocolHandler:
    """测试A2A协议处理器"""
    
    @pytest_asyncio.fixture
    async def protocol_handler(self):
        """创建协议处理器实例"""
        capability = create_a2a_capability(A2ACapabilityType.TEXT_PROCESSING)
        profile = create_a2a_agent_profile(
            agent_id="test_agent",
            agent_name="Test Agent",
            capabilities=[capability]
        )
        transport = A2AHTTPTransport()
        handler = A2AProtocolHandler(profile, transport)
        await transport.connect("http://test-endpoint")
        yield handler
        await transport.disconnect()
    
    async def test_handshake(self, protocol_handler):
        """测试握手过程"""
        # 创建握手消息
        handshake_message = A2AMessage(
            message_id="test_handshake",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.HANDSHAKE,
            sender_id="remote_agent",
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={
                "agent_profile": {
                    "agent_id": "remote_agent",
                    "agent_name": "Remote Agent",
                    "agent_type": "test",
                    "version": "1.0",
                    "capabilities": [],
                    "supported_protocols": ["2.0"],
                    "endpoint": "http://remote-agent"
                }
            }
        )
        
        # 处理握手消息
        response = await protocol_handler.process_message(handshake_message)
        
        # 验证响应
        assert response is not None
        assert response.message_type == A2AMessageType.HANDSHAKE
        assert response.receiver_id == "remote_agent"
        assert response.correlation_id == "test_handshake"
        assert response.payload["handshake_accepted"] is True
    
    async def test_capability_exchange(self, protocol_handler):
        """测试能力交换"""
        # 创建能力交换消息
        exchange_message = A2AMessage(
            message_id="test_exchange",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type=A2AMessageType.CAPABILITY_EXCHANGE,
            sender_id="remote_agent",
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={
                "capabilities": [
                    {
                        "type": "text_processing",
                        "version": "1.0",
                        "description": "Remote capability",
                        "input_formats": ["text"],
                        "output_formats": ["json"]
                    }
                ]
            }
        )
        
        # 处理能力交换消息
        response = await protocol_handler.process_message(exchange_message)
        
        # 验证响应
        assert response is not None
        assert response.message_type == A2AMessageType.CAPABILITY_EXCHANGE
        assert response.receiver_id == "remote_agent"
        assert response.correlation_id == "test_exchange"
        assert response.payload["compatibility_status"] == "compatible"
    
    async def test_task_request(self, protocol_handler):
        """测试任务请求"""
        # 发送任务请求
        correlation_id = await protocol_handler.send_task_request(
            target_agent_id="remote_agent",
            target_endpoint="http://remote-agent",
            task_description="Test task",
            task_data={"input": "test"}
        )
        
        assert correlation_id is not None
        
        # 验证消息历史
        assert len(protocol_handler.message_history) > 0
        last_message = protocol_handler.message_history[-1]
        assert last_message.message_type == A2AMessageType.TASK_REQUEST
        assert last_message.payload["task_description"] == "Test task"
    
    async def test_collaboration_invite(self, protocol_handler):
        """测试协作邀请"""
        # 发送协作邀请
        collaboration_id = await protocol_handler.send_collaboration_invite(
            target_agents=["agent1", "agent2"],
            collaboration_type="test_collab",
            collaboration_data={
                "task": "Test collaboration",
                "roles": {"reviewer": "agent1", "executor": "agent2"},
                "duration": "1h"
            }
        )
        
        assert collaboration_id is not None
        assert collaboration_id in protocol_handler.active_collaborations
        
        # 验证协作记录
        collab_info = protocol_handler.active_collaborations[collaboration_id]
        assert collab_info["type"] == "test_collab"
        assert len(collab_info["participants"]) == 2
        assert collab_info["status"] == "invited"
    
    async def test_error_handling(self, protocol_handler):
        """测试错误处理"""
        # 创建无效消息类型
        invalid_message = A2AMessage(
            message_id="test_error",
            protocol_version=A2AProtocolVersion.V2_0,
            message_type="INVALID_TYPE",  # 类型错误
            sender_id="remote_agent",
            receiver_id="test_agent",
            timestamp=datetime.now(),
            payload={"test": "data"}
        )
        
        # 处理消息应该返回错误响应
        response = await protocol_handler.process_message(invalid_message)
        
        assert response is not None
        assert response.message_type == A2AMessageType.ERROR_REPORT
        assert "error_message" in response.payload
    
    async def test_connection_status(self, protocol_handler):
        """测试连接状态查询"""
        status = protocol_handler.get_connection_status()
        
        assert status["agent_id"] == "test_agent"
        assert isinstance(status["connected_agents"], int)
        assert isinstance(status["active_collaborations"], int)
        assert isinstance(status["messages_processed"], int)
        assert status["transport_type"] == "A2AHTTPTransport" 