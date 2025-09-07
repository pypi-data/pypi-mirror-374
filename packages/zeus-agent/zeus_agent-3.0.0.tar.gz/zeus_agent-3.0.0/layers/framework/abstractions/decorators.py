"""
ADC平台核心装饰器系统
提供能力声明、知识增强、上下文感知等功能装饰器

设计理念：
- 声明式编程：通过装饰器声明Agent能力和特性
- 知识库优先：自动集成知识库检索和增强
- 上下文感知：智能管理对话和任务上下文
"""

import asyncio
import functools
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CapabilityType(Enum):
    """能力类型枚举"""
    DESIGN = "design"           # 设计能力
    VERIFICATION = "verification"  # 验证能力
    OPTIMIZATION = "optimization"  # 优化能力
    ANALYSIS = "analysis"       # 分析能力
    GENERATION = "generation"   # 生成能力
    DEBUGGING = "debugging"     # 调试能力
    CONSULTATION = "consultation"  # 咨询能力


class KnowledgeDomain(Enum):
    """知识领域枚举"""
    FPGA = "fpga"              # FPGA相关知识
    HDL = "hdl"                # HDL语言知识
    VERIFICATION = "verification"  # 验证方法学
    PROTOCOLS = "protocols"     # 通信协议
    OPTIMIZATION = "optimization"  # 优化技术
    DEBUGGING = "debugging"     # 调试技术
    TOOLS = "tools"            # EDA工具


@dataclass
class CapabilityMetadata:
    """能力元数据"""
    name: str
    capability_type: CapabilityType
    description: str
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.7
    max_retry_count: int = 3
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeEnhancementConfig:
    """知识增强配置"""
    domains: List[KnowledgeDomain]
    retrieval_count: int = 5
    confidence_threshold: float = 0.6
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_context_injection: bool = True
    context_window_size: int = 2000


@dataclass
class ContextAwarenessConfig:
    """上下文感知配置"""
    enable_conversation_history: bool = True
    history_window_size: int = 10
    enable_task_context: bool = True
    enable_user_preferences: bool = True
    enable_session_memory: bool = True
    context_expiry_seconds: int = 7200


# 全局注册表
_capability_registry: Dict[str, CapabilityMetadata] = {}
_method_capabilities: Dict[str, List[str]] = {}


def capability(
    name: str,
    capability_type: CapabilityType,
    description: str,
    input_types: List[str] = None,
    output_types: List[str] = None,
    prerequisites: List[str] = None,
    confidence_threshold: float = 0.7,
    max_retry_count: int = 3,
    timeout_seconds: int = 30
):
    """
    能力装饰器 - 声明方法的能力特性
    
    Args:
        name: 能力名称
        capability_type: 能力类型
        description: 能力描述
        input_types: 输入类型列表
        output_types: 输出类型列表
        prerequisites: 前置条件
        confidence_threshold: 置信度阈值
        max_retry_count: 最大重试次数
        timeout_seconds: 超时时间
    
    Example:
        @capability(
            name="verilog_code_generation",
            capability_type=CapabilityType.GENERATION,
            description="生成Verilog HDL代码",
            input_types=["natural_language", "specification"],
            output_types=["verilog_code", "testbench"],
            confidence_threshold=0.8
        )
        async def generate_verilog_code(self, request: str) -> str:
            # 实现代码生成逻辑
            pass
    """
    def decorator(func: Callable) -> Callable:
        # 创建能力元数据
        metadata = CapabilityMetadata(
            name=name,
            capability_type=capability_type,
            description=description,
            input_types=input_types or [],
            output_types=output_types or [],
            prerequisites=prerequisites or [],
            confidence_threshold=confidence_threshold,
            max_retry_count=max_retry_count,
            timeout_seconds=timeout_seconds
        )
        
        # 注册能力
        _capability_registry[name] = metadata
        
        # 记录方法的能力
        method_key = f"{func.__module__}.{func.__qualname__}"
        if method_key not in _method_capabilities:
            _method_capabilities[method_key] = []
        _method_capabilities[method_key].append(name)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            retry_count = 0
            
            logger.info(f"🚀 执行能力: {name} ({capability_type.value})")
            
            while retry_count < max_retry_count:
                try:
                    # 设置超时
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                    
                    execution_time = time.time() - start_time
                    logger.info(f"✅ 能力执行成功: {name} (耗时: {execution_time:.2f}s)")
                    
                    # 添加执行元数据
                    if hasattr(result, '__dict__'):
                        result._capability_metadata = {
                            'capability_name': name,
                            'execution_time': execution_time,
                            'retry_count': retry_count,
                            'confidence': getattr(result, 'confidence', 1.0)
                        }
                    
                    return result
                    
                except asyncio.TimeoutError:
                    retry_count += 1
                    logger.warning(f"⏰ 能力执行超时: {name} (重试 {retry_count}/{max_retry_count})")
                    if retry_count >= max_retry_count:
                        raise
                        
                except Exception as e:
                    retry_count += 1
                    logger.error(f"❌ 能力执行失败: {name} (重试 {retry_count}/{max_retry_count}): {e}")
                    if retry_count >= max_retry_count:
                        raise
                    
                    # 短暂等待后重试
                    await asyncio.sleep(0.5 * retry_count)
            
        # 保存元数据到函数属性
        wrapper._capability_metadata = metadata
        wrapper._is_capability = True
        
        return wrapper
    
    return decorator


def knowledge_enhanced(
    domains: List[KnowledgeDomain],
    retrieval_count: int = 5,
    confidence_threshold: float = 0.6,
    enable_caching: bool = True,
    cache_ttl_seconds: int = 3600,
    enable_context_injection: bool = True,
    context_window_size: int = 2000
):
    """
    知识增强装饰器 - 自动检索和注入相关知识
    
    Args:
        domains: 知识领域列表
        retrieval_count: 检索数量
        confidence_threshold: 置信度阈值
        enable_caching: 启用缓存
        cache_ttl_seconds: 缓存TTL
        enable_context_injection: 启用上下文注入
        context_window_size: 上下文窗口大小
    
    Example:
        @knowledge_enhanced(
            domains=[KnowledgeDomain.FPGA, KnowledgeDomain.HDL],
            retrieval_count=3,
            confidence_threshold=0.7
        )
        async def design_fpga_module(self, specification: str) -> str:
            # 方法执行前会自动检索相关FPGA和HDL知识
            # 知识会注入到self.enhanced_context中
            pass
    """
    def decorator(func: Callable) -> Callable:
        config = KnowledgeEnhancementConfig(
            domains=domains,
            retrieval_count=retrieval_count,
            confidence_threshold=confidence_threshold,
            enable_caching=enable_caching,
            cache_ttl_seconds=cache_ttl_seconds,
            enable_context_injection=enable_context_injection,
            context_window_size=context_window_size
        )
        
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            logger.info(f"🧠 启用知识增强: {func.__name__} (领域: {[d.value for d in domains]})")
            
            try:
                # 提取查询内容
                query_text = _extract_query_from_args(args, kwargs)
                
                # 检索相关知识
                if hasattr(self, 'knowledge_service'):
                    enhanced_knowledge = await self._retrieve_knowledge(
                        query_text, config
                    )
                    
                    # 注入增强上下文
                    if enable_context_injection:
                        self.enhanced_context = enhanced_knowledge
                        logger.debug(f"💡 已注入 {len(enhanced_knowledge)} 条知识")
                
                # 执行原始方法
                result = await func(self, *args, **kwargs)
                
                # 清理增强上下文
                if hasattr(self, 'enhanced_context'):
                    delattr(self, 'enhanced_context')
                
                return result
                
            except Exception as e:
                logger.error(f"❌ 知识增强失败: {e}")
                # 降级执行原始方法
                return await func(self, *args, **kwargs)
        
        # 保存配置到函数属性
        wrapper._knowledge_enhancement_config = config
        wrapper._is_knowledge_enhanced = True
        
        return wrapper
    
    return decorator


def context_aware(
    enable_conversation_history: bool = True,
    history_window_size: int = 10,
    enable_task_context: bool = True,
    enable_user_preferences: bool = True,
    enable_session_memory: bool = True,
    context_expiry_seconds: int = 7200
):
    """
    上下文感知装饰器 - 自动管理和注入上下文信息
    
    Args:
        enable_conversation_history: 启用对话历史
        history_window_size: 历史窗口大小
        enable_task_context: 启用任务上下文
        enable_user_preferences: 启用用户偏好
        enable_session_memory: 启用会话记忆
        context_expiry_seconds: 上下文过期时间
    
    Example:
        @context_aware(
            enable_conversation_history=True,
            history_window_size=5,
            enable_task_context=True
        )
        async def continue_design_task(self, new_requirement: str) -> str:
            # 方法执行前会自动加载相关上下文
            # 上下文信息可通过self.context访问
            pass
    """
    def decorator(func: Callable) -> Callable:
        config = ContextAwarenessConfig(
            enable_conversation_history=enable_conversation_history,
            history_window_size=history_window_size,
            enable_task_context=enable_task_context,
            enable_user_preferences=enable_user_preferences,
            enable_session_memory=enable_session_memory,
            context_expiry_seconds=context_expiry_seconds
        )
        
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            logger.info(f"🎯 启用上下文感知: {func.__name__}")
            
            try:
                # 加载上下文
                if hasattr(self, 'context_manager'):
                    context = await self._load_context(config)
                    self.current_context = context
                    logger.debug(f"📝 已加载上下文: {len(context.get('history', []))} 条历史")
                
                # 执行原始方法
                result = await func(self, *args, **kwargs)
                
                # 更新上下文
                if hasattr(self, 'context_manager'):
                    await self._update_context(func.__name__, args, kwargs, result)
                
                return result
                
            except Exception as e:
                logger.error(f"❌ 上下文感知失败: {e}")
                # 降级执行原始方法
                return await func(self, *args, **kwargs)
        
        # 保存配置到函数属性
        wrapper._context_awareness_config = config
        wrapper._is_context_aware = True
        
        return wrapper
    
    return decorator


# 辅助函数

def _extract_query_from_args(args, kwargs) -> str:
    """从参数中提取查询文本"""
    query_parts = []
    
    # 从位置参数提取
    for arg in args:
        if isinstance(arg, str) and len(arg) > 10:  # 假设有意义的查询至少10个字符
            query_parts.append(arg)
    
    # 从关键字参数提取
    for key, value in kwargs.items():
        if isinstance(value, str) and len(value) > 10:
            query_parts.append(f"{key}: {value}")
    
    return " ".join(query_parts)


def get_capability_metadata(capability_name: str) -> Optional[CapabilityMetadata]:
    """获取能力元数据"""
    return _capability_registry.get(capability_name)


def get_method_capabilities(method_key: str) -> List[str]:
    """获取方法的能力列表"""
    return _method_capabilities.get(method_key, [])


def list_all_capabilities() -> Dict[str, CapabilityMetadata]:
    """列出所有注册的能力"""
    return _capability_registry.copy()


def capability_exists(capability_name: str) -> bool:
    """检查能力是否存在"""
    return capability_name in _capability_registry


# 能力发现装饰器
def discoverable(category: str = "general", priority: int = 0):
    """
    可发现装饰器 - 标记方法为可被动态发现的能力
    
    Args:
        category: 能力分类
        priority: 优先级（数字越大优先级越高）
    """
    def decorator(func: Callable) -> Callable:
        func._is_discoverable = True
        func._discovery_category = category
        func._discovery_priority = priority
        return func
    
    return decorator


# 性能监控装饰器
def performance_monitored(
    enable_timing: bool = True,
    enable_memory_tracking: bool = False,
    enable_metrics_collection: bool = True
):
    """
    性能监控装饰器 - 自动收集方法执行的性能指标
    
    Args:
        enable_timing: 启用执行时间监控
        enable_memory_tracking: 启用内存使用监控
        enable_metrics_collection: 启用指标收集
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            if enable_timing:
                logger.debug(f"⏱️ 开始执行: {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                
                if enable_timing:
                    execution_time = time.time() - start_time
                    logger.info(f"⏱️ 执行完成: {func.__name__} (耗时: {execution_time:.3f}s)")
                
                return result
                
            except Exception as e:
                if enable_timing:
                    execution_time = time.time() - start_time
                    logger.error(f"⏱️ 执行失败: {func.__name__} (耗时: {execution_time:.3f}s): {e}")
                raise
        
        wrapper._is_performance_monitored = True
        return wrapper
    
    return decorator


# 组合装饰器 - 常用组合
def fpga_expert_method(
    capability_name: str,
    capability_type: CapabilityType,
    description: str,
    knowledge_domains: List[KnowledgeDomain] = None,
    enable_context: bool = True
):
    """
    FPGA专家方法装饰器 - 组合常用装饰器
    
    这是一个便利装饰器，组合了capability、knowledge_enhanced和context_aware
    """
    def decorator(func: Callable) -> Callable:
        # 应用多个装饰器
        enhanced_func = func
        
        # 1. 性能监控
        enhanced_func = performance_monitored()(enhanced_func)
        
        # 2. 上下文感知
        if enable_context:
            enhanced_func = context_aware()(enhanced_func)
        
        # 3. 知识增强
        if knowledge_domains:
            enhanced_func = knowledge_enhanced(domains=knowledge_domains)(enhanced_func)
        
        # 4. 能力声明
        enhanced_func = capability(
            name=capability_name,
            capability_type=capability_type,
            description=description
        )(enhanced_func)
        
        # 5. 可发现性
        enhanced_func = discoverable(category="fpga_expert")(enhanced_func)
        
        return enhanced_func
    
    return decorator 