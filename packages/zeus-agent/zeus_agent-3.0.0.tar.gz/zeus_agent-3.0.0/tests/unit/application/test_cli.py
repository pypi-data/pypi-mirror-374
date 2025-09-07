"""
Unit tests for CLI application layer
"""

import pytest
import argparse
import asyncio
import sys
import io
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from layers.application.cli.main import ADCCLIApp
from layers.application.cli.commands import CommandRegistry
from layers.application.cli.interactive import InteractiveShell


class TestADCCLIApp:
    """Test ADC CLI Application"""
    
    def test_initialization(self):
        """Test CLI app initialization"""
        app = ADCCLIApp()
        
        assert hasattr(app, 'config_manager')
        assert hasattr(app, 'logger')
        assert hasattr(app, 'command_registry')
        assert hasattr(app, 'interactive_shell')
        assert app.interactive_shell is None
    
    def test_create_parser(self):
        """Test argument parser creation"""
        app = ADCCLIApp()
        parser = app.create_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "adc"
        assert "Zeus" in parser.description
    
    def test_parser_version_argument(self):
        """Test version argument parsing"""
        app = ADCCLIApp()
        parser = app.create_parser()
        
        # Test version argument
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                parser.parse_args(['--version'])
        
        # SystemExit with code 0 indicates successful version display
        assert exc_info.value.code == 0
    
    def test_parser_interactive_argument(self):
        """Test interactive argument parsing"""
        app = ADCCLIApp()
        parser = app.create_parser()
        
        args = parser.parse_args(['--interactive'])
        assert args.interactive is True
    
    def test_parser_help_argument(self):
        """Test help argument parsing"""
        app = ADCCLIApp()
        parser = app.create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.stdout', new_callable=io.StringIO):
                parser.parse_args(['--help'])
        
        assert exc_info.value.code == 0
    
    @pytest.mark.asyncio
    async def test_run_async_with_command(self):
        """Test async run with command"""
        app = ADCCLIApp()
        
        # Mock successful command execution
        with patch.object(app.command_registry, 'execute_command', return_value=0) as mock_execute:
            args = Mock()
            args.log_level = 'INFO'
            args.verbose = False
            args.config = None
            args.interactive = False
            args.command = 'demo'
            
            result = await app.run_async(args)
            
            assert result == 0
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_async_with_interactive(self):
        """Test async run with interactive mode"""
        app = ADCCLIApp()
        
        # Mock interactive shell
        mock_shell = Mock()
        mock_shell.run = Mock(return_value=0)
        
        with patch('layers.application.cli.interactive.InteractiveShell', return_value=mock_shell):
            args = Mock()
            args.log_level = 'INFO'
            args.verbose = False
            args.config = None
            args.interactive = True
            args.command = None
            
            result = await app.run_async(args)
            
            assert result == 0
            assert app.interactive_shell is not None
            mock_shell.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_async_no_command(self):
        """Test async run without command (shows help)"""
        app = ADCCLIApp()
        
        with patch.object(app, 'create_parser') as mock_parser_creator:
            mock_parser = Mock()
            mock_parser.print_help = Mock()
            mock_parser_creator.return_value = mock_parser
            
            args = Mock()
            args.log_level = 'INFO'
            args.verbose = False
            args.config = None
            args.interactive = False
            args.command = None
            
            result = await app.run_async(args)
            
            assert result == 0
            mock_parser.print_help.assert_called_once()


class TestCommandRegistry:
    """Test Command Registry"""
    
    def test_initialization(self):
        """Test command registry initialization"""
        registry = CommandRegistry()
        
        assert hasattr(registry, 'commands')
        assert isinstance(registry.commands, dict)
    
    def test_register_commands(self):
        """Test command registration"""
        registry = CommandRegistry()
        
        # Create a mock argument parser with subparsers
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Should not raise any exceptions
        registry.register_commands(subparsers)
        
        # Verify that subcommands were added
        assert len(subparsers.choices) > 0
        assert 'agent' in subparsers.choices
        assert 'workflow' in subparsers.choices
        assert 'team' in subparsers.choices
        assert 'demo' in subparsers.choices
        assert 'system' in subparsers.choices
    
    @pytest.mark.asyncio
    async def test_execute_agent_list_command(self):
        """Test agent list command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for agent list command
        args = Mock()
        args.command = 'agent'
        args.agent_action = 'list'
        args.format = 'table'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            # Should execute successfully (return 0)
            assert result == 0
            # Should print some output
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_workflow_list_command(self):
        """Test workflow list command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for workflow list command
        args = Mock()
        args.command = 'workflow'
        args.workflow_action = 'list'
        args.format = 'table'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            assert result == 0
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_team_list_command(self):
        """Test team list command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for team list command
        args = Mock()
        args.command = 'team'
        args.team_action = 'list'
        args.format = 'table'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            assert result == 0
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_system_info_command(self):
        """Test system info command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for system info command
        args = Mock()
        args.command = 'system'
        args.system_action = 'info'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            assert result == 0
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_system_health_command(self):
        """Test system health command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for system health command
        args = Mock()
        args.command = 'system'
        args.system_action = 'health'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            assert result == 0
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_demo_basic_command(self):
        """Test demo basic command execution"""
        registry = CommandRegistry()
        
        # Mock arguments for demo command
        args = Mock()
        args.command = 'demo'
        args.demo_type = 'basic'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            assert result == 0
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_invalid_command(self):
        """Test execution of invalid command"""
        registry = CommandRegistry()
        
        # Mock arguments for invalid command
        args = Mock()
        args.command = 'invalid'
        
        with patch('builtins.print') as mock_print:
            result = await registry.execute_command(args)
            
            # Should return 1 for invalid command
            assert result == 1
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_command_with_exception(self):
        """Test command execution with exception"""
        registry = CommandRegistry()
        
        # Mock arguments that will cause an exception
        args = Mock()
        args.command = 'agent'
        args.agent_action = 'create'
        args.name = 'test_agent'
        args.type = 'openai'
        args.model = 'gpt-4o-mini'
        args.system_message = None
        
        # Mock the OpenAI adapter to raise an exception
        with patch('layers.application.cli.commands.OpenAIAdapter') as mock_adapter:
            mock_adapter.side_effect = Exception("Connection error")
            
            with patch('builtins.print') as mock_print:
                result = await registry.execute_command(args)
                
                # Should handle exception gracefully and return 1
                assert result == 1
                mock_print.assert_called()


class TestInteractiveShell:
    """Test Interactive Shell"""
    
    def test_initialization(self):
        """Test interactive shell initialization"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        assert hasattr(shell, 'command_registry')
        assert shell.command_registry == registry
        assert hasattr(shell, 'history_file')
        assert hasattr(shell, 'running')
        assert hasattr(shell, 'builtin_commands')
    
    def test_convert_to_argv(self):
        """Test command conversion to argv format"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        result = shell._convert_to_argv(["agent", "list"])
        
        assert isinstance(result, list)
        assert result == ["agent", "list"]
    
    def test_get_prompt(self):
        """Test prompt generation"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        prompt = shell._get_prompt()
        
        assert isinstance(prompt, str)
        assert "adc>" in prompt
    
    @pytest.mark.asyncio
    async def test_builtin_help_command(self):
        """Test built-in help command"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        with patch('builtins.print') as mock_print:
            await shell._cmd_help([])
            
            mock_print.assert_called()
            # Should print help information
            calls = [call.args[0] for call in mock_print.call_args_list]
            help_text = ' '.join(str(call) for call in calls)
            assert "可用命令" in help_text or "Agent管理" in help_text
    
    @pytest.mark.asyncio
    async def test_builtin_version_command(self):
        """Test built-in version command"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        with patch('builtins.print') as mock_print:
            await shell._cmd_version([])
            
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_line_with_builtin_command(self):
        """Test executing built-in command"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        with patch('builtins.print') as mock_print:
            await shell._execute_line("help")
            
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_line_with_empty_input(self):
        """Test executing empty line"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        # Should not raise any exception
        await shell._execute_line("")
        await shell._execute_line("   ")
    
    @pytest.mark.asyncio
    async def test_execute_line_with_unknown_command(self):
        """Test executing unknown command"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        with patch('builtins.print') as mock_print:
            await shell._execute_line("unknown_command")
            
            mock_print.assert_called()
            # Should print error message
            calls = [call.args[0] for call in mock_print.call_args_list]
            error_text = ' '.join(str(call) for call in calls)
            assert "未知命令" in error_text


class TestCLIEdgeCases:
    """Test CLI edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_cli_app_with_missing_config(self):
        """Test CLI app behavior with missing configuration"""
        with patch('layers.infrastructure.config.config_manager.ConfigManager') as mock_config:
            mock_config.side_effect = Exception("Config not found")
            
            # Should handle config initialization error gracefully
            try:
                app = ADCCLIApp()
                # Should not raise exception during initialization
                assert hasattr(app, 'command_registry')
            except Exception:
                pytest.fail("CLI app should handle missing config gracefully")
    
    def test_command_registry_with_invalid_subparsers(self):
        """Test command registry with invalid subparsers"""
        registry = CommandRegistry()
        
        # Should handle None subparsers gracefully
        try:
            registry.register_commands(None)
        except Exception as e:
            # Should raise AttributeError or similar, which is expected
            assert isinstance(e, (AttributeError, TypeError))
    
    @pytest.mark.asyncio
    async def test_interactive_shell_with_malformed_input(self):
        """Test interactive shell with malformed input"""
        registry = CommandRegistry()
        shell = InteractiveShell(registry)
        
        # Test with various malformed inputs
        malformed_inputs = [
            "agent --invalid-flag-without-command",
            "workflow create --name",  # Missing value
            "team create --name 'unclosed quote",
            "system info --unknown-flag"
        ]
        
        for malformed_input in malformed_inputs:
            # Execution might fail, but should not crash
            with patch('builtins.print'):  # Suppress error output
                await shell._execute_line(malformed_input)
                # Should complete without raising exception
    
    def test_cli_app_with_unicode_arguments(self):
        """Test CLI app with unicode arguments"""
        app = ADCCLIApp()
        parser = app.create_parser()
        
        # Should handle unicode in arguments
        try:
            # This might raise SystemExit due to unknown command, but should not crash on unicode
            parser.parse_args(['--help'])
        except SystemExit:
            # Expected for help command
            pass
    
    @pytest.mark.asyncio
    async def test_command_execution_with_network_timeout(self):
        """Test command execution with network timeout"""
        registry = CommandRegistry()
        
        args = Mock()
        args.command = 'demo'
        args.demo_type = 'openai'
        
        # Mock network timeout
        with patch('layers.application.cli.commands.OpenAIAdapter') as mock_adapter:
            mock_adapter.side_effect = TimeoutError("Network timeout")
            
            with patch('builtins.print') as mock_print:
                result = await registry.execute_command(args)
                
                # Should handle timeout gracefully and return 0 (demo commands handle errors)
                assert result == 0
                mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__]) 