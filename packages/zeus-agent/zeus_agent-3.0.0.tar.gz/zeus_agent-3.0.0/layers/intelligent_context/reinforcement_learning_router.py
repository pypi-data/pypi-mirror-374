"""
强化学习路由器 - 自适应路由策略学习

基于强化学习的智能路由器，能够从用户反馈中学习并持续优化路由决策，
实现真正的"越用越聪明"的自适应系统。

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import logging
from collections import defaultdict, deque
import pickle
import random

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """动作类型"""
    ROUTE_TO_LOCAL_KB = "route_to_local_kb"
    ROUTE_TO_AI_TRAINING = "route_to_ai_training"
    ROUTE_TO_WEB_SEARCH = "route_to_web_search"
    ROUTE_TO_FUSION = "route_to_fusion"
    ROUTE_TO_CACHE = "route_to_cache"

class StateFeature(Enum):
    """状态特征"""
    QUERY_COMPLEXITY = "query_complexity"
    USER_ROLE = "user_role"
    DOMAIN_MATCH = "domain_match"
    TIME_SENSITIVITY = "time_sensitivity"
    COST_SENSITIVITY = "cost_sensitivity"
    QUALITY_REQUIREMENT = "quality_requirement"
    CONTEXT_CONTINUITY = "context_continuity"
    HISTORICAL_SUCCESS = "historical_success"

class RewardType(Enum):
    """奖励类型"""
    USER_SATISFACTION = "user_satisfaction"
    COST_EFFICIENCY = "cost_efficiency"
    RESPONSE_TIME = "response_time"
    ACCURACY = "accuracy"
    ENGAGEMENT = "engagement"

@dataclass
class State:
    """状态表示"""
    features: Dict[StateFeature, float]
    query_hash: str
    user_id: str
    session_id: str
    timestamp: datetime
    
    def to_vector(self) -> np.ndarray:
        """转换为向量表示"""
        return np.array([self.features.get(feature, 0.0) for feature in StateFeature])
    
    def __hash__(self) -> int:
        """状态哈希，用于Q表索引"""
        feature_tuple = tuple(round(self.features.get(f, 0.0), 2) for f in StateFeature)
        return hash(feature_tuple)

@dataclass
class Action:
    """动作表示"""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    estimated_cost: float = 0.0
    estimated_latency: float = 0.0

@dataclass
class Reward:
    """奖励信号"""
    total_reward: float
    reward_components: Dict[RewardType, float]
    feedback_timestamp: datetime
    explanation: str

@dataclass
class Experience:
    """经验样本 (State, Action, Reward, Next_State)"""
    state: State
    action: Action
    reward: Reward
    next_state: Optional[State]
    done: bool
    timestamp: datetime

class RewardFunction:
    """奖励函数"""
    
    def __init__(
        self,
        satisfaction_weight: float = 0.4,
        cost_weight: float = 0.2,
        speed_weight: float = 0.2,
        accuracy_weight: float = 0.2
    ):
        self.weights = {
            RewardType.USER_SATISFACTION: satisfaction_weight,
            RewardType.COST_EFFICIENCY: cost_weight,
            RewardType.RESPONSE_TIME: speed_weight,
            RewardType.ACCURACY: accuracy_weight
        }
    
    def calculate_reward(
        self,
        user_satisfaction: float,
        actual_cost: float,
        expected_cost: float,
        actual_latency: float,
        expected_latency: float,
        accuracy_score: float
    ) -> Reward:
        """计算综合奖励"""
        
        # 用户满意度奖励 (0-1)
        satisfaction_reward = user_satisfaction
        
        # 成本效率奖励
        cost_efficiency = max(0, 1 - actual_cost / max(expected_cost, 0.001))
        
        # 响应时间奖励
        speed_efficiency = max(0, 1 - actual_latency / max(expected_latency, 0.001))
        
        # 准确性奖励
        accuracy_reward = accuracy_score
        
        # 计算加权总奖励
        reward_components = {
            RewardType.USER_SATISFACTION: satisfaction_reward,
            RewardType.COST_EFFICIENCY: cost_efficiency,
            RewardType.RESPONSE_TIME: speed_efficiency,
            RewardType.ACCURACY: accuracy_reward
        }
        
        total_reward = sum(
            reward_components[reward_type] * self.weights[reward_type]
            for reward_type in reward_components
        )
        
        # 奖励范围归一化到 [-1, 1]
        total_reward = max(-1.0, min(1.0, total_reward * 2 - 1))
        
        explanation = f"满意度:{satisfaction_reward:.2f}, 成本效率:{cost_efficiency:.2f}, " \
                     f"速度:{speed_efficiency:.2f}, 准确性:{accuracy_reward:.2f}"
        
        return Reward(
            total_reward=total_reward,
            reward_components=reward_components,
            feedback_timestamp=datetime.now(),
            explanation=explanation
        )

class QLearningAgent:
    """Q学习智能体"""
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q表：状态-动作值函数
        self.q_table: Dict[Tuple[int, ActionType], float] = defaultdict(float)
        
        # 经验回放缓冲区
        self.experience_buffer: deque = deque(maxlen=10000)
        
        # 学习统计
        self.learning_stats = {
            'episodes': 0,
            'total_reward': 0.0,
            'average_reward': 0.0,
            'exploration_rate': self.epsilon,
            'q_table_size': 0
        }
        
        logger.info(f"🧠 Q学习智能体初始化 - 学习率:{learning_rate}, 折扣因子:{discount_factor}")
    
    def get_state_key(self, state: State) -> int:
        """获取状态键"""
        return hash(state)
    
    def select_action(self, state: State, available_actions: List[ActionType]) -> ActionType:
        """选择动作（ε-贪婪策略）"""
        state_key = self.get_state_key(state)
        
        # ε-贪婪策略
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            action = random.choice(available_actions)
            logger.debug(f"🎲 探索选择动作: {action.value}")
        else:
            # 利用：选择Q值最高的动作
            q_values = {action: self.q_table[(state_key, action)] for action in available_actions}
            action = max(q_values.items(), key=lambda x: x[1])[0]
            logger.debug(f"🎯 利用选择动作: {action.value} (Q值: {q_values[action]:.3f})")
        
        return action
    
    def learn_from_experience(self, experience: Experience):
        """从经验中学习"""
        # 添加到经验缓冲区
        self.experience_buffer.append(experience)
        
        # 获取状态和动作的键
        state_key = self.get_state_key(experience.state)
        action_key = (state_key, experience.action.action_type)
        
        # 计算目标Q值
        if experience.done or experience.next_state is None:
            target_q = experience.reward.total_reward
        else:
            next_state_key = self.get_state_key(experience.next_state)
            # 获取下一状态的最大Q值
            next_q_values = [
                self.q_table[(next_state_key, action)] 
                for action in ActionType
            ]
            max_next_q = max(next_q_values) if next_q_values else 0.0
            target_q = experience.reward.total_reward + self.discount_factor * max_next_q
        
        # 更新Q值
        current_q = self.q_table[action_key]
        self.q_table[action_key] += self.learning_rate * (target_q - current_q)
        
        # 更新探索率
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # 更新统计信息
        self.learning_stats['episodes'] += 1
        self.learning_stats['total_reward'] += experience.reward.total_reward
        self.learning_stats['average_reward'] = (
            self.learning_stats['total_reward'] / self.learning_stats['episodes']
        )
        self.learning_stats['exploration_rate'] = self.epsilon
        self.learning_stats['q_table_size'] = len(self.q_table)
        
        logger.debug(f"📚 学习更新 - Q值: {current_q:.3f} → {self.q_table[action_key]:.3f}")
    
    def batch_learn(self, batch_size: int = 32):
        """批量学习"""
        if len(self.experience_buffer) < batch_size:
            return
        
        # 随机采样经验
        batch = random.sample(list(self.experience_buffer), batch_size)
        
        for experience in batch:
            self.learn_from_experience(experience)
        
        logger.info(f"📚 批量学习完成 - 样本数: {batch_size}")
    
    def get_q_values(self, state: State) -> Dict[ActionType, float]:
        """获取状态的所有Q值"""
        state_key = self.get_state_key(state)
        return {action: self.q_table[(state_key, action)] for action in ActionType}
    
    def save_model(self, filepath: str):
        """保存模型"""
        model_data = {
            'q_table': dict(self.q_table),
            'learning_stats': self.learning_stats,
            'hyperparameters': {
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min
            }
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"💾 模型已保存到 {filepath}")
    
    def load_model(self, filepath: str):
        """加载模型"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_table = defaultdict(float, model_data['q_table'])
            self.learning_stats = model_data['learning_stats']
            
            # 恢复超参数
            params = model_data['hyperparameters']
            self.learning_rate = params['learning_rate']
            self.discount_factor = params['discount_factor']
            self.epsilon = params['epsilon']
            self.epsilon_decay = params['epsilon_decay']
            self.epsilon_min = params['epsilon_min']
            
            logger.info(f"📂 模型已从 {filepath} 加载")
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")

