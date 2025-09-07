# Agent Development Center - 贡献指南

感谢您对 Agent Development Center (ADC) 项目的关注！本指南将帮助您了解如何为这个基于7层架构的下一代AI Agent开发框架做出贡献。

## 📋 贡献方式

### 🐛 报告问题

- 使用 GitHub Issues 报告 Bug
- 提供详细的问题描述和复现步骤
- 包含环境信息（操作系统、Python 版本、依赖包版本等）
- 如果涉及特定适配器，请标明使用的框架（OpenAI、AutoGen等）
- 附上相关的日志信息和错误堆栈

### 💡 功能建议

- 在 Issues 中提出新功能建议
- 详细描述功能需求和使用场景
- 讨论实现方案的可行性
- 考虑7层架构中的合适位置
- 评估对现有功能的影响

### 🔧 代码贡献

1. **Fork 项目**到您的 GitHub 账户
2. **创建分支**: `git checkout -b feature/your-feature-name`
3. **提交更改**: `git commit -m "feat: add some feature"`
4. **推送分支**: `git push origin feature/your-feature-name`
5. **创建 Pull Request**

## 🏗️ 7层架构概述

ADC 采用清晰的7层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│                     开发体验层 (DevX Layer)                  │
│  CLI Tools  │  Interactive Shell  │  Web Studio  │  API Docs │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   应用编排层 (Application Layer)              │
│   Project Mgmt  │  Team Collab  │  Workflow  │  Integration  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  业务能力层 (Business Capability Layer)       │
│ Collaboration │ Workflow Engine │ Tool Integration │ Advanced │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   认知架构层 (Cognitive Architecture)          │
│ Perception │ Reasoning │ Memory │ Learning │ Communication   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   框架抽象层 (Framework Abstraction)          │
│ Universal Agent │ Task │ Context │ Result │ Capability Mgmt  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    适配器层 (Adapter Layer)                   │
│  AutoGen  │  OpenAI  │  LangGraph  │  CrewAI  │  Custom...   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   基础设施层 (Infrastructure Layer)            │
│ Observability │ Security │ Scalability │ Reliability │ Perf  │
└─────────────────────────────────────────────────────────────┘
```

## 📝 开发规范

### 项目结构

```
layers/
├── infrastructure/           # 基础设施层
│   ├── logging/             # 智能日志系统
│   ├── config/              # 配置管理
│   ├── cache/               # 缓存系统
│   ├── security/            # 安全管理
│   └── performance/         # 性能监控
├── adapter/                 # 适配器层
│   ├── base.py              # 基础适配器
│   ├── autogen/             # AutoGen适配器
│   ├── openai/              # OpenAI适配器
│   └── registry/            # 适配器注册系统
├── framework/               # 框架抽象层
│   └── abstractions/        # 通用抽象接口
│       ├── agent.py         # UniversalAgent
│       ├── task.py          # UniversalTask
│       ├── context.py       # UniversalContext
│       ├── result.py        # UniversalResult
│       └── enhanced_agent.py # 增强Agent接口
├── cognitive/               # 认知架构层
│   ├── cognitive_agent.py   # 认知Agent
│   ├── memory.py            # 记忆系统
│   ├── learning.py          # 学习系统
│   └── communication.py     # 通信系统
├── business/                # 业务能力层
│   ├── teams/               # 团队协作管理
│   │   └── collaboration_manager.py
│   └── workflows/           # 工作流引擎
│       └── workflow_engine.py
├── application/             # 应用编排层
│   ├── cli/                 # CLI应用
│   └── web/                 # Web应用
└── README.md                # 架构文档
```

### 命名规范

- **文件名**: 使用 `snake_case` (如: `collaboration_manager.py`)
- **目录名**: 使用 `snake_case`
- **Python 模块**: 使用 `snake_case`
- **类名**: 使用 `PascalCase` (如: `UniversalAgent`, `CollaborationManager`)
- **函数/变量**: 使用 `snake_case`
- **常量**: 使用 `UPPER_SNAKE_CASE`

### 代码风格

- **Python**: 遵循 PEP 8 规范
- **注释**: 使用英文，避免中英文混用（根据用户规则要求）
- **文档字符串**: 使用 Google 风格
- **类型提示**: 必须使用 Python 类型提示
- **异步代码**: 优先使用 async/await 模式

### 层级开发规范

#### 基础设施层 (Infrastructure Layer)
- 提供系统级服务（日志、配置、缓存、安全）
- 必须保证高可用性和性能
- 使用工厂模式和单例模式
- 完整的错误处理和监控

#### 适配器层 (Adapter Layer)
- 继承 `BaseAdapter` 并实现所有必要方法
- 提供框架特定的实现细节
- 统一的错误处理和性能优化
- 完整的测试覆盖

#### 框架抽象层 (Framework Abstraction)
- 定义通用接口和数据模型
- 保持框架无关性
- 提供默认实现和扩展点
- 完整的类型注解

#### 认知架构层 (Cognitive Architecture)
- 实现Agent的认知能力
- 模块化设计（感知、推理、记忆、学习、通信）
- 支持认知状态管理
- 可配置的认知策略

#### 业务能力层 (Business Capability)
- 实现高级业务功能
- 支持多种协作模式和工作流类型
- 提供可扩展的业务逻辑
- 完整的业务流程监控

#### 应用编排层 (Application Layer)
- 组装底层能力为完整应用
- 提供用户友好的接口
- 支持多种部署模式
- 完整的应用生命周期管理

#### 开发体验层 (DevX Layer)
- 提供优秀的开发者体验
- 现代化的工具和界面
- 完整的文档和示例
- 友好的错误提示

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明:**

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具、辅助工具更新
- `perf`: 性能优化
- `security`: 安全相关

**作用域说明:**

- `infrastructure`: 基础设施层
- `adapter`: 适配器层
- `framework`: 框架抽象层
- `cognitive`: 认知架构层
- `business`: 业务能力层
- `application`: 应用编排层
- `devx`: 开发体验层
- `openai`: OpenAI相关
- `autogen`: AutoGen相关
- `cli`: 命令行界面
- `docs`: 文档

**示例:**

```
feat(adapter): add LangGraph adapter implementation
fix(business): resolve workflow execution deadlock
docs(framework): update UniversalAgent API documentation
refactor(cognitive): simplify memory management logic
test(infrastructure): add comprehensive logging tests
perf(adapter): optimize OpenAI API call batching
security(infrastructure): add encryption for sensitive config
```

## 🧪 测试要求

### 测试覆盖

- 新功能必须包含相应的测试用例
- 适配器必须有完整的集成测试
- 确保现有测试通过
- 测试覆盖率不低于 85%

### 测试类型

- **单元测试**: 测试独立的函数和类
- **集成测试**: 测试层间交互和适配器集成
- **功能测试**: 测试完整的Agent工作流
- **性能测试**: 测试系统性能和资源使用
- **安全测试**: 测试安全机制和漏洞防护

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定层的测试
python -m pytest tests/test_infrastructure/
python -m pytest tests/test_adapter/
python -m pytest tests/test_business/

# 运行特定适配器测试
python -m pytest tests/test_adapter/test_openai_adapter.py

# 查看测试覆盖率
python -m pytest --cov=layers --cov-report=html

# 运行性能测试
python -m pytest tests/performance/ -v

# 运行安全测试
python -m pytest tests/security/ -v
```

## 🔌 适配器开发

### 开发新的适配器

1. **创建适配器目录**

   ```bash
   mkdir -p layers/adapter/your_framework/
   touch layers/adapter/your_framework/__init__.py
   touch layers/adapter/your_framework/adapter.py
   touch layers/adapter/your_framework/agent_wrapper.py
   ```

2. **实现基础接口**

   ```python
   from ..base import BaseAdapter
   from ...framework.abstractions import UniversalAgent, UniversalTask, UniversalContext, UniversalResult

   class YourFrameworkAdapter(BaseAdapter):
       async def initialize(self, config: Dict[str, Any]) -> None:
           """初始化适配器"""
           pass

       async def create_agent(self, agent_config: Dict[str, Any]) -> UniversalAgent:
           """创建Agent"""
           pass

       async def execute_task(self, task: UniversalTask, context: UniversalContext) -> UniversalResult:
           """执行任务"""
           pass

       def get_framework_capabilities(self) -> List[AdapterCapability]:
           """获取框架能力"""
           pass
   ```

3. **注册适配器**

   ```python
   # 在 layers/adapter/__init__.py 中添加
   from .your_framework import YourFrameworkAdapter

   __all__ = [
       "BaseAdapter",
       "AutoGenAdapter",
       "OpenAIAdapter",
       "YourFrameworkAdapter"  # 新增
   ]
   ```

4. **编写测试**

   ```bash
   mkdir -p tests/test_adapter/
   touch tests/test_adapter/test_your_framework_adapter.py
   ```

### 适配器开发检查清单

- [ ] 继承 `BaseAdapter` 并实现所有必要方法
- [ ] 提供完整的异步支持
- [ ] 实现统一的错误处理
- [ ] 添加性能监控和指标
- [ ] 编写全面的测试用例
- [ ] 更新文档和示例
- [ ] 通过所有测试和代码质量检查

## 📚 文档贡献

### 文档类型

- **架构文档**: 7层架构设计和原理
- **开发文档**: 各层开发指南和最佳实践
- **API 文档**: 接口和类的详细说明
- **示例文档**: 实际使用案例和代码示例
- **部署文档**: 部署和运维指南

### 文档规范

- 使用 Markdown 格式
- 包含目录和导航链接
- 提供代码示例和架构图
- 保持内容的准确性和时效性
- 支持中英文（根据内容性质决定）

### 文档结构

```markdown
# 标题

## 概述
简要介绍功能或概念

## 快速开始
提供快速上手的步骤

## 详细说明
深入的技术细节和API说明

## 示例
实际的使用示例和代码片段

## 最佳实践
推荐的使用模式和注意事项

## 故障排除
常见问题和解决方案

## 相关链接
相关文档和资源的链接
```

## 🤝 社区行为准则

### 我们的承诺

- 创造一个开放、友好、多元化的技术社区
- 尊重不同的技术观点和实现方案
- 接受建设性的技术反馈
- 关注项目和社区的长远发展

### 期望行为

- 使用友好和专业的技术语言
- 尊重不同框架和技术选择
- 优雅地接受代码审查和建议
- 积极参与技术讨论和知识分享
- 对新贡献者表示欢迎和支持

### 不当行为

- 恶意批评特定框架或技术选择
- 人身攻击或非技术性争论
- 未经许可发布他人的代码或设计
- 在技术讨论中使用不当语言
- 其他违反开源社区准则的行为

## 🚀 开发环境设置

### 环境要求

- Python 3.8+
- Git 2.20+
- 推荐使用 PyCharm 或 VS Code
- OpenAI API Key (可选，用于OpenAI功能)

### 开发环境配置

```bash
# 1. 克隆项目
git clone https://github.com/your-org/agent-dev-center.git
cd agent-dev-center

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export OPENAI_API_KEY="your-api-key-here"  # 可选

# 4. 运行系统健康检查
python3 adc_simple.py system health

# 5. 运行测试确保环境正常
python -m pytest

# 6. 运行演示
python3 adc_simple.py demo openai
python3 adc_simple.py demo business
```

### 代码质量工具

```bash
# 代码格式化
black layers/ examples/ tests/

# 代码检查
flake8 layers/ examples/

# 类型检查
mypy layers/

# 测试覆盖率
pytest --cov=layers --cov-report=html

# 安全检查
bandit -r layers/
```

### 开发工具配置

#### VS Code 配置 (.vscode/settings.json)

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm 配置

- 设置Python解释器为项目虚拟环境
- 启用代码检查和格式化
- 配置测试运行器为pytest
- 启用类型检查

## 📊 质量标准

### 代码质量

- **测试覆盖率**: 最低85%，目标90%+
- **类型注解**: 所有公共接口必须有类型注解
- **文档覆盖**: 所有公共API必须有文档
- **性能基准**: 不得降低现有性能指标
- **安全标准**: 通过安全扫描和审计

### 审查流程

1. **自动检查**: CI/CD自动运行测试和代码质量检查
2. **同行审查**: 至少一位维护者审查代码
3. **功能测试**: 验证新功能的正确性和兼容性
4. **性能测试**: 确保性能符合要求
5. **安全审查**: 检查潜在的安全问题

## 📞 联系方式

- **GitHub Issues**: 技术问题和功能建议
- **GitHub Discussions**: 技术讨论和经验分享
- **项目维护者**: 通过 GitHub 联系核心开发团队
- **邮箱**: dev@agent-dev-center.com

## 🎯 贡献重点

### 当前优先级

1. **适配器扩展**: LangGraph、CrewAI等新框架适配器
2. **Web API开发**: REST API接口实现
3. **测试完善**: 提升测试覆盖率和质量
4. **性能优化**: 系统性能改进和优化
5. **文档完善**: API文档和使用指南

### 长期目标

- **分布式架构**: 支持多节点部署
- **企业级功能**: 高级安全和权限管理
- **插件生态**: 第三方插件开发框架
- **可视化工具**: 图形化工作流设计器

## 🙏 致谢

感谢所有为 Agent Development Center 项目做出贡献的开发者！特别感谢：

- 7层架构设计的贡献者
- 各个适配器的开发者
- CLI界面的完善者
- 业务层功能的实现者
- 文档和测试的贡献者
- 社区反馈和建议的提供者

## 🏆 贡献者认可

我们通过以下方式认可贡献者的努力：

- **代码贡献**: 在项目中署名和致谢
- **文档贡献**: 在文档中标注作者信息
- **重大贡献**: 加入项目维护者团队
- **社区贡献**: 在社区中给予特殊认可

---

*最后更新: 2025年1月15日*

**🚀 一起构建下一代AI Agent开发框架！**

*基于7层架构设计，让我们共同推进Agent开发技术的发展！*
