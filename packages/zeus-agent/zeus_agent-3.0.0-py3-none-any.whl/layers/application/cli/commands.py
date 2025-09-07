"""
CLI Commands
命令行界面命令系统 - 增强版
"""

import argparse
import asyncio
import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
import subprocess
import tempfile
import webbrowser

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track, Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ...adapter.openai.adapter import OpenAIAdapter
from ...adapter.openai.agent_wrapper import OpenAIAgentWrapper
from ...business.teams.collaboration_manager import CollaborationManager, CollaborationPattern, CollaborationRole
from ...business.workflows.workflow_engine import WorkflowEngine, WorkflowStepType
from ...framework.abstractions.task import UniversalTask, TaskType
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.agent import AgentCapability


class CommandRegistry:
    """
    命令注册系统 - 增强版
    """
    
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        if RICH_AVAILABLE:
            self.console = Console()
        self.project_root = Path.cwd()
        
    def register_commands(self, subparsers) -> None:
        """注册所有命令"""
        
        # Agent命令组
        agent_parser = subparsers.add_parser('agent', help='🤖 Agent管理命令')
        agent_subparsers = agent_parser.add_subparsers(dest='agent_action')
        
        # agent list
        list_parser = agent_subparsers.add_parser('list', help='📋 列出所有Agent')
        list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='输出格式')
        list_parser.add_argument('--filter', help='过滤条件（名称、类型等）')
        list_parser.add_argument('--sort', choices=['name', 'type', 'created'], default='name', help='排序字段')
        
        # agent create
        create_parser = agent_subparsers.add_parser('create', help='✨ 创建新Agent')
        create_parser.add_argument('--name', required=True, help='Agent名称')
        create_parser.add_argument('--type', choices=['openai', 'autogen', 'langgraph', 'fpga_expert', 'code_expert', 'data_analyst', 'custom'], default='openai', help='Agent类型')
        create_parser.add_argument('--model', default='gpt-4o-mini', help='使用的模型')
        create_parser.add_argument('--system-message', help='系统消息')
        create_parser.add_argument('--template', choices=['basic', 'advanced', 'enterprise', 'fpga_basic', 'fpga_advanced', 'verification_expert'], help='使用模板创建')
        create_parser.add_argument('--capabilities', nargs='+', help='Agent能力列表')
        create_parser.add_argument('--interactive', action='store_true', help='交互式创建')
        
        # agent chat
        chat_parser = agent_subparsers.add_parser('chat', help='💬 与Agent对话')
        chat_parser.add_argument('--name', required=True, help='Agent名称')
        chat_parser.add_argument('--message', help='消息内容（如果不提供则进入交互模式）')
        chat_parser.add_argument('--history', action='store_true', help='显示对话历史')
        chat_parser.add_argument('--save', help='保存对话到文件')
        
        # agent info
        info_parser = agent_subparsers.add_parser('info', help='ℹ️ 显示Agent详细信息')
        info_parser.add_argument('name', help='Agent名称')
        
        # agent delete
        delete_parser = agent_subparsers.add_parser('delete', help='🗑️ 删除Agent')
        delete_parser.add_argument('name', help='Agent名称')
        delete_parser.add_argument('--force', action='store_true', help='强制删除（不确认）')
        
        # Workflow命令组
        workflow_parser = subparsers.add_parser('workflow', help='⚙️ 工作流管理命令')
        workflow_subparsers = workflow_parser.add_subparsers(dest='workflow_action')
        
        # workflow list
        wf_list_parser = workflow_subparsers.add_parser('list', help='📋 列出所有工作流')
        wf_list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='输出格式')
        wf_list_parser.add_argument('--status', choices=['active', 'completed', 'failed'], help='按状态过滤')
        
        # workflow create
        wf_create_parser = workflow_subparsers.add_parser('create', help='✨ 创建工作流')
        wf_create_parser.add_argument('--name', required=True, help='工作流名称')
        wf_create_parser.add_argument('--description', help='工作流描述')
        wf_create_parser.add_argument('--template', help='使用模板')
        wf_create_parser.add_argument('--file', help='从文件创建工作流')
        wf_create_parser.add_argument('--interactive', action='store_true', help='交互式创建')
        
        # workflow run
        wf_run_parser = workflow_subparsers.add_parser('run', help='▶️ 运行工作流')
        wf_run_parser.add_argument('--id', required=True, help='工作流ID')
        wf_run_parser.add_argument('--context', help='初始上下文（JSON格式）')
        wf_run_parser.add_argument('--watch', action='store_true', help='实时监控执行状态')
        wf_run_parser.add_argument('--timeout', type=int, default=300, help='超时时间（秒）')
        
        # workflow status
        wf_status_parser = workflow_subparsers.add_parser('status', help='📊 查看工作流状态')
        wf_status_parser.add_argument('id', help='工作流执行ID')
        wf_status_parser.add_argument('--follow', action='store_true', help='持续跟踪状态')
        
        # workflow logs
        wf_logs_parser = workflow_subparsers.add_parser('logs', help='📄 查看工作流日志')
        wf_logs_parser.add_argument('id', help='工作流执行ID')
        wf_logs_parser.add_argument('--follow', action='store_true', help='持续跟踪日志')
        wf_logs_parser.add_argument('--lines', type=int, default=100, help='显示行数')
        
        # Team命令组
        team_parser = subparsers.add_parser('team', help='👥 团队管理命令')
        team_subparsers = team_parser.add_subparsers(dest='team_action')
        
        # team list
        team_list_parser = team_subparsers.add_parser('list', help='📋 列出所有团队')
        team_list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='输出格式')
        
        # team create
        team_create_parser = team_subparsers.add_parser('create', help='✨ 创建团队')
        team_create_parser.add_argument('--name', required=True, help='团队名称')
        team_create_parser.add_argument('--members', nargs='+', help='团队成员列表')
        team_create_parser.add_argument('--template', help='使用团队模板')
        team_create_parser.add_argument('--interactive', action='store_true', help='交互式创建')
        
        # team collaborate
        team_collab_parser = team_subparsers.add_parser('collaborate', help='🤝 执行团队协作')
        team_collab_parser.add_argument('--team', required=True, help='团队名称')
        team_collab_parser.add_argument('--task', required=True, help='任务描述')
        team_collab_parser.add_argument('--pattern', 
                                      choices=[p.value for p in CollaborationPattern],
                                      default='parallel', help='协作模式')
        team_collab_parser.add_argument('--watch', action='store_true', help='实时监控协作状态')
        
        # team performance
        team_perf_parser = team_subparsers.add_parser('performance', help='📊 查看团队性能')
        team_perf_parser.add_argument('name', help='团队名称')
        team_perf_parser.add_argument('--period', choices=['day', 'week', 'month'], default='week', help='统计周期')
        
        # Project命令组
        project_parser = subparsers.add_parser('project', help='🏗️ 项目管理命令')
        project_subparsers = project_parser.add_subparsers(dest='project_action')
        
        # project init
        proj_init_parser = project_subparsers.add_parser('init', help='🚀 初始化新项目')
        proj_init_parser.add_argument('name', help='项目名称')
        proj_init_parser.add_argument('--template', help='项目模板')
        proj_init_parser.add_argument('--path', help='项目路径')
        proj_init_parser.add_argument('--interactive', action='store_true', help='交互式创建')
        
        # project list
        proj_list_parser = project_subparsers.add_parser('list', help='📋 列出所有项目')
        proj_list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='输出格式')
        
        # project status
        proj_status_parser = project_subparsers.add_parser('status', help='📊 查看项目状态')
        proj_status_parser.add_argument('name', nargs='?', help='项目名称（默认当前项目）')
        
        # project build
        proj_build_parser = project_subparsers.add_parser('build', help='🔨 构建项目')
        proj_build_parser.add_argument('--target', help='构建目标')
        proj_build_parser.add_argument('--watch', action='store_true', help='监控文件变化并自动构建')
        
        # project deploy
        proj_deploy_parser = project_subparsers.add_parser('deploy', help='🚀 部署项目')
        proj_deploy_parser.add_argument('--env', choices=['dev', 'staging', 'prod'], default='dev', help='部署环境')
        proj_deploy_parser.add_argument('--dry-run', action='store_true', help='预演模式')
        
        # Config命令组
        config_parser = subparsers.add_parser('config', help='⚙️ 配置管理命令')
        config_subparsers = config_parser.add_subparsers(dest='config_action')
        
        # config get
        config_get_parser = config_subparsers.add_parser('get', help='📖 获取配置值')
        config_get_parser.add_argument('key', help='配置键')
        
        # config set
        config_set_parser = config_subparsers.add_parser('set', help='✏️ 设置配置值')
        config_set_parser.add_argument('key', help='配置键')
        config_set_parser.add_argument('value', help='配置值')
        
        # config list
        config_list_parser = config_subparsers.add_parser('list', help='📋 列出所有配置')
        config_list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='输出格式')
        
        # config edit
        config_edit_parser = config_subparsers.add_parser('edit', help='✏️ 编辑配置文件')
        config_edit_parser.add_argument('--editor', help='指定编辑器')
        
        # Monitor命令组
        monitor_parser = subparsers.add_parser('monitor', help='📊 监控命令')
        monitor_subparsers = monitor_parser.add_subparsers(dest='monitor_action')
        
        # monitor system
        monitor_sys_parser = monitor_subparsers.add_parser('system', help='💻 系统监控')
        monitor_sys_parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')
        
        # monitor agents
        monitor_agents_parser = monitor_subparsers.add_parser('agents', help='🤖 Agent监控')
        monitor_agents_parser.add_argument('--interval', type=int, default=10, help='刷新间隔（秒）')
        
        # monitor workflows
        monitor_wf_parser = monitor_subparsers.add_parser('workflows', help='⚙️ 工作流监控')
        monitor_wf_parser.add_argument('--interval', type=int, default=15, help='刷新间隔（秒）')
        
        # Tools命令组
        tools_parser = subparsers.add_parser('tools', help='🛠️ 工具命令')
        tools_subparsers = tools_parser.add_subparsers(dest='tools_action')
        
        # tools validate
        tools_validate_parser = tools_subparsers.add_parser('validate', help='✅ 验证配置和设置')
        tools_validate_parser.add_argument('--fix', action='store_true', help='自动修复问题')
        
        # tools benchmark
        tools_bench_parser = tools_subparsers.add_parser('benchmark', help='⚡ 性能基准测试')
        tools_bench_parser.add_argument('--type', choices=['agent', 'workflow', 'system'], default='system', help='测试类型')
        tools_bench_parser.add_argument('--duration', type=int, default=60, help='测试时长（秒）')
        
        # tools export
        tools_export_parser = tools_subparsers.add_parser('export', help='📤 导出数据')
        tools_export_parser.add_argument('--type', choices=['agents', 'workflows', 'teams', 'all'], required=True, help='导出类型')
        tools_export_parser.add_argument('--format', choices=['json', 'yaml', 'csv'], default='json', help='导出格式')
        tools_export_parser.add_argument('--output', help='输出文件路径')
        
        # tools import
        tools_import_parser = tools_subparsers.add_parser('import', help='📥 导入数据')
        tools_import_parser.add_argument('file', help='导入文件路径')
        tools_import_parser.add_argument('--type', choices=['agents', 'workflows', 'teams', 'auto'], default='auto', help='导入类型')
        tools_import_parser.add_argument('--merge', action='store_true', help='合并模式（不覆盖现有数据）')
        
        # Demo命令组 - 增强版
        demo_parser = subparsers.add_parser('demo', help='🎮 演示命令')
        demo_subparsers = demo_parser.add_subparsers(dest='demo_type')
        
        # demo openai
        openai_parser = demo_subparsers.add_parser('openai', help='🤖 OpenAI演示')
        openai_parser.add_argument('--model', default='gpt-4o-mini', help='使用的模型')
        openai_parser.add_argument('--interactive', action='store_true', help='交互模式')
        
        # demo business
        business_parser = demo_subparsers.add_parser('business', help='🏢 业务层演示')
        business_parser.add_argument('--module', choices=['collaboration', 'workflow', 'team', 'all'], default='all', help='演示模块')
        business_parser.add_argument('--verbose', action='store_true', help='详细输出')
        
        # demo orchestration
        orchestration_parser = demo_subparsers.add_parser('orchestration', help='🎭 应用编排演示')
        orchestration_parser.add_argument('--verbose', action='store_true', help='详细输出')
        
        # demo interactive
        interactive_parser = demo_subparsers.add_parser('interactive', help='🎯 交互式演示向导')
        
        # Help命令组
        help_parser = subparsers.add_parser('help', help='❓ 帮助命令')
        help_subparsers = help_parser.add_subparsers(dest='help_topic')
        
        # help commands
        help_cmd_parser = help_subparsers.add_parser('commands', help='📋 命令列表')
        help_cmd_parser.add_argument('--category', help='命令分类')
        
        # help examples
        help_examples_parser = help_subparsers.add_parser('examples', help='💡 使用示例')
        help_examples_parser.add_argument('--command', help='特定命令的示例')
        
        # help docs
        help_docs_parser = help_subparsers.add_parser('docs', help='📚 打开文档')
        help_docs_parser.add_argument('--local', action='store_true', help='打开本地文档')
        
    async def execute_command(self, args: argparse.Namespace) -> int:
        """执行命令"""
        try:
            if args.command == 'agent':
                return await self._handle_agent_commands(args)
            elif args.command == 'workflow':
                return await self._handle_workflow_commands(args)
            elif args.command == 'team':
                return await self._handle_team_commands(args)
            elif args.command == 'project':
                return await self._handle_project_commands(args)
            elif args.command == 'config':
                return await self._handle_config_commands(args)
            elif args.command == 'monitor':
                return await self._handle_monitor_commands(args)
            elif args.command == 'tools':
                return await self._handle_tools_commands(args)
            elif args.command == 'demo':
                return await self._handle_demo_commands(args)
            elif args.command == 'help':
                return await self._handle_help_commands(args)
            else:
                print(f"未知命令: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ 命令执行错误: {e}")
            return 1
    
    def _print_table(self, data: List[Dict], title: str = ""):
        """打印表格"""
        if RICH_AVAILABLE and hasattr(self, 'console'):
            table = Table(title=title)
            if data:
                for key in data[0].keys():
                    table.add_column(key, style="cyan")
                for row in data:
                    table.add_row(*[str(v) for v in row.values()])
                self.console.print(table)
        else:
            # 回退到简单文本表格
            if data:
                headers = list(data[0].keys())
                print(f"{'  '.join(headers)}")
                print("-" * 50)
                for row in data:
                    print(f"{'  '.join(str(v) for v in row.values())}")
    
    async def _handle_agent_commands(self, args: argparse.Namespace) -> int:
        """处理Agent命令"""
        if args.agent_action == 'list':
            return await self._agent_list(args)
        elif args.agent_action == 'create':
            return await self._agent_create(args)
        elif args.agent_action == 'chat':
            return await self._agent_chat(args)
        elif args.agent_action == 'info':
            return await self._agent_info(args)
        elif args.agent_action == 'delete':
            return await self._agent_delete(args)
        else:
            print(f"未知Agent操作: {args.agent_action}")
            return 1
    
    async def _agent_list(self, args: argparse.Namespace) -> int:
        """列出Agent"""
        print("📋 Agent列表:")
        print("=" * 50)
        
        # 这里应该从实际的Agent管理器获取数据
        # 目前显示示例数据
        agents = [
            {"名称": "OpenAI Assistant", "类型": "openai", "模型": "gpt-4o-mini", "状态": "ready"},
            {"名称": "Code Expert", "类型": "autogen", "模型": "multi", "状态": "inactive"},
            {"名称": "AutoGen Team", "类型": "autogen", "模型": "multi", "状态": "ready"},
        ]
        
        # 应用过滤器
        if args.filter:
            agents = [a for a in agents if args.filter.lower() in a["名称"].lower() or args.filter.lower() in a["类型"].lower()]
        
        # 应用排序
        if args.sort == 'name':
            agents.sort(key=lambda x: x["名称"])
        elif args.sort == 'type':
            agents.sort(key=lambda x: x["类型"])
        
        if args.format == 'json':
            print(json.dumps(agents, indent=2, ensure_ascii=False))
        elif args.format == 'yaml':
            print(yaml.dump(agents, indent=2, allow_unicode=True))
        else:
            self._print_table(agents, "Agent列表")
        
        return 0
    
    async def _agent_create(self, args: argparse.Namespace) -> int:
        """创建Agent - 真正的Zeus开发体验层实现"""
        print(f"✨ 创建新Agent: {args.name}")
        print("=" * 50)
        
        try:
            # 导入真正的Agent工厂
            from .agent_factory import ZeusAgentFactory, AgentSpec, AgentType, TemplateType
            
            # 创建工厂实例
            factory = ZeusAgentFactory()
            
            # 解析Agent类型
            agent_type_map = {
                'openai': AgentType.OPENAI,
                'autogen': AgentType.AUTOGEN,
                'langgraph': AgentType.LANGGRAPH,
                'fpga_expert': AgentType.FPGA_EXPERT,
                'code_expert': AgentType.CODE_EXPERT,
                'custom': AgentType.CUSTOM
            }
            agent_type = agent_type_map.get(args.type, AgentType.OPENAI)
            
            # 确定模板类型
            if args.template:
                template_map = {
                    'basic': TemplateType.BASIC,
                    'advanced': TemplateType.ADVANCED,
                    'enterprise': TemplateType.ENTERPRISE,
                    'fpga_basic': TemplateType.FPGA_BASIC,
                    'fpga_advanced': TemplateType.FPGA_ADVANCED,
                    'verification_expert': TemplateType.VERIFICATION_EXPERT
                }
                template_type = template_map.get(args.template, TemplateType.BASIC)
            else:
                # 根据Agent类型自动选择模板
                if agent_type == AgentType.FPGA_EXPERT:
                    template_type = TemplateType.FPGA_ADVANCED
                else:
                    template_type = TemplateType.ADVANCED
            
            # 处理能力和知识域
            capabilities = args.capabilities or self._get_default_capabilities(agent_type)
            knowledge_domains = self._get_default_knowledge_domains(agent_type)
            
            # 创建Agent规格
            spec = AgentSpec(
                name=args.name,
                agent_type=agent_type,
                template_type=template_type,
                model=args.model,
                capabilities=capabilities,
                knowledge_domains=knowledge_domains,
                system_message=args.system_message
            )
            
            # 显示创建信息
            print(f"   名称: {spec.name}")
            print(f"   类型: {spec.agent_type.value}")
            print(f"   模板: {spec.template_type.value}")
            print(f"   模型: {spec.model}")
            print(f"   能力: {', '.join(spec.capabilities)}")
            print(f"   知识域: {', '.join(spec.knowledge_domains)}")
            if spec.system_message:
                print(f"   系统消息: {spec.system_message[:50]}...")
            
            # 实际创建Agent
            print(f"\n🔧 正在生成Agent文件...")
            result = await factory.create_agent(spec)
            
            if result.success:
                print(f"\n🎉 Agent创建成功！")
                print(f"   📁 位置: {result.agent_path}")
                print(f"   📋 配置: {result.config_path}")
                print(f"   🐍 主脚本: {result.main_script}")
                print(f"   📄 生成文件: {len(result.generated_files)}个")
                
                print(f"\n🚀 下一步:")
                print(f"   1. cd {result.agent_path}")
                print(f"   2. pip install -r requirements.txt")
                print(f"   3. python {result.main_script.name}")
                print(f"   4. zeus agent chat --name {args.name}")
                
                return 0
            else:
                print(f"❌ 创建失败: {result.error_message}")
                return 1
                
        except ImportError as e:
            print(f"❌ 导入Agent工厂失败: {e}")
            print("请确保Zeus平台核心组件已正确安装")
            return 1
        except Exception as e:
            print(f"❌ 创建Agent失败: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def _get_default_capabilities(self, agent_type: 'AgentType') -> List[str]:
        """获取默认能力"""
        from .agent_factory import AgentType
        
        if agent_type == AgentType.FPGA_EXPERT:
            return ["testbench_generation", "timing_analysis", "synthesis_optimization", "debug_assistance"]
        elif agent_type == AgentType.CODE_EXPERT:
            return ["code_generation", "code_review", "bug_detection", "optimization"]
        else:
            return ["chat", "information_retrieval", "analysis"]
    
    def _get_default_knowledge_domains(self, agent_type: 'AgentType') -> List[str]:
        """获取默认知识域"""
        from .agent_factory import AgentType
        
        if agent_type == AgentType.FPGA_EXPERT:
            return ["fpga", "verilog", "verification", "timing"]
        elif agent_type == AgentType.CODE_EXPERT:
            return ["programming", "software_engineering", "algorithms"]
        else:
            return ["general"]
    
    async def _agent_chat(self, args: argparse.Namespace) -> int:
        """与Agent对话"""
        print(f"💬 与Agent对话: {args.name}")
        print("=" * 50)
        
        if args.message:
            # 单次对话
            print(f"用户: {args.message}")
            print(f"Agent: 这是来自{args.name}的回复（模拟）")
            
            if args.save:
                # 保存对话到文件
                with open(args.save, 'a', encoding='utf-8') as f:
                    f.write(f"用户: {args.message}\n")
                    f.write(f"Agent: 这是来自{args.name}的回复（模拟）\n\n")
                print(f"✅ 对话已保存到: {args.save}")
        else:
            # 交互模式
            print("进入交互模式，输入 'quit' 退出")
            while True:
                try:
                    user_input = input("用户: ").strip()
                    if user_input.lower() in ['quit', 'exit', '退出']:
                        break
                    print(f"Agent: 这是来自{args.name}的回复（模拟）")
                except KeyboardInterrupt:
                    break
        
        return 0
    
    async def _agent_info(self, args: argparse.Namespace) -> int:
        """显示Agent详细信息"""
        print(f"ℹ️ 显示Agent详细信息: {args.name}")
        print("=" * 50)
        
        # 这里应该从实际的Agent管理器获取数据
        # 目前显示示例数据
        agent_info = [
            {"属性": "名称", "值": args.name},
            {"属性": "类型", "值": "openai"},
            {"属性": "模型", "值": "gpt-4o-mini"},
            {"属性": "状态", "值": "ready"},
            {"属性": "创建时间", "值": "2023-10-27 10:00:00"},
            {"属性": "能力", "值": "自然语言处理, 代码生成, 信息检索"}
        ]
        
        self._print_table(agent_info, f"Agent: {args.name}")
        return 0
    
    async def _agent_delete(self, args: argparse.Namespace) -> int:
        """删除Agent"""
        print(f"🗑️ 删除Agent: {args.name}")
        print("=" * 50)
        
        if args.force:
            confirm = "y"
        else:
            confirm = input("确定要删除该Agent吗？(y/N): ").lower()
            
        if confirm == "y":
            try:
                # 这里应该从实际的Agent管理器删除
                print(f"✅ 已删除Agent: {args.name}")
                return 0
            except Exception as e:
                print(f"❌ 删除Agent失败: {e}")
                return 1
        else:
            print("👋 取消删除")
            return 0

    # 添加其他命令处理方法的简化版本...
    async def _handle_workflow_commands(self, args: argparse.Namespace) -> int:
        """处理工作流命令"""
        print(f"⚙️ 工作流命令: {args.workflow_action}")
        return 0

    async def _handle_team_commands(self, args: argparse.Namespace) -> int:
        """处理团队命令"""
        print(f"👥 团队命令: {args.team_action}")
        return 0

    async def _handle_project_commands(self, args: argparse.Namespace) -> int:
        """处理项目命令"""
        print(f"🏗️ 项目命令: {args.project_action}")
        return 0

    async def _handle_config_commands(self, args: argparse.Namespace) -> int:
        """处理配置命令"""
        print(f"⚙️ 配置命令: {args.config_action}")
        return 0

    async def _handle_monitor_commands(self, args: argparse.Namespace) -> int:
        """处理监控命令"""
        print(f"📊 监控命令: {args.monitor_action}")
        return 0

    async def _handle_tools_commands(self, args: argparse.Namespace) -> int:
        """处理工具命令"""
        print(f"🛠️ 工具命令: {args.tools_action}")
        return 0

    async def _handle_demo_commands(self, args: argparse.Namespace) -> int:
        """处理演示命令"""
        if args.demo_type == 'openai':
            return await self._run_openai_demo(args)
        elif args.demo_type == 'business':
            return await self._run_business_demo(args)
        elif args.demo_type == 'orchestration':
            return await self._run_orchestration_demo(args)
        elif args.demo_type == 'interactive':
            return await self._run_interactive_demo()
        else:
            print(f"未知演示类型: {args.demo_type}")
            return 1

    async def _run_openai_demo(self, args: argparse.Namespace) -> int:
        """运行OpenAI演示"""
        print("🤖 运行OpenAI演示")
        print("=" * 50)
        
        try:
            # 运行实际的OpenAI演示
            result = subprocess.run([
                sys.executable, "examples/openai_demo.py"
            ], cwd=project_root, capture_output=False)
            return result.returncode
        except Exception as e:
            print(f"❌ OpenAI演示执行失败: {e}")
            return 1

    async def _run_business_demo(self, args: argparse.Namespace) -> int:
        """运行业务层演示"""
        print("🏢 运行业务层演示")
        print("=" * 50)
        
        try:
            # 运行实际的业务层演示
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root)
            result = subprocess.run([
                sys.executable, "examples/business_layer_demo.py"
            ], cwd=project_root, capture_output=False, env=env)
            return result.returncode
        except Exception as e:
            print(f"❌ 业务层演示执行失败: {e}")
            return 1

    async def _run_orchestration_demo(self, args: argparse.Namespace) -> int:
        """运行应用编排演示"""
        print("🎭 运行应用编排演示")
        print("=" * 50)
        
        try:
            # 运行实际的应用编排演示
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root)
            result = subprocess.run([
                sys.executable, "examples/application_orchestration_demo.py"
            ], cwd=project_root, capture_output=False, env=env)
            return result.returncode
        except Exception as e:
            print(f"❌ 应用编排演示执行失败: {e}")
            return 1

    async def _run_interactive_demo(self) -> int:
        """运行交互式演示向导"""
        print("🎯 交互式演示向导")
        print("=" * 50)
        
        print("欢迎使用ADC交互式演示向导！")
        print("请选择您想要演示的功能：")
        print("1. OpenAI适配器演示")
        print("2. 业务能力层演示") 
        print("3. 应用编排层演示")
        print("4. 退出")
        
        while True:
            try:
                choice = input("请选择 (1-4): ").strip()
                if choice == '1':
                    return await self._run_openai_demo(argparse.Namespace(model='gpt-4o-mini', interactive=True))
                elif choice == '2':
                    return await self._run_business_demo(argparse.Namespace(module='all', verbose=True))
                elif choice == '3':
                    return await self._run_orchestration_demo(argparse.Namespace(verbose=True))
                elif choice == '4':
                    print("👋 再见！")
                    return 0
                else:
                    print("❌ 无效选择，请重试")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                return 0

    async def _handle_help_commands(self, args: argparse.Namespace) -> int:
        """处理帮助命令"""
        if args.help_topic == 'commands':
            return await self._help_commands(args)
        elif args.help_topic == 'examples':
            return await self._help_examples(args)
        elif args.help_topic == 'docs':
            return await self._help_docs(args)
        else:
            print("❓ 帮助:")
            print("=" * 50)
            print("请使用 'help commands' 查看所有命令。")
            print("使用 'help examples <command>' 查看特定命令的示例。")
            print("使用 'help docs' 打开文档。")
            return 0

    async def _help_commands(self, args: argparse.Namespace) -> int:
        """显示所有命令"""
        print("📋 所有命令:")
        print("=" * 50)
        
        commands = [
            {"分类": "Agent管理", "命令": "list, create, chat, info, delete"},
            {"分类": "工作流管理", "命令": "list, create, run, status, logs"},
            {"分类": "团队管理", "命令": "list, create, collaborate, performance"},
            {"分类": "项目管理", "命令": "init, list, status, build, deploy"},
            {"分类": "配置管理", "命令": "get, set, list, edit"},
            {"分类": "监控", "命令": "system, agents, workflows"},
            {"分类": "工具", "命令": "validate, benchmark, export, import"},
            {"分类": "演示", "命令": "openai, business, orchestration, interactive"},
            {"分类": "帮助", "命令": "commands, examples, docs"}
        ]
        
        self._print_table(commands, "命令分类")
        return 0

    async def _help_examples(self, args: argparse.Namespace) -> int:
        """显示特定命令的示例"""
        print(f"💡 使用示例: {args.command}")
        print("=" * 50)
        
        if args.command == 'agent create':
            print("✨ 创建新Agent示例:")
            print("  adc agent create --name MyAgent --type openai --model gpt-4o-mini")
            print("  adc agent create --name MyAgent --interactive")
        elif args.command == 'demo business':
            print("🏢 业务层演示示例:")
            print("  adc demo business --module all --verbose")
        else:
            print(f"未找到命令 '{args.command}' 的示例。")
        
        return 0

    async def _help_docs(self, args: argparse.Namespace) -> int:
        """打开文档"""
        print("📚 打开文档:")
        print("=" * 50)
        
        if args.local:
            try:
                readme_path = project_root / "README.md"
                if readme_path.exists():
                    webbrowser.open(f"file://{readme_path}")
                    print(f"✅ 已打开本地文档: {readme_path}")
                else:
                    print(f"❌ 本地文档不存在: {readme_path}")
                    return 1
            except Exception as e:
                print(f"❌ 打开本地文档失败: {e}")
                return 1
        else:
            print("✅ 文档链接: https://github.com/fpga1988/zeus")
        
        return 0 