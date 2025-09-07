# 测试框架 (Testing Framework)

## 1. 概述

为Agent应用提供一套全面、易用、高效的测试框架是保证其质量、稳定性和可维护性的关键。由于Agent应用的复杂性，特别是其与外部世界（API、数据库）、不确定性（LLM的响应）和内部状态（内存、上下文）的深度交互，传统的测试方法需要被扩展和适配。本测试框架旨在为开发者提供从单元测试、集成测试到端到端（E2E）测试的全方位支持。

## 2. 设计目标

*   **易用性**: 提供简洁的API和声明式的测试用例编写方式，降低测试的编写和维护成本。
*   **隔离性**: 能够轻松地隔离被测试单元（如单个能力），并模拟（Mock）其依赖项。
*   **可复现性**: 测试结果应该是稳定和可复现的，尤其是在处理与LLM等不确定性组件的交互时。
*   **覆盖全面**: 支持不同层级的测试需求，确保Agent的每个部分都得到充分验证。
*   **与DevX集成**: 与CLI、SDK和CI/CD流程无缝集成。

## 3. 测试框架组件

### 3.1 单元测试 (Unit Testing)

专注于测试最小的可测试单元——通常是一个原子能力（Atomic Capability）。

*   **核心功能**:
    *   **能力加载器**: 可以独立加载一个或多个能力函数进行测试，而无需启动整个Agent应用。
    *   **依赖注入**: 自动或手动注入被测试能力所需的依赖（如工具、配置），并允许在测试中用模拟对象（Mock）替换它们。

*   **示例代码**:

    ```python
    from agent_sdk.testing import TestContext
    from unittest.mock import MagicMock
    from my_agent.capabilities import get_weather

    def test_get_weather_sunny():
        # 1. 准备模拟数据和对象
        mock_weather_api = MagicMock()
        mock_weather_api.fetch.return_value = {"temp": 25, "condition": "sunny"}

        # 2. 使用测试上下文运行能力
        with TestContext() as ctx:
            # 注入模拟的依赖
            ctx.register_tool("weather_api", mock_weather_api)
            
            # 执行被测试的能力
            result = ctx.run(get_weather, city="beijing")

        # 3. 断言结果
        assert result["temperature"] == 25
        assert "阳光明媚" in result["suggestion"]
        mock_weather_api.fetch.assert_called_once_with(city="beijing")
    ```

### 3.2 集成测试 (Integration Testing)

测试多个组件之间的交互，例如一个组合能力（Workflow）的执行，或者能力与内存系统、知识库的交互。

*   **核心功能**:
    *   **内存数据库**: 提供一个内存中的（in-memory）向量数据库和键值存储，用于测试与记忆和知识相关的能力。
    *   **工作流测试器**: 提供一个专门的测试运行器来执行和验证一个完整的工作流。

*   **示例代码**:

    ```python
    from agent_sdk.testing import WorkflowTestBed
    from my_agent.workflows import travel_planner_workflow

    def test_travel_planner_workflow():
        # 1. 设置测试平台，可以预加载数据
        test_bed = WorkflowTestBed(workflow=travel_planner_workflow)
        test_bed.mock_capability("get_weather", returns={"temperature": 30, ...})
        test_bed.mock_capability("find_pois", returns=[{"name": "The Palace Museum"}, ...])

        # 2. 执行工作流
        result = test_bed.run(city="beijing", days=3)

        # 3. 断言最终结果或中间状态
        assert "The Palace Museum" in result["itinerary"]
        assert test_bed.get_call_history("get_weather").call_count == 1
    ```

### 3.3 端到端测试 (End-to-End Testing)

从用户的视角出发，通过API接口测试整个Agent应用的完整功能。这通常涉及到与LLM的真实或模拟交互。

*   **核心功能**:
    *   **LLM模拟器 (LLM Simulator)**: 这是E2E测试的核心。它是一个可编程的模拟LLM，可以根据预设的规则返回响应，而不是进行真实的API调用。这保证了测试的稳定性和低成本。
        *   **基于规则的响应**: `when(prompt_contains="你好").reply("你好！有什么可以帮您？")`
        *   **基于函数的响应**: `when(tool_call="get_weather").reply(lambda city: f"正在查询{city}的天气...")`
    *   **会话客户端 (Session Client)**: 提供一个模拟用户与Agent进行多轮对话的客户端。

*   **示例代码**:

    ```python
    from agent_sdk.testing.e2e import E2ESession, llm_simulator

    def test_full_conversation_flow():
        # 1. 定义LLM模拟器的行为
        llm_simulator.when_prompt_contains("订一张去上海的机票").tool_call("book_flight", destination="shanghai")
        llm_simulator.when_tool_result("book_flight").reply("机票已预订成功！")

        # 2. 启动一个E2E测试会话
        with E2ESession() as session:
            # 第一轮对话
            response1 = session.send("帮我订一张去上海的机票")
            assert "正在为您处理" in response1.text

            # 框架会自动处理工具调用和后续的LLM交互

            # 等待最终的回复
            response2 = session.get_latest_response()
            assert "机票已预订成功" in response2.text
    ```

## 4. 与CLI的集成

*   **`agent test`**: CLI中的`test`命令是测试框架的统一入口。
    *   `agent test`: 默认运行所有单元测试和集成测试。
    *   `agent test --e2e`: 专门运行端到端测试。
    *   `agent test --coverage`: 收集代码覆盖率信息，并可以配置覆盖率阈值，未达到则测试失败，常用于CI/CD流程。

## 5. 实现考量

*   **构建于现有库之上**: 测试框架应尽可能地利用和封装现有的优秀测试库，如`pytest`（用于测试发现、断言和插件系统）和`unittest.mock`（用于模拟）。
*   **性能**: 测试执行，特别是单元测试和集成测试，应该非常快，以鼓励开发者频繁运行。
*   **异步支持**: 框架需要原生支持测试`async/await`风格的异步代码。