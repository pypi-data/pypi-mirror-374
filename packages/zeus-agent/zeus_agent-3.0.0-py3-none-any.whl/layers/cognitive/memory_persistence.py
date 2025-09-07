"""
Memory Persistence Module - 记忆持久化模块
实现完整的数据库持久化功能，支持所有记忆类型的存储和检索

提供功能：
- SQLite数据库存储
- 优化的查询和索引
- 批量操作支持
- 数据迁移和备份
- 性能监控和优化
- 事务管理
- 数据完整性保证
"""

import asyncio
import sqlite3
import aiosqlite
import json
import pickle
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
import numpy as np
from contextlib import asynccontextmanager
import os

from .memory import (
    MemoryItem, MemoryType, EpisodicMemory, SemanticMemory, ProceduralMemory,
    MemoryImportance
)

logger = logging.getLogger(__name__)


class PersistenceMode(Enum):
    """持久化模式"""
    IMMEDIATE = "immediate"    # 立即持久化
    BATCH = "batch"           # 批量持久化
    PERIODIC = "periodic"     # 定期持久化
    LAZY = "lazy"            # 懒惰持久化（仅在关闭时）


class StorageBackend(Enum):
    """存储后端"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MEMORY = "memory"


@dataclass
class PersistenceConfig:
    """持久化配置"""
    storage_backend: StorageBackend = StorageBackend.SQLITE
    database_path: str = "memory_database.db"
    persistence_mode: PersistenceMode = PersistenceMode.BATCH
    batch_size: int = 100
    batch_timeout: float = 30.0  # 秒
    max_connections: int = 10
    enable_wal: bool = True      # Write-Ahead Logging
    enable_foreign_keys: bool = True
    vacuum_interval: int = 3600  # 秒
    backup_interval: int = 86400 # 秒
    retention_days: int = 365    # 数据保留天数
    enable_compression: bool = True
    enable_encryption: bool = False
    encryption_key: Optional[str] = None


class MemoryDatabaseSchema:
    """记忆数据库模式定义"""
    
    # 主要表结构
    TABLES = {
        'memory_items': '''
            CREATE TABLE IF NOT EXISTS memory_items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                tags TEXT,  -- JSON array
                metadata TEXT,  -- JSON object
                embedding BLOB,  -- Serialized numpy array
                embedding_model TEXT,
                semantic_keywords TEXT,  -- JSON array
                is_deleted BOOLEAN DEFAULT FALSE,
                version INTEGER DEFAULT 1
            )
        ''',
        
        'episodic_memories': '''
            CREATE TABLE IF NOT EXISTS episodic_memories (
                id TEXT PRIMARY KEY,
                episode_id TEXT UNIQUE NOT NULL,
                event TEXT NOT NULL,
                context TEXT NOT NULL,  -- JSON object
                participants TEXT NOT NULL,  -- JSON array
                location TEXT,
                timestamp TIMESTAMP NOT NULL,
                emotional_valence REAL DEFAULT 0.0,
                importance REAL DEFAULT 0.5,
                related_episodes TEXT,  -- JSON array
                metadata TEXT,  -- JSON object
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE
            )
        ''',
        
        'semantic_memories': '''
            CREATE TABLE IF NOT EXISTS semantic_memories (
                id TEXT PRIMARY KEY,
                concept_id TEXT UNIQUE NOT NULL,
                concept TEXT NOT NULL,
                definition TEXT NOT NULL,
                properties TEXT,  -- JSON object
                relationships TEXT,  -- JSON object
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                metadata TEXT,  -- JSON object
                is_deleted BOOLEAN DEFAULT FALSE
            )
        ''',
        
        'procedural_memories': '''
            CREATE TABLE IF NOT EXISTS procedural_memories (
                id TEXT PRIMARY KEY,
                procedure_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                steps TEXT NOT NULL,  -- JSON array
                preconditions TEXT,  -- JSON array
                postconditions TEXT,  -- JSON array
                success_rate REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                metadata TEXT,  -- JSON object
                is_deleted BOOLEAN DEFAULT FALSE
            )
        ''',
        
        'memory_relationships': '''
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                direction TEXT DEFAULT 'bidirectional',  -- unidirectional, bidirectional
                metadata TEXT,  -- JSON object
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES memory_items (id),
                FOREIGN KEY (target_id) REFERENCES memory_items (id)
            )
        ''',
        
        'memory_snapshots': '''
            CREATE TABLE IF NOT EXISTS memory_snapshots (
                id TEXT PRIMARY KEY,
                name TEXT,
                snapshot_data TEXT NOT NULL,  -- JSON object
                compression_type TEXT DEFAULT 'none',
                size_bytes INTEGER,
                checksum TEXT,
                created_at TIMESTAMP NOT NULL,
                metadata TEXT  -- JSON object
            )
        ''',
        
        'memory_statistics': '''
            CREATE TABLE IF NOT EXISTS memory_statistics (
                id TEXT PRIMARY KEY,
                stat_type TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                metadata TEXT  -- JSON object
            )
        ''',
        
        'memory_operations_log': '''
            CREATE TABLE IF NOT EXISTS memory_operations_log (
                id TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,  -- INSERT, UPDATE, DELETE, QUERY
                table_name TEXT NOT NULL,
                record_id TEXT,
                operation_data TEXT,  -- JSON object
                execution_time REAL,  -- milliseconds
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp TIMESTAMP NOT NULL
            )
        '''
    }
    
    # 索引定义
    INDEXES = [
        'CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items (memory_type)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_importance ON memory_items (importance DESC)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_created_at ON memory_items (created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_last_accessed ON memory_items (last_accessed DESC)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_content_hash ON memory_items (content_hash)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_tags ON memory_items (tags)',
        'CREATE INDEX IF NOT EXISTS idx_memory_items_deleted ON memory_items (is_deleted)',
        
        'CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memories (timestamp DESC)',
        'CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memories (importance DESC)',
        'CREATE INDEX IF NOT EXISTS idx_episodic_participants ON episodic_memories (participants)',
        'CREATE INDEX IF NOT EXISTS idx_episodic_deleted ON episodic_memories (is_deleted)',
        
        'CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memories (concept)',
        'CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_memories (confidence DESC)',
        'CREATE INDEX IF NOT EXISTS idx_semantic_deleted ON semantic_memories (is_deleted)',
        
        'CREATE INDEX IF NOT EXISTS idx_procedural_name ON procedural_memories (name)',
        'CREATE INDEX IF NOT EXISTS idx_procedural_success_rate ON procedural_memories (success_rate DESC)',
        'CREATE INDEX IF NOT EXISTS idx_procedural_usage_count ON procedural_memories (usage_count DESC)',
        'CREATE INDEX IF NOT EXISTS idx_procedural_deleted ON procedural_memories (is_deleted)',
        
        'CREATE INDEX IF NOT EXISTS idx_relationships_source ON memory_relationships (source_id)',
        'CREATE INDEX IF NOT EXISTS idx_relationships_target ON memory_relationships (target_id)',
        'CREATE INDEX IF NOT EXISTS idx_relationships_type ON memory_relationships (relationship_type)',
        'CREATE INDEX IF NOT EXISTS idx_relationships_strength ON memory_relationships (strength DESC)',
        
        'CREATE INDEX IF NOT EXISTS idx_snapshots_created_at ON memory_snapshots (created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_statistics_type_name ON memory_statistics (stat_type, stat_name)',
        'CREATE INDEX IF NOT EXISTS idx_statistics_timestamp ON memory_statistics (timestamp DESC)',
        'CREATE INDEX IF NOT EXISTS idx_operations_log_timestamp ON memory_operations_log (timestamp DESC)',
        'CREATE INDEX IF NOT EXISTS idx_operations_log_operation_type ON memory_operations_log (operation_type)'
    ]


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: PersistenceConfig):
        self.config = config
        self.db_path = Path(config.database_path)
        self.connection_pool = []
        self.max_connections = config.max_connections
        self.active_connections = 0
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # 确保数据库目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """初始化数据库"""
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                # 启用WAL模式
                if self.config.enable_wal:
                    await db.execute('PRAGMA journal_mode=WAL')
                
                # 启用外键约束
                if self.config.enable_foreign_keys:
                    await db.execute('PRAGMA foreign_keys=ON')
                
                # 设置其他优化参数
                await db.execute('PRAGMA synchronous=NORMAL')
                await db.execute('PRAGMA cache_size=10000')
                await db.execute('PRAGMA temp_store=MEMORY')
                
                # 创建表
                for table_name, table_sql in MemoryDatabaseSchema.TABLES.items():
                    await db.execute(table_sql)
                    self.logger.debug(f"Created/verified table: {table_name}")
                
                # 创建索引
                for index_sql in MemoryDatabaseSchema.INDEXES:
                    await db.execute(index_sql)
                
                await db.commit()
                self.logger.info("Database initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接（连接池）"""
        async with self.lock:
            if self.connection_pool:
                connection = self.connection_pool.pop()
            else:
                if self.active_connections >= self.max_connections:
                    # 等待连接可用
                    while self.active_connections >= self.max_connections:
                        await asyncio.sleep(0.01)
                
                connection = await aiosqlite.connect(str(self.db_path))
                await connection.execute('PRAGMA foreign_keys=ON')
                self.active_connections += 1
        
        try:
            yield connection
        finally:
            async with self.lock:
                if len(self.connection_pool) < self.max_connections // 2:
                    self.connection_pool.append(connection)
                else:
                    await connection.close()
                    self.active_connections -= 1
    
    async def execute_query(self, query: str, params: Optional[Tuple] = None,
                          fetch_one: bool = False, fetch_all: bool = False) -> Any:
        """执行查询"""
        start_time = datetime.now()
        
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(query, params or ())
                
                if fetch_one:
                    result = await cursor.fetchone()
                elif fetch_all:
                    result = await cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                await db.commit()
                
                # 记录操作日志
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                await self._log_operation(
                    operation_type="QUERY",
                    table_name="unknown",
                    execution_time=execution_time,
                    success=True
                )
                
                return result
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._log_operation(
                operation_type="QUERY",
                table_name="unknown",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_batch(self, queries: List[Tuple[str, Tuple]]) -> List[Any]:
        """批量执行查询"""
        start_time = datetime.now()
        results = []
        
        try:
            async with self.get_connection() as db:
                for query, params in queries:
                    cursor = await db.execute(query, params)
                    results.append(cursor.rowcount)
                
                await db.commit()
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                await self._log_operation(
                    operation_type="BATCH",
                    table_name="multiple",
                    execution_time=execution_time,
                    success=True,
                    operation_data={"batch_size": len(queries)}
                )
                
                return results
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._log_operation(
                operation_type="BATCH",
                table_name="multiple",
                execution_time=execution_time,
                success=False,
                error_message=str(e),
                operation_data={"batch_size": len(queries)}
            )
            self.logger.error(f"Batch execution failed: {e}")
            raise
    
    async def _log_operation(self, operation_type: str, table_name: str,
                           execution_time: float, success: bool,
                           record_id: str = None, operation_data: Dict = None,
                           error_message: str = None) -> None:
        """记录操作日志"""
        try:
            log_id = str(uuid.uuid4())
            query = '''
                INSERT INTO memory_operations_log 
                (id, operation_type, table_name, record_id, operation_data, 
                 execution_time, success, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                log_id, operation_type, table_name, record_id,
                json.dumps(operation_data) if operation_data else None,
                execution_time, success, error_message, datetime.now()
            )
            
            async with self.get_connection() as db:
                await db.execute(query, params)
                await db.commit()
        
        except Exception as e:
            # 记录日志失败不应该影响主要操作
            self.logger.warning(f"Failed to log operation: {e}")
    
    async def vacuum_database(self) -> None:
        """清理数据库"""
        try:
            async with self.get_connection() as db:
                await db.execute('VACUUM')
                self.logger.info("Database vacuum completed")
        except Exception as e:
            self.logger.error(f"Database vacuum failed: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        try:
            # 获取表大小信息
            for table_name in MemoryDatabaseSchema.TABLES.keys():
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count = await self.execute_query(count_query, fetch_one=True)
                stats[f"{table_name}_count"] = count[0] if count else 0
            
            # 获取数据库文件大小
            if self.db_path.exists():
                stats["database_size_bytes"] = self.db_path.stat().st_size
            
            # 获取最近的操作统计
            recent_ops_query = '''
                SELECT operation_type, COUNT(*), AVG(execution_time)
                FROM memory_operations_log 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY operation_type
            '''
            recent_ops = await self.execute_query(recent_ops_query, fetch_all=True)
            stats["recent_operations"] = {
                op_type: {"count": count, "avg_time": avg_time}
                for op_type, count, avg_time in recent_ops
            }
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}


class MemoryPersistenceManager:
    """记忆持久化管理器"""
    
    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self.db_manager = DatabaseManager(self.config)
        self.pending_operations = []
        self.last_batch_time = datetime.now()
        self.batch_task = None
        self.is_running = False
        
        # 压缩和加密支持
        self.compression_enabled = self.config.enable_compression
        self.encryption_enabled = self.config.enable_encryption
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def initialize(self) -> None:
        """初始化持久化管理器"""
        await self.db_manager.initialize()
        
        if self.config.persistence_mode == PersistenceMode.BATCH:
            self.is_running = True
            self.batch_task = asyncio.create_task(self._batch_processing_loop())
        
        self.logger.info("Memory persistence manager initialized")
    
    async def shutdown(self) -> None:
        """关闭持久化管理器"""
        self.is_running = False
        
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
        
        # 处理剩余的待处理操作
        if self.pending_operations:
            await self._flush_batch()
        
        self.logger.info("Memory persistence manager shut down")
    
    async def store_memory_item(self, memory_item: MemoryItem) -> str:
        """存储记忆项"""
        operation = {
            "type": "store_memory_item",
            "data": memory_item,
            "timestamp": datetime.now()
        }
        
        if self.config.persistence_mode == PersistenceMode.IMMEDIATE:
            return await self._execute_store_memory_item(memory_item)
        else:
            self.pending_operations.append(operation)
            return memory_item.item_id
    
    async def _execute_store_memory_item(self, memory_item: MemoryItem) -> str:
        """执行存储记忆项"""
        try:
            # 序列化复杂数据
            tags_json = json.dumps(memory_item.tags) if memory_item.tags else None
            metadata_json = json.dumps(memory_item.metadata) if memory_item.metadata else None
            embedding_blob = pickle.dumps(memory_item.embedding) if memory_item.embedding is not None else None
            keywords_json = json.dumps(memory_item.semantic_keywords) if memory_item.semantic_keywords else None
            
            # 计算内容哈希
            content_str = str(memory_item.content)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            query = '''
                INSERT OR REPLACE INTO memory_items 
                (id, content, content_hash, memory_type, importance, access_count, 
                 last_accessed, created_at, updated_at, tags, metadata, embedding, 
                 embedding_model, semantic_keywords, is_deleted, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                memory_item.item_id,
                content_str,
                content_hash,
                memory_item.memory_type.value,
                memory_item.importance,
                memory_item.access_count,
                memory_item.last_accessed,
                memory_item.created_at,
                datetime.now(),  # updated_at
                tags_json,
                metadata_json,
                embedding_blob,
                memory_item.embedding_model,
                keywords_json,
                False,  # is_deleted
                1       # version
            )
            
            await self.db_manager.execute_query(query, params)
            
            self.logger.debug(f"Stored memory item: {memory_item.item_id}")
            return memory_item.item_id
        
        except Exception as e:
            self.logger.error(f"Failed to store memory item {memory_item.item_id}: {e}")
            raise
    
    async def retrieve_memory_item(self, item_id: str) -> Optional[MemoryItem]:
        """检索记忆项"""
        try:
            query = '''
                SELECT id, content, memory_type, importance, access_count, 
                       last_accessed, created_at, tags, metadata, embedding,
                       embedding_model, semantic_keywords
                FROM memory_items 
                WHERE id = ? AND is_deleted = FALSE
            '''
            
            row = await self.db_manager.execute_query(query, (item_id,), fetch_one=True)
            
            if not row:
                return None
            
            # 反序列化数据
            tags = json.loads(row[7]) if row[7] else []
            metadata = json.loads(row[8]) if row[8] else {}
            embedding = pickle.loads(row[9]) if row[9] else None
            semantic_keywords = json.loads(row[11]) if row[11] else []
            
            # 更新访问计数
            await self._update_access_count(item_id)
            
            memory_item = MemoryItem(
                item_id=row[0],
                content=row[1],
                memory_type=MemoryType(row[2]),
                importance=row[3],
                access_count=row[4] + 1,  # 增加访问计数
                last_accessed=datetime.now(),
                created_at=row[6],
                tags=tags,
                metadata=metadata,
                embedding=embedding,
                embedding_model=row[10],
                semantic_keywords=semantic_keywords
            )
            
            return memory_item
        
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory item {item_id}: {e}")
            return None
    
    async def _update_access_count(self, item_id: str) -> None:
        """更新访问计数"""
        try:
            query = '''
                UPDATE memory_items 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            '''
            await self.db_manager.execute_query(query, (datetime.now(), item_id))
        except Exception as e:
            self.logger.warning(f"Failed to update access count for {item_id}: {e}")
    
    async def search_memory_items(self, 
                                 memory_types: Optional[List[MemoryType]] = None,
                                 tags: Optional[List[str]] = None,
                                 min_importance: float = 0.0,
                                 max_results: int = 100,
                                 order_by: str = "importance DESC") -> List[MemoryItem]:
        """搜索记忆项"""
        try:
            # 构建查询条件
            conditions = ["is_deleted = FALSE"]
            params = []
            
            if memory_types:
                type_placeholders = ",".join("?" * len(memory_types))
                conditions.append(f"memory_type IN ({type_placeholders})")
                params.extend([mt.value for mt in memory_types])
            
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
            
            if min_importance > 0:
                conditions.append("importance >= ?")
                params.append(min_importance)
            
            where_clause = " AND ".join(conditions)
            
            query = f'''
                SELECT id, content, memory_type, importance, access_count, 
                       last_accessed, created_at, tags, metadata, embedding,
                       embedding_model, semantic_keywords
                FROM memory_items 
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT ?
            '''
            params.append(max_results)
            
            rows = await self.db_manager.execute_query(query, tuple(params), fetch_all=True)
            
            memory_items = []
            for row in rows:
                tags = json.loads(row[7]) if row[7] else []
                metadata = json.loads(row[8]) if row[8] else {}
                embedding = pickle.loads(row[9]) if row[9] else None
                semantic_keywords = json.loads(row[11]) if row[11] else []
                
                memory_item = MemoryItem(
                    item_id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    importance=row[3],
                    access_count=row[4],
                    last_accessed=row[5],
                    created_at=row[6],
                    tags=tags,
                    metadata=metadata,
                    embedding=embedding,
                    embedding_model=row[10],
                    semantic_keywords=semantic_keywords
                )
                memory_items.append(memory_item)
            
            return memory_items
        
        except Exception as e:
            self.logger.error(f"Failed to search memory items: {e}")
            return []
    
    async def store_episodic_memory(self, episodic_memory: EpisodicMemory) -> str:
        """存储情景记忆"""
        try:
            query = '''
                INSERT OR REPLACE INTO episodic_memories 
                (id, episode_id, event, context, participants, location, timestamp,
                 emotional_valence, importance, related_episodes, metadata, 
                 created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            record_id = str(uuid.uuid4())
            params = (
                record_id,
                episodic_memory.episode_id,
                episodic_memory.event,
                json.dumps(episodic_memory.context),
                json.dumps(episodic_memory.participants),
                episodic_memory.location,
                episodic_memory.timestamp,
                episodic_memory.emotional_valence,
                episodic_memory.importance,
                json.dumps(episodic_memory.related_episodes),
                json.dumps(episodic_memory.metadata),
                datetime.now(),
                datetime.now(),
                False
            )
            
            await self.db_manager.execute_query(query, params)
            return record_id
        
        except Exception as e:
            self.logger.error(f"Failed to store episodic memory: {e}")
            raise
    
    async def store_semantic_memory(self, semantic_memory: SemanticMemory) -> str:
        """存储语义记忆"""
        try:
            query = '''
                INSERT OR REPLACE INTO semantic_memories 
                (id, concept_id, concept, definition, properties, relationships,
                 confidence, source, created_at, updated_at, metadata, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            record_id = str(uuid.uuid4())
            params = (
                record_id,
                semantic_memory.concept_id,
                semantic_memory.concept,
                semantic_memory.definition,
                json.dumps(semantic_memory.properties),
                json.dumps(semantic_memory.relationships),
                semantic_memory.confidence,
                semantic_memory.source,
                semantic_memory.created_at,
                datetime.now(),
                json.dumps(semantic_memory.metadata),
                False
            )
            
            await self.db_manager.execute_query(query, params)
            return record_id
        
        except Exception as e:
            self.logger.error(f"Failed to store semantic memory: {e}")
            raise
    
    async def store_procedural_memory(self, procedural_memory: ProceduralMemory) -> str:
        """存储程序记忆"""
        try:
            query = '''
                INSERT OR REPLACE INTO procedural_memories 
                (id, procedure_id, name, description, steps, preconditions,
                 postconditions, success_rate, usage_count, last_used,
                 created_at, updated_at, metadata, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            record_id = str(uuid.uuid4())
            params = (
                record_id,
                procedural_memory.procedure_id,
                procedural_memory.name,
                procedural_memory.description,
                json.dumps(procedural_memory.steps),
                json.dumps(procedural_memory.preconditions),
                json.dumps(procedural_memory.postconditions),
                procedural_memory.success_rate,
                procedural_memory.usage_count,
                procedural_memory.last_used,
                procedural_memory.created_at,
                datetime.now(),
                json.dumps(procedural_memory.metadata),
                False
            )
            
            await self.db_manager.execute_query(query, params)
            return record_id
        
        except Exception as e:
            self.logger.error(f"Failed to store procedural memory: {e}")
            raise
    
    async def create_memory_snapshot(self, name: str, data: Dict[str, Any]) -> str:
        """创建记忆快照"""
        try:
            snapshot_id = str(uuid.uuid4())
            
            # 序列化和可选压缩
            data_json = json.dumps(data, default=str)
            compressed_data = data_json
            compression_type = "none"
            
            if self.compression_enabled:
                import gzip
                compressed_data = gzip.compress(data_json.encode()).decode('latin-1')
                compression_type = "gzip"
            
            # 计算校验和
            checksum = hashlib.md5(compressed_data.encode()).hexdigest()
            
            query = '''
                INSERT INTO memory_snapshots 
                (id, name, snapshot_data, compression_type, size_bytes, checksum, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                snapshot_id,
                name,
                compressed_data,
                compression_type,
                len(compressed_data),
                checksum,
                datetime.now(),
                json.dumps({"original_size": len(data_json)})
            )
            
            await self.db_manager.execute_query(query, params)
            
            self.logger.info(f"Created memory snapshot: {snapshot_id}")
            return snapshot_id
        
        except Exception as e:
            self.logger.error(f"Failed to create memory snapshot: {e}")
            raise
    
    async def restore_memory_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """恢复记忆快照"""
        try:
            query = '''
                SELECT snapshot_data, compression_type, checksum
                FROM memory_snapshots 
                WHERE id = ?
            '''
            
            row = await self.db_manager.execute_query(query, (snapshot_id,), fetch_one=True)
            
            if not row:
                return None
            
            snapshot_data, compression_type, stored_checksum = row
            
            # 验证校验和
            actual_checksum = hashlib.md5(snapshot_data.encode()).hexdigest()
            if actual_checksum != stored_checksum:
                raise ValueError(f"Snapshot {snapshot_id} checksum mismatch")
            
            # 解压缩
            if compression_type == "gzip":
                import gzip
                decompressed_data = gzip.decompress(snapshot_data.encode('latin-1')).decode()
            else:
                decompressed_data = snapshot_data
            
            return json.loads(decompressed_data)
        
        except Exception as e:
            self.logger.error(f"Failed to restore memory snapshot {snapshot_id}: {e}")
            return None
    
    async def _batch_processing_loop(self) -> None:
        """批量处理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(1.0)  # 检查间隔
                
                current_time = datetime.now()
                time_since_last_batch = (current_time - self.last_batch_time).total_seconds()
                
                should_process = (
                    len(self.pending_operations) >= self.config.batch_size or
                    time_since_last_batch >= self.config.batch_timeout
                )
                
                if should_process and self.pending_operations:
                    await self._flush_batch()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in batch processing loop: {e}")
    
    async def _flush_batch(self) -> None:
        """刷新批处理队列"""
        if not self.pending_operations:
            return
        
        try:
            batch_queries = []
            
            for operation in self.pending_operations:
                if operation["type"] == "store_memory_item":
                    memory_item = operation["data"]
                    
                    # 构建查询和参数
                    tags_json = json.dumps(memory_item.tags) if memory_item.tags else None
                    metadata_json = json.dumps(memory_item.metadata) if memory_item.metadata else None
                    embedding_blob = pickle.dumps(memory_item.embedding) if memory_item.embedding is not None else None
                    keywords_json = json.dumps(memory_item.semantic_keywords) if memory_item.semantic_keywords else None
                    content_str = str(memory_item.content)
                    content_hash = hashlib.sha256(content_str.encode()).hexdigest()
                    
                    query = '''
                        INSERT OR REPLACE INTO memory_items 
                        (id, content, content_hash, memory_type, importance, access_count, 
                         last_accessed, created_at, updated_at, tags, metadata, embedding, 
                         embedding_model, semantic_keywords, is_deleted, version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    
                    params = (
                        memory_item.item_id, content_str, content_hash,
                        memory_item.memory_type.value, memory_item.importance,
                        memory_item.access_count, memory_item.last_accessed,
                        memory_item.created_at, datetime.now(), tags_json,
                        metadata_json, embedding_blob, memory_item.embedding_model,
                        keywords_json, False, 1
                    )
                    
                    batch_queries.append((query, params))
            
            if batch_queries:
                await self.db_manager.execute_batch(batch_queries)
                self.logger.info(f"Flushed batch of {len(batch_queries)} operations")
            
            self.pending_operations.clear()
            self.last_batch_time = datetime.now()
        
        except Exception as e:
            self.logger.error(f"Failed to flush batch: {e}")
    
    async def cleanup_old_data(self, retention_days: int = None) -> Dict[str, int]:
        """清理旧数据"""
        retention_days = retention_days or self.config.retention_days
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleanup_results = {}
        
        try:
            # 清理旧的操作日志
            log_query = "DELETE FROM memory_operations_log WHERE timestamp < ?"
            log_count = await self.db_manager.execute_query(log_query, (cutoff_date,))
            cleanup_results["operations_log_deleted"] = log_count
            
            # 清理旧的统计数据
            stats_query = "DELETE FROM memory_statistics WHERE timestamp < ?"
            stats_count = await self.db_manager.execute_query(stats_query, (cutoff_date,))
            cleanup_results["statistics_deleted"] = stats_count
            
            # 软删除旧的低重要性记忆项
            memory_query = '''
                UPDATE memory_items 
                SET is_deleted = TRUE 
                WHERE created_at < ? AND importance < 0.3 AND access_count < 2
            '''
            memory_count = await self.db_manager.execute_query(memory_query, (cutoff_date,))
            cleanup_results["memory_items_archived"] = memory_count
            
            self.logger.info(f"Cleanup completed: {cleanup_results}")
            return cleanup_results
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return {}
    
    async def get_persistence_statistics(self) -> Dict[str, Any]:
        """获取持久化统计信息"""
        try:
            db_stats = await self.db_manager.get_database_stats()
            
            return {
                "database_stats": db_stats,
                "pending_operations": len(self.pending_operations),
                "persistence_mode": self.config.persistence_mode.value,
                "batch_size": self.config.batch_size,
                "last_batch_time": self.last_batch_time.isoformat(),
                "config": asdict(self.config)
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get persistence statistics: {e}")
            return {} 