"""
语义缓存系统 - 智能查询缓存和响应复用

基于语义相似度的智能缓存系统，可以显著降低成本和提升响应速度。
支持用户角色兼容性检查、缓存新鲜度管理、智能缓存策略等功能。

Author: ADC Team
Date: 2024-12-19
Version: 1.0.0
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from collections import defaultdict

from .vector_database_service import VectorDatabaseService
from .embedding_service import EmbeddingService
from ..framework.abstractions.knowledge_based_agent import UserRole

logger = logging.getLogger(__name__)

class CachePriority(Enum):
    """缓存优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CacheStatus(Enum):
    """缓存状态"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    PENDING = "pending"

@dataclass
class CacheEntry:
    """缓存条目"""
    entry_id: str
    original_query: str
    response: str
    user_role: UserRole
    timestamp: datetime
    ttl_seconds: int = 3600 * 24 * 7  # 默认7天
    access_count: int = 0
    last_access: Optional[datetime] = None
    priority: CachePriority = CachePriority.MEDIUM
    status: CacheStatus = CacheStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    cost_saved: float = 0.0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.status != CacheStatus.ACTIVE:
            return True
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    def is_compatible_with_user(self, user_role: UserRole) -> bool:
        """检查与用户角色的兼容性"""
        # 专家的缓存可以给所有人用
        if self.user_role == UserRole.EXPERT:
            return True
        
        # 研究者的缓存可以给专家和研究者用
        if self.user_role == UserRole.RESEARCHER:
            return user_role in [UserRole.EXPERT, UserRole.RESEARCHER]
        
        # 中级用户的缓存可以给中级和初学者用
        if self.user_role == UserRole.INTERMEDIATE:
            return user_role in [UserRole.INTERMEDIATE, UserRole.BEGINNER]
        
        # 初学者的缓存只能给初学者用
        return self.user_role == user_role
    
    def update_access(self):
        """更新访问信息"""
        self.access_count += 1
        self.last_access = datetime.now()

@dataclass
class CacheHitResult:
    """缓存命中结果"""
    hit: bool
    entry: Optional[CacheEntry] = None
    similarity_score: float = 0.0
    reason: str = ""
    cost_saved: float = 0.0

@dataclass
class CacheStats:
    """缓存统计信息"""
    total_entries: int = 0
    active_entries: int = 0
    expired_entries: int = 0
    hit_count: int = 0
    miss_count: int = 0
    total_cost_saved: float = 0.0
    average_similarity: float = 0.0
    cache_size_mb: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    @property
    def cost_efficiency(self) -> float:
        return self.total_cost_saved / max(self.total_entries, 1)

class SemanticCache:
    """语义缓存系统"""
    
    def __init__(
        self,
        vector_db_service: Optional[VectorDatabaseService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        similarity_threshold: float = 0.85,
        max_cache_size: int = 10000,
        cleanup_interval_hours: int = 24
    ):
        self.vector_db = vector_db_service or VectorDatabaseService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self.cleanup_interval_hours = cleanup_interval_hours
        
        # 缓存统计
        self.stats = CacheStats()
        self.cache_entries: Dict[str, CacheEntry] = {}
        
        # 角色兼容性矩阵
        self.role_compatibility = {
            UserRole.EXPERT: [UserRole.EXPERT, UserRole.RESEARCHER, UserRole.INTERMEDIATE, UserRole.BEGINNER],
            UserRole.RESEARCHER: [UserRole.EXPERT, UserRole.RESEARCHER],
            UserRole.INTERMEDIATE: [UserRole.INTERMEDIATE, UserRole.BEGINNER],
            UserRole.BEGINNER: [UserRole.BEGINNER]
        }
        
        logger.info(f"🎯 语义缓存系统初始化完成 - 相似度阈值: {similarity_threshold}")
    
    async def initialize(self):
        """初始化缓存系统"""
        try:
            # 初始化向量数据库
            await self.vector_db.initialize()
            
            # 初始化嵌入服务
            await self.embedding_service.initialize()
            
            # 创建缓存集合
            await self.vector_db.create_collection("semantic_cache")
            
            # 启动定期清理任务
            asyncio.create_task(self._periodic_cleanup())
            
            logger.info("✅ 语义缓存系统初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 语义缓存系统初始化失败: {e}")
            raise
    
    async def get_cached_response(
        self,
        query: str,
        user_role: UserRole,
        min_similarity: Optional[float] = None
    ) -> CacheHitResult:
        """获取缓存响应"""
        try:
            threshold = min_similarity or self.similarity_threshold
            
            # 生成查询嵌入
            query_embedding = await self.embedding_service.generate_embeddings([query])
            if not query_embedding:
                return CacheHitResult(hit=False, reason="嵌入生成失败")
            
            # 在向量数据库中搜索相似查询
            similar_results = await self.vector_db.similarity_search(
                collection_name="semantic_cache",
                query_embedding=query_embedding[0],
                top_k=10,
                threshold=threshold
            )
            
            if not similar_results:
                self.stats.miss_count += 1
                return CacheHitResult(hit=False, reason="未找到相似缓存")
            
            # 检查缓存条目的有效性和兼容性
            for result in similar_results:
                entry_id = result.get('metadata', {}).get('entry_id')
                if not entry_id or entry_id not in self.cache_entries:
                    continue
                
                entry = self.cache_entries[entry_id]
                
                # 检查缓存是否过期
                if entry.is_expired():
                    continue
                
                # 检查用户角色兼容性
                if not entry.is_compatible_with_user(user_role):
                    continue
                
                # 找到有效的缓存条目
                entry.update_access()
                self.stats.hit_count += 1
                self.stats.total_cost_saved += entry.cost_saved
                
                logger.info(f"🎯 缓存命中: {query[:50]}... -> 相似度: {result['similarity']:.3f}")
                
                return CacheHitResult(
                    hit=True,
                    entry=entry,
                    similarity_score=result['similarity'],
                    reason="缓存命中",
                    cost_saved=entry.cost_saved
                )
            
            self.stats.miss_count += 1
            return CacheHitResult(hit=False, reason="无兼容的有效缓存")
            
        except Exception as e:
            logger.error(f"❌ 获取缓存响应失败: {e}")
            self.stats.miss_count += 1
            return CacheHitResult(hit=False, reason=f"缓存查询错误: {e}")
    
    async def cache_response(
        self,
        query: str,
        response: str,
        user_role: UserRole,
        cost_saved: float = 0.0,
        quality_score: float = 0.0,
        priority: CachePriority = CachePriority.MEDIUM,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """缓存响应"""
        try:
            # 检查是否应该缓存
            should_cache, final_priority = await self._should_cache_response(
                query, response, cost_saved, quality_score, priority
            )
            
            if not should_cache:
                logger.debug(f"🚫 跳过缓存: {query[:50]}...")
                return False
            
            # 生成缓存条目ID
            entry_id = self._generate_entry_id(query, user_role)
            
            # 检查是否已存在
            if entry_id in self.cache_entries:
                logger.debug(f"🔄 更新已存在的缓存条目: {entry_id}")
                existing_entry = self.cache_entries[entry_id]
                existing_entry.response = response
                existing_entry.timestamp = datetime.now()
                existing_entry.quality_score = max(existing_entry.quality_score, quality_score)
                return True
            
            # 创建新的缓存条目
            cache_entry = CacheEntry(
                entry_id=entry_id,
                original_query=query,
                response=response,
                user_role=user_role,
                timestamp=datetime.now(),
                ttl_seconds=ttl_seconds or (3600 * 24 * 7),  # 默认7天
                priority=final_priority,
                quality_score=quality_score,
                cost_saved=cost_saved,
                metadata=metadata or {}
            )
            
            # 生成查询嵌入
            query_embedding = await self.embedding_service.generate_embeddings([query])
            if not query_embedding:
                logger.error("❌ 无法生成查询嵌入，缓存失败")
                return False
            
            # 存储到向量数据库
            doc_metadata = {
                'entry_id': entry_id,
                'user_role': user_role.value,
                'timestamp': cache_entry.timestamp.isoformat(),
                'priority': final_priority.value,
                'quality_score': quality_score,
                'cost_saved': cost_saved
            }
            
            success = await self.vector_db.add_document(
                collection_name="semantic_cache",
                document=query,
                embedding=query_embedding[0],
                metadata=doc_metadata,
                doc_id=entry_id
            )
            
            if success:
                # 存储到内存缓存
                self.cache_entries[entry_id] = cache_entry
                self.stats.total_entries += 1
                self.stats.active_entries += 1
                
                logger.info(f"✅ 缓存成功: {query[:50]}... (ID: {entry_id})")
                
                # 检查缓存大小限制
                await self._enforce_cache_size_limit()
                
                return True
            else:
                logger.error("❌ 向量数据库存储失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 缓存响应失败: {e}")
            return False
    
    async def invalidate_cache(
        self,
        query_pattern: Optional[str] = None,
        user_role: Optional[UserRole] = None,
        older_than_hours: Optional[int] = None
    ) -> int:
        """无效化缓存"""
        invalidated_count = 0
        
        try:
            entries_to_invalidate = []
            
            for entry_id, entry in self.cache_entries.items():
                should_invalidate = False
                
                # 按查询模式过滤
                if query_pattern and query_pattern.lower() in entry.original_query.lower():
                    should_invalidate = True
                
                # 按用户角色过滤
                if user_role and entry.user_role == user_role:
                    should_invalidate = True
                
                # 按时间过滤
                if older_than_hours:
                    cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
                    if entry.timestamp < cutoff_time:
                        should_invalidate = True
                
                if should_invalidate:
                    entries_to_invalidate.append(entry_id)
            
            # 执行无效化
            for entry_id in entries_to_invalidate:
                entry = self.cache_entries[entry_id]
                entry.status = CacheStatus.INVALIDATED
                
                # 从向量数据库中删除
                await self.vector_db.delete_document("semantic_cache", entry_id)
                
                # 从内存中删除
                del self.cache_entries[entry_id]
                
                invalidated_count += 1
                self.stats.active_entries -= 1
            
            logger.info(f"🗑️ 无效化了 {invalidated_count} 个缓存条目")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"❌ 无效化缓存失败: {e}")
            return 0
    
    async def get_cache_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        # 更新统计信息
        active_count = sum(1 for entry in self.cache_entries.values() 
                          if entry.status == CacheStatus.ACTIVE and not entry.is_expired())
        
        expired_count = sum(1 for entry in self.cache_entries.values() 
                           if entry.is_expired())
        
        total_cost_saved = sum(entry.cost_saved * entry.access_count 
                              for entry in self.cache_entries.values())
        
        # 估算缓存大小
        cache_size_mb = len(json.dumps([entry.__dict__ for entry in self.cache_entries.values()])) / (1024 * 1024)
        
        self.stats.active_entries = active_count
        self.stats.expired_entries = expired_count
        self.stats.total_cost_saved = total_cost_saved
        self.stats.cache_size_mb = cache_size_mb
        
        return self.stats
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """优化缓存"""
        optimization_result = {
            'cleaned_expired': 0,
            'promoted_entries': 0,
            'demoted_entries': 0,
            'recommendations': []
        }
        
        try:
            # 清理过期条目
            expired_count = await self._cleanup_expired_entries()
            optimization_result['cleaned_expired'] = expired_count
            
            # 调整缓存优先级
            promoted, demoted = await self._adjust_cache_priorities()
            optimization_result['promoted_entries'] = promoted
            optimization_result['demoted_entries'] = demoted
            
            # 生成优化建议
            recommendations = await self._generate_optimization_recommendations()
            optimization_result['recommendations'] = recommendations
            
            logger.info(f"🔧 缓存优化完成: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ 缓存优化失败: {e}")
            return optimization_result
    
    # 私有方法
    def _generate_entry_id(self, query: str, user_role: UserRole) -> str:
        """生成缓存条目ID"""
        content = f"{query}_{user_role.value}_{datetime.now().date().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def _should_cache_response(
        self,
        query: str,
        response: str,
        cost_saved: float,
        quality_score: float,
        priority: CachePriority
    ) -> Tuple[bool, CachePriority]:
        """判断是否应该缓存响应"""
        
        # 高成本响应必须缓存
        if cost_saved > 0.5:
            return True, CachePriority.HIGH
        
        # 高质量响应优先缓存
        if quality_score > 0.8:
            return True, max(priority, CachePriority.MEDIUM)
        
        # 长响应（可能包含丰富信息）优先缓存
        if len(response) > 500:
            return True, priority
        
        # 常见查询模式
        common_patterns = ['什么是', '如何', '为什么', '怎么样', '区别', '优缺点']
        if any(pattern in query for pattern in common_patterns):
            return True, CachePriority.MEDIUM
        
        # 默认缓存，但优先级较低
        return True, CachePriority.LOW
    
    async def _enforce_cache_size_limit(self):
        """强制执行缓存大小限制"""
        if len(self.cache_entries) <= self.max_cache_size:
            return
        
        # 计算需要删除的条目数
        entries_to_remove = len(self.cache_entries) - self.max_cache_size
        
        # 按优先级和访问频率排序
        entries_sorted = sorted(
            self.cache_entries.items(),
            key=lambda x: (
                x[1].priority.value,  # 优先级
                x[1].access_count,    # 访问次数
                x[1].timestamp        # 时间戳
            )
        )
        
        # 删除优先级最低的条目
        for i in range(entries_to_remove):
            entry_id, entry = entries_sorted[i]
            
            # 从向量数据库删除
            await self.vector_db.delete_document("semantic_cache", entry_id)
            
            # 从内存删除
            del self.cache_entries[entry_id]
            self.stats.active_entries -= 1
        
        logger.info(f"🗑️ 清理了 {entries_to_remove} 个低优先级缓存条目")
    
    async def _cleanup_expired_entries(self) -> int:
        """清理过期条目"""
        expired_entries = []
        
        for entry_id, entry in self.cache_entries.items():
            if entry.is_expired():
                expired_entries.append(entry_id)
        
        for entry_id in expired_entries:
            # 从向量数据库删除
            await self.vector_db.delete_document("semantic_cache", entry_id)
            
            # 从内存删除
            del self.cache_entries[entry_id]
            self.stats.active_entries -= 1
            self.stats.expired_entries += 1
        
        return len(expired_entries)
    
    async def _adjust_cache_priorities(self) -> Tuple[int, int]:
        """调整缓存优先级"""
        promoted = demoted = 0
        
        for entry in self.cache_entries.values():
            old_priority = entry.priority
            
            # 高访问频率 -> 提升优先级
            if entry.access_count > 10 and entry.priority == CachePriority.LOW:
                entry.priority = CachePriority.MEDIUM
                promoted += 1
            elif entry.access_count > 50 and entry.priority == CachePriority.MEDIUM:
                entry.priority = CachePriority.HIGH
                promoted += 1
            
            # 低访问频率 -> 降低优先级
            elif entry.access_count < 2 and entry.priority == CachePriority.HIGH:
                entry.priority = CachePriority.MEDIUM
                demoted += 1
            elif entry.access_count < 1 and entry.priority == CachePriority.MEDIUM:
                entry.priority = CachePriority.LOW
                demoted += 1
        
        return promoted, demoted
    
    async def _generate_optimization_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 分析命中率
        if self.stats.hit_rate < 0.3:
            recommendations.append("命中率较低，建议降低相似度阈值或增加缓存时间")
        
        # 分析缓存大小
        if self.stats.cache_size_mb > 100:
            recommendations.append("缓存占用空间较大，建议清理低价值缓存或压缩响应内容")
        
        # 分析成本效益
        if self.stats.cost_efficiency < 0.1:
            recommendations.append("缓存成本效益较低，建议优化缓存策略")
        
        return recommendations
    
    async def _periodic_cleanup(self):
        """定期清理任务"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
                
                logger.info("🧹 开始定期缓存清理")
                
                # 清理过期条目
                expired_count = await self._cleanup_expired_entries()
                
                # 优化缓存
                await self.optimize_cache()
                
                logger.info(f"🧹 定期清理完成，清理了 {expired_count} 个过期条目")
                
            except Exception as e:
                logger.error(f"❌ 定期清理任务失败: {e}")
                await asyncio.sleep(3600)  # 出错后1小时后重试

# 工厂函数
def create_semantic_cache(
    similarity_threshold: float = 0.85,
    max_cache_size: int = 10000
) -> SemanticCache:
    """创建语义缓存实例"""
    return SemanticCache(
        similarity_threshold=similarity_threshold,
        max_cache_size=max_cache_size
    ) 