"""
负载均衡器 - Load Balancer
实现请求分发、负载管理和故障转移功能
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """负载均衡策略枚举"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class BackendStatus(Enum):
    """后端状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


@dataclass
class BackendServer:
    """后端服务器"""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    status: BackendStatus = BackendStatus.HEALTHY
    health_score: float = 1.0
    response_times: List[float] = field(default_factory=list)
    error_count: int = 0
    last_health_check: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalancerConfig:
    """负载均衡器配置"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: int = 30
    health_check_timeout: int = 5
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    enable_sticky_sessions: bool = False
    sticky_session_timeout: int = 300


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.backends: Dict[str, BackendServer] = {}
        self.backend_list: List[str] = []
        self.current_index = 0
        self.health_check_task: Optional[asyncio.Task] = None
        self.sticky_sessions: Dict[str, str] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        logger.info(f"Load Balancer initialized with strategy: {config.strategy.value}")
    
    async def start(self):
        """启动负载均衡器"""
        if self.health_check_task is None or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Load Balancer health check loop started")
    
    async def stop(self):
        """停止负载均衡器"""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Load Balancer health check loop stopped")
    
    async def add_backend(self, backend: BackendServer) -> bool:
        """添加后端服务器"""
        async with self._lock:
            try:
                self.backends[backend.server_id] = backend
                self.backend_list.append(backend.server_id)
                self.circuit_breakers[backend.server_id] = {
                    "failure_count": 0,
                    "last_failure_time": None,
                    "circuit_open": False,
                    "circuit_open_time": None
                }
                
                logger.info(f"Added backend server: {backend.host}:{backend.port}")
                return True
            except Exception as e:
                logger.error(f"Failed to add backend server: {e}")
                return False
    
    async def remove_backend(self, server_id: str) -> bool:
        """移除后端服务器"""
        async with self._lock:
            try:
                if server_id in self.backends:
                    del self.backends[server_id]
                    self.backend_list = [bid for bid in self.backend_list if bid != server_id]
                    
                    if server_id in self.circuit_breakers:
                        del self.circuit_breakers[server_id]
                    
                    logger.info(f"Removed backend server: {server_id}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to remove backend server {server_id}: {e}")
                return False
    
    async def get_backend(self, request_info: Optional[Dict[str, Any]] = None) -> Optional[BackendServer]:
        """获取后端服务器"""
        async with self._lock:
            try:
                if not self.backend_list:
                    return None
                
                # 过滤健康的后端
                healthy_backends = [
                    bid for bid in self.backend_list
                    if (self.backends[bid].status == BackendStatus.HEALTHY and
                        not self.circuit_breakers[bid]["circuit_open"])
                ]
                
                if not healthy_backends:
                    logger.warning("No healthy backends available")
                    return None
                
                # 根据策略选择后端
                if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                    selected_id = self._round_robin_select(healthy_backends)
                elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                    selected_id = self._least_connections_select(healthy_backends)
                elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                    selected_id = self._weighted_round_robin_select(healthy_backends)
                elif self.config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                    selected_id = self._least_response_time_select(healthy_backends)
                elif self.config.strategy == LoadBalancingStrategy.IP_HASH:
                    selected_id = self._ip_hash_select(healthy_backends, request_info)
                elif self.config.strategy == LoadBalancingStrategy.RANDOM:
                    selected_id = random.choice(healthy_backends)
                else:
                    selected_id = healthy_backends[0]
                
                if selected_id:
                    backend = self.backends[selected_id]
                    backend.current_connections += 1
                    return backend
                
                return None
                
            except Exception as e:
                logger.error(f"Failed to get backend: {e}")
                return None
    
    async def release_backend(self, server_id: str):
        """释放后端服务器连接"""
        try:
            if server_id in self.backends:
                backend = self.backends[server_id]
                backend.current_connections = max(0, backend.current_connections - 1)
        except Exception as e:
            logger.error(f"Failed to release backend {server_id}: {e}")
    
    async def update_backend_health(self, server_id: str, health_score: float, response_time: Optional[float] = None):
        """更新后端健康状态"""
        try:
            if server_id in self.backends:
                backend = self.backends[server_id]
                backend.health_score = health_score
                backend.last_health_check = datetime.now()
                
                if response_time is not None:
                    backend.response_times.append(response_time)
                    # 保持最近100个响应时间
                    if len(backend.response_times) > 100:
                        backend.response_times = backend.response_times[-100:]
                
                # 更新状态
                if health_score >= 0.8:
                    backend.status = BackendStatus.HEALTHY
                elif health_score >= 0.5:
                    backend.status = BackendStatus.OVERLOADED
                else:
                    backend.status = BackendStatus.UNHEALTHY
                
                # 重置断路器
                if health_score > 0.5:
                    self.circuit_breakers[server_id]["failure_count"] = 0
                    self.circuit_breakers[server_id]["circuit_open"] = False
                
        except Exception as e:
            logger.error(f"Failed to update backend health for {server_id}: {e}")
    
    async def record_backend_error(self, server_id: str):
        """记录后端错误"""
        try:
            if server_id in self.backends:
                backend = self.backends[server_id]
                backend.error_count += 1
                
                # 更新断路器
                circuit_breaker = self.circuit_breakers[server_id]
                circuit_breaker["failure_count"] += 1
                circuit_breaker["last_failure_time"] = datetime.now()
                
                # 检查是否触发断路器
                if (circuit_breaker["failure_count"] >= self.config.circuit_breaker_threshold and
                    not circuit_breaker["circuit_open"]):
                    circuit_breaker["circuit_open"] = True
                    circuit_breaker["circuit_open_time"] = datetime.now()
                    logger.warning(f"Circuit breaker opened for backend {server_id}")
                
        except Exception as e:
            logger.error(f"Failed to record backend error for {server_id}: {e}")
    
    def _round_robin_select(self, healthy_backends: List[str]) -> str:
        """轮询选择"""
        if not healthy_backends:
            return None
        
        selected_id = healthy_backends[self.current_index % len(healthy_backends)]
        self.current_index = (self.current_index + 1) % len(healthy_backends)
        return selected_id
    
    def _least_connections_select(self, healthy_backends: List[str]) -> str:
        """最少连接选择"""
        if not healthy_backends:
            return None
        
        return min(healthy_backends, key=lambda bid: self.backends[bid].current_connections)
    
    def _weighted_round_robin_select(self, healthy_backends: List[str]) -> str:
        """加权轮询选择"""
        if not healthy_backends:
            return None
        
        # 计算总权重
        total_weight = sum(self.backends[bid].weight for bid in healthy_backends)
        if total_weight == 0:
            return random.choice(healthy_backends)
        
        # 加权随机选择
        rand = random.uniform(0, total_weight)
        current_weight = 0
        
        for bid in healthy_backends:
            current_weight += self.backends[bid].weight
            if rand <= current_weight:
                return bid
        
        return healthy_backends[-1]
    
    def _least_response_time_select(self, healthy_backends: List[str]) -> str:
        """最少响应时间选择"""
        if not healthy_backends:
            return None
        
        def get_avg_response_time(bid):
            backend = self.backends[bid]
            if not backend.response_times:
                return float('inf')
            return statistics.mean(backend.response_times)
        
        return min(healthy_backends, key=get_avg_response_time)
    
    def _ip_hash_select(self, healthy_backends: List[str], request_info: Optional[Dict[str, Any]]) -> str:
        """IP哈希选择"""
        if not healthy_backends:
            return None
        
        if not request_info or "client_ip" not in request_info:
            return random.choice(healthy_backends)
        
        client_ip = request_info["client_ip"]
        hash_value = hash(client_ip) % len(healthy_backends)
        return healthy_backends[hash_value]
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        try:
            for server_id in list(self.backends.keys()):
                await self._check_backend_health(server_id)
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    async def _check_backend_health(self, server_id: str):
        """检查单个后端健康状态"""
        try:
            backend = self.backends[server_id]
            
            # 检查断路器状态
            circuit_breaker = self.circuit_breakers[server_id]
            if circuit_breaker["circuit_open"]:
                # 检查是否应该关闭断路器
                if (circuit_breaker["circuit_open_time"] and
                    datetime.now() - circuit_breaker["circuit_open_time"] > timedelta(seconds=self.config.circuit_breaker_timeout)):
                    circuit_breaker["circuit_open"] = False
                    circuit_breaker["failure_count"] = 0
                    logger.info(f"Circuit breaker closed for backend {server_id}")
            
            # 这里应该实现具体的健康检查逻辑
            # 目前是模拟实现
            health_score = 0.9 + random.uniform(-0.1, 0.1)
            await self.update_backend_health(server_id, health_score)
            
        except Exception as e:
            logger.error(f"Health check failed for backend {server_id}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            total_backends = len(self.backends)
            healthy_backends = sum(1 for b in self.backends.values() if b.status == BackendStatus.HEALTHY)
            total_connections = sum(b.current_connections for b in self.backends.values())
            
            return {
                "total_backends": total_backends,
                "healthy_backends": healthy_backends,
                "unhealthy_backends": total_backends - healthy_backends,
                "total_connections": total_connections,
                "strategy": self.config.strategy.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "config": {
                "strategy": self.config.strategy.value,
                "health_check_interval": self.config.health_check_interval,
                "max_retries": self.config.max_retries
            },
            "backends": [backend.__dict__ for backend in self.backends.values()],
            "current_index": self.current_index,
            "sticky_sessions": self.sticky_sessions,
            "circuit_breakers": self.circuit_breakers
        } 