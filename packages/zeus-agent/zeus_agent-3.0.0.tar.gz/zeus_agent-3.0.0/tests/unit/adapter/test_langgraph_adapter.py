"""
LangGraph适配器单元测试
测试LangGraph适配器的各项功能，包括A2A协议集成
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 导入测试目标
from layers.adapter.langgraph.adapter import (
    LangGraphAdapter, 
    LangGraphWorkflow, 
    LangGraphNode,
    LangGraphState,
    LANGGRAPH_AVAILABLE
)
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from layers.framework.abstractions.context import UniversalContext
from layers.adapter.base import AdapterError, AdapterInitializationError


class TestLangGraphState:
    """LangGraph状态测试类"""
    
    def test_state_initialization(self):
        """测试状态初始化"""
        # 测试默认初始化
        state = LangGraphState()
        assert state.state == {}
        assert state.messages == []
        assert "created_at" in state.metadata
        assert state.metadata["step_count"] == 0
        
        # 测试带初始状态的初始化
        initial_state = {"key": "value"}
        state = LangGraphState(initial_state)
        assert state.state == initial_state
    
    def test_state_update(self):
        """测试状态更新"""
        state = LangGraphState()
        initial_step_count = state.metadata["step_count"]
        
        updates = {"new_key": "new_value", "count": 42}
        state.update(updates)
        
        assert state.state["new_key"] == "new_value"
        assert state.state["count"] == 42
        assert state.metadata["step_count"] == initial_step_count + 1
    
    def test_add_message(self):
        """测试添加消息"""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langchain_core.messages import HumanMessage
        
        state = LangGraphState()
        message = HumanMessage(content="Test message")
        
        state.add_message(message)
        assert len(state.messages) == 1
        assert state.messages[0] == message
    
    def test_get_state(self):
        """测试获取完整状态"""
        state = LangGraphState({"initial": "data"})
        full_state = state.get_state()
        
        assert "state" in full_state
        assert "messages" in full_state
        assert "metadata" in full_state
        assert full_state["state"]["initial"] == "data"


class TestLangGraphNode:
    """LangGraph节点测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.test_func = Mock(return_value={"result": "test"})
        self.node = LangGraphNode("test_node", self.test_func, "test_type")
    
    def test_node_initialization(self):
        """测试节点初始化"""
        assert self.node.node_id == "test_node"
        assert self.node.node_func == self.test_func
        assert self.node.node_type == "test_type"
        assert self.node.execution_count == 0
        assert self.node.a2a_profile is not None
    
    @pytest.mark.asyncio
    async def test_node_execution(self):
        """测试节点执行"""
        state = LangGraphState({"input": "test"})
        
        result = await self.node.execute(state)
        
        assert result == {"result": "test"}
        assert self.node.execution_count == 1
        assert self.node.last_execution_time is not None
        self.test_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_node_execution_with_async_function(self):
        """测试异步函数节点执行"""
        async def async_func(state, config):
            return {"async_result": "success"}
        
        async_node = LangGraphNode("async_node", async_func, "async")
        state = LangGraphState()
        
        result = await async_node.execute(state)
        
        assert result == {"async_result": "success"}
        assert async_node.execution_count == 1
    
    @pytest.mark.asyncio
    async def test_node_execution_error(self):
        """测试节点执行错误"""
        error_func = Mock(side_effect=Exception("Test error"))
        error_node = LangGraphNode("error_node", error_func, "error")
        state = LangGraphState()
        
        with pytest.raises(Exception):
            await error_node.execute(state)


