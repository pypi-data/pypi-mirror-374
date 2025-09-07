"""
应用编排器 - Application Orchestrator
负责应用的动态组装、配置和编排
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ...framework.abstractions.agent import UniversalAgent
from ...framework.abstractions.task import UniversalTask
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult

logger = logging.getLogger(__name__)


class ApplicationType(Enum):
    """应用类型枚举"""
    CLI = "cli"
    WEB = "web"
    API = "api"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    EMBEDDED = "embedded"
    BACKGROUND = "background"
    CUSTOM = "custom"


class ApplicationStatus(Enum):
    """应用状态枚举"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ApplicationConfig:
    """应用配置"""
    app_id: str
    name: str
    description: str
    app_type: ApplicationType
    version: str
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    health_check: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ApplicationInstance:
    """应用实例"""
    instance_id: str
    app_config: ApplicationConfig
    status: ApplicationStatus
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    health_score: float = 1.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class ApplicationOrchestrator:
    """应用编排器"""
    
    def __init__(self):
        self.applications: Dict[str, ApplicationConfig] = {}
        self.instances: Dict[str, ApplicationInstance] = {}
        self.running_instances: Dict[str, List[str]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        
        logger.info("Application Orchestrator initialized")
    
    async def register_application(self, config: ApplicationConfig) -> bool:
        """注册应用"""
        async with self._lock:
            try:
                # 处理应用类型
                if isinstance(config.app_type, str):
                    try:
                        config.app_type = ApplicationType(config.app_type)
                    except ValueError:
                        logger.warning(f"Unknown application type: {config.app_type}, using CUSTOM")
                        config.app_type = ApplicationType.CUSTOM
                
                # 确保所有必需字段都有默认值
                if not hasattr(config, 'environment') or config.environment is None:
                    config.environment = {}
                if not hasattr(config, 'resources') or config.resources is None:
                    config.resources = {}
                
                self.applications[config.app_id] = config
                self.running_instances[config.app_id] = []
                logger.info(f"Registered application: {config.name} ({config.app_id})")
                await self._notify_event("app_registered", config)
                return True
            except Exception as e:
                logger.error(f"Failed to register application {config.app_id}: {e}")
                return False
    
    async def unregister_application(self, app_id: str) -> bool:
        """注销应用"""
        async with self._lock:
            try:
                if app_id in self.applications:
                    # 停止所有运行中的实例
                    if app_id in self.running_instances:
                        for instance_id in self.running_instances[app_id]:
                            await self.stop_instance(instance_id)
                    
                    del self.applications[app_id]
                    if app_id in self.running_instances:
                        del self.running_instances[app_id]
                    
                    logger.info(f"Unregistered application: {app_id}")
                    await self._notify_event("app_unregistered", app_id)
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to unregister application {app_id}: {e}")
                return False
    
    async def start_application(self, app_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """启动应用"""
        async with self._lock:
            try:
                if app_id not in self.applications:
                    logger.error(f"Application {app_id} not found")
                    return None
                
                app_config = self.applications[app_id]
                
                # 应用配置覆盖
                if config_overrides:
                    app_config.config.update(config_overrides)
                
                # 创建应用实例
                instance = ApplicationInstance(
                    instance_id=f"{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    app_config=app_config,
                    status=ApplicationStatus.STARTING,
                    start_time=datetime.now()
                )
                
                # 启动应用
                success = await self._start_instance(instance)
                if success:
                    self.instances[instance.instance_id] = instance
                    self.running_instances[app_id].append(instance.instance_id)
                    instance.status = ApplicationStatus.RUNNING
                    
                    logger.info(f"Started application instance: {instance.instance_id}")
                    await self._notify_event("instance_started", instance)
                    return instance.instance_id
                else:
                    instance.status = ApplicationStatus.ERROR
                    logger.error(f"Failed to start application instance: {instance.instance_id}")
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to start application {app_id}: {e}")
                return None
    
    async def stop_instance(self, instance_id: str) -> bool:
        """停止应用实例"""
        async with self._lock:
            try:
                if instance_id not in self.instances:
                    return False
                
                instance = self.instances[instance_id]
                instance.status = ApplicationStatus.STOPPING
                
                # 停止应用
                success = await self._stop_instance(instance)
                if success:
                    instance.status = ApplicationStatus.STOPPED
                    instance.stop_time = datetime.now()
                    
                    # 从运行实例列表中移除
                    app_id = instance.app_config.app_id
                    if app_id in self.running_instances:
                        self.running_instances[app_id] = [
                            i for i in self.running_instances[app_id] 
                            if i != instance_id
                        ]
                    
                    logger.info(f"Stopped application instance: {instance_id}")
                    await self._notify_event("instance_stopped", instance)
                    return True
                else:
                    instance.status = ApplicationStatus.ERROR
                    logger.error(f"Failed to stop application instance: {instance_id}")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to stop instance {instance_id}: {e}")
                return False
    
    async def restart_instance(self, instance_id: str) -> bool:
        """重启应用实例"""
        try:
            if await self.stop_instance(instance_id):
                instance = self.instances[instance_id]
                return await self.start_application(instance.app_config.app_id) is not None
            return False
        except Exception as e:
            logger.error(f"Failed to restart instance {instance_id}: {e}")
            return False
    
    async def get_application_status(self, app_id: str) -> Dict[str, Any]:
        """获取应用状态"""
        try:
            if app_id not in self.applications:
                return {"error": "Application not found"}
            
            app_config = self.applications[app_id]
            running_instances = self.running_instances.get(app_id, [])
            
            instances_info = []
            for instance_id in running_instances:
                if instance_id in self.instances:
                    instance = self.instances[instance_id]
                    instances_info.append({
                        "instance_id": instance.instance_id,
                        "status": instance.status.value,
                        "start_time": instance.start_time.isoformat() if instance.start_time else None,
                        "health_score": instance.health_score,
                        "metrics": instance.metrics
                    })
            
            return {
                "app_id": app_id,
                "name": app_config.name,
                "status": "running" if running_instances else "stopped",
                "running_instances": len(running_instances),
                "instances": instances_info,
                "config": app_config.config,
                "dependencies": app_config.dependencies
            }
        except Exception as e:
            logger.error(f"Failed to get application status for {app_id}: {e}")
            return {"error": str(e)}
    
    async def list_applications(self) -> List[Dict[str, Any]]:
        """列出所有应用"""
        try:
            apps = []
            for app_id, app_config in self.applications.items():
                running_count = len(self.running_instances.get(app_id, []))
                apps.append({
                    "app_id": app_id,
                    "name": app_config.name,
                    "description": app_config.description,
                    "type": app_config.app_type.value,
                    "version": app_config.version,
                    "running_instances": running_count,
                    "status": "running" if running_count > 0 else "stopped"
                })
            return apps
        except Exception as e:
            logger.error(f"Failed to list applications: {e}")
            return []
    
    async def add_event_handler(self, event_type: str, handler: Callable):
        """添加事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _notify_event(self, event_type: str, data: Any):
        """通知事件处理器"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")
    
    async def _start_instance(self, instance: ApplicationInstance) -> bool:
        """启动应用实例的具体实现"""
        try:
            # 这里应该根据应用类型实现具体的启动逻辑
            # 目前是模拟实现
            await asyncio.sleep(0.1)  # 模拟启动时间
            
            # 健康检查
            if instance.app_config.health_check:
                try:
                    health_result = await instance.app_config.health_check()
                    instance.health_score = health_result.get("score", 1.0)
                except Exception as e:
                    logger.warning(f"Health check failed for {instance.instance_id}: {e}")
                    instance.health_score = 0.8
            
            return True
        except Exception as e:
            logger.error(f"Failed to start instance {instance.instance_id}: {e}")
            return False
    
    async def _stop_instance(self, instance: ApplicationInstance) -> bool:
        """停止应用实例的具体实现"""
        try:
            # 这里应该根据应用类型实现具体的停止逻辑
            # 目前是模拟实现
            await asyncio.sleep(0.1)  # 模拟停止时间
            return True
        except Exception as e:
            logger.error(f"Failed to stop instance {instance.instance_id}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            total_apps = len(self.applications)
            running_apps = sum(1 for instances in self.running_instances.values() if instances)
            total_instances = sum(len(instances) for instances in self.running_instances.values())
            
            return {
                "status": "healthy",
                "total_applications": total_apps,
                "running_applications": running_apps,
                "total_instances": total_instances,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 