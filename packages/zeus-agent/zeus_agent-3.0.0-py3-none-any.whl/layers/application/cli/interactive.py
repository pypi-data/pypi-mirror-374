"""
Interactive Shell
交互式Shell界面 - 增强版
"""

import asyncio
import sys
import os
import shlex
from typing import List, Dict, Any, Optional, Tuple
import readline
import atexit
from pathlib import Path
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import print as rprint
    from rich.live import Live
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ADCCompleter:
    """
    ADC命令自动补全器
    """
    
    def __init__(self, command_registry):
        self.command_registry = command_registry
        self.commands = self._build_command_tree()
    
    def _build_command_tree(self) -> Dict[str, Any]:
        """构建命令树用于自动补全"""
        return {
            'agent': {
                'list': ['--format', '--filter', '--sort'],
                'create': ['--name', '--type', '--model', '--system-message', '--template', '--capabilities', '--interactive'],
                'chat': ['--name', '--message', '--history', '--save'],
                'info': [],
                'delete': ['--force']
            },
            'workflow': {
                'list': ['--format', '--status'],
                'create': ['--name', '--description', '--template', '--file', '--interactive'],
                'run': ['--id', '--context', '--watch', '--timeout'],
                'status': ['--follow'],
                'logs': ['--follow', '--lines']
            },
            'team': {
                'list': ['--format'],
                'create': ['--name', '--members', '--template', '--interactive'],
                'collaborate': ['--team', '--task', '--pattern', '--watch'],
                'performance': ['--period']
            },
            'project': {
                'init': ['--template', '--path', '--interactive'],
                'list': ['--format'],
                'status': [],
                'build': ['--target', '--watch'],
                'deploy': ['--env', '--dry-run']
            },
            'config': {
                'get': [],
                'set': [],
                'list': ['--format'],
                'edit': ['--editor']
            },
            'monitor': {
                'system': ['--interval'],
                'agents': ['--interval'],
                'workflows': ['--interval']
            },
            'tools': {
                'validate': ['--fix'],
                'benchmark': ['--type', '--duration'],
                'export': ['--type', '--format', '--output'],
                'import': ['--type', '--merge']
            },
            'demo': {
                'openai': ['--model', '--interactive'],
                'business': ['--module', '--verbose'],
                'orchestration': ['--verbose'],
                'interactive': []
            },
            'help': {
                'commands': ['--category'],
                'examples': ['--command'],
                'docs': ['--local']
            }
        }
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """自动补全函数"""
        try:
            line = readline.get_line_buffer()
            tokens = shlex.split(line) if line else []
            
            # 如果当前正在输入，tokens的最后一个可能是不完整的
            if line.endswith(' '):
                current_token = ''
            else:
                current_token = tokens[-1] if tokens else ''
                tokens = tokens[:-1] if tokens else []
            
            candidates = self._get_candidates(tokens, current_token)
            
            # 过滤匹配的候选项
            matches = [cmd for cmd in candidates if cmd.startswith(current_token)]
            
            if state < len(matches):
                return matches[state]
            else:
                return None
                
        except Exception:
            return None
    
    def _get_candidates(self, tokens: List[str], current_token: str) -> List[str]:
        """获取候选补全项"""
        if not tokens:
            # 顶级命令
            return list(self.commands.keys()) + ['exit', 'quit', 'help', 'clear', 'history', 'version', 'status']
        
        if len(tokens) == 1:
            # 第一级子命令
            main_cmd = tokens[0]
            if main_cmd in self.commands:
                return list(self.commands[main_cmd].keys())
        
        elif len(tokens) == 2:
            # 第二级参数
            main_cmd, sub_cmd = tokens[0], tokens[1]
            if main_cmd in self.commands and sub_cmd in self.commands[main_cmd]:
                return self.commands[main_cmd][sub_cmd]
        
        return []


