# 感知引擎 (Perception Engine)

## 1. 概述

感知引擎（Perception Engine）是认知架构的门户，负责从多样化的内外部环境中捕获信息，并将其转化为Agent内部可以理解和处理的结构化格式。它充当着Agent的“感官系统”，是所有后续认知过程（如理解、推理、规划）的数据来源。感知引擎不仅处理直接的用户输入，还可能监控API响应、系统通知、传感器数据流等多种信息源。

## 2. 设计目标

*   **多模态输入 (Multi-modal Input)**: 支持处理多种形式的输入，包括文本、图像、音频、视频、结构化数据（如JSON）等。
*   **多源监听 (Multi-source Monitoring)**: 能够同时监听和接收来自不同信息源的数据，如用户界面、消息队列、API端点、文件系统等。
*   **标准化输出 (Standardized Output)**: 将所有捕获到的原始、异构的数据，转换为统一的、标准化的内部事件格式（如“Perception Event”），方便下游组件处理。
*   **可扩展的适配器模型 (Extensible Adapter Model)**: 提供一个插件式框架，允许开发者轻松添加新的“感知适配器”（Perception Adapter）来支持新的数据源或数据类型。
*   **高效与实时 (Efficiency & Real-time)**: 能够低延迟地处理输入信息，对于需要实时响应的场景（如流式数据处理）至关重要。
*   **可配置的过滤与预处理 (Configurable Filtering & Pre-processing)**: 允许在数据进入认知核心之前，进行初步的过滤、降噪和预处理，以减少不相关信息的干扰。

## 3. 核心组件

### 3.1 感知适配器 (Perception Adapter)

感知适配器是感知引擎的基本工作单元，每个适配器负责与一个特定的数据源进行交互。

*   **职责**: 连接到数据源、监听新数据、获取数据、并将其初步包装成一个内部原始事件。
*   **示例**:
    *   `ConsoleInputAdapter`: 从命令行读取用户输入。
    *   `WebhookAdapter`: 监听HTTP POST请求。
    *   `FileWatcherAdapter`: 监控文件系统中的文件变化。
    *   `AudioStreamAdapter`: 处理来自麦克风的音频流。
    *   `APIResponseAdapter`: 捕获对外部API调用的异步响应。

### 3.2 数据转换器 (Data Transformer)

数据转换器负责将适配器传来的、特定于源的原始数据，转换为标准的多模态格式。

*   **职责**: 对原始数据进行解析和格式转换。例如，将原始的HTTP请求体（JSON字符串）解析为Python字典，或将音频流数据转码并提取基本特征。
*   **示例**:
    *   `JsonToDictTransformer`: 将JSON字符串转换为字典。
    *   `SpeechToTextTransformer`: 将音频数据转换为文本（可能需要调用外部ASR服务）。
    *   `ImagePreprocessor`: 对图像进行尺寸调整、归一化等预处理。

### 3.3 事件生成器 (Event Generator)

事件生成器是感知流程的最后一步，它接收转换后的数据，并将其封装成一个标准化的`PerceptionEvent`对象。

*   **职责**: 创建`PerceptionEvent`，为其填充元数据（如来源、时间戳、数据类型），并确保其格式符合Agent内部的统一规范。

### 3.4 感知管理器 (Perception Manager)

作为感知引擎的协调者，负责管理所有适配器的生命周期，并编排从数据捕获到事件生成的完整流程。

*   **职责**: 加载和配置适配器、启动和停止监听、将适配器捕获的数据路由到合适的转换器和生成器。

## 4. 关键接口设计

```python
from typing import Dict, Any, List, Protocol
from abc import ABC, abstractmethod

# 标准化的感知事件
@dataclasses.dataclass
class PerceptionEvent:
    source: str  # e.g., 'user_console', 'github_webhook'
    event_id: str
    timestamp: float
    data_type: str # e.g., 'text', 'audio', 'json'
    content: Any
    metadata: Dict[str, Any]

# 感知适配器接口
class IPerceptionAdapter(Protocol):
    def start(self, callback: callable) -> None:
        """开始监听，当有数据时调用callback"""
        ...

    def stop(self) -> None:
        """停止监听"""
        ...

# 感知引擎主类
class PerceptionEngine:
    def __init__(self, adapters: List[IPerceptionAdapter]):
        self.adapters = adapters
        self.event_queue = [] # 用于存放生成的PerceptionEvent

    def run(self) -> None:
        """启动所有适配器"""
        for adapter in self.adapters:
            adapter.start(self.handle_raw_data)

    def handle_raw_data(self, raw_data: Any, source_info: Dict) -> None:
        """处理来自适配器的原始数据，并将其转换为PerceptionEvent"""
        # 1. 调用DataTransformer进行转换
        # 2. 调用EventGenerator创建事件
        # 3. 将事件放入队列
        event = self._generate_event(raw_data, source_info)
        self.event_queue.append(event)

    def get_next_event(self) -> PerceptionEvent:
        """供认知核心调用，获取下一个感知事件"""
        if self.event_queue:
            return self.event_queue.pop(0)
        return None
```

## 5. 与其他组件的交互

*   **数据提供者**: 感知引擎是`Cognitive Core`的唯一数据来源。`Cognitive Core`通过调用`get_next_event()`来驱动整个认知循环的开始。
*   **与理解引擎的衔接**: 感知引擎产生的`PerceptionEvent`是`Understanding Engine`的直接输入。`Understanding Engine`会对事件中的`content`进行深入的语义分析。
*   **与执行引擎的关联**: `Execution Engine`在调用外部工具或API后，会产生结果。这些结果（如API的HTTP响应）本身也可以被一个特定的`Perception Adapter`（如`APIResponseAdapter`）捕获，从而形成一个完整的“行动-感知”闭环。