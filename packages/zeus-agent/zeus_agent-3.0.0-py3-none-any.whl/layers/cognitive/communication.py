"""
Communication Module - 通信模块
提供Agent间通信能力：消息总线、团队协议、通信管理
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
from collections import defaultdict, deque
import weakref


class MessageType(Enum):
    """消息类型枚举"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    COMMAND = "command"
    QUERY = "query"
    UPDATE = "update"
    ERROR = "error"


class MessagePriority(Enum):
    """消息优先级"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class CommunicationPattern(Enum):
    """通信模式"""
    POINT_TO_POINT = "point_to_point"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    REQUEST_RESPONSE = "request_response"
    PIPELINE = "pipeline"


@dataclass
class Message:
    """消息"""
    message_id: str
    sender_id: str
    receiver_id: Optional[str]  # None表示广播
    message_type: MessageType
    content: Any
    priority: MessagePriority = MessagePriority.NORMAL
    topic: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        if self.expiry_time is None:
            return False
        return datetime.now() > self.expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "topic": self.topic,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp.isoformat(),
            "expiry_time": self.expiry_time.isoformat() if self.expiry_time else None,
            "metadata": self.metadata
        }


@dataclass
class CommunicationChannel:
    """通信通道"""
    channel_id: str
    name: str
    description: str
    participants: Set[str] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    message_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageHandler(ABC):
    """消息处理器接口"""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """处理消息，可选返回响应消息"""
        pass
    
    @abstractmethod
    def can_handle(self, message: Message) -> bool:
        """判断是否能处理该消息"""
        pass


class MessageFilter(ABC):
    """消息过滤器接口"""
    
    @abstractmethod
    def should_process(self, message: Message) -> bool:
        """判断消息是否应该被处理"""
        pass


class MessageRouter:
    """消息路由器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.routing_rules = {}
        self.default_route = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_route(self, pattern: str, destination: str, priority: int = 0) -> None:
        """添加路由规则"""
        if pattern not in self.routing_rules:
            self.routing_rules[pattern] = []
        
        self.routing_rules[pattern].append({
            "destination": destination,
            "priority": priority,
            "created_at": datetime.now()
        })
        
        # 按优先级排序
        self.routing_rules[pattern].sort(key=lambda x: x["priority"])
    
    def set_default_route(self, destination: str) -> None:
        """设置默认路由"""
        self.default_route = destination
    
    def route_message(self, message: Message) -> List[str]:
        """路由消息，返回目标地址列表"""
        destinations = []
        
        # 检查具体接收者
        if message.receiver_id:
            destinations.append(message.receiver_id)
            return destinations
        
        # 检查主题路由
        if message.topic:
            if message.topic in self.routing_rules:
                for rule in self.routing_rules[message.topic]:
                    destinations.append(rule["destination"])
        
        # 检查消息类型路由
        message_type_pattern = f"type:{message.message_type.value}"
        if message_type_pattern in self.routing_rules:
            for rule in self.routing_rules[message_type_pattern]:
                destinations.append(rule["destination"])
        
        # 检查发送者路由
        sender_pattern = f"sender:{message.sender_id}"
        if sender_pattern in self.routing_rules:
            for rule in self.routing_rules[sender_pattern]:
                destinations.append(rule["destination"])
        
        # 如果没有找到路由，使用默认路由
        if not destinations and self.default_route:
            destinations.append(self.default_route)
        
        return list(set(destinations))  # 去重


