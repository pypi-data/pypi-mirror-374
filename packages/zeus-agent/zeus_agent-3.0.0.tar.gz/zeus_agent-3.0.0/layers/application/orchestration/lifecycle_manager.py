"""
应用生命周期管理器 - Application Lifecycle Manager
负责应用的启动、停止、重启、监控和状态管理
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """生命周期状态枚举"""
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    RESTARTING = "restarting"
    MAINTENANCE = "maintenance"


class ProcessType(Enum):
    """进程类型枚举"""
    MAIN = "main"
    WORKER = "worker"
    BACKGROUND = "background"
    MONITOR = "monitor"


@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    process_type: ProcessType
    name: str
    command: str
    args: List[str]
    working_dir: str
    environment: Dict[str, str]
    start_time: datetime
    status: LifecycleState
    exit_code: Optional[int] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LifecycleConfig:
    """生命周期配置"""
    auto_restart: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    graceful_shutdown_timeout: int = 30
    health_check_interval: int = 60
    process_monitoring: bool = True
    log_rotation: bool = True
    backup_enabled: bool = False
    backup_interval: int = 3600


class ApplicationLifecycleManager:
    """应用生命周期管理器"""
    
    def __init__(self, config: LifecycleConfig):
        self.config = config
        self.processes: Dict[int, ProcessInfo] = {}
        self.process_types: Dict[ProcessType, List[int]] = {
            ProcessType.MAIN: [],
            ProcessType.WORKER: [],
            ProcessType.BACKGROUND: [],
            ProcessType.MONITOR: []
        }
        self.restart_counts: Dict[int, int] = {}
        self.state_handlers: Dict[LifecycleState, List[Callable]] = {}
        self.shutdown_handlers: List[Callable] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        
        # 注册信号处理器
        self._setup_signal_handlers()
        
        logger.info("Application Lifecycle Manager initialized")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, self._signal_handler)
        except Exception as e:
            logger.warning(f"Failed to setup signal handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"Received signal {signum}")
        if signum in (signal.SIGTERM, signal.SIGINT):
            asyncio.create_task(self.graceful_shutdown())
    
    async def start(self):
        """启动生命周期管理器"""
        try:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Application Lifecycle Manager started")
        except Exception as e:
            logger.error(f"Failed to start lifecycle manager: {e}")
    
    async def stop(self):
        """停止生命周期管理器"""
        try:
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # 停止所有进程
            await self.stop_all_processes()
            logger.info("Application Lifecycle Manager stopped")
        except Exception as e:
            logger.error(f"Failed to stop lifecycle manager: {e}")
    
    async def start_process(self, process_type: ProcessType, name: str, command: str, 
                          args: List[str] = None, working_dir: str = None, 
                          environment: Dict[str, str] = None) -> Optional[int]:
        """启动进程"""
        try:
            args = args or []
            working_dir = working_dir or os.getcwd()
            environment = environment or {}
            
            # 创建进程
            process = await asyncio.create_subprocess_exec(
                command, *args,
                cwd=working_dir,
                env={**os.environ, **environment},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 记录进程信息
            process_info = ProcessInfo(
                pid=process.pid,
                process_type=process_type,
                name=name,
                command=command,
                args=args,
                working_dir=working_dir,
                environment=environment,
                start_time=datetime.now(),
                status=LifecycleState.STARTING
            )
            
            self.processes[process.pid] = process_info
            self.process_types[process_type].append(process.pid)
            self.restart_counts[process.pid] = 0
            
            # 启动进程监控
            asyncio.create_task(self._monitor_process(process, process_info))
            
            logger.info(f"Started process: {name} (PID: {process.pid})")
            await self._notify_state_change(process_info, LifecycleState.STARTING)
            
            return process.pid
            
        except Exception as e:
            logger.error(f"Failed to start process {name}: {e}")
            return None
    
    async def stop_process(self, pid: int, force: bool = False) -> bool:
        """停止进程"""
        try:
            if pid not in self.processes:
                return False
            
            process_info = self.processes[pid]
            process_info.status = LifecycleState.STOPPING
            
            if force:
                # 强制终止
                os.kill(pid, signal.SIGKILL)
                process_info.status = LifecycleState.STOPPED
                logger.info(f"Force stopped process: {process_info.name} (PID: {pid})")
            else:
                # 优雅关闭
                os.kill(pid, signal.SIGTERM)
                
                # 等待进程结束
                try:
                    await asyncio.wait_for(self._wait_process_exit(pid), 
                                         timeout=self.config.graceful_shutdown_timeout)
                except asyncio.TimeoutError:
                    # 超时后强制终止
                    os.kill(pid, signal.SIGKILL)
                    logger.warning(f"Force killed process {pid} after timeout")
            
            await self._notify_state_change(process_info, LifecycleState.STOPPED)
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop process {pid}: {e}")
            return False
    
    async def restart_process(self, pid: int) -> bool:
        """重启进程"""
        try:
            if pid not in self.processes:
                return False
            
            process_info = self.processes[pid]
            process_info.status = LifecycleState.RESTARTING
            
            # 停止进程
            if await self.stop_process(pid):
                # 等待一段时间后重启
                await asyncio.sleep(self.config.restart_delay)
                
                # 重启进程
                new_pid = await self.start_process(
                    process_info.process_type,
                    process_info.name,
                    process_info.command,
                    process_info.args,
                    process_info.working_dir,
                    process_info.environment
                )
                
                if new_pid:
                    # 更新重启计数
                    self.restart_counts[new_pid] = self.restart_counts.get(pid, 0) + 1
                    
                    # 清理旧进程信息
                    del self.processes[pid]
                    self.process_types[process_info.process_type].remove(pid)
                    if pid in self.restart_counts:
                        del self.restart_counts[pid]
                    
                    logger.info(f"Restarted process: {process_info.name} (PID: {pid} -> {new_pid})")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart process {pid}: {e}")
            return False
    
    async def stop_all_processes(self):
        """停止所有进程"""
        try:
            pids = list(self.processes.keys())
            for pid in pids:
                await self.stop_process(pid, force=True)
        except Exception as e:
            logger.error(f"Failed to stop all processes: {e}")
    
    async def get_process_status(self, pid: int) -> Optional[Dict[str, Any]]:
        """获取进程状态"""
        try:
            if pid not in self.processes:
                return None
            
            process_info = self.processes[pid]
            return {
                "pid": pid,
                "name": process_info.name,
                "type": process_info.process_type.value,
                "status": process_info.status.value,
                "start_time": process_info.start_time.isoformat(),
                "exit_code": process_info.exit_code,
                "memory_usage": process_info.memory_usage,
                "cpu_usage": process_info.cpu_usage,
                "restart_count": self.restart_counts.get(pid, 0),
                "metadata": process_info.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get process status for {pid}: {e}")
            return None
    
    async def list_processes(self) -> List[Dict[str, Any]]:
        """列出所有进程"""
        try:
            processes = []
            for pid, process_info in self.processes.items():
                processes.append(await self.get_process_status(pid))
            return [p for p in processes if p is not None]
        except Exception as e:
            logger.error(f"Failed to list processes: {e}")
            return []
    
    async def add_state_handler(self, state: LifecycleState, handler: Callable):
        """添加状态变化处理器"""
        if state not in self.state_handlers:
            self.state_handlers[state] = []
        self.state_handlers[state].append(handler)
    
    async def add_shutdown_handler(self, handler: Callable):
        """添加关闭处理器"""
        self.shutdown_handlers.append(handler)
    
    async def graceful_shutdown(self):
        """优雅关闭"""
        try:
            logger.info("Starting graceful shutdown...")
            
            # 执行关闭处理器
            for handler in self.shutdown_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler()
                    else:
                        handler()
                except Exception as e:
                    logger.error(f"Shutdown handler error: {e}")
            
            # 停止所有进程
            await self.stop_all_processes()
            
            # 停止生命周期管理器
            await self.stop()
            
            logger.info("Graceful shutdown completed")
            self._shutdown_event.set()
            
        except Exception as e:
            logger.error(f"Graceful shutdown failed: {e}")
            sys.exit(1)
    
    async def wait_for_shutdown(self):
        """等待关闭完成"""
        await self._shutdown_event.wait()
    
    async def _monitor_process(self, process: asyncio.subprocess.Process, process_info: ProcessInfo):
        """监控进程"""
        try:
            # 等待进程结束
            exit_code = await process.wait()
            
            # 更新进程状态
            process_info.exit_code = exit_code
            process_info.status = LifecycleState.STOPPED
            
            # 从进程类型列表中移除
            if process.pid in self.process_types[process_info.process_type]:
                self.process_types[process_info.process_type].remove(process.pid)
            
            logger.info(f"Process {process_info.name} (PID: {process.pid}) exited with code {exit_code}")
            
            # 检查是否需要重启
            if (self.config.auto_restart and 
                process_info.process_type != ProcessType.MAIN and
                self.restart_counts.get(process.pid, 0) < self.config.max_restart_attempts):
                
                logger.info(f"Restarting process {process_info.name} (PID: {process.pid})")
                await self.restart_process(process.pid)
            else:
                # 清理进程信息
                if process.pid in self.processes:
                    del self.processes[process.pid]
                if process.pid in self.restart_counts:
                    del self.restart_counts[process.pid]
                
                await self._notify_state_change(process_info, LifecycleState.STOPPED)
            
        except Exception as e:
            logger.error(f"Process monitoring error for {process_info.name} (PID: {process.pid}): {e}")
            process_info.status = LifecycleState.ERROR
    
    async def _wait_process_exit(self, pid: int):
        """等待进程退出"""
        while pid in self.processes:
            await asyncio.sleep(0.1)
    
    async def _monitoring_loop(self):
        """监控循环"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        try:
            for pid in list(self.processes.keys()):
                await self._check_process_health(pid)
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    async def _check_process_health(self, pid: int):
        """检查进程健康状态"""
        try:
            if pid not in self.processes:
                return
            
            process_info = self.processes[pid]
            
            # 检查进程是否还在运行
            try:
                os.kill(pid, 0)  # 发送信号0检查进程是否存在
                process_info.status = LifecycleState.RUNNING
            except OSError:
                # 进程不存在
                process_info.status = LifecycleState.STOPPED
                logger.warning(f"Process {process_info.name} (PID: {pid}) is not running")
            
            # 这里可以添加更多的健康检查逻辑
            # 比如检查内存使用、CPU使用等
            
        except Exception as e:
            logger.error(f"Health check failed for process {pid}: {e}")
    
    async def _notify_state_change(self, process_info: ProcessInfo, new_state: LifecycleState):
        """通知状态变化"""
        if new_state in self.state_handlers:
            for handler in self.state_handlers[new_state]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(process_info)
                    else:
                        handler(process_info)
                except Exception as e:
                    logger.error(f"State handler error for {new_state}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            total_processes = len(self.processes)
            running_processes = sum(1 for p in self.processes.values() if p.status == LifecycleState.RUNNING)
            stopped_processes = sum(1 for p in self.processes.values() if p.status == LifecycleState.STOPPED)
            error_processes = sum(1 for p in self.processes.values() if p.status == LifecycleState.ERROR)
            
            process_type_counts = {}
            for process_type, pids in self.process_types.items():
                process_type_counts[process_type.value] = len(pids)
            
            return {
                "total_processes": total_processes,
                "running_processes": running_processes,
                "stopped_processes": stopped_processes,
                "error_processes": error_processes,
                "process_types": process_type_counts,
                "auto_restart": self.config.auto_restart,
                "max_restart_attempts": self.config.max_restart_attempts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "config": {
                "auto_restart": self.config.auto_restart,
                "max_restart_attempts": self.config.max_restart_attempts,
                "restart_delay": self.config.restart_delay,
                "graceful_shutdown_timeout": self.config.graceful_shutdown_timeout
            },
            "processes": [process_info.__dict__ for process_info in self.processes.values()],
            "process_types": {pt.value: pids for pt, pids in self.process_types.items()},
            "restart_counts": self.restart_counts
        } 