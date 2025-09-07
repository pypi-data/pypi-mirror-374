"""
Learning Module - 学习模块
提供多模式学习能力：监督学习、无监督学习、强化学习、元学习
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import numpy as np
from collections import defaultdict, deque
import pickle


class LearningType(Enum):
    """学习类型枚举"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    META = "meta"
    TRANSFER = "transfer"
    ONLINE = "online"


class LearningStrategy(Enum):
    """学习策略枚举"""
    INCREMENTAL = "incremental"
    BATCH = "batch"
    ACTIVE = "active"
    PASSIVE = "passive"


@dataclass
class Experience:
    """经验数据"""
    experience_id: str
    state: Any
    action: Any
    reward: Optional[float] = None
    next_state: Optional[Any] = None
    outcome: Optional[Any] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningExample:
    """学习样例"""
    example_id: str
    input_data: Any
    target_output: Optional[Any] = None
    features: Dict[str, Any] = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    confidence: float = 1.0
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Pattern:
    """模式"""
    pattern_id: str
    pattern_type: str
    description: str
    features: Dict[str, Any]
    frequency: int = 1
    confidence: float = 0.5
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class Skill:
    """技能"""
    skill_id: str
    name: str
    description: str
    proficiency_level: float = 0.0  # 0.0 to 1.0
    usage_count: int = 0
    success_rate: float = 0.0
    learning_progress: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_practiced: Optional[datetime] = None


@dataclass
class LearningGoal:
    """学习目标"""
    goal_id: str
    description: str
    target_skill: str
    target_proficiency: float
    current_progress: float = 0.0
    deadline: Optional[datetime] = None
    priority: float = 0.5
    status: str = "active"  # active, completed, paused, cancelled
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class BaseLearner(ABC):
    """学习器基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_trained = False
    
    @abstractmethod
    async def learn(self, examples: List[LearningExample]) -> Dict[str, Any]:
        """执行学习"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any) -> Dict[str, Any]:
        """进行预测"""
        pass
    
    @abstractmethod
    async def evaluate(self, test_examples: List[LearningExample]) -> Dict[str, Any]:
        """评估模型性能"""
        pass
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        return {
            "is_trained": self.is_trained,
            "config": self.config
        }