class MessageQueue:
    """消息队列"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_size = self.config.get("max_size", 10000)
        self.queues = defaultdict(lambda: deque(maxlen=self.max_size))
        self.priority_queues = defaultdict(lambda: {
            MessagePriority.CRITICAL: deque(),
            MessagePriority.HIGH: deque(),
            MessagePriority.NORMAL: deque(),
            MessagePriority.LOW: deque(),
            MessagePriority.BACKGROUND: deque()
        })
        self.subscribers = defaultdict(set)
        self.message_stats = defaultdict(int)
        self.lock = asyncio.Lock()
    
    async def enqueue(self, queue_name: str, message: Message) -> bool:
        """入队消息"""
        async with self.lock:
            try:
                # 检查消息是否过期
                if message.is_expired():
                    return False
                
                # 添加到优先级队列
                self.priority_queues[queue_name][message.priority].append(message)
                
                # 更新统计
                self.message_stats[f"{queue_name}_enqueued"] += 1
                self.message_stats[f"{queue_name}_current_size"] = self._get_queue_size(queue_name)
                
                return True
            
            except Exception as e:
                logging.error(f"Error enqueueing message: {e}")
                return False
    
    async def dequeue(self, queue_name: str) -> Optional[Message]:
        """出队消息（按优先级）"""
        async with self.lock:
            try:
                priority_queue = self.priority_queues[queue_name]
                
                # 按优先级顺序检查队列
                for priority in MessagePriority:
                    if priority_queue[priority]:
                        message = priority_queue[priority].popleft()
                        
                        # 检查消息是否过期
                        if message.is_expired():
                            continue
                        
                        # 更新统计
                        self.message_stats[f"{queue_name}_dequeued"] += 1
                        self.message_stats[f"{queue_name}_current_size"] = self._get_queue_size(queue_name)
                        
                        return message
                
                return None
            
            except Exception as e:
                logging.error(f"Error dequeuing message: {e}")
                return None
    
    async def peek(self, queue_name: str) -> Optional[Message]:
        """查看队列顶部消息（不出队）"""
        async with self.lock:
            priority_queue = self.priority_queues[queue_name]
            
            for priority in MessagePriority:
                if priority_queue[priority]:
                    return priority_queue[priority][0]
            
            return None
    
    def _get_queue_size(self, queue_name: str) -> int:
        """获取队列大小"""
        total_size = 0
        priority_queue = self.priority_queues[queue_name]
        
        for priority in MessagePriority:
            total_size += len(priority_queue[priority])
        
        return total_size
    
    def get_queue_statistics(self, queue_name: str) -> Dict[str, Any]:
        """获取队列统计信息"""
        return {
            "current_size": self._get_queue_size(queue_name),
            "enqueued": self.message_stats.get(f"{queue_name}_enqueued", 0),
            "dequeued": self.message_stats.get(f"{queue_name}_dequeued", 0),
            "priority_distribution": {
                priority.name: len(self.priority_queues[queue_name][priority])
                for priority in MessagePriority
            }
        }


class MessageBus:
    """消息总线 - 核心通信组件"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.message_queue = MessageQueue(self.config.get("queue", {}))
        self.message_router = MessageRouter(self.config.get("router", {}))
        
        # 注册的处理器和过滤器
        self.message_handlers = defaultdict(list)
        self.message_filters = []
        
        # 订阅管理
        self.topic_subscribers = defaultdict(set)
        self.agent_subscriptions = defaultdict(set)
        
        # 通道管理
        self.channels = {}
        
        # 消息历史和统计
        self.message_history = deque(maxlen=10000)
        self.message_stats = defaultdict(int)
        
        # 异步任务管理
        self.processing_tasks = set()
        self.is_running = False
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start(self) -> None:
        """启动消息总线"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动消息处理任务
        processing_task = asyncio.create_task(self._message_processing_loop())
        self.processing_tasks.add(processing_task)
        
        # 启动清理任务
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.processing_tasks.add(cleanup_task)
        
        self.logger.info("Message bus started")
    
    async def stop(self) -> None:
        """停止消息总线"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有处理任务
        for task in self.processing_tasks:
            task.cancel()
        
        # 等待任务完成
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        self.processing_tasks.clear()
        self.logger.info("Message bus stopped")
    
    async def send_message(self, message: Message) -> bool:
        """发送消息"""
        try:
            # 应用过滤器
            for filter_obj in self.message_filters:
                if not filter_obj.should_process(message):
                    self.message_stats["filtered_messages"] += 1
                    return False
            
            # 路由消息
            destinations = self.message_router.route_message(message)
            
            if not destinations:
                self.logger.warning(f"No route found for message {message.message_id}")
                return False
            
            # 发送到目标队列
            success_count = 0
            for destination in destinations:
                if await self.message_queue.enqueue(destination, message):
                    success_count += 1
            
            # 记录消息历史
            self.message_history.append(message)
            self.message_stats["sent_messages"] += 1
            
            return success_count > 0
        
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def publish(self, topic: str, content: Any, sender_id: str, **kwargs) -> bool:
        """发布消息到主题"""
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=None,
            message_type=MessageType.BROADCAST,
            content=content,
            topic=topic,
            priority=kwargs.get("priority", MessagePriority.NORMAL),
            **kwargs
        )
        
        return await self.send_message(message)
    
    async def subscribe(self, agent_id: str, topic: str) -> bool:
        """订阅主题"""
        try:
            self.topic_subscribers[topic].add(agent_id)
            self.agent_subscriptions[agent_id].add(topic)
            
            # 添加路由规则
            self.message_router.add_route(topic, agent_id)
            
            self.logger.info(f"Agent {agent_id} subscribed to topic {topic}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error subscribing to topic: {e}")
            return False
    
    async def unsubscribe(self, agent_id: str, topic: str) -> bool:
        """取消订阅主题"""
        try:
            self.topic_subscribers[topic].discard(agent_id)
            self.agent_subscriptions[agent_id].discard(topic)
            
            self.logger.info(f"Agent {agent_id} unsubscribed from topic {topic}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error unsubscribing from topic: {e}")
            return False
    
    def register_handler(self, agent_id: str, handler: MessageHandler) -> None:
        """注册消息处理器"""
        self.message_handlers[agent_id].append(handler)
        self.logger.info(f"Registered message handler for agent {agent_id}")
    
    def add_filter(self, filter_obj: MessageFilter) -> None:
        """添加消息过滤器"""
        self.message_filters.append(filter_obj)
        self.logger.info("Added message filter")
    
    async def create_channel(self, channel_name: str, participants: List[str], **kwargs) -> str:
        """创建通信通道"""
        channel_id = str(uuid.uuid4())
        
        channel = CommunicationChannel(
            channel_id=channel_id,
            name=channel_name,
            description=kwargs.get("description", ""),
            participants=set(participants),
            metadata=kwargs.get("metadata", {})
        )
        
        self.channels[channel_id] = channel
        
        # 为通道参与者添加路由规则
        for participant in participants:
            self.message_router.add_route(f"channel:{channel_id}", participant)
        
        self.logger.info(f"Created communication channel {channel_name} with ID {channel_id}")
        return channel_id
    
    async def send_to_channel(self, channel_id: str, message: Message) -> bool:
        """发送消息到通道"""
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        if not channel.is_active:
            return False
        
        # 设置消息主题为通道ID
        message.topic = f"channel:{channel_id}"
        
        # 发送消息
        success = await self.send_message(message)
        
        if success:
            # 记录到通道历史
            channel.message_history.append(message)
        
        return success
    
    async def _message_processing_loop(self) -> None:
        """消息处理循环"""
        while self.is_running:
            try:
                # 处理各个队列中的消息
                for agent_id in list(self.message_handlers.keys()):
                    message = await self.message_queue.dequeue(agent_id)
                    
                    if message:
                        await self._process_message(agent_id, message)
                
                # 短暂休眠避免CPU占用过高
                await asyncio.sleep(0.01)
            
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, agent_id: str, message: Message) -> None:
        """处理单个消息"""
        try:
            handlers = self.message_handlers.get(agent_id, [])
            
            for handler in handlers:
                if handler.can_handle(message):
                    response = await handler.handle_message(message)
                    
                    # 如果有响应消息，发送回去
                    if response:
                        await self.send_message(response)
                    
                    self.message_stats["processed_messages"] += 1
                    break
            else:
                self.logger.warning(f"No handler found for message {message.message_id} to agent {agent_id}")
        
        except Exception as e:
            self.logger.error(f"Error processing message {message.message_id}: {e}")
    
    async def _cleanup_loop(self) -> None:
        """清理循环 - 清理过期消息和统计信息"""
        while self.is_running:
            try:
                # 每分钟运行一次清理
                await asyncio.sleep(60)
                
                # 清理过期消息历史
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=24)  # 保留24小时
                
                # 清理消息历史
                while (self.message_history and 
                       self.message_history[0].timestamp < cutoff_time):
                    self.message_history.popleft()
                
                # 清理通道历史
                for channel in self.channels.values():
                    while (channel.message_history and 
                           channel.message_history[0].timestamp < cutoff_time):
                        channel.message_history.popleft()
                
                self.logger.debug("Completed message cleanup")
            
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取消息总线统计信息"""
        return {
            "message_stats": dict(self.message_stats),
            "active_subscriptions": {
                agent_id: list(topics) 
                for agent_id, topics in self.agent_subscriptions.items()
            },
            "topic_subscribers": {
                topic: list(subscribers) 
                for topic, subscribers in self.topic_subscribers.items()
            },
            "active_channels": len([c for c in self.channels.values() if c.is_active]),
            "total_channels": len(self.channels),
            "message_history_size": len(self.message_history),
            "registered_handlers": {
                agent_id: len(handlers) 
                for agent_id, handlers in self.message_handlers.items()
            },
            "is_running": self.is_running
        }


class TeamProtocol:
    """团队协作协议"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.protocols = {}
        self.active_sessions = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def define_protocol(self, protocol_name: str, protocol_spec: Dict[str, Any]) -> None:
        """定义协作协议"""
        self.protocols[protocol_name] = {
            "name": protocol_name,
            "description": protocol_spec.get("description", ""),
            "participants": protocol_spec.get("participants", []),
            "communication_pattern": protocol_spec.get("communication_pattern", CommunicationPattern.BROADCAST),
            "message_flow": protocol_spec.get("message_flow", []),
            "rules": protocol_spec.get("rules", []),
            "timeout": protocol_spec.get("timeout", 300),  # 5分钟默认超时
            "created_at": datetime.now()
        }
        
        self.logger.info(f"Defined team protocol: {protocol_name}")
    
    async def start_session(self, protocol_name: str, participants: List[str], **kwargs) -> str:
        """启动协作会话"""
        if protocol_name not in self.protocols:
            raise ValueError(f"Protocol {protocol_name} not defined")
        
        session_id = str(uuid.uuid4())
        protocol = self.protocols[protocol_name]
        
        session = {
            "session_id": session_id,
            "protocol_name": protocol_name,
            "participants": participants,
            "current_step": 0,
            "status": "active",
            "started_at": datetime.now(),
            "timeout_at": datetime.now() + timedelta(seconds=protocol["timeout"]),
            "message_log": [],
            "context": kwargs.get("context", {}),
            "metadata": kwargs.get("metadata", {})
        }
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Started team protocol session {session_id} for protocol {protocol_name}")
        return session_id
    
    async def process_message(self, session_id: str, message: Message) -> Dict[str, Any]:
        """处理协作消息"""
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.active_sessions[session_id]
        protocol = self.protocols[session["protocol_name"]]
        
        # 检查会话是否过期
        if datetime.now() > session["timeout_at"]:
            session["status"] = "timeout"
            return {"success": False, "error": "Session timeout"}
        
        # 记录消息
        session["message_log"].append({
            "message": message.to_dict(),
            "timestamp": datetime.now(),
            "step": session["current_step"]
        })
        
        # 处理消息流
        result = await self._process_protocol_step(session, message, protocol)
        
        return result
    
    async def _process_protocol_step(self, session: Dict[str, Any], message: Message, protocol: Dict[str, Any]) -> Dict[str, Any]:
        """处理协议步骤"""
        current_step = session["current_step"]
        message_flow = protocol.get("message_flow", [])
        
        if current_step >= len(message_flow):
            session["status"] = "completed"
            return {"success": True, "status": "completed"}
        
        step_spec = message_flow[current_step]
        
        # 验证消息是否符合当前步骤要求
        if not self._validate_message_for_step(message, step_spec):
            return {"success": False, "error": "Message does not match step requirements"}
        
        # 执行步骤逻辑
        step_result = await self._execute_step(session, message, step_spec)
        
        if step_result.get("success", False):
            session["current_step"] += 1
            
            # 检查是否完成所有步骤
            if session["current_step"] >= len(message_flow):
                session["status"] = "completed"
                return {"success": True, "status": "completed", "result": step_result}
        
        return step_result
    
    def _validate_message_for_step(self, message: Message, step_spec: Dict[str, Any]) -> bool:
        """验证消息是否符合步骤要求"""
        # 检查消息类型
        expected_type = step_spec.get("expected_message_type")
        if expected_type and message.message_type.value != expected_type:
            return False
        
        # 检查发送者
        expected_sender = step_spec.get("expected_sender")
        if expected_sender and message.sender_id != expected_sender:
            return False
        
        # 检查内容格式
        content_schema = step_spec.get("content_schema")
        if content_schema:
            # 简化的内容验证
            if isinstance(content_schema, dict) and isinstance(message.content, dict):
                for required_key in content_schema.get("required", []):
                    if required_key not in message.content:
                        return False
        
        return True
    
    async def _execute_step(self, session: Dict[str, Any], message: Message, step_spec: Dict[str, Any]) -> Dict[str, Any]:
        """执行协议步骤"""
        step_type = step_spec.get("type", "message")
        
        if step_type == "message":
            # 简单的消息传递步骤
            return {"success": True, "action": "message_received"}
        
        elif step_type == "decision":
            # 决策步骤
            decision_result = await self._handle_decision_step(session, message, step_spec)
            return decision_result
        
        elif step_type == "aggregation":
            # 聚合步骤
            aggregation_result = await self._handle_aggregation_step(session, message, step_spec)
            return aggregation_result
        
        elif step_type == "validation":
            # 验证步骤
            validation_result = await self._handle_validation_step(session, message, step_spec)
            return validation_result
        
        else:
            return {"success": False, "error": f"Unknown step type: {step_type}"}
    
    async def _handle_decision_step(self, session: Dict[str, Any], message: Message, step_spec: Dict[str, Any]) -> Dict[str, Any]:
        """处理决策步骤"""
        # 简化的决策处理
        decision_options = step_spec.get("options", [])
        decision_content = message.content
        
        if isinstance(decision_content, dict) and "decision" in decision_content:
            chosen_option = decision_content["decision"]
            
            if chosen_option in decision_options:
                session["context"]["last_decision"] = chosen_option
                return {"success": True, "decision": chosen_option}
        
        return {"success": False, "error": "Invalid decision"}
    
    async def _handle_aggregation_step(self, session: Dict[str, Any], message: Message, step_spec: Dict[str, Any]) -> Dict[str, Any]:
        """处理聚合步骤"""
        # 收集来自多个参与者的输入
        if "aggregated_inputs" not in session["context"]:
            session["context"]["aggregated_inputs"] = []
        
        session["context"]["aggregated_inputs"].append({
            "sender": message.sender_id,
            "content": message.content,
            "timestamp": message.timestamp
        })
        
        # 检查是否收集到所有参与者的输入
        expected_participants = step_spec.get("required_participants", session["participants"])
        received_from = {input_data["sender"] for input_data in session["context"]["aggregated_inputs"]}
        
        if len(received_from) >= len(expected_participants):
            # 执行聚合逻辑
            aggregated_result = self._aggregate_inputs(session["context"]["aggregated_inputs"], step_spec)
            session["context"]["aggregation_result"] = aggregated_result
            
            return {"success": True, "aggregated_result": aggregated_result}
        
        return {"success": True, "status": "waiting_for_more_inputs", "received_count": len(received_from)}
    
    async def _handle_validation_step(self, session: Dict[str, Any], message: Message, step_spec: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证步骤"""
        validation_rules = step_spec.get("validation_rules", [])
        
        for rule in validation_rules:
            if not self._apply_validation_rule(message, rule):
                return {"success": False, "error": f"Validation failed: {rule.get('description', 'Unknown rule')}"}
        
        return {"success": True, "validation": "passed"}
    
    def _aggregate_inputs(self, inputs: List[Dict[str, Any]], step_spec: Dict[str, Any]) -> Any:
        """聚合输入数据"""
        aggregation_method = step_spec.get("aggregation_method", "collect")
        
        if aggregation_method == "collect":
            return [input_data["content"] for input_data in inputs]
        
        elif aggregation_method == "majority_vote":
            # 简单的多数投票
            votes = {}
            for input_data in inputs:
                vote = str(input_data["content"])
                votes[vote] = votes.get(vote, 0) + 1
            
            return max(votes.items(), key=lambda x: x[1])[0] if votes else None
        
        elif aggregation_method == "average":
            # 数值平均
            numeric_values = []
            for input_data in inputs:
                try:
                    value = float(input_data["content"])
                    numeric_values.append(value)
                except (ValueError, TypeError):
                    continue
            
            return sum(numeric_values) / len(numeric_values) if numeric_values else 0
        
        else:
            return inputs
    
    def _apply_validation_rule(self, message: Message, rule: Dict[str, Any]) -> bool:
        """应用验证规则"""
        rule_type = rule.get("type", "required")
        
        if rule_type == "required":
            required_fields = rule.get("fields", [])
            if isinstance(message.content, dict):
                return all(field in message.content for field in required_fields)
        
        elif rule_type == "type_check":
            expected_type = rule.get("expected_type", "str")
            content_type = type(message.content).__name__
            return content_type == expected_type
        
        elif rule_type == "value_range":
            if isinstance(message.content, (int, float)):
                min_val = rule.get("min", float('-inf'))
                max_val = rule.get("max", float('inf'))
                return min_val <= message.content <= max_val
        
        return True
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        protocol = self.protocols[session["protocol_name"]]
        
        return {
            "session_id": session_id,
            "protocol_name": session["protocol_name"],
            "status": session["status"],
            "current_step": session["current_step"],
            "total_steps": len(protocol.get("message_flow", [])),
            "participants": session["participants"],
            "started_at": session["started_at"].isoformat(),
            "timeout_at": session["timeout_at"].isoformat(),
            "message_count": len(session["message_log"]),
            "progress": session["current_step"] / len(protocol.get("message_flow", [])) if protocol.get("message_flow") else 0
        }
    
    def get_protocol_statistics(self) -> Dict[str, Any]:
        """获取协议统计信息"""
        return {
            "defined_protocols": len(self.protocols),
            "active_sessions": len([s for s in self.active_sessions.values() if s["status"] == "active"]),
            "completed_sessions": len([s for s in self.active_sessions.values() if s["status"] == "completed"]),
            "timeout_sessions": len([s for s in self.active_sessions.values() if s["status"] == "timeout"]),
            "total_sessions": len(self.active_sessions)
        }


class CommunicationManager:
    """通信管理器 - 统一的通信管理接口"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 初始化核心组件
        self.message_bus = MessageBus(self.config.get("message_bus", {}))
        self.team_protocol = TeamProtocol(self.config.get("team_protocol", {}))
        
        # 通信统计
        self.communication_stats = defaultdict(int)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start(self) -> None:
        """启动通信管理器"""
        await self.message_bus.start()
        self.logger.info("Communication manager started")
    
    async def stop(self) -> None:
        """停止通信管理器"""
        await self.message_bus.stop()
        self.logger.info("Communication manager stopped")
    
    async def send_message(self, sender_id: str, receiver_id: str, content: Any, **kwargs) -> bool:
        """发送点对点消息"""
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=kwargs.get("message_type", MessageType.REQUEST),
            content=content,
            priority=kwargs.get("priority", MessagePriority.NORMAL),
            **kwargs
        )
        
        success = await self.message_bus.send_message(message)
        if success:
            self.communication_stats["point_to_point_messages"] += 1
        
        return success
    
    async def broadcast_message(self, sender_id: str, content: Any, **kwargs) -> bool:
        """广播消息"""
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=None,
            message_type=MessageType.BROADCAST,
            content=content,
            priority=kwargs.get("priority", MessagePriority.NORMAL),
            **kwargs
        )
        
        success = await self.message_bus.send_message(message)
        if success:
            self.communication_stats["broadcast_messages"] += 1
        
        return success
    
    async def publish_to_topic(self, sender_id: str, topic: str, content: Any, **kwargs) -> bool:
        """发布到主题"""
        success = await self.message_bus.publish(topic, content, sender_id, **kwargs)
        if success:
            self.communication_stats["topic_messages"] += 1
        
        return success
    
    async def subscribe_to_topic(self, agent_id: str, topic: str) -> bool:
        """订阅主题"""
        success = await self.message_bus.subscribe(agent_id, topic)
        if success:
            self.communication_stats["subscriptions"] += 1
        
        return success
    
    def register_message_handler(self, agent_id: str, handler: MessageHandler) -> None:
        """注册消息处理器"""
        self.message_bus.register_handler(agent_id, handler)
        self.communication_stats["registered_handlers"] += 1
    
    def define_team_protocol(self, protocol_name: str, protocol_spec: Dict[str, Any]) -> None:
        """定义团队协作协议"""
        self.team_protocol.define_protocol(protocol_name, protocol_spec)
        self.communication_stats["defined_protocols"] += 1
    
    async def start_team_session(self, protocol_name: str, participants: List[str], **kwargs) -> str:
        """启动团队协作会话"""
        session_id = await self.team_protocol.start_session(protocol_name, participants, **kwargs)
        self.communication_stats["team_sessions"] += 1
        return session_id
    
    async def create_communication_channel(self, channel_name: str, participants: List[str], **kwargs) -> str:
        """创建通信通道"""
        channel_id = await self.message_bus.create_channel(channel_name, participants, **kwargs)
        self.communication_stats["created_channels"] += 1
        return channel_id
    
    def get_communication_statistics(self) -> Dict[str, Any]:
        """获取通信统计信息"""
        message_bus_stats = self.message_bus.get_statistics()
        protocol_stats = self.team_protocol.get_protocol_statistics()
        
        return {
            "communication_stats": dict(self.communication_stats),
            "message_bus": message_bus_stats,
            "team_protocols": protocol_stats,
            "timestamp": datetime.now().isoformat()
        } 