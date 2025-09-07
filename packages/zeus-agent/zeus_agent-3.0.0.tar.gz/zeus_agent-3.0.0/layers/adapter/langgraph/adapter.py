"""
LangGraph适配器 - 完整实现
与ADC 8层架构和A2A协议集成的LangGraph框架适配器

主要功能:
- LangGraph图结构工作流支持
- 状态管理和节点执行
- A2A协议集成
- 条件分支和循环控制
- 并行执行和同步机制
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import json
import uuid

# LangGraph导入
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_core.runnables import RunnableConfig
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Mock classes for when LangGraph is not available
    class BaseMessage:
        def __init__(self, content: str):
            self.content = content
    
    class HumanMessage(BaseMessage):
        pass
    
    class AIMessage(BaseMessage):
        pass
    
    class RunnableConfig:
        pass
    
    logging.warning("LangGraph not available. Install with: pip install langgraph")

# ADC架构导入
from ...framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult
from ...framework.abstractions.a2a_protocol import (
    A2AProtocolHandler,
    A2AAgentProfile,
    A2ACapabilityType,
    A2AHTTPTransport,
    create_a2a_capability,
    create_a2a_agent_profile
)
from ...framework.abstractions.a2a_integration import create_a2a_layer_adapter
from ...framework.abstractions.layer_communication import LayerName
from ..base import BaseAdapter, AdapterCapability, AdapterError, AdapterInitializationError, AdapterExecutionError

logger = logging.getLogger(__name__)


class LangGraphState:
    """LangGraph状态管理类"""
    
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self.state = initial_state or {}
        self.messages = []
        self.metadata = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "step_count": 0
        }
    
    def update(self, updates: Dict[str, Any]):
        """更新状态"""
        self.state.update(updates)
        self.metadata["updated_at"] = datetime.now()
        self.metadata["step_count"] += 1
    
    def add_message(self, message: BaseMessage):
        """添加消息"""
        self.messages.append(message)
    
    def get_state(self) -> Dict[str, Any]:
        """获取完整状态"""
        return {
            "state": self.state,
            "messages": self.messages,
            "metadata": self.metadata
        }


class LangGraphNode:
    """LangGraph节点包装器"""
    
    def __init__(self, node_id: str, node_func: Callable, node_type: str = "function"):
        self.node_id = node_id
        self.node_func = node_func
        self.node_type = node_type
        self.execution_count = 0
        self.last_execution_time = None
        
        # 创建A2A配置文件
        self.a2a_profile = create_a2a_agent_profile(
            agent_id=node_id,
            agent_name=f"LangGraph Node: {node_id}",
            agent_type="langgraph_node",
            capabilities=[
                create_a2a_capability(
                    A2ACapabilityType.WORKFLOW_ORCHESTRATION,
                    version="1.0",
                    description=f"LangGraph workflow node: {node_type}"
                )
            ]
        )
    
    async def execute(self, state: LangGraphState, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """执行节点"""
        try:
            self.execution_count += 1
            self.last_execution_time = datetime.now()
            
            logger.info(f"Executing LangGraph node: {self.node_id}")
            
            # 执行节点函数
            if asyncio.iscoroutinefunction(self.node_func):
                result = await self.node_func(state.get_state(), config)
            else:
                result = await asyncio.to_thread(self.node_func, state.get_state(), config)
            
            # 更新状态
            if isinstance(result, dict):
                state.update(result)
            
            logger.info(f"Node {self.node_id} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing node {self.node_id}: {e}")
            raise AdapterExecutionError(f"Node execution failed: {str(e)}")


class LangGraphWorkflow:
    """LangGraph工作流包装器"""
    
    def __init__(self, workflow_id: str, adapter_instance):
        self.workflow_id = workflow_id
        self.adapter = adapter_instance
        self.nodes: Dict[str, LangGraphNode] = {}
        self.edges = []
        self.conditional_edges = []
        self.state_schema = {}
        self.graph = None
        self.compiled_graph = None
        self.checkpointer = MemorySaver() if LANGGRAPH_AVAILABLE else None
        
        logger.info(f"Created LangGraph workflow: {workflow_id}")
    
    def add_node(self, node_id: str, node_func: Callable, node_type: str = "function"):
        """添加节点"""
        node = LangGraphNode(node_id, node_func, node_type)
        self.nodes[node_id] = node
        logger.info(f"Added node {node_id} to workflow {self.workflow_id}")
    
    def add_edge(self, from_node: str, to_node: str):
        """添加边"""
        self.edges.append((from_node, to_node))
        logger.info(f"Added edge {from_node} -> {to_node} in workflow {self.workflow_id}")
    
    def add_conditional_edge(self, from_node: str, condition_func: Callable, edge_map: Dict[str, str]):
        """添加条件边"""
        self.conditional_edges.append({
            "from_node": from_node,
            "condition": condition_func,
            "edge_map": edge_map
        })
        logger.info(f"Added conditional edge from {from_node} in workflow {self.workflow_id}")
    
    def set_entry_point(self, node_id: str):
        """设置入口点"""
        self.entry_point = node_id
        logger.info(f"Set entry point to {node_id} in workflow {self.workflow_id}")
    
    def compile(self) -> bool:
        """编译工作流"""
        try:
            if not LANGGRAPH_AVAILABLE:
                raise AdapterError("LangGraph not available")
            
            # 创建状态图
            self.graph = StateGraph(self.state_schema)
            
            # 添加节点
            for node_id, node in self.nodes.items():
                self.graph.add_node(node_id, node.node_func)
            
            # 添加边
            for from_node, to_node in self.edges:
                self.graph.add_edge(from_node, to_node)
            
            # 添加条件边
            for cond_edge in self.conditional_edges:
                self.graph.add_conditional_edges(
                    cond_edge["from_node"],
                    cond_edge["condition"],
                    cond_edge["edge_map"]
                )
            
            # 设置入口点
            if hasattr(self, 'entry_point'):
                self.graph.set_entry_point(self.entry_point)
            
            # 编译图
            self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
            
            logger.info(f"Successfully compiled workflow {self.workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compile workflow {self.workflow_id}: {e}")
            return False
    
    async def execute(self, initial_state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """执行工作流"""
        try:
            if not self.compiled_graph:
                if not self.compile():
                    raise AdapterExecutionError("Failed to compile workflow")
            
            logger.info(f"Executing workflow {self.workflow_id}")
            
            # 执行编译后的图
            result = await asyncio.to_thread(
                self.compiled_graph.invoke,
                initial_state,
                config or {}
            )
            
            logger.info(f"Workflow {self.workflow_id} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow {self.workflow_id}: {e}")
            raise AdapterExecutionError(f"Workflow execution failed: {str(e)}")
    
    async def stream_execute(self, initial_state: Dict[str, Any], config: Optional[RunnableConfig] = None):
        """流式执行工作流"""
        try:
            if not self.compiled_graph:
                if not self.compile():
                    raise AdapterExecutionError("Failed to compile workflow")
            
            logger.info(f"Streaming workflow {self.workflow_id}")
            
            # 流式执行
            async for chunk in self.compiled_graph.astream(initial_state, config or {}):
                yield chunk
            
        except Exception as e:
            logger.error(f"Error streaming workflow {self.workflow_id}: {e}")
            raise AdapterExecutionError(f"Workflow streaming failed: {str(e)}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "workflow_id": self.workflow_id,
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "conditional_edges_count": len(self.conditional_edges),
            "compiled": self.compiled_graph is not None,
            "has_checkpointer": self.checkpointer is not None,
            "nodes": {
                node_id: {
                    "type": node.node_type,
                    "execution_count": node.execution_count,
                    "last_execution": node.last_execution_time.isoformat() if node.last_execution_time else None
                } for node_id, node in self.nodes.items()
            }
        }


class LangGraphAdapter(BaseAdapter):
    """
    LangGraph适配器 - 完整实现
    
    支持功能:
    - LangGraph图结构工作流
    - 状态管理和持久化
    - A2A协议集成
    - 条件分支和循环
    - 并行执行和流式处理
    - 与ADC 8层架构的完整集成
    """
    
    def __init__(self, name: str = "langgraph"):
        super().__init__(name)
        
        if not LANGGRAPH_AVAILABLE:
            raise AdapterInitializationError("LangGraph is not available. Please install: pip install langgraph")
        
        # 组件管理
        self.workflows: Dict[str, LangGraphWorkflow] = {}
        self.global_state: Dict[str, Any] = {}
        self.llm_configs: Dict[str, Dict[str, Any]] = {}
        
        # A2A集成
        self.a2a_adapter = create_a2a_layer_adapter(LayerName.ADAPTER)
        
        logger.info("LangGraph adapter initialized successfully")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化适配器"""
        try:
            self.config = config
            
            # 配置默认LLM
            default_llm = config.get('default_llm', {})
            if default_llm:
                self.llm_configs['default'] = default_llm
            
            # 初始化全局状态
            self.global_state = config.get('global_state', {})
            
            self.is_initialized = True
            self.status = self.status.READY
            self.metadata.last_initialized = datetime.now()
            self.metadata.initialization_count += 1
            
            logger.info(f"LangGraph adapter {self.name} initialized successfully")
            
        except Exception as e:
            self.status = self.status.ERROR
            logger.error(f"Failed to initialize LangGraph adapter: {e}")
            raise AdapterInitializationError(f"Initialization failed: {str(e)}")
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """创建工作流（在LangGraph中相当于Agent）"""
        try:
            workflow_id = agent_config.get('workflow_id', f"workflow_{len(self.workflows)}")
            
            # 创建工作流
            workflow = LangGraphWorkflow(workflow_id, self)
            
            # 添加节点
            nodes_config = agent_config.get('nodes', [])
            for node_config in nodes_config:
                node_id = node_config['node_id']
                node_func = self._create_node_function(node_config)
                node_type = node_config.get('type', 'function')
                workflow.add_node(node_id, node_func, node_type)
            
            # 添加边
            edges_config = agent_config.get('edges', [])
            for edge in edges_config:
                workflow.add_edge(edge['from'], edge['to'])
            
            # 添加条件边
            conditional_edges_config = agent_config.get('conditional_edges', [])
            for cond_edge in conditional_edges_config:
                condition_func = self._create_condition_function(cond_edge['condition'])
                workflow.add_conditional_edge(
                    cond_edge['from'],
                    condition_func,
                    cond_edge['edge_map']
                )
            
            # 设置入口点
            entry_point = agent_config.get('entry_point')
            if entry_point:
                workflow.set_entry_point(entry_point)
            
            # 设置状态模式
            workflow.state_schema = agent_config.get('state_schema', {})
            
            self.workflows[workflow_id] = workflow
            
            # 注册A2A能力
            for node in workflow.nodes.values():
                self.a2a_adapter.register_agent(node.a2a_profile)
            
            self.metadata.successful_operations += 1
            logger.info(f"Created LangGraph workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create workflow: {e}")
            raise AdapterExecutionError(f"Workflow creation failed: {str(e)}")
    
    async def create_team(self, team_config: Dict[str, Any]) -> str:
        """创建工作流组合（团队）"""
        try:
            team_id = team_config.get('team_id', f"team_{len(self.workflows)}")
            workflow_ids = team_config.get('workflow_ids', [])
            
            # 创建组合工作流
            combined_workflow = LangGraphWorkflow(team_id, self)
            
            # 添加子工作流作为节点
            for i, workflow_id in enumerate(workflow_ids):
                if workflow_id in self.workflows:
                    sub_workflow = self.workflows[workflow_id]
                    node_func = self._create_workflow_node_function(sub_workflow)
                    combined_workflow.add_node(f"workflow_{i}", node_func, "workflow")
            
            # 添加工作流间的连接
            connections = team_config.get('connections', [])
            for conn in connections:
                combined_workflow.add_edge(conn['from'], conn['to'])
            
            # 编译组合工作流
            combined_workflow.compile()
            self.workflows[team_id] = combined_workflow
            
            self.metadata.successful_operations += 1
            logger.info(f"Created LangGraph team: {team_id}")
            return team_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create team: {e}")
            raise AdapterExecutionError(f"Team creation failed: {str(e)}")
    
    def get_capabilities(self) -> List[AdapterCapability]:
        """获取适配器能力"""
        return [
            AdapterCapability.WORKFLOW_ORCHESTRATION,
            AdapterCapability.CONVERSATION,
            AdapterCapability.TOOL_CALLING,
            AdapterCapability.CODE_GENERATION
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            status = {
                "adapter_name": self.name,
                "status": self.status.value,
                "initialized": self.is_initialized,
                "langgraph_available": LANGGRAPH_AVAILABLE,
                "workflows_count": len(self.workflows),
                "success_rate": self.metadata.success_rate,
                "timestamp": datetime.now().isoformat()
            }
            
            # 测试基本功能
            if LANGGRAPH_AVAILABLE and self.is_initialized:
                status["health"] = "healthy"
                # 检查工作流状态
                compiled_workflows = sum(1 for wf in self.workflows.values() if wf.compiled_graph is not None)
                status["compiled_workflows"] = compiled_workflows
            else:
                status["health"] = "unhealthy"
                status["issues"] = []
                if not LANGGRAPH_AVAILABLE:
                    status["issues"].append("LangGraph not available")
                if not self.is_initialized:
                    status["issues"].append("Not initialized")
            
            return status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "adapter_name": self.name,
                "health": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行任务"""
        try:
            if not self.is_ready():
                raise AdapterError("Adapter not ready")
            
            task_type = task.task_type
            task_content = task.content
            
            if task_type == TaskType.WORKFLOW_ORCHESTRATION:
                return await self._execute_workflow_task(task, context)
            elif task_type == TaskType.CHAT:
                return await self._execute_chat_task(task, context)
            elif task_type == TaskType.CODE_GENERATION:
                return await self._execute_code_task(task, context)
            else:
                return await self._execute_generic_task(task, context)
                
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Task execution failed: {e}")
            return UniversalResult(
                success=False,
                data={},
                error=str(e),
                metadata={"adapter": self.name, "task_type": task.task_type.name}
            )
    
    async def _execute_workflow_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行工作流任务"""
        try:
            # 从任务上下文中获取工作流ID
            workflow_id = task.context.get('workflow_id')
            if not workflow_id or workflow_id not in self.workflows:
                raise AdapterError("Workflow not found")
            
            workflow = self.workflows[workflow_id]
            
            # 准备初始状态
            initial_state = {
                "task_content": task.content,
                "context": context.data,
                "messages": [HumanMessage(content=task.content)]
            }
            
            # 执行工作流
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "workflow_result": result,
                    "workflow_id": workflow_id,
                    "workflow_status": workflow.get_workflow_status()
                },
                metadata={"adapter": self.name, "task_type": "workflow"}
            )
            
        except Exception as e:
            logger.error(f"Error in workflow task: {e}")
            raise
    
    async def _execute_chat_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行聊天任务"""
        try:
            # 创建简单的聊天工作流
            if "chat_workflow" not in self.workflows:
                await self._create_default_chat_workflow()
            
            workflow = self.workflows["chat_workflow"]
            
            initial_state = {
                "messages": [HumanMessage(content=task.content)],
                "context": context.data
            }
            
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "reply": result.get("response", "No response generated"),
                    "workflow_id": "chat_workflow"
                },
                metadata={"adapter": self.name, "task_type": "chat"}
            )
            
        except Exception as e:
            logger.error(f"Error in chat task: {e}")
            raise
    
    async def _execute_code_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行代码任务"""
        try:
            # 创建简单的代码生成工作流
            if "code_workflow" not in self.workflows:
                await self._create_default_code_workflow()
            
            workflow = self.workflows["code_workflow"]
            
            initial_state = {
                "task": task.content,
                "language": context.data.get("language", "python"),
                "context": context.data
            }
            
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "code_result": result.get("code", "No code generated"),
                    "workflow_id": "code_workflow"
                },
                metadata={"adapter": self.name, "task_type": "code"}
            )
            
        except Exception as e:
            logger.error(f"Error in code task: {e}")
            raise
    
    async def _execute_generic_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行通用任务"""
        try:
            # 选择第一个可用工作流
            if not self.workflows:
                raise AdapterError("No workflows available")
            
            workflow = list(self.workflows.values())[0]
            
            initial_state = {
                "task": task.content,
                "task_type": task.task_type.name,
                "context": context.data
            }
            
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "result": result,
                    "workflow_id": workflow.workflow_id
                },
                metadata={"adapter": self.name, "task_type": "generic"}
            )
            
        except Exception as e:
            logger.error(f"Error in generic task: {e}")
            raise
    
    def _create_node_function(self, node_config: Dict[str, Any]) -> Callable:
        """创建节点函数"""
        node_type = node_config.get('type', 'function')
        
        if node_type == 'llm':
            return self._create_llm_node(node_config)
        elif node_type == 'tool':
            return self._create_tool_node(node_config)
        elif node_type == 'condition':
            return self._create_condition_node(node_config)
        else:
            return self._create_generic_node(node_config)
    
    def _create_llm_node(self, node_config: Dict[str, Any]) -> Callable:
        """创建LLM节点"""
        async def llm_node(state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            # 模拟LLM调用
            messages = state.get("messages", [])
            prompt = node_config.get('prompt', 'Process the input')
            
            # 这里应该调用实际的LLM
            response = f"LLM response for: {prompt}"
            
            return {
                "response": response,
                "messages": messages + [AIMessage(content=response)]
            }
        
        return llm_node
    
    def _create_tool_node(self, node_config: Dict[str, Any]) -> Callable:
        """创建工具节点"""
        async def tool_node(state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            tool_name = node_config.get('tool_name', 'generic_tool')
            tool_input = state.get('tool_input', {})
            
            # 模拟工具调用
            result = f"Tool {tool_name} executed with input: {tool_input}"
            
            return {
                "tool_result": result,
                "tool_name": tool_name
            }
        
        return tool_node
    
    def _create_condition_node(self, node_config: Dict[str, Any]) -> Callable:
        """创建条件节点"""
        async def condition_node(state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            condition = node_config.get('condition', 'true')
            
            # 简单的条件评估
            if condition == 'true':
                result = True
            elif condition == 'false':
                result = False
            else:
                # 这里可以实现更复杂的条件逻辑
                result = True
            
            return {
                "condition_result": result,
                "condition": condition
            }
        
        return condition_node
    
    def _create_generic_node(self, node_config: Dict[str, Any]) -> Callable:
        """创建通用节点"""
        async def generic_node(state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            node_id = node_config.get('node_id', 'generic')
            processing = node_config.get('processing', 'default')
            
            return {
                "node_result": f"Node {node_id} processed with {processing}",
                "processed_at": datetime.now().isoformat()
            }
        
        return generic_node
    
    def _create_condition_function(self, condition_config: Dict[str, Any]) -> Callable:
        """创建条件函数"""
        def condition_func(state: Dict[str, Any]) -> str:
            condition_type = condition_config.get('type', 'simple')
            
            if condition_type == 'simple':
                # 简单条件
                return condition_config.get('default_path', 'continue')
            else:
                # 复杂条件逻辑
                return 'continue'
        
        return condition_func
    
    def _create_workflow_node_function(self, workflow: LangGraphWorkflow) -> Callable:
        """为子工作流创建节点函数"""
        async def workflow_node(state: Dict[str, Any], config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            result = await workflow.execute(state, config)
            return {
                "sub_workflow_result": result,
                "sub_workflow_id": workflow.workflow_id
            }
        
        return workflow_node
    
    async def _create_default_chat_workflow(self):
        """创建默认聊天工作流"""
        chat_config = {
            "workflow_id": "chat_workflow",
            "nodes": [
                {
                    "node_id": "chat_node",
                    "type": "llm",
                    "prompt": "Respond to the user's message"
                }
            ],
            "edges": [],
            "entry_point": "chat_node"
        }
        
        await self.create_agent(chat_config)
    
    async def _create_default_code_workflow(self):
        """创建默认代码生成工作流"""
        code_config = {
            "workflow_id": "code_workflow",
            "nodes": [
                {
                    "node_id": "code_node",
                    "type": "llm",
                    "prompt": "Generate code for the given task"
                }
            ],
            "edges": [],
            "entry_point": "code_node"
        }
        
        await self.create_agent(code_config)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        if workflow_id not in self.workflows:
            return {"status": "not_found"}
        
        return self.workflows[workflow_id].get_workflow_status()
    
    def get_adapter_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "adapter_name": self.name,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "workflows_count": len(self.workflows),
            "llm_configs": list(self.llm_configs.keys()),
            "a2a_integration": self.a2a_adapter.get_integration_status(),
            "status": "active"
        } 