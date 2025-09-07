# 🚀 ADC CLI Tool - 用户指南

Agent Development Center 命令行界面工具，提供完整的8层架构管理功能。

## 📦 安装和配置

### 前置要求

- Python 3.8+
- 虚拟环境（推荐）

### 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖包
pip install rich pyyaml
```

### 启动CLI工具

```bash
# 直接使用脚本
./adc --help

# 或使用Python模块
python -m layers.application.cli.main --help
```

## 🎯 核心功能

### 1. Agent管理 🤖

```bash
# 列出所有Agent
./adc agent list --format table

# 创建新Agent
./adc agent create --name MyAgent --type openai --model gpt-4o-mini

# 与Agent对话
./adc agent chat --name MyAgent --message "Hello!"

# 显示Agent详细信息
./adc agent info MyAgent

# 删除Agent
./adc agent delete MyAgent --force
```

### 2. 工作流管理 ⚙️

```bash
# 列出所有工作流
./adc workflow list --format table

# 创建工作流
./adc workflow create --name MyWorkflow --description "测试工作流"

# 运行工作流
./adc workflow run --id workflow_001 --watch

# 查看工作流状态
./adc workflow status workflow_001 --follow

# 查看工作流日志
./adc workflow logs workflow_001 --follow --lines 100
```

### 3. 团队管理 👥

```bash
# 列出所有团队
./adc team list --format table

# 创建团队
./adc team create --name DevTeam --members alice bob charlie

# 执行团队协作
./adc team collaborate --team DevTeam --task "代码审查" --pattern parallel

# 查看团队性能
./adc team performance DevTeam --period week
```

### 4. 项目管理 🏗️

```bash
# 初始化新项目
./adc project init MyProject --template fastapi_app --interactive

# 列出所有项目
./adc project list --format table

# 查看项目状态
./adc project status MyProject

# 构建项目
./adc project build --target production --watch

# 部署项目
./adc project deploy --env staging --dry-run
```

### 5. 配置管理 ⚙️

```bash
# 获取配置值
./adc config get openai_model

# 设置配置值
./adc config set openai_model gpt-4o-mini

# 列出所有配置
./adc config list --format table

# 编辑配置文件
./adc config edit --editor vim
```

### 6. 监控功能 📊

```bash
# 系统监控
./adc monitor system --interval 5

# Agent监控
./adc monitor agents --interval 10

# 工作流监控
./adc monitor workflows --interval 15
```

### 7. 工具集 🛠️

```bash
# 验证配置和设置
./adc tools validate --fix

# 性能基准测试
./adc tools benchmark --type system --duration 60

# 导出数据
./adc tools export --type agents --format json --output agents.json

# 导入数据
./adc tools import agents.json --type agents --merge
```

### 8. 演示功能 🎮

```bash
# OpenAI演示
./adc demo openai --model gpt-4o-mini --interactive

# 业务层演示
./adc demo business --module all --verbose

# 应用编排演示
./adc demo orchestration --verbose

# 交互式演示向导
./adc demo interactive
```

## 🎨 交互模式

### 启动交互模式

```bash
./adc --interactive
```

### 交互模式特性

- **🔄 自动补全**: 使用Tab键自动补全命令和参数
- **📚 Rich界面**: 美观的表格、面板和语法高亮
- **📝 命令历史**: 自动保存和浏览命令历史
- **🔗 别名系统**: 支持自定义命令别名
- **💻 内置命令**: 类似Shell的内置命令（cd、ls、pwd等）

### 内置命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `help` | 显示帮助信息 | `help` |
| `exit/quit` | 退出Shell | `exit` |
| `clear` | 清屏 | `clear` |
| `history` | 显示命令历史 | `history` |
| `version` | 显示版本信息 | `version` |
| `status` | 显示系统状态 | `status` |
| `alias` | 管理别名 | `alias ll 'agent list'` |
| `echo` | 输出文本 | `echo Hello World` |
| `cd` | 切换目录 | `cd /path/to/dir` |
| `ls` | 列出文件 | `ls -la` |
| `pwd` | 显示当前目录 | `pwd` |
| `env` | 显示环境变量 | `env` |
| `session` | 会话管理 | `session save/load` |

### 预定义别名

| 别名 | 命令 | 描述 |
|------|------|------|
| `a` | `agent` | Agent管理 |
| `w` | `workflow` | 工作流管理 |
| `t` | `team` | 团队管理 |
| `p` | `project` | 项目管理 |
| `c` | `config` | 配置管理 |
| `m` | `monitor` | 监控功能 |
| `d` | `demo` | 演示功能 |
| `h` | `help` | 帮助信息 |
| `ll` | `agent list` | 列出Agent |
| `cc` | `config list` | 列出配置 |
| `ss` | `status` | 显示状态 |

## 📋 命令参考

### 全局选项

```bash
./adc [全局选项] 命令 [命令选项]

全局选项:
  --version, -v         显示版本信息
  --config, -c CONFIG   指定配置文件路径
  --verbose, -V         详细输出模式
  --interactive, -i     启动交互模式
  --log-level LEVEL     设置日志级别 (DEBUG|INFO|WARNING|ERROR)
```

### 输出格式

大多数列表命令支持多种输出格式：

- `table` - 表格格式（默认，使用Rich美化）
- `json` - JSON格式
- `yaml` - YAML格式

### 过滤和排序

许多命令支持过滤和排序：

```bash
# 过滤Agent
./adc agent list --filter openai

# 按类型排序
./adc agent list --sort type

# 按状态过滤工作流
./adc workflow list --status active
```

## 🎪 演示和示例

### 快速开始

```bash
# 1. 启动交互模式
./adc --interactive

# 2. 查看系统状态
status

# 3. 运行演示
demo interactive

# 4. 列出Agent
agent list

# 5. 创建新Agent
agent create --name TestAgent --interactive

# 6. 与Agent对话
agent chat --name TestAgent
```

### 完整工作流示例

```bash
# 1. 创建项目
./adc project init MyAIApp --template ai_project

# 2. 创建团队
./adc team create --name AITeam --interactive

# 3. 创建工作流
./adc workflow create --name AIWorkflow --interactive

# 4. 运行工作流
./adc workflow run --id AIWorkflow --watch

# 5. 监控执行
./adc monitor workflows --interval 5
```

## 🔧 配置和自定义

### 配置文件

ADC支持YAML格式的配置文件：

```yaml
# ~/.adc_config.yaml
openai:
  model: gpt-4o-mini
  api_key: your_api_key

logging:
  level: INFO
  file: ~/.adc.log

interface:
  theme: dark
  auto_complete: true
  history_size: 1000

aliases:
  myalias: "agent list --format json"
```

### 环境变量

| 环境变量 | 描述 | 默认值 |
|----------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 无 |
| `ADC_CONFIG` | 配置文件路径 | `~/.adc_config.yaml` |
| `ADC_LOG_LEVEL` | 日志级别 | `INFO` |
| `ADC_WORKSPACE` | 工作目录 | `./workspace` |

### 会话管理

```bash
# 保存当前会话
session save

# 加载会话
session load

# 清空会话
session clear

# 查看会话信息
session info
```

## 🐛 故障排除

### 常见问题

1. **命令不识别**
   ```bash
   # 检查帮助
   ./adc --help
   
   # 验证安装
   ./adc tools validate
   ```

2. **Rich界面显示问题**
   ```bash
   # 检查Rich是否安装
   pip list | grep rich
   
   # 重新安装
   pip install --upgrade rich
   ```

3. **权限问题**
   ```bash
   # 给脚本添加执行权限
   chmod +x adc
   ```

4. **Python路径问题**
   ```bash
   # 设置PYTHONPATH
   export PYTHONPATH=/path/to/agent_dev_center
   ```

### 调试模式

```bash
# 启用详细输出
./adc --verbose --log-level DEBUG command

# 查看系统信息
./adc tools validate
```

### 日志查看

```bash
# 查看工作流日志
./adc workflow logs workflow_id --follow

# 查看系统日志
tail -f ~/.adc.log
```

## 📚 高级用法

### 脚本化使用

```bash
#!/bin/bash
# 自动化脚本示例

# 设置环境
export PYTHONPATH=/path/to/zeus

# 创建Agent
./adc agent create --name AutoAgent --type openai

# 运行工作流
./adc workflow run --id auto_workflow

# 导出结果
./adc tools export --type all --format json --output results.json
```

### 管道使用

```bash
# 将Agent列表导出为JSON并处理
./adc agent list --format json | jq '.[] | select(.status == "ready")'

# 批量创建Agent
cat agents.txt | while read name; do
  ./adc agent create --name "$name" --type openai
done
```

### 集成到CI/CD

```yaml
# .github/workflows/adc.yml
name: ADC Integration
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate ADC
        run: ./adc tools validate
      - name: Run tests
        run: ./adc tools benchmark --type system
```

## 🤝 贡献和反馈

如果您发现问题或有改进建议，请：

1. 提交Issue到GitHub仓库
2. 使用`./adc tools validate --fix`尝试自动修复
3. 查看详细日志进行诊断
4. 联系开发团队

---

**🎉 享受使用ADC CLI工具！让AI Agent开发变得更简单、更高效！** 