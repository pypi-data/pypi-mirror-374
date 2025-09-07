"""
Layer Communication Tests
测试层通信组件的功能
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any, List

from layers.framework.abstractions.layer_communication import (
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


class TestLayerMessageHandler(LayerMessageHandler):
    """测试用的消息处理器"""
    
    def __init__(self):
        self.messages = []
        self.processed_count = 0
    
    async def handle_message(self, message: LayerMessage) -> bool:
        """处理消息"""
        self.messages.append(message)
        self.processed_count += 1
        return True


@pytest.mark.asyncio
class TestLayerCommunication:
    """测试层通信组件"""
    
    @pytest_asyncio.fixture
    async def message_handler(self):
        """创建消息处理器"""
        return TestLayerMessageHandler()
    
    @pytest_asyncio.fixture
    async def message_router(self, message_handler):
        """创建消息路由器"""
        router = LayerMessageRouter()
        router.register_handler("test", message_handler)
        return router
    
    @pytest_asyncio.fixture
    async def message_queue(self):
        """创建消息队列"""
        return LayerMessageQueue()
    
    @pytest_asyncio.fixture
    async def message_filter(self):
        """创建消息过滤器"""
        return LayerMessageFilter()
    
    @pytest_asyncio.fixture
    async def message_transformer(self):
        """创建消息转换器"""
        return LayerMessageTransformer()
    
    @pytest_asyncio.fixture
    async def message_validator(self):
        """创建消息验证器"""
        return LayerMessageValidator()
    
    @pytest_asyncio.fixture
    async def message_logger(self):
        """创建消息日志记录器"""
        return LayerMessageLogger()
    
    @pytest_asyncio.fixture
    async def layer_manager(self, message_router, message_queue, message_filter, message_transformer, message_validator, message_logger):
        """创建层通信管理器"""
        manager = LayerCommunicationManager(
            router=message_router,
            queue=message_queue,
            filter=message_filter,
            transformer=message_transformer,
            validator=message_validator,
            logger=message_logger
        )
        return manager
    
    async def test_message_routing(self, layer_manager, message_handler):
        """测试消息路由"""
        # 创建消息
        message = LayerMessage(
            id="test_message",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        # 发送消息
        await layer_manager.send_message(message)
        
        # 验证消息路由
        assert len(message_handler.messages) == 1
        assert message_handler.messages[0].id == "test_message"
        assert message_handler.messages[0].type == LayerMessageType.REQUEST
        assert message_handler.messages[0].source == "test_source"
        assert message_handler.messages[0].target == "test"
        assert message_handler.messages[0].content["action"] == "test_action"
    
    async def test_message_filtering(self, layer_manager, message_handler):
        """测试消息过滤"""
        # 创建消息
        message1 = LayerMessage(
            id="test_message_1",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.HIGH,
            timestamp=datetime.now()
        )
        
        message2 = LayerMessage(
            id="test_message_2",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.LOW,
            timestamp=datetime.now()
        )
        
        # 设置过滤器
        layer_manager.filter.add_rule(lambda m: m.priority == LayerMessagePriority.HIGH)
        
        # 发送消息
        await layer_manager.send_message(message1)
        await layer_manager.send_message(message2)
        
        # 验证消息过滤
        assert len(message_handler.messages) == 1
        assert message_handler.messages[0].id == "test_message_1"
    
    async def test_message_transformation(self, layer_manager, message_handler):
        """测试消息转换"""
        # 创建消息
        message = LayerMessage(
            id="test_message",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action", "data": "test_data"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        # 设置转换器
        layer_manager.transformer.add_transform(
            lambda m: LayerMessage(
                id=m.id,
                type=m.type,
                source=m.source,
                target=m.target,
                content={"transformed_action": m.content["action"], "transformed_data": m.content["data"]},
                status=m.status,
                priority=m.priority,
                timestamp=m.timestamp
            )
        )
        
        # 发送消息
        await layer_manager.send_message(message)
        
        # 验证消息转换
        assert len(message_handler.messages) == 1
        assert message_handler.messages[0].content["transformed_action"] == "test_action"
        assert message_handler.messages[0].content["transformed_data"] == "test_data"
    
    async def test_message_validation(self, layer_manager, message_handler):
        """测试消息验证"""
        # 创建消息
        valid_message = LayerMessage(
            id="test_message_1",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        invalid_message = LayerMessage(
            id="test_message_2",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={},  # 缺少必需的action字段
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        # 设置验证器
        layer_manager.validator.add_rule(lambda m: "action" in m.content)
        
        # 发送消息
        await layer_manager.send_message(valid_message)
        await layer_manager.send_message(invalid_message)
        
        # 验证消息验证
        assert len(message_handler.messages) == 1
        assert message_handler.messages[0].id == "test_message_1"
    
    async def test_message_queueing(self, layer_manager, message_handler):
        """测试消息队列"""
        # 创建消息
        messages = [
            LayerMessage(
                id=f"test_message_{i}",
                type=LayerMessageType.REQUEST,
                source="test_source",
                target="test",
                content={"action": "test_action"},
                status=LayerMessageStatus.PENDING,
                priority=LayerMessagePriority.NORMAL,
                timestamp=datetime.now()
            )
            for i in range(5)
        ]
        
        # 暂停消息处理
        layer_manager.queue.pause()
        
        # 发送消息
        for message in messages:
            await layer_manager.send_message(message)
        
        # 验证消息队列
        assert layer_manager.queue.size() == 5
        assert len(message_handler.messages) == 0
        
        # 恢复消息处理
        await layer_manager.queue.resume()
        
        # 等待消息处理完成
        await asyncio.sleep(0.1)
        
        # 验证消息处理
        assert layer_manager.queue.size() == 0
        assert len(message_handler.messages) == 5
        assert [m.id for m in message_handler.messages] == [f"test_message_{i}" for i in range(5)]
    
    async def test_message_logging(self, layer_manager, message_handler):
        """测试消息日志记录"""
        # 创建消息
        message = LayerMessage(
            id="test_message",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="test",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        # 发送消息
        await layer_manager.send_message(message)
        
        # 验证消息日志
        logs = layer_manager.logger.get_logs()
        assert len(logs) == 2  # 原始消息和处理后的消息
        
        # 验证原始消息
        assert logs[0]["message_id"] == "test_message"
        assert logs[0]["type"] == LayerMessageType.REQUEST.value
        assert logs[0]["source"] == "test_source"
        assert logs[0]["target"] == "test"
        assert logs[0]["status"] == LayerMessageStatus.PENDING.value
        
        # 验证处理后的消息
        assert logs[1]["message_id"] == "test_message"
        assert logs[1]["type"] == LayerMessageType.REQUEST.value
        assert logs[1]["source"] == "test_source"
        assert logs[1]["target"] == "test"
        assert logs[1]["status"] == LayerMessageStatus.COMPLETED.value
    
    async def test_error_handling(self, layer_manager, message_handler):
        """测试错误处理"""
        # 创建一个会失败的消息处理器
        failing_handler = TestLayerMessageHandler()
        failing_handler.handle_message = AsyncMock(side_effect=Exception("Test error"))
        layer_manager.router.register_handler("failing", failing_handler)
        
        # 创建消息
        message = LayerMessage(
            id="test_message",
            type=LayerMessageType.REQUEST,
            source="test_source",
            target="failing",
            content={"action": "test_action"},
            status=LayerMessageStatus.PENDING,
            priority=LayerMessagePriority.NORMAL,
            timestamp=datetime.now()
        )
        
        # 发送消息
        await layer_manager.send_message(message)
        
        # 验证错误处理
        logs = layer_manager.logger.get_logs()
        assert len(logs) == 2  # 原始消息和错误消息
        
        # 验证原始消息
        assert logs[0]["message_id"] == "test_message"
        assert logs[0]["type"] == LayerMessageType.REQUEST.value
        assert logs[0]["source"] == "test_source"
        assert logs[0]["target"] == "failing"
        assert logs[0]["status"] == LayerMessageStatus.PENDING.value
        assert logs[0]["error"] is None
        
        # 验证错误消息
        assert logs[1]["message_id"] == "test_message"
        assert logs[1]["type"] == LayerMessageType.REQUEST.value
        assert logs[1]["source"] == "test_source"
        assert logs[1]["target"] == "failing"
        assert logs[1]["status"] == LayerMessageStatus.ERROR.value
        assert logs[1]["error"]["message"] == "Test error"
    
    async def test_message_metrics(self, layer_manager, message_handler):
        """测试消息指标"""
        # 创建消息
        messages = [
            LayerMessage(
                id=f"test_message_{i}",
                type=LayerMessageType.REQUEST,
                source="test_source",
                target="test",
                content={"action": "test_action"},
                status=LayerMessageStatus.PENDING,
                priority=LayerMessagePriority.NORMAL,
                timestamp=datetime.now()
            )
            for i in range(5)
        ]
        
        # 发送消息
        for message in messages:
            await layer_manager.send_message(message)
        
        # 验证消息指标
        metrics = layer_manager.get_metrics()
        assert metrics["total_messages"] == 5
        assert metrics["processed_messages"] == 5
        assert metrics["success_rate"] == 1.0
        assert metrics["average_processing_time"] > 0 