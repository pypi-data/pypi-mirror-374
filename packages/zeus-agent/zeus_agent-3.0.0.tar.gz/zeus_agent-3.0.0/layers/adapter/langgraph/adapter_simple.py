"""
LangGraph适配器 - 简化版本
与ADC 8层架构和A2A协议集成的LangGraph框架适配器

这个版本专注于核心功能，处理LangGraph依赖问题
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# LangGraph导入处理
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_core.runnables import RunnableConfig
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available. Install with: pip install langgraph")

# ADC架构导入
from ...framework.abstractions.task import UniversalTask, TaskType
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult
from ...framework.abstractions.a2a_protocol import (
    A2AAgentProfile,
    A2ACapabilityType,
    create_a2a_capability,
    create_a2a_agent_profile
)
from ...framework.abstractions.layer_communication import LayerName
from ..base import BaseAdapter, AdapterCapability, AdapterError, AdapterInitializationError

logger = logging.getLogger(__name__)


# Mock classes for when LangGraph is not available
class MockMessage:
    """Mock message class"""
    def __init__(self, content: str):
        self.content = content


class MockHumanMessage(MockMessage):
    """Mock human message"""
    pass


class MockAIMessage(MockMessage):
    """Mock AI message"""
    pass


class MockA2AAdapter:
    """Mock A2A adapter for simplified version"""
    
    def __init__(self, layer_name: LayerName):
        self.layer_name = layer_name
        self.registered_agents = []
        self.logger = logging.getLogger(f"MockA2A.{layer_name.value}")
    
    def register_agent(self, profile: A2AAgentProfile):
        """注册Agent"""
        self.registered_agents.append(profile.agent_id)
        self.logger.info(f"Registered agent: {profile.agent_id}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        return {
            "layer_name": self.layer_name.value,
            "registered_agents": len(self.registered_agents),
            "agents": self.registered_agents,
            "status": "active"
        }


class LangGraphWorkflowSimple:
    """简化的LangGraph工作流"""
    
    def __init__(self, workflow_id: str, adapter_instance):
        self.workflow_id = workflow_id
        self.adapter = adapter_instance
        self.nodes = {}
        self.edges = []
        self.conditional_edges = []
        self.entry_point = None
        self.state = {}
        self.execution_count = 0
        
        logger.info(f"Created simplified LangGraph workflow: {workflow_id}")
    
    def add_node(self, node_id: str, node_func: Callable, node_type: str = "function"):
        """添加节点"""
        self.nodes[node_id] = {
            "id": node_id,
            "func": node_func,
            "type": node_type,
            "execution_count": 0,
            "a2a_profile": create_a2a_agent_profile(
                agent_id=f"{self.workflow_id}_{node_id}",
                agent_name=f"LangGraph Node: {node_id}",
                agent_type="langgraph_node",
                capabilities=[
                    create_a2a_capability(
                        A2ACapabilityType.WORKFLOW_MANAGEMENT,
                        version="1.0",
                        description=f"LangGraph workflow node: {node_type}"
                    )
                ]
            )
        }
        logger.info(f"Added node {node_id} to workflow {self.workflow_id}")
    
    def add_edge(self, from_node: str, to_node: str):
        """添加边"""
        self.edges.append((from_node, to_node))
        logger.info(f"Added edge {from_node} -> {to_node}")
    
    def add_conditional_edge(self, from_node: str, condition_func: Callable, edge_map: Dict[str, str]):
        """添加条件边"""
        self.conditional_edges.append({
            "from": from_node,
            "condition": condition_func,
            "map": edge_map
        })
        logger.info(f"Added conditional edge from {from_node}")
    
    def set_entry_point(self, node_id: str):
        """设置入口点"""
        self.entry_point = node_id
        logger.info(f"Set entry point to {node_id}")
    
    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        try:
            self.execution_count += 1
            self.state = initial_state.copy()
            
            logger.info(f"Executing workflow {self.workflow_id}")
            
            if not self.entry_point or self.entry_point not in self.nodes:
                raise AdapterError("No valid entry point")
            
            # 简单的顺序执行模拟
            current_node = self.entry_point
            visited_nodes = []
            
            while current_node and current_node not in visited_nodes:
                visited_nodes.append(current_node)
                
                if current_node in self.nodes:
                    node = self.nodes[current_node]
                    node["execution_count"] += 1
                    
                    # 执行节点函数
                    if asyncio.iscoroutinefunction(node["func"]):
                        result = await node["func"](self.state, None)
                    else:
                        result = await asyncio.to_thread(node["func"], self.state, None)
                    
                    # 更新状态
                    if isinstance(result, dict):
                        self.state.update(result)
                    
                    logger.info(f"Executed node {current_node}")
                
                # 查找下一个节点
                current_node = None
                for from_node, to_node in self.edges:
                    if from_node == visited_nodes[-1]:
                        current_node = to_node
                        break
                
                # 检查条件边
                for cond_edge in self.conditional_edges:
                    if cond_edge["from"] == visited_nodes[-1]:
                        condition_result = cond_edge["condition"](self.state)
                        if condition_result in cond_edge["map"]:
                            current_node = cond_edge["map"][condition_result]
                            break
            
            logger.info(f"Workflow {self.workflow_id} completed")
            return self.state
            
        except Exception as e:
            logger.error(f"Error executing workflow {self.workflow_id}: {e}")
            raise AdapterError(f"Workflow execution failed: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "workflow_id": self.workflow_id,
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "conditional_edges_count": len(self.conditional_edges),
            "execution_count": self.execution_count,
            "compiled": True,  # 简化版本总是"编译"的
            "nodes": {
                node_id: {
                    "type": node["type"],
                    "execution_count": node["execution_count"]
                } for node_id, node in self.nodes.items()
            }
        }


class LangGraphAdapterSimple(BaseAdapter):
    """
    LangGraph适配器 - 简化版本
    
    与BaseAdapter接口兼容，支持基本的LangGraph功能和A2A协议集成
    """
    
    def __init__(self, name: str = "langgraph_simple"):
        super().__init__(name)
        
        self.workflows: Dict[str, LangGraphWorkflowSimple] = {}
        self.llm_configs: Dict[str, Dict[str, Any]] = {}
        self.global_state: Dict[str, Any] = {}
        
        # 使用Mock A2A适配器
        self.a2a_adapter = MockA2AAdapter(LayerName.ADAPTER)
        
        logger.info("LangGraph simple adapter initialized")
    
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
        """创建工作流"""
        try:
            workflow_id = agent_config.get('workflow_id', f"workflow_{len(self.workflows)}")
            
            # 创建工作流
            workflow = LangGraphWorkflowSimple(workflow_id, self)
            
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
            
            self.workflows[workflow_id] = workflow
            
            # 注册A2A能力
            for node in workflow.nodes.values():
                self.a2a_adapter.register_agent(node["a2a_profile"])
            
            self.metadata.successful_operations += 1
            logger.info(f"Created LangGraph workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create workflow: {e}")
            raise AdapterError(f"Workflow creation failed: {str(e)}")
    
    async def create_team(self, team_config: Dict[str, Any]) -> str:
        """创建工作流组合（团队）"""
        try:
            team_id = team_config.get('team_id', f"team_{len(self.workflows)}")
            workflow_ids = team_config.get('workflow_ids', [])
            
            # 创建组合工作流
            combined_workflow = LangGraphWorkflowSimple(team_id, self)
            
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
            
            # 设置入口点
            if combined_workflow.nodes:
                first_node = list(combined_workflow.nodes.keys())[0]
                combined_workflow.set_entry_point(first_node)
            
            self.workflows[team_id] = combined_workflow
            
            self.metadata.successful_operations += 1
            logger.info(f"Created LangGraph team: {team_id}")
            return team_id
            
        except Exception as e:
            self.metadata.failed_operations += 1
            logger.error(f"Failed to create team: {e}")
            raise AdapterError(f"Team creation failed: {str(e)}")
    
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
            if self.is_initialized:
                status["health"] = "healthy"
                status["compiled_workflows"] = len(self.workflows)
            else:
                status["health"] = "unhealthy"
                status["issues"] = ["Not initialized"]
            
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
                "messages": [{"role": "user", "content": task.content}]
            }
            
            # 执行工作流
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "workflow_result": result,
                    "workflow_id": workflow_id,
                    "workflow_status": workflow.get_status()
                },
                metadata={"adapter": self.name, "task_type": "workflow"}
            )
            
        except Exception as e:
            logger.error(f"Error in workflow task: {e}")
            raise
    
    async def _execute_chat_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
        """执行聊天任务"""
        try:
            # 创建或使用默认聊天工作流
            if "chat_workflow" not in self.workflows:
                await self._create_default_chat_workflow()
            
            workflow = self.workflows["chat_workflow"]
            
            initial_state = {
                "messages": [{"role": "user", "content": task.content}],
                "context": context.data
            }
            
            result = await workflow.execute(initial_state)
            
            self.metadata.successful_operations += 1
            return UniversalResult(
                success=True,
                data={
                    "reply": result.get("response", "Chat response generated"),
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
            # 创建或使用默认代码工作流
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
                    "code_result": result.get("code", "Code generated"),
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
        node_id = node_config.get('node_id', 'generic')
        
        if node_type == 'llm':
            async def llm_node(state: Dict[str, Any], config) -> Dict[str, Any]:
                prompt = node_config.get('prompt', 'Process the input')
                messages = state.get("messages", [])
                
                # 模拟LLM调用
                response = f"LLM response for: {prompt}"
                
                return {
                    "response": response,
                    "messages": messages + [{"role": "assistant", "content": response}]
                }
            
            return llm_node
        
        elif node_type == 'tool':
            async def tool_node(state: Dict[str, Any], config) -> Dict[str, Any]:
                tool_name = node_config.get('tool_name', 'generic_tool')
                
                result = f"Tool {tool_name} executed"
                
                return {
                    "tool_result": result,
                    "tool_name": tool_name
                }
            
            return tool_node
        
        else:  # function type
            async def generic_node(state: Dict[str, Any], config) -> Dict[str, Any]:
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
                return condition_config.get('default_path', 'continue')
            else:
                return 'continue'
        
        return condition_func
    
    def _create_workflow_node_function(self, workflow: LangGraphWorkflowSimple) -> Callable:
        """为子工作流创建节点函数"""
        async def workflow_node(state: Dict[str, Any], config) -> Dict[str, Any]:
            result = await workflow.execute(state)
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
        
        return self.workflows[workflow_id].get_status()
    
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