"""
Universal Result Abstraction
通用结果抽象，提供框架无关的任务执行结果表示
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json


class ResultStatus(Enum):
    """结果状态"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ResultType(Enum):
    """结果类型"""
    TEXT = "text"
    CODE = "code"
    FILE = "file"
    JSON = "json"
    BINARY = "binary"
    MULTIMODAL = "multimodal"
    STRUCTURED = "structured"
    ANALYSIS = "analysis"


@dataclass
class ResultMetadata:
    """结果元数据"""
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None  # bytes
    token_usage: Optional[Dict[str, int]] = None
    model_info: Optional[Dict[str, Any]] = None
    framework_info: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    
@dataclass
class ErrorInfo:
    """错误信息"""
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    retry_suggestions: List[str] = field(default_factory=list)


class UniversalResult:
    """
    通用结果类
    
    提供框架无关的任务执行结果表示
    """
    
    def __init__(self,
                 content: Any = None,
                 status: ResultStatus = ResultStatus.SUCCESS,
                 result_type: ResultType = ResultType.TEXT,
                 metadata: Optional[Union[ResultMetadata, Dict[str, Any]]] = None,
                 error: Optional[ErrorInfo] = None,
                 task_id: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None):
        
        # 支持content或data参数
        self.content = content if content is not None else data
        self.data = data if data is not None else content
        self.status = status
        self.result_type = result_type
        self.task_id = task_id
        
        # 处理metadata参数
        if isinstance(metadata, dict):
            self.metadata = ResultMetadata()
            self.metadata_dict = metadata
        else:
            self.metadata = metadata or ResultMetadata()
            self.metadata_dict = {}
            
        self.error = error
        
        # 额外的结果数据
        self.artifacts: List[Dict[str, Any]] = []
        self.intermediate_steps: List[Dict[str, Any]] = []
        self.citations: List[Dict[str, Any]] = []
        self.confidence_score: Optional[float] = None
    
    def add_artifact(self, name: str, content: Any, artifact_type: str = "file") -> None:
        """添加结果工件"""
        artifact = {
            "name": name,
            "content": content,
            "type": artifact_type,
            "created_at": datetime.now().isoformat()
        }
        self.artifacts.append(artifact)
    
    def add_intermediate_step(self, step_name: str, description: str, data: Any = None) -> None:
        """添加中间步骤"""
        step = {
            "step_name": step_name,
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.intermediate_steps.append(step)
    
    def add_citation(self, source: str, title: str, url: Optional[str] = None, content: Optional[str] = None) -> None:
        """添加引用"""
        citation = {
            "source": source,
            "title": title,
            "url": url,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.citations.append(citation)
    
    def is_successful(self) -> bool:
        """检查是否成功"""
        return self.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL_SUCCESS]
    
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self.status in [ResultStatus.FAILURE, ResultStatus.ERROR, ResultStatus.TIMEOUT]
    
    def get_text_content(self) -> str:
        """获取文本内容"""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, dict):
            return json.dumps(self.content, ensure_ascii=False, indent=2)
        else:
            return str(self.content)
    
    def get_json_content(self) -> Dict[str, Any]:
        """获取JSON内容"""
        if isinstance(self.content, dict):
            return self.content
        elif isinstance(self.content, str):
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {"text": self.content}
        else:
            return {"value": self.content}
    
    def get_artifacts_by_type(self, artifact_type: str) -> List[Dict[str, Any]]:
        """按类型获取工件"""
        return [artifact for artifact in self.artifacts if artifact["type"] == artifact_type]
    
    def get_artifact(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定名称的工件"""
        for artifact in self.artifacts:
            if artifact["name"] == name:
                return artifact
        return None
    
    def set_confidence_score(self, score: float) -> None:
        """设置置信度分数"""
        if 0.0 <= score <= 1.0:
            self.confidence_score = score
        else:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "status": self.status.value,
            "result_type": self.result_type.value,
            "metadata": {
                "execution_time": self.metadata.execution_time,
                "memory_usage": self.metadata.memory_usage,
                "token_usage": self.metadata.token_usage,
                "model_info": self.metadata.model_info,
                "framework_info": self.metadata.framework_info,
                "created_at": self.metadata.created_at.isoformat()
            },
            "error": {
                "error_type": self.error.error_type,
                "error_message": self.error.error_message,
                "error_code": self.error.error_code,
                "stack_trace": self.error.stack_trace,
                "retry_suggestions": self.error.retry_suggestions
            } if self.error else None,
            "artifacts": self.artifacts,
            "intermediate_steps": self.intermediate_steps,
            "citations": self.citations,
            "confidence_score": self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalResult':
        """从字典创建结果"""
        # 创建元数据
        metadata_data = data.get("metadata", {})
        metadata = ResultMetadata(
            execution_time=metadata_data.get("execution_time"),
            memory_usage=metadata_data.get("memory_usage"),
            token_usage=metadata_data.get("token_usage"),
            model_info=metadata_data.get("model_info"),
            framework_info=metadata_data.get("framework_info"),
            created_at=datetime.fromisoformat(metadata_data["created_at"]) if metadata_data.get("created_at") else datetime.now()
        )
        
        # 创建错误信息
        error_data = data.get("error")
        error = None
        if error_data:
            error = ErrorInfo(
                error_type=error_data["error_type"],
                error_message=error_data["error_message"],
                error_code=error_data.get("error_code"),
                stack_trace=error_data.get("stack_trace"),
                retry_suggestions=error_data.get("retry_suggestions", [])
            )
        
        # 创建结果对象
        result = cls(
            content=data["content"],
            status=ResultStatus(data["status"]),
            result_type=ResultType(data["result_type"]),
            metadata=metadata,
            error=error
        )
        
        # 设置额外数据
        result.artifacts = data.get("artifacts", [])
        result.intermediate_steps = data.get("intermediate_steps", [])
        result.citations = data.get("citations", [])
        result.confidence_score = data.get("confidence_score")
        
        return result
    
    def __str__(self) -> str:
        status_str = self.status.value
        content_preview = str(self.content)[:50] + "..." if len(str(self.content)) > 50 else str(self.content)
        return f"UniversalResult(status='{status_str}', type='{self.result_type.value}', content='{content_preview}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # 增强的结果处理功能
    
    def validate(self) -> List[str]:
        """验证结果是否有效"""
        errors = []
        
        if self.content is None:
            errors.append("Result content cannot be None")
        
        if self.confidence_score is not None and not (0.0 <= self.confidence_score <= 1.0):
            errors.append("Confidence score must be between 0.0 and 1.0")
        
        if self.status == ResultStatus.ERROR and not self.error:
            errors.append("Error status requires error information")
        
        return errors
    
    def is_valid(self) -> bool:
        """检查结果是否有效"""
        return len(self.validate()) == 0
    

    
    def has_high_confidence(self, threshold: float = 0.8) -> bool:
        """检查是否有高置信度"""
        return self.confidence_score is not None and self.confidence_score >= threshold
    
    def get_quality_score(self) -> float:
        """计算结果质量分数"""
        score = 0.0
        
        # 基础分数：成功状态
        if self.is_successful():
            score += 0.4
        
        # 置信度分数
        if self.confidence_score is not None:
            score += 0.3 * self.confidence_score
        
        # 内容质量
        if self.content and len(str(self.content).strip()) > 0:
            score += 0.2
        
        # 元数据完整性
        if self.metadata.execution_time is not None:
            score += 0.05
        if self.metadata.token_usage:
            score += 0.05
        
        return min(1.0, score)
    
    def merge_with(self, other: 'UniversalResult', strategy: str = 'combine') -> 'UniversalResult':
        """与另一个结果合并"""
        if strategy == 'combine':
            # 合并内容
            if isinstance(self.content, str) and isinstance(other.content, str):
                merged_content = f"{self.content}\n{other.content}"
            elif isinstance(self.content, list) and isinstance(other.content, list):
                merged_content = self.content + other.content
            else:
                merged_content = [self.content, other.content]
            
            # 合并工件
            merged_artifacts = self.artifacts + other.artifacts
            
            # 合并中间步骤
            merged_steps = self.intermediate_steps + other.intermediate_steps
            
            # 合并引用
            merged_citations = self.citations + other.citations
            
            # 计算平均置信度
            confidence_scores = [s for s in [self.confidence_score, other.confidence_score] if s is not None]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
            
            return UniversalResult(
                content=merged_content,
                status=self.status if self.is_successful() else other.status,
                result_type=self.result_type,
                metadata=self.metadata,  # 使用第一个结果的元数据
                artifacts=merged_artifacts,
                intermediate_steps=merged_steps,
                citations=merged_citations,
                confidence_score=avg_confidence
            )
        
        elif strategy == 'prefer_better':
            # 选择质量更好的结果
            return self if self.get_quality_score() >= other.get_quality_score() else other
        
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
    
    def extract_key_insights(self, max_insights: int = 5) -> List[str]:
        """提取关键见解"""
        insights = []
        
        # 从内容中提取见解（简单的基于关键词的方法）
        if isinstance(self.content, str):
            content_lower = self.content.lower()
            
            # 查找关键模式
            patterns = [
                ("important", "重要发现"),
                ("significant", "重要意义"),
                ("key point", "关键点"),
                ("conclusion", "结论"),
                ("recommendation", "建议")
            ]
            
            for pattern, label in patterns:
                if pattern in content_lower and len(insights) < max_insights:
                    # 提取包含关键词的句子
                    sentences = self.content.split('.')
                    for sentence in sentences:
                        if pattern in sentence.lower() and len(insights) < max_insights:
                            insights.append(f"{label}: {sentence.strip()}")
                            break
        
        return insights
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = {}
        
        if self.metadata.execution_time is not None:
            metrics["execution_time_seconds"] = self.metadata.execution_time
            
            # 性能等级
            if self.metadata.execution_time < 1.0:
                metrics["performance_level"] = "excellent"
            elif self.metadata.execution_time < 5.0:
                metrics["performance_level"] = "good"
            elif self.metadata.execution_time < 10.0:
                metrics["performance_level"] = "average"
            else:
                metrics["performance_level"] = "slow"
        
        if self.metadata.memory_usage:
            metrics["memory_usage_mb"] = self.metadata.memory_usage
        
        if self.metadata.token_usage:
            metrics["token_usage"] = self.metadata.token_usage
            
            # 效率指标
            if "total_tokens" in self.metadata.token_usage:
                total_tokens = self.metadata.token_usage["total_tokens"]
                if self.metadata.execution_time:
                    metrics["tokens_per_second"] = total_tokens / self.metadata.execution_time
        
        metrics["quality_score"] = self.get_quality_score()
        
        return metrics
    
    def create_summary(self) -> Dict[str, Any]:
        """创建结果摘要"""
        return {
            "status": self.status.value,
            "type": self.result_type.value,
            "success": self.is_successful(),
            "confidence": self.confidence_score,
            "quality_score": self.get_quality_score(),
            "content_length": len(str(self.content)) if self.content else 0,
            "has_artifacts": len(self.artifacts) > 0,
            "has_citations": len(self.citations) > 0,
            "step_count": len(self.intermediate_steps),
            "execution_time": self.metadata.execution_time,
            "created_at": self.metadata.created_at.isoformat()
        } 