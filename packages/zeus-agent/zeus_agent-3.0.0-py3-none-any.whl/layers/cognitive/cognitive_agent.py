"""
Cognitive Agent - 认知Agent
整合感知、推理、记忆、学习、通信能力的完整认知Agent实现
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

from ..framework.abstractions.agent import UniversalAgent, AgentCapability, AgentStatus, AgentMetadata
from ..framework.abstractions.task import UniversalTask, TaskType
from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.result import UniversalResult, ResultStatus

from .perception import PerceptionEngine
from .reasoning import ReasoningEngine, ReasoningType
from .memory import MemorySystem, MemoryType
from .learning import LearningModule, LearningType, Experience, Skill
from .communication import CommunicationManager, MessageHandler, Message, MessageType


class CognitiveState(Enum):
    """认知状态枚举"""
    IDLE = "idle"
    PERCEIVING = "perceiving"
    REASONING = "reasoning"
    LEARNING = "learning"
    COMMUNICATING = "communicating"
    EXECUTING = "executing"
    ERROR = "error"


@dataclass
class AgentIdentity:
    """Agent身份信息"""
    agent_id: str
    name: str
    role: str
    description: str
    goals: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    expertise_domains: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CognitiveMetrics:
    """认知指标"""
    perception_accuracy: float = 0.0
    reasoning_consistency: float = 0.0
    memory_efficiency: float = 0.0
    learning_progress: float = 0.0
    communication_effectiveness: float = 0.0
    overall_performance: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class CognitiveMessageHandler(MessageHandler):
    """认知Agent的消息处理器"""
    
    def __init__(self, cognitive_agent: 'CognitiveAgent'):
        self.cognitive_agent = cognitive_agent
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """处理接收到的消息"""
        try:
            # 根据消息类型处理
            if message.message_type == MessageType.REQUEST:
                return await self._handle_request(message)
            elif message.message_type == MessageType.QUERY:
                return await self._handle_query(message)
            elif message.message_type == MessageType.COMMAND:
                return await self._handle_command(message)
            elif message.message_type == MessageType.NOTIFICATION:
                await self._handle_notification(message)
                return None
            else:
                return await self._handle_generic_message(message)
        
        except Exception as e:
            self.logger.error(f"Error handling message {message.message_id}: {e}")
            return self._create_error_response(message, str(e))
    
    def can_handle(self, message: Message) -> bool:
        """判断是否能处理该消息"""
        # 认知Agent可以处理所有类型的消息
        return True
    
    async def _handle_request(self, message: Message) -> Message:
        """处理请求消息"""
        # 将请求转换为任务
        task = UniversalTask(
            content=str(message.content),
            task_type=TaskType.GENERAL,
            metadata={"source": "message_request", "correlation_id": message.correlation_id}
        )
        
        # 执行任务
        result = await self.cognitive_agent.execute(task, UniversalContext())
        
        # 创建响应消息
        return Message(
            message_id=str(uuid.uuid4()),
            sender_id=self.cognitive_agent.identity.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=result.content,
            correlation_id=message.message_id,
            metadata={"result_status": result.status.value}
        )
    
    async def _handle_query(self, message: Message) -> Message:
        """处理查询消息"""
        query_content = message.content
        
        # 从记忆中检索相关信息
        memory_results = await self.cognitive_agent.memory_system.retrieve_memory(query_content)
        
        # 使用推理引擎分析查询
        reasoning_result = await self.cognitive_agent.reasoning_engine.reason(
            premises=[query_content],
            reasoning_types=[ReasoningType.LOGICAL]
        )
        
        response_content = {
            "query": query_content,
            "memory_results": memory_results,
            "reasoning": reasoning_result.get("best_result", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return Message(
            message_id=str(uuid.uuid4()),
            sender_id=self.cognitive_agent.identity.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=response_content,
            correlation_id=message.message_id
        )
    
    async def _handle_command(self, message: Message) -> Optional[Message]:
        """处理命令消息"""
        command = message.content
        
        if isinstance(command, dict):
            command_type = command.get("type", "unknown")
            
            if command_type == "learn":
                # 学习命令
                await self.cognitive_agent._handle_learning_command(command)
            elif command_type == "remember":
                # 记忆命令
                await self.cognitive_agent._handle_memory_command(command)
            elif command_type == "status":
                # 状态查询命令
                status_info = self.cognitive_agent.get_status_info()
                return Message(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.cognitive_agent.identity.agent_id,
                    receiver_id=message.sender_id,
                    message_type=MessageType.RESPONSE,
                    content=status_info,
                    correlation_id=message.message_id
                )
        
        return None
    
    async def _handle_notification(self, message: Message) -> None:
        """处理通知消息"""
        # 记录通知到记忆系统
        await self.cognitive_agent.memory_system.store_memory(
            content=message.content,
            memory_type=MemoryType.EPISODIC,
            event=f"Received notification from {message.sender_id}",
            participants=[message.sender_id, self.cognitive_agent.identity.agent_id],
            importance=0.5
        )
    
    async def _handle_generic_message(self, message: Message) -> Message:
        """处理通用消息"""
        # 使用感知引擎处理消息内容
        perception_result = await self.cognitive_agent.perception_engine.perceive(
            message.content
        )
        
        response_content = {
            "message_received": True,
            "perception_analysis": perception_result,
            "timestamp": datetime.now().isoformat()
        }
        
        return Message(
            message_id=str(uuid.uuid4()),
            sender_id=self.cognitive_agent.identity.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=response_content,
            correlation_id=message.message_id
        )
    
    def _create_error_response(self, original_message: Message, error_message: str) -> Message:
        """创建错误响应"""
        return Message(
            message_id=str(uuid.uuid4()),
            sender_id=self.cognitive_agent.identity.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            content={"error": error_message, "original_message_id": original_message.message_id},
            correlation_id=original_message.message_id
        )


class CognitiveAgent(UniversalAgent):
    """认知Agent - 具备完整认知能力的AI Agent"""
    
    def __init__(self, identity: AgentIdentity, config: Optional[Dict[str, Any]] = None):
        self.identity = identity
        self.config = config or {}
        
        # 初始化认知组件
        self.perception_engine = PerceptionEngine()
        self.reasoning_engine = ReasoningEngine(self.config.get("reasoning", {}))
        self.memory_system = MemorySystem(self.config.get("memory", {}))
        self.learning_module = LearningModule(self.config.get("learning", {}))
        self.communication_manager = CommunicationManager(self.config.get("communication", {}))
        
        # Agent状态和指标
        self.cognitive_state = CognitiveState.IDLE
        self.cognitive_metrics = CognitiveMetrics()
        self.execution_history = []
        
        # 消息处理
        self.message_handler = CognitiveMessageHandler(self)
        
        # 异步任务管理
        self.background_tasks = set()
        self.is_running = False
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{identity.agent_id}")
    
    async def initialize(self) -> None:
        """初始化认知Agent"""
        try:
            # 初始化各个认知组件
            await self.perception_engine.initialize()
            await self.memory_system.initialize()  # 初始化记忆系统
            await self.communication_manager.start()
            
            # 注册消息处理器
            self.communication_manager.register_message_handler(
                self.identity.agent_id, 
                self.message_handler
            )
            
            # 启动后台任务
            self.is_running = True
            background_task = asyncio.create_task(self._background_processing_loop())
            self.background_tasks.add(background_task)
            
            # 初始化技能
            await self._initialize_skills()
            
            self.logger.info(f"Cognitive Agent {self.identity.name} initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize cognitive agent: {e}")
            raise
    
    async def shutdown(self) -> None:
        """关闭认知Agent"""
        self.is_running = False
        
        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # 停止通信管理器
        await self.communication_manager.stop()
        
        # 关闭记忆系统
        await self.memory_system.shutdown()
        
        # 清理感知引擎
        await self.perception_engine.cleanup()
        
        self.logger.info(f"Cognitive Agent {self.identity.name} shut down")
    
    async def execute(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务 - 认知Agent的核心执行方法"""
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        self.logger.info(f"Starting task execution {execution_id}: {task.content[:100]}...")
        
        try:
            # 记录任务开始
            execution_record = {
                "execution_id": execution_id,
                "task": task,
                "context": context,
                "start_time": start_time,
                "cognitive_steps": []
            }
            
            # 第1步：感知阶段
            self.cognitive_state = CognitiveState.PERCEIVING
            perception_result = await self._cognitive_perceive(task, context)
            execution_record["cognitive_steps"].append(("perception", perception_result))
            
            # 第2步：推理阶段
            self.cognitive_state = CognitiveState.REASONING
            reasoning_result = await self._cognitive_reason(task, context, perception_result)
            execution_record["cognitive_steps"].append(("reasoning", reasoning_result))
            
            # 第3步：执行阶段
            self.cognitive_state = CognitiveState.EXECUTING
            execution_result = await self._cognitive_execute(task, context, reasoning_result)
            execution_record["cognitive_steps"].append(("execution", execution_result))
            
            # 第4步：学习阶段
            self.cognitive_state = CognitiveState.LEARNING
            learning_result = await self._cognitive_learn(task, context, execution_result)
            execution_record["cognitive_steps"].append(("learning", learning_result))
            
            # 创建最终结果
            final_result = UniversalResult(
                content=execution_result.get("result", "Task completed"),
                status=ResultStatus.SUCCESS,
                metadata={
                    "execution_id": execution_id,
                    "cognitive_steps": len(execution_record["cognitive_steps"]),
                    "perception_confidence": perception_result.get("overall_confidence", 0.0),
                    "reasoning_confidence": reasoning_result.get("best_result", {}).get("confidence", 0.0),
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
            # 记录执行历史
            execution_record["end_time"] = datetime.now()
            execution_record["result"] = final_result
            execution_record["success"] = True
            self.execution_history.append(execution_record)
            
            # 存储到情景记忆
            await self.memory_system.store_memory(
                content=f"Completed task: {task.content}",
                memory_type=MemoryType.EPISODIC,
                event="Task execution",
                participants=[self.identity.agent_id],
                importance=0.7,
                metadata={"execution_id": execution_id, "task_type": task.task_type.value}
            )
            
            self.cognitive_state = CognitiveState.IDLE
            self.logger.info(f"Task execution {execution_id} completed successfully")
            
            return final_result
        
        except Exception as e:
            self.cognitive_state = CognitiveState.ERROR
            self.logger.error(f"Task execution {execution_id} failed: {e}")
            
            error_result = UniversalResult(
                content=f"Task execution failed: {str(e)}",
                status=ResultStatus.ERROR,
                metadata={
                    "execution_id": execution_id,
                    "error": str(e),
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
            return error_result
    
    async def _cognitive_perceive(self, task: UniversalTask, context: UniversalContext) -> Dict[str, Any]:
        """认知感知阶段"""
        # 感知任务内容
        perception_result = await self.perception_engine.perceive(task.content, context)
        
        # 分析上下文
        context_analysis = {}
        if context.entries:
            context_content = {entry.key: entry.content for entry in context.entries}
            context_analysis = await self.perception_engine.perceive(context_content)
        
        # 从记忆中检索相关信息
        memory_results = await self.memory_system.retrieve_memory(
            task.content,
            memory_types=[MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]
        )
        
        combined_result = {
            "task_perception": perception_result,
            "context_analysis": context_analysis,
            "memory_retrieval": memory_results,
            "overall_confidence": perception_result.get("overall_confidence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
        return combined_result
    
    async def _cognitive_reason(self, task: UniversalTask, context: UniversalContext, perception_result: Dict[str, Any]) -> Dict[str, Any]:
        """认知推理阶段"""
        # 构建推理前提
        premises = [task.content]
        
        # 添加感知结果作为前提
        if perception_result.get("task_perception", {}).get("intent"):
            intent_info = perception_result["task_perception"]["intent"]
            premises.append(f"Intent: {intent_info['type']} (confidence: {intent_info['confidence']})")
        
        # 添加记忆检索结果
        memory_results = perception_result.get("memory_retrieval", {})
        for memory_type, memories in memory_results.items():
            if memories:
                premises.append(f"Relevant {memory_type}: {memories[0] if memories else 'None'}")
        
        # 执行多模式推理
        reasoning_types = [ReasoningType.LOGICAL, ReasoningType.CAUSAL]
        if task.task_type == TaskType.CREATIVE:
            reasoning_types.append(ReasoningType.ANALOGICAL)
        
        reasoning_result = await self.reasoning_engine.reason(
            premises=premises,
            reasoning_types=reasoning_types,
            context={
                "task_type": task.task_type.value,
                "agent_expertise": self.identity.expertise_domains,
                "confidence_threshold": 0.6
            }
        )
        
        # 制定执行计划
        if reasoning_result.get("best_result"):
            plan = await self.reasoning_engine.create_plan(
                goal=task.content,
                constraints={
                    "max_steps": 10,
                    "time_limit": 300  # 5分钟
                }
            )
            reasoning_result["execution_plan"] = {
                "plan_id": plan.plan_id,
                "steps": plan.steps,
                "estimated_duration": plan.estimated_duration
            }
        
        return reasoning_result
    
    async def _cognitive_execute(self, task: UniversalTask, context: UniversalContext, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """认知执行阶段"""
        execution_result = {
            "result": None,
            "success": False,
            "steps_executed": 0,
            "execution_details": []
        }
        
        try:
            # 获取执行计划
            execution_plan = reasoning_result.get("execution_plan")
            best_reasoning = reasoning_result.get("best_result", {})
            
            if execution_plan and execution_plan.get("steps"):
                # 按计划执行
                for i, step in enumerate(execution_plan["steps"]):
                    step_result = await self._execute_step(step, context)
                    execution_result["execution_details"].append({
                        "step": i + 1,
                        "step_name": step.get("name", f"Step {i+1}"),
                        "result": step_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    execution_result["steps_executed"] = i + 1
                    
                    if not step_result.get("success", False):
                        break
                
                execution_result["success"] = True
                execution_result["result"] = f"Executed {execution_result['steps_executed']} steps successfully"
            
            else:
                # 直接执行（基于推理结论）
                conclusion = best_reasoning.get("conclusion", "No clear conclusion")
                execution_result["result"] = f"Based on reasoning: {conclusion}"
                execution_result["success"] = True
                execution_result["steps_executed"] = 1
            
            return execution_result
        
        except Exception as e:
            execution_result["result"] = f"Execution failed: {str(e)}"
            execution_result["success"] = False
            return execution_result
    
    async def _execute_step(self, step: Dict[str, Any], context: UniversalContext) -> Dict[str, Any]:
        """执行单个步骤 - 使用规划引擎的完整步骤执行"""
        from .planning import PlanStep, StepType
        
        # 转换为PlanStep对象
        plan_step = PlanStep(
            step_id=step.get("step_id", str(uuid.uuid4())),
            name=step.get("name", "Unknown Step"),
            description=step.get("description", ""),
            step_type=StepType.ACTION,  # 默认为动作类型
            action=step.get("action", "execute_generic"),
            parameters=step.get("parameters", {}),
            estimated_duration=step.get("estimated_duration", 30.0)
        )
        
        try:
            # 使用规划引擎的步骤执行方法
            result = await self.reasoning_engine.planning_engine._execute_step(plan_step, None)
            
            return {
                "success": True,
                "result": result,
                "step_id": plan_step.step_id,
                "step_name": plan_step.name,
                "execution_time": plan_step.actual_duration,
                "type": "planned_execution"
            }
            
        except Exception as e:
            self.logger.error(f"Step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "step_id": plan_step.step_id,
                "step_name": plan_step.name,
                "type": "failed_execution"
            }
    
    async def _cognitive_learn(self, task: UniversalTask, context: UniversalContext, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """认知学习阶段"""
        learning_result = {
            "learning_applied": False,
            "experience_recorded": False,
            "skills_updated": False,
            "patterns_recognized": False
        }
        
        try:
            # 记录经验
            experience = Experience(
                experience_id=str(uuid.uuid4()),
                state=task.content,
                action=execution_result.get("result", ""),
                reward=1.0 if execution_result.get("success", False) else -0.5,
                outcome=execution_result,
                context={
                    "task_type": task.task_type.value,
                    "execution_steps": execution_result.get("steps_executed", 0)
                }
            )
            
            self.learning_module.add_experience(experience)
            learning_result["experience_recorded"] = True
            
            # 模式识别
            recent_experiences = self.learning_module.experience_buffer.get_experiences(count=10)
            if len(recent_experiences) >= 3:
                patterns = await self.learning_module.recognize_patterns([exp.state for exp in recent_experiences])
                learning_result["patterns_recognized"] = len(patterns) > 0
                learning_result["patterns_found"] = len(patterns)
            
            # 技能练习（如果相关技能存在）
            relevant_skills = self._find_relevant_skills(task)
            for skill_id in relevant_skills:
                practice_result = await self.learning_module.practice_skill(
                    skill_id, 
                    {
                        "success": execution_result.get("success", False),
                        "quality": 0.8 if execution_result.get("success", False) else 0.3
                    }
                )
                if practice_result.get("success", False):
                    learning_result["skills_updated"] = True
            
            learning_result["learning_applied"] = True
            
            return learning_result
        
        except Exception as e:
            self.logger.error(f"Learning phase error: {e}")
            learning_result["error"] = str(e)
            return learning_result
    
    def get_schema(self) -> Dict[str, Any]:
        """获取认知Agent的配置模式"""
        return {
            "type": "object",
            "properties": {
                "identity": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "name": {"type": "string"},
                        "role": {"type": "string"},
                        "description": {"type": "string"},
                        "goals": {"type": "array", "items": {"type": "string"}},
                        "values": {"type": "array", "items": {"type": "string"}},
                        "expertise_domains": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["agent_id", "name", "role", "description"]
                },
                "perception": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "confidence_threshold": {"type": "number", "default": 0.7}
                    }
                },
                "reasoning": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "reasoning_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["logical", "causal"]
                        }
                    }
                },
                "memory": {
                    "type": "object",
                    "properties": {
                        "working": {
                            "type": "object",
                            "properties": {
                                "capacity": {"type": "integer", "default": 7}
                            }
                        },
                        "persistence": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": True},
                                "database_path": {"type": "string", "default": "memory.db"},
                                "persistence_mode": {"type": "string", "default": "batch"}
                            }
                        }
                    }
                },
                "learning": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "learning_rate": {"type": "number", "default": 0.1}
                    }
                },
                "communication": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "max_connections": {"type": "integer", "default": 10}
                    }
                }
            },
            "required": ["identity"]
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置认知Agent"""
        self.config.update(config)
        
        # 更新身份信息
        if "identity" in config:
            identity_config = config["identity"]
            for key, value in identity_config.items():
                if hasattr(self.identity, key):
                    setattr(self.identity, key, value)
        
        # 重新配置各个组件
        if "perception" in config:
            self.perception_engine.configure(config["perception"])
        
        if "reasoning" in config:
            self.reasoning_engine.configure(config["reasoning"])
        
        if "memory" in config:
            # 注意：内存配置可能需要重新初始化
            pass
        
        if "learning" in config:
            self.learning_module.configure(config["learning"])
        
        if "communication" in config:
            self.communication_manager.configure(config["communication"])
    
    def _find_relevant_skills(self, task: UniversalTask) -> List[str]:
        """寻找与任务相关的技能"""
        # 简化的技能匹配
        task_keywords = task.content.lower().split()
        relevant_skills = []
        
        # 基于任务类型匹配技能
        if task.task_type == TaskType.ANALYSIS:
            relevant_skills.extend(["analysis", "reasoning", "data_processing"])
        elif task.task_type == TaskType.CREATIVE:
            relevant_skills.extend(["creativity", "ideation", "content_generation"])
        elif task.task_type == TaskType.PROBLEM_SOLVING:
            relevant_skills.extend(["problem_solving", "logical_reasoning", "planning"])
        
        return relevant_skills
    
    async def _background_processing_loop(self) -> None:
        """后台处理循环"""
        while self.is_running:
            try:
                # 定期执行记忆整合
                if datetime.now().minute % 10 == 0:  # 每10分钟
                    await self.memory_system.consolidate_memories()
                
                # 定期应用遗忘机制
                if datetime.now().hour % 6 == 0 and datetime.now().minute == 0:  # 每6小时
                    await self.memory_system.apply_forgetting()
                
                # 更新认知指标
                await self._update_cognitive_metrics()
                
                # 休眠
                await asyncio.sleep(60)  # 每分钟检查一次
            
            except Exception as e:
                self.logger.error(f"Background processing error: {e}")
                await asyncio.sleep(60)
    
    async def _update_cognitive_metrics(self) -> None:
        """更新认知指标"""
        try:
            # 获取各组件统计信息
            memory_stats = await self.memory_system.get_memory_statistics()
            learning_stats = self.learning_module.get_learning_statistics()
            communication_stats = self.communication_manager.get_communication_statistics()
            
            # 计算指标
            self.cognitive_metrics.memory_efficiency = self._calculate_memory_efficiency(memory_stats)
            self.cognitive_metrics.learning_progress = self._calculate_learning_progress(learning_stats)
            self.cognitive_metrics.communication_effectiveness = self._calculate_communication_effectiveness(communication_stats)
            
            # 计算整体性能
            metrics = [
                self.cognitive_metrics.perception_accuracy,
                self.cognitive_metrics.reasoning_consistency,
                self.cognitive_metrics.memory_efficiency,
                self.cognitive_metrics.learning_progress,
                self.cognitive_metrics.communication_effectiveness
            ]
            
            self.cognitive_metrics.overall_performance = sum(metrics) / len(metrics)
            self.cognitive_metrics.last_updated = datetime.now()
        
        except Exception as e:
            self.logger.error(f"Error updating cognitive metrics: {e}")
    
    def _calculate_memory_efficiency(self, memory_stats: Dict[str, Any]) -> float:
        """计算记忆效率"""
        working_memory = memory_stats.get("working_memory", {})
        utilization = working_memory.get("active_items", 0) / working_memory.get("capacity", 1)
        return min(utilization * 2, 1.0)  # 50%利用率 = 100%效率
    
    def _calculate_learning_progress(self, learning_stats: Dict[str, Any]) -> float:
        """计算学习进度"""
        skill_stats = learning_stats.get("skill_acquisition", {})
        avg_proficiency = skill_stats.get("average_proficiency", 0.0)
        return avg_proficiency
    
    def _calculate_communication_effectiveness(self, communication_stats: Dict[str, Any]) -> float:
        """计算通信效果"""
        msg_stats = communication_stats.get("communication_stats", {})
        sent = msg_stats.get("point_to_point_messages", 0) + msg_stats.get("broadcast_messages", 0)
        
        if sent == 0:
            return 0.5  # 中性分数
        
        # 简化的效果计算
        return min(sent / 100, 1.0)  # 发送100条消息 = 100%效果
    
    async def _initialize_skills(self) -> None:
        """初始化技能"""
        # 基于Agent专业领域初始化技能
        for domain in self.identity.expertise_domains:
            skill = Skill(
                skill_id=f"{domain.lower()}_skill",
                name=f"{domain} Skill",
                description=f"Skill in {domain}",
                proficiency_level=0.5  # 初始熟练度50%
            )
            self.learning_module.add_skill(skill)
        
        # 添加通用技能
        general_skills = [
            ("communication", "Communication", "Ability to communicate effectively"),
            ("problem_solving", "Problem Solving", "Ability to solve complex problems"),
            ("learning", "Learning", "Ability to learn from experience"),
            ("reasoning", "Reasoning", "Ability to reason logically")
        ]
        
        for skill_id, name, description in general_skills:
            skill = Skill(
                skill_id=skill_id,
                name=name,
                description=description,
                proficiency_level=0.3  # 初始熟练度30%
            )
            self.learning_module.add_skill(skill)
    
    async def _handle_learning_command(self, command: Dict[str, Any]) -> None:
        """处理学习命令"""
        learning_type_str = command.get("learning_type", "supervised")
        learning_data = command.get("data", [])
        
        try:
            learning_type = LearningType(learning_type_str)
            await self.learning_module.learn(learning_type, learning_data)
            self.logger.info(f"Learning command executed: {learning_type_str}")
        except Exception as e:
            self.logger.error(f"Learning command failed: {e}")
    
    async def _handle_memory_command(self, command: Dict[str, Any]) -> None:
        """处理记忆命令"""
        memory_type_str = command.get("memory_type", "working")
        content = command.get("content", "")
        
        try:
            memory_type = MemoryType(memory_type_str)
            await self.memory_system.store_memory(content, memory_type, **command.get("metadata", {}))
            self.logger.info(f"Memory command executed: {memory_type_str}")
        except Exception as e:
            self.logger.error(f"Memory command failed: {e}")
    
    # UniversalAgent接口实现
    
    def get_capabilities(self) -> List[AgentCapability]:
        """获取Agent能力列表"""
        return [
            AgentCapability.TEXT_PROCESSING,
            AgentCapability.REASONING,
            AgentCapability.LEARNING,
            AgentCapability.MEMORY,
            AgentCapability.COMMUNICATION,
            AgentCapability.PROBLEM_SOLVING,
            AgentCapability.ANALYSIS,
            AgentCapability.PLANNING
        ]
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置Agent参数"""
        self.config.update(config)
        
        # 重新配置各个组件
        if "perception" in config:
            self.perception_engine.config.update(config["perception"])
        
        if "reasoning" in config:
            self.reasoning_engine.config.update(config["reasoning"])
        
        if "memory" in config:
            self.memory_system.config.update(config["memory"])
        
        if "learning" in config:
            self.learning_module.config.update(config["learning"])
    
    def get_status(self) -> AgentStatus:
        """获取Agent状态"""
        if self.cognitive_state == CognitiveState.ERROR:
            return AgentStatus.ERROR
        elif self.cognitive_state == CognitiveState.IDLE:
            return AgentStatus.IDLE
        else:
            return AgentStatus.BUSY
    
    def get_metadata(self) -> AgentMetadata:
        """获取Agent元数据"""
        return AgentMetadata(
            agent_id=self.identity.agent_id,
            name=self.identity.name,
            agent_type="CognitiveAgent",
            version="1.0.0",
            capabilities=self.get_capabilities(),
            status=self.get_status(),
            created_at=self.identity.created_at,
            last_active=datetime.now(),
            metadata={
                "role": self.identity.role,
                "expertise_domains": self.identity.expertise_domains,
                "cognitive_state": self.cognitive_state.value,
                "cognitive_metrics": {
                    "overall_performance": self.cognitive_metrics.overall_performance,
                    "memory_efficiency": self.cognitive_metrics.memory_efficiency,
                    "learning_progress": self.cognitive_metrics.learning_progress
                }
            }
        )
    
    def get_status_info(self) -> Dict[str, Any]:
        """获取详细状态信息"""
        return {
            "identity": {
                "agent_id": self.identity.agent_id,
                "name": self.identity.name,
                "role": self.identity.role,
                "expertise_domains": self.identity.expertise_domains
            },
            "cognitive_state": self.cognitive_state.value,
            "cognitive_metrics": {
                "perception_accuracy": self.cognitive_metrics.perception_accuracy,
                "reasoning_consistency": self.cognitive_metrics.reasoning_consistency,
                "memory_efficiency": self.cognitive_metrics.memory_efficiency,
                "learning_progress": self.cognitive_metrics.learning_progress,
                "communication_effectiveness": self.cognitive_metrics.communication_effectiveness,
                "overall_performance": self.cognitive_metrics.overall_performance,
                "last_updated": self.cognitive_metrics.last_updated.isoformat()
            },
            "execution_history": {
                "total_executions": len(self.execution_history),
                "recent_executions": [
                    {
                        "execution_id": record["execution_id"],
                        "task_content": record["task"].content[:50] + "...",
                        "success": record.get("success", False),
                        "start_time": record["start_time"].isoformat()
                    }
                    for record in self.execution_history[-5:]  # 最近5次执行
                ]
            },
            "component_status": {
                "perception_engine": "initialized" if self.perception_engine.is_initialized else "not_initialized",
                "reasoning_engine": "active",
                "memory_system": "active",
                "learning_module": "active",
                "communication_manager": "running" if self.communication_manager.message_bus.is_running else "stopped"
            },
            "is_running": self.is_running,
            "timestamp": datetime.now().isoformat()
        } 