"""
Enhanced Interactive Shell
增强版交互式Shell - 提供更好的开发体验
"""

import asyncio
import os
import sys
import readline
import shlex
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .commands import CommandRegistry
from .enhanced_commands import EnhancedCommandRegistry


class ADCCompleter:
    """ADC命令自动补全器"""
    
    def __init__(self):
        self.commands = [
            # 基础命令
            'help', 'exit', 'quit', 'clear', 'version', 'status',
            
            # 系统命令
            'system status', 'system health', 'system metrics',
            
            # 开发工具
            'dev debug', 'dev test', 'dev profile',
            
            # 数据管理
            'data backup', 'data restore', 'data export',
            
            # 集成
            'integration list', 'integration test', 'integration configure',
            
            # 安全
            'security audit', 'security scan',
            
            # 监控
            'monitor start', 'monitor stop', 'monitor logs',
            
            # API
            'api start', 'api docs', 'api test',
            
            # 插件
            'plugin list', 'plugin install', 'plugin enable', 'plugin disable',
            
            # 学习
            'learn tutorial', 'learn examples', 'learn docs',
            
            # 社区
            'community share', 'community discover',
            
            # AI助手
            'ai chat', 'ai analyze', 'ai optimize',
            
            # 原有命令
            'agent list', 'agent create', 'agent chat', 'agent info', 'agent delete',
            'workflow list', 'workflow create', 'workflow run', 'workflow status', 'workflow logs',
            'team list', 'team create', 'team collaborate', 'team performance',
            'project init', 'project list', 'project status', 'project build', 'project deploy',
            'config get', 'config set', 'config list', 'config reset',
            'demo business', 'demo cognitive', 'demo workflow', 'demo orchestration'
        ]
    
    def complete(self, text, state):
        """补全逻辑"""
        if state == 0:
            # 这是第一次调用，找到所有匹配项
            if text:
                self.matches = [s for s in self.commands if s.startswith(text)]
            else:
                self.matches = self.commands[:]
        
        try:
            return self.matches[state]
        except IndexError:
            return None