class StateExtractor:
    """状态特征提取器"""
    
    def __init__(self):
        self.feature_extractors = {
            StateFeature.QUERY_COMPLEXITY: self._extract_query_complexity,
            StateFeature.USER_ROLE: self._extract_user_role,
            StateFeature.DOMAIN_MATCH: self._extract_domain_match,
            StateFeature.TIME_SENSITIVITY: self._extract_time_sensitivity,
            StateFeature.COST_SENSITIVITY: self._extract_cost_sensitivity,
            StateFeature.QUALITY_REQUIREMENT: self._extract_quality_requirement,
            StateFeature.CONTEXT_CONTINUITY: self._extract_context_continuity,
            StateFeature.HISTORICAL_SUCCESS: self._extract_historical_success
        }
    
    def extract_state(
        self,
        query: str,
        user_profile: Dict[str, Any],
        context: Dict[str, Any],
        session_history: List[Dict[str, Any]]
    ) -> State:
        """提取状态特征"""
        
        features = {}
        for feature_type in StateFeature:
            try:
                extractor = self.feature_extractors[feature_type]
                features[feature_type] = extractor(query, user_profile, context, session_history)
            except Exception as e:
                logger.warning(f"⚠️ 特征提取失败 {feature_type.value}: {e}")
                features[feature_type] = 0.0
        
        return State(
            features=features,
            query_hash=str(hash(query)),
            user_id=user_profile.get('user_id', 'anonymous'),
            session_id=context.get('session_id', 'default'),
            timestamp=datetime.now()
        )
    
    def _extract_query_complexity(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取查询复杂度特征"""
        # 基于查询长度和复杂性关键词
        complexity_score = 0.0
        
        # 长度因子
        length_score = min(1.0, len(query) / 200)
        complexity_score += length_score * 0.3
        
        # 复杂性关键词
        complex_keywords = ['如何实现', '设计方案', '优化', '架构', '算法', '比较', '分析']
        keyword_score = sum(1 for keyword in complex_keywords if keyword in query) / len(complex_keywords)
        complexity_score += keyword_score * 0.4
        
        # 技术术语密度
        technical_terms = ['FPGA', 'HDL', 'RTL', 'Verilog', 'VHDL', '时序', '综合']
        term_density = sum(1 for term in technical_terms if term in query) / max(len(query.split()), 1)
        complexity_score += min(1.0, term_density * 10) * 0.3
        
        return min(1.0, complexity_score)
    
    def _extract_user_role(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取用户角色特征"""
        role_mapping = {
            'beginner': 0.0,
            'intermediate': 0.33,
            'expert': 0.67,
            'researcher': 1.0
        }
        return role_mapping.get(user_profile.get('role', 'beginner'), 0.0)
    
    def _extract_domain_match(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取领域匹配度特征"""
        fpga_keywords = ['FPGA', 'HDL', 'Verilog', 'VHDL', '可编程', '逻辑', '综合', '仿真']
        matches = sum(1 for keyword in fpga_keywords if keyword.lower() in query.lower())
        return min(1.0, matches / 3)  # 归一化到[0,1]
    
    def _extract_time_sensitivity(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取时间敏感性特征"""
        time_keywords = ['最新', '当前', '现在', '今年', '最近', '趋势', '发展']
        time_score = sum(1 for keyword in time_keywords if keyword in query) / len(time_keywords)
        return min(1.0, time_score * 2)
    
    def _extract_cost_sensitivity(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取成本敏感性特征"""
        # 基于用户角色和历史行为推断成本敏感性
        role = user_profile.get('role', 'beginner')
        if role == 'beginner':
            return 0.8  # 初学者对成本敏感
        elif role == 'intermediate':
            return 0.5  # 中级用户中等敏感
        else:
            return 0.2  # 专家和研究者对成本不太敏感
    
    def _extract_quality_requirement(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取质量要求特征"""
        quality_keywords = ['最佳', '推荐', '标准', '规范', '权威', '官方', '专业']
        quality_score = sum(1 for keyword in quality_keywords if keyword in query) / len(quality_keywords)
        
        # 结合用户角色
        role = user_profile.get('role', 'beginner')
        role_quality_factor = {'beginner': 0.5, 'intermediate': 0.7, 'expert': 0.9, 'researcher': 1.0}
        
        return min(1.0, quality_score + role_quality_factor.get(role, 0.5))
    
    def _extract_context_continuity(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取上下文连续性特征"""
        if not history:
            return 0.0
        
        # 检查与最近查询的相似性
        recent_queries = [item.get('query', '') for item in history[-3:]]
        if not recent_queries:
            return 0.0
        
        # 简单的词汇重叠度计算
        query_words = set(query.lower().split())
        max_overlap = 0.0
        
        for recent_query in recent_queries:
            recent_words = set(recent_query.lower().split())
            if recent_words:
                overlap = len(query_words & recent_words) / len(query_words | recent_words)
                max_overlap = max(max_overlap, overlap)
        
        return max_overlap
    
    def _extract_historical_success(
        self, query: str, user_profile: Dict, context: Dict, history: List
    ) -> float:
        """提取历史成功率特征"""
        if not history:
            return 0.5  # 默认中等成功率
        
        # 计算最近查询的平均满意度
        recent_satisfactions = []
        for item in history[-10:]:  # 最近10次查询
            if 'satisfaction' in item:
                recent_satisfactions.append(item['satisfaction'])
        
        if recent_satisfactions:
            return sum(recent_satisfactions) / len(recent_satisfactions)
        else:
            return 0.5

class ReinforcementLearningRouter:
    """强化学习路由器"""
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.1,
        model_save_path: Optional[str] = None
    ):
        self.q_agent = QLearningAgent(
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=exploration_rate
        )
        
        self.state_extractor = StateExtractor()
        self.reward_function = RewardFunction()
        self.model_save_path = model_save_path
        
        # 路由历史和会话管理
        self.routing_history: List[Dict[str, Any]] = []
        self.active_sessions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.pending_experiences: Dict[str, Experience] = {}
        
        # 性能统计
        self.performance_stats = {
            'total_routes': 0,
            'successful_routes': 0,
            'average_reward': 0.0,
            'learning_episodes': 0,
            'exploration_ratio': 0.0
        }
        
        logger.info("🧠 强化学习路由器初始化完成")
    
    async def initialize(self):
        """初始化路由器"""
        # 加载预训练模型（如果存在）
        if self.model_save_path:
            try:
                self.q_agent.load_model(self.model_save_path)
                logger.info("📂 加载了预训练的强化学习模型")
            except:
                logger.info("🆕 未找到预训练模型，从头开始学习")
        
        # 启动定期保存任务
        if self.model_save_path:
            asyncio.create_task(self._periodic_model_save())
    
    async def route_query(
        self,
        query: str,
        user_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[ActionType, Dict[str, Any]]:
        """路由查询"""
        session_id = context.get('session_id', 'default')
        session_history = self.active_sessions[session_id]
        
        # 提取当前状态
        current_state = self.state_extractor.extract_state(
            query, user_profile, context, session_history
        )
        
        # 获取可用动作
        available_actions = list(ActionType)
        
        # 选择动作
        selected_action = self.q_agent.select_action(current_state, available_actions)
        
        # 创建动作对象
        action = Action(
            action_type=selected_action,
            parameters=self._get_action_parameters(selected_action, current_state),
            confidence=self._estimate_action_confidence(selected_action, current_state),
            estimated_cost=self._estimate_action_cost(selected_action),
            estimated_latency=self._estimate_action_latency(selected_action)
        )
        
        # 记录路由决策
        route_record = {
            'timestamp': datetime.now(),
            'query': query,
            'state': current_state,
            'action': action,
            'user_id': user_profile.get('user_id', 'anonymous'),
            'session_id': session_id
        }
        
        self.routing_history.append(route_record)
        session_history.append(route_record)
        
        # 创建待完成的经验（等待反馈）
        experience_key = f"{session_id}_{len(session_history)}"
        self.pending_experiences[experience_key] = Experience(
            state=current_state,
            action=action,
            reward=None,  # 待填充
            next_state=None,  # 待填充
            done=False,
            timestamp=datetime.now()
        )
        
        # 更新统计
        self.performance_stats['total_routes'] += 1
        self.performance_stats['exploration_ratio'] = self.q_agent.epsilon
        
        logger.info(f"🎯 强化学习路由: {query[:50]}... → {selected_action.value}")
        
        # 返回路由决策和元数据
        return selected_action, {
            'experience_key': experience_key,
            'confidence': action.confidence,
            'estimated_cost': action.estimated_cost,
            'estimated_latency': action.estimated_latency,
            'q_values': self.q_agent.get_q_values(current_state),
            'state_features': current_state.features
        }
    
    async def provide_feedback(
        self,
        experience_key: str,
        user_satisfaction: float,
        actual_cost: float,
        actual_latency: float,
        accuracy_score: float,
        next_query: Optional[str] = None,
        next_user_profile: Optional[Dict[str, Any]] = None,
        next_context: Optional[Dict[str, Any]] = None
    ):
        """提供反馈，完成学习循环"""
        if experience_key not in self.pending_experiences:
            logger.warning(f"⚠️ 未找到经验键: {experience_key}")
            return
        
        experience = self.pending_experiences[experience_key]
        
        # 计算奖励
        reward = self.reward_function.calculate_reward(
            user_satisfaction=user_satisfaction,
            actual_cost=actual_cost,
            expected_cost=experience.action.estimated_cost,
            actual_latency=actual_latency,
            expected_latency=experience.action.estimated_latency,
            accuracy_score=accuracy_score
        )
        
        # 提取下一状态（如果有下一个查询）
        next_state = None
        if next_query and next_user_profile and next_context:
            session_id = next_context.get('session_id', 'default')
            session_history = self.active_sessions[session_id]
            next_state = self.state_extractor.extract_state(
                next_query, next_user_profile, next_context, session_history
            )
        
        # 完成经验
        experience.reward = reward
        experience.next_state = next_state
        experience.done = (next_state is None)
        
        # 学习
        self.q_agent.learn_from_experience(experience)
        
        # 更新统计
        self.performance_stats['learning_episodes'] += 1
        if user_satisfaction > 0.7:  # 认为满意度>0.7为成功
            self.performance_stats['successful_routes'] += 1
        
        total_reward = self.q_agent.learning_stats['total_reward']
        episodes = self.q_agent.learning_stats['episodes']
        self.performance_stats['average_reward'] = total_reward / max(episodes, 1)
        
        # 清理已完成的经验
        del self.pending_experiences[experience_key]
        
        logger.info(f"📚 强化学习反馈: 奖励={reward.total_reward:.3f}, 满意度={user_satisfaction:.2f}")
    
    def _get_action_parameters(self, action: ActionType, state: State) -> Dict[str, Any]:
        """获取动作参数"""
        parameters = {}
        
        if action == ActionType.ROUTE_TO_FUSION:
            # 根据状态特征决定融合策略
            if state.features.get(StateFeature.TIME_SENSITIVITY, 0) > 0.7:
                parameters['fusion_strategy'] = 'temporal_fusion'
            elif state.features.get(StateFeature.QUALITY_REQUIREMENT, 0) > 0.8:
                parameters['fusion_strategy'] = 'quality_driven_fusion'
            elif state.features.get(StateFeature.COST_SENSITIVITY, 0) > 0.7:
                parameters['fusion_strategy'] = 'cost_aware_fusion'
            else:
                parameters['fusion_strategy'] = 'semantic_fusion'
        
        return parameters
    
    def _estimate_action_confidence(self, action: ActionType, state: State) -> float:
        """估算动作置信度"""
        # 基于Q值和状态特征估算置信度
        state_key = self.q_agent.get_state_key(state)
        q_value = self.q_agent.q_table[(state_key, action)]
        
        # 将Q值转换为置信度 [0, 1]
        confidence = max(0.0, min(1.0, (q_value + 1) / 2))
        
        return confidence
    
    def _estimate_action_cost(self, action: ActionType) -> float:
        """估算动作成本"""
        cost_mapping = {
            ActionType.ROUTE_TO_CACHE: 0.001,
            ActionType.ROUTE_TO_LOCAL_KB: 0.1,
            ActionType.ROUTE_TO_AI_TRAINING: 1.0,
            ActionType.ROUTE_TO_WEB_SEARCH: 0.5,
            ActionType.ROUTE_TO_FUSION: 2.0
        }
        return cost_mapping.get(action, 0.5)
    
    def _estimate_action_latency(self, action: ActionType) -> float:
        """估算动作延迟"""
        latency_mapping = {
            ActionType.ROUTE_TO_CACHE: 0.1,
            ActionType.ROUTE_TO_LOCAL_KB: 0.8,
            ActionType.ROUTE_TO_AI_TRAINING: 2.5,
            ActionType.ROUTE_TO_WEB_SEARCH: 1.5,
            ActionType.ROUTE_TO_FUSION: 4.0
        }
        return latency_mapping.get(action, 2.0)
    
    async def _periodic_model_save(self):
        """定期保存模型"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时保存一次
                
                if self.model_save_path and self.q_agent.learning_stats['episodes'] > 0:
                    self.q_agent.save_model(self.model_save_path)
                    logger.info("💾 定期保存强化学习模型")
                    
            except Exception as e:
                logger.error(f"❌ 模型保存失败: {e}")
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """获取学习分析数据"""
        return {
            'q_learning_stats': self.q_agent.learning_stats,
            'performance_stats': self.performance_stats,
            'routing_history_size': len(self.routing_history),
            'active_sessions': len(self.active_sessions),
            'pending_experiences': len(self.pending_experiences),
            'q_table_insights': self._analyze_q_table()
        }
    
    def _analyze_q_table(self) -> Dict[str, Any]:
        """分析Q表"""
        if not self.q_agent.q_table:
            return {'empty_table': True}
        
        # 统计Q值分布
        q_values = list(self.q_agent.q_table.values())
        
        # 统计动作偏好
        action_preferences = defaultdict(list)
        for (state_key, action), q_value in self.q_agent.q_table.items():
            action_preferences[action].append(q_value)
        
        action_stats = {}
        for action, q_vals in action_preferences.items():
            action_stats[action.value] = {
                'avg_q_value': sum(q_vals) / len(q_vals),
                'max_q_value': max(q_vals),
                'min_q_value': min(q_vals),
                'count': len(q_vals)
            }
        
        return {
            'total_state_action_pairs': len(q_values),
            'avg_q_value': sum(q_values) / len(q_values),
            'max_q_value': max(q_values),
            'min_q_value': min(q_values),
            'action_preferences': action_stats
        }
    
    async def export_learning_data(self, filepath: str):
        """导出学习数据"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'learning_analytics': self.get_learning_analytics(),
            'routing_history': [
                {
                    'timestamp': record['timestamp'].isoformat(),
                    'query': record['query'],
                    'action': record['action'].action_type.value,
                    'confidence': record['action'].confidence,
                    'user_id': record['user_id']
                }
                for record in self.routing_history[-1000:]  # 最近1000条记录
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 学习数据已导出到 {filepath}")

# 工厂函数
def create_reinforcement_learning_router(
    learning_rate: float = 0.1,
    discount_factor: float = 0.95,
    exploration_rate: float = 0.1,
    model_save_path: Optional[str] = None
) -> ReinforcementLearningRouter:
    """创建强化学习路由器"""
    return ReinforcementLearningRouter(
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        exploration_rate=exploration_rate,
        model_save_path=model_save_path
    ) 