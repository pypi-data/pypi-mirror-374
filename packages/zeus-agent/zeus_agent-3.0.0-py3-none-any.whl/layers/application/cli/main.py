#!/usr/bin/env python3
"""
ADC CLI Application
Agent Development Center 命令行界面主程序
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, List
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from .commands import CommandRegistry
from .interactive import InteractiveShell
from ...infrastructure.logging import get_logger
from ...infrastructure.config.config_manager import ConfigManager


class ADCCLIApp:
    """
    ADC CLI应用程序主类
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = get_logger("adc_cli")
        self.command_registry = CommandRegistry()
        self.interactive_shell = None
        
    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog="adc",
            description="Agent Development Center - 下一代AI Agent开发平台",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  adc --version                    # 显示版本信息
  adc --interactive                # 启动交互模式
  adc agent list                   # 列出所有Agent
  adc agent create --name MyAgent  # 创建新Agent
  adc workflow run --id workflow1  # 运行工作流
  adc team create --name MyTeam    # 创建团队
  adc demo openai                  # 运行OpenAI演示
  adc demo business                # 运行业务层演示

更多信息请访问: https://github.com/fpga1988/zeus
            """
        )
        
        # 全局选项
        parser.add_argument(
            "--version", "-v",
            action="version",
            version="Agent Development Center v2.0.0-alpha"
        )
        
        parser.add_argument(
            "--config", "-c",
            type=str,
            help="配置文件路径"
        )
        
        parser.add_argument(
            "--verbose", "-V",
            action="store_true",
            help="详细输出模式"
        )
        
        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="启动交互模式"
        )
        
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="日志级别"
        )
        
        # 子命令
        subparsers = parser.add_subparsers(
            dest="command",
            help="可用命令",
            metavar="COMMAND"
        )
        
        # 注册所有命令
        self.command_registry.register_commands(subparsers)
        
        return parser
    
    def setup_logging(self, log_level: str, verbose: bool = False):
        """设置日志"""
        level = getattr(logging, log_level.upper())
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if verbose else '%(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    
    async def run_async(self, args: argparse.Namespace) -> int:
        """异步运行应用程序"""
        try:
            # 设置日志
            self.setup_logging(args.log_level, args.verbose)
            
            # 加载配置
            if args.config:
                self.config_manager.load_config(args.config)
            
            # 交互模式
            if args.interactive:
                self.interactive_shell = InteractiveShell(self.command_registry)
                return await self.interactive_shell.run()
            
            # 命令模式
            if args.command:
                return await self.command_registry.execute_command(args)
            else:
                # 没有命令，显示帮助
                parser = self.create_parser()
                parser.print_help()
                return 0
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，ADC已退出")
            return 130
        except Exception as e:
            self.logger.error(f"应用程序错误: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    async def run_command(self, command_args: List[str]) -> bool:
        """运行指定命令 - 用于测试和程序化调用"""
        try:
            parser = self.create_parser()
            args = parser.parse_args(command_args)
            result = await self.run_async(args)
            return result == 0  # 成功返回True，失败返回False
        except SystemExit:
            # argparse在--help或--version时会抛出SystemExit
            return True
        except Exception as e:
            self.logger.error(f"命令执行错误: {e}")
            return False
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """运行应用程序"""
        parser = self.create_parser()
        args = parser.parse_args(argv)
        
        # 运行异步主函数
        try:
            return asyncio.run(self.run_async(args))
        except KeyboardInterrupt:
            return 130


def main():
    """CLI入口点"""
    app = ADCCLIApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main() 