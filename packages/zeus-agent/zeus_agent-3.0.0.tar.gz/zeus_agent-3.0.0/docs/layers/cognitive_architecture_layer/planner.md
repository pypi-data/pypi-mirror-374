# 规划器 (Planner)

## 1. 概述

规划器（Planner）是认知架构中负责制定行动策略的核心组件。它将Agent的高层目标（Goal）和通过推理得出的见解，转化为一个具体的、有序的、可执行的步骤序列（Plan）。规划器是连接“思考”与“行动”的桥梁，它确保Agent的行为是深思熟虑的、有目的的，并且能够有效地导向目标的达成。

## 2. 设计目标

*   **目标导向 (Goal-Oriented)**: 所有生成的计划都必须明确地服务于一个或多个既定目标。
*   **分层规划 (Hierarchical Planning)**: 支持将复杂的高层目标分解为更简单、更易于管理的子任务和具体行动。
*   **动态适应性 (Dynamic Adaptation)**: 能够根据环境的变化、新信息的出现或执行过程中的意外失败，对现有计划进行动态地修改、重新排序或完全重新规划（Re-planning）。
*   **资源感知 (Resource-Awareness)**: 在规划时能考虑到可用资源（如时间、API调用次数、计算资源），并生成符合资源约束的计划。
*   **可解释性 (Explainable Plans)**: 生成的计划应该是人类可理解的，能够清晰地展示每一步行动的理由和预期效果。
*   **多样性与优化 (Diversity & Optimization)**: 能够生成多个候选计划，并根据一定的标准（如效率、成本、成功率）对它们进行评估和排序，选出最优计划。

## 3. 核心组件

### 3.1 目标分解器 (Goal Decomposer)

负责将模糊或复杂的高层目标分解为一系列更小、更具体的子目标。

*   **功能**: 采用任务分解技术（如Hierarchical Task Networks - HTN），将“预订一次旅行”这样的高层目标，分解为“查询航班”、“查询酒店”、“预订租车”等子目标。
*   **实现**: 可以通过预定义的任务模板、利用LLM的常识知识，或通过与`Reasoning Engine`交互来完成分解。

### 3.2 行动生成器 (Action Generator)

为每个子目标，生成一个或多个可能的具体行动（Action）。

*   **功能**: 识别出可以用于实现某个子目标的工具、API或内部函数。一个行动通常包括：要调用的工具、所需的参数、以及执行的前提条件和预期效果。
*   **示例**: 对于“查询航班”子目标，可以生成行动：`call_api(api_name='skyscanner.search', params={'from': 'SFO', 'to': 'JFK', 'date': '2024-12-25'})`。

### 3.3 计划构建器 (Plan Synthesizer)

将生成的行动组合并排序，形成一个连贯的计划。

*   **功能**: 
    *   **排序**: 确定行动之间的执行顺序和依赖关系。
    *   **组合**: 将独立的行动序列组合成一个完整的计划图或序列。
    *   **约束检查**: 确保整个计划满足所有已知的时间、资源和逻辑约束。

### 3.4 计划评估器与选择器 (Plan Evaluator & Selector)

对可能生成的多个候选计划进行评估，并选择最佳方案。

*   **功能**: 
    *   **成本/收益分析**: 评估每个计划的预期成本（时间、金钱）和成功概率。
    *   **风险评估**: 识别计划中可能失败的环节和潜在风险。
    *   **选择**: 根据预定义的策略（如“最快”、“最省钱”、“最稳妥”）选择一个计划提交执行。

### 3.5 重新规划器 (Re-planner)

当计划执行失败或环境发生重大变化时被激活。

*   **功能**: 分析失败的原因，修改当前计划（例如，替换一个失败的API调用），或者废弃当前计划并从头开始一个新的规划过程。

## 4. 关键接口设计

```python
from typing import Dict, Any, List, Protocol
from dataclasses import dataclass

@dataclass
class Goal:
    description: str
    priority: float
    constraints: Dict[str, Any]

@dataclass
class Action:
    tool_name: str
    parameters: Dict[str, Any]
    preconditions: List[str]
    effects: List[str]

@dataclass
class Plan:
    goal: Goal
    actions: List[Action]
    estimated_cost: float
    confidence_score: float

class Planner:
    def __init__(self, goal_decomposer, action_generator, plan_synthesizer, plan_evaluator):
        self.goal_decomposer = goal_decomposer
        self.action_generator = action_generator
        self.plan_synthesizer = plan_synthesizer
        self.plan_evaluator = plan_evaluator

    def create_plan(self, goal: Goal, context: Dict[str, Any]) -> Plan:
        """为给定的目标创建一个计划"""
        # 1. 分解目标
        sub_goals = self.goal_decomposer.decompose(goal, context)

        # 2. 为每个子目标生成行动
        all_actions = []
        for sub_goal in sub_goals:
            actions = self.action_generator.generate(sub_goal, context)
            all_actions.extend(actions)

        # 3. 构建候选计划
        candidate_plans = self.plan_synthesizer.synthesize(all_actions, goal, context)

        # 4. 评估并选择最佳计划
        best_plan = self.plan_evaluator.select_best(candidate_plans)
        
        return best_plan

    def replan(self, failed_plan: Plan, failure_info: Dict[str, Any], context: Dict[str, Any]) -> Plan:
        """当一个计划失败时进行重新规划"""
        # ... 重新规划逻辑 ...
        pass
```

## 5. 与其他组件的交互

*   **输入来源**: `Planner`由`Cognitive Core`在接收到明确目标后激活。它需要`Understanding Engine`提供的上下文理解和`Reasoning Engine`提供的推断结论作为规划的依据。
*   **与工具/行动知识的交互**: `Action Generator`需要访问一个“工具库”或“能力注册表”，以了解Agent有哪些可用的工具以及如何使用它们。
*   **输出去向**: 生成的`Plan`被提交给`Execution Engine`来执行。
*   **与学习引擎的反馈**: 计划的执行结果（成功、失败、效率）是`Learning Engine`的宝贵输入。学习引擎可以利用这些数据来优化未来的规划策略（例如，学习到某个API比另一个更可靠）。

## 6. 实现考量

*   **规划算法**: 可以采用多种规划算法，从简单的基于模板的规划，到经典的AI规划算法（如PDDL），再到利用LLM进行常识规划（Graph of Thoughts, Tree of Thoughts）。
*   **计划表示**: 计划可以用简单的步骤列表、有向无环图（DAG）或更复杂的行为树来表示。
*   **处理不确定性**: 在现实世界中，行动的效果往往是不确定的。规划器需要能够处理这种不确定性，例如通过制定包含备用方案的“应急计划”。