class TestLangGraphWorkflow:
    """LangGraph工作流测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.adapter = Mock()
        self.workflow = LangGraphWorkflow("test_workflow", self.adapter)
    
    def test_workflow_initialization(self):
        """测试工作流初始化"""
        assert self.workflow.workflow_id == "test_workflow"
        assert self.workflow.adapter == self.adapter
        assert len(self.workflow.nodes) == 0
        assert len(self.workflow.edges) == 0
        assert len(self.workflow.conditional_edges) == 0
    
    def test_add_node(self):
        """测试添加节点"""
        test_func = Mock()
        
        self.workflow.add_node("node1", test_func, "test")
        
        assert "node1" in self.workflow.nodes
        assert self.workflow.nodes["node1"].node_func == test_func
        assert self.workflow.nodes["node1"].node_type == "test"
    
    def test_add_edge(self):
        """测试添加边"""
        self.workflow.add_edge("node1", "node2")
        
        assert ("node1", "node2") in self.workflow.edges
    
    def test_add_conditional_edge(self):
        """测试添加条件边"""
        condition_func = Mock()
        edge_map = {"true": "node2", "false": "node3"}
        
        self.workflow.add_conditional_edge("node1", condition_func, edge_map)
        
        assert len(self.workflow.conditional_edges) == 1
        cond_edge = self.workflow.conditional_edges[0]
        assert cond_edge["from_node"] == "node1"
        assert cond_edge["condition"] == condition_func
        assert cond_edge["edge_map"] == edge_map
    
    def test_set_entry_point(self):
        """测试设置入口点"""
        self.workflow.set_entry_point("start_node")
        
        assert self.workflow.entry_point == "start_node"
    
    def test_get_workflow_status(self):
        """测试获取工作流状态"""
        # 添加一些节点和边
        self.workflow.add_node("node1", Mock(), "test")
        self.workflow.add_edge("node1", "node2")
        
        status = self.workflow.get_workflow_status()
        
        assert status["workflow_id"] == "test_workflow"
        assert status["nodes_count"] == 1
        assert status["edges_count"] == 1
        assert status["conditional_edges_count"] == 0
        assert status["compiled"] is False
        assert "nodes" in status
    
    @patch('layers.adapter.langgraph.adapter.StateGraph')
    def test_compile_workflow(self, mock_state_graph):
        """测试工作流编译"""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock StateGraph
        mock_graph = Mock()
        mock_state_graph.return_value = mock_graph
        mock_graph.compile.return_value = Mock()
        
        # 添加节点和边
        self.workflow.add_node("node1", Mock(), "test")
        self.workflow.add_edge("node1", "node2")
        self.workflow.set_entry_point("node1")
        
        result = self.workflow.compile()
        
        assert result is True
        mock_state_graph.assert_called_once()
        mock_graph.add_node.assert_called()
        mock_graph.add_edge.assert_called_with("node1", "node2")
        mock_graph.set_entry_point.assert_called_with("node1")
        mock_graph.compile.assert_called_once()


class TestLangGraphAdapter:
    """LangGraph适配器测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.adapter = None
        if LANGGRAPH_AVAILABLE:
            try:
                self.adapter = LangGraphAdapter("test_langgraph")
            except Exception:
                self.adapter = None
    
    def test_adapter_initialization(self):
        """测试适配器初始化"""
        if not LANGGRAPH_AVAILABLE:
            # 测试LangGraph不可用时的错误处理
            with pytest.raises(AdapterInitializationError):
                LangGraphAdapter("test")
        else:
            # 测试正常初始化
            adapter = LangGraphAdapter("test_adapter")
            assert adapter.name == "test_adapter"
            assert hasattr(adapter, 'workflows')
            assert hasattr(adapter, 'a2a_adapter')
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """测试适配器初始化"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        config = {
            "default_llm": {
                "model": "gpt-4",
                "temperature": 0.7
            },
            "global_state": {
                "session_id": "test"
            }
        }
        
        await self.adapter.initialize(config)
        
        assert self.adapter.is_initialized
        assert self.adapter.status.value == "ready"
        assert "default" in self.adapter.llm_configs
        assert self.adapter.global_state["session_id"] == "test"
    
    def test_get_capabilities(self):
        """测试获取适配器能力"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        capabilities = self.adapter.get_capabilities()
        
        assert len(capabilities) > 0
        from layers.adapter.base import AdapterCapability
        assert AdapterCapability.WORKFLOW_ORCHESTRATION in capabilities
    
    @pytest.mark.asyncio
    async def test_create_agent_simple_workflow(self):
        """测试创建简单工作流"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        await self.adapter.initialize({})
        
        workflow_config = {
            "workflow_id": "test_workflow",
            "nodes": [
                {
                    "node_id": "node1",
                    "type": "function",
                    "processing": "test"
                }
            ],
            "edges": [],
            "entry_point": "node1"
        }
        
        workflow_id = await self.adapter.create_agent(workflow_config)
        
        assert workflow_id == "test_workflow"
        assert workflow_id in self.adapter.workflows
        assert len(self.adapter.workflows[workflow_id].nodes) == 1
    
    @pytest.mark.asyncio
    async def test_create_team(self):
        """测试创建团队（工作流组合）"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        await self.adapter.initialize({})
        
        # 先创建两个工作流
        workflow1_config = {
            "workflow_id": "workflow1",
            "nodes": [{"node_id": "node1", "type": "function"}],
            "entry_point": "node1"
        }
        workflow2_config = {
            "workflow_id": "workflow2", 
            "nodes": [{"node_id": "node2", "type": "function"}],
            "entry_point": "node2"
        }
        
        await self.adapter.create_agent(workflow1_config)
        await self.adapter.create_agent(workflow2_config)
        
        # 创建团队
        team_config = {
            "team_id": "test_team",
            "workflow_ids": ["workflow1", "workflow2"],
            "connections": [{"from": "workflow_0", "to": "workflow_1"}]
        }
        
        team_id = await self.adapter.create_team(team_config)
        
        assert team_id == "test_team"
        assert team_id in self.adapter.workflows
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        await self.adapter.initialize({})
        
        health_status = await self.adapter.health_check()
        
        assert "adapter_name" in health_status
        assert "health" in health_status
        assert "langgraph_available" in health_status
        assert health_status["langgraph_available"] == LANGGRAPH_AVAILABLE
    
    @pytest.mark.asyncio
    async def test_execute_chat_task(self):
        """测试执行聊天任务"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        await self.adapter.initialize({})
        
        # 创建聊天任务
        task = UniversalTask(
            content="Hello, how are you?",
            task_type=TaskType.CHAT,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={},
            task_id="chat_test"
        )
        
        context = UniversalContext({'user_id': 'test_user'})
        
        # 执行任务
        result = await self.adapter.execute_task(task, context)
        
        assert result.success
        assert "reply" in result.data
        assert result.data["workflow_id"] == "chat_workflow"
    
    @pytest.mark.asyncio
    async def test_execute_workflow_task(self):
        """测试执行工作流任务"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        await self.adapter.initialize({})
        
        # 先创建一个工作流
        workflow_config = {
            "workflow_id": "test_workflow",
            "nodes": [
                {
                    "node_id": "node1",
                    "type": "function",
                    "processing": "test"
                }
            ],
            "entry_point": "node1"
        }
        
        await self.adapter.create_agent(workflow_config)
        
        # 创建工作流任务
        task = UniversalTask(
            content="Execute workflow task",
            task_type=TaskType.WORKFLOW_ORCHESTRATION,
            priority=TaskPriority.HIGH,
            requirements=TaskRequirements(),
            context={'workflow_id': 'test_workflow'},
            task_id="workflow_test"
        )
        
        context = UniversalContext({'user_id': 'test_user'})
        
        # 执行任务
        result = await self.adapter.execute_task(task, context)
        
        assert result.success
        assert "workflow_result" in result.data
        assert result.data["workflow_id"] == "test_workflow"
    
    @pytest.mark.asyncio
    async def test_execute_task_adapter_not_ready(self):
        """测试适配器未就绪时执行任务"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        # 不初始化适配器
        task = UniversalTask(
            content="Test task",
            task_type=TaskType.CHAT,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={},
            task_id="test"
        )
        
        context = UniversalContext({})
        
        result = await self.adapter.execute_task(task, context)
        
        assert not result.success
        assert "not ready" in result.error.lower()
    
    def test_get_workflow_status(self):
        """测试获取工作流状态"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        # 测试不存在的工作流
        status = self.adapter.get_workflow_status("nonexistent")
        assert status["status"] == "not_found"
    
    def test_get_adapter_status(self):
        """测试获取适配器状态"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        status = self.adapter.get_adapter_status()
        
        assert status["adapter_name"] == "test_langgraph"
        assert status["langgraph_available"] == LANGGRAPH_AVAILABLE
        assert "workflows_count" in status
        assert "a2a_integration" in status
    
    def test_create_node_functions(self):
        """测试创建节点函数"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        # 测试LLM节点
        llm_config = {"type": "llm", "prompt": "Test prompt"}
        llm_func = self.adapter._create_node_function(llm_config)
        assert callable(llm_func)
        
        # 测试工具节点
        tool_config = {"type": "tool", "tool_name": "test_tool"}
        tool_func = self.adapter._create_node_function(tool_config)
        assert callable(tool_func)
        
        # 测试条件节点
        condition_config = {"type": "condition", "condition": "true"}
        condition_func = self.adapter._create_node_function(condition_config)
        assert callable(condition_func)
        
        # 测试通用节点
        generic_config = {"type": "function", "node_id": "test"}
        generic_func = self.adapter._create_node_function(generic_config)
        assert callable(generic_func)
    
    def test_create_condition_function(self):
        """测试创建条件函数"""
        if not self.adapter:
            pytest.skip("LangGraph not available")
        
        condition_config = {"type": "simple", "default_path": "next"}
        condition_func = self.adapter._create_condition_function(condition_config)
        
        assert callable(condition_func)
        result = condition_func({"test": "state"})
        assert result == "next"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 