"""
API Documentation Generator
API文档生成器 - 自动生成完整的API文档
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import inspect
import importlib

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


class APIDocsGenerator:
    """API文档生成器"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.output_dir = Path("docs/api")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API端点信息
        self.endpoints = []
        
        # 组件信息
        self.components = {}
        
        # 示例数据
        self.examples = {}
    
    def generate_all_docs(self):
        """生成所有API文档"""
        if self.console:
            self.console.print("[green]🚀 开始生成API文档...[/green]")
        else:
            print("🚀 开始生成API文档...")
        
        # 收集API端点信息
        self._collect_endpoints()
        
        # 收集组件信息
        self._collect_components()
        
        # 生成示例数据
        self._generate_examples()
        
        # 生成各种格式的文档
        self._generate_markdown_docs()
        self._generate_html_docs()
        self._generate_openapi_spec()
        self._generate_postman_collection()
        
        if self.console:
            self.console.print("[green]✅ API文档生成完成！[/green]")
        else:
            print("✅ API文档生成完成！")
    
    def _collect_endpoints(self):
        """收集API端点信息"""
        self.endpoints = [
            {
                "path": "/",
                "method": "GET",
                "summary": "主页面",
                "description": "ADC Web管理界面主页面",
                "response_type": "HTML",
                "tags": ["UI"]
            },
            {
                "path": "/api/status",
                "method": "GET",
                "summary": "获取系统状态",
                "description": "获取ADC系统的整体状态信息",
                "response_type": "JSON",
                "tags": ["System"],
                "parameters": [],
                "responses": {
                    "200": {
                        "description": "成功获取系统状态",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "example": "running"},
                                "version": {"type": "string", "example": "3.0.0"},
                                "uptime": {"type": "string", "example": "2:30:15"},
                                "system_health": {"type": "string", "example": "healthy"}
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/agents",
                "method": "GET",
                "summary": "获取所有Agent",
                "description": "获取系统中所有注册的Agent列表",
                "response_type": "JSON",
                "tags": ["Agents"],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "Agent状态过滤",
                        "required": False,
                        "schema": {"type": "string", "enum": ["active", "inactive", "all"]}
                    },
                    {
                        "name": "type",
                        "in": "query",
                        "description": "Agent类型过滤",
                        "required": False,
                        "schema": {"type": "string", "enum": ["openai", "autogen", "langgraph", "custom"]}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功获取Agent列表",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "example": "agent_001"},
                                    "name": {"type": "string", "example": "OpenAI Agent"},
                                    "type": {"type": "string", "example": "openai"},
                                    "status": {"type": "string", "example": "active"},
                                    "capabilities": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/agents/create",
                "method": "POST",
                "summary": "创建新Agent",
                "description": "创建并注册新的Agent到系统",
                "response_type": "JSON",
                "tags": ["Agents"],
                "request_body": {
                    "description": "Agent创建参数",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "type"],
                                "properties": {
                                    "name": {"type": "string", "description": "Agent名称", "example": "My Custom Agent"},
                                    "type": {"type": "string", "description": "Agent类型", "example": "custom"},
                                    "description": {"type": "string", "description": "Agent描述", "example": "一个自定义的Agent"},
                                    "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Agent能力列表"},
                                    "config": {"type": "object", "description": "Agent配置参数"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Agent创建成功",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "example": "agent_004"},
                                "name": {"type": "string", "example": "My Custom Agent"},
                                "status": {"type": "string", "example": "active"},
                                "message": {"type": "string", "example": "Agent创建成功"}
                            }
                        }
                    },
                    "400": {
                        "description": "请求参数错误",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "缺少必需的参数: name"}
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/workflows",
                "method": "GET",
                "summary": "获取所有工作流",
                "description": "获取系统中所有注册的工作流列表",
                "response_type": "JSON",
                "tags": ["Workflows"],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "工作流状态过滤",
                        "required": False,
                        "schema": {"type": "string", "enum": ["active", "inactive", "draft"]}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功获取工作流列表",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "example": "workflow_001"},
                                    "name": {"type": "string", "example": "软件开发标准流程"},
                                    "description": {"type": "string", "example": "标准的软件开发工作流"},
                                    "status": {"type": "string", "example": "active"},
                                    "steps": {"type": "integer", "example": 6}
                                }
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/workflows/create",
                "method": "POST",
                "summary": "创建新工作流",
                "description": "创建并注册新的工作流到系统",
                "response_type": "JSON",
                "tags": ["Workflows"],
                "request_body": {
                    "description": "工作流创建参数",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "description": "工作流名称", "example": "数据分析流程"},
                                    "description": {"type": "string", "description": "工作流描述"},
                                    "steps": {"type": "array", "items": {"type": "object"}, "description": "工作流步骤定义"},
                                    "config": {"type": "object", "description": "工作流配置参数"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "工作流创建成功",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "example": "workflow_003"},
                                "name": {"type": "string", "example": "数据分析流程"},
                                "status": {"type": "string", "example": "active"},
                                "message": {"type": "string", "example": "工作流创建成功"}
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/workflows/{workflow_id}/run",
                "method": "POST",
                "summary": "运行工作流",
                "description": "执行指定的工作流",
                "response_type": "JSON",
                "tags": ["Workflows"],
                "parameters": [
                    {
                        "name": "workflow_id",
                        "in": "path",
                        "description": "工作流ID",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "request_body": {
                    "description": "工作流执行上下文",
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "context": {"type": "object", "description": "执行上下文数据"},
                                    "parameters": {"type": "object", "description": "执行参数"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "工作流开始执行",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "execution_id": {"type": "string", "example": "exec_workflow_001_20250823_143000"},
                                "workflow_id": {"type": "string", "example": "workflow_001"},
                                "status": {"type": "string", "example": "running"},
                                "start_time": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "404": {
                        "description": "工作流不存在",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "工作流不存在: workflow_999"}
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/teams",
                "method": "GET",
                "summary": "获取所有团队",
                "description": "获取系统中所有注册的团队列表",
                "response_type": "JSON",
                "tags": ["Teams"],
                "responses": {
                    "200": {
                        "description": "成功获取团队列表",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "example": "team_001"},
                                    "name": {"type": "string", "example": "全栈开发团队"},
                                    "description": {"type": "string", "example": "负责全栈开发任务"},
                                    "members_count": {"type": "integer", "example": 7},
                                    "status": {"type": "string", "example": "active"}
                                }
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/teams/create",
                "method": "POST",
                "summary": "创建新团队",
                "description": "创建并注册新的团队到系统",
                "response_type": "JSON",
                "tags": ["Teams"],
                "request_body": {
                    "description": "团队创建参数",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "description": "团队名称", "example": "AI研究团队"},
                                    "description": {"type": "string", "description": "团队描述"},
                                    "members": {"type": "array", "items": {"type": "string"}, "description": "团队成员列表"},
                                    "config": {"type": "object", "description": "团队配置参数"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "团队创建成功",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "example": "team_003"},
                                "name": {"type": "string", "example": "AI研究团队"},
                                "status": {"type": "string", "example": "active"},
                                "message": {"type": "string", "example": "团队创建成功"}
                            }
                        }
                    }
                }
            },
            {
                "path": "/api/metrics",
                "method": "GET",
                "summary": "获取系统指标",
                "description": "获取系统性能指标和统计信息",
                "response_type": "JSON",
                "tags": ["System"],
                "responses": {
                    "200": {
                        "description": "成功获取系统指标",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "cpu_usage": {"type": "number", "format": "float", "example": 15.2},
                                "memory_usage": {"type": "number", "format": "float", "example": 45.8},
                                "disk_usage": {"type": "number", "format": "float", "example": 30.1},
                                "network_io": {"type": "number", "format": "float", "example": 2.5},
                                "response_time": {"type": "integer", "example": 120},
                                "success_rate": {"type": "number", "format": "float", "example": 99.8}
                            }
                        }
                    }
                }
            },
            {
                "path": "/ws",
                "method": "WebSocket",
                "summary": "实时状态更新",
                "description": "WebSocket连接，提供实时系统状态更新",
                "response_type": "WebSocket",
                "tags": ["Real-time"],
                "responses": {
                    "101": {
                        "description": "WebSocket连接升级成功",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "example": "status_update"},
                                "data": {"type": "object", "description": "状态数据"}
                            }
                        }
                    }
                }
            }
        ]
    
    def _collect_components(self):
        """收集组件信息"""
        self.components = {
            "schemas": {
                "Agent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Agent唯一标识符"},
                        "name": {"type": "string", "description": "Agent名称"},
                        "type": {"type": "string", "description": "Agent类型", "enum": ["openai", "autogen", "langgraph", "custom"]},
                        "status": {"type": "string", "description": "Agent状态", "enum": ["active", "inactive", "error"]},
                        "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Agent能力列表"},
                        "created_at": {"type": "string", "format": "date-time", "description": "创建时间"},
                        "updated_at": {"type": "string", "format": "date-time", "description": "更新时间"}
                    },
                    "required": ["id", "name", "type", "status"]
                },
                "Workflow": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "工作流唯一标识符"},
                        "name": {"type": "string", "description": "工作流名称"},
                        "description": {"type": "string", "description": "工作流描述"},
                        "status": {"type": "string", "description": "工作流状态", "enum": ["active", "inactive", "draft"]},
                        "steps": {"type": "array", "items": {"type": "object"}, "description": "工作流步骤定义"},
                        "created_at": {"type": "string", "format": "date-time", "description": "创建时间"}
                    },
                    "required": ["id", "name", "status"]
                },
                "Team": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "团队唯一标识符"},
                        "name": {"type": "string", "description": "团队名称"},
                        "description": {"type": "string", "description": "团队描述"},
                        "members_count": {"type": "integer", "description": "成员数量"},
                        "status": {"type": "string", "description": "团队状态", "enum": ["active", "inactive"]},
                        "created_at": {"type": "string", "format": "date-time", "description": "创建时间"}
                    },
                    "required": ["id", "name", "status"]
                },
                "SystemStatus": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "系统状态", "enum": ["running", "stopped", "error"]},
                        "version": {"type": "string", "description": "系统版本"},
                        "uptime": {"type": "string", "description": "运行时间"},
                        "system_health": {"type": "string", "description": "系统健康状态", "enum": ["healthy", "warning", "critical"]},
                        "active_agents": {"type": "integer", "description": "活跃Agent数量"},
                        "active_workflows": {"type": "integer", "description": "活跃工作流数量"}
                    },
                    "required": ["status", "version", "system_health"]
                }
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API密钥认证"
                }
            }
        }
    
    def _generate_examples(self):
        """生成示例数据"""
        self.examples = {
            "create_agent": {
                "summary": "创建OpenAI Agent",
                "value": {
                    "name": "OpenAI Assistant",
                    "type": "openai",
                    "description": "基于OpenAI的智能助手",
                    "capabilities": ["text_generation", "conversation", "code_assistance"],
                    "config": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                }
            },
            "create_workflow": {
                "summary": "创建数据分析工作流",
                "value": {
                    "name": "数据分析流程",
                    "description": "标准的数据分析工作流程",
                    "steps": [
                        {"name": "数据收集", "type": "data_collection", "order": 1},
                        {"name": "数据清洗", "type": "data_cleaning", "order": 2},
                        {"name": "数据分析", "type": "data_analysis", "order": 3},
                        {"name": "结果输出", "type": "result_output", "order": 4}
                    ]
                }
            },
            "create_team": {
                "summary": "创建开发团队",
                "value": {
                    "name": "全栈开发团队",
                    "description": "负责全栈开发任务的专业团队",
                    "members": ["alice", "bob", "charlie", "diana"],
                    "config": {
                        "collaboration_pattern": "parallel",
                        "communication_tools": ["slack", "github", "jira"]
                    }
                }
            }
        }
    
    def _generate_markdown_docs(self):
        """生成Markdown格式的API文档"""
        md_file = self.output_dir / "API_REFERENCE.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# ADC API 参考文档\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**版本**: v3.0.0\n\n")
            
            f.write("## 📋 目录\n\n")
            f.write("- [概述](#概述)\n")
            f.write("- [认证](#认证)\n")
            f.write("- [端点](#端点)\n")
            f.write("- [数据模型](#数据模型)\n")
            f.write("- [示例](#示例)\n")
            f.write("- [错误处理](#错误处理)\n\n")
            
            f.write("## 📖 概述\n\n")
            f.write("ADC (Agent Development Center) 提供了完整的RESTful API，用于管理AI Agent、工作流、团队等资源。\n\n")
            
            f.write("### 基础URL\n")
            f.write("```\nhttp://localhost:8000\n```\n\n")
            
            f.write("### 响应格式\n")
            f.write("所有API响应都使用JSON格式，包含以下字段：\n")
            f.write("- `status`: 响应状态\n")
            f.write("- `data`: 响应数据\n")
            f.write("- `message`: 响应消息\n")
            f.write("- `timestamp`: 响应时间戳\n\n")
            
            f.write("## 🔐 认证\n\n")
            f.write("目前API使用API密钥认证，在请求头中添加：\n")
            f.write("```\nX-API-Key: your_api_key_here\n```\n\n")
            
            f.write("## 🌐 端点\n\n")
            
            # 按标签分组端点
            tags = {}
            for endpoint in self.endpoints:
                for tag in endpoint.get('tags', ['Other']):
                    if tag not in tags:
                        tags[tag] = []
                    tags[tag].append(endpoint)
            
            for tag, tag_endpoints in tags.items():
                f.write(f"### {tag}\n\n")
                
                for endpoint in tag_endpoints:
                    f.write(f"#### {endpoint['method']} {endpoint['path']}\n\n")
                    f.write(f"**摘要**: {endpoint['summary']}\n\n")
                    f.write(f"**描述**: {endpoint['description']}\n\n")
                    
                    if 'parameters' in endpoint:
                        f.write("**参数**:\n\n")
                        for param in endpoint['parameters']:
                            f.write(f"- `{param['name']}` ({param['in']}) - {param['description']}")
                            if param.get('required'):
                                f.write(" **[必需]**")
                            f.write("\n")
                        f.write("\n")
                    
                    if 'request_body' in endpoint:
                        f.write("**请求体**:\n\n")
                        f.write(f"```json\n{json.dumps(endpoint['request_body']['content']['application/json']['schema'], indent=2, ensure_ascii=False)}\n```\n\n")
                    
                    if 'responses' in endpoint:
                        f.write("**响应**:\n\n")
                        for status_code, response in endpoint['responses'].items():
                            f.write(f"**{status_code}** - {response['description']}\n\n")
                            if 'schema' in response:
                                f.write(f"```json\n{json.dumps(response['schema'], indent=2, ensure_ascii=False)}\n```\n\n")
                
                f.write("---\n\n")
            
            f.write("## 📊 数据模型\n\n")
            
            for schema_name, schema in self.components['schemas'].items():
                f.write(f"### {schema_name}\n\n")
                f.write(f"```json\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n```\n\n")
            
            f.write("## 💡 示例\n\n")
            
            for example_name, example in self.examples.items():
                f.write(f"### {example['summary']}\n\n")
                f.write(f"```json\n{json.dumps(example['value'], indent=2, ensure_ascii=False)}\n```\n\n")
            
            f.write("## ❌ 错误处理\n\n")
            f.write("API使用标准HTTP状态码表示请求结果：\n\n")
            f.write("- `200 OK` - 请求成功\n")
            f.write("- `201 Created` - 资源创建成功\n")
            f.write("- `400 Bad Request` - 请求参数错误\n")
            f.write("- `401 Unauthorized` - 认证失败\n")
            f.write("- `404 Not Found` - 资源不存在\n")
            f.write("- `500 Internal Server Error` - 服务器内部错误\n\n")
            
            f.write("错误响应格式：\n")
            f.write("```json\n{\n")
            f.write('  "error": "错误描述",\n')
            f.write('  "code": "ERROR_CODE",\n')
            f.write('  "timestamp": "2025-08-23T14:30:00Z"\n')
            f.write("}\n```\n")
        
        if self.console:
            self.console.print(f"[green]✅ Markdown文档已生成: {md_file}[/green]")
        else:
            print(f"✅ Markdown文档已生成: {md_file}")
    
    def _generate_html_docs(self):
        """生成HTML格式的API文档"""
        html_file = self.output_dir / "API_REFERENCE.html"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADC API 参考文档</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
        }}
        h4 {{
            color: #34495e;
            margin-top: 20px;
        }}
        .endpoint {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .method {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 4px;
            font-weight: bold;
            color: white;
            margin-right: 10px;
        }}
        .method.get {{ background: #28a745; }}
        .method.post {{ background: #007bff; }}
        .method.put {{ background: #ffc107; color: #212529; }}
        .method.delete {{ background: #dc3545; }}
        .method.websocket {{ background: #6f42c1; }}
        .path {{
            font-family: monospace;
            font-size: 1.1em;
            color: #495057;
        }}
        .tag {{
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 5px 5px 5px 0;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            color: #e83e8c;
        }}
        pre {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
        }}
        .toc {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
        }}
        .toc a {{
            text-decoration: none;
            color: #007bff;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .example {{
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .status-code {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        .status-code.2xx {{ background: #d4edda; color: #155724; }}
        .status-code.4xx {{ background: #f8d7da; color: #721c24; }}
        .status-code.5xx {{ background: #f5c6cb; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ADC API 参考文档</h1>
        
        <div class="toc">
            <h3>📋 目录</h3>
            <ul>
                <li><a href="#overview">概述</a></li>
                <li><a href="#authentication">认证</a></li>
                <li><a href="#endpoints">端点</a></li>
                <li><a href="#models">数据模型</a></li>
                <li><a href="#examples">示例</a></li>
                <li><a href="#errors">错误处理</a></li>
            </ul>
        </div>
        
        <h2 id="overview">📖 概述</h2>
        <p>ADC (Agent Development Center) 提供了完整的RESTful API，用于管理AI Agent、工作流、团队等资源。</p>
        
        <h3>基础URL</h3>
        <pre><code>http://localhost:8000</code></pre>
        
        <h3>响应格式</h3>
        <p>所有API响应都使用JSON格式，包含以下字段：</p>
        <ul>
            <li><code>status</code>: 响应状态</li>
            <li><code>data</code>: 响应数据</li>
            <li><code>message</code>: 响应消息</li>
            <li><code>timestamp</code>: 响应时间戳</li>
        </ul>
        
        <h2 id="authentication">🔐 认证</h2>
        <p>目前API使用API密钥认证，在请求头中添加：</p>
        <pre><code>X-API-Key: your_api_key_here</code></pre>
        
        <h2 id="endpoints">🌐 端点</h2>
        """
        
        # 按标签分组端点
        tags = {}
        for endpoint in self.endpoints:
            for tag in endpoint.get('tags', ['Other']):
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(endpoint)
        
        for tag, tag_endpoints in tags.items():
            html_content += f"""
        <h3>{tag}</h3>
        """
            
            for endpoint in tag_endpoints:
                html_content += f"""
        <div class="endpoint">
            <h4>
                <span class="method {endpoint['method'].lower()}">{endpoint['method']}</span>
                <span class="path">{endpoint['path']}</span>
            </h4>
            <p><strong>摘要</strong>: {endpoint['summary']}</p>
            <p><strong>描述</strong>: {endpoint['description']}</p>
            """
                
                # 添加标签
                for tag_name in endpoint.get('tags', []):
                    html_content += f'<span class="tag">{tag_name}</span>'
                
                html_content += "<br><br>"
                
                if 'parameters' in endpoint:
                    html_content += "<strong>参数:</strong><br>"
                    for param in endpoint['parameters']:
                        required = " **[必需]**" if param.get('required') else ""
                        html_content += f"- <code>{param['name']}</code> ({param['in']}) - {param['description']}{required}<br>"
                    html_content += "<br>"
                
                if 'request_body' in endpoint:
                    html_content += "<strong>请求体:</strong><br>"
                    html_content += f"<pre><code>{json.dumps(endpoint['request_body']['content']['application/json']['schema'], indent=2, ensure_ascii=False)}</code></pre><br>"
                
                if 'responses' in endpoint:
                    html_content += "<strong>响应:</strong><br>"
                    for status_code, response in endpoint['responses'].items():
                        status_class = "2xx" if status_code.startswith("2") else "4xx" if status_code.startswith("4") else "5xx"
                        html_content += f"<span class='status-code {status_class}'>{status_code}</span> - {response['description']}<br>"
                        if 'schema' in response:
                            html_content += f"<pre><code>{json.dumps(response['schema'], indent=2, ensure_ascii=False)}</code></pre><br>"
                
                html_content += """
        </div>
        """
        
        html_content += """
        <h2 id="models">📊 数据模型</h2>
        """
        
        for schema_name, schema in self.components['schemas'].items():
            html_content += f"""
        <h3>{schema_name}</h3>
        <pre><code>{json.dumps(schema, indent=2, ensure_ascii=False)}</code></pre>
        """
        
        html_content += """
        <h2 id="examples">💡 示例</h2>
        """
        
        for example_name, example in self.examples.items():
            html_content += f"""
        <div class="example">
            <h4>{example['summary']}</h4>
            <pre><code>{json.dumps(example['value'], indent=2, ensure_ascii=False)}</code></pre>
        </div>
        """
        
        html_content += """
        <h2 id="errors">❌ 错误处理</h2>
        <p>API使用标准HTTP状态码表示请求结果：</p>
        <ul>
            <li><code>200 OK</code> - 请求成功</li>
            <li><code>201 Created</code> - 资源创建成功</li>
            <li><code>400 Bad Request</code> - 请求参数错误</li>
            <li><code>401 Unauthorized</code> - 认证失败</li>
            <li><code>404 Not Found</code> - 资源不存在</li>
            <li><code>500 Internal Server Error</code> - 服务器内部错误</li>
        </ul>
        
        <p>错误响应格式：</p>
        <pre><code>{
  "error": "错误描述",
  "code": "ERROR_CODE",
  "timestamp": "2025-08-23T14:30:00Z"
}</code></pre>
        
        <hr>
        <p><em>文档生成时间: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + """</em></p>
        <p><em>ADC版本: v3.0.0</em></p>
    </div>
</body>
</html>
        """
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if self.console:
            self.console.print(f"[green]✅ HTML文档已生成: {html_file}[/green]")
        else:
            print(f"✅ HTML文档已生成: {html_file}")
    
    def _generate_openapi_spec(self):
        """生成OpenAPI规范文档"""
        openapi_file = self.output_dir / "openapi.yaml"
        
        openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "ADC API",
                "description": "Agent Development Center API",
                "version": "3.0.0",
                "contact": {
                    "name": "ADC Team",
                    "email": "support@adc.dev"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "本地开发服务器"
                }
            ],
            "paths": {},
            "components": self.components,
            "tags": [
                {"name": "System", "description": "系统管理相关API"},
                {"name": "Agents", "description": "Agent管理相关API"},
                {"name": "Workflows", "description": "工作流管理相关API"},
                {"name": "Teams", "description": "团队管理相关API"},
                {"name": "Real-time", "description": "实时数据相关API"}
            ]
        }
        
        # 构建路径
        for endpoint in self.endpoints:
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            if path not in openapi_spec['paths']:
                openapi_spec['paths'][path] = {}
            
            openapi_spec['paths'][path][method] = {
                "summary": endpoint['summary'],
                "description": endpoint['description'],
                "tags": endpoint.get('tags', ['Other']),
                "responses": endpoint.get('responses', {})
            }
            
            if 'parameters' in endpoint:
                openapi_spec['paths'][path][method]['parameters'] = endpoint['parameters']
            
            if 'request_body' in endpoint:
                openapi_spec['paths'][path][method]['request_body'] = endpoint['request_body']
        
        # 写入YAML文件
        with open(openapi_file, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        if self.console:
            self.console.print(f"[green]✅ OpenAPI规范已生成: {openapi_file}[/green]")
        else:
            print(f"✅ OpenAPI规范已生成: {openapi_file}")
    
    def _generate_postman_collection(self):
        """生成Postman集合文件"""
        postman_file = self.output_dir / "ADC_API.postman_collection.json"
        
        collection = {
            "info": {
                "name": "ADC API Collection",
                "description": "ADC API的Postman集合",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                }
            ]
        }
        
        # 按标签分组
        tags = {}
        for endpoint in self.endpoints:
            for tag in endpoint.get('tags', ['Other']):
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(endpoint)
        
        for tag, tag_endpoints in tags.items():
            tag_folder = {
                "name": tag,
                "item": []
            }
            
            for endpoint in tag_endpoints:
                item = {
                    "name": f"{endpoint['method']} {endpoint['path']}",
                    "request": {
                        "method": endpoint['method'],
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + endpoint['path'],
                            "host": ["{{base_url}}"],
                            "path": endpoint['path'].split('/')[1:]
                        }
                    }
                }
                
                if 'request_body' in endpoint:
                    item['request']['body'] = {
                        "mode": "raw",
                        "raw": json.dumps(self.examples.get(f"create_{tag.lower().rstrip('s')}", {}).get('value', {}), indent=2, ensure_ascii=False)
                    }
                
                tag_folder['item'].append(item)
            
            collection['item'].append(tag_folder)
        
        # 写入JSON文件
        with open(postman_file, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        if self.console:
            self.console.print(f"[green]✅ Postman集合已生成: {postman_file}[/green]")
        else:
            print(f"✅ Postman集合已生成: {postman_file}")


def main():
    """主函数"""
    generator = APIDocsGenerator()
    generator.generate_all_docs()


if __name__ == "__main__":
    main() 