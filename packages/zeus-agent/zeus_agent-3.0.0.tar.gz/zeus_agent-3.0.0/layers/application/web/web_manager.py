"""
Web Interface Manager
Web界面管理器 - 提供可视化的ADC管理界面
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import webbrowser
import tempfile

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ...business.teams.collaboration_manager import CollaborationManager
from ...business.workflows.workflow_engine import WorkflowEngine
from ...framework.abstractions.agent import UniversalAgent
from ...framework.abstractions.task import UniversalTask
from ...framework.abstractions.context import UniversalContext


class WebInterfaceManager:
    """Web界面管理器"""
    
    def __init__(self):
        self.app = None
        self.server = None
        self.console = Console() if RICH_AVAILABLE else None
        self.port = 8000
        self.host = "localhost"
        self.is_running = False
        
        # 初始化组件
        self.collaboration_manager = CollaborationManager()
        self.workflow_engine = WorkflowEngine()
        
        # 系统状态
        self.system_status = {
            "start_time": datetime.now(),
            "uptime": "0:00:00",
            "total_requests": 0,
            "active_connections": 0,
            "system_health": "healthy"
        }
        
        if FASTAPI_AVAILABLE:
            self._create_app()
    
    def _create_app(self):
        """创建FastAPI应用"""
        self.app = FastAPI(
            title="ADC Web Interface",
            description="Agent Development Center Web管理界面",
            version="3.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 添加CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
        self._register_routes()
        
        # 注册WebSocket
        self._register_websockets()
    
    def _register_routes(self):
        """注册API路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """根路径 - 显示主页面"""
            return self._generate_main_page()
        
        @self.app.get("/api/status")
        async def get_status():
            """获取系统状态"""
            return self._get_system_status()
        
        @self.app.get("/api/agents")
        async def get_agents():
            """获取所有Agent"""
            return self._get_agents()
        
        @self.app.get("/api/workflows")
        async def get_workflows():
            """获取所有工作流"""
            return self._get_workflows()
        
        @self.app.get("/api/teams")
        async def get_teams():
            """获取所有团队"""
            return self._get_teams()
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """获取系统指标"""
            return self._get_system_metrics()
        
        @self.app.post("/api/agents/create")
        async def create_agent(agent_data: Dict[str, Any]):
            """创建新Agent"""
            return await self._create_agent(agent_data)
        
        @self.app.post("/api/workflows/create")
        async def create_workflow(workflow_data: Dict[str, Any]):
            """创建新工作流"""
            return await self._create_workflow(workflow_data)
        
        @self.app.post("/api/teams/create")
        async def create_team(team_data: Dict[str, Any]):
            """创建新团队"""
            return await self._create_team(team_data)
        
        @self.app.post("/api/workflows/{workflow_id}/run")
        async def run_workflow(workflow_id: str, context: Dict[str, Any] = None):
            """运行工作流"""
            return await self._run_workflow(workflow_id, context)
        
        @self.app.get("/api/docs")
        async def get_api_docs():
            """获取API文档"""
            return self._generate_api_docs()
    
    def _register_websockets(self):
        """注册WebSocket连接"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.system_status["active_connections"] += 1
            
            try:
                while True:
                    # 发送实时更新
                    await websocket.send_text(json.dumps({
                        "type": "status_update",
                        "data": self._get_system_status()
                    }))
                    await asyncio.sleep(5)  # 每5秒更新一次
                    
            except WebSocketDisconnect:
                self.system_status["active_connections"] -= 1
    
    def _generate_main_page(self) -> str:
        """生成主页面HTML"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADC Web管理界面</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .card h3 {{
            margin-top: 0;
            color: #fff;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .status-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .status-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4ade80;
        }}
        .status-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .button {{
            background: linear-gradient(45deg, #4ade80, #22c55e);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: transform 0.2s;
        }}
        .button:hover {{
            transform: translateY(-2px);
        }}
        .nav {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            transition: background 0.3s;
        }}
        .nav a:hover {{
            background: rgba(255,255,255,0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ADC Web管理界面</h1>
            <p>Agent Development Center - 下一代AI Agent开发框架</p>
        </div>
        
        <div class="nav">
            <a href="/docs">📚 API文档</a>
            <a href="/api/status">📊 系统状态</a>
            <a href="/api/agents">🤖 Agent管理</a>
            <a href="/api/workflows">⚙️ 工作流管理</a>
            <a href="/api/teams">👥 团队管理</a>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🎯 系统概览</h3>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-value" id="uptime">--</div>
                        <div class="status-label">运行时间</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value" id="requests">--</div>
                        <div class="status-label">总请求数</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value" id="connections">--</div>
                        <div class="status-label">活跃连接</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value" id="health">--</div>
                        <div class="status-label">系统健康</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🔧 快速操作</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="button" onclick="createAgent()">创建Agent</button>
                    <button class="button" onclick="createWorkflow()">创建工作流</button>
                    <button class="button" onclick="createTeam()">创建团队</button>
                    <button class="button" onclick="runDemo()">运行演示</button>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 实时监控</h3>
                <div id="realtime-stats">
                    <p>正在连接实时数据...</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🏗️ 架构状态</h3>
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">基础设施层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">适配器层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">框架抽象层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">智能上下文层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">认知架构层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">业务能力层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">✅</div>
                    <div class="status-label">应用编排层</div>
                </div>
                <div class="status-item">
                    <div class="status-value">🟡</div>
                    <div class="status-label">开发体验层</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 实时更新系统状态
        function updateStatus() {{
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('requests').textContent = data.total_requests;
                    document.getElementById('connections').textContent = data.active_connections;
                    document.getElementById('health').textContent = data.system_health;
                }});
        }}
        
        // 每5秒更新一次状态
        setInterval(updateStatus, 5000);
        updateStatus();
        
        // WebSocket连接
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onmessage = function(event) {{
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {{
                // 更新实时统计
                document.getElementById('realtime-stats').innerHTML = `
                    <p><strong>CPU使用率:</strong> 15%</p>
                    <p><strong>内存使用率:</strong> 45%</p>
                    <p><strong>活跃Agent:</strong> ${{data.data.active_agents || 0}}</p>
                    <p><strong>运行中工作流:</strong> ${{data.data.active_workflows || 0}}</p>
                `;
            }}
        }};
        
        // 快速操作函数
        function createAgent() {{
            alert('Agent创建功能开发中...');
        }}
        
        function createWorkflow() {{
            alert('工作流创建功能开发中...');
        }}
        
        function createTeam() {{
            alert('团队创建功能开发中...');
        }}
        
        function runDemo() {{
            alert('演示功能开发中...');
        }}
    </script>
