"""
Reasoning Module
推理模块 - 实现基础逻辑推理能力

该模块提供多种推理策略，包括演绎推理、归纳推理、类比推理等，
帮助Agent进行逻辑思考和决策。
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class ReasoningType(Enum):
    """推理类型枚举"""
    DEDUCTIVE = "deductive"          # 演绎推理
    INDUCTIVE = "inductive"          # 归纳推理
    ABDUCTIVE = "abductive"          # 溯因推理
    ANALOGICAL = "analogical"        # 类比推理
    CAUSAL = "causal"               # 因果推理
    LOGICAL = "logical"             # 逻辑推理
    PROBABILISTIC = "probabilistic"  # 概率推理


class ConfidenceLevel(Enum):
    """置信度等级"""
    VERY_LOW = "very_low"      # 0.0 - 0.2
    LOW = "low"                # 0.2 - 0.4
    MEDIUM = "medium"          # 0.4 - 0.6
    HIGH = "high"              # 0.6 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_id: str
    description: str
    input_data: Any
    output_data: Any
    reasoning_type: ReasoningType
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    """推理结果"""
    conclusion: Any
    reasoning_type: ReasoningType
    confidence: float
    steps: List[ReasoningStep] = field(default_factory=list)
    premises: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """获取置信度等级"""
        if self.confidence < 0.2:
            return ConfidenceLevel.VERY_LOW
        elif self.confidence < 0.4:
            return ConfidenceLevel.LOW
        elif self.confidence < 0.6:
            return ConfidenceLevel.MEDIUM
        elif self.confidence < 0.8:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "conclusion": self.conclusion,
            "reasoning_type": self.reasoning_type.value,
            "confidence": self.confidence,
            "confidence_level": self.get_confidence_level().value,
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "reasoning_type": step.reasoning_type.value,
                    "confidence": step.confidence,
                    "timestamp": step.timestamp.isoformat()
                }
                for step in self.steps
            ],
            "premises": self.premises,
            "assumptions": self.assumptions,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class BaseReasoner(ABC):
    """基础推理器抽象类"""
    
    def __init__(self, name: str, reasoning_type: ReasoningType):
        self.name = name
        self.reasoning_type = reasoning_type
        self.enabled = True
        self.config = {}
    
    @abstractmethod
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """推理方法"""
        pass
    
    @abstractmethod
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """检查是否可以处理给定的前提"""
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置推理器"""
        self.config.update(config)


class LogicalReasoner(BaseReasoner):
    """逻辑推理器"""
    
    def __init__(self):
        super().__init__("LogicalReasoner", ReasoningType.LOGICAL)
        
        # 逻辑连接词
        self.logical_operators = {
            "and": ["and", "且", "并且", "同时"],
            "or": ["or", "或", "或者"],
            "not": ["not", "非", "不是", "并非"],
            "if": ["if", "如果", "假如", "若"],
            "then": ["then", "那么", "则"],
            "implies": ["implies", "意味着", "导致"]
        }
        
        # 逻辑模式
        self.patterns = {
            "modus_ponens": r"如果(.+)，那么(.+)。(.+)。因此(.+)",
            "modus_tollens": r"如果(.+)，那么(.+)。不是(.+)。因此不是(.+)",
            "hypothetical_syllogism": r"如果(.+)，那么(.+)。如果(.+)，那么(.+)。因此如果(.+)，那么(.+)"
        }
    
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """检查是否可以处理逻辑推理"""
        if not premises:
            return False
        
        # 检查是否包含逻辑连接词
        text = " ".join(premises).lower()
        for operator_type, keywords in self.logical_operators.items():
            if any(keyword in text for keyword in keywords):
                return True
        
        return False
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """执行逻辑推理"""
        if not self.can_handle(premises, context):
            raise ValueError("LogicalReasoner cannot handle the given premises")
        
        steps = []
        conclusion = None
        confidence = 0.6
        
        # 尝试应用不同的逻辑推理规则
        for premise in premises:
            # Modus Ponens (肯定前件)
            if "如果" in premise and "那么" in premise:
                step = ReasoningStep(
                    step_id=f"logical_step_{len(steps) + 1}",
                    description="应用肯定前件推理规则",
                    input_data=premise,
                    output_data="识别条件语句",
                    reasoning_type=ReasoningType.LOGICAL,
                    confidence=0.7
                )
                steps.append(step)
                
                # 简单的条件语句解析
                parts = premise.split("那么")
                if len(parts) == 2:
                    condition = parts[0].replace("如果", "").strip()
                    result = parts[1].strip()
                    conclusion = f"基于条件'{condition}'，可以推断出'{result}'"
                    confidence = 0.7
        
        # 如果没有找到明确的逻辑结构，进行一般性逻辑分析
        if conclusion is None:
            step = ReasoningStep(
                step_id=f"logical_step_{len(steps) + 1}",
                description="一般逻辑分析",
                input_data=premises,
                output_data="逻辑关系分析",
                reasoning_type=ReasoningType.LOGICAL,
                confidence=0.5
            )
            steps.append(step)
            
            conclusion = f"基于给定前提，存在逻辑关联性"
            confidence = 0.5
        
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.LOGICAL,
            confidence=confidence,
            steps=steps,
            premises=premises,
            metadata={"reasoner": self.name}
        )


