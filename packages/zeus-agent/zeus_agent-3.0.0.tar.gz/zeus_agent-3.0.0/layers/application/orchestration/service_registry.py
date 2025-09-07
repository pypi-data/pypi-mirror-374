"""
服务注册表 - Service Registry
提供服务发现、注册、注销和健康检查功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    """服务类型枚举"""
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    QUEUE = "queue"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    CUSTOM = "custom"


@dataclass
class ServiceEndpoint:
    """服务端点"""
    protocol: str
    host: str
    port: int
    path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceInfo:
    """服务信息"""
    service_id: str
    name: str
    description: str
    version: str
    service_type: ServiceType
    endpoints: List[ServiceEndpoint]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceInstance:
    """服务实例"""
    instance_id: str
    service_info: ServiceInfo
    status: ServiceStatus
    health_score: float = 1.0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self, heartbeat_interval: int = 30, health_check_timeout: int = 10):
        self.services: Dict[str, ServiceInfo] = {}
        self.instances: Dict[str, ServiceInstance] = {}
        self.service_instances: Dict[str, List[str]] = {}
        self.heartbeat_interval = heartbeat_interval
        self.health_check_timeout = health_check_timeout
        self._lock = asyncio.Lock()
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        logger.info("Service Registry initialized")
    
    async def start(self):
        """启动服务注册表"""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            logger.info("Service Registry heartbeat monitor started")
    
    async def stop(self):
        """停止服务注册表"""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Service Registry heartbeat monitor stopped")
    
    async def register_service(self, service_info: ServiceInfo) -> bool:
        """注册服务"""
        async with self._lock:
            try:
                self.services[service_info.service_id] = service_info
                self.service_instances[service_info.service_id] = []
                logger.info(f"Registered service: {service_info.name} ({service_info.service_id})")
                return True
            except Exception as e:
                logger.error(f"Failed to register service {service_info.service_id}: {e}")
                return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """注销服务"""
        async with self._lock:
            try:
                if service_id in self.services:
                    # 停止所有相关实例
                    if service_id in self.service_instances:
                        for instance_id in self.service_instances[service_id]:
                            await self.deregister_instance(instance_id)
                    
                    del self.services[service_id]
                    if service_id in self.service_instances:
                        del self.service_instances[service_id]
                    
                    logger.info(f"Unregistered service: {service_id}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to unregister service {service_id}: {e}")
                return False
    
    async def register_instance(self, service_id: str, instance_info: Dict[str, Any]) -> Optional[str]:
        """注册服务实例"""
        async with self._lock:
            try:
                if service_id not in self.services:
                    logger.error(f"Service {service_id} not found")
                    return None
                
                service_info = self.services[service_id]
                
                # 创建实例
                instance = ServiceInstance(
                    instance_id=instance_info.get("instance_id", f"{service_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    service_info=service_info,
                    status=ServiceStatus.HEALTHY,
                    start_time=datetime.now()
                )
                
                # 注册实例
                self.instances[instance.instance_id] = instance
                self.service_instances[service_id].append(instance.instance_id)
                
                logger.info(f"Registered service instance: {instance.instance_id}")
                return instance.instance_id
                
            except Exception as e:
                logger.error(f"Failed to register instance for service {service_id}: {e}")
                return None
    
    async def deregister_instance(self, instance_id: str) -> bool:
        """注销服务实例"""
        async with self._lock:
            try:
                if instance_id not in self.instances:
                    return False
                
                instance = self.instances[instance_id]
                service_id = instance.service_info.service_id
                
                # 从服务实例列表中移除
                if service_id in self.service_instances:
                    self.service_instances[service_id] = [
                        i for i in self.service_instances[service_id] 
                        if i != instance_id
                    ]
                
                # 删除实例
                del self.instances[instance_id]
                
                logger.info(f"Deregistered service instance: {instance_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to deregister instance {instance_id}: {e}")
                return False
    
    async def update_instance_heartbeat(self, instance_id: str, health_score: Optional[float] = None) -> bool:
        """更新实例心跳"""
        try:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                instance.last_heartbeat = datetime.now()
                
                if health_score is not None:
                    instance.health_score = max(0.0, min(1.0, health_score))
                    instance.status = ServiceStatus.HEALTHY if instance.health_score > 0.5 else ServiceStatus.UNHEALTHY
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update heartbeat for instance {instance_id}: {e}")
            return False
    
    async def discover_service(self, service_name: str, tags: Optional[List[str]] = None) -> List[ServiceInfo]:
        """发现服务"""
        try:
            discovered_services = []
            
            for service_id, service_info in self.services.items():
                if service_info.name == service_name:
                    # 标签匹配
                    if tags is None or all(tag in service_info.tags for tag in tags):
                        discovered_services.append(service_info)
            
            return discovered_services
        except Exception as e:
            logger.error(f"Failed to discover service {service_name}: {e}")
            return []
    
    async def get_service_instances(self, service_id: str) -> List[ServiceInstance]:
        """获取服务的所有实例"""
        try:
            if service_id not in self.service_instances:
                return []
            
            instances = []
            for instance_id in self.service_instances[service_id]:
                if instance_id in self.instances:
                    instances.append(self.instances[instance_id])
            
            return instances
        except Exception as e:
            logger.error(f"Failed to get instances for service {service_id}: {e}")
            return []
    
    async def list_services(self) -> List[Dict[str, Any]]:
        """列出所有服务"""
        try:
            services = []
            for service_id, service_info in self.services.items():
                instance_count = len(self.service_instances.get(service_id, []))
                instances = await self.get_service_instances(service_id)
                healthy_count = sum(1 for instance in instances 
                                  if instance.status == ServiceStatus.HEALTHY)
                
                services.append({
                    "service_id": service_id,
                    "name": service_info.name,
                    "description": service_info.description,
                    "type": service_info.service_type.value,
                    "version": service_info.version,
                    "total_instances": instance_count,
                    "healthy_instances": healthy_count,
                    "tags": service_info.tags,
                    "created_at": service_info.created_at.isoformat()
                })
            
            return services
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            total_services = len(self.services)
            total_instances = sum(len(instances) for instances in self.service_instances.values())
            healthy_instances = sum(1 for instance in self.instances.values() 
                                  if instance.status == ServiceStatus.HEALTHY)
            
            return {
                "status": "healthy" if healthy_instances > 0 else "unhealthy",
                "total_services": total_services,
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "unhealthy_instances": total_instances - healthy_instances,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _heartbeat_monitor(self):
        """心跳监控任务"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._check_heartbeats()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
    
    async def _check_heartbeats(self):
        """检查心跳"""
        try:
            current_time = datetime.now()
            timeout_threshold = current_time - timedelta(seconds=self.heartbeat_interval * 2)
            
            instances_to_remove = []
            
            for instance_id, instance in self.instances.items():
                if instance.last_heartbeat < timeout_threshold:
                    # 心跳超时，标记为不健康
                    instance.status = ServiceStatus.UNHEALTHY
                    instance.health_score = 0.0
                    logger.warning(f"Instance {instance_id} heartbeat timeout")
                    
                    # 如果长时间无心跳，考虑移除实例
                    if instance.last_heartbeat < current_time - timedelta(seconds=self.heartbeat_interval * 4):
                        instances_to_remove.append(instance_id)
            
            # 移除长时间无心跳的实例
            for instance_id in instances_to_remove:
                await self.deregister_instance(instance_id)
                logger.info(f"Removed stale instance: {instance_id}")
                
        except Exception as e:
            logger.error(f"Heartbeat check failed: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "services": [service_info.__dict__ for service_info in self.services.values()],
            "instances": [instance.__dict__ for instance in self.instances.values()],
            "service_instances": self.service_instances,
            "heartbeat_interval": self.heartbeat_interval,
            "health_check_timeout": self.health_check_timeout
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典格式恢复"""
        try:
            # 这里应该实现从字典恢复状态的逻辑
            # 为了简化，目前只记录日志
            logger.info("Service Registry state restored from dictionary")
        except Exception as e:
            logger.error(f"Failed to restore Service Registry state: {e}") 