class EnhancedADCShell:
    """增强版ADC交互式Shell"""
    
    def __init__(self):
        self.running = True
        self.command_registry = CommandRegistry()
        self.enhanced_registry = EnhancedCommandRegistry()
        self.history_file = Path.home() / '.adc_history'
        self.session_start = datetime.now()
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # 设置readline
        self._setup_readline()
        
        # 会话信息
        self.session_info = {
            'start_time': self.session_start,
            'commands_executed': 0,
            'current_directory': os.getcwd(),
            'environment': os.environ.get('ENV', 'development')
        }
    
    def _setup_readline(self):
        """设置readline功能"""
        try:
            # 设置历史文件
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
            
            # 设置补全器
            self.completer = ADCCompleter()
            readline.set_completer(self.completer.complete)
            
            # 启用tab补全
            readline.parse_and_bind('tab: complete')
            
            # 设置历史文件大小
            readline.set_history_length(1000)
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️ readline设置失败: {e}[/yellow]")
            else:
                print(f"⚠️ readline设置失败: {e}")
    
    def _save_history(self):
        """保存命令历史"""
        try:
            readline.write_history_file(str(self.history_file))
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️ 历史保存失败: {e}[/yellow]")
            else:
                print(f"⚠️ 历史保存失败: {e}")
    
    def _show_welcome(self):
        """显示欢迎信息"""
        if self.console:
            welcome_text = f"""
🌟 [bold cyan]Agent Development Center[/bold cyan] - 增强版交互式Shell
🚀 [bold green]版本[/bold green]: v3.0 | [bold blue]环境[/bold blue]: {self.session_info['environment']}
📅 [bold yellow]启动时间[/bold yellow]: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
💡 [bold magenta]提示[/bold magenta]: 输入 'help' 查看所有可用命令
🔧 [bold cyan]提示[/bold cyan]: 使用 Tab 键进行命令补全
            """
            self.console.print(Panel(welcome_text, title="🎉 欢迎使用ADC", border_style="green"))
        else:
            print("🌟 Agent Development Center - 增强版交互式Shell")
            print("🚀 版本: v3.0 | 环境:", self.session_info['environment'])
            print("📅 启动时间:", self.session_start.strftime('%Y-%m-%d %H:%M:%S'))
            print("💡 提示: 输入 'help' 查看所有可用命令")
            print("🔧 提示: 使用 Tab 键进行命令补全")
            print("=" * 60)
    
    def _show_help(self):
        """显示帮助信息"""
        if self.console:
            help_table = Table(title="📚 ADC命令帮助", show_header=True, header_style="bold magenta")
            help_table.add_column("命令组", style="cyan", width=20)
            help_table.add_column("命令", style="green", width=30)
            help_table.add_column("描述", style="white", width=40)
            
            help_table.add_row("🖥️ 系统", "system status", "显示系统状态")
            help_table.add_row("🖥️ 系统", "system health", "系统健康检查")
            help_table.add_row("🖥️ 系统", "system metrics", "系统性能指标")
            help_table.add_row("🛠️ 开发", "dev debug", "启动调试模式")
            help_table.add_row("🛠️ 开发", "dev test", "运行测试套件")
            help_table.add_row("🛠️ 开发", "dev profile", "性能分析")
            help_table.add_row("💾 数据", "data backup", "数据备份")
            help_table.add_row("💾 数据", "data restore", "数据恢复")
            help_table.add_row("💾 数据", "data export", "数据导出")
            help_table.add_row("🔗 集成", "integration list", "列出集成")
            help_table.add_row("🔗 集成", "integration test", "测试集成")
            help_table.add_row("🔒 安全", "security audit", "安全审计")
            help_table.add_row("🔒 安全", "security scan", "安全扫描")
            help_table.add_row("📊 监控", "monitor start", "启动监控")
            help_table.add_row("📊 监控", "monitor stop", "停止监控")
            help_table.add_row("🌐 API", "api start", "启动API服务器")
            help_table.add_row("🌐 API", "api docs", "生成API文档")
            help_table.add_row("🔌 插件", "plugin list", "列出插件")
            help_table.add_row("🔌 插件", "plugin install", "安装插件")
            help_table.add_row("📚 学习", "learn tutorial", "交互式教程")
            help_table.add_row("📚 学习", "learn examples", "查看示例")
            help_table.add_row("🌍 社区", "community share", "分享作品")
            help_table.add_row("🌍 社区", "community discover", "发现作品")
            help_table.add_row("🤖 AI", "ai chat", "AI助手对话")
            help_table.add_row("🤖 AI", "ai analyze", "AI分析")
            help_table.add_row("🤖 AI", "ai optimize", "AI优化建议")
            
            self.console.print(help_table)
            
            # 显示原有命令
            legacy_table = Table(title="🔧 原有命令", show_header=True, header_style="bold yellow")
            legacy_table.add_column("命令组", style="cyan", width=20)
            legacy_table.add_column("命令", style="green", width=30)
            legacy_table.add_column("描述", style="white", width=40)
            
            legacy_table.add_row("🤖 Agent", "agent list", "列出所有Agent")
            legacy_table.add_row("🤖 Agent", "agent create", "创建新Agent")
            legacy_table.add_row("🤖 Agent", "agent chat", "与Agent对话")
            legacy_table.add_row("⚙️ 工作流", "workflow list", "列出所有工作流")
            legacy_table.add_row("⚙️ 工作流", "workflow create", "创建工作流")
            legacy_table.add_row("⚙️ 工作流", "workflow run", "运行工作流")
            legacy_table.add_row("👥 团队", "team list", "列出所有团队")
            legacy_table.add_row("👥 团队", "team create", "创建团队")
            legacy_table.add_row("👥 团队", "team collaborate", "执行团队协作")
            legacy_table.add_row("🏗️ 项目", "project init", "初始化新项目")
            legacy_table.add_row("🏗️ 项目", "project list", "列出所有项目")
            legacy_table.add_row("🏗️ 项目", "project status", "查看项目状态")
            legacy_table.add_row("⚙️ 配置", "config get", "获取配置值")
            legacy_table.add_row("⚙️ 配置", "config set", "设置配置值")
            legacy_table.add_row("🎭 演示", "demo business", "业务能力层演示")
            legacy_table.add_row("🎭 演示", "demo cognitive", "认知架构层演示")
            legacy_table.add_row("🎭 演示", "demo workflow", "工作流引擎演示")
            legacy_table.add_row("🎭 演示", "demo orchestration", "应用编排层演示")
            
            self.console.print(legacy_table)
            
        else:
            print("📚 ADC命令帮助")
            print("🖥️ 系统命令:")
            print("  system status    - 显示系统状态")
            print("  system health    - 系统健康检查")
            print("  system metrics   - 系统性能指标")
            print("🛠️ 开发工具:")
            print("  dev debug        - 启动调试模式")
            print("  dev test         - 运行测试套件")
            print("  dev profile      - 性能分析")
            print("💾 数据管理:")
            print("  data backup      - 数据备份")
            print("  data restore     - 数据恢复")
            print("  data export      - 数据导出")
            print("🔗 集成管理:")
            print("  integration list - 列出集成")
            print("  integration test - 测试集成")
            print("🔒 安全管理:")
            print("  security audit   - 安全审计")
            print("  security scan    - 安全扫描")
            print("📊 监控管理:")
            print("  monitor start    - 启动监控")
            print("  monitor stop     - 停止监控")
            print("🌐 API管理:")
            print("  api start        - 启动API服务器")
            print("  api docs         - 生成API文档")
            print("🔌 插件管理:")
            print("  plugin list      - 列出插件")
            print("  plugin install   - 安装插件")
            print("📚 学习工具:")
            print("  learn tutorial   - 交互式教程")
            print("  learn examples   - 查看示例")
            print("🌍 社区功能:")
            print("  community share  - 分享作品")
            print("  community discover - 发现作品")
            print("🤖 AI助手:")
            print("  ai chat          - AI助手对话")
            print("  ai analyze       - AI分析")
            print("  ai optimize      - AI优化建议")
    
    def _show_status(self):
        """显示会话状态"""
        if self.console:
            status_table = Table(title="📊 会话状态", show_header=True, header_style="bold blue")
            status_table.add_column("项目", style="cyan", width=20)
            status_table.add_column("值", style="green", width=40)
            
            status_table.add_row("启动时间", self.session_start.strftime('%Y-%m-%d %H:%M:%S'))
            status_table.add_row("运行时长", str(datetime.now() - self.session_start))
            status_table.add_row("执行命令数", str(self.session_info['commands_executed']))
            status_table.add_row("当前目录", self.session_info['current_directory'])
            status_table.add_row("环境", self.session_info['environment'])
            status_table.add_row("Python版本", sys.version.split()[0])
            status_table.add_row("ADC版本", "v3.0")
            
            self.console.print(status_table)
        else:
            print("📊 会话状态")
            print("启动时间:", self.session_start.strftime('%Y-%m-%d %H:%M:%S'))
            print("运行时长:", datetime.now() - self.session_start)
            print("执行命令数:", self.session_info['commands_executed'])
            print("当前目录:", self.session_info['current_directory'])
            print("环境:", self.session_info['environment'])
            print("Python版本:", sys.version.split()[0])
            print("ADC版本: v3.0")
    
    def _execute_builtin_command(self, command: str, args: List[str]) -> bool:
        """执行内置命令"""
        if command == 'help':
            self._show_help()
            return True
        elif command == 'status':
            self._show_status()
            return True
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            return True
        elif command == 'version':
            if self.console:
                self.console.print("[bold cyan]ADC版本: v3.0[/bold cyan]")
            else:
                print("ADC版本: v3.0")
            return True
        elif command == 'exit' or command == 'quit':
            if self.console:
                self.console.print("[yellow]👋 再见！[/yellow]")
            else:
                print("👋 再见！")
            self.running = False
            return True
        elif command == 'pwd':
            print(os.getcwd())
            return True
        elif command == 'ls':
            try:
                files = os.listdir('.')
                for file in files:
                    if os.path.isdir(file):
                        print(f"📁 {file}/")
                    else:
                        print(f"📄 {file}")
            except Exception as e:
                print(f"❌ 列出目录失败: {e}")
            return True
        elif command == 'cd':
            if args:
                try:
                    os.chdir(args[0])
                    self.session_info['current_directory'] = os.getcwd()
                    print(f"📁 切换到目录: {os.getcwd()}")
                except Exception as e:
                    print(f"❌ 切换目录失败: {e}")
            else:
                print("❌ 请指定目录路径")
            return True
        elif command == 'env':
            for key, value in os.environ.items():
                print(f"{key}={value}")
            return True
        elif command == 'session':
            self._show_status()
            return True
        
        return False
    
    async def _execute_adc_command(self, command: str, args: List[str]) -> bool:
        """执行ADC命令"""
        try:
            # 构建模拟的args对象
            class MockArgs:
                def __init__(self, cmd, arguments):
                    self.cmd = cmd
                    self.arguments = arguments
                    
                    # 设置命令动作属性
                    if cmd.startswith('system '):
                        self.system_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('dev '):
                        self.dev_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('data '):
                        self.data_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('integration '):
                        self.integration_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('security '):
                        self.security_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('monitor '):
                        self.monitor_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('api '):
                        self.api_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('plugin '):
                        self.plugin_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('learn '):
                        self.learn_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('community '):
                        self.community_action = cmd.split(' ', 1)[1]
                    elif cmd.startswith('ai '):
                        self.ai_action = cmd.split(' ', 1)[1]
                    
                    # 设置其他属性
                    for i, arg in enumerate(arguments):
                        setattr(self, f'arg_{i}', arg)
            
            mock_args = MockArgs(command, args)
            
            # 尝试执行增强命令
            if command.startswith(('system', 'dev', 'data', 'integration', 'security', 'monitor', 'api', 'plugin', 'learn', 'community', 'ai')):
                result = await self.enhanced_registry.execute_command(mock_args)
                return True
            else:
                # 这里可以添加对原有命令的支持
                if self.console:
                    self.console.print(f"[yellow]🔄 命令 '{command}' 正在处理中...[/yellow]")
                else:
                    print(f"🔄 命令 '{command}' 正在处理中...")
                return True
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ 命令执行失败: {e}[/red]")
            else:
                print(f"❌ 命令执行失败: {e}")
            return True
    
    async def run(self):
        """运行Shell"""
        self._show_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                if self.console:
                    prompt = Prompt.ask(f"[bold green]ADC[/bold green] [bold cyan]{os.getcwd()}[/bold cyan] [bold yellow]>>>[/bold yellow]")
                else:
                    prompt = input(f"ADC {os.getcwd()} >>> ")
                
                if not prompt.strip():
                    continue
                
                # 解析命令
                try:
                    parts = shlex.split(prompt)
                    command = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]❌ 命令解析失败: {e}[/red]")
                    else:
                        print(f"❌ 命令解析失败: {e}")
                    continue
                
                # 更新会话信息
                self.session_info['commands_executed'] += 1
                
                # 执行命令
                if not self._execute_builtin_command(command, args):
                    await self._execute_adc_command(command, args)
                
            except KeyboardInterrupt:
                if self.console:
                    self.console.print("\n[yellow]⚠️ 使用 'exit' 或 'quit' 退出[/yellow]")
                else:
                    print("\n⚠️ 使用 'exit' 或 'quit' 退出")
            except EOFError:
                break
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]❌ 意外错误: {e}[/red]")
                else:
                    print(f"❌ 意外错误: {e}")
        
        # 保存历史
        self._save_history()


async def main():
    """主函数"""
    shell = EnhancedADCShell()
    await shell.run()


if __name__ == "__main__":
    asyncio.run(main()) 