class CausalReasoner(BaseReasoner):
    """因果推理器"""
    
    def __init__(self):
        super().__init__("CausalReasoner", ReasoningType.CAUSAL)
        
        # 因果关系指示词
        self.causal_indicators = {
            "cause": ["因为", "由于", "因", "导致", "引起", "造成", "because", "due to", "cause", "lead to"],
            "effect": ["所以", "因此", "结果", "导致", "造成", "therefore", "thus", "result in", "consequently"]
        }
    
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """检查是否可以处理因果推理"""
        text = " ".join(premises).lower()
        
        # 检查因果指示词
        all_indicators = []
        for indicators in self.causal_indicators.values():
            all_indicators.extend(indicators)
        
        return any(indicator in text for indicator in all_indicators)
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """执行因果推理"""
        if not self.can_handle(premises, context):
            raise ValueError("CausalReasoner cannot handle the given premises")
        
        steps = []
        causes = []
        effects = []
        
        # 分析因果关系
        for premise in premises:
            premise_lower = premise.lower()
            
            # 查找原因
            for cause_word in self.causal_indicators["cause"]:
                if cause_word in premise_lower:
                    # 简单的因果关系提取
                    parts = premise.split(cause_word)
                    if len(parts) >= 2:
                        cause = parts[1].strip()
                        causes.append(cause)
                        
                        step = ReasoningStep(
                            step_id=f"causal_step_{len(steps) + 1}",
                            description=f"识别原因: {cause}",
                            input_data=premise,
                            output_data=cause,
                            reasoning_type=ReasoningType.CAUSAL,
                            confidence=0.6
                        )
                        steps.append(step)
            
            # 查找结果
            for effect_word in self.causal_indicators["effect"]:
                if effect_word in premise_lower:
                    parts = premise.split(effect_word)
                    if len(parts) >= 2:
                        effect = parts[1].strip()
                        effects.append(effect)
                        
                        step = ReasoningStep(
                            step_id=f"causal_step_{len(steps) + 1}",
                            description=f"识别结果: {effect}",
                            input_data=premise,
                            output_data=effect,
                            reasoning_type=ReasoningType.CAUSAL,
                            confidence=0.6
                        )
                        steps.append(step)
        
        # 构建因果链
        if causes and effects:
            conclusion = f"因果关系链: {' -> '.join(causes)} 导致 {' -> '.join(effects)}"
            confidence = 0.7
        elif causes:
            conclusion = f"识别到原因: {', '.join(causes)}"
            confidence = 0.6
        elif effects:
            conclusion = f"识别到结果: {', '.join(effects)}"
            confidence = 0.6
        else:
            conclusion = "存在潜在的因果关系，但需要更多信息进行分析"
            confidence = 0.4
        
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.CAUSAL,
            confidence=confidence,
            steps=steps,
            premises=premises,
            metadata={
                "reasoner": self.name,
                "causes": causes,
                "effects": effects
            }
        )


