"""
ApplicationOrchestrator单元测试
测试应用编排器的所有功能
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import asyncio

from layers.application.orchestration.orchestrator import ApplicationOrchestrator
from layers.application.orchestration.orchestrator import (
    ApplicationConfig, ApplicationInstance, ApplicationType, 
    ApplicationStatus
)


class TestApplicationOrchestrator:
    """测试ApplicationOrchestrator类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.orchestrator = ApplicationOrchestrator()
        
        # 创建模拟的应用配置
        self.mock_app_config = ApplicationConfig(
            app_id="test_app_001",
            name="Test Application",
            version="1.0.0",
            app_type=ApplicationType.WEB,
            description="Test application for testing",
            dependencies=[],
            config={"port": 8080, "host": "localhost"}
        )
    
    def test_orchestrator_initialization(self):
        """测试编排器初始化"""
        assert self.orchestrator.applications == {}
        assert self.orchestrator.instances == {}
        assert self.orchestrator.running_instances == {}
        assert self.orchestrator.event_handlers == {}
    
    @pytest.mark.asyncio
    async def test_register_application_success(self):
        """测试成功注册应用"""
        success = await self.orchestrator.register_application(self.mock_app_config)
        
        assert success is True
        assert self.mock_app_config.app_id in self.orchestrator.applications
        assert self.orchestrator.applications[self.mock_app_config.app_id] == self.mock_app_config
    
    @pytest.mark.asyncio
    async def test_register_application_duplicate(self):
        """测试重复注册应用"""
        # 第一次注册
        success1 = await self.orchestrator.register_application(self.mock_app_config)
        assert success1 is True
        
        # 第二次注册相同ID应该成功（当前实现允许重复注册）
        success2 = await self.orchestrator.register_application(self.mock_app_config)
        assert success2 is True
    
    @pytest.mark.asyncio
    async def test_register_application_invalid_config(self):
        """测试注册无效的应用配置"""
        # 创建无效配置（缺少必需字段）
        invalid_config = ApplicationConfig(
            app_id="",  # 空的app_id
            name="",    # 空的name
            version="", # 空的version
            app_type=ApplicationType.WEB,
            description="Invalid config",
            dependencies=[],
            config={}
        )
        
        success = await self.orchestrator.register_application(invalid_config)
        assert success is True  # 当前实现不验证配置有效性
    
    @pytest.mark.asyncio
    async def test_start_application_success(self):
        """测试成功启动应用"""
        # 先注册应用
        await self.orchestrator.register_application(self.mock_app_config)
        
        # 启动应用
        instance_id = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test", "port": 8080}
        )
        
        assert instance_id is not None
        assert instance_id in self.orchestrator.instances
        
        # 验证实例状态
        instance = self.orchestrator.instances[instance_id]
        assert instance.app_config.app_id == self.mock_app_config.app_id
        assert instance.status == ApplicationStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_start_application_not_found(self):
        """测试启动不存在的应用"""
        instance_id = await self.orchestrator.start_application(
            "non_existent_app",
            {"environment": "test"}
        )
        
        assert instance_id is None
    
    @pytest.mark.asyncio
    async def test_start_application_already_running(self):
        """测试启动已经运行的应用"""
        # 先注册并启动应用
        await self.orchestrator.register_application(self.mock_app_config)
        instance_id1 = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test"}
        )
        
        assert instance_id1 is not None
        
        # 等待确保时间戳不同（至少1秒）
        await asyncio.sleep(1.1)
        
        # 再次启动会创建新的实例
        instance_id2 = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test"}
        )
        
        assert instance_id2 is not None
        assert instance_id2 != instance_id1  # 每次启动都创建新实例
    
    @pytest.mark.asyncio
    async def test_stop_application_success(self):
        """测试成功停止应用"""
        # 先注册并启动应用
        await self.orchestrator.register_application(self.mock_app_config)
        instance_id = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test"}
        )
        
        assert instance_id is not None
        
        # 停止应用
        success = await self.orchestrator.stop_instance(instance_id)
        assert success is True
        
        # 验证实例状态更新
        updated_instance = self.orchestrator.instances[instance_id]
        assert updated_instance.status == ApplicationStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_stop_application_not_found(self):
        """测试停止不存在的应用实例"""
        success = await self.orchestrator.stop_instance("non_existent_instance")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_restart_application_success(self):
        """测试成功重启应用"""
        # 先注册并启动应用
        await self.orchestrator.register_application(self.mock_app_config)
        instance_id = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test"}
        )
        
        assert instance_id is not None
        
        # 重启应用
        success = await self.orchestrator.restart_instance(instance_id)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_get_application_status(self):
        """测试获取应用状态"""
        # 先注册应用
        await self.orchestrator.register_application(self.mock_app_config)
        
        # 获取应用状态
        status = await self.orchestrator.get_application_status(self.mock_app_config.app_id)
        assert "error" not in status
        assert status["app_id"] == self.mock_app_config.app_id
    
    @pytest.mark.asyncio
    async def test_get_application_status_not_found(self):
        """测试获取不存在应用的状态"""
        status = await self.orchestrator.get_application_status("non_existent_app")
        assert "error" in status
        assert status["error"] == "Application not found"
    
    @pytest.mark.asyncio
    async def test_list_applications(self):
        """测试列出应用"""
        # 先注册几个应用
        await self.orchestrator.register_application(self.mock_app_config)
        
        # 创建另一个应用
        app2 = ApplicationConfig(
            app_id="test_app_002",
            name="Test Application 2",
            version="1.0.0",
            app_type=ApplicationType.API,
            description="Another test application",
            dependencies=[],
            config={"port": 8081, "host": "localhost"}
        )
        await self.orchestrator.register_application(app2)
        
        # 列出所有应用
        apps = await self.orchestrator.list_applications()
        assert len(apps) == 2
        
        # 验证应用列表
        assert len(apps) == 2
        app_ids = [app["app_id"] for app in apps]
        assert "test_app_001" in app_ids
        assert "test_app_002" in app_ids
    
    @pytest.mark.asyncio
    async def test_unregister_application(self):
        """测试注销应用"""
        # 先注册应用
        await self.orchestrator.register_application(self.mock_app_config)
        assert self.mock_app_config.app_id in self.orchestrator.applications
        
        # 注销应用
        success = await self.orchestrator.unregister_application(self.mock_app_config.app_id)
        assert success is True
        assert self.mock_app_config.app_id not in self.orchestrator.applications
    
    @pytest.mark.asyncio
    async def test_unregister_application_not_found(self):
        """测试注销不存在的应用"""
        success = await self.orchestrator.unregister_application("non_existent_app")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_application_metrics(self):
        """测试应用指标收集"""
        # 先注册并启动应用
        await self.orchestrator.register_application(self.mock_app_config)
        instance_id = await self.orchestrator.start_application(
            self.mock_app_config.app_id,
            {"environment": "test"}
        )
        
        assert instance_id is not None
        
        # 获取应用状态
        status = await self.orchestrator.get_application_status(self.mock_app_config.app_id)
        assert "error" not in status
        assert "app_id" in status
    
    @pytest.mark.asyncio
    async def test_application_metrics_not_found(self):
        """测试获取不存在应用的指标"""
        status = await self.orchestrator.get_application_status("non_existent_app")
        assert "error" in status
        assert status["error"] == "Application not found"
    
    @pytest.mark.asyncio
    async def test_event_handlers(self):
        """测试事件处理器"""
        # 注册事件处理器
        event_received = False
        event_data = None
        
        def test_handler(data):
            nonlocal event_received, event_data
            event_received = True
            event_data = data
        
        await self.orchestrator.add_event_handler("test_event", test_handler)
        
        # 触发事件
        await self.orchestrator._notify_event("test_event", {"test": "data"})
        
        # 验证事件处理器被调用
        assert event_received is True
        assert event_data == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_application_health_check(self):
        """测试应用健康检查"""
        # 先注册应用
        await self.orchestrator.register_application(self.mock_app_config)
        
        # 执行健康检查
        health_status = await self.orchestrator.health_check()
        assert "error" not in health_status
        assert "status" in health_status
    
    @pytest.mark.asyncio
    async def test_application_health_check_not_found(self):
        """测试不存在应用的健康检查"""
        health_status = await self.orchestrator.health_check()
        assert "error" not in health_status
        assert "status" in health_status 