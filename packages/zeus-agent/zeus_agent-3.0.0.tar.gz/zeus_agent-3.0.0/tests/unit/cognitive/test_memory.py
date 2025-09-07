"""
Unit tests for memory module
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List

from layers.cognitive.memory import (
    MemorySystem,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    MemoryConsolidator,
    MemoryRetriever,
    ForgettingMechanism,
    MemoryType,
    MemoryImportance,
    MemoryItem
)


class TestMemoryType:
    """Test MemoryType enum"""
    
    def test_memory_type_values(self):
        """Test all memory type values"""
        assert MemoryType.WORKING.value == "working"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.PROCEDURAL.value == "procedural"
    
    def test_memory_type_count(self):
        """Test that we have all expected memory types"""
        types = list(MemoryType)
        assert len(types) == 4


class TestMemoryImportance:
    """Test MemoryImportance enum"""
    
    def test_importance_values(self):
        """Test all importance level values"""
        assert MemoryImportance.CRITICAL.value == 1.0
        assert MemoryImportance.HIGH.value == 0.8
        assert MemoryImportance.MEDIUM.value == 0.6
        assert MemoryImportance.LOW.value == 0.4
        assert MemoryImportance.MINIMAL.value == 0.2
    
    def test_importance_count(self):
        """Test that we have all expected importance levels"""
        levels = list(MemoryImportance)
        assert len(levels) == 5


class TestMemoryItem:
    """Test MemoryItem dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of MemoryItem"""
        item = MemoryItem(
            item_id="test_001",
            content="Test memory content",
            memory_type=MemoryType.WORKING,
            importance=0.7
        )
        
        assert item.item_id == "test_001"
        assert item.content == "Test memory content"
        assert item.memory_type == MemoryType.WORKING
        assert item.importance == 0.7
        assert item.access_count == 0
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.last_accessed, datetime)
        assert item.tags == []
        assert item.metadata == {}
    
    def test_full_initialization(self):
        """Test full initialization with all parameters"""
        created = datetime(2024, 1, 1, 12, 0, 0)
        accessed = datetime(2024, 1, 2, 12, 0, 0)
        tags = ["important", "conversation"]
        metadata = {"source": "user_input", "confidence": 0.9}
        
        item = MemoryItem(
            item_id="test_002",
            content={"type": "conversation", "text": "Hello world"},
            memory_type=MemoryType.EPISODIC,
            importance=0.9,
            access_count=5,
            last_accessed=accessed,
            created_at=created,
            tags=tags,
            metadata=metadata
        )
        
        assert item.item_id == "test_002"
        assert item.content == {"type": "conversation", "text": "Hello world"}
        assert item.memory_type == MemoryType.EPISODIC
        assert item.importance == 0.9
        assert item.access_count == 5
        assert item.last_accessed == accessed
        assert item.created_at == created
        assert item.tags == tags
        assert item.metadata == metadata
    
    def test_post_init_sets_last_accessed(self):
        """Test that __post_init__ sets last_accessed if None"""
        item = MemoryItem(
            item_id="test_003",
            content="Test",
            memory_type=MemoryType.SEMANTIC,
            importance=0.5
        )
        
        # last_accessed should be set to created_at
        assert item.last_accessed == item.created_at


class TestEpisodicMemory:
    """Test EpisodicMemory dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of EpisodicMemory"""
        episode = EpisodicMemory(
            episode_id="ep_001",
            event="User asked about weather",
            context={"location": "office", "time": "morning"},
            participants=["user", "assistant"]
        )
        
        assert episode.episode_id == "ep_001"
        assert episode.event == "User asked about weather"
        assert episode.context == {"location": "office", "time": "morning"}
        assert episode.participants == ["user", "assistant"]
        assert episode.location is None
        assert isinstance(episode.timestamp, datetime)
        assert episode.emotional_valence == 0.0
        assert episode.importance == 0.5
        assert episode.related_episodes == []
        assert episode.metadata == {}
    
    def test_full_initialization(self):
        """Test full initialization with all parameters"""
        timestamp = datetime(2024, 1, 1, 14, 30, 0)
        
        episode = EpisodicMemory(
            episode_id="ep_002",
            event="Successful task completion",
            context={"task": "data_analysis", "duration": "2_hours"},
            participants=["user", "assistant", "system"],
            location="virtual_workspace",
            timestamp=timestamp,
            emotional_valence=0.8,
            importance=0.9,
            related_episodes=["ep_001"],
            metadata={"outcome": "success", "satisfaction": "high"}
        )
        
        assert episode.episode_id == "ep_002"
        assert episode.event == "Successful task completion"
        assert episode.location == "virtual_workspace"
        assert episode.timestamp == timestamp
        assert episode.emotional_valence == 0.8
        assert episode.importance == 0.9
        assert episode.related_episodes == ["ep_001"]
        assert episode.metadata == {"outcome": "success", "satisfaction": "high"}


class TestSemanticMemory:
    """Test SemanticMemory dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of SemanticMemory"""
        semantic = SemanticMemory(
            concept_id="concept_001",
            concept="Python",
            definition="A high-level programming language"
        )
        
        assert semantic.concept_id == "concept_001"
        assert semantic.concept == "Python"
        assert semantic.definition == "A high-level programming language"
        assert semantic.properties == {}
        assert semantic.relationships == {}
        assert semantic.confidence == 1.0
        assert semantic.source is None
        assert isinstance(semantic.created_at, datetime)
        assert semantic.updated_at is None
        assert semantic.metadata == {}
    
    def test_full_initialization(self):
        """Test full initialization with all parameters"""
        created = datetime(2024, 1, 1, 10, 0, 0)
        updated = datetime(2024, 1, 2, 10, 0, 0)
        properties = {"paradigm": "multi-paradigm", "typing": "dynamic"}
        relationships = {"is_a": ["programming_language"], "used_for": ["web_development", "ai"]}
        
        semantic = SemanticMemory(
            concept_id="concept_002",
            concept="Machine Learning",
            definition="A subset of AI that learns from data",
            properties=properties,
            relationships=relationships,
            confidence=0.95,
            source="expert_knowledge",
            created_at=created,
            updated_at=updated,
            metadata={"domain": "technology", "complexity": "high"}
        )
        
        assert semantic.concept_id == "concept_002"
        assert semantic.concept == "Machine Learning"
        assert semantic.properties == properties
        assert semantic.relationships == relationships
        assert semantic.confidence == 0.95
        assert semantic.source == "expert_knowledge"
        assert semantic.created_at == created
        assert semantic.updated_at == updated
        assert semantic.metadata == {"domain": "technology", "complexity": "high"}


class TestProceduralMemory:
    """Test ProceduralMemory dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of ProceduralMemory"""
        steps = [
            {"step": 1, "action": "analyze_problem"},
            {"step": 2, "action": "generate_solution"},
            {"step": 3, "action": "validate_result"}
        ]
        
        procedure = ProceduralMemory(
            procedure_id="proc_001",
            name="Problem Solving",
            description="General problem solving procedure",
            steps=steps
        )
        
        assert procedure.procedure_id == "proc_001"
        assert procedure.name == "Problem Solving"
        assert procedure.description == "General problem solving procedure"
        assert procedure.steps == steps
        assert procedure.preconditions == []
        assert procedure.postconditions == []
        assert procedure.success_rate == 1.0
        assert procedure.usage_count == 0
        assert procedure.last_used is None
        assert isinstance(procedure.created_at, datetime)
        assert procedure.metadata == {}
    
    def test_full_initialization(self):
        """Test full initialization with all parameters"""
        created = datetime(2024, 1, 1, 8, 0, 0)
        last_used = datetime(2024, 1, 5, 14, 30, 0)
        steps = [{"step": 1, "action": "start_process"}]
        preconditions = ["input_available", "system_ready"]
        postconditions = ["output_generated", "state_updated"]
        
        procedure = ProceduralMemory(
            procedure_id="proc_002",
            name="Data Processing",
            description="Process incoming data",
            steps=steps,
            preconditions=preconditions,
            postconditions=postconditions,
            success_rate=0.85,
            usage_count=10,
            last_used=last_used,
            created_at=created,
            metadata={"category": "data_handling", "complexity": "medium"}
        )
        
        assert procedure.preconditions == preconditions
        assert procedure.postconditions == postconditions
        assert procedure.success_rate == 0.85
        assert procedure.usage_count == 10
        assert procedure.last_used == last_used
        assert procedure.created_at == created
        assert procedure.metadata == {"category": "data_handling", "complexity": "medium"}


class TestWorkingMemory:
    """Test WorkingMemory implementation"""
    
    def test_initialization(self):
        """Test WorkingMemory initialization"""
        working_memory = WorkingMemory(capacity=7)
        
        assert working_memory.capacity == 7
        assert working_memory.current_size == 0
        assert len(working_memory.items) == 0
    
    @pytest.mark.asyncio
    async def test_store_item(self):
        """Test storing items in working memory"""
        working_memory = WorkingMemory(capacity=3)
        
        item1 = MemoryItem("item1", "content1", MemoryType.WORKING, 0.8)
        result = await working_memory.store(item1)
        
        assert result is True
        assert working_memory.current_size == 1
        assert "item1" in working_memory.items
    
    @pytest.mark.asyncio
    async def test_capacity_limit(self):
        """Test working memory capacity limits"""
        working_memory = WorkingMemory(capacity=2)
        
        item1 = MemoryItem("item1", "content1", MemoryType.WORKING, 0.5)
        item2 = MemoryItem("item2", "content2", MemoryType.WORKING, 0.7)
        item3 = MemoryItem("item3", "content3", MemoryType.WORKING, 0.9)
        
        await working_memory.store(item1)
        await working_memory.store(item2)
        
        assert working_memory.current_size == 2
        
        # Should evict least important item when adding third
        await working_memory.store(item3)
        
        assert working_memory.current_size == 2
        assert "item1" not in working_memory.items  # Should be evicted (lowest importance)
        assert "item2" in working_memory.items
        assert "item3" in working_memory.items
    
    @pytest.mark.asyncio
    async def test_retrieve_item(self):
        """Test retrieving items from working memory"""
        working_memory = WorkingMemory()
        
        item = MemoryItem("test_item", "test_content", MemoryType.WORKING, 0.7)
        await working_memory.store(item)
        
        retrieved = await working_memory.retrieve("test_item")
        
        assert retrieved is not None
        assert retrieved.item_id == "test_item"
        assert retrieved.content == "test_content"
        assert retrieved.access_count == 1  # Should increment access count
    
    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self):
        """Test retrieving non-existent item"""
        working_memory = WorkingMemory()
        
        retrieved = await working_memory.retrieve("nonexistent")
        
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self):
        """Test searching items by tags"""
        working_memory = WorkingMemory()
        
        item1 = MemoryItem("item1", "content1", MemoryType.WORKING, 0.7, tags=["urgent", "task"])
        item2 = MemoryItem("item2", "content2", MemoryType.WORKING, 0.5, tags=["info", "reference"])
        item3 = MemoryItem("item3", "content3", MemoryType.WORKING, 0.8, tags=["urgent", "info"])
        
        await working_memory.store(item1)
        await working_memory.store(item2)
        await working_memory.store(item3)
        
        urgent_items = await working_memory.search(tags=["urgent"])
        
        assert len(urgent_items) == 2
        assert any(item.item_id == "item1" for item in urgent_items)
        assert any(item.item_id == "item3" for item in urgent_items)


class TestMemorySystem:
    """Test MemorySystem orchestration"""
    
    def test_initialization(self):
        """Test MemorySystem initialization"""
        memory_system = MemorySystem()
        
        assert hasattr(memory_system, 'working_memory')
        assert hasattr(memory_system, 'episodic_memory')
        assert hasattr(memory_system, 'semantic_memory')
        assert hasattr(memory_system, 'procedural_memory')
        assert hasattr(memory_system, 'consolidator')
        assert hasattr(memory_system, 'retriever')
        assert hasattr(memory_system, 'forgetting_mechanism')
    
    @pytest.mark.asyncio
    async def test_store_memory_item(self):
        """Test storing memory items"""
        memory_system = MemorySystem()
        
        item = MemoryItem("test_001", "test_content", MemoryType.WORKING, 0.8)
        result = await memory_system.store_memory(item)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_item(self):
        """Test retrieving memory items"""
        memory_system = MemorySystem()
        
        item = MemoryItem("retrieve_test", "content_to_retrieve", MemoryType.WORKING, 0.7)
        await memory_system.store_memory(item)
        
        retrieved = await memory_system.retrieve_memory("retrieve_test", MemoryType.WORKING)
        
        assert retrieved is not None
        assert retrieved.item_id == "retrieve_test"
        assert retrieved.content == "content_to_retrieve"
    
    @pytest.mark.asyncio
    async def test_search_memories(self):
        """Test searching memories across types"""
        memory_system = MemorySystem()
        
        # Store items in different memory types
        working_item = MemoryItem("work_001", "working_content", MemoryType.WORKING, 0.6, tags=["search_test"])
        await memory_system.store_memory(working_item)
        
        results = await memory_system.search_memories(tags=["search_test"])
        
        assert len(results) >= 1
        assert any(item.item_id == "work_001" for item in results)


class TestMemoryRetriever:
    """Test MemoryRetriever functionality"""
    
    def test_initialization(self):
        """Test MemoryRetriever initialization"""
        retriever = MemoryRetriever()
        
        assert hasattr(retriever, 'retrieval_strategies')
        assert isinstance(retriever.retrieval_strategies, dict)
    
    @pytest.mark.asyncio
    async def test_similarity_based_retrieval(self):
        """Test similarity-based memory retrieval"""
        retriever = MemoryRetriever()
        
        # Create test memories
        memories = [
            MemoryItem("mem1", "python programming", MemoryType.SEMANTIC, 0.8),
            MemoryItem("mem2", "java development", MemoryType.SEMANTIC, 0.7),
            MemoryItem("mem3", "programming concepts", MemoryType.SEMANTIC, 0.9)
        ]
        
        # Test similarity retrieval
        similar = await retriever.retrieve_similar("programming", memories, top_k=2)
        
        assert len(similar) <= 2
        assert all(isinstance(item, MemoryItem) for item in similar)


class TestMemoryConsolidator:
    """Test MemoryConsolidator functionality"""
    
    def test_initialization(self):
        """Test MemoryConsolidator initialization"""
        consolidator = MemoryConsolidator()
        
        assert hasattr(consolidator, 'consolidation_threshold')
        assert hasattr(consolidator, 'consolidation_strategies')
    
    @pytest.mark.asyncio
    async def test_consolidation_process(self):
        """Test memory consolidation process"""
        consolidator = MemoryConsolidator()
        
        # Create working memory items for consolidation
        working_items = [
            MemoryItem("temp1", "temporary_info1", MemoryType.WORKING, 0.9),
            MemoryItem("temp2", "temporary_info2", MemoryType.WORKING, 0.8)
        ]
        
        # Test consolidation
        consolidated = await consolidator.consolidate_memories(working_items)
        
        assert isinstance(consolidated, list)
        # Consolidated memories should have different memory types
        for memory in consolidated:
            assert isinstance(memory, MemoryItem)


class TestForgettingMechanism:
    """Test ForgettingMechanism functionality"""
    
    def test_initialization(self):
        """Test ForgettingMechanism initialization"""
        forgetting = ForgettingMechanism()
        
        assert hasattr(forgetting, 'decay_rate')
        assert hasattr(forgetting, 'forgetting_curve')
    
    def test_calculate_decay(self):
        """Test decay calculation"""
        forgetting = ForgettingMechanism()
        
        # Test decay calculation for different time periods
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        decay_1h = forgetting.calculate_decay(one_hour_ago, now)
        decay_1d = forgetting.calculate_decay(one_day_ago, now)
        
        assert 0.0 <= decay_1h <= 1.0
        assert 0.0 <= decay_1d <= 1.0
        assert decay_1d >= decay_1h  # Older memories should decay more
    
    @pytest.mark.asyncio
    async def test_apply_forgetting(self):
        """Test applying forgetting to memories"""
        forgetting = ForgettingMechanism()
        
        # Create memories with different ages
        old_time = datetime.now() - timedelta(days=30)
        recent_time = datetime.now() - timedelta(hours=1)
        
        old_memory = MemoryItem("old", "old_content", MemoryType.EPISODIC, 0.8, 
                               created_at=old_time, last_accessed=old_time)
        recent_memory = MemoryItem("recent", "recent_content", MemoryType.EPISODIC, 0.8,
                                 created_at=recent_time, last_accessed=recent_time)
        
        memories = [old_memory, recent_memory]
        
        # Apply forgetting
        updated_memories = await forgetting.apply_forgetting(memories)
        
        assert len(updated_memories) <= len(memories)
        # Some memories might be forgotten based on decay


class TestMemoryEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_store_none_item(self):
        """Test storing None item"""
        working_memory = WorkingMemory()
        
        # Should handle None gracefully
        result = await working_memory.store(None)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_retrieve_empty_id(self):
        """Test retrieving with empty ID"""
        working_memory = WorkingMemory()
        
        retrieved = await working_memory.retrieve("")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_search_empty_criteria(self):
        """Test searching with empty criteria"""
        working_memory = WorkingMemory()
        
        # Add some items
        item = MemoryItem("test", "content", MemoryType.WORKING, 0.5)
        await working_memory.store(item)
        
        # Search with empty criteria should return all items
        results = await working_memory.search()
        assert len(results) >= 1
    
    def test_memory_item_with_very_large_content(self):
        """Test memory item with very large content"""
        large_content = {"data": "A" * 100000, "numbers": list(range(10000))}
        
        item = MemoryItem("large", large_content, MemoryType.SEMANTIC, 0.7)
        
        assert item.content == large_content
        assert item.item_id == "large"
    
    def test_memory_item_with_unicode_content(self):
        """Test memory item with unicode content"""
        unicode_content = "记忆内容 🧠 émojis and ñoñ-ASCII"
        
        item = MemoryItem("unicode", unicode_content, MemoryType.EPISODIC, 0.6)
        
        assert item.content == unicode_content
        assert item.item_id == "unicode"


if __name__ == "__main__":
    pytest.main([__file__]) 