class AnalogicalReasoner(BaseReasoner):
    """类比推理器"""
    
    def __init__(self):
        super().__init__("AnalogicalReasoner", ReasoningType.ANALOGICAL)
        
        # 类比指示词
        self.analogy_indicators = [
            "像", "如同", "类似", "好比", "就像", "相当于",
            "like", "similar to", "analogous to", "comparable to", "as"
        ]
    
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """检查是否可以处理类比推理"""
        text = " ".join(premises).lower()
        return any(indicator in text for indicator in self.analogy_indicators)
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """执行类比推理"""
        if not self.can_handle(premises, context):
            raise ValueError("AnalogicalReasoner cannot handle the given premises")
        
        steps = []
        analogies = []
        
        # 识别类比关系
        for premise in premises:
            for indicator in self.analogy_indicators:
                if indicator in premise:
                    parts = premise.split(indicator)
                    if len(parts) >= 2:
                        source = parts[0].strip()
                        target = parts[1].strip()
                        
                        analogy = {
                            "source": source,
                            "target": target,
                            "relationship": indicator
                        }
                        analogies.append(analogy)
                        
                        step = ReasoningStep(
                            step_id=f"analogical_step_{len(steps) + 1}",
                            description=f"识别类比: {source} {indicator} {target}",
                            input_data=premise,
                            output_data=analogy,
                            reasoning_type=ReasoningType.ANALOGICAL,
                            confidence=0.6
                        )
                        steps.append(step)
        
        # 生成类比推理结论
        if analogies:
            conclusion = f"基于类比推理，发现了{len(analogies)}个类比关系"
            confidence = 0.6
            
            # 如果有多个类比，尝试找出共同模式
            if len(analogies) > 1:
                conclusion += "，这些类比可能揭示了共同的结构或模式"
                confidence = 0.7
        else:
            conclusion = "未能识别出明确的类比关系"
            confidence = 0.3
        
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.ANALOGICAL,
            confidence=confidence,
            steps=steps,
            premises=premises,
            metadata={
                "reasoner": self.name,
                "analogies": analogies
            }
        )


class InductiveReasoner(BaseReasoner):
    """归纳推理器"""
    
    def __init__(self):
        super().__init__("InductiveReasoner", ReasoningType.INDUCTIVE)
    
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """检查是否可以处理归纳推理"""
        # 归纳推理通常需要多个相似的观察或实例
        return len(premises) >= 2
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """执行归纳推理"""
        if not self.can_handle(premises, context):
            raise ValueError("InductiveReasoner requires at least 2 premises")
        
        steps = []
        patterns = []
        
        # 寻找共同模式
        step = ReasoningStep(
            step_id="inductive_step_1",
            description="分析前提中的共同模式",
            input_data=premises,
            output_data="模式识别",
            reasoning_type=ReasoningType.INDUCTIVE,
            confidence=0.5
        )
        steps.append(step)
        
        # 简单的模式识别：查找共同词汇
        all_words = []
        for premise in premises:
            words = premise.lower().split()
            all_words.extend(words)
        
        # 计算词频
        word_freq = {}
        for word in all_words:
            if len(word) > 3:  # 忽略短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 找出高频词作为模式
        common_words = [word for word, freq in word_freq.items() if freq >= 2]
        
        if common_words:
            patterns = common_words[:5]  # 取前5个
            conclusion = f"基于归纳推理，发现共同模式: {', '.join(patterns)}"
            confidence = 0.6
        else:
            conclusion = "基于归纳推理，前提之间存在某种规律性，但需要更多数据来确定具体模式"
            confidence = 0.4
        
        # 生成一般性结论
        step = ReasoningStep(
            step_id="inductive_step_2",
            description="生成一般性结论",
            input_data=patterns,
            output_data=conclusion,
            reasoning_type=ReasoningType.INDUCTIVE,
            confidence=confidence
        )
        steps.append(step)
        
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.INDUCTIVE,
            confidence=confidence,
            steps=steps,
            premises=premises,
            metadata={
                "reasoner": self.name,
                "patterns": patterns,
                "common_words": common_words
            }
        )


