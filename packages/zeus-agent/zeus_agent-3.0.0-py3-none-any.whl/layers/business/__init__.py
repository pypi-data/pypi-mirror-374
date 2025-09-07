"""
业务能力层 - Business Capability Layer
提供业务级功能：团队协作、工作流引擎、项目管理
"""

# 项目管理
from .project import ProjectManager

# 团队协作
from .teams.collaboration_manager import CollaborationManager, CollaborationPattern
from .teams.team_engine import TeamManager

# 工作流引擎
from .workflows.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowExecution,
    WorkflowStep, WorkflowStepType, WorkflowStatus, StepStatus
)

# 层间通信管理器
from .communication_manager import (
    BusinessCommunicationManager
)

__all__ = [
    # 项目管理
    "ProjectManager",
    
    # 团队协作
    "CollaborationManager", "CollaborationPattern",
    "TeamManager",
    
    # 工作流引擎
    "WorkflowEngine", "WorkflowDefinition", "WorkflowExecution",
    "WorkflowStep", "WorkflowStepType", "WorkflowStatus", "StepStatus",
    
    # 层间通信管理器
    "BusinessCommunicationManager"
]

__version__ = "1.0.0"
__author__ = "Agent Development Center Business Team" 