# 角色管理器 (Persona Manager)

## 1. 概述

角色管理器（Persona Manager）是认知架构中负责塑造和维持Agent个性和行为风格的专门组件。它确保Agent在与用户交互时，其语言、语气、决策偏好和行为模式都与其预设的“角色”（Persona）保持一致。角色不仅仅是简单的系统提示（System Prompt），而是一套深度集成的、影响Agent认知全流程的配置和约束。

## 2. 设计目标

*   **一致性 (Consistency)**: 确保Agent在长时间、多轮次的交互中，其行为和语言风格始终保持一致，符合其角色设定。
*   **可塑性 (Malleability)**: 提供灵活的机制来定义、切换和修改Agent的角色。角色可以被设计为静态的，也可以是动态演化的。
*   **深度集成 (Deep Integration)**: 角色设定应能影响到认知架构的多个层面，包括语言生成、决策偏好、甚至是学习方式。
*   **可管理性 (Manageability)**: 提供清晰的接口和工具来创建、存储和管理大量的角色模板。
*   **情境自适应 (Context-aware Adaptation)**: 允许角色在不同的交互情境下，微调其行为表现（例如，在正式和非正式对话中表现出不同的语气）。

## 3. 核心组件

### 3.1 角色模板库 (Persona Template Library)

一个存储和管理预定义角色模板的仓库。

*   **功能**: 
    *   存储角色模板，每个模板包含定义角色所需的全部信息。
    *   提供创建、读取、更新和删除（CRUD）角色模板的功能。
    *   支持角色的版本控制。
*   **存储**: 可以是文件系统（如YAML或JSON文件）、数据库或专门的配置中心。

### 3.2 角色定义模型 (Persona Definition Model)

定义了一个角色的具体构成元素。一个角色模板通常包含以下部分：

*   **核心身份 (Core Identity)**: 
    *   `name`: 角色的名字（如“小P”）。
    *   `background`: 角色的背景故事或设定。
    *   `traits`: 性格特质关键词（如“友好”、“严谨”、“幽默”）。
*   **语言风格 (Linguistic Style)**: 
    *   `system_prompt`: 指导LLM生成风格的核心提示。
    *   `vocabulary`: 偏好使用的词汇或需要避免的词汇。
    *   `tone_and_manner`: 语气和风格的描述（如“正式”、“口语化”、“富有同情心”）。
*   **行为偏好 (Behavioral Preferences)**: 
    *   `risk_appetite`: 风险偏好（如“保守”、“激进”），会影响`Planner`的决策。
    *   `communication_strategy`: 沟通策略（如“主动提问”、“简洁回答”）。
    *   `ethical_guardrails`: 特定于角色的伦理和行为准则。
*   **认知偏向 (Cognitive Biases)**: 
    *   `reasoning_style`: 推理风格偏好（如“偏好逻辑推理”、“偏好直觉判断”）。
    *   `learning_rate`: 学习和适应新事物的速度。

### 3.3 角色注入器 (Persona Injector)

负责在认知过程的关键节点，将当前激活角色的配置和约束“注入”到相应的认知组件中。

*   **功能**: 
    *   向`Generator`（通常在RAG系统或直接的LLM调用中）提供`system_prompt`。
    *   向`Planner`传递`risk_appetite`等行为偏好，以影响计划评估。
    *   向`Understanding Engine`提供上下文，帮助其更好地理解与角色相关的特定语境。

### 3.4 角色上下文管理器 (Persona Context Manager)

负责在会话中加载、激活和管理当前的角色状态。

*   **功能**: 
    *   根据初始配置或用户指令，加载一个角色模板。
    *   在多角色Agent中，处理角色的切换逻辑。
    *   管理角色的动态状态（如果角色被设计为可演化的）。

## 4. 关键接口设计

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Persona:
    id: str
    name: str
    background: str
    traits: List[str]
    linguistic_style: Dict[str, Any]
    behavioral_preferences: Dict[str, Any]
    cognitive_biases: Dict[str, Any]

class PersonaManager:
    def __init__(self, template_library):
        self.library = template_library
        self._active_persona: Optional[Persona] = None

    def load_persona(self, persona_id: str) -> None:
        """从库中加载并激活一个角色"""
        self._active_persona = self.library.get_persona(persona_id)

    def get_active_persona(self) -> Optional[Persona]:
        """获取当前激活的角色"""
        return self._active_persona

    def inject_into_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """将角色信息注入到一个上下文字典中，供其他组件使用"""
        if not self._active_persona:
            return context

        context['persona'] = {
            'system_prompt': self._active_persona.linguistic_style.get('system_prompt'),
            'risk_appetite': self._active_persona.behavioral_preferences.get('risk_appetite')
            # ... and so on
        }
        return context

class PersonaTemplateLibrary:
    def get_persona(self, persona_id: str) -> Persona:
        # Logic to load persona from a file or database
        pass
```

## 5. 与其他组件的交互

*   **由认知核心管理**: `PersonaManager`本身由`Cognitive Core`进行管理。`Cognitive Core`在初始化时会指令`PersonaManager`加载默认角色。
*   **影响多个组件**: `PersonaManager`通过`Cognitive Core`提供的上下文，间接地影响多个认知组件：
    *   **语言生成**: 主要影响最终的语言模型调用，决定了回复的风格。
    *   **规划**: `behavioral_preferences`会成为`Planner`评估计划时的额外约束或权重。
    *   **推理**: `cognitive_biases`可以引导`Reasoning Engine`选择特定的推理路径。
    *   **学习**: 角色的设定可以影响`Learning Engine`的学习目标（例如，一个“谨慎”的角色可能更注重避免犯错）。

## 6. 实现考量

*   **动态与静态角色**: 需要明确一个角色是静态的（其属性在整个会话中不变），还是动态的（其特质或信念会根据交互而演化）。动态角色需要与`Learning Engine`和`Memory System`进行更紧密的集成。
*   **角色冲突**: 在多Agent协作或角色切换时，需要有机制来处理潜在的角色定义冲突。
*   **角色设计的艺术**: 设计一个引人入胜且一致的角色本身是一项挑战，需要结合心理学、编剧和UX设计的知识。提供良好的角色设计工具和指南是非常有价值的。