</body>
</html>
        """
    
    def _get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        # 计算运行时间
        uptime = datetime.now() - self.system_status["start_time"]
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        return {
            "status": "running",
            "version": "3.0.0",
            "start_time": self.system_status["start_time"].isoformat(),
            "uptime": uptime_str,
            "total_requests": self.system_status["total_requests"],
            "active_connections": self.system_status["active_connections"],
            "system_health": self.system_status["system_health"],
            "active_agents": 12,  # 模拟数据
            "active_workflows": 3,  # 模拟数据
            "total_teams": 5,  # 模拟数据
            "architecture_layers": {
                "infrastructure": {"status": "running", "completion": 75},
                "adapter": {"status": "running", "completion": 85},
                "framework_abstraction": {"status": "running", "completion": 98},
                "intelligent_context": {"status": "running", "completion": 80},
                "cognitive_architecture": {"status": "running", "completion": 85},
                "business_capability": {"status": "running", "completion": 95},
                "application_orchestration": {"status": "running", "completion": 100},
                "development_experience": {"status": "partial", "completion": 70}
            }
        }
    
    def _get_agents(self) -> List[Dict[str, Any]]:
        """获取所有Agent"""
        # 模拟Agent数据
        return [
            {
                "id": "agent_001",
                "name": "OpenAI Agent",
                "type": "openai",
                "status": "active",
                "capabilities": ["text_generation", "conversation"],
                "created_at": "2025-08-23T10:00:00Z"
            },
            {
                "id": "agent_002",
                "name": "AutoGen Agent",
                "type": "autogen",
                "status": "active",
                "capabilities": ["collaboration", "task_execution"],
                "created_at": "2025-08-23T10:30:00Z"
            },
            {
                "id": "agent_003",
                "name": "LangGraph Agent",
                "type": "langgraph",
                "status": "active",
                "capabilities": ["workflow_execution", "state_management"],
                "created_at": "2025-08-23T11:00:00Z"
            }
        ]
    
    def _get_workflows(self) -> List[Dict[str, Any]]:
        """获取所有工作流"""
        # 模拟工作流数据
        return [
            {
                "id": "workflow_001",
                "name": "软件开发标准流程",
                "description": "标准的软件开发工作流",
                "status": "active",
                "steps": 6,
                "created_at": "2025-08-23T09:00:00Z"
            },
            {
                "id": "workflow_002",
                "name": "电商平台开发流程",
                "description": "电商平台开发专用工作流",
                "status": "active",
                "steps": 5,
                "created_at": "2025-08-23T09:30:00Z"
            }
        ]
    
    def _get_teams(self) -> List[Dict[str, Any]]:
        """获取所有团队"""
        # 模拟团队数据
        return [
            {
                "id": "team_001",
                "name": "全栈开发团队",
                "description": "负责全栈开发任务",
                "members_count": 7,
                "status": "active",
                "created_at": "2025-08-23T08:00:00Z"
            },
            {
                "id": "team_002",
                "name": "AI研究团队",
                "description": "专注于AI算法研究",
                "members_count": 5,
                "status": "active",
                "created_at": "2025-08-23T08:30:00Z"
            }
        ]
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return {
            "cpu_usage": 15.2,
            "memory_usage": 45.8,
            "disk_usage": 30.1,
            "network_io": 2.5,
            "response_time": 120,
            "success_rate": 99.8,
            "error_rate": 0.2,
            "active_sessions": 8
        }
    
    async def _create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新Agent"""
        # 模拟Agent创建
        agent_id = f"agent_{len(self._get_agents()) + 1:03d}"
        return {
            "id": agent_id,
            "name": agent_data.get("name", "New Agent"),
            "type": agent_data.get("type", "custom"),
            "status": "active",
            "message": "Agent创建成功"
        }
    
    async def _create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新工作流"""
        # 模拟工作流创建
        workflow_id = f"workflow_{len(self._get_workflows()) + 1:03d}"
        return {
            "id": workflow_id,
            "name": workflow_data.get("name", "New Workflow"),
            "description": workflow_data.get("description", ""),
            "status": "active",
            "message": "工作流创建成功"
        }
    
    async def _create_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新团队"""
        # 模拟团队创建
        team_id = f"team_{len(self._get_teams()) + 1:03d}"
        return {
            "id": team_id,
            "name": team_data.get("name", "New Team"),
            "description": team_data.get("description", ""),
            "members_count": len(team_data.get("members", [])),
            "status": "active",
            "message": "团队创建成功"
        }
    
    async def _run_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行工作流"""
        # 模拟工作流执行
        execution_id = f"exec_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "message": "工作流开始执行"
        }
    
    def _generate_api_docs(self) -> str:
        """生成API文档页面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADC API文档</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .method { font-weight: bold; color: #007bff; }
        .url { font-family: monospace; background: #f8f9fa; padding: 5px; }
    </style>
</head>
<body>
    <h1>ADC API文档</h1>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/status</div>
        <p>获取系统状态信息</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/agents</div>
        <p>获取所有Agent列表</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/workflows</div>
        <p>获取所有工作流列表</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/teams</div>
        <p>获取所有团队列表</p>
    </div>
    
    <div class="endpoint">
        <div class="method">POST</div>
        <div class="url">/api/agents/create</div>
        <p>创建新Agent</p>
    </div>
    
    <div class="endpoint">
        <div class="method">POST</div>
        <div class="url">/api/workflows/create</div>
        <p>创建新工作流</p>
    </div>
    
    <div class="endpoint">
        <div class="method">POST</div>
        <div class="url">/api/teams/create</div>
        <p>创建新团队</p>
    </div>
    
    <div class="endpoint">
        <div class="method">POST</div>
        <div class="url">/api/workflows/{workflow_id}/run</div>
        <p>运行指定工作流</p>
    </div>
    
    <div class="endpoint">
        <div class="method">WebSocket</div>
        <div class="url">/ws</div>
        <p>实时状态更新</p>
    </div>
</body>
</html>
        """
    
    async def start(self, host: str = None, port: int = None):
        """启动Web服务器"""
        if not FASTAPI_AVAILABLE:
            if self.console:
                self.console.print("[red]❌ FastAPI未安装，无法启动Web服务器[/red]")
            else:
                print("❌ FastAPI未安装，无法启动Web服务器")
            return False
        
        if host:
            self.host = host
        if port:
            self.port = port
        
        try:
            if self.console:
                self.console.print(f"[green]🚀 启动Web服务器...[/green]")
                self.console.print(f"[blue]📍 地址: http://{self.host}:{self.port}[/blue]")
                self.console.print(f"[blue]📚 API文档: http://{self.host}:{self.port}/docs[/blue]")
                self.console.print(f"[blue]📖 交互式文档: http://{self.host}:{self.port}/redoc[/blue]")
            else:
                print(f"🚀 启动Web服务器...")
                print(f"📍 地址: http://{self.host}:{self.port}")
                print(f"📚 API文档: http://{self.host}:{self.port}/docs")
                print(f"📖 交互式文档: http://{self.host}:{self.port}/redoc")
            
            # 启动服务器
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            
            # 在新线程中启动服务器
            import threading
            server_thread = threading.Thread(target=self.server.run)
            server_thread.daemon = True
            server_thread.start()
            
            self.is_running = True
            
            # 等待服务器启动
            await asyncio.sleep(2)
            
            # 自动打开浏览器
            try:
                webbrowser.open(f"http://{self.host}:{self.port}")
            except:
                pass
            
            if self.console:
                self.console.print("[green]✅ Web服务器启动成功！[/green]")
            else:
                print("✅ Web服务器启动成功！")
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Web服务器启动失败: {e}[/red]")
            else:
                print(f"❌ Web服务器启动失败: {e}")
            return False
    
    async def stop(self):
        """停止Web服务器"""
        if self.server and self.is_running:
            try:
                self.server.should_exit = True
                self.is_running = False
                if self.console:
                    self.console.print("[yellow]🛑 Web服务器已停止[/yellow]")
                else:
                    print("🛑 Web服务器已停止")
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]❌ 停止Web服务器失败: {e}[/red]")
                else:
                    print(f"❌ 停止Web服务器失败: {e}")
    
    def is_server_running(self) -> bool:
        """检查服务器是否运行"""
        return self.is_running


async def main():
    """主函数"""
    web_manager = WebInterfaceManager()
    
    try:
        await web_manager.start()
        
        # 保持运行
        while web_manager.is_server_running():
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        if web_manager.console:
            web_manager.console.print("\n[yellow]⚠️ 收到中断信号，正在停止服务器...[/yellow]")
        else:
            print("\n⚠️ 收到中断信号，正在停止服务器...")
        
        await web_manager.stop()


if __name__ == "__main__":
    asyncio.run(main()) 