class ReasoningEngine:
    """推理引擎 - 管理多个推理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.reasoners: Dict[str, BaseReasoner] = {}
        self.reasoning_history: List[ReasoningResult] = []
        self.max_history = 500
        
        # 初始化规划引擎
        from .planning import PlanningEngine
        self.planning_engine = PlanningEngine(self.config.get('planning', {}))
        
        # 注册默认推理器
        self.register_reasoner(LogicalReasoner())
        self.register_reasoner(CausalReasoner())
        self.register_reasoner(AnalogicalReasoner())
        self.register_reasoner(InductiveReasoner())
    
    def register_reasoner(self, reasoner: BaseReasoner) -> None:
        """注册推理器"""
        self.reasoners[reasoner.name] = reasoner
    
    def unregister_reasoner(self, name: str) -> bool:
        """注销推理器"""
        if name in self.reasoners:
            del self.reasoners[name]
            return True
        return False
    
    def get_reasoner(self, name: str) -> Optional[BaseReasoner]:
        """获取推理器"""
        return self.reasoners.get(name)
    
    def list_reasoners(self) -> List[str]:
        """列出所有推理器"""
        return list(self.reasoners.keys())
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None, 
                    preferred_reasoner: str = None) -> ReasoningResult:
        """执行推理"""
        if not premises:
            raise ValueError("Premises cannot be empty")
        
        # 如果指定了首选推理器
        if preferred_reasoner and preferred_reasoner in self.reasoners:
            reasoner = self.reasoners[preferred_reasoner]
            if reasoner.can_handle(premises, context) and reasoner.enabled:
                result = await reasoner.reason(premises, context)
                self._add_to_history(result)
                return result
        
        # 自动选择最合适的推理器
        best_reasoner = None
        best_score = 0
        
        for reasoner in self.reasoners.values():
            if reasoner.enabled and reasoner.can_handle(premises, context):
                # 简单的选择策略：优先选择特定类型的推理器
                score = 1
                if reasoner.reasoning_type == ReasoningType.LOGICAL:
                    score = 3  # 逻辑推理优先级高
                elif reasoner.reasoning_type == ReasoningType.CAUSAL:
                    score = 2  # 因果推理次之
                
                if score > best_score:
                    best_score = score
                    best_reasoner = reasoner
        
        if best_reasoner:
            result = await best_reasoner.reason(premises, context)
            self._add_to_history(result)
            return result
        
        # 如果没有合适的推理器，返回基础推理结果
        result = ReasoningResult(
            conclusion="无法进行具体推理，但前提已被记录",
            reasoning_type=ReasoningType.LOGICAL,
            confidence=0.1,
            premises=premises,
            metadata={"fallback": True}
        )
        self._add_to_history(result)
        return result
    
    async def multi_perspective_reasoning(self, premises: List[str], 
                                        context: Dict[str, Any] = None) -> List[ReasoningResult]:
        """多角度推理 - 使用多个推理器分析同一组前提"""
        results = []
        
        for reasoner in self.reasoners.values():
            if reasoner.enabled and reasoner.can_handle(premises, context):
                try:
                    result = await reasoner.reason(premises, context)
                    results.append(result)
                except Exception as e:
                    # 记录错误但继续其他推理器
                    error_result = ReasoningResult(
                        conclusion=f"推理器 {reasoner.name} 出错: {str(e)}",
                        reasoning_type=reasoner.reasoning_type,
                        confidence=0.0,
                        premises=premises,
                        metadata={"error": True, "reasoner": reasoner.name}
                    )
                    results.append(error_result)
        
        # 将所有结果添加到历史
        for result in results:
            self._add_to_history(result)
        
        return results
    
    def _add_to_history(self, result: ReasoningResult) -> None:
        """添加到推理历史"""
        self.reasoning_history.append(result)
        
        # 限制历史记录大小
        if len(self.reasoning_history) > self.max_history:
            self.reasoning_history = self.reasoning_history[-self.max_history:]
    
    def get_recent_reasoning(self, count: int = 10) -> List[ReasoningResult]:
        """获取最近的推理结果"""
        return self.reasoning_history[-count:]
    
    def get_reasoning_stats(self) -> Dict[str, Any]:
        """获取推理统计信息"""
        if not self.reasoning_history:
            return {"total": 0}
        
        # 统计各类型推理的数量和平均置信度
        type_stats = {}
        for result in self.reasoning_history:
            reasoning_type = result.reasoning_type.value
            if reasoning_type not in type_stats:
                type_stats[reasoning_type] = {"count": 0, "total_confidence": 0}
            
            type_stats[reasoning_type]["count"] += 1
            type_stats[reasoning_type]["total_confidence"] += result.confidence
        
        # 计算平均置信度
        for stats in type_stats.values():
            stats["average_confidence"] = stats["total_confidence"] / stats["count"]
            del stats["total_confidence"]
        
        return {
            "total": len(self.reasoning_history),
            "type_distribution": type_stats,
            "reasoners_count": len(self.reasoners),
            "enabled_reasoners": sum(1 for r in self.reasoners.values() if r.enabled)
        }
    
    def clear_history(self) -> None:
        """清空推理历史"""
        self.reasoning_history.clear()
    
    async def create_plan(self, goal: str, constraints: Dict[str, Any] = None):
        """创建执行计划 - 委托给规划引擎"""
        from .planning import Constraint
        
        # 转换约束格式
        constraint_list = []
        if constraints:
            for key, value in constraints.items():
                constraint_list.append(Constraint(
                    constraint_id=str(uuid.uuid4()),
                    type=key,
                    description=f"{key}: {value}",
                    parameters={"value": value}
                ))
        
        return await self.planning_engine.create_plan(goal, constraints=constraint_list)
    
    async def reason(self, premises: List[str], reasoning_types: List[ReasoningType] = None, 
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """增强的推理方法 - 支持多种推理类型"""
        if not reasoning_types:
            reasoning_types = [ReasoningType.LOGICAL]
        
        results = []
        
        # 对每种推理类型执行推理
        for reasoning_type in reasoning_types:
            # 找到对应的推理器
            reasoner = None
            for r in self.reasoners.values():
                if r.reasoning_type == reasoning_type and r.enabled and r.can_handle(premises, context):
                    reasoner = r
                    break
            
            if reasoner:
                try:
                    result = await reasoner.reason(premises, context)
                    results.append({
                        "reasoning_type": reasoning_type.value,
                        "result": result,
                        "success": True
                    })
                except Exception as e:
                    results.append({
                        "reasoning_type": reasoning_type.value,
                        "error": str(e),
                        "success": False
                    })
            else:
                results.append({
                    "reasoning_type": reasoning_type.value,
                    "error": f"No suitable reasoner found for {reasoning_type.value}",
                    "success": False
                })
        
        # 选择最佳结果
        successful_results = [r for r in results if r.get("success", False)]
        if successful_results:
            best_result = max(successful_results, key=lambda x: x["result"].confidence if hasattr(x["result"], 'confidence') else 0.5)
        else:
            # 创建默认结果
            from .reasoning import ReasoningResult
            best_result = {
                "reasoning_type": "fallback",
                "result": ReasoningResult(
                    conclusion="Unable to perform reasoning with available reasoners",
                    reasoning_type=ReasoningType.LOGICAL,
                    confidence=0.1,
                    premises=premises
                ),
                "success": False
            }
        
        return {
            "best_result": best_result["result"] if best_result.get("success") else best_result,
            "all_results": results,
            "reasoning_types_used": reasoning_types,
            "success_count": len(successful_results),
            "total_count": len(results)
        } 