class SupervisedLearning(BaseLearner):
    """监督学习器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.model_data = {}
        self.training_history = []
    
    async def learn(self, examples: List[LearningExample]) -> Dict[str, Any]:
        """执行监督学习"""
        if not examples:
            return {"success": False, "error": "No training examples provided"}
        
        # 简化的监督学习实现
        learning_stats = {
            "examples_processed": len(examples),
            "features_extracted": 0,
            "patterns_learned": 0
        }
        
        # 提取特征和标签
        features_data = []
        labels_data = []
        
        for example in examples:
            if example.target_output is not None:
                features_data.append(example.input_data)
                labels_data.append(example.target_output)
        
        # 构建简单的映射模型
        self.model_data = {
            "input_output_mapping": dict(zip(features_data, labels_data)),
            "feature_statistics": self._calculate_feature_statistics(examples),
            "label_distribution": self._calculate_label_distribution(examples)
        }
        
        learning_stats["features_extracted"] = len(self.model_data["feature_statistics"])
        learning_stats["patterns_learned"] = len(self.model_data["input_output_mapping"])
        
        # 记录训练历史
        training_record = {
            "timestamp": datetime.now(),
            "examples_count": len(examples),
            "model_version": len(self.training_history) + 1
        }
        self.training_history.append(training_record)
        
        self.is_trained = True
        
        return {
            "success": True,
            "statistics": learning_stats,
            "model_info": {
                "type": "supervised",
                "training_examples": len(examples),
                "model_size": len(self.model_data["input_output_mapping"])
            }
        }
    
    async def predict(self, input_data: Any) -> Dict[str, Any]:
        """进行预测"""
        if not self.is_trained:
            return {"success": False, "error": "Model not trained"}
        
        # 简单的最近邻预测
        if input_data in self.model_data["input_output_mapping"]:
            prediction = self.model_data["input_output_mapping"][input_data]
            confidence = 1.0
        else:
            # 寻找最相似的输入
            best_match = self._find_best_match(input_data)
            if best_match:
                prediction = self.model_data["input_output_mapping"][best_match]
                confidence = 0.7  # 降低置信度
            else:
                prediction = None
                confidence = 0.0
        
        return {
            "success": True,
            "prediction": prediction,
            "confidence": confidence,
            "model_type": "supervised"
        }
    
    async def evaluate(self, test_examples: List[LearningExample]) -> Dict[str, Any]:
        """评估模型性能"""
        if not self.is_trained:
            return {"success": False, "error": "Model not trained"}
        
        correct_predictions = 0
        total_predictions = 0
        
        for example in test_examples:
            if example.target_output is not None:
                prediction_result = await self.predict(example.input_data)
                if prediction_result["success"] and prediction_result["prediction"] == example.target_output:
                    correct_predictions += 1
                total_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        return {
            "success": True,
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_feature_statistics(self, examples: List[LearningExample]) -> Dict[str, Any]:
        """计算特征统计信息"""
        feature_stats = defaultdict(list)
        
        for example in examples:
            for feature_name, feature_value in example.features.items():
                feature_stats[feature_name].append(feature_value)
        
        # 计算基本统计量
        stats = {}
        for feature_name, values in feature_stats.items():
            if values:
                stats[feature_name] = {
                    "count": len(values),
                    "unique_values": len(set(str(v) for v in values))
                }
        
        return stats
    
    def _calculate_label_distribution(self, examples: List[LearningExample]) -> Dict[str, int]:
        """计算标签分布"""
        label_counts = defaultdict(int)
        
        for example in examples:
            if example.target_output is not None:
                label_counts[str(example.target_output)] += 1
        
        return dict(label_counts)
    
    def _find_best_match(self, input_data: Any) -> Optional[Any]:
        """寻找最佳匹配"""
        # 简化的相似度匹配
        input_str = str(input_data).lower()
        best_match = None
        best_similarity = 0.0
        
        for known_input in self.model_data["input_output_mapping"].keys():
            known_str = str(known_input).lower()
            similarity = self._calculate_similarity(input_str, known_str)
            
            if similarity > best_similarity and similarity > 0.5:  # 相似度阈值
                best_similarity = similarity
                best_match = known_input
        
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        # 简单的Jaccard相似度
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


class UnsupervisedLearning(BaseLearner):
    """无监督学习器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.clusters = {}
        self.patterns = {}
    
    async def learn(self, examples: List[LearningExample]) -> Dict[str, Any]:
        """执行无监督学习"""
        if not examples:
            return {"success": False, "error": "No examples provided"}
        
        learning_stats = {
            "examples_processed": len(examples),
            "clusters_found": 0,
            "patterns_discovered": 0
        }
        
        # 简单的聚类分析
        clusters = await self._perform_clustering(examples)
        self.clusters = clusters
        learning_stats["clusters_found"] = len(clusters)
        
        # 模式发现
        patterns = await self._discover_patterns(examples)
        self.patterns = patterns
        learning_stats["patterns_discovered"] = len(patterns)
        
        self.is_trained = True
        
        return {
            "success": True,
            "statistics": learning_stats,
            "clusters": list(clusters.keys()),
            "patterns": list(patterns.keys())
        }
    
    async def predict(self, input_data: Any) -> Dict[str, Any]:
        """进行聚类预测"""
        if not self.is_trained:
            return {"success": False, "error": "Model not trained"}
        
        # 找到最匹配的聚类
        best_cluster = await self._assign_to_cluster(input_data)
        
        return {
            "success": True,
            "cluster": best_cluster,
            "confidence": 0.8,
            "model_type": "unsupervised"
        }
    
    async def evaluate(self, test_examples: List[LearningExample]) -> Dict[str, Any]:
        """评估聚类质量"""
        if not self.is_trained:
            return {"success": False, "error": "Model not trained"}
        
        # 简化的聚类质量评估
        cluster_assignments = []
        for example in test_examples:
            cluster = await self._assign_to_cluster(example.input_data)
            cluster_assignments.append(cluster)
        
        # 计算聚类内聚性
        cohesion_score = self._calculate_cohesion(cluster_assignments)
        
        return {
            "success": True,
            "cohesion_score": cohesion_score,
            "total_clusters": len(self.clusters),
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    async def _perform_clustering(self, examples: List[LearningExample]) -> Dict[str, List[str]]:
        """执行聚类分析"""
        # 简化的基于特征的聚类
        clusters = defaultdict(list)
        
        for example in examples:
            # 基于输入数据的简单聚类
            cluster_key = self._determine_cluster_key(example.input_data)
            clusters[cluster_key].append(example.example_id)
        
        return dict(clusters)
    
    async def _discover_patterns(self, examples: List[LearningExample]) -> Dict[str, Dict[str, Any]]:
        """发现模式"""
        patterns = {}
        
        # 寻找频繁出现的特征组合
        feature_combinations = defaultdict(int)
        
        for example in examples:
            # 提取特征组合
            features_str = str(sorted(example.features.items()))
            feature_combinations[features_str] += 1
        
        # 将频繁模式转换为模式对象
        for pattern_str, frequency in feature_combinations.items():
            if frequency > 1:  # 至少出现2次才算模式
                pattern_id = f"pattern_{len(patterns)}"
                patterns[pattern_id] = {
                    "description": pattern_str,
                    "frequency": frequency,
                    "confidence": frequency / len(examples)
                }
        
        return patterns
    
    def _determine_cluster_key(self, input_data: Any) -> str:
        """确定聚类键"""
        # 简化的聚类键生成
        input_str = str(input_data)
        
        # 基于长度和首字符聚类
        length_category = "short" if len(input_str) < 10 else "medium" if len(input_str) < 50 else "long"
        first_char = input_str[0].lower() if input_str else "empty"
        
        return f"{length_category}_{first_char}"
    
    async def _assign_to_cluster(self, input_data: Any) -> str:
        """将输入分配到聚类"""
        cluster_key = self._determine_cluster_key(input_data)
        
        # 如果聚类存在，返回该聚类；否则返回最相似的聚类
        if cluster_key in self.clusters:
            return cluster_key
        
        # 寻找最相似的聚类
        best_cluster = None
        best_similarity = 0.0
        
        for existing_cluster in self.clusters.keys():
            similarity = self._calculate_cluster_similarity(cluster_key, existing_cluster)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = existing_cluster
        
        return best_cluster or "unknown"
    
    def _calculate_cluster_similarity(self, cluster1: str, cluster2: str) -> float:
        """计算聚类相似度"""
        # 简单的字符串相似度
        common_chars = set(cluster1) & set(cluster2)
        total_chars = set(cluster1) | set(cluster2)
        
        return len(common_chars) / len(total_chars) if total_chars else 0.0
    
    def _calculate_cohesion(self, cluster_assignments: List[str]) -> float:
        """计算聚类内聚性"""
        if not cluster_assignments:
            return 0.0
        
        # 计算聚类分布的均匀性
        cluster_counts = defaultdict(int)
        for cluster in cluster_assignments:
            cluster_counts[cluster] += 1
        
        total_items = len(cluster_assignments)
        expected_size = total_items / len(cluster_counts) if cluster_counts else 1
        
        # 计算与期望大小的偏差
        deviation_sum = sum(abs(count - expected_size) for count in cluster_counts.values())
        max_possible_deviation = total_items
        
        cohesion = 1.0 - (deviation_sum / max_possible_deviation) if max_possible_deviation > 0 else 1.0
        return cohesion


class ReinforcementLearning(BaseLearner):
    """强化学习器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = self.config.get("learning_rate", 0.1)
        self.discount_factor = self.config.get("discount_factor", 0.9)
        self.epsilon = self.config.get("epsilon", 0.1)  # exploration rate
        self.experiences = []
    
    async def learn(self, experiences: List[Experience]) -> Dict[str, Any]:
        """从经验中学习"""
        if not experiences:
            return {"success": False, "error": "No experiences provided"}
        
        learning_stats = {
            "experiences_processed": len(experiences),
            "q_values_updated": 0,
            "average_reward": 0.0
        }
        
        total_reward = 0.0
        q_updates = 0
        
        for experience in experiences:
            if experience.reward is not None:
                # Q-learning更新
                current_q = self.q_table[str(experience.state)][str(experience.action)]
                
                if experience.next_state is not None:
                    # 计算下一状态的最大Q值
                    next_state_q_values = self.q_table[str(experience.next_state)]
                    max_next_q = max(next_state_q_values.values()) if next_state_q_values else 0.0
                else:
                    max_next_q = 0.0  # 终止状态
                
                # Q-learning公式: Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
                new_q = current_q + self.learning_rate * (
                    experience.reward + self.discount_factor * max_next_q - current_q
                )
                
                self.q_table[str(experience.state)][str(experience.action)] = new_q
                q_updates += 1
                total_reward += experience.reward
        
        # 存储经验
        self.experiences.extend(experiences)
        
        learning_stats["q_values_updated"] = q_updates
        learning_stats["average_reward"] = total_reward / len(experiences) if experiences else 0.0
        
        self.is_trained = True
        
        return {
            "success": True,
            "statistics": learning_stats,
            "q_table_size": len(self.q_table),
            "total_experiences": len(self.experiences)
        }
    
    async def predict(self, state: Any) -> Dict[str, Any]:
        """选择动作（预测）"""
        state_str = str(state)
        
        if state_str not in self.q_table:
            return {
                "success": True,
                "action": "random",
                "confidence": 0.0,
                "exploration": True
            }
        
        state_q_values = self.q_table[state_str]
        
        # ε-贪心策略
        if np.random.random() < self.epsilon:
            # 探索：随机选择动作
            action = np.random.choice(list(state_q_values.keys())) if state_q_values else "random"
            exploration = True
            confidence = 0.1
        else:
            # 利用：选择Q值最高的动作
            action = max(state_q_values.items(), key=lambda x: x[1])[0]
            exploration = False
            confidence = 0.9
        
        return {
            "success": True,
            "action": action,
            "confidence": confidence,
            "exploration": exploration,
            "q_value": state_q_values.get(action, 0.0)
        }
    
    async def evaluate(self, test_experiences: List[Experience]) -> Dict[str, Any]:
        """评估强化学习性能"""
        if not test_experiences:
            return {"success": False, "error": "No test experiences provided"}
        
        total_reward = 0.0
        correct_actions = 0
        total_actions = 0
        
        for experience in test_experiences:
            if experience.reward is not None:
                total_reward += experience.reward
            
            # 检查是否选择了正确的动作
            prediction_result = await self.predict(experience.state)
            if prediction_result["success"] and prediction_result["action"] == str(experience.action):
                correct_actions += 1
            total_actions += 1
        
        average_reward = total_reward / len(test_experiences) if test_experiences else 0.0
        action_accuracy = correct_actions / total_actions if total_actions > 0 else 0.0
        
        return {
            "success": True,
            "average_reward": average_reward,
            "total_reward": total_reward,
            "action_accuracy": action_accuracy,
            "episodes_evaluated": len(test_experiences)
        }
    
    def update_exploration_rate(self, new_epsilon: float) -> None:
        """更新探索率"""
        self.epsilon = max(0.01, min(1.0, new_epsilon))  # 限制在合理范围内
    
    def get_policy(self) -> Dict[str, str]:
        """获取当前策略"""
        policy = {}
        
        for state, actions in self.q_table.items():
            if actions:
                best_action = max(actions.items(), key=lambda x: x[1])[0]
                policy[state] = best_action
        
        return policy


class MetaLearning(BaseLearner):
    """元学习器 - 学习如何学习"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.learning_strategies = {}
        self.strategy_performance = defaultdict(list)
        self.meta_knowledge = {}
    
    async def learn(self, learning_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """元学习：从多个学习任务中学习"""
        if not learning_tasks:
            return {"success": False, "error": "No learning tasks provided"}
        
        learning_stats = {
            "tasks_processed": len(learning_tasks),
            "strategies_discovered": 0,
            "meta_patterns_found": 0
        }
        
        # 分析不同学习任务的特征和最佳策略
        for task in learning_tasks:
            task_features = task.get("features", {})
            task_performance = task.get("performance", {})
            best_strategy = task.get("best_strategy", "unknown")
            
            # 记录策略性能
            strategy_key = self._generate_strategy_key(task_features)
            self.strategy_performance[strategy_key].append({
                "strategy": best_strategy,
                "performance": task_performance,
                "features": task_features
            })
        
        # 发现元模式
        meta_patterns = self._discover_meta_patterns()
        self.meta_knowledge.update(meta_patterns)
        
        learning_stats["strategies_discovered"] = len(self.strategy_performance)
        learning_stats["meta_patterns_found"] = len(meta_patterns)
        
        self.is_trained = True
        
        return {
            "success": True,
            "statistics": learning_stats,
            "meta_knowledge": list(self.meta_knowledge.keys())
        }
    
    async def predict(self, task_features: Dict[str, Any]) -> Dict[str, Any]:
        """预测最佳学习策略"""
        if not self.is_trained:
            return {"success": False, "error": "Meta-learner not trained"}
        
        strategy_key = self._generate_strategy_key(task_features)
        
        # 寻找最相似的已知任务类型
        best_strategy = self._recommend_strategy(task_features)
        
        return {
            "success": True,
            "recommended_strategy": best_strategy["strategy"],
            "confidence": best_strategy["confidence"],
            "reasoning": best_strategy["reasoning"]
        }
    
    async def evaluate(self, test_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估元学习性能"""
        if not self.is_trained:
            return {"success": False, "error": "Meta-learner not trained"}
        
        correct_recommendations = 0
        total_recommendations = 0
        
        for task in test_tasks:
            task_features = task.get("features", {})
            actual_best_strategy = task.get("best_strategy", "unknown")
            
            prediction_result = await self.predict(task_features)
            if (prediction_result["success"] and 
                prediction_result["recommended_strategy"] == actual_best_strategy):
                correct_recommendations += 1
            
            total_recommendations += 1
        
        accuracy = correct_recommendations / total_recommendations if total_recommendations > 0 else 0.0
        
        return {
            "success": True,
            "recommendation_accuracy": accuracy,
            "correct_recommendations": correct_recommendations,
            "total_recommendations": total_recommendations
        }
    
    def _generate_strategy_key(self, task_features: Dict[str, Any]) -> str:
        """生成策略键"""
        # 基于任务特征生成键
        key_components = []
        
        for feature, value in sorted(task_features.items()):
            if isinstance(value, (int, float)):
                # 数值特征离散化
                if value < 0.3:
                    category = "low"
                elif value < 0.7:
                    category = "medium"
                else:
                    category = "high"
                key_components.append(f"{feature}_{category}")
            else:
                key_components.append(f"{feature}_{str(value)}")
        
        return "_".join(key_components)
    
    def _discover_meta_patterns(self) -> Dict[str, Any]:
        """发现元模式"""
        patterns = {}
        
        # 分析策略性能模式
        for strategy_key, performances in self.strategy_performance.items():
            if len(performances) > 1:  # 至少有2个样本
                # 计算平均性能
                avg_performance = {}
                for perf_record in performances:
                    for metric, value in perf_record["performance"].items():
                        if metric not in avg_performance:
                            avg_performance[metric] = []
                        avg_performance[metric].append(value)
                
                # 计算平均值
                for metric in avg_performance:
                    values = avg_performance[metric]
                    if all(isinstance(v, (int, float)) for v in values):
                        avg_performance[metric] = sum(values) / len(values)
                
                patterns[strategy_key] = {
                    "average_performance": avg_performance,
                    "sample_count": len(performances),
                    "most_common_strategy": self._find_most_common_strategy(performances)
                }
        
        return patterns
    
    def _find_most_common_strategy(self, performances: List[Dict[str, Any]]) -> str:
        """找到最常见的策略"""
        strategy_counts = defaultdict(int)
        
        for perf_record in performances:
            strategy = perf_record.get("strategy", "unknown")
            strategy_counts[strategy] += 1
        
        return max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else "unknown"
    
    def _recommend_strategy(self, task_features: Dict[str, Any]) -> Dict[str, Any]:
        """推荐学习策略"""
        strategy_key = self._generate_strategy_key(task_features)
        
        # 直接匹配
        if strategy_key in self.meta_knowledge:
            pattern = self.meta_knowledge[strategy_key]
            return {
                "strategy": pattern["most_common_strategy"],
                "confidence": 0.9,
                "reasoning": f"Direct match with pattern {strategy_key}"
            }
        
        # 寻找最相似的模式
        best_match = None
        best_similarity = 0.0
        
        for known_key, pattern in self.meta_knowledge.items():
            similarity = self._calculate_pattern_similarity(strategy_key, known_key)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = pattern
        
        if best_match and best_similarity > 0.5:
            return {
                "strategy": best_match["most_common_strategy"],
                "confidence": best_similarity * 0.8,
                "reasoning": f"Similar pattern match with confidence {best_similarity:.2f}"
            }
        
        # 默认策略
        return {
            "strategy": "supervised",  # 默认推荐监督学习
            "confidence": 0.3,
            "reasoning": "No similar patterns found, using default strategy"
        }
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """计算模式相似度"""
        components1 = set(pattern1.split("_"))
        components2 = set(pattern2.split("_"))
        
        intersection = len(components1 & components2)
        union = len(components1 | components2)
        
        return intersection / union if union > 0 else 0.0


class ExperienceBuffer:
    """经验缓冲区"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.capacity = self.config.get("capacity", 10000)
        self.experiences = deque(maxlen=self.capacity)
        self.experience_index = {}
    
    def add_experience(self, experience: Experience) -> None:
        """添加经验"""
        self.experiences.append(experience)
        self.experience_index[experience.experience_id] = experience
        
        # 如果超出容量，从索引中删除最旧的经验
        if len(self.experiences) == self.capacity and len(self.experience_index) > self.capacity:
            # 清理索引中不再存在于deque中的经验
            valid_ids = {exp.experience_id for exp in self.experiences}
            self.experience_index = {k: v for k, v in self.experience_index.items() if k in valid_ids}
    
    def get_experiences(self, 
                       count: Optional[int] = None,
                       criteria: Optional[Dict[str, Any]] = None) -> List[Experience]:
        """获取经验"""
        # 过滤经验
        filtered_experiences = []
        
        for experience in self.experiences:
            if self._matches_criteria(experience, criteria):
                filtered_experiences.append(experience)
        
        # 限制数量
        if count is not None:
            filtered_experiences = filtered_experiences[-count:]  # 获取最近的经验
        
        return filtered_experiences
    
    def _matches_criteria(self, experience: Experience, criteria: Optional[Dict[str, Any]]) -> bool:
        """检查经验是否符合条件"""
        if criteria is None:
            return True
        
        # 奖励范围过滤
        if "reward_range" in criteria and experience.reward is not None:
            min_reward, max_reward = criteria["reward_range"]
            if not (min_reward <= experience.reward <= max_reward):
                return False
        
        # 时间范围过滤
        if "time_range" in criteria:
            start_time, end_time = criteria["time_range"]
            if not (start_time <= experience.timestamp <= end_time):
                return False
        
        # 上下文匹配
        if "context_keys" in criteria:
            required_keys = criteria["context_keys"]
            if not all(key in experience.context for key in required_keys):
                return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓冲区统计信息"""
        if not self.experiences:
            return {
                "total_experiences": 0,
                "capacity": self.capacity,
                "utilization": 0.0
            }
        
        rewards = [exp.reward for exp in self.experiences if exp.reward is not None]
        
        return {
            "total_experiences": len(self.experiences),
            "capacity": self.capacity,
            "utilization": len(self.experiences) / self.capacity,
            "reward_statistics": {
                "count": len(rewards),
                "average": sum(rewards) / len(rewards) if rewards else 0.0,
                "min": min(rewards) if rewards else None,
                "max": max(rewards) if rewards else None
            },
            "time_range": {
                "earliest": min(exp.timestamp for exp in self.experiences),
                "latest": max(exp.timestamp for exp in self.experiences)
            }
        }


class PatternRecognizer:
    """模式识别器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.patterns = {}
        self.pattern_threshold = self.config.get("pattern_threshold", 3)
    
    async def recognize_patterns(self, data: List[Any]) -> List[Pattern]:
        """识别模式"""
        if not data:
            return []
        
        # 序列模式识别
        sequence_patterns = self._find_sequence_patterns(data)
        
        # 频率模式识别
        frequency_patterns = self._find_frequency_patterns(data)
        
        # 结构模式识别
        structure_patterns = self._find_structure_patterns(data)
        
        all_patterns = sequence_patterns + frequency_patterns + structure_patterns
        
        # 更新模式库
        for pattern in all_patterns:
            if pattern.pattern_id in self.patterns:
                # 更新现有模式
                existing_pattern = self.patterns[pattern.pattern_id]
                existing_pattern.frequency += pattern.frequency
                existing_pattern.last_seen = datetime.now()
                existing_pattern.examples.extend(pattern.examples)
            else:
                # 添加新模式
                self.patterns[pattern.pattern_id] = pattern
        
        return all_patterns
    
    def _find_sequence_patterns(self, data: List[Any]) -> List[Pattern]:
        """寻找序列模式"""
        patterns = []
        
        # 寻找重复的子序列
        for length in range(2, min(6, len(data) // 2)):  # 序列长度2-5
            for start in range(len(data) - length + 1):
                subsequence = data[start:start + length]
                
                # 计算这个子序列在数据中的出现次数
                count = 0
                for i in range(len(data) - length + 1):
                    if data[i:i + length] == subsequence:
                        count += 1
                
                if count >= self.pattern_threshold:
                    pattern_id = f"seq_{hash(str(subsequence)) % 10000}"
                    pattern = Pattern(
                        pattern_id=pattern_id,
                        pattern_type="sequence",
                        description=f"Repeated subsequence: {subsequence}",
                        features={"length": length, "elements": subsequence},
                        frequency=count,
                        confidence=count / (len(data) - length + 1),
                        examples=[str(subsequence)]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_frequency_patterns(self, data: List[Any]) -> List[Pattern]:
        """寻找频率模式"""
        patterns = []
        
        # 统计元素频率
        frequency_count = defaultdict(int)
        for item in data:
            frequency_count[str(item)] += 1
        
        # 寻找高频元素
        total_items = len(data)
        for item, count in frequency_count.items():
            if count >= self.pattern_threshold:
                frequency_ratio = count / total_items
                
                pattern_id = f"freq_{hash(item) % 10000}"
                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="frequency",
                    description=f"High frequency item: {item}",
                    features={"item": item, "frequency_ratio": frequency_ratio},
                    frequency=count,
                    confidence=frequency_ratio,
                    examples=[item]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_structure_patterns(self, data: List[Any]) -> List[Pattern]:
        """寻找结构模式"""
        patterns = []
        
        # 寻找数据类型模式
        type_sequence = [type(item).__name__ for item in data]
        type_pattern_count = defaultdict(int)
        
        # 寻找类型序列模式
        for length in range(2, min(4, len(type_sequence))):
            for start in range(len(type_sequence) - length + 1):
                type_subseq = tuple(type_sequence[start:start + length])
                type_pattern_count[type_subseq] += 1
        
        for type_pattern, count in type_pattern_count.items():
            if count >= self.pattern_threshold:
                pattern_id = f"struct_{hash(str(type_pattern)) % 10000}"
                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="structure",
                    description=f"Type sequence pattern: {type_pattern}",
                    features={"type_sequence": type_pattern, "length": len(type_pattern)},
                    frequency=count,
                    confidence=count / (len(type_sequence) - len(type_pattern) + 1),
                    examples=[str(type_pattern)]
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Pattern]:
        """获取模式"""
        if pattern_type is None:
            return list(self.patterns.values())
        
        return [pattern for pattern in self.patterns.values() if pattern.pattern_type == pattern_type]


class SkillAcquisition:
    """技能习得系统"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.skills = {}
        self.learning_goals = {}
        self.skill_dependencies = defaultdict(set)
    
    def add_skill(self, skill: Skill) -> None:
        """添加技能"""
        self.skills[skill.skill_id] = skill
        
        # 建立技能依赖关系
        for prereq in skill.prerequisites:
            self.skill_dependencies[skill.skill_id].add(prereq)
    
    def set_learning_goal(self, goal: LearningGoal) -> None:
        """设置学习目标"""
        self.learning_goals[goal.goal_id] = goal
    
    async def practice_skill(self, skill_id: str, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """练习技能"""
        if skill_id not in self.skills:
            return {"success": False, "error": "Skill not found"}
        
        skill = self.skills[skill_id]
        
        # 检查前置技能
        missing_prerequisites = self._check_prerequisites(skill_id)
        if missing_prerequisites:
            return {
                "success": False, 
                "error": "Missing prerequisites",
                "missing_skills": missing_prerequisites
            }
        
        # 模拟技能练习
        practice_success = practice_data.get("success", True)
        practice_quality = practice_data.get("quality", 0.8)
        
        # 更新技能统计
        skill.usage_count += 1
        skill.last_practiced = datetime.now()
        
        # 更新成功率（指数移动平均）
        alpha = 0.1  # 学习率
        if practice_success:
            skill.success_rate = (1 - alpha) * skill.success_rate + alpha * 1.0
        else:
            skill.success_rate = (1 - alpha) * skill.success_rate + alpha * 0.0
        
        # 更新熟练度
        proficiency_gain = practice_quality * 0.05  # 每次练习最多提升5%
        skill.proficiency_level = min(1.0, skill.proficiency_level + proficiency_gain)
        
        # 更新学习进度
        skill.learning_progress["total_practice_sessions"] = skill.usage_count
        skill.learning_progress["last_improvement"] = proficiency_gain
        
        return {
            "success": True,
            "skill_id": skill_id,
            "new_proficiency": skill.proficiency_level,
            "success_rate": skill.success_rate,
            "proficiency_gain": proficiency_gain
        }
    
    def _check_prerequisites(self, skill_id: str) -> List[str]:
        """检查技能前置条件"""
        missing_skills = []
        
        if skill_id in self.skill_dependencies:
            for prereq_id in self.skill_dependencies[skill_id]:
                if prereq_id not in self.skills:
                    missing_skills.append(prereq_id)
                else:
                    prereq_skill = self.skills[prereq_id]
                    if prereq_skill.proficiency_level < 0.5:  # 需要至少50%熟练度
                        missing_skills.append(prereq_id)
        
        return missing_skills
    
    def get_learning_recommendations(self) -> List[Dict[str, Any]]:
        """获取学习建议"""
        recommendations = []
        
        # 基于学习目标的建议
        for goal in self.learning_goals.values():
            if goal.status == "active":
                target_skill_id = goal.target_skill
                
                if target_skill_id in self.skills:
                    skill = self.skills[target_skill_id]
                    progress_needed = goal.target_proficiency - skill.proficiency_level
                    
                    if progress_needed > 0:
                        # 估算需要的练习次数
                        estimated_sessions = int(progress_needed / 0.05)  # 假设每次提升5%
                        
                        recommendations.append({
                            "type": "skill_practice",
                            "skill_id": target_skill_id,
                            "skill_name": skill.name,
                            "current_proficiency": skill.proficiency_level,
                            "target_proficiency": goal.target_proficiency,
                            "progress_needed": progress_needed,
                            "estimated_sessions": estimated_sessions,
                            "priority": goal.priority
                        })
        
        # 基于技能依赖的建议
        for skill_id, skill in self.skills.items():
            if skill.proficiency_level < 0.3:  # 低熟练度技能
                missing_prereqs = self._check_prerequisites(skill_id)
                if missing_prereqs:
                    recommendations.append({
                        "type": "prerequisite_learning",
                        "skill_id": skill_id,
                        "skill_name": skill.name,
                        "missing_prerequisites": missing_prereqs,
                        "priority": 0.8
                    })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x.get("priority", 0.5), reverse=True)
        
        return recommendations
    
    def get_skill_statistics(self) -> Dict[str, Any]:
        """获取技能统计信息"""
        if not self.skills:
            return {
                "total_skills": 0,
                "average_proficiency": 0.0,
                "skills_by_proficiency": {}
            }
        
        total_skills = len(self.skills)
        total_proficiency = sum(skill.proficiency_level for skill in self.skills.values())
        average_proficiency = total_proficiency / total_skills
        
        # 按熟练度分类
        proficiency_categories = {"beginner": 0, "intermediate": 0, "advanced": 0, "expert": 0}
        
        for skill in self.skills.values():
            if skill.proficiency_level < 0.25:
                proficiency_categories["beginner"] += 1
            elif skill.proficiency_level < 0.5:
                proficiency_categories["intermediate"] += 1
            elif skill.proficiency_level < 0.8:
                proficiency_categories["advanced"] += 1
            else:
                proficiency_categories["expert"] += 1
        
        return {
            "total_skills": total_skills,
            "average_proficiency": average_proficiency,
            "skills_by_proficiency": proficiency_categories,
            "active_learning_goals": len([g for g in self.learning_goals.values() if g.status == "active"]),
            "total_practice_sessions": sum(skill.usage_count for skill in self.skills.values())
        }


class LearningModule:
    """学习模块 - 统一的学习系统"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 初始化各种学习器
        self.supervised_learning = SupervisedLearning(self.config.get("supervised", {}))
        self.unsupervised_learning = UnsupervisedLearning(self.config.get("unsupervised", {}))
        self.reinforcement_learning = ReinforcementLearning(self.config.get("reinforcement", {}))
        self.meta_learning = MetaLearning(self.config.get("meta", {}))
        
        # 初始化学习支持组件
        self.experience_buffer = ExperienceBuffer(self.config.get("experience_buffer", {}))
        self.pattern_recognizer = PatternRecognizer(self.config.get("pattern_recognition", {}))
        self.skill_acquisition = SkillAcquisition(self.config.get("skill_acquisition", {}))
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def learn(self, 
                   learning_type: LearningType, 
                   data: List[Any], 
                   **kwargs) -> Dict[str, Any]:
        """统一的学习接口"""
        try:
            if learning_type == LearningType.SUPERVISED:
                return await self.supervised_learning.learn(data)
            
            elif learning_type == LearningType.UNSUPERVISED:
                return await self.unsupervised_learning.learn(data)
            
            elif learning_type == LearningType.REINFORCEMENT:
                return await self.reinforcement_learning.learn(data)
            
            elif learning_type == LearningType.META:
                return await self.meta_learning.learn(data)
            
            else:
                return {"success": False, "error": f"Unsupported learning type: {learning_type}"}
        
        except Exception as e:
            self.logger.error(f"Learning error: {e}")
            return {"success": False, "error": str(e)}
    
    async def predict(self, learning_type: LearningType, input_data: Any) -> Dict[str, Any]:
        """统一的预测接口"""
        try:
            if learning_type == LearningType.SUPERVISED:
                return await self.supervised_learning.predict(input_data)
            
            elif learning_type == LearningType.UNSUPERVISED:
                return await self.unsupervised_learning.predict(input_data)
            
            elif learning_type == LearningType.REINFORCEMENT:
                return await self.reinforcement_learning.predict(input_data)
            
            elif learning_type == LearningType.META:
                return await self.meta_learning.predict(input_data)
            
            else:
                return {"success": False, "error": f"Unsupported learning type: {learning_type}"}
        
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            return {"success": False, "error": str(e)}
    
    def add_experience(self, experience: Experience) -> None:
        """添加经验到缓冲区"""
        self.experience_buffer.add_experience(experience)
    
    async def recognize_patterns(self, data: List[Any]) -> List[Pattern]:
        """识别模式"""
        return await self.pattern_recognizer.recognize_patterns(data)
    
    def add_skill(self, skill: Skill) -> None:
        """添加技能"""
        self.skill_acquisition.add_skill(skill)
    
    async def practice_skill(self, skill_id: str, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """练习技能"""
        return await self.skill_acquisition.practice_skill(skill_id, practice_data)
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        return {
            "supervised_learning": self.supervised_learning.get_learning_statistics(),
            "unsupervised_learning": self.unsupervised_learning.get_learning_statistics(),
            "reinforcement_learning": self.reinforcement_learning.get_learning_statistics(),
            "meta_learning": self.meta_learning.get_learning_statistics(),
            "experience_buffer": self.experience_buffer.get_statistics(),
            "skill_acquisition": self.skill_acquisition.get_skill_statistics(),
            "patterns_recognized": len(self.pattern_recognizer.get_patterns()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_learning_recommendations(self) -> List[Dict[str, Any]]:
        """获取学习建议"""
        return self.skill_acquisition.get_learning_recommendations() 