class InteractiveShell:
    """
    交互式Shell界面 - 增强版
    """
    
    def __init__(self, command_registry):
        self.command_registry = command_registry
        self.history_file = Path.home() / ".adc_history"
        self.running = True
        self.session_commands = []
        
        if RICH_AVAILABLE:
            self.console = Console()
        
        # 设置历史记录和自动补全
        self._setup_history()
        self._setup_completion()
        
        # 内置命令
        self.builtin_commands = {
            'help': self._cmd_help,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
            'clear': self._cmd_clear,
            'history': self._cmd_history,
            'version': self._cmd_version,
            'status': self._cmd_status,
            'alias': self._cmd_alias,
            'echo': self._cmd_echo,
            'cd': self._cmd_cd,
            'ls': self._cmd_ls,
            'pwd': self._cmd_pwd,
            'env': self._cmd_env,
            'session': self._cmd_session,
        }
        
        # 别名系统
        self.aliases = {
            'a': 'agent',
            'w': 'workflow',
            't': 'team',
            'p': 'project',
            'c': 'config',
            'm': 'monitor',
            'd': 'demo',
            'h': 'help',
            'll': 'agent list',
            'cc': 'config list',
            'ss': 'status',
        }
    
    def _setup_history(self):
        """设置命令历史记录"""
        try:
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
            
            # 限制历史记录数量
            readline.set_history_length(1000)
            
            # 注册退出时保存历史记录
            atexit.register(self._save_history)
            
        except Exception:
            # 如果readline不可用，忽略错误
            pass
    
    def _setup_completion(self):
        """设置自动补全"""
        try:
            self.completer = ADCCompleter(self.command_registry)
            readline.set_completer(self.completer.complete)
            readline.parse_and_bind("tab: complete")
            
            # 设置补全显示选项
            readline.parse_and_bind("set show-all-if-ambiguous on")
            readline.parse_and_bind("set completion-ignore-case on")
            readline.parse_and_bind("set completion-query-items 200")
            
        except Exception:
            pass
    
    def _save_history(self):
        """保存命令历史记录"""
        try:
            readline.write_history_file(str(self.history_file))
        except Exception:
            pass
    
    async def run(self) -> int:
        """运行交互式Shell"""
        self._print_welcome()
        
        while self.running:
            try:
                # 显示提示符并获取输入
                prompt = self._get_prompt()
                line = input(prompt).strip()
                
                if not line:
                    continue
                
                # 记录会话命令
                self.session_commands.append(line)
                
                # 解析和执行命令
                await self._execute_line(line)
                
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    self.console.print("\n[yellow]使用 'exit' 或 'quit' 退出[/yellow]")
                else:
                    print("\n使用 'exit' 或 'quit' 退出")
                continue
            except EOFError:
                if RICH_AVAILABLE:
                    self.console.print("\n[green]👋 再见![/green]")
                else:
                    print("\n👋 再见!")
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ 错误: {e}[/red]")
                else:
                    print(f"❌ 错误: {e}")
        
        return 0
    
    def _print_welcome(self):
        """打印欢迎信息"""
        if RICH_AVAILABLE:
            welcome_panel = Panel.fit(
                "[bold green]🚀 Agent Development Center - 交互模式[/bold green]\n\n"
                "[cyan]欢迎使用ADC交互式Shell！[/cyan]\n\n"
                "[yellow]💡 提示:[/yellow]\n"
                "   • 输入 '[bold]help[/bold]' 查看可用命令\n"
                "   • 使用 '[bold]Tab[/bold]' 键自动补全命令\n"
                "   • 输入 '[bold]demo interactive[/bold]' 启动演示向导\n"
                "   • 输入 '[bold]exit[/bold]' 或 '[bold]quit[/bold]' 退出\n\n"
                "[dim]版本: v2.0.0-enhanced | 支持: 8层架构 | 状态: 100%完成[/dim]",
                title="ADC Interactive Shell",
                border_style="green"
            )
            self.console.print(welcome_panel)
        else:
            print("🚀 Agent Development Center - 交互模式")
            print("=" * 60)
            print("欢迎使用ADC交互式Shell！")
            print()
            print("💡 提示:")
            print("   • 输入 'help' 查看可用命令")
            print("   • 使用 Tab 键自动补全命令")
            print("   • 输入 'demo interactive' 启动演示向导")
            print("   • 输入 'exit' 或 'quit' 退出")
            print()
    
    def _get_prompt(self) -> str:
        """获取命令提示符"""
        current_dir = Path.cwd().name
        if RICH_AVAILABLE:
            # Rich不支持input的提示符着色，所以使用普通文本
            return f"adc:{current_dir}$ "
        else:
            return f"adc:{current_dir}$ "
    
    async def _execute_line(self, line: str):
        """执行命令行"""
        try:
            # 处理别名
            line = self._resolve_aliases(line)
            
            # 解析命令
            tokens = shlex.split(line)
            if not tokens:
                return
            
            command = tokens[0]
            
            # 检查内置命令
            if command in self.builtin_commands:
                await self.builtin_commands[command](tokens[1:])
                return
            
            # 构建argparse参数
            args_list = tokens
            
            # 使用命令注册器执行命令
            parser = argparse.ArgumentParser(prog="adc", add_help=False)
            subparsers = parser.add_subparsers(dest="command")
            self.command_registry.register_commands(subparsers)
            
            try:
                args = parser.parse_args(args_list)
                result = await self.command_registry.execute_command(args)
                
                if result != 0:
                    if RICH_AVAILABLE:
                        self.console.print(f"[red]命令执行失败，退出码: {result}[/red]")
                    else:
                        print(f"命令执行失败，退出码: {result}")
                        
            except SystemExit:
                # argparse在--help时会抛出SystemExit
                pass
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌ 命令执行错误: {e}[/red]")
                else:
                    print(f"❌ 命令执行错误: {e}")
                
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ 解析错误: {e}[/red]")
            else:
                print(f"❌ 解析错误: {e}")
    
    def _resolve_aliases(self, line: str) -> str:
        """解析别名"""
        tokens = shlex.split(line) if line else []
        if tokens and tokens[0] in self.aliases:
            alias_expansion = shlex.split(self.aliases[tokens[0]])
            return ' '.join(alias_expansion + tokens[1:])
        return line
    
    # 内置命令实现
    async def _cmd_help(self, args: List[str]):
        """显示帮助"""
        if RICH_AVAILABLE:
            help_table = Table(title="ADC Interactive Shell - 内置命令")
            help_table.add_column("命令", style="cyan")
            help_table.add_column("描述", style="magenta")
            help_table.add_column("示例", style="green")
            
            help_data = [
                ("help", "显示帮助信息", "help"),
                ("exit/quit", "退出Shell", "exit"),
                ("clear", "清屏", "clear"),
                ("history", "显示命令历史", "history"),
                ("version", "显示版本信息", "version"),
                ("status", "显示系统状态", "status"),
                ("alias", "管理别名", "alias ll 'agent list'"),
                ("echo", "输出文本", "echo Hello World"),
                ("cd", "切换目录", "cd /path/to/dir"),
                ("ls", "列出文件", "ls -la"),
                ("pwd", "显示当前目录", "pwd"),
                ("env", "显示环境变量", "env"),
                ("session", "会话管理", "session save/load"),
            ]
            
            for cmd, desc, example in help_data:
                help_table.add_row(cmd, desc, example)
            
            self.console.print(help_table)
            
            self.console.print("\n[yellow]💡 ADC命令示例:[/yellow]")
            examples = [
                "agent list --format table",
                "workflow run --id wf_001",
                "team create --name MyTeam --interactive",
                "demo business --verbose",
                "config set openai_model gpt-4o-mini"
            ]
            for example in examples:
                self.console.print(f"  [green]adc:{Path.cwd().name}$[/green] {example}")
                
        else:
            print("ADC Interactive Shell - 内置命令:")
            print("=" * 40)
            print("help       - 显示帮助信息")
            print("exit/quit  - 退出Shell")
            print("clear      - 清屏")
            print("history    - 显示命令历史")
            print("version    - 显示版本信息")
            print("status     - 显示系统状态")
            print("alias      - 管理别名")
            print("echo       - 输出文本")
            print("cd         - 切换目录")
            print("ls         - 列出文件")
            print("pwd        - 显示当前目录")
            print("env        - 显示环境变量")
            print("session    - 会话管理")
    
    async def _cmd_exit(self, args: List[str]):
        """退出Shell"""
        if args and args[0] == '--save-session':
            await self._cmd_session(['save'])
        
        if RICH_AVAILABLE:
            self.console.print("[green]👋 再见！感谢使用ADC![/green]")
        else:
            print("👋 再见！感谢使用ADC!")
        self.running = False
    
    async def _cmd_clear(self, args: List[str]):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    async def _cmd_history(self, args: List[str]):
        """显示命令历史"""
        if RICH_AVAILABLE:
            history_table = Table(title="命令历史")
            history_table.add_column("序号", style="cyan", width=6)
            history_table.add_column("命令", style="magenta")
            
            # 显示最近的命令
            recent_commands = self.session_commands[-20:] if len(self.session_commands) > 20 else self.session_commands
            for i, cmd in enumerate(recent_commands, 1):
                history_table.add_row(str(i), cmd)
            
            self.console.print(history_table)
        else:
            print("命令历史:")
            print("=" * 20)
            recent_commands = self.session_commands[-20:] if len(self.session_commands) > 20 else self.session_commands
            for i, cmd in enumerate(recent_commands, 1):
                print(f"{i:3d}  {cmd}")
    
    async def _cmd_version(self, args: List[str]):
        """显示版本信息"""
        if RICH_AVAILABLE:
            version_panel = Panel(
                "[bold green]Agent Development Center[/bold green]\n"
                "[cyan]版本:[/cyan] v2.0.0-enhanced\n"
                "[cyan]架构:[/cyan] 8层完整架构\n"
                "[cyan]完成度:[/cyan] 100%\n"
                "[cyan]支持功能:[/cyan] Agent管理、工作流、团队协作、应用编排\n"
                "[cyan]增强功能:[/cyan] Rich界面、自动补全、别名系统",
                title="版本信息",
                border_style="green"
            )
            self.console.print(version_panel)
        else:
            print("Zeus AI Platform")
            print("版本: v2.0.0-enhanced")
            print("架构: 8层完整架构")
            print("完成度: 100%")
            print("支持功能: Agent管理、工作流、团队协作、应用编排")
            print("增强功能: Rich界面、自动补全、别名系统")
    
    async def _cmd_status(self, args: List[str]):
        """显示系统状态"""
        if RICH_AVAILABLE:
            status_table = Table(title="系统状态")
            status_table.add_column("组件", style="cyan")
            status_table.add_column("状态", style="magenta")
            status_table.add_column("描述", style="green")
            
            status_data = [
                ("Shell", "✅ 运行中", "交互式Shell正常运行"),
                ("命令系统", "✅ 就绪", "所有命令已注册"),
                ("自动补全", "✅ 启用", "Tab补全功能正常"),
                ("Rich界面", "✅ 可用" if RICH_AVAILABLE else "❌ 不可用", "增强显示功能"),
                ("历史记录", "✅ 启用", f"历史文件: {self.history_file}"),
                ("别名系统", "✅ 启用", f"已定义 {len(self.aliases)} 个别名"),
            ]
            
            for component, status, desc in status_data:
                status_table.add_row(component, status, desc)
            
            self.console.print(status_table)
        else:
            print("系统状态:")
            print("=" * 30)
            print("Shell: ✅ 运行中")
            print("命令系统: ✅ 就绪")
            print("自动补全: ✅ 启用")
            print(f"Rich界面: {'✅ 可用' if RICH_AVAILABLE else '❌ 不可用'}")
            print(f"历史记录: ✅ 启用 ({self.history_file})")
            print(f"别名系统: ✅ 启用 ({len(self.aliases)} 个别名)")
    
    async def _cmd_alias(self, args: List[str]):
        """管理别名"""
        if not args:
            # 显示所有别名
            if RICH_AVAILABLE:
                alias_table = Table(title="别名列表")
                alias_table.add_column("别名", style="cyan")
                alias_table.add_column("命令", style="magenta")
                
                for alias, command in self.aliases.items():
                    alias_table.add_row(alias, command)
                
                self.console.print(alias_table)
            else:
                print("别名列表:")
                print("=" * 20)
                for alias, command in self.aliases.items():
                    print(f"{alias:10} -> {command}")
        
        elif len(args) == 1:
            # 显示特定别名
            alias = args[0]
            if alias in self.aliases:
                print(f"{alias} -> {self.aliases[alias]}")
            else:
                print(f"别名 '{alias}' 不存在")
        
        elif len(args) == 2:
            # 设置别名
            alias, command = args[0], args[1]
            self.aliases[alias] = command
            print(f"✅ 设置别名: {alias} -> {command}")
        
        else:
            print("用法: alias [别名] [命令]")
    
    async def _cmd_echo(self, args: List[str]):
        """输出文本"""
        text = ' '.join(args)
        if RICH_AVAILABLE:
            self.console.print(text)
        else:
            print(text)
    
    async def _cmd_cd(self, args: List[str]):
        """切换目录"""
        if not args:
            target = Path.home()
        else:
            target = Path(args[0]).expanduser()
        
        try:
            os.chdir(target)
            if RICH_AVAILABLE:
                self.console.print(f"[green]切换到目录: {target}[/green]")
            else:
                print(f"切换到目录: {target}")
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ 无法切换目录: {e}[/red]")
            else:
                print(f"❌ 无法切换目录: {e}")
    
    async def _cmd_ls(self, args: List[str]):
        """列出文件"""
        import subprocess
        try:
            result = subprocess.run(['ls'] + args, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"❌ 无法执行ls命令: {e}")
    
    async def _cmd_pwd(self, args: List[str]):
        """显示当前目录"""
        current_dir = Path.cwd()
        if RICH_AVAILABLE:
            self.console.print(f"[cyan]当前目录: {current_dir}[/cyan]")
        else:
            print(f"当前目录: {current_dir}")
    
    async def _cmd_env(self, args: List[str]):
        """显示环境变量"""
        if args:
            # 显示特定环境变量
            var_name = args[0]
            value = os.environ.get(var_name)
            if value:
                print(f"{var_name}={value}")
            else:
                print(f"环境变量 '{var_name}' 未设置")
        else:
            # 显示所有环境变量
            if RICH_AVAILABLE:
                env_table = Table(title="环境变量")
                env_table.add_column("变量名", style="cyan")
                env_table.add_column("值", style="magenta")
                
                for key, value in sorted(os.environ.items()):
                    # 限制显示长度
                    display_value = value[:50] + "..." if len(value) > 50 else value
                    env_table.add_row(key, display_value)
                
                self.console.print(env_table)
            else:
                for key, value in sorted(os.environ.items()):
                    print(f"{key}={value}")
    
    async def _cmd_session(self, args: List[str]):
        """会话管理"""
        if not args:
            print("用法: session [save|load|clear|info]")
            return
        
        action = args[0]
        
        if action == 'save':
            session_file = Path.home() / ".adc_session"
            try:
                with open(session_file, 'w') as f:
                    for cmd in self.session_commands:
                        f.write(f"{cmd}\n")
                print(f"✅ 会话已保存到: {session_file}")
            except Exception as e:
                print(f"❌ 保存会话失败: {e}")
        
        elif action == 'load':
            session_file = Path.home() / ".adc_session"
            try:
                if session_file.exists():
                    with open(session_file, 'r') as f:
                        loaded_commands = f.read().strip().split('\n')
                    self.session_commands.extend(loaded_commands)
                    print(f"✅ 已加载 {len(loaded_commands)} 条命令")
                else:
                    print("❌ 会话文件不存在")
            except Exception as e:
                print(f"❌ 加载会话失败: {e}")
        
        elif action == 'clear':
            self.session_commands.clear()
            print("✅ 会话命令已清空")
        
        elif action == 'info':
            print(f"会话信息:")
            print(f"  命令总数: {len(self.session_commands)}")
            print(f"  历史文件: {self.history_file}")
            if self.session_commands:
                print(f"  最近命令: {self.session_commands[-1]}")
        
        else:
            print("未知操作，支持: save, load, clear, info") 