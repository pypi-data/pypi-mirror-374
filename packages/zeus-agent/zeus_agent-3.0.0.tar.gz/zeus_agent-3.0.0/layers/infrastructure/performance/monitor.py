"""
性能监控系统
支持实时监控、指标收集、性能分析、告警和性能优化建议
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import json


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"        # 计数器（只增不减）
    GAUGE = "gauge"           # 测量值（可增可减）
    HISTOGRAM = "histogram"    # 直方图
    TIMER = "timer"           # 计时器
    RATE = "rate"             # 速率


class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """性能指标"""
    name: str
    type: MetricType
    value: Union[float, int]
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""


@dataclass
class Alert:
    """性能告警"""
    id: str
    level: AlertLevel
    metric_name: str
    message: str
    threshold: float
    current_value: float
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int
    thread_count: int
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class MetricCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._lock = threading.RLock()
    
    def record(self, name: str, value: Union[float, int], 
               metric_type: MetricType = MetricType.GAUGE,
               tags: Optional[Dict[str, str]] = None,
               unit: str = "", description: str = ""):
        """记录指标"""
        with self._lock:
            metric = Metric(
                name=name,
                type=metric_type,
                value=value,
                timestamp=time.time(),
                tags=tags or {},
                unit=unit,
                description=description
            )
            self._metrics[name].append(metric)
    
    def get_latest(self, name: str) -> Optional[Metric]:
        """获取最新指标值"""
        with self._lock:
            if name in self._metrics and self._metrics[name]:
                return self._metrics[name][-1]
            return None
    
    def get_history(self, name: str, limit: Optional[int] = None) -> List[Metric]:
        """获取历史指标"""
        with self._lock:
            if name not in self._metrics:
                return []
            
            history = list(self._metrics[name])
            if limit:
                return history[-limit:]
            return history
    
    def get_statistics(self, name: str, duration_seconds: Optional[float] = None) -> Dict[str, float]:
        """获取指标统计信息"""
        with self._lock:
            if name not in self._metrics:
                return {}
            
            now = time.time()
            metrics = self._metrics[name]
            
            # 筛选时间范围内的指标
            if duration_seconds:
                cutoff_time = now - duration_seconds
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            else:
                metrics = list(metrics)
            
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            try:
                return {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'latest': values[-1],
                    'first': values[0]
                }
            except Exception:
                return {'count': len(values), 'latest': values[-1] if values else 0}
    
    def clear(self, name: Optional[str] = None):
        """清除指标历史"""
        with self._lock:
            if name:
                if name in self._metrics:
                    self._metrics[name].clear()
            else:
                self._metrics.clear()


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.collector = MetricCollector()
        self._running = False
        self._thread = None
        self._callbacks: List[Callable[[PerformanceSnapshot], None]] = []
    
    def add_callback(self, callback: Callable[[PerformanceSnapshot], None]):
        """添加监控回调"""
        self._callbacks.append(callback)
    
    def start(self):
        """开始监控"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                snapshot = self._collect_system_metrics()
                
                # 记录系统指标
                self.collector.record("system.cpu_percent", snapshot.cpu_percent, MetricType.GAUGE, unit="%")
                self.collector.record("system.memory_percent", snapshot.memory_percent, MetricType.GAUGE, unit="%")
                self.collector.record("system.memory_used_mb", snapshot.memory_used_mb, MetricType.GAUGE, unit="MB")
                self.collector.record("system.disk_usage_percent", snapshot.disk_usage_percent, MetricType.GAUGE, unit="%")
                self.collector.record("system.process_count", snapshot.process_count, MetricType.GAUGE)
                self.collector.record("system.thread_count", snapshot.thread_count, MetricType.GAUGE)
                
                # 网络IO指标
                for key, value in snapshot.network_io.items():
                    self.collector.record(f"system.network.{key}", value, MetricType.GAUGE, unit="bytes")
                
                # 调用回调函数
                for callback in self._callbacks:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        print(f"监控回调执行失败: {e}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"系统监控异常: {e}")
                time.sleep(self.interval)
    
    def _collect_system_metrics(self) -> PerformanceSnapshot:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # 网络IO
            network_io = psutil.net_io_counters()._asdict()
            
            # 进程和线程数
            process_count = len(psutil.pids())
            current_process = psutil.Process()
            thread_count = current_process.num_threads()
            
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count,
                thread_count=thread_count
            )
            
        except Exception as e:
            print(f"收集系统指标失败: {e}")
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_usage_percent=0.0,
                network_io={},
                process_count=0,
                thread_count=0
            )


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._alerts: Dict[str, Alert] = {}
        self._handlers: List[Callable[[Alert], None]] = []
        self._lock = threading.RLock()
    
    def add_rule(self, name: str, metric_name: str, condition: str, 
                 threshold: float, level: AlertLevel = AlertLevel.WARNING,
                 message: str = ""):
        """添加告警规则"""
        with self._lock:
            self._rules[name] = {
                'metric_name': metric_name,
                'condition': condition,  # >, <, >=, <=, ==
                'threshold': threshold,
                'level': level,
                'message': message or f"{metric_name} {condition} {threshold}"
            }
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """添加告警处理器"""
        self._handlers.append(handler)
    
    def check_alerts(self, collector: MetricCollector):
        """检查告警条件"""
        with self._lock:
            for rule_name, rule in self._rules.items():
                metric = collector.get_latest(rule['metric_name'])
                if not metric:
                    continue
                
                # 检查告警条件
                should_alert = self._evaluate_condition(
                    metric.value, rule['condition'], rule['threshold']
                )
                
                alert_id = f"{rule_name}_{rule['metric_name']}"
                current_alert = self._alerts.get(alert_id)
                
                if should_alert and (not current_alert or current_alert.resolved):
                    # 触发新告警
                    alert = Alert(
                        id=alert_id,
                        level=rule['level'],
                        metric_name=rule['metric_name'],
                        message=rule['message'],
                        threshold=rule['threshold'],
                        current_value=metric.value,
                        timestamp=time.time()
                    )
                    
                    self._alerts[alert_id] = alert
                    self._trigger_alert(alert)
                
                elif not should_alert and current_alert and not current_alert.resolved:
                    # 解决告警
                    current_alert.resolved = True
                    current_alert.resolved_at = time.time()
                    self._resolve_alert(current_alert)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估告警条件"""
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        elif condition == '==':
            return abs(value - threshold) < 1e-6
        else:
            return False
    
    def _trigger_alert(self, alert: Alert):
        """触发告警"""
        print(f"🚨 告警触发: {alert.message} (当前值: {alert.current_value})")
        
        for handler in self._handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"告警处理器执行失败: {e}")
    
    def _resolve_alert(self, alert: Alert):
        """解决告警"""
        print(f"✅ 告警解决: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        with self._lock:
            return [alert for alert in self._alerts.values() if not alert.resolved]
    
    def get_all_alerts(self) -> List[Alert]:
        """获取所有告警"""
        with self._lock:
            return list(self._alerts.values())


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self._profiles: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def profile(self, name: str = "default"):
        """性能分析装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    
                    profile_data = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'duration_ms': (end_time - start_time) * 1000,
                        'memory_delta_mb': end_memory - start_memory,
                        'timestamp': start_time,
                        'success': success,
                        'error': error,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                    
                    with self._lock:
                        self._profiles[name].append(profile_data)
                        
                        # 保持最近1000条记录
                        if len(self._profiles[name]) > 1000:
                            self._profiles[name] = self._profiles[name][-1000:]
                
                return result
            
            return wrapper
        return decorator
    
    def get_profile_stats(self, name: str = "default") -> Dict[str, Any]:
        """获取性能分析统计"""
        with self._lock:
            if name not in self._profiles or not self._profiles[name]:
                return {}
            
            profiles = self._profiles[name]
            durations = [p['duration_ms'] for p in profiles]
            memory_deltas = [p['memory_delta_mb'] for p in profiles]
            
            # 按函数分组统计
            function_stats = defaultdict(list)
            for profile in profiles:
                function_stats[profile['function']].append(profile['duration_ms'])
            
            return {
                'total_calls': len(profiles),
                'success_rate': sum(1 for p in profiles if p['success']) / len(profiles),
                'duration_stats': {
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'avg_ms': statistics.mean(durations),
                    'median_ms': statistics.median(durations),
                    'p95_ms': self._percentile(durations, 95),
                    'p99_ms': self._percentile(durations, 99)
                },
                'memory_stats': {
                    'avg_delta_mb': statistics.mean(memory_deltas),
                    'max_delta_mb': max(memory_deltas),
                    'min_delta_mb': min(memory_deltas)
                },
                'function_stats': {
                    func: {
                        'calls': len(times),
                        'avg_ms': statistics.mean(times),
                        'max_ms': max(times)
                    }
                    for func, times in function_stats.items()
                }
            }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class PerformanceMonitor:
    """性能监控主类"""
    
    def __init__(self, monitor_interval: float = 1.0):
        self.collector = MetricCollector()
        self.system_monitor = SystemMonitor(monitor_interval)
        self.alert_manager = AlertManager()
        self.profiler = PerformanceProfiler()
        
        # 设置默认告警规则
        self._setup_default_alerts()
        
        # 系统监控回调
        self.system_monitor.add_callback(self._on_system_metrics)
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_manager.add_rule(
            "high_cpu", "system.cpu_percent", ">", 80.0, 
            AlertLevel.WARNING, "CPU使用率过高"
        )
        self.alert_manager.add_rule(
            "high_memory", "system.memory_percent", ">", 85.0,
            AlertLevel.WARNING, "内存使用率过高"
        )
        self.alert_manager.add_rule(
            "critical_memory", "system.memory_percent", ">", 95.0,
            AlertLevel.CRITICAL, "内存使用率严重过高"
        )
    
    def _on_system_metrics(self, snapshot: PerformanceSnapshot):
        """系统指标回调"""
        # 检查告警
        self.alert_manager.check_alerts(self.collector)
    
    def start_monitoring(self):
        """开始监控"""
        self.system_monitor.start()
        print("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.system_monitor.stop()
        print("性能监控已停止")
    
    def record_metric(self, name: str, value: Union[float, int], 
                     metric_type: MetricType = MetricType.GAUGE, **kwargs):
        """记录自定义指标"""
        self.collector.record(name, value, metric_type, **kwargs)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        return {
            'system_metrics': {
                'cpu': self.collector.get_statistics("system.cpu_percent", 300),  # 5分钟
                'memory': self.collector.get_statistics("system.memory_percent", 300),
                'disk': self.collector.get_statistics("system.disk_usage_percent", 300)
            },
            'active_alerts': [
                {
                    'id': alert.id,
                    'level': alert.level.value,
                    'message': alert.message,
                    'current_value': alert.current_value,
                    'timestamp': alert.timestamp
                }
                for alert in self.alert_manager.get_active_alerts()
            ],
            'performance_profiles': self.profiler.get_profile_stats()
        }


# 全局性能监控实例
_global_monitor = None


def get_performance_monitor(**kwargs) -> PerformanceMonitor:
    """获取全局性能监控实例"""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor(**kwargs)
    
    return _global_monitor


# 便捷函数和装饰器
def record_metric(name: str, value: Union[float, int], 
                 metric_type: MetricType = MetricType.GAUGE, **kwargs):
    """记录性能指标"""
    get_performance_monitor().record_metric(name, value, metric_type, **kwargs)


def profile(name: str = "default"):
    """性能分析装饰器"""
    return get_performance_monitor().profiler.profile(name)


def start_monitoring():
    """启动性能监控"""
    get_performance_monitor().start_monitoring()


def stop_monitoring():
    """停止性能监控"""
    get_performance_monitor().stop_monitoring() 