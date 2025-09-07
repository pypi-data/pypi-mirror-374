# 🔌 适配器层 (Adapter Layer)

## 📋 概述

适配器层是Agent Development Center架构的第2层，负责多框架适配和转换机制。这一层提供了统一的接口，使ADC能够与各种AI Agent框架无缝集成。

## 🎯 核心功能

### 1. 多框架支持
- **AutoGen适配器** - 微软AutoGen框架集成
- **LangGraph适配器** - LangChain生态集成
- **OpenAI适配器** - OpenAI GPT系列模型集成
- **CrewAI适配器** - CrewAI协作框架集成
- **自定义适配器** - 支持第三方框架扩展

### 2. 统一接口抽象
- **标准化接口** - 统一的Agent调用接口
- **能力映射** - 框架能力到ADC能力的映射
- **参数转换** - 自动参数格式转换
- **错误处理** - 统一的错误处理机制

### 3. 动态适配
- **运行时发现** - 自动发现可用框架
- **能力检测** - 动态检测框架能力
- **优雅降级** - 支持能力缺失时的降级处理

## 📚 文档结构

### 核心文档
- **[README.md](./README.md)** - 适配器层总览 (当前文档)
- **[autogen_adapter.md](./autogen_adapter.md)** - AutoGen适配器详细设计
- **[langchain_adapter.md](./langchain_adapter.md)** - LangGraph适配器详细设计
- **[crewai_adapter.md](./crewai_adapter.md)** - CrewAI适配器详细设计

### 文档说明
- **autogen_adapter.md** - 微软AutoGen框架的完整集成方案
- **langchain_adapter.md** - LangChain生态系统的深度集成
- **crewai_adapter.md** - CrewAI协作框架的完整支持

## 🔧 技术特性

### 适配器架构
```
┌─────────────────────────────────────────────────────────────┐
│                    适配器层 (Adapter Layer)                   │
├─────────────────────────────────────────────────────────────┤
│  AutoGen  │  LangGraph  │  OpenAI  │  CrewAI  │  Custom   │
│  Adapter  │  Adapter    │ Adapter  │ Adapter  │ Adapter   │
└─────────────────────────────────────────────────────────────┘
                              │ 统一接口抽象
┌─────────────────────────────────────────────────────────────┐
│                  框架抽象层 (Framework Layer)                │
└─────────────────────────────────────────────────────────────┘
```

### 核心接口
- **AgentAdapter** - 基础适配器接口
- **CapabilityMapper** - 能力映射器
- **ParameterConverter** - 参数转换器
- **ErrorHandler** - 错误处理器

## 📊 实现状态

| 适配器 | 状态 | 完成度 | 特性支持 |
|--------|------|--------|----------|
| **AutoGen** | ✅ 完成 | 95% | 完整Agent协作支持 |
| **LangGraph** | ✅ 完成 | 90% | 工作流和状态管理 |
| **OpenAI** | ✅ 完成 | 85% | GPT系列模型集成 |
| **CrewAI** | ✅ 完成 | 80% | 团队协作框架 |
| **自定义** | 🟡 基础 | 60% | 基础扩展支持 |

## 🚀 快速开始

### 1. 基本使用
```python
from layers.adapter import AutoGenAdapter, LangGraphAdapter

# 创建AutoGen适配器
autogen_adapter = AutoGenAdapter()

# 创建LangGraph适配器
langgraph_adapter = LangGraphAdapter()
```

### 2. 能力检测
```python
# 检测框架能力
capabilities = autogen_adapter.get_capabilities()
print(f"AutoGen支持的能力: {capabilities}")
```

### 3. 动态适配
```python
# 根据任务选择最佳适配器
best_adapter = adapter_registry.get_best_adapter(task_requirements)
```

## 🔗 相关链接

### 架构文档
- [主架构文档](../ARCHITECTURE_DESIGN.md)
- [框架抽象层](../framework_abstraction_layer/)
- [基础设施层](../infrastructure_layer/)

### 技术文档
- [API接口文档](../layers/adapter/)
- [示例代码](../examples/)
- [测试用例](../tests/unit/adapter/)

### 外部资源
- [AutoGen官方文档](https://microsoft.github.io/autogen/)
- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [CrewAI官方文档](https://docs.crewai.com/)

## 📈 发展计划

### 短期目标 (1-2个月)
- [ ] 完善OpenAI适配器的流式响应支持
- [ ] 增强CrewAI适配器的团队协作功能
- [ ] 优化参数转换的性能

### 中期目标 (3-6个月)
- [ ] 添加更多第三方框架支持
- [ ] 实现智能适配器选择算法
- [ ] 建立适配器性能基准测试

### 长期目标 (6-12个月)
- [ ] 支持跨框架Agent协作
- [ ] 实现自适应能力映射
- [ ] 建立适配器生态系统

## 🐛 常见问题

### Q: 如何添加新的框架支持？
A: 继承`AgentAdapter`基类，实现必要的接口方法，然后在适配器注册表中注册。

### Q: 支持哪些参数类型？
A: 支持Python基本类型、复杂对象、以及框架特定的参数类型，自动进行类型转换。

### Q: 如何处理框架版本差异？
A: 通过版本检测和兼容性映射，自动适配不同版本的框架API。

## 📞 技术支持

### 维护团队
- **适配器开发**: Adapter Development Team
- **框架集成**: Framework Integration Team
- **技术支持**: Technical Support Team

### 反馈渠道
- **问题报告**: 通过GitHub Issues
- **功能建议**: 通过项目讨论区
- **技术咨询**: 通过开发团队

---

## 📋 文档维护

### 更新频率
- **核心功能**: 每月更新
- **新框架支持**: 功能完成时更新
- **性能优化**: 优化完成时更新

### 版本历史
| 版本 | 日期 | 更新内容 | 维护人 |
|------|------|----------|--------|
| v2.0 | 2025-08-23 | 统一文档格式，完善导航 | Documentation Team |
| v1.5 | 2025-08-15 | 添加CrewAI适配器支持 | Adapter Team |
| v1.0 | 2025-07-01 | 初始版本发布 | Development Team |

---

*最后更新: 2025年8月23日*
*维护团队: Agent Development Center Adapter Team*
*文档版本: v2.0*
class BaseAdapter:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.initialized = False
        
    def initialize(self) -> bool:
        """初始化适配器，加载必要资源"""
        pass
        
    def shutdown(self) -> bool:
        """关闭适配器，释放资源"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """返回此适配器支持的能力列表"""
        pass
    
    def create_agent(self, agent_config: dict) -> 'AgentInterface':
        """创建一个Agent实例"""
        pass
    
    def create_task(self, task_config: dict) -> 'TaskInterface':
        """创建一个任务实例"""
        pass
    
    def execute_task(self, agent: 'AgentInterface', task: 'TaskInterface') -> 'ResultInterface':
        """执行指定任务"""
        pass
```

### 3.2 AdapterRegistry

管理所有已注册的适配器，提供适配器的注册、发现和生命周期管理功能。

```python
class AdapterRegistry:
    def __init__(self):
        self._adapters = {}
        self._capabilities_map = {}
        
    def register(self, name: str, adapter_class: Type[BaseAdapter], capabilities: List[str] = None) -> bool:
        """注册一个适配器"""
        pass
        
    def unregister(self, name: str) -> bool:
        """注销一个适配器"""
        pass
    
    def get_adapter(self, name: str) -> Optional[BaseAdapter]:
        """获取指定名称的适配器实例"""
        pass
    
    def find_adapters_by_capability(self, capability: str) -> List[str]:
        """根据能力查找支持的适配器"""
        pass
    
    def initialize_all(self) -> bool:
        """初始化所有已注册的适配器"""
        pass
    
    def shutdown_all(self) -> bool:
        """关闭所有已注册的适配器"""
        pass
```

### 3.3 FrameworkCapability

定义了统一的能力模型，用于描述和映射各框架的特性和功能。

```python
class CapabilityLevel(Enum):
    BASIC = 1       # 基础能力
    STANDARD = 2    # 标准能力
    ADVANCED = 3    # 高级能力
    EXPERIMENTAL = 4 # 实验性能力

class FrameworkCapability:
    def __init__(self, name: str, description: str, level: CapabilityLevel = CapabilityLevel.STANDARD):
        self.name = name
        self.description = description
        self.level = level
        self.parameters = {}
        
    def add_parameter(self, name: str, description: str, required: bool = False, default_value = None):
        """添加能力参数定义"""
        self.parameters[name] = {
            'description': description,
            'required': required,
            'default': default_value
        }
        return self
```

### 3.4 ConceptTranslator

负责在不同框架的概念模型之间进行转换，确保概念的一致性。

```python
class ConceptTranslator:
    def __init__(self, source_framework: str, target_framework: str):
        self.source = source_framework
        self.target = target_framework
        self._translation_maps = self._load_translation_maps()
        
    def _load_translation_maps(self) -> dict:
        """加载概念转换映射表"""
        pass
        
    def translate_agent_config(self, config: dict) -> dict:
        """转换Agent配置"""
        pass
    
    def translate_task_config(self, config: dict) -> dict:
        """转换任务配置"""
        pass
    
    def translate_result(self, result: Any) -> 'ResultInterface':
        """转换执行结果"""
        pass
```

### 3.5 PerformanceOptimizer

提供性能优化功能，减少适配过程中的性能开销。

```python
class PerformanceOptimizer:
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
        self.metrics = {}
        self.optimizations = self._load_optimizations()
        
    def _load_optimizations(self) -> dict:
        """加载针对特定适配器的优化策略""\