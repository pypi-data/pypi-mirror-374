# 学习引擎 (Learning Engine)

## 1. 概述

学习引擎（Learning Engine）是认知架构中负责实现Agent自我进化和能力提升的核心组件。它通过观察Agent的行动、结果、环境反馈以及与用户的交互，从中提取有价值的知识和经验，并利用这些学习成果来优化Agent未来的行为和决策。学习引擎使得Agent不仅仅是一个静态的程序，而是一个能够持续学习、适应和成长的动态实体。

## 2. 设计目标

*   **从经验中学习 (Learning from Experience)**: 能够从成功的行动、失败的尝试、用户的反馈和环境的变化中自动学习。
*   **持续优化 (Continuous Optimization)**: 持续地改进Agent的知识库、推理模型、规划策略和执行效率。
*   **多模式学习 (Multi-modal Learning)**: 支持多种学习范式，包括强化学习、监督学习、模仿学习和无监督学习。
*   **知识增量更新 (Incremental Knowledge Update)**: 能够将新学到的知识平滑地整合进现有的`Memory System`和`Knowledge Graph`中，而不会破坏其一致性。
*   **可配置的学习策略 (Configurable Learning Strategies)**: 允许开发者根据应用场景，配置和选择不同的学习算法和策略。
*   **安全与稳定 (Safety & Stability)**: 确保学习过程是稳定和收敛的，避免学习到有害或错误的行为，并提供回滚到先前稳定状态的机制。

## 3. 核心组件

### 3.1 经验收集器 (Experience Collector)

负责从Agent的整个认知循环中捕获和记录可用于学习的数据点。

*   **功能**: 监听并记录关键事件，形成结构化的“经验元组”（Experience Tuple）。一个典型的元组可能包含：
    *   **状态 (State)**: 行动前的世界状态和Agent的内部信念。
    *   **行动 (Action)**: Agent执行的具体行动。
    *   **结果 (Outcome)**: 行动产生的直接输出或世界状态的变化。
    *   **奖励/反馈 (Reward/Feedback)**: 来自环境的奖励信号、用户的明确反馈（赞/踩）或隐式反馈（如用户是否采纳了建议）。

### 3.2 信用分配模块 (Credit Assignment Module)

在复杂的任务中，一个最终的成功或失败往往是一系列行动共同作用的结果。该模块负责将最终的反馈信号合理地分配给序列中的每一个行动。

*   **功能**: 分析行动序列和最终结果之间的因果和时序关系，确定哪些步骤是关键的“功臣”或“罪魁祸首”。

### 3.3 学习算法库 (Learning Algorithm Library)

包含一系列可供选择的学习算法的实现。

*   **强化学习 (Reinforcement Learning)**: 如Q-learning、PPO等，用于根据奖励信号优化Agent的策略（Policy），即在特定状态下选择哪个行动。
*   **监督学习 (Supervised Learning)**: 当有明确的“正确答案”时使用。例如，利用用户修正过的计划来微调`Planner`的模型。
*   **模仿学习 (Imitation Learning)**: 通过观察和模仿专家（如人类用户）的行为来进行学习。
*   **无监督学习 (Unsupervised Learning)**: 从无标签的数据中发现模式，例如，通过聚类分析用户的历史请求来发现新的意图类别。

### 3.4 模型/知识更新器 (Model/Knowledge Updater)

负责将学习算法产生的更新应用到Agent的相应组件中。

*   **功能**: 
    *   **更新规划策略**: 调整`Planner`中行动选择的权重或规则。
    *   **修正知识图谱**: 在`Knowledge Graph`中添加新的事实、关系或修正错误的节点。
    *   **微调语言模型**: （在有足够数据和计算资源的情况下）微调底层的LLM模型。
    *   **优化工具使用**: 学习到在特定情境下某个工具比另一个更有效。

## 4. 关键接口设计

```python
from typing import Dict, Any, List, Protocol
from dataclasses import dataclass

@dataclass
class Experience:
    state: Dict[str, Any]
    action: 'Action'
    outcome: 'ExecutionResult'
    feedback: float # A numerical feedback signal

class ILearningAlgorithm(Protocol):
    def learn(self, experiences: List[Experience]) -> Dict[str, Any]:
        """从一批经验中学习，并返回更新指令"""
        ...

class LearningEngine:
    def __init__(self, algorithm: ILearningAlgorithm, model_updater):
        self.experience_buffer: List[Experience] = []
        self.algorithm = algorithm
        self.model_updater = model_updater

    def log_experience(self, experience: Experience) -> None:
        """记录一次经验"""
        self.experience_buffer.append(experience)

    def trigger_learning_cycle(self) -> None:
        """触发一次学习过程"""
        if not self.experience_buffer:
            return

        # 1. 调用学习算法
        updates = self.algorithm.learn(self.experience_buffer)

        # 2. 应用更新
        self.model_updater.apply_updates(updates)

        # 3. 清空缓冲区
        self.experience_buffer.clear()

class ModelUpdater:
    def apply_updates(self, updates: Dict[str, Any]) -> None:
        """将学习到的更新应用到Agent的各个组件"""
        # e.g., updates could be {'planner_policy': new_policy_dict}
        # This method would then know how to update the Planner.
        pass
```

## 5. 与其他组件的交互

*   **全方位监控**: `Learning Engine`是唯一一个需要与认知架构中几乎所有其他组件交互的组件。它从`Cognitive Core`、`Planner`、`Execution Engine`等处收集状态、行动和结果信息。
*   **接收反馈**: 它从外部（如用户反馈按钮）或内部（如`Execution Engine`报告的执行成功与否）接收反馈信号。
*   **更新其他组件**: 它的输出是针对其他组件的“更新指令”。例如，它可能会直接修改`Planner`的内部策略模型，或向`Knowledge Graph`中写入新的三元组。

## 6. 实现考量

*   **在线学习 vs. 离线学习**: 学习过程可以是在线（实时进行）的，也可以是离线（定期批量进行）的。在线学习适应性更强，但可能不稳定；离线学习更稳定，但有延迟。
*   **探索与利用 (Exploration vs. Exploitation)**: 特别是在强化学习中，需要平衡“利用”已知最优策略和“探索”可能更优的新策略之间的关系。
*   **学习的安全性**: 必须有机制防止Agent学习到有害或不希望的行为。例如，通过设置严格的约束、人类监督或在模拟环境中进行预训练。
*   **遗忘机制**: 并非所有学到的东西都是永久有用的。需要有机制来“遗忘”过时的或被证明是错误的知识，这可以与`Memory System`中的遗忘机制相结合。