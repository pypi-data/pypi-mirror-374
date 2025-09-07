"""
应用编排层演示 - Application Orchestration Layer Demo
展示应用编排层的核心功能：应用组装、服务发现、负载均衡、生命周期管理
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入应用编排层组件
try:
    from layers.application.orchestration.orchestrator import (
        ApplicationOrchestrator, ApplicationConfig, ApplicationType
    )
    from layers.application.orchestration.service_registry import (
        ServiceRegistry, ServiceInfo, ServiceType, ServiceEndpoint
    )
    from layers.application.orchestration.load_balancer import (
        LoadBalancer, LoadBalancerConfig, BackendServer, LoadBalancingStrategy
    )
    from layers.application.orchestration.lifecycle_manager import (
        ApplicationLifecycleManager, LifecycleConfig, ProcessType, LifecycleState
    )
    IMPORTS_SUCCESS = True
except ImportError as e:
    logger.error(f"导入失败: {e}")
    IMPORTS_SUCCESS = False


class ApplicationOrchestrationDemo:
    """应用编排层演示类"""
    
    def __init__(self):
        self.orchestrator = None
        self.service_registry = None
        self.load_balancer = None
        self.lifecycle_manager = None
        
    async def run_demo(self):
        """运行演示"""
        print("🌟 Agent Development Center - 应用编排层演示")
        print("=" * 60)
        print("本演示将展示应用编排层的核心功能：")
        print("• 应用编排器 - 动态组装和配置应用")
        print("• 服务注册表 - 服务发现和注册")
        print("• 负载均衡器 - 请求分发和负载管理")
        print("• 生命周期管理器 - 应用启动、停止、重启、监控")
        print("=" * 60)
        
        try:
            # 初始化组件
            await self._initialize_components()
            
            # 运行演示
            await self._demo_application_orchestration()
            await self._demo_service_registry()
            await self._demo_load_balancer()
            await self._demo_lifecycle_management()
            
            # 综合演示
            await self._demo_integration()
            
        except Exception as e:
            logger.error(f"演示过程中发生错误: {e}")
            raise
        finally:
            # 清理资源
            await self._cleanup()
    
    async def _initialize_components(self):
        """初始化组件"""
        print("\n🚀 初始化应用编排层组件...")
        
        try:
            if not IMPORTS_SUCCESS:
                raise ImportError("应用编排层组件导入失败")
            
            # 创建应用编排器
            self.orchestrator = ApplicationOrchestrator()
            
            # 创建服务注册表
            self.service_registry = ServiceRegistry()
            await self.service_registry.start()
            
            # 创建负载均衡器
            lb_config = LoadBalancerConfig(
                strategy=LoadBalancingStrategy.ROUND_ROBIN,
                health_check_interval=10,
                circuit_breaker_threshold=3
            )
            self.load_balancer = LoadBalancer(lb_config)
            await self.load_balancer.start()
            
            # 创建生命周期管理器
            lifecycle_config = LifecycleConfig(
                auto_restart=True,
                max_restart_attempts=3,
                restart_delay=2.0
            )
            self.lifecycle_manager = ApplicationLifecycleManager(lifecycle_config)
            await self.lifecycle_manager.start()
            
            print("✅ 所有组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    async def _demo_application_orchestration(self):
        """演示应用编排器"""
        print("\n📋 1. 应用编排器演示")
        print("-" * 40)
        
        try:
            # 创建应用配置
            app_configs = [
                {
                    "app_id": "web_app_001",
                    "name": "Web应用服务",
                    "description": "提供Web界面和API服务",
                    "app_type": "web",
                    "version": "1.0.0",
                    "dependencies": ["database", "cache"],
                    "config": {"port": 8080, "workers": 4},
                    "environment": {},
                    "resources": {}
                },
                {
                    "app_id": "api_gateway_001",
                    "name": "API网关服务",
                    "description": "统一API入口和路由",
                    "app_type": "api",
                    "version": "1.0.0",
                    "dependencies": ["auth", "rate_limit"],
                    "config": {"port": 8000, "timeout": 30},
                    "environment": {},
                    "resources": {}
                },
                {
                    "app_id": "worker_service_001",
                    "name": "后台工作服务",
                    "description": "处理异步任务和批处理",
                    "app_type": "background",
                    "version": "1.0.0",
                    "dependencies": ["queue", "storage"],
                    "config": {"workers": 8, "batch_size": 100},
                    "environment": {},
                    "resources": {}
                }
            ]
            
            # 注册应用
            for app_config_data in app_configs:
                config = ApplicationConfig(**app_config_data)
                success = await self.orchestrator.register_application(config)
                if success:
                    print(f"✅ 注册应用: {config.name} ({config.app_id})")
                else:
                    print(f"❌ 注册应用失败: {config.name}")
            
            # 启动应用
            print("\n🚀 启动应用实例...")
            for app_config_data in app_configs:
                app_id = app_config_data["app_id"]
                instance_id = await self.orchestrator.start_application(app_id)
                if instance_id:
                    print(f"✅ 启动应用实例: {app_id} -> {instance_id}")
                else:
                    print(f"❌ 启动应用实例失败: {app_id}")
            
            # 获取应用状态
            print("\n📊 应用状态:")
            for app_config_data in app_configs:
                app_id = app_config_data["app_id"]
                status = await self.orchestrator.get_application_status(app_id)
                if "error" not in status:
                    print(f"   {app_id}: {status['status']} ({status['running_instances']} 个实例)")
                else:
                    print(f"   {app_id}: 获取状态失败")
            
            # 列出所有应用
            apps = await self.orchestrator.list_applications()
            print(f"\n📋 已注册应用数量: {len(apps)}")
            
        except Exception as e:
            logger.error(f"应用编排器演示失败: {e}")
            raise
    
    async def _demo_service_registry(self):
        """演示服务注册表"""
        print("\n📋 2. 服务注册表演示")
        print("-" * 40)
        
        try:
            # 创建服务信息
            service_infos = [
                {
                    "service_id": "user_service_001",
                    "name": "用户服务",
                    "description": "用户管理和认证服务",
                    "version": "1.0.0",
                    "service_type": ServiceType.HTTP,
                    "endpoints": [
                        ServiceEndpoint("http", "localhost", 8001, "/api/users"),
                        ServiceEndpoint("http", "localhost", 8002, "/api/users")
                    ],
                    "tags": ["user", "auth", "core"],
                    "dependencies": ["database", "redis"]
                },
                {
                    "service_id": "order_service_001",
                    "name": "订单服务",
                    "description": "订单管理和处理服务",
                    "version": "1.0.0",
                    "service_type": ServiceType.HTTP,
                    "endpoints": [
                        ServiceEndpoint("http", "localhost", 8003, "/api/orders"),
                        ServiceEndpoint("http", "localhost", 8004, "/api/orders")
                    ],
                    "tags": ["order", "business", "core"],
                    "dependencies": ["database", "message_queue"]
                },
                {
                    "service_id": "notification_service_001",
                    "name": "通知服务",
                    "description": "消息推送和通知服务",
                    "version": "1.0.0",
                    "service_type": ServiceType.HTTP,
                    "endpoints": [
                        ServiceEndpoint("http", "localhost", 8005, "/api/notifications")
                    ],
                    "tags": ["notification", "communication"],
                    "dependencies": ["email", "sms", "push"]
                }
            ]
            
            # 注册服务
            for service_info_data in service_infos:
                service_info = ServiceInfo(**service_info_data)
                success = await self.service_registry.register_service(service_info)
                if success:
                    print(f"✅ 注册服务: {service_info.name} ({service_info.service_id})")
                else:
                    print(f"❌ 注册服务失败: {service_info.name}")
            
            # 注册服务实例
            print("\n🔧 注册服务实例...")
            for service_info_data in service_infos:
                service_id = service_info_data["service_id"]
                instance_info = {
                    "instance_id": f"{service_id}_instance_001",
                    "host": "localhost",
                    "port": 8001 + hash(service_id) % 10
                }
                
                instance_id = await self.service_registry.register_instance(service_id, instance_info)
                if instance_id:
                    print(f"✅ 注册实例: {service_id} -> {instance_id}")
                else:
                    print(f"❌ 注册实例失败: {service_id}")
            
            # 服务发现
            print("\n🔍 服务发现演示...")
            discovered_services = await self.service_registry.discover_service("用户服务", tags=["core"])
            print(f"   发现核心用户服务: {len(discovered_services)} 个")
            
            # 列出所有服务
            services = await self.service_registry.list_services()
            print(f"\n📋 已注册服务数量: {len(services)}")
            
            # 健康检查
            health = await self.service_registry.health_check()
            print(f"📊 服务注册表健康状态: {health['status']}")
            
        except Exception as e:
            logger.error(f"服务注册表演示失败: {e}")
            raise
    
    async def _demo_load_balancer(self):
        """演示负载均衡器"""
        print("\n📋 3. 负载均衡器演示")
        print("-" * 40)
        
        try:
            # 添加后端服务器
            backend_servers = [
                BackendServer("backend_001", "localhost", 8001, weight=2, max_connections=100),
                BackendServer("backend_002", "localhost", 8002, weight=1, max_connections=80),
                BackendServer("backend_003", "localhost", 8003, weight=3, max_connections=120),
                BackendServer("backend_004", "localhost", 8004, weight=1, max_connections=60)
            ]
            
            print("🔧 添加后端服务器...")
            for backend in backend_servers:
                success = await self.load_balancer.add_backend(backend)
                if success:
                    print(f"✅ 添加后端: {backend.host}:{backend.port} (权重: {backend.weight})")
                else:
                    print(f"❌ 添加后端失败: {backend.host}:{backend.port}")
            
            # 测试负载均衡
            print("\n⚖️ 测试负载均衡...")
            request_count = 20
            
            for i in range(request_count):
                backend = await self.load_balancer.get_backend()
                if backend:
                    print(f"   请求 {i+1:2d}: 路由到 {backend.host}:{backend.port}")
                    # 模拟请求处理
                    await asyncio.sleep(0.1)
                    # 释放连接
                    await self.load_balancer.release_backend(backend.server_id)
                else:
                    print(f"   请求 {i+1:2d}: 无可用后端")
            
            # 更新后端健康状态
            print("\n💚 更新后端健康状态...")
            for backend in backend_servers:
                health_score = 0.8 + (hash(backend.server_id) % 20) / 100.0
                response_time = 0.1 + (hash(backend.server_id) % 50) / 1000.0
                await self.load_balancer.update_backend_health(
                    backend.server_id, health_score, response_time
                )
                print(f"   后端 {backend.server_id}: 健康分数 {health_score:.2f}, 响应时间 {response_time:.3f}s")
            
            # 获取统计信息
            stats = await self.load_balancer.get_stats()
            print(f"\n📊 负载均衡器统计: {stats['total_backends']} 个后端, {stats['healthy_backends']} 个健康")
            
        except Exception as e:
            logger.error(f"负载均衡器演示失败: {e}")
            raise
    
    async def _demo_lifecycle_management(self):
        """演示生命周期管理"""
        print("\n📋 4. 生命周期管理器演示")
        print("-" * 40)
        
        try:
            # 添加状态变化处理器
            async def on_process_started(process_info):
                print(f"   🚀 进程启动: {process_info.name} (PID: {process_info.pid})")
            
            async def on_process_stopped(process_info):
                print(f"   🛑 进程停止: {process_info.name} (PID: {process_info.pid})")
            
            await self.lifecycle_manager.add_state_handler(LifecycleState.RUNNING, on_process_started)
            await self.lifecycle_manager.add_state_handler(LifecycleState.STOPPED, on_process_stopped)
            
            # 启动不同类型的进程
            print("🔧 启动不同类型的进程...")
            
            # 主进程
            main_pid = await self.lifecycle_manager.start_process(
                ProcessType.MAIN, "主应用进程", "python", ["-c", "import time; time.sleep(5)"]
            )
            if main_pid:
                print(f"✅ 启动主进程: PID {main_pid}")
            
            # 工作进程
            worker_pid = await self.lifecycle_manager.start_process(
                ProcessType.WORKER, "工作进程", "python", ["-c", "import time; time.sleep(10)"]
            )
            if worker_pid:
                print(f"✅ 启动工作进程: PID {worker_pid}")
            
            # 后台进程
            background_pid = await self.lifecycle_manager.start_process(
                ProcessType.BACKGROUND, "后台进程", "python", ["-c", "import time; time.sleep(15)"]
            )
            if background_pid:
                print(f"✅ 启动后台进程: PID {background_pid}")
            
            # 等待一段时间让进程运行
            print("\n⏳ 等待进程运行...")
            await asyncio.sleep(3)
            
            # 获取进程状态
            print("\n📊 进程状态:")
            for pid in [main_pid, worker_pid, background_pid]:
                if pid:
                    status = await self.lifecycle_manager.get_process_status(pid)
                    if status:
                        print(f"   PID {pid}: {status['name']} - {status['status']}")
            
            # 重启进程
            if worker_pid:
                print(f"\n🔄 重启工作进程 (PID: {worker_pid})...")
                success = await self.lifecycle_manager.restart_process(worker_pid)
                if success:
                    print("✅ 工作进程重启成功")
                else:
                    print("❌ 工作进程重启失败")
            
            # 获取统计信息
            stats = await self.lifecycle_manager.get_stats()
            print(f"\n📊 生命周期管理器统计: {stats['total_processes']} 个进程, {stats['running_processes']} 个运行中")
            
        except Exception as e:
            logger.error(f"生命周期管理器演示失败: {e}")
            raise
    
    async def _demo_integration(self):
        """综合演示"""
        print("\n📋 5. 综合演示 - 端到端应用编排")
        print("-" * 40)
        
        try:
            print("🔗 集成所有组件...")
            
            # 1. 应用编排器状态
            orchestrator_health = await self.orchestrator.health_check()
            print(f"   应用编排器: {orchestrator_health['status']}")
            
            # 2. 服务注册表状态
            service_health = await self.service_registry.health_check()
            print(f"   服务注册表: {service_health['status']}")
            
            # 3. 负载均衡器状态
            lb_stats = await self.load_balancer.get_stats()
            print(f"   负载均衡器: {lb_stats['healthy_backends']}/{lb_stats['total_backends']} 个健康后端")
            
            # 4. 生命周期管理器状态
            lifecycle_stats = await self.lifecycle_manager.get_stats()
            print(f"   生命周期管理器: {lifecycle_stats['running_processes']}/{lifecycle_stats['total_processes']} 个进程运行中")
            
            # 5. 整体健康评估
            overall_health = "healthy"
            if (orchestrator_health['status'] == "unhealthy" or
                service_health['status'] == "unhealthy" or
                lb_stats['healthy_backends'] == 0 or
                lifecycle_stats['running_processes'] == 0):
                overall_health = "unhealthy"
            
            print(f"\n🎯 整体健康状态: {overall_health}")
            
            if overall_health == "healthy":
                print("✅ 应用编排层运行正常，所有组件工作正常！")
            else:
                print("⚠️ 应用编排层存在问题，需要检查组件状态")
            
        except Exception as e:
            logger.error(f"综合演示失败: {e}")
            raise
    
    async def _cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        
        try:
            if self.lifecycle_manager:
                await self.lifecycle_manager.stop()
                print("✅ 生命周期管理器已停止")
            
            if self.load_balancer:
                await self.load_balancer.stop()
                print("✅ 负载均衡器已停止")
            
            if self.service_registry:
                await self.service_registry.stop()
                print("✅ 服务注册表已停止")
            
            print("✅ 所有资源清理完成")
            
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


async def main():
    """主函数"""
    demo = ApplicationOrchestrationDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示失败: {e}")
        logger.error(f"演示失败: {e}")
    finally:
        print("\n🎉 应用编排层演示结束") 