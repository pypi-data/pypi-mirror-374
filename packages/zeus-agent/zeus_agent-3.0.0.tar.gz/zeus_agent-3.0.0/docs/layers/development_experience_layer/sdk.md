# 软件开发套件 (SDK)

## 1. 概述

软件开发套件（SDK）是开发者在代码层面与统一Agent框架进行交互的主要工具。它是一系列精心设计的API、库、装饰器和数据结构的集合，旨在简化Agent能力的开发、集成和管理。一个好的SDK能够让开发者聚焦于业务逻辑的实现，而无需关心底层的复杂性，同时保证代码的规范性、可测试性和可维护性。

## 2. 设计原则

*   **高内聚，低耦合**: SDK的各个模块应该功能内聚，同时与其他部分保持松耦合，便于独立演进和测试。
*   **符合直觉的API**: API设计应遵循“最小惊讶原则”，命名清晰，参数明确，易于理解和使用。
*   **强类型与代码补全**: 尽可能使用Python的类型提示（Type Hinting），为开发者提供强大的静态检查和IDE代码补全支持。
*   **可测试性优先**: SDK的设计应原生支持单元测试和集成测试。例如，提供依赖注入容器，方便在测试中替换依赖项。
*   **向后兼容**: 在API演进过程中，应谨慎考虑向后兼容性，避免破坏性的变更，或提供清晰的迁移指南。

## 3. 核心功能模块

### 3.1 能力定义 (Capability Definition)

这是SDK最核心的部分，提供了一种声明式的方式来定义Agent的能力。

*   **原子能力 (Atomic Capability)**: 使用装饰器来定义一个函数作为原子能力。

    ```python
    from agent_sdk.capability import capability, Tool
    from pydantic import BaseModel

    class WeatherInput(BaseModel):
        city: str

    class WeatherOutput(BaseModel):
        temperature: float
        description: str

    @capability(
        name="get_weather",
        description="获取指定城市的天气信息",
        input_model=WeatherInput,
        output_model=WeatherOutput
    )
    def get_weather(city: str) -> dict:
        """这里是调用天气API的实际逻辑"""
        # ... 调用外部API ...
        return {"temperature": 25.0, "description": "晴天"}
    ```

*   **组合能力 (Composite Capability)**: 提供API来编排和组合多个原子能力。

    ```python
    from agent_sdk.workflow import Workflow

    def travel_planner_workflow(city: str, days: int) -> str:
        workflow = Workflow(name="travel_planner")

        weather_task = workflow.add_task(get_weather, city=city)
        poi_task = workflow.add_task(find_points_of_interest, city=city)

        # ... 更复杂的编排逻辑 ...

        report = workflow.add_task(
            generate_report, 
            weather=weather_task.output, 
            pois=poi_task.output
        )

        return workflow
    ```

### 3.2 认知核心交互 (Cognitive Core Interaction)

提供与Planner, RAG, Reasoning Engine等认知组件交互的接口。

*   **示例**: 

    ```python
    from agent_sdk.cognitive import cognitive_core

    @capability(name="chat")
    def chat_with_agent(query: str):
        # 直接调用认知核心进行一次性的问答
        response = cognitive_core.chat(query)
        return response

    @capability(name="complex_task")
    def execute_complex_task(goal: str):
        # 启动一个长期的、多步骤的规划任务
        plan = cognitive_core.plan(goal)
        for step in plan:
            cognitive_core.execute(step)
    ```

### 3.3 上下文与内存 (Context & Memory)

提供简单易用的API来访问和管理当前任务的上下文以及长短期记忆。

*   **示例**: 

    ```python
    from agent_sdk.context import current_task, session

    @capability(name="contextual_greeting")
    def greeting() -> str:
        user_id = current_task.get("user_id")
        
        # 从会话内存中读取历史信息
        previous_name = session.memory.get("user_name")

        if previous_name:
            return f"欢迎回来, {previous_name}!"
        else:
            # ... 询问名字并存入会话内存 ...
            name = ask_for_name()
            session.memory.set("user_name", name)
            return f"你好, {name}!"
    ```

### 3.4 工具使用 (Tool Usage)

简化在能力中定义和使用外部工具（如API调用、数据库查询）的过程。

*   **示例**: SDK可以与`langchain`等工具使用框架集成，或者提供自己的工具抽象。

    ```python
    from agent_sdk.tools import APITool

    # 定义一个工具
    google_search = APITool(
        name="google_search",
        api_spec_url="https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest"
    )

    @capability(name="search_and_summarize")
    @uses_tool(google_search) # 声明此能力需要使用该工具
    def search_and_summarize(query: str, search_tool: Tool) -> str:
        # 在函数签名中注入工具实例
        search_results = search_tool.run(query=query)
        summary = summarize(search_results)
        return summary
    ```

## 4. 与CLI的关系

SDK和CLI是DevX层的两个紧密协作的组件。

*   CLI的`agent new`命令生成的项目模板中，会包含一个使用SDK定义好的`main.py`或`app.py`文件。
*   CLI的`agent run`命令会加载并运行由SDK定义的能力。
*   开发者在SDK代码中做的修改，会由CLI的热重载功能自动捕获并重新加载。

## 5. 实现考量

*   **依赖管理**: SDK本身及其依赖需要被清晰地打包和版本化。使用`pyproject.toml`和现代的包管理工具（如Poetry, PDM）是最佳实践。
*   **文档生成**: 利用代码中的类型提示和文档字符串（docstrings），自动生成API参考文档。工具如Sphinx, MkDocs可以与代码库集成，实现文档的持续构建。
*   **示例代码**: 提供丰富且实用的示例代码和教程，是推广SDK和降低学习曲线的关键。