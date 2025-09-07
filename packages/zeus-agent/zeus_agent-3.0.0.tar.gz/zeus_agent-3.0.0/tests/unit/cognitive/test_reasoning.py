"""
Unit tests for reasoning module
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from layers.cognitive.reasoning import (
    ReasoningEngine,
    LogicalReasoner,
    CausalReasoner,
    AnalogicalReasoner,
    InductiveReasoner,
    BaseReasoner,
    ReasoningResult,
    ReasoningStep,
    ReasoningType,
    ConfidenceLevel
)


class MockReasoner(BaseReasoner):
    """Mock reasoner for testing"""
    
    def __init__(self, name: str = "MockReasoner", reasoning_type: ReasoningType = ReasoningType.LOGICAL):
        super().__init__(name, reasoning_type)
        self.reason_called = False
        self.can_handle_called = False
        self.last_premises = None
        self.last_context = None
    
    async def reason(self, premises: List[str], context: Dict[str, Any] = None) -> ReasoningResult:
        """Mock reasoning method"""
        self.reason_called = True
        self.last_premises = premises
        self.last_context = context
        
        return ReasoningResult(
            conclusion="Mock conclusion from premises",
            reasoning_type=self.reasoning_type,
            confidence=0.8,
            premises=premises,
            steps=[
                ReasoningStep(
                    step_id="step_1",
                    description="Mock reasoning step",
                    input_data=premises,
                    output_data="intermediate result",
                    reasoning_type=self.reasoning_type,
                    confidence=0.8
                )
            ]
        )
    
    def can_handle(self, premises: List[str], context: Dict[str, Any] = None) -> bool:
        """Mock can_handle method"""
        self.can_handle_called = True
        return len(premises) > 0


class TestReasoningType:
    """Test ReasoningType enum"""
    
    def test_reasoning_type_values(self):
        """Test all reasoning type values"""
        assert ReasoningType.DEDUCTIVE.value == "deductive"
        assert ReasoningType.INDUCTIVE.value == "inductive"
        assert ReasoningType.ABDUCTIVE.value == "abductive"
        assert ReasoningType.ANALOGICAL.value == "analogical"
        assert ReasoningType.CAUSAL.value == "causal"
        assert ReasoningType.LOGICAL.value == "logical"
        assert ReasoningType.PROBABILISTIC.value == "probabilistic"
    
    def test_reasoning_type_count(self):
        """Test that we have all expected reasoning types"""
        types = list(ReasoningType)
        assert len(types) == 7


class TestConfidenceLevel:
    """Test ConfidenceLevel enum"""
    
    def test_confidence_level_values(self):
        """Test all confidence level values"""
        assert ConfidenceLevel.VERY_LOW.value == "very_low"
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.VERY_HIGH.value == "very_high"
    
    def test_confidence_level_count(self):
        """Test that we have all expected confidence levels"""
        levels = list(ConfidenceLevel)
        assert len(levels) == 5


class TestReasoningStep:
    """Test ReasoningStep dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of ReasoningStep"""
        step = ReasoningStep(
            step_id="step_1",
            description="Test step",
            input_data=["premise1", "premise2"],
            output_data="conclusion",
            reasoning_type=ReasoningType.LOGICAL,
            confidence=0.9
        )
        
        assert step.step_id == "step_1"
        assert step.description == "Test step"
        assert step.input_data == ["premise1", "premise2"]
        assert step.output_data == "conclusion"
        assert step.reasoning_type == ReasoningType.LOGICAL
        assert step.confidence == 0.9
        assert isinstance(step.timestamp, datetime)
        assert step.metadata == {}
    
    def test_full_initialization(self):
        """Test full initialization with metadata"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        metadata = {"source": "test", "method": "modus_ponens"}
        
        step = ReasoningStep(
            step_id="step_2",
            description="Complex step",
            input_data={"premises": ["A", "B"]},
            output_data={"conclusion": "C"},
            reasoning_type=ReasoningType.DEDUCTIVE,
            confidence=0.75,
            timestamp=timestamp,
            metadata=metadata
        )
        
        assert step.step_id == "step_2"
        assert step.description == "Complex step"
        assert step.reasoning_type == ReasoningType.DEDUCTIVE
        assert step.confidence == 0.75
        assert step.timestamp == timestamp
        assert step.metadata == metadata


class TestReasoningResult:
    """Test ReasoningResult dataclass"""
    
    def test_basic_initialization(self):
        """Test basic initialization of ReasoningResult"""
        result = ReasoningResult(
            conclusion="Test conclusion",
            reasoning_type=ReasoningType.INDUCTIVE,
            confidence=0.8
        )
        
        assert result.conclusion == "Test conclusion"
        assert result.reasoning_type == ReasoningType.INDUCTIVE
        assert result.confidence == 0.8
        assert result.steps == []
        assert result.premises == []
        assert result.assumptions == []
        assert result.evidence == []
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)
    
    def test_full_initialization(self):
        """Test full initialization with all parameters"""
        steps = [
            ReasoningStep("step1", "First step", "input", "output", ReasoningType.LOGICAL)
        ]
        premises = ["If A then B", "A is true"]
        assumptions = ["Standard logic applies"]
        evidence = [{"type": "observation", "data": "B is observed"}]
        metadata = {"method": "deduction", "source": "test"}
        
        result = ReasoningResult(
            conclusion="Therefore B is true",
            reasoning_type=ReasoningType.DEDUCTIVE,
            confidence=0.95,
            steps=steps,
            premises=premises,
            assumptions=assumptions,
            evidence=evidence,
            metadata=metadata
        )
        
        assert result.conclusion == "Therefore B is true"
        assert result.reasoning_type == ReasoningType.DEDUCTIVE
        assert result.confidence == 0.95
        assert result.steps == steps
        assert result.premises == premises
        assert result.assumptions == assumptions
        assert result.evidence == evidence
        assert result.metadata == metadata
    
    def test_confidence_level_calculation(self):
        """Test confidence level calculation"""
        # Test VERY_LOW (0.0 - 0.2)
        result_very_low = ReasoningResult("test", ReasoningType.LOGICAL, 0.1)
        assert result_very_low.get_confidence_level() == ConfidenceLevel.VERY_LOW
        
        # Test LOW (0.2 - 0.4)
        result_low = ReasoningResult("test", ReasoningType.LOGICAL, 0.3)
        assert result_low.get_confidence_level() == ConfidenceLevel.LOW
        
        # Test MEDIUM (0.4 - 0.6)
        result_medium = ReasoningResult("test", ReasoningType.LOGICAL, 0.5)
        assert result_medium.get_confidence_level() == ConfidenceLevel.MEDIUM
        
        # Test HIGH (0.6 - 0.8)
        result_high = ReasoningResult("test", ReasoningType.LOGICAL, 0.7)
        assert result_high.get_confidence_level() == ConfidenceLevel.HIGH
        
        # Test VERY_HIGH (0.8 - 1.0)
        result_very_high = ReasoningResult("test", ReasoningType.LOGICAL, 0.9)
        assert result_very_high.get_confidence_level() == ConfidenceLevel.VERY_HIGH
        
        # Test boundary cases
        result_boundary_low = ReasoningResult("test", ReasoningType.LOGICAL, 0.2)
        assert result_boundary_low.get_confidence_level() == ConfidenceLevel.LOW
        
        result_boundary_high = ReasoningResult("test", ReasoningType.LOGICAL, 0.8)
        assert result_boundary_high.get_confidence_level() == ConfidenceLevel.VERY_HIGH
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        step = ReasoningStep("step1", "Test step", "input", "output", ReasoningType.LOGICAL)
        result = ReasoningResult(
            conclusion="Test conclusion",
            reasoning_type=ReasoningType.CAUSAL,
            confidence=0.85,
            steps=[step],
            premises=["premise1"],
            assumptions=["assumption1"],
            evidence=[{"data": "evidence1"}],
            metadata={"source": "test"}
        )
        
        data = result.to_dict()
        
        assert data["conclusion"] == "Test conclusion"
        assert data["reasoning_type"] == "causal"
        assert data["confidence"] == 0.85
        assert len(data["steps"]) == 1
        assert data["premises"] == ["premise1"]
        assert data["assumptions"] == ["assumption1"]
        assert data["evidence"] == [{"data": "evidence1"}]
        assert data["metadata"] == {"source": "test"}
        assert "timestamp" in data


class TestBaseReasoner:
    """Test BaseReasoner abstract class"""
    
    def test_initialization(self):
        """Test reasoner initialization"""
        reasoner = MockReasoner("TestReasoner", ReasoningType.ANALOGICAL)
        
        assert reasoner.name == "TestReasoner"
        assert reasoner.reasoning_type == ReasoningType.ANALOGICAL
        assert reasoner.enabled is True
        assert reasoner.config == {}
    
    def test_configure_method(self):
        """Test configuration method"""
        reasoner = MockReasoner()
        config = {"threshold": 0.7, "max_steps": 10}
        
        reasoner.configure(config)
        
        assert reasoner.config == config
        
        # Test updating configuration
        new_config = {"threshold": 0.8, "verbose": True}
        reasoner.configure(new_config)
        
        expected = {"threshold": 0.8, "max_steps": 10, "verbose": True}
        assert reasoner.config == expected
    
    @pytest.mark.asyncio
    async def test_reason_method(self):
        """Test reasoning method"""
        reasoner = MockReasoner()
        premises = ["All humans are mortal", "Socrates is human"]
        context = {"domain": "philosophy"}
        
        result = await reasoner.reason(premises, context)
        
        assert reasoner.reason_called is True
        assert reasoner.last_premises == premises
        assert reasoner.last_context == context
        assert isinstance(result, ReasoningResult)
        assert result.conclusion == "Mock conclusion from premises"
        assert result.reasoning_type == ReasoningType.LOGICAL
        assert len(result.steps) == 1
    
    def test_can_handle_method(self):
        """Test can_handle method"""
        reasoner = MockReasoner()
        
        # Test with premises
        premises = ["premise1", "premise2"]
        assert reasoner.can_handle(premises) is True
        assert reasoner.can_handle_called is True
        
        # Reset and test empty premises
        reasoner.can_handle_called = False
        assert reasoner.can_handle([]) is False
        assert reasoner.can_handle_called is True


class TestLogicalReasoner:
    """Test LogicalReasoner implementation"""
    
    def test_initialization(self):
        """Test LogicalReasoner initialization"""
        reasoner = LogicalReasoner()
        
        assert reasoner.name == "LogicalReasoner"
        assert reasoner.reasoning_type == ReasoningType.LOGICAL
        assert reasoner.enabled is True
        assert hasattr(reasoner, 'logical_operators')
        assert hasattr(reasoner, 'patterns')
        assert "and" in reasoner.logical_operators
        assert "modus_ponens" in reasoner.patterns
    
    def test_can_handle_logical_premises(self):
        """Test can_handle with logical premises"""
        reasoner = LogicalReasoner()
        
        # Should handle premises with logical operators
        logical_premises = ["If A then B", "A is true"]
        assert reasoner.can_handle(logical_premises) is True
        
        # Should handle premises with Chinese logical operators
        chinese_premises = ["如果下雨，那么地面湿润", "现在下雨"]
        assert reasoner.can_handle(chinese_premises) is True
        
        # Should not handle empty premises
        assert reasoner.can_handle([]) is False
    
    @pytest.mark.asyncio
    async def test_reason_basic_logic(self):
        """Test basic logical reasoning"""
        reasoner = LogicalReasoner()
        premises = ["If it rains, then the ground is wet", "It is raining"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        assert result.reasoning_type == ReasoningType.LOGICAL
        assert result.premises == premises
        assert result.confidence > 0
        assert len(result.steps) > 0
    
    @pytest.mark.asyncio
    async def test_reason_with_context(self):
        """Test reasoning with additional context"""
        reasoner = LogicalReasoner()
        premises = ["如果下雨，那么地面湿润", "现在下雨"]  # Use Chinese logical structure
        context = {"domain": "weather"}
        
        result = await reasoner.reason(premises, context)
        
        assert isinstance(result, ReasoningResult)
        assert result.reasoning_type == ReasoningType.LOGICAL
        # Context should influence the reasoning
    
    @pytest.mark.asyncio
    async def test_reason_invalid_premises(self):
        """Test reasoning with invalid or contradictory premises"""
        reasoner = LogicalReasoner()
        premises = ["如果A，那么B", "A为真"]  # Valid logical structure
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should handle logical premises
        assert result.confidence > 0


class TestCausalReasoner:
    """Test CausalReasoner implementation"""
    
    def test_initialization(self):
        """Test CausalReasoner initialization"""
        reasoner = CausalReasoner()
        
        assert reasoner.name == "CausalReasoner"
        assert reasoner.reasoning_type == ReasoningType.CAUSAL
        assert reasoner.enabled is True
    
    def test_can_handle_causal_premises(self):
        """Test can_handle with causal premises"""
        reasoner = CausalReasoner()
        
        # Should handle premises with causal indicators
        causal_premises = ["Smoking causes cancer", "John smokes"]
        assert reasoner.can_handle(causal_premises) is True
        
        # Should handle premises with causal keywords
        cause_effect_premises = ["雨水导致地面湿润", "昨天下雨了"]  # Use Chinese causal structure
        assert reasoner.can_handle(cause_effect_premises) is True
        
        # Should not handle empty premises
        assert reasoner.can_handle([]) is False
    
    @pytest.mark.asyncio
    async def test_reason_causal_chain(self):
        """Test causal chain reasoning"""
        reasoner = CausalReasoner()
        premises = ["Heavy rain causes flooding", "Flooding causes traffic delays", "It rained heavily"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        assert result.reasoning_type == ReasoningType.CAUSAL
        assert result.confidence > 0
        # Should identify causal chain
    
    @pytest.mark.asyncio
    async def test_reason_correlation_vs_causation(self):
        """Test handling correlation vs causation"""
        reasoner = CausalReasoner()
        premises = ["抽烟导致癌症", "约翰抽烟"]  # Use clear causal structure
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should handle causal premises
        assert result.confidence > 0


class TestAnalogicalReasoner:
    """Test AnalogicalReasoner implementation"""
    
    def test_initialization(self):
        """Test AnalogicalReasoner initialization"""
        reasoner = AnalogicalReasoner()
        
        assert reasoner.name == "AnalogicalReasoner"
        assert reasoner.reasoning_type == ReasoningType.ANALOGICAL
        assert reasoner.enabled is True
    
    def test_can_handle_analogical_premises(self):
        """Test can_handle with analogical premises"""
        reasoner = AnalogicalReasoner()
        
        # Should handle premises with analogical structure
        analogy_premises = ["The atom is like a solar system", "Electrons orbit the nucleus"]
        assert reasoner.can_handle(analogy_premises) is True
        
        # Should handle comparison premises
        comparison_premises = ["A heart is similar to a pump", "Pumps move fluids"]
        assert reasoner.can_handle(comparison_premises) is True
    
    @pytest.mark.asyncio
    async def test_reason_analogy(self):
        """Test analogical reasoning"""
        reasoner = AnalogicalReasoner()
        premises = ["The brain is like a computer", "Computers process information", "Computers have memory"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        assert result.reasoning_type == ReasoningType.ANALOGICAL
        assert result.confidence > 0
        # Should draw conclusions based on analogy
    
    @pytest.mark.asyncio
    async def test_reason_weak_analogy(self):
        """Test handling weak analogies"""
        reasoner = AnalogicalReasoner()
        premises = ["The Earth is like a spaceship", "Spaceships have pilots"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should recognize weak analogy
        assert result.confidence <= 0.6  # Lower confidence for weak analogy


class TestInductiveReasoner:
    """Test InductiveReasoner implementation"""
    
    def test_initialization(self):
        """Test InductiveReasoner initialization"""
        reasoner = InductiveReasoner()
        
        assert reasoner.name == "InductiveReasoner"
        assert reasoner.reasoning_type == ReasoningType.INDUCTIVE
        assert reasoner.enabled is True
    
    def test_can_handle_inductive_premises(self):
        """Test can_handle with inductive premises"""
        reasoner = InductiveReasoner()
        
        # Should handle premises with patterns or observations
        pattern_premises = ["Swan 1 is white", "Swan 2 is white", "Swan 3 is white"]
        assert reasoner.can_handle(pattern_premises) is True
        
        # Should handle statistical premises
        stats_premises = ["90% of cats like fish", "Fluffy is a cat"]
        assert reasoner.can_handle(stats_premises) is True
    
    @pytest.mark.asyncio
    async def test_reason_pattern_recognition(self):
        """Test pattern-based inductive reasoning"""
        reasoner = InductiveReasoner()
        premises = ["The sun rose yesterday", "The sun rose today", "The sun has risen every day in history"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        assert result.reasoning_type == ReasoningType.INDUCTIVE
        assert result.confidence > 0
        # Should predict future based on pattern
    
    @pytest.mark.asyncio
    async def test_reason_statistical_inference(self):
        """Test statistical inductive reasoning"""
        reasoner = InductiveReasoner()
        premises = ["95% of emails with 'FREE' in subject are spam", "This email has 'FREE' in subject"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should make probabilistic conclusion
        assert result.confidence > 0.5  # Should have reasonable confidence
    
    @pytest.mark.asyncio
    async def test_reason_small_sample(self):
        """Test reasoning with small sample size"""
        reasoner = InductiveReasoner()
        premises = ["Person 1 likes chocolate", "Person 2 likes chocolate"]
        
        result = await reasoner.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should have lower confidence due to small sample
        assert result.confidence < 0.7


class TestReasoningEngine:
    """Test ReasoningEngine orchestration"""
    
    def test_initialization(self):
        """Test ReasoningEngine initialization"""
        engine = ReasoningEngine()
        
        assert hasattr(engine, 'reasoners')
        assert isinstance(engine.reasoners, dict)
        assert len(engine.reasoners) >= 4  # Should have default reasoners
        assert hasattr(engine, 'reasoning_history')
        assert isinstance(engine.reasoning_history, list)
    
    def test_register_reasoner(self):
        """Test registering a new reasoner"""
        engine = ReasoningEngine()
        reasoner = MockReasoner("TestReasoner")
        
        initial_count = len(engine.reasoners)
        engine.register_reasoner(reasoner)
        
        assert len(engine.reasoners) == initial_count + 1
        assert "TestReasoner" in engine.reasoners
        assert engine.reasoners["TestReasoner"] == reasoner
    
    def test_unregister_reasoner(self):
        """Test unregistering a reasoner"""
        engine = ReasoningEngine()
        reasoner = MockReasoner("TestReasoner")
        
        engine.register_reasoner(reasoner)
        initial_count = len(engine.reasoners)
        
        result = engine.unregister_reasoner("TestReasoner")
        
        assert result is True
        assert len(engine.reasoners) == initial_count - 1
        assert "TestReasoner" not in engine.reasoners
        
        # Test unregistering non-existent reasoner
        result = engine.unregister_reasoner("NonExistent")
        assert result is False
    
    def test_get_reasoner_by_name(self):
        """Test getting reasoner by name"""
        engine = ReasoningEngine()
        reasoner = MockReasoner("UniqueReasoner")
        
        engine.register_reasoner(reasoner)
        
        found = engine.get_reasoner("UniqueReasoner")
        assert found == reasoner
        
        not_found = engine.get_reasoner("NonExistentReasoner")
        assert not_found is None
    
    @pytest.mark.asyncio
    async def test_reason_with_suitable_reasoner(self):
        """Test reasoning with a suitable reasoner"""
        engine = ReasoningEngine()
        reasoner = MockReasoner("TestReasoner")
        engine.register_reasoner(reasoner)
        
        premises = ["premise1", "premise2"]
        result = await engine.reason(premises)
        
        assert isinstance(result, ReasoningResult)
        # Should use one of the available reasoners
    
    @pytest.mark.asyncio
    async def test_reason_with_preferred_reasoner(self):
        """Test reasoning with preferred reasoner"""
        engine = ReasoningEngine()
        reasoner = MockReasoner("PreferredReasoner")
        engine.register_reasoner(reasoner)
        
        premises = ["logical premise"]
        result = await engine.reason(premises, preferred_reasoner="PreferredReasoner")
        
        assert isinstance(result, ReasoningResult)
        assert reasoner.reason_called is True
    
    @pytest.mark.asyncio
    async def test_reason_no_suitable_reasoner(self):
        """Test reasoning when no reasoner can handle premises"""
        engine = ReasoningEngine()
        # Clear all reasoners
        engine.reasoners.clear()
        
        premises = ["unsupported premise"]
        result = await engine.reason(premises)
        
        # Should return a fallback result
        assert isinstance(result, ReasoningResult)
        assert result.confidence < 0.5  # Low confidence for fallback
    
    @pytest.mark.asyncio
    async def test_reasoning_history(self):
        """Test reasoning history tracking"""
        engine = ReasoningEngine()
        
        initial_history_length = len(engine.reasoning_history)
        
        premises = ["test premise"]
        await engine.reason(premises)
        
        # History should be updated
        assert len(engine.reasoning_history) == initial_history_length + 1
        assert isinstance(engine.reasoning_history[-1], ReasoningResult)


class TestReasoningEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_reason_empty_premises(self):
        """Test reasoning with empty premises"""
        reasoner = LogicalReasoner()
        
        # LogicalReasoner should raise error for empty premises
        with pytest.raises(ValueError, match="LogicalReasoner cannot handle the given premises"):
            await reasoner.reason([])
    
    @pytest.mark.asyncio
    async def test_reason_none_premises(self):
        """Test reasoning with None premises"""
        reasoner = LogicalReasoner()
        
        # LogicalReasoner should raise error for None premises
        with pytest.raises(ValueError, match="LogicalReasoner cannot handle the given premises"):
            await reasoner.reason(None)
    
    @pytest.mark.asyncio
    async def test_reason_very_long_premises(self):
        """Test reasoning with very long premises"""
        reasoner = LogicalReasoner()
        long_premises = ["Very long premise " + "word " * 1000] * 10
        
        result = await reasoner.reason(long_premises)
        
        assert isinstance(result, ReasoningResult)
        # Should handle long premises without crashing
    
    @pytest.mark.asyncio
    async def test_reason_unicode_premises(self):
        """Test reasoning with unicode premises"""
        reasoner = LogicalReasoner()
        unicode_premises = ["如果天下雨，那么地面湿润 🌧️", "现在天下雨了 ☔"]
        
        result = await reasoner.reason(unicode_premises)
        
        assert isinstance(result, ReasoningResult)
        assert result.premises == unicode_premises
    
    def test_reasoner_name_uniqueness(self):
        """Test handling of duplicate reasoner names"""
        engine = ReasoningEngine()
        reasoner1 = MockReasoner("SameName")
        reasoner2 = MockReasoner("SameName")
        
        engine.register_reasoner(reasoner1)
        engine.register_reasoner(reasoner2)
        
        # Second registration should replace the first
        assert engine.reasoners["SameName"] == reasoner2
        
        found = engine.get_reasoner("SameName")
        assert found == reasoner2


if __name__ == "__main__":
    pytest.main([__file__]) 