"""
Project Manager
项目管理器，负责管理Agent开发项目
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import copy


class ProjectManager:
    """
    项目管理器
    
    管理Agent开发项目的生命周期
    """
    
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
    
    def create_project(self, name: str, description: str = "") -> str:
        """创建新项目"""
        project_id = str(uuid.uuid4())
        self.projects[project_id] = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now(),
            "status": "active",
            "agents": [],
            "tasks": [],
            "config": {}
        }
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        project = self.projects.get(project_id)
        if project is None:
            return None
        # 返回深拷贝以防止外部修改内部数据
        return copy.deepcopy(project)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """列出所有项目"""
        # 返回深拷贝以防止外部修改内部数据
        return copy.deepcopy(list(self.projects.values()))
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False

    def assign_team(self, project_id: str, team_id: str) -> bool:
        """为项目分配团队"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]["team_id"] = team_id
        self.projects[project_id]["team_assigned_at"] = datetime.now()
        return True
    
    def get_project_team(self, project_id: str) -> Optional[str]:
        """获取项目分配的团队ID"""
        project = self.projects.get(project_id)
        if project is None:
            return None
        return project.get("team_id")
    
    def update_project_status(self, project_id: str, status: str) -> bool:
        """更新项目状态"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]["status"] = status
        self.projects[project_id]["updated_at"] = datetime.now()
        return True
    
    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目状态"""
        project = self.projects.get(project_id)
        if project is None:
            return None
        
        return {
            "project_id": project_id,
            "status": project.get("status", "unknown"),
            "created_at": project.get("created_at"),
            "updated_at": project.get("updated_at"),
            "team_id": project.get("team_id"),
            "team_assigned_at": project.get("team_assigned_at")
        }