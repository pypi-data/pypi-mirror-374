"""
Context Manager - 上下文管理器
负责统一管理和协调各种上下文信息
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .context_store import ContextStore
from .relevance_engine import RelevanceEngine
from .memory_manager import MemoryManager
from .context_adapter import ContextAdapter
from .context_optimizer import ContextOptimizer

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """上下文类型"""
    SYSTEM = "system"           # 系统上下文
    USER = "user"              # 用户上下文
    CONVERSATION = "conversation"  # 对话上下文
    TASK = "task"              # 任务上下文
    DOMAIN = "domain"          # 领域上下文
    TEMPORAL = "temporal"      # 时间上下文
    ENVIRONMENTAL = "environmental"  # 环境上下文


class ContextPriority(Enum):
    """上下文优先级"""
    CRITICAL = 1    # 关键上下文
    HIGH = 2        # 高优先级
    MEDIUM = 3      # 中等优先级
    LOW = 4         # 低优先级
    BACKGROUND = 5  # 背景上下文


@dataclass
class ContextItem:
    """上下文项"""
    id: str
    type: ContextType
    content: Any
    priority: ContextPriority
    relevance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_access(self):
        """更新访问信息"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_context_size: int = 8000, relevance_threshold: float = 0.3):
        self.max_context_size = max_context_size
        self.relevance_threshold = relevance_threshold
        
        # 初始化子组件
        self.context_store = ContextStore()
        self.relevance_engine = RelevanceEngine()
        self.memory_manager = MemoryManager()
        self.context_adapter = ContextAdapter()
        self.context_optimizer = ContextOptimizer()
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    async def build_context(self, 
                          task_description: str,
                          user_id: str = None,
                          session_id: str = None,
                          agent_type: str = None,
                          additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        构建完整的上下文
        
        Args:
            task_description: 任务描述
            user_id: 用户ID
            session_id: 会话ID
            agent_type: Agent类型
            additional_context: 额外上下文
            
        Returns:
            构建好的上下文字典
        """
        try:
            self.logger.info(f"Building context for task: {task_description[:100]}...")
            
            # 1. 收集各类上下文
            contexts = await self._collect_contexts(
                task_description, user_id, session_id, agent_type, additional_context
            )
            
            # 2. 计算相关性评分
            await self._calculate_relevance_scores(contexts, task_description)
            
            # 3. 过滤和排序上下文
            filtered_contexts = self._filter_and_sort_contexts(contexts)
            
            # 4. 优化上下文大小
            optimized_contexts = await self._optimize_context_size(filtered_contexts)
            
            # 5. 适配上下文格式
            formatted_context = await self.context_adapter.format_context(
                optimized_contexts, agent_type
            )
            
            # 6. 更新访问统计
            await self._update_access_statistics(optimized_contexts)
            
            self.logger.info(f"Context built successfully with {len(optimized_contexts)} items")
            return formatted_context
            
        except Exception as e:
            self.logger.error(f"Error building context: {str(e)}")
            # 返回基础上下文
            return await self._build_fallback_context(task_description, agent_type)
    
    async def _collect_contexts(self, 
                              task_description: str,
                              user_id: str,
                              session_id: str,
                              agent_type: str,
                              additional_context: Dict[str, Any]) -> List[ContextItem]:
        """收集各类上下文"""
        contexts = []
        
        # 系统上下文
        system_context = await self._get_system_context(agent_type)
        contexts.extend(system_context)
        
        # 用户上下文
        if user_id:
            user_context = await self._get_user_context(user_id)
            contexts.extend(user_context)
        
        # 会话上下文
        if session_id:
            conversation_context = await self._get_conversation_context(session_id)
            contexts.extend(conversation_context)
        
        # 任务相关上下文
        task_context = await self._get_task_context(task_description)
        contexts.extend(task_context)
        
        # 领域知识上下文
        domain_context = await self._get_domain_context(task_description, agent_type)
        contexts.extend(domain_context)
        
        # 时间上下文
        temporal_context = await self._get_temporal_context()
        contexts.extend(temporal_context)
        
        # 额外上下文
        if additional_context:
            extra_context = self._process_additional_context(additional_context)
            contexts.extend(extra_context)
        
        return contexts
    
    async def _get_system_context(self, agent_type: str) -> List[ContextItem]:
        """获取系统上下文"""
        system_contexts = []
        
        # Agent角色定义
        role_definition = await self.context_store.get_agent_role(agent_type)
        if role_definition:
            system_contexts.append(ContextItem(
                id=f"role_{agent_type}",
                type=ContextType.SYSTEM,
                content=role_definition,
                priority=ContextPriority.CRITICAL,
                metadata={"category": "role_definition"}
            ))
        
        # 系统规则和约束
        system_rules = await self.context_store.get_system_rules()
        if system_rules:
            system_contexts.append(ContextItem(
                id="system_rules",
                type=ContextType.SYSTEM,
                content=system_rules,
                priority=ContextPriority.HIGH,
                metadata={"category": "rules"}
            ))
        
        return system_contexts
    
    async def _get_user_context(self, user_id: str) -> List[ContextItem]:
        """获取用户上下文"""
        user_contexts = []
        
        # 用户偏好
        user_preferences = await self.memory_manager.get_user_preferences(user_id)
        if user_preferences:
            user_contexts.append(ContextItem(
                id=f"preferences_{user_id}",
                type=ContextType.USER,
                content=user_preferences,
                priority=ContextPriority.HIGH,
                metadata={"category": "preferences"}
            ))
        
        # 用户历史行为
        user_history = await self.memory_manager.get_user_history(user_id, limit=10)
        if user_history:
            user_contexts.append(ContextItem(
                id=f"history_{user_id}",
                type=ContextType.USER,
                content=user_history,
                priority=ContextPriority.MEDIUM,
                metadata={"category": "history"}
            ))
        
        return user_contexts
    
    async def _get_conversation_context(self, session_id: str) -> List[ContextItem]:
        """获取对话上下文"""
        conversation_contexts = []
        
        # 获取对话历史
        conversation_history = await self.memory_manager.get_conversation_history(
            session_id, limit=20
        )
        
        if conversation_history:
            conversation_contexts.append(ContextItem(
                id=f"conversation_{session_id}",
                type=ContextType.CONVERSATION,
                content=conversation_history,
                priority=ContextPriority.HIGH,
                metadata={"category": "conversation_history"}
            ))
        
        return conversation_contexts
    
    async def _get_task_context(self, task_description: str) -> List[ContextItem]:
        """获取任务相关上下文"""
        task_contexts = []
        
        # 相似任务经验
        similar_tasks = await self.memory_manager.find_similar_tasks(task_description, limit=5)
        if similar_tasks:
            task_contexts.append(ContextItem(
                id="similar_tasks",
                type=ContextType.TASK,
                content=similar_tasks,
                priority=ContextPriority.MEDIUM,
                metadata={"category": "similar_tasks"}
            ))
        
        return task_contexts
    
    async def _get_domain_context(self, task_description: str, agent_type: str) -> List[ContextItem]:
        """获取领域知识上下文"""
        domain_contexts = []
        
        # 领域特定知识
        domain_knowledge = await self.context_store.get_domain_knowledge(
            task_description, agent_type
        )
        
        if domain_knowledge:
            domain_contexts.append(ContextItem(
                id="domain_knowledge",
                type=ContextType.DOMAIN,
                content=domain_knowledge,
                priority=ContextPriority.MEDIUM,
                metadata={"category": "domain_knowledge"}
            ))
        
        return domain_contexts
    
    async def _get_temporal_context(self) -> List[ContextItem]:
        """获取时间上下文"""
        temporal_contexts = []
        
        # 当前时间信息
        current_time = datetime.now()
        time_info = {
            "current_datetime": current_time.isoformat(),
            "day_of_week": current_time.strftime("%A"),
            "time_of_day": self._get_time_of_day(current_time)
        }
        
        temporal_contexts.append(ContextItem(
            id="current_time",
            type=ContextType.TEMPORAL,
            content=time_info,
            priority=ContextPriority.LOW,
            metadata={"category": "current_time"}
        ))
        
        return temporal_contexts
    
    def _process_additional_context(self, additional_context: Dict[str, Any]) -> List[ContextItem]:
        """处理额外上下文"""
        contexts = []
        
        for key, value in additional_context.items():
            contexts.append(ContextItem(
                id=f"additional_{key}",
                type=ContextType.ENVIRONMENTAL,
                content={key: value},
                priority=ContextPriority.MEDIUM,
                metadata={"category": "additional", "key": key}
            ))
        
        return contexts
    
    async def _calculate_relevance_scores(self, contexts: List[ContextItem], task_description: str):
        """计算相关性评分"""
        for context_item in contexts:
            score = await self.relevance_engine.calculate_relevance(
                context_item.content, task_description, context_item.type
            )
            context_item.relevance_score = score
    
    def _filter_and_sort_contexts(self, contexts: List[ContextItem]) -> List[ContextItem]:
        """过滤和排序上下文"""
        # 过滤低相关性的上下文
        filtered_contexts = [
            ctx for ctx in contexts 
            if ctx.relevance_score >= self.relevance_threshold or 
               ctx.priority.value <= ContextPriority.HIGH.value
        ]
        
        # 按优先级和相关性排序
        filtered_contexts.sort(
            key=lambda x: (x.priority.value, -x.relevance_score)
        )
        
        return filtered_contexts
    
    async def _optimize_context_size(self, contexts: List[ContextItem]) -> List[ContextItem]:
        """优化上下文大小"""
        return await self.context_optimizer.optimize_size(contexts, self.max_context_size)
    
    async def _update_access_statistics(self, contexts: List[ContextItem]):
        """更新访问统计"""
        for context_item in contexts:
            context_item.update_access()
            await self.context_store.update_context_stats(context_item)
    
    async def _build_fallback_context(self, task_description: str, agent_type: str) -> Dict[str, Any]:
        """构建回退上下文"""
        return {
            "system_prompt": f"You are a {agent_type} assistant.",
            "user_prompt": task_description,
            "context_items": [],
            "metadata": {"fallback": True}
        }
    
    def _get_time_of_day(self, current_time: datetime) -> str:
        """获取时段"""
        hour = current_time.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def add_context_feedback(self, context_id: str, feedback: Dict[str, Any]):
        """添加上下文反馈"""
        await self.context_optimizer.add_feedback(context_id, feedback)
    
    async def get_context_analytics(self) -> Dict[str, Any]:
        """获取上下文分析"""
        return await self.context_store.get_analytics() 