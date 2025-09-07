# CLI工具 (Command-Line Interface)

## 1. 概述

CLI（Command-Line Interface）工具是开发者与统一Agent框架进行交互的核心入口。它提供了一套统一、简洁、强大的命令，覆盖了Agent应用的整个生命周期，从项目创建、本地开发、测试，到最终的打包和部署。一个设计良好的CLI可以极大地提升开发效率和幸福感。

## 2. 设计目标

*   **一致性 (Consistency)**: 所有命令和参数设计遵循统一的命名和行为规范，降低学习成本。
*   **可发现性 (Discoverability)**: 提供清晰的帮助信息 (`--help`) 和命令自动补全功能，让开发者可以轻松发现和使用各种功能。
*   **可组合性 (Composability)**: 命令设计遵循Unix哲学，使其可以轻松地通过管道（pipe）与其他命令行工具组合使用。
*   **可扩展性 (Extensibility)**: 提供插件机制，允许开发者或社区为CLI添加新的命令和功能。
*   **用户友好 (User-Friendly)**: 提供彩色的输出、进度条、清晰的错误提示和建议，优化用户体验。

## 3. 核心命令设计

基础命令: `agent <command> <subcommand> [arguments] [flags]`

### 3.1 项目管理

*   **`agent new <project_name> [--template <template_name>]`**: 创建一个新的Agent项目。
    *   `project_name`: 新项目的名称。
    *   `--template`: （可选）指定一个项目模板。可以提供多种预设模板，如`simple-echo-agent`, `rag-agent`, `data-analysis-agent`等。
    *   **执行流程**: 
        1.  从模板仓库（可以是本地或远程Git仓库）拉取模板文件。
        2.  替换模板中的占位符（如项目名称、作者等）。
        3.  初始化Git仓库。
        4.  （可选）自动安装初始依赖。

### 3.2 本地开发

*   **`agent run [--port <port_number>] [--hot-reload]`**: 启动本地开发服务器。
    *   `--port`: 指定API服务器监听的端口。
    *   `--hot-reload`: 默认开启，当代码文件发生变化时，自动重新加载Agent应用。
    *   **执行流程**: 
        1.  启动文件系统监视器（watcher），监听指定目录下的文件变更。
        2.  加载Agent应用配置，启动应用实例。
        3.  启动API网关，开始接收请求。
        4.  当文件变更时，平滑地重启应用实例。

### 3.3 能力管理

*   **`agent capability list`**: 列出当前项目中已安装的能力。
*   **`agent capability add <capability_name>`**: 从能力仓库中添加一个新的能力包到项目中。
*   **`agent capability remove <capability_name>`**: 从项目中移除一个能力包。

### 3.4 测试

*   **`agent test [test_path] [--coverage]`**: 运行测试。
    *   `test_path`: （可选）指定要运行的测试文件或目录。
    *   `--coverage`: （可选）生成测试覆盖率报告。
    *   **执行流程**: 
        1.  发现匹配`*_test.py`模式的测试文件。
        2.  使用底层的测试框架（如Pytest）执行测试。
        3.  输出格式化的测试结果。

### 3.5 部署

*   **`agent deploy [--target <target_env>]`**: 部署Agent应用。
    *   `--target`: 指定部署目标，如`docker`, `kubernetes`, `serverless`等。配置在项目的一个部署文件中（如`deploy.yml`）。
    *   **执行流程**: 
        1.  读取`deploy.yml`配置文件。
        2.  根据目标环境执行相应的部署步骤：
            *   **Docker**: 构建Docker镜像，并推送到指定的镜像仓库。
            *   **Kubernetes**: 生成或更新Kubernetes的部署（Deployment）、服务（Service）等YAML文件，并使用`kubectl apply`应用到集群中。

## 4. 实现技术选型

*   **Python**: [Typer](https://typer.tiangolo.com/) 或 [Click](https://click.palletsprojects.com/) - 这两个库都提供了构建现代化CLI应用的强大功能，包括自动生成帮助文档、类型检查、命令分组等。
*   **Go**: [Cobra](https://github.com/spf13/cobra) - Go语言社区最流行的CLI框架，被Kubernetes, Docker等大量项目使用，性能优秀，生态成熟。

选择哪种语言主要取决于框架核心的开发语言。如果核心是Python，那么使用Typer或Click会更自然。

## 5. 插件系统设计

为了实现可扩展性，CLI应支持插件系统。

*   **发现机制**: CLI在启动时，会扫描特定目录（如`~/.agent/plugins`）或项目依赖（如`pyproject.toml`中定义的`agent.plugins`入口点），来发现已安装的插件。
*   **插件接口**: 插件需要实现一个简单的接口，例如一个`register`函数，该函数接收CLI的主命令对象作为参数，然后可以在其上注册新的子命令。

```python
# 示例: 一个CLI插件
import typer

app = typer.Typer()

@app.command()
def my_plugin_command():
    """这是一个来自插件的命令"""
    print("插件命令已执行!")

# 在插件的入口点中被调用
def register(main_cli_app):
    main_cli_app.add_typer(app, name="myplugin")
```