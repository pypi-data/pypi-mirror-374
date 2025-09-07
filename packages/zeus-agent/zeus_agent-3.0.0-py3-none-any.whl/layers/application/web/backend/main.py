"""
ADC Web应用后端 - FastAPI
提供Agent管理、工作流编排、团队协作等API接口
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import json

# 创建FastAPI应用
app = FastAPI(
    title="ADC Web API",
    description="Agent Development Center Web应用后端API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class AgentCreate(BaseModel):
    name: str
    description: str
    type: str
    capabilities: List[str]
    config: Dict[str, Any] = {}

class Agent(AgentCreate):
    id: str
    status: str
    created_at: str
    updated_at: str

class WorkflowCreate(BaseModel):
    name: str
    description: str
    steps: List[Dict[str, Any]]

class Workflow(WorkflowCreate):
    id: str
    status: str
    created_at: str
    updated_at: str

class TeamCreate(BaseModel):
    name: str
    description: str
    members: List[Dict[str, str]]

class Team(TeamCreate):
    id: str
    status: str
    created_at: str
    updated_at: str

# 模拟数据存储
agents_db = {}
workflows_db = {}
teams_db = {}

# 工具函数
def generate_id():
    return f"id_{len(agents_db) + len(workflows_db) + len(teams_db) + 1}"

def get_current_time():
    return datetime.now().isoformat()

# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ADC Web API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": get_current_time(),
        "version": "0.1.0"
    }

# Agent管理API
@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """获取所有Agent列表"""
    return list(agents_db.values())

@app.post("/api/agents", response_model=Agent)
async def create_agent(agent: AgentCreate):
    """创建新Agent"""
    agent_id = generate_id()
    new_agent = Agent(
        id=agent_id,
        **agent.dict(),
        status="stopped",
        created_at=get_current_time(),
        updated_at=get_current_time()
    )
    agents_db[agent_id] = new_agent
    return new_agent

@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """获取指定Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.put("/api/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_update: AgentCreate):
    """更新Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    updated_agent = Agent(
        id=agent_id,
        **agent_update.dict(),
        status=agents_db[agent_id].status,
        created_at=agents_db[agent_id].created_at,
        updated_at=get_current_time()
    )
    agents_db[agent_id] = updated_agent
    return updated_agent

@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """删除Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    del agents_db[agent_id]
    return {"message": "Agent deleted successfully"}

@app.post("/api/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """启动Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agents_db[agent_id].status = "running"
    agents_db[agent_id].updated_at = get_current_time()
    return {"message": "Agent started successfully"}

@app.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """停止Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agents_db[agent_id].status = "stopped"
    agents_db[agent_id].updated_at = get_current_time()
    return {"message": "Agent stopped successfully"}

# 工作流管理API
@app.get("/api/workflows", response_model=List[Workflow])
async def get_workflows():
    """获取所有工作流列表"""
    return list(workflows_db.values())

@app.post("/api/workflows", response_model=Workflow)
async def create_workflow(workflow: WorkflowCreate):
    """创建新工作流"""
    workflow_id = generate_id()
    new_workflow = Workflow(
        id=workflow_id,
        **workflow.dict(),
        status="draft",
        created_at=get_current_time(),
        updated_at=get_current_time()
    )
    workflows_db[workflow_id] = new_workflow
    return new_workflow

@app.get("/api/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """获取指定工作流"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows_db[workflow_id]

# 团队管理API
@app.get("/api/teams", response_model=List[Team])
async def get_teams():
    """获取所有团队列表"""
    return list(teams_db.values())

@app.post("/api/teams", response_model=Team)
async def create_team(team: TeamCreate):
    """创建新团队"""
    team_id = generate_id()
    new_team = Team(
        id=team_id,
        **team.dict(),
        status="active",
        created_at=get_current_time(),
        updated_at=get_current_time()
    )
    teams_db[team_id] = new_team
    return new_team

# 系统状态API
@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "agents": {
            "total": len(agents_db),
            "running": len([a for a in agents_db.values() if a.status == "running"]),
            "stopped": len([a for a in agents_db.values() if a.status == "stopped"]),
            "error": len([a for a in agents_db.values() if a.status == "error"])
        },
        "workflows": {
            "total": len(workflows_db),
            "active": len([w for w in workflows_db.values() if w.status == "active"]),
            "completed": len([w for w in workflows_db.values() if w.status == "completed"]),
            "failed": len([w for w in workflows_db.values() if w.status == "failed"])
        },
        "teams": {
            "total": len(teams_db),
            "active": len([t for t in teams_db.values() if t.status == "active"])
        },
        "timestamp": get_current_time()
    }

if __name__ == "__main__":
    # 添加一些示例数据
    agents_db["demo_1"] = Agent(
        id="demo_1",
        name="Demo OpenAI Agent",
        description="演示用的OpenAI Agent",
        type="openai",
        capabilities=["conversation", "text_analysis"],
        config={"model": "gpt-4"},
        status="running",
        created_at=get_current_time(),
        updated_at=get_current_time()
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 