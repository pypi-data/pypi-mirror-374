"""
Workflow Engine
工作流引擎，支持复杂的多步骤任务编排和执行
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json

from ...framework.abstractions.agent import UniversalAgent
from ...framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult, ResultStatus

logger = logging.getLogger(__name__)


class WorkflowStepType(Enum):
    """工作流步骤类型"""
    AGENT_TASK = "agent_task"  # Agent任务
    CONDITION = "condition"  # 条件判断
    PARALLEL = "parallel"  # 并行执行
    LOOP = "loop"  # 循环执行
    DELAY = "delay"  # 延迟
    WEBHOOK = "webhook"  # Webhook调用
    SCRIPT = "script"  # 脚本执行
    HUMAN_INPUT = "human_input"  # 人工输入


class WorkflowStatus(Enum):
    """工作流状态"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"


@dataclass
class WorkflowStep:
    """工作流步骤定义"""
    step_id: str
    name: str
    step_type: WorkflowStepType
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # 依赖的步骤ID
    conditions: List[Dict[str, Any]] = field(default_factory=list)  # 执行条件
    timeout: Optional[int] = None  # 超时时间（秒）
    retry_count: int = 0  # 重试次数
    max_retries: int = 3  # 最大重试次数
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepExecution:
    """步骤执行状态"""
    step_id: str
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[UniversalResult] = None
    error: Optional[str] = None
    retry_count: int = 0
    execution_log: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    global_config: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)


@dataclass
class WorkflowExecution:
    """工作流执行状态"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_executions: Dict[str, StepExecution] = field(default_factory=dict)
    context: UniversalContext = field(default_factory=UniversalContext)
    final_result: Optional[UniversalResult] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """
    工作流引擎
    
    支持复杂的多步骤任务编排和执行
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.agents: Dict[str, UniversalAgent] = {}
        self.step_handlers: Dict[WorkflowStepType, Callable] = {
            WorkflowStepType.AGENT_TASK: self._handle_agent_task,
            WorkflowStepType.CONDITION: self._handle_condition,
            WorkflowStepType.PARALLEL: self._handle_parallel,
            WorkflowStepType.LOOP: self._handle_loop,
            WorkflowStepType.DELAY: self._handle_delay,
            WorkflowStepType.WEBHOOK: self._handle_webhook,
            WorkflowStepType.SCRIPT: self._handle_script,
            WorkflowStepType.HUMAN_INPUT: self._handle_human_input,
        }
        self.running_executions: Set[str] = set()
    
    def register_agent(self, agent_id: str, agent: UniversalAgent) -> None:
        """注册Agent"""
        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id}")
    
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """注册工作流定义"""
        try:
            self.workflows[workflow.workflow_id] = workflow
            logger.info(f"Registered workflow: {workflow.name} ({workflow.workflow_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to register workflow {workflow.workflow_id}: {e}")
            return False
    
    async def start_workflow(self, workflow_id: str, task: UniversalTask) -> str:
        """启动工作流执行 - execute_workflow的别名"""
        # 从task创建初始上下文
        initial_context = UniversalContext(
            session_id=getattr(task, 'session_id', None),
            data=getattr(task, 'data', {}) or {}
        )
        return await self.execute_workflow(workflow_id, initial_context)
    
    async def wait_for_completion(self, execution_id: str, timeout: int = 60):
        """等待工作流执行完成"""
        import asyncio
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if execution_id in self.executions:
                execution = self.executions[execution_id]
                if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                    return execution
            await asyncio.sleep(0.1)
        
        # 超时，返回当前状态
        return self.executions.get(execution_id)
    
    def create_workflow(self, 
                       name: str, 
                       description: str = "",
                       workflow_id: Optional[str] = None) -> str:
        """创建工作流定义"""
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow: {name} ({workflow_id})")
        return workflow_id
    
    def add_step(self, 
                workflow_id: str,
                step_name: str,
                step_type: WorkflowStepType,
                config: Dict[str, Any],
                dependencies: List[str] = None,
                conditions: List[Dict[str, Any]] = None,
                step_id: Optional[str] = None) -> str:
        """添加工作流步骤"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if step_id is None:
            step_id = str(uuid.uuid4())
        
        step = WorkflowStep(
            step_id=step_id,
            name=step_name,
            step_type=step_type,
            config=config,
            dependencies=dependencies or [],
            conditions=conditions or []
        )
        
        self.workflows[workflow_id].steps.append(step)
        logger.info(f"Added step {step_name} to workflow {workflow_id}")
        return step_id
    
    def validate_workflow(self, workflow_id: str) -> List[str]:
        """验证工作流定义"""
        if workflow_id not in self.workflows:
            return ["Workflow not found"]
        
        workflow = self.workflows[workflow_id]
        errors = []
        
        if not workflow.steps:
            errors.append("Workflow has no steps")
            return errors
        
        step_ids = {step.step_id for step in workflow.steps}
        
        # 检查依赖关系
        for step in workflow.steps:
            for dep_id in step.dependencies:
                if dep_id not in step_ids:
                    errors.append(f"Step {step.name} depends on non-existent step {dep_id}")
        
        # 检查循环依赖
        if self._has_circular_dependencies(workflow.steps):
            errors.append("Workflow has circular dependencies")
        
        # 检查Agent存在性
        for step in workflow.steps:
            if step.step_type == WorkflowStepType.AGENT_TASK:
                agent_id = step.config.get("agent_id")
                if agent_id and agent_id not in self.agents:
                    errors.append(f"Step {step.name} references non-existent agent {agent_id}")
        
        return errors
    
    def _has_circular_dependencies(self, steps: List[WorkflowStep]) -> bool:
        """检查是否存在循环依赖"""
        step_deps = {step.step_id: set(step.dependencies) for step in steps}
        
        def has_cycle(step_id: str, visited: Set[str], path: Set[str]) -> bool:
            if step_id in path:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            path.add(step_id)
            
            for dep_id in step_deps.get(step_id, set()):
                if has_cycle(dep_id, visited, path):
                    return True
            
            path.remove(step_id)
            return False
        
        visited = set()
        for step_id in step_deps:
            if step_id not in visited:
                if has_cycle(step_id, visited, set()):
                    return True
        
        return False
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             initial_context: Optional[UniversalContext] = None,
                             execution_id: Optional[str] = None) -> str:
        """执行工作流"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # 验证工作流
        errors = self.validate_workflow(workflow_id)
        if errors:
            raise ValueError(f"Workflow validation failed: {errors}")
        
        if execution_id is None:
            execution_id = str(uuid.uuid4())
        
        # 创建执行实例
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            context=initial_context or UniversalContext()
        )
        
        workflow = self.workflows[workflow_id]
        
        # 初始化步骤执行状态
        for step in workflow.steps:
            execution.step_executions[step.step_id] = StepExecution(step_id=step.step_id)
        
        self.executions[execution_id] = execution
        self.running_executions.add(execution_id)
        
        try:
            logger.info(f"Starting workflow execution: {workflow.name} ({execution_id})")
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()
            
            # 执行工作流
            await self._execute_workflow_steps(execution, workflow)
            
            # 完成执行
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            
            # 生成最终结果
            execution.final_result = self._generate_final_result(execution, workflow)
            
            logger.info(f"Workflow execution completed: {execution_id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.error = str(e)
            logger.error(f"Workflow execution failed: {execution_id}, error: {e}")
            
        finally:
            self.running_executions.discard(execution_id)
        
        return execution_id
    
    async def _execute_workflow_steps(self, 
                                    execution: WorkflowExecution,
                                    workflow: WorkflowDefinition) -> None:
        """执行工作流步骤"""
        completed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # 找到可以执行的步骤
            ready_steps = []
            
            for step in workflow.steps:
                step_exec = execution.step_executions[step.step_id]
                
                if (step_exec.status == StepStatus.PENDING and 
                    all(dep_id in completed_steps for dep_id in step.dependencies)):
                    
                    # 检查执行条件
                    if self._check_step_conditions(step, execution.context):
                        ready_steps.append(step)
            
            if not ready_steps:
                # 检查是否有正在运行的步骤
                running_steps = [
                    step_id for step_id, step_exec in execution.step_executions.items()
                    if step_exec.status == StepStatus.RUNNING
                ]
                
                if not running_steps:
                    # 没有可执行的步骤，可能是条件不满足或者有错误
                    break
                
                # 等待正在运行的步骤完成
                await asyncio.sleep(0.1)
                continue
            
            # 执行准备好的步骤
            tasks = []
            for step in ready_steps:
                task = self._execute_single_step(step, execution, workflow)
                tasks.append((step.step_id, task))
            
            # 等待步骤完成
            for step_id, task in tasks:
                try:
                    await task
                    step_exec = execution.step_executions[step_id]
                    if step_exec.status == StepStatus.COMPLETED:
                        completed_steps.add(step_id)
                except Exception as e:
                    logger.error(f"Step {step_id} failed: {e}")
                    execution.step_executions[step_id].status = StepStatus.FAILED
                    execution.step_executions[step_id].error = str(e)
                    
                    # 根据配置决定是否继续执行
                    if not workflow.global_config.get("continue_on_error", False):
                        raise
    
    async def _execute_single_step(self, 
                                 step: WorkflowStep,
                                 execution: WorkflowExecution,
                                 workflow: WorkflowDefinition) -> None:
        """执行单个步骤"""
        step_exec = execution.step_executions[step.step_id]
        step_exec.status = StepStatus.RUNNING
        step_exec.start_time = datetime.now()
        
        try:
            # 获取步骤处理器
            handler = self.step_handlers.get(step.step_type)
            if not handler:
                raise ValueError(f"No handler for step type: {step.step_type}")
            
            # 执行步骤
            result = await handler(step, execution.context, step_exec)
            
            step_exec.result = result
            step_exec.status = StepStatus.COMPLETED
            step_exec.end_time = datetime.now()
            
            # 更新上下文
            if result and result.is_successful():
                execution.context.set(f"step_{step.step_id}_result", result.content)
                execution.context.set(f"step_{step.name}_result", result.content)
            
            logger.info(f"Step completed: {step.name} ({step.step_id})")
            
        except Exception as e:
            step_exec.status = StepStatus.FAILED
            step_exec.error = str(e)
            step_exec.end_time = datetime.now()
            
            logger.error(f"Step failed: {step.name} ({step.step_id}), error: {e}")
            
            # 重试逻辑
            if step_exec.retry_count < step.max_retries:
                step_exec.retry_count += 1
                step_exec.status = StepStatus.PENDING
                step_exec.execution_log.append(f"Retry {step_exec.retry_count}: {str(e)}")
                logger.info(f"Retrying step: {step.name} (attempt {step_exec.retry_count})")
            else:
                raise
    
    def _check_step_conditions(self, step: WorkflowStep, context: UniversalContext) -> bool:
        """检查步骤执行条件"""
        if not step.conditions:
            return True
        
        for condition in step.conditions:
            condition_type = condition.get("type", "always")
            
            if condition_type == "always":
                continue
            elif condition_type == "context_value":
                key = condition.get("key")
                expected_value = condition.get("value")
                operator = condition.get("operator", "equals")
                
                if not key:
                    continue
                
                actual_value = context.get(key)
                
                if operator == "equals" and actual_value != expected_value:
                    return False
                elif operator == "not_equals" and actual_value == expected_value:
                    return False
                elif operator == "exists" and not context.has(key):
                    return False
                elif operator == "not_exists" and context.has(key):
                    return False
            elif condition_type == "previous_step_success":
                step_id = condition.get("step_id")
                if step_id:
                    result = context.get(f"step_{step_id}_result")
                    if not result:
                        return False
        
        return True
    
    async def _handle_agent_task(self, 
                               step: WorkflowStep,
                               context: UniversalContext,
                               step_exec: StepExecution) -> UniversalResult:
        """处理Agent任务步骤"""
        agent_id = step.config.get("agent_id")
        if not agent_id or agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        
        # 创建任务
        task_content = step.config.get("task_content", step.name)
        task_type_str = step.config.get("task_type", "CONVERSATION")
        task_type = TaskType[task_type_str] if hasattr(TaskType, task_type_str) else TaskType.CONVERSATION
        
        task = UniversalTask(
            content=task_content,
            task_type=task_type
        )
        
        # 增强上下文
        task_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
        task_context.set("workflow_step", step.name)
        task_context.set("step_config", step.config)
        
        # 执行任务
        result = await agent.execute(task, task_context)
        
        step_exec.execution_log.append(f"Agent {agent_id} executed task: {task_content}")
        
        return result
    
    async def _handle_condition(self, 
                              step: WorkflowStep,
                              context: UniversalContext,
                              step_exec: StepExecution) -> UniversalResult:
        """处理条件判断步骤"""
        condition_expr = step.config.get("expression", "true")
        
        # 简单的条件表达式评估
        # 在实际应用中，应该使用更安全的表达式评估器
        try:
            # 替换上下文变量
            import re
            def replace_var(match):
                var_name = match.group(1)
                return str(context.get(var_name, "None"))
            
            expr = re.sub(r'\{(\w+)\}', replace_var, condition_expr)
            
            # 评估表达式（这里使用简单的eval，生产环境应使用更安全的方法）
            result = eval(expr)
            
            step_exec.execution_log.append(f"Condition evaluated: {condition_expr} -> {result}")
            
            return UniversalResult(
                content={"condition_result": result, "expression": condition_expr},
                status=ResultStatus.SUCCESS
            )
            
        except Exception as e:
            return UniversalResult(
                content=f"Condition evaluation failed: {str(e)}",
                status=ResultStatus.ERROR
            )
    
    async def _handle_parallel(self, 
                             step: WorkflowStep,
                             context: UniversalContext,
                             step_exec: StepExecution) -> UniversalResult:
        """处理并行执行步骤"""
        parallel_steps = step.config.get("steps", [])
        
        if not parallel_steps:
            return UniversalResult(
                content="No parallel steps defined",
                status=ResultStatus.ERROR
            )
        
        tasks = []
        for parallel_step_config in parallel_steps:
            # 创建临时步骤
            temp_step = WorkflowStep(
                step_id=str(uuid.uuid4()),
                name=parallel_step_config.get("name", "Parallel Step"),
                step_type=WorkflowStepType[parallel_step_config.get("type", "AGENT_TASK")],
                config=parallel_step_config.get("config", {})
            )
            
            # 执行步骤
            task = self._execute_parallel_substep(temp_step, context)
            tasks.append(task)
        
        # 等待所有并行任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({"step_index": i, "error": str(result)})
            elif isinstance(result, UniversalResult) and result.is_successful():
                successful_results.append({"step_index": i, "result": result.content})
            else:
                failed_results.append({"step_index": i, "error": "Unknown error"})
        
        step_exec.execution_log.append(f"Parallel execution: {len(successful_results)} succeeded, {len(failed_results)} failed")
        
        return UniversalResult(
            content={
                "successful_results": successful_results,
                "failed_results": failed_results,
                "total_steps": len(parallel_steps)
            },
            status=ResultStatus.SUCCESS if successful_results else ResultStatus.ERROR
        )
    
    async def _execute_parallel_substep(self, step: WorkflowStep, context: UniversalContext) -> UniversalResult:
        """执行并行子步骤"""
        handler = self.step_handlers.get(step.step_type)
        if not handler:
            raise ValueError(f"No handler for step type: {step.step_type}")
        
        temp_step_exec = StepExecution(step_id=step.step_id)
        return await handler(step, context, temp_step_exec)
    
    async def _handle_loop(self, 
                         step: WorkflowStep,
                         context: UniversalContext,
                         step_exec: StepExecution) -> UniversalResult:
        """处理循环执行步骤"""
        loop_config = step.config
        max_iterations = loop_config.get("max_iterations", 10)
        condition = loop_config.get("condition", "false")
        loop_step_config = loop_config.get("step", {})
        
        results = []
        iteration = 0
        
        while iteration < max_iterations:
            # 检查循环条件
            if not self._evaluate_loop_condition(condition, context, iteration):
                break
            
            # 执行循环步骤
            temp_step = WorkflowStep(
                step_id=f"{step.step_id}_iter_{iteration}",
                name=f"{step.name} (Iteration {iteration})",
                step_type=WorkflowStepType[loop_step_config.get("type", "AGENT_TASK")],
                config=loop_step_config.get("config", {})
            )
            
            try:
                result = await self._execute_parallel_substep(temp_step, context)
                results.append({
                    "iteration": iteration,
                    "result": result.content if result.is_successful() else None,
                    "success": result.is_successful()
                })
                
                # 更新循环上下文
                context.set(f"loop_iteration", iteration)
                context.set(f"loop_last_result", result.content if result.is_successful() else None)
                
            except Exception as e:
                results.append({
                    "iteration": iteration,
                    "error": str(e),
                    "success": False
                })
            
            iteration += 1
        
        step_exec.execution_log.append(f"Loop executed {iteration} iterations")
        
        return UniversalResult(
            content={
                "iterations": iteration,
                "results": results,
                "completed": iteration < max_iterations
            },
            status=ResultStatus.SUCCESS
        )
    
    def _evaluate_loop_condition(self, condition: str, context: UniversalContext, iteration: int) -> bool:
        """评估循环条件"""
        try:
            # 替换变量
            import re
            def replace_var(match):
                var_name = match.group(1)
                if var_name == "iteration":
                    return str(iteration)
                return str(context.get(var_name, "None"))
            
            expr = re.sub(r'\{(\w+)\}', replace_var, condition)
            return bool(eval(expr))
            
        except Exception:
            return False
    
    async def _handle_delay(self, 
                          step: WorkflowStep,
                          context: UniversalContext,
                          step_exec: StepExecution) -> UniversalResult:
        """处理延迟步骤"""
        delay_seconds = step.config.get("delay_seconds", 1)
        
        step_exec.execution_log.append(f"Delaying for {delay_seconds} seconds")
        await asyncio.sleep(delay_seconds)
        
        return UniversalResult(
            content=f"Delayed for {delay_seconds} seconds",
            status=ResultStatus.SUCCESS
        )
    
    async def _handle_webhook(self, 
                            step: WorkflowStep,
                            context: UniversalContext,
                            step_exec: StepExecution) -> UniversalResult:
        """处理Webhook调用步骤"""
        import aiohttp
        
        url = step.config.get("url")
        method = step.config.get("method", "POST").upper()
        headers = step.config.get("headers", {})
        data = step.config.get("data", {})
        
        if not url:
            return UniversalResult(
                content="Webhook URL not specified",
                status=ResultStatus.ERROR
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    response_data = await response.text()
                    
                    step_exec.execution_log.append(f"Webhook called: {method} {url}, status: {response.status}")
                    
                    return UniversalResult(
                        content={
                            "status_code": response.status,
                            "response": response_data,
                            "headers": dict(response.headers)
                        },
                        status=ResultStatus.SUCCESS if response.status < 400 else ResultStatus.ERROR
                    )
                    
        except Exception as e:
            return UniversalResult(
                content=f"Webhook call failed: {str(e)}",
                status=ResultStatus.ERROR
            )
    
    async def _handle_script(self, 
                           step: WorkflowStep,
                           context: UniversalContext,
                           step_exec: StepExecution) -> UniversalResult:
        """处理脚本执行步骤"""
        script_code = step.config.get("script", "")
        script_type = step.config.get("type", "python")
        
        if not script_code:
            return UniversalResult(
                content="No script code provided",
                status=ResultStatus.ERROR
            )
        
        if script_type != "python":
            return UniversalResult(
                content=f"Script type {script_type} not supported",
                status=ResultStatus.ERROR
            )
        
        try:
            # 创建受限的执行环境
            script_globals = {
                "context": context,
                "step_config": step.config,
                "__builtins__": {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "print": print,
                }
            }
            
            # 执行脚本
            exec(script_code, script_globals)
            
            # 获取返回值
            result_value = script_globals.get("result", "Script executed successfully")
            
            step_exec.execution_log.append(f"Script executed successfully")
            
            return UniversalResult(
                content=result_value,
                status=ResultStatus.SUCCESS
            )
            
        except Exception as e:
            return UniversalResult(
                content=f"Script execution failed: {str(e)}",
                status=ResultStatus.ERROR
            )
    
    async def _handle_human_input(self, 
                                step: WorkflowStep,
                                context: UniversalContext,
                                step_exec: StepExecution) -> UniversalResult:
        """处理人工输入步骤"""
        prompt = step.config.get("prompt", "Please provide input:")
        input_type = step.config.get("input_type", "text")
        timeout = step.config.get("timeout", 300)  # 5分钟超时
        
        step_exec.execution_log.append(f"Waiting for human input: {prompt}")
        
        # 在实际应用中，这里应该通过UI或其他方式获取人工输入
        # 目前返回一个占位符结果
        return UniversalResult(
            content={
                "prompt": prompt,
                "input_type": input_type,
                "status": "waiting_for_input",
                "message": "Human input step requires external interface"
            },
            status=ResultStatus.SUCCESS
        )
    
    def _generate_final_result(self, 
                             execution: WorkflowExecution,
                             workflow: WorkflowDefinition) -> UniversalResult:
        """生成最终结果"""
        successful_steps = [
            step_exec for step_exec in execution.step_executions.values()
            if step_exec.status == StepStatus.COMPLETED and step_exec.result and step_exec.result.is_successful()
        ]
        
        failed_steps = [
            step_exec for step_exec in execution.step_executions.values()
            if step_exec.status == StepStatus.FAILED
        ]
        
        final_content = {
            "workflow_name": workflow.name,
            "execution_id": execution.execution_id,
            "total_steps": len(workflow.steps),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "execution_time": (execution.end_time - execution.start_time).total_seconds() if execution.end_time and execution.start_time else 0,
            "step_results": {
                step_exec.step_id: step_exec.result.content if step_exec.result else None
                for step_exec in successful_steps
            }
        }
        
        return UniversalResult(
            content=final_content,
            status=ResultStatus.SUCCESS if not failed_steps else ResultStatus.PARTIAL_SUCCESS
        )
    
    def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """获取工作流定义"""
        return self.workflows.get(workflow_id)
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取执行状态"""
        return self.executions.get(execution_id)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """列出所有工作流"""
        return list(self.workflows.values())
    
    def list_executions(self, workflow_id: Optional[str] = None) -> List[WorkflowExecution]:
        """列出执行历史"""
        executions = list(self.executions.values())
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        return executions
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """取消执行"""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            self.running_executions.discard(execution_id)
            logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
        return False
    
    def export_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """导出工作流定义"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "config": step.config,
                    "dependencies": step.dependencies,
                    "conditions": step.conditions,
                    "timeout": step.timeout,
                    "max_retries": step.max_retries
                }
                for step in workflow.steps
            ],
            "global_config": workflow.global_config,
            "timeout": workflow.timeout,
            "tags": workflow.tags
        }
    
    def import_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """导入工作流定义"""
        workflow_id = workflow_data.get("workflow_id", str(uuid.uuid4()))
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=workflow_data["name"],
            description=workflow_data.get("description", ""),
            global_config=workflow_data.get("global_config", {}),
            timeout=workflow_data.get("timeout"),
            version=workflow_data.get("version", "1.0"),
            tags=workflow_data.get("tags", [])
        )
        
        # 导入步骤
        for step_data in workflow_data.get("steps", []):
            step = WorkflowStep(
                step_id=step_data["step_id"],
                name=step_data["name"],
                step_type=WorkflowStepType(step_data["step_type"]),
                config=step_data.get("config", {}),
                dependencies=step_data.get("dependencies", []),
                conditions=step_data.get("conditions", []),
                timeout=step_data.get("timeout"),
                max_retries=step_data.get("max_retries", 3)
            )
            workflow.steps.append(step)
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Imported workflow: {workflow.name} ({workflow_id})")
        
        return workflow_id 