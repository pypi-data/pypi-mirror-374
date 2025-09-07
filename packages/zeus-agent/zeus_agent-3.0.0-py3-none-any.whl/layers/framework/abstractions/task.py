"""
Universal Task Abstraction
通用任务抽象，定义框架无关的任务表示
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class TaskPriority(Enum):
    """任务优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型"""
    CONVERSATION = "conversation"
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATION = "file_operation"
    WEB_SEARCH = "web_search"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    TOOL_EXECUTION = "tool_execution"
    CUSTOM = "custom"
    
    # 业务任务类型
    CREATIVE = "creative"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"
    PROJECT = "project"
    COMPLEX_PROJECT = "complex_project"
    WORKFLOW = "workflow"
    COLLABORATION = "collaboration"
    COMPLEX_REASONING = "complex_reasoning"


@dataclass
class TaskRequirements:
    """任务需求"""
    capabilities: List[str] = field(default_factory=list)
    max_execution_time: Optional[int] = None  # seconds
    memory_limit: Optional[int] = None  # MB
    preferred_framework: Optional[str] = None
    fallback_frameworks: List[str] = field(default_factory=list)


@dataclass
class TaskMetadata:
    """任务元数据"""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    retries: int = 0
    max_retries: int = 3


class UniversalTask:
    """
    通用任务类
    
    提供框架无关的任务表示
    """
    
    def __init__(self,
                 content: Optional[str] = None,
                 task_type: TaskType = TaskType.CONVERSATION,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 requirements: Optional[TaskRequirements] = None,
                 context: Optional[Dict[str, Any]] = None,
                 task_id: Optional[str] = None,
                 description: Optional[str] = None):
        
        self.id = task_id or str(uuid.uuid4())
        self.task_id = self.id  # 添加task_id别名以保持兼容性
        # 支持content或description参数
        self.content = content or description or ""
        self.description = description or content or ""
        self.task_type = task_type
        self.priority = priority
        self.requirements = requirements or TaskRequirements()
        self.context = context or {}
        self.status = TaskStatus.PENDING
        self.metadata = TaskMetadata()
        
        # 存储任务结果和错误信息
        self.result: Optional['UniversalResult'] = None
        self.error: Optional[str] = None
    
    def start(self) -> None:
        """开始执行任务"""
        self.status = TaskStatus.RUNNING
        self.metadata.started_at = datetime.now()
    
    def complete(self, result: 'UniversalResult') -> None:
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.metadata.completed_at = datetime.now()
        
        if self.metadata.started_at:
            self.metadata.execution_time = (self.metadata.completed_at - self.metadata.started_at).total_seconds()
    
    def fail(self, error: str) -> None:
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.metadata.completed_at = datetime.now()
        
        if self.metadata.started_at:
            self.metadata.execution_time = (self.metadata.completed_at - self.metadata.started_at).total_seconds()
    
    def cancel(self) -> None:
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.metadata.completed_at = datetime.now()
        
        if self.metadata.started_at:
            self.metadata.execution_time = (self.metadata.completed_at - self.metadata.started_at).total_seconds()
    
    def retry(self) -> bool:
        """重试任务"""
        if self.metadata.retries < self.metadata.max_retries:
            self.metadata.retries += 1
            self.status = TaskStatus.PENDING
            self.error = None
            self.result = None
            return True
        return False
    
    def add_context(self, key: str, value: Any) -> None:
        """添加上下文信息"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文信息"""
        return self.context.get(key, default)
    
    def has_context(self, key: str) -> bool:
        """检查是否有指定的上下文信息"""
        return key in self.context
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "requirements": {
                "capabilities": self.requirements.capabilities,
                "max_execution_time": self.requirements.max_execution_time,
                "memory_limit": self.requirements.memory_limit,
                "preferred_framework": self.requirements.preferred_framework,
                "fallback_frameworks": self.requirements.fallback_frameworks
            },
            "context": self.context,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "started_at": self.metadata.started_at.isoformat() if self.metadata.started_at else None,
                "completed_at": self.metadata.completed_at.isoformat() if self.metadata.completed_at else None,
                "execution_time": self.metadata.execution_time,
                "retries": self.metadata.retries,
                "max_retries": self.metadata.max_retries
            },
            "error": self.error,
            "result": self.result.to_dict() if self.result else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalTask':
        """从字典创建任务"""
        task = cls(
            content=data["content"],
            task_type=TaskType(data["task_type"]),
            priority=TaskPriority(data["priority"]),
            task_id=data.get("id")
        )
        
        # 设置需求
        req_data = data.get("requirements", {})
        task.requirements = TaskRequirements(
            capabilities=req_data.get("capabilities", []),
            max_execution_time=req_data.get("max_execution_time"),
            memory_limit=req_data.get("memory_limit"),
            preferred_framework=req_data.get("preferred_framework"),
            fallback_frameworks=req_data.get("fallback_frameworks", [])
        )
        
        # 设置上下文
        task.context = data.get("context", {})
        
        # 设置状态
        task.status = TaskStatus(data["status"])
        
        # 设置元数据
        meta_data = data.get("metadata", {})
        task.metadata = TaskMetadata(
            created_at=datetime.fromisoformat(meta_data["created_at"]) if meta_data.get("created_at") else datetime.now(),
            started_at=datetime.fromisoformat(meta_data["started_at"]) if meta_data.get("started_at") else None,
            completed_at=datetime.fromisoformat(meta_data["completed_at"]) if meta_data.get("completed_at") else None,
            execution_time=meta_data.get("execution_time"),
            retries=meta_data.get("retries", 0),
            max_retries=meta_data.get("max_retries", 3)
        )
        
        # 设置错误和结果
        task.error = data.get("error")
        if data.get("result"):
            from .result import UniversalResult
            task.result = UniversalResult.from_dict(data["result"])
        
        return task
    
    def __str__(self) -> str:
        return f"UniversalTask(id='{self.id}', type='{self.task_type.value}', status='{self.status.value}', content='{self.content[:50]}...')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # 增强的任务执行流程方法
    
    def validate(self) -> List[str]:
        """验证任务是否有效"""
        errors = []
        
        if not self.content.strip():
            errors.append("Task content cannot be empty")
        
        if self.requirements.max_execution_time is not None and self.requirements.max_execution_time <= 0:
            errors.append("Max execution time must be positive")
        
        if self.requirements.memory_limit is not None and self.requirements.memory_limit <= 0:
            errors.append("Memory limit must be positive")
        
        return errors
    
    def is_valid(self) -> bool:
        """检查任务是否有效"""
        return len(self.validate()) == 0
    
    def can_execute(self) -> bool:
        """检查任务是否可以执行"""
        return (
            self.status in [TaskStatus.PENDING, TaskStatus.RUNNING] and
            self.is_valid() and
            self.metadata.retries <= self.metadata.max_retries
        )
    
    def is_timeout(self) -> bool:
        """检查任务是否超时"""
        if not self.requirements.max_execution_time or not self.metadata.started_at:
            return False
        
        elapsed = (datetime.now() - self.metadata.started_at).total_seconds()
        return elapsed > self.requirements.max_execution_time
    
    def get_elapsed_time(self) -> Optional[float]:
        """获取已执行时间（秒）"""
        if not self.metadata.started_at:
            return None
        
        end_time = self.metadata.completed_at or datetime.now()
        return (end_time - self.metadata.started_at).total_seconds()
    
    def get_remaining_time(self) -> Optional[float]:
        """获取剩余执行时间（秒）"""
        if not self.requirements.max_execution_time:
            return None
        
        elapsed = self.get_elapsed_time()
        if elapsed is None:
            return self.requirements.max_execution_time
        
        return max(0, self.requirements.max_execution_time - elapsed)
    
    def add_checkpoint(self, name: str, data: Dict[str, Any] = None) -> None:
        """添加检查点"""
        if not hasattr(self, 'checkpoints'):
            self.checkpoints = []
        
        checkpoint = {
            "name": name,
            "timestamp": datetime.now(),
            "data": data or {}
        }
        self.checkpoints.append(checkpoint)
    
    def get_checkpoints(self) -> List[Dict[str, Any]]:
        """获取所有检查点"""
        return getattr(self, 'checkpoints', [])
    
    def merge_context(self, other_context: Dict[str, Any]) -> None:
        """合并上下文信息"""
        if other_context:
            self.context.update(other_context) 