"""
Cognitive Universal Agent Tests
测试认知通用Agent的功能
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

from layers.framework.abstractions.cognitive_agent import (
    CognitiveUniversalAgent,
    AgentType,
    ModelConfig,
    ToolConfig,
    MemoryConfig,
    BehaviorConfig,
    AgentConfig,
    ChatContext,
    ChatResponse,
    ToolResult,
    CodeResult,
    CodeExecutionResult,
    AnalysisResult
)
from layers.framework.abstractions.agent import AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus, ResultMetadata


class TestCognitiveAgent(CognitiveUniversalAgent):
    """测试用的认知Agent实现"""
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置Agent"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取Agent的schema"""
        return {
            "name": "test_agent",
            "description": "Test agent for unit testing",
            "version": "1.0.0",
            "capabilities": [
                AgentCapability.CONVERSATION,
                AgentCapability.REASONING
            ]
        }
    
    async def execute(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务"""
        # 这个方法会被mock，所以这里不需要实现
        pass


@pytest.mark.asyncio
class TestCognitiveUniversalAgent:
    """测试认知通用Agent"""
    
    @pytest_asyncio.fixture
    async def agent_config(self):
        """创建Agent配置"""
        return AgentConfig(
            name="test_agent",
            type=AgentType.CONVERSATIONAL,
            model=ModelConfig(
                provider="openai",
                model="gpt-4",
                temperature=0.7,
                max_tokens=1000
            ),
            capabilities=[
                AgentCapability.CONVERSATION,
                AgentCapability.REASONING
            ],
            tools=[
                ToolConfig(
                    name="calculator",
                    type="python",
                    description="计算器工具",
                    enabled=True,
                    config={"timeout": 5}
                )
            ],
            memory=MemoryConfig(
                enabled=True,
                max_memories=1000,
                memory_type="conversation"
            ),
            behavior=BehaviorConfig(
                max_consecutive_auto_reply=3,
                human_input_mode="NEVER",
                code_execution_config={}
            ),
            system_message="You are a helpful AI assistant.",
            description="测试智能体"
        )
    
    @pytest_asyncio.fixture
    async def agent(self, agent_config):
        """创建Agent实例"""
        agent = TestCognitiveAgent(agent_config)
        agent.execute = AsyncMock()  # 模拟execute方法
        return agent
    
    async def test_chat(self, agent):
        """测试对话功能"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.9  # type: ignore
        agent.execute.return_value = UniversalResult(
            content={"response": "Hello! How can I help you?"},
            status=ResultStatus.SUCCESS,
            result_type="conversation",
            metadata=metadata
        )
        
        # 创建对话上下文
        context = ChatContext(
            conversation_history=[
                {"user": "Hi", "assistant": "Hello!", "timestamp": "2024-03-20T10:00:00"}
            ],
            user_preferences={"language": "en"},
            session_data={"session_id": "123"}
        )
        
        # 测试对话
        response = await agent.chat("How are you?", context)
        
        # 验证结果
        assert isinstance(response, ChatResponse)
        assert response.content == "Hello! How can I help you?"
        assert response.confidence == 0.9
        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0]["user"] == "How are you?"
        assert agent.conversation_history[0]["assistant"] == "Hello! How can I help you?"
        
        # 验证任务创建
        task = agent.execute.call_args[0][0]
        assert task.content == "How are you?"
        assert task.task_type == TaskType.CONVERSATION
        
        # 验证上下文传递
        exec_context = agent.execute.call_args[0][1]
        assert exec_context.get("conversation_mode") is True
        assert len(exec_context.get("conversation_history")) == 1
        assert exec_context.get("user_preferences") == {"language": "en"}
    
    async def test_execute_tool(self, agent):
        """测试工具执行功能"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"tool": "calculator"})
        metadata.execution_time = 0.1  # type: ignore
        agent.execute.return_value = UniversalResult(
            content={"tool_result": 42},
            status=ResultStatus.SUCCESS,
            result_type="tool_execution",
            metadata=metadata
        )
        
        # 测试工具执行
        result = await agent.execute_tool(
            "calculator",
            expression="2 + 2"
        )
        
        # 验证结果
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.result == 42
        assert result.error_message is None
        assert result.execution_time > 0
        
        # 验证任务创建
        task = agent.execute.call_args[0][0]
        assert task.content == "Execute tool: calculator"
        assert task.task_type == TaskType.TOOL_EXECUTION
        
        # 验证上下文传递
        exec_context = agent.execute.call_args[0][1]
        assert exec_context.get("tool_name") == "calculator"
        assert exec_context.get("tool_parameters") == {"expression": "2 + 2"}
    
    async def test_generate_code(self, agent):
        """测试代码生成功能"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        agent.execute.return_value = UniversalResult(
            content={
                "code": "def add(a, b):\n    return a + b",
                "explanation": "A simple addition function",
                "dependencies": ["typing"]
            },
            status=ResultStatus.SUCCESS,
            result_type="code_generation",
            metadata=metadata
        )
        
        # 测试代码生成
        result = await agent.generate_code(
            "Write a function to add two numbers",
            language="python"
        )
        
        # 验证结果
        assert isinstance(result, CodeResult)
        assert "def add(a, b):" in result.code
        assert result.language == "python"
        assert result.explanation == "A simple addition function"
        assert "typing" in result.dependencies
        
        # 验证任务创建
        task = agent.execute.call_args[0][0]
        assert task.content == "Generate python code for: Write a function to add two numbers"
        assert task.task_type == TaskType.CODE_GENERATION
        
        # 验证上下文传递
        exec_context = agent.execute.call_args[0][1]
        assert exec_context.get("language") == "python"
        assert exec_context.get("code_generation") is True
    
    async def test_execute_code(self, agent):
        """测试代码执行功能"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"language": "python"})
        metadata.execution_time = 0.1  # type: ignore
        agent.execute.return_value = UniversalResult(
            content={
                "output": "4",
                "return_code": 0
            },
            status=ResultStatus.SUCCESS,
            result_type="code_execution",
            metadata=metadata
        )
        
        # 测试代码执行
        result = await agent.execute_code(
            "print(2 + 2)",
            language="python"
        )
        
        # 验证结果
        assert isinstance(result, CodeExecutionResult)
        assert result.success is True
        assert result.output == "4"
        assert result.error is None
        assert result.execution_time > 0
        assert result.return_code == 0
        
        # 验证任务创建
        task = agent.execute.call_args[0][0]
        assert task.content == "print(2 + 2)"
        assert task.task_type == TaskType.CODE_EXECUTION
        
        # 验证上下文传递
        exec_context = agent.execute.call_args[0][1]
        assert exec_context.get("language") == "python"
        assert exec_context.get("code_execution") is True
    
    async def test_analyze_content(self, agent):
        """测试内容分析功能"""
        # 模拟成功的执行结果
        metadata = ResultMetadata(framework_info={"model": "gpt-4"})
        metadata.confidence = 0.85  # type: ignore
        agent.execute.return_value = UniversalResult(
            content={
                "sentiment": "positive",
                "keywords": ["happy", "excited"],
                "summary": "A positive message"
            },
            status=ResultStatus.SUCCESS,
            result_type="analysis",
            metadata=metadata
        )
        
        # 测试内容分析
        result = await agent.analyze_content(
            "I'm so happy and excited about this!",
            analysis_type="sentiment"
        )
        
        # 验证结果
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "sentiment"
        assert result.result["sentiment"] == "positive"
        assert "happy" in result.result["keywords"]
        assert result.confidence == 0.85
        
        # 验证任务创建
        task = agent.execute.call_args[0][0]
        assert "sentiment" in task.content
        assert task.task_type == TaskType.ANALYSIS
        
        # 验证上下文传递
        exec_context = agent.execute.call_args[0][1]
        assert exec_context.get("analysis_type") == "sentiment"
        assert "I'm so happy" in exec_context.get("content")
    
    async def test_memory_management(self, agent):
        """测试记忆管理功能"""
        # 测试记忆存储
        await agent.remember(
            "user_preference",
            {"theme": "dark", "language": "en"},
            metadata={"source": "user_settings"}
        )
        
        # 验证记忆存储
        assert "user_preference" in agent.memory
        stored_memory = agent.memory["user_preference"]
        assert stored_memory["value"]["theme"] == "dark"
        assert stored_memory["metadata"]["source"] == "user_settings"
        
        # 测试记忆检索
        recalled_value = await agent.recall("user_preference")
        assert recalled_value["theme"] == "dark"
        assert recalled_value["language"] == "en"
        
        # 测试记忆搜索
        search_results = await agent.search_memory("dark")
        assert len(search_results) == 1
        assert search_results[0]["key"] == "user_preference"
        
        # 测试记忆限制
        for i in range(1100):  # 超过最大记忆数量
            await agent.remember(f"test_{i}", i)
        assert len(agent.memory) == 1000  # 验证记忆数量限制
    
    async def test_error_handling(self, agent):
        """测试错误处理"""
        # 模拟执行失败
        agent.execute.return_value = UniversalResult(
            content={},
            status=ResultStatus.ERROR,
            result_type="conversation",
            error={"message": "Failed to process request"},
            metadata=ResultMetadata(framework_info={})
        )
        
        # 测试对话错误处理
        response = await agent.chat("Hello")
        assert "error" in response.content.lower()
        assert response.confidence == 0.0
        
        # 测试工具执行错误处理
        result = await agent.execute_tool("invalid_tool")
        assert result.success is False
        assert "Failed to process request" in result.error_message
        
        # 测试代码生成错误处理
        code_result = await agent.generate_code("invalid request")
        assert code_result.code == ""
        assert "Error:" in code_result.explanation
        
        # 测试代码执行错误处理
        exec_result = await agent.execute_code("invalid code")
        assert exec_result.success is False
        assert exec_result.return_code == -1
        
        # 测试分析错误处理
        analysis_result = await agent.analyze_content("", "invalid_type")
        assert "error" in analysis_result.result
        assert analysis_result.confidence == 0.0
    
    async def test_performance_metrics(self, agent):
        """测试性能指标"""
        # 添加一些测试数据
        agent.execute.return_value = UniversalResult(
            content={"response": "Hello!"},
            status=ResultStatus.SUCCESS,
            result_type="conversation",
            metadata=ResultMetadata(framework_info={})
        )
        await agent.chat("Hello")
        await agent.remember("test", "value")
        
        # 获取指标
        metrics = agent.get_cognitive_metrics()
        
        # 验证指标
        assert metrics["agent_type"] == AgentType.CONVERSATIONAL.value
        assert metrics["conversation_count"] == 1
        assert metrics["memory_count"] == 1
        assert metrics["tool_count"] == 1
        assert AgentCapability.CONVERSATION.value in metrics["capabilities"]
        assert metrics["model_provider"] == "openai"
        assert metrics["model_name"] == "gpt-4" 