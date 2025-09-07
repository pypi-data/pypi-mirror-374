"""
Agentic RAG系统单元测试
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# 测试导入
try:
    from layers.intelligent_context.agentic_rag_system import (
        AgenticRAGProcessor,
        ReflectionEngine,
        RAGPlanningEngine,
        QueryComplexity,
        ReflectionResult,
        RetrievalPlan,
        SimpleRetrievalPlan,
        MultiHopRetrievalPlan,
        CreativeRetrievalPlan,
        RAGContext,
        AgenticResponse
    )
    from layers.framework.abstractions.context import UniversalContext
    from layers.framework.abstractions.task import UniversalTask, TaskType
    AGENTIC_RAG_AVAILABLE = True
except ImportError:
    AGENTIC_RAG_AVAILABLE = False
    pytest.skip("Agentic RAG系统不可用", allow_module_level=True)


class TestReflectionEngine:
    """反思引擎测试"""
    
    def test_initialization(self):
        """测试初始化"""
        engine = ReflectionEngine()
        assert engine is not None
        assert engine.config['quality_threshold'] == 0.8
        assert len(engine.reflection_history) == 0
    
    def test_custom_config(self):
        """测试自定义配置"""
        custom_config = {
            'quality_threshold': 0.9,
            'relevance_weight': 0.4
        }
        engine = ReflectionEngine(custom_config)
        assert engine.config['quality_threshold'] == 0.9
        assert engine.config['relevance_weight'] == 0.4
    
    @pytest.mark.asyncio
    async def test_assess_relevance(self):
        """测试相关性评估"""
        engine = ReflectionEngine()
        
        # 测试高相关性
        relevance = await engine._assess_relevance(
            "FPGA设计方法",
            "FPGA是一种可编程逻辑器件，设计方法包括硬件描述语言编程"
        )
        assert relevance > 0.5
        
        # 测试低相关性
        relevance = await engine._assess_relevance(
            "FPGA设计",
            "今天天气很好"
        )
        assert relevance < 0.3
    
    @pytest.mark.asyncio
    async def test_estimate_query_complexity(self):
        """测试查询复杂度估算"""
        engine = ReflectionEngine()
        
        # 简单查询
        complexity = await engine._estimate_query_complexity("什么是FPGA")
        assert complexity == QueryComplexity.SIMPLE
        
        # 创造性查询
        complexity = await engine._estimate_query_complexity("设计一个FPGA计数器")
        assert complexity == QueryComplexity.CREATIVE
        
        # 多跳推理查询
        complexity = await engine._estimate_query_complexity("比较FPGA和ASIC的优缺点")
        assert complexity == QueryComplexity.MULTI_HOP
    
    @pytest.mark.asyncio
    async def test_reflection_process(self):
        """测试完整反思过程"""
        engine = ReflectionEngine()
        
        # 创建模拟的RAG上下文和生成结果
        rag_context = RAGContext(
            query="什么是FPGA",
            plan=SimpleRetrievalPlan(),
            iteration=0,
            accumulated_knowledge=[],
            context_metadata={}
        )
        
        # 模拟生成结果
        from layers.intelligent_context.rag_system import GenerationResult, GenerationMode
        generation_result = GenerationResult(
            generated_content="FPGA是Field Programmable Gate Array的缩写，是一种可编程逻辑器件。",
            confidence_score=0.8,
            generation_metadata={'sources': []},
            mode_used=GenerationMode.GUIDED
        )
        
        # 执行反思
        reflection_result = await engine.reflect(rag_context, generation_result)
        
        assert isinstance(reflection_result, ReflectionResult)
        assert reflection_result.confidence > 0.0
        assert len(reflection_result.quality_dimensions) > 0
        assert 'relevance' in reflection_result.quality_dimensions


class TestRAGPlanningEngine:
    """RAG规划引擎测试"""
    
    def test_initialization(self):
        """测试初始化"""
        engine = RAGPlanningEngine()
        assert engine is not None
        assert engine.config['max_iterations'] == 5
        assert len(engine.planning_history) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_query_complexity(self):
        """测试查询复杂度分析"""
        engine = RAGPlanningEngine()
        
        # 测试不同类型的查询
        test_cases = [
            ("什么是", QueryComplexity.SIMPLE),
            ("如何设计", QueryComplexity.MODERATE),
            ("比较分析", QueryComplexity.MULTI_HOP),
            ("创建一个", QueryComplexity.CREATIVE),
            ("优化性能", QueryComplexity.COMPLEX)
        ]
        
        for query, expected_complexity in test_cases:
            complexity = await engine._analyze_query_complexity(query)
            assert complexity == expected_complexity
    
    @pytest.mark.asyncio
    async def test_create_retrieval_plan(self):
        """测试检索计划创建"""
        engine = RAGPlanningEngine()
        
        # 简单查询计划
        plan = await engine.create_retrieval_plan("什么是FPGA")
        assert isinstance(plan, SimpleRetrievalPlan)
        assert plan.max_iterations == 1
        
        # 多跳查询计划
        plan = await engine.create_retrieval_plan("比较FPGA和ASIC的设计流程")
        assert isinstance(plan, MultiHopRetrievalPlan)
        assert plan.max_iterations == 3
        
        # 创造性查询计划
        plan = await engine.create_retrieval_plan("设计一个FPGA计数器模块")
        assert isinstance(plan, CreativeRetrievalPlan)
        assert plan.max_iterations == 5
    
    @pytest.mark.asyncio
    async def test_decompose_query(self):
        """测试查询分解"""
        engine = RAGPlanningEngine()
        
        # 测试连接词分解
        sub_queries = await engine._decompose_query("FPGA设计方法和ASIC设计流程")
        assert len(sub_queries) >= 2
        
        # 测试标点符号分解
        sub_queries = await engine._decompose_query("什么是FPGA，如何使用")
        assert len(sub_queries) >= 2
    
    @pytest.mark.asyncio
    async def test_extract_creative_requirements(self):
        """测试创造性需求提取"""
        engine = RAGPlanningEngine()
        
        # 测试代码生成需求
        requirements = await engine._extract_creative_requirements("写一个Verilog代码")
        assert requirements['output_format'] == 'code'
        
        # 测试FPGA领域需求
        requirements = await engine._extract_creative_requirements("设计FPGA时序约束")
        assert requirements['domain_specific'] == True
        assert requirements['domain'] == 'fpga'


class TestAgenticRAGProcessor:
    """Agentic RAG处理器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        processor = AgenticRAGProcessor()
        assert processor is not None
        assert processor.reflection_engine is not None
        assert processor.planning_engine is not None
        assert processor.base_rag_system is not None
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = {
            'max_iterations': 3,
            'quality_threshold': 0.9,
            'enable_reflection': False
        }
        processor = AgenticRAGProcessor(config)
        assert processor.config['max_iterations'] == 3
        assert processor.config['quality_threshold'] == 0.9
        assert processor.config['enable_reflection'] == False
    
    def test_extract_query_from_task(self):
        """测试从任务提取查询"""
        processor = AgenticRAGProcessor()
        
        # 测试有content的任务
        task = UniversalTask(content="什么是FPGA", task_type=TaskType.CONVERSATION)
        query = processor._extract_query_from_task(task)
        assert query == "什么是FPGA"
        
        # 测试没有content的任务
        task = Mock()
        task.content = None
        task.description = "FPGA相关问题"
        query = processor._extract_query_from_task(task)
        assert query == "FPGA相关问题"
    
    @pytest.mark.asyncio
    async def test_adapt_query_for_iteration(self):
        """测试迭代查询适配"""
        processor = AgenticRAGProcessor()
        
        # 创建多跳计划的上下文
        sub_queries = ["FPGA基础", "FPGA应用", "FPGA优势"]
        plan = MultiHopRetrievalPlan(sub_queries)
        rag_context = RAGContext(
            query="什么是FPGA",
            plan=plan,
            iteration=0,
            accumulated_knowledge=[],
            context_metadata={}
        )
        
        # 测试子查询选择
        adapted_query = await processor._adapt_query_for_iteration(rag_context)
        assert adapted_query in sub_queries
        
        # 测试迭代调整
        rag_context.iteration = 1
        rag_context.accumulated_knowledge.append({
            'content': 'short content'
        })
        adapted_query = await processor._adapt_query_for_iteration(rag_context)
        assert "完整信息" in adapted_query or adapted_query in sub_queries
    
    @pytest.mark.asyncio
    async def test_convert_agentic_response_to_context(self):
        """测试Agentic响应转换为上下文"""
        processor = AgenticRAGProcessor()
        
        base_context = UniversalContext({'original': 'data'})
        agentic_response = AgenticResponse(
            content="测试内容",
            confidence=0.8,
            iterations_used=2,
            quality_dimensions={'relevance': 0.9},
            sources=[{'id': 'doc1'}],
            metadata={'test': 'metadata'}
        )
        
        enhanced_context = await processor._convert_agentic_response_to_context(
            base_context, agentic_response
        )
        
        assert enhanced_context.get('rag_enhanced_content') == "测试内容"
        assert enhanced_context.get('rag_metadata')['confidence'] == 0.8
        assert enhanced_context.get('rag_metadata')['iterations_used'] == 2
        assert enhanced_context.get('rag_processing_info')['processor_type'] == 'agentic'


@pytest.mark.asyncio
@pytest.mark.integration
class TestAgenticRAGIntegration:
    """Agentic RAG集成测试"""
    
    async def test_simple_processing_flow(self):
        """测试简单处理流程"""
        processor = AgenticRAGProcessor({
            'max_iterations': 2,
            'enable_reflection': True,
            'enable_planning': True
        })
        
        # 模拟处理
        with patch.object(processor.base_rag_system, 'enhance_with_rag') as mock_rag:
            mock_enhanced_context = UniversalContext({
                'rag_enhanced_content': '测试RAG内容',
                'rag_metadata': {'quality_score': 0.8}
            })
            mock_rag.return_value = mock_enhanced_context
            
            result = await processor.process("什么是FPGA？")
            
            assert isinstance(result, AgenticResponse)
            assert result.confidence > 0.0
            assert result.iterations_used >= 1
            assert len(result.content) > 0
    
    async def test_complex_query_processing(self):
        """测试复杂查询处理"""
        processor = AgenticRAGProcessor({
            'max_iterations': 3,
            'quality_threshold': 0.7
        })
        
        complex_query = "比较FPGA和ASIC在设计流程、成本和性能方面的差异"
        
        with patch.object(processor.base_rag_system, 'enhance_with_rag') as mock_rag:
            mock_enhanced_context = UniversalContext({
                'rag_enhanced_content': '详细的比较分析内容...',
                'rag_metadata': {'quality_score': 0.75}
            })
            mock_rag.return_value = mock_enhanced_context
            
            result = await processor.process(complex_query)
            
            assert isinstance(result, AgenticResponse)
            assert result.iterations_used >= 1
            # 复杂查询可能需要更多迭代
            assert result.iterations_used <= 3
    
    async def test_error_handling(self):
        """测试错误处理"""
        processor = AgenticRAGProcessor()
        
        # 模拟RAG系统错误
        with patch.object(processor.base_rag_system, 'enhance_with_rag') as mock_rag:
            mock_rag.side_effect = Exception("RAG系统错误")
            
            result = await processor.process("测试查询")
            
            # 应该返回错误响应而不是抛出异常
            assert isinstance(result, AgenticResponse)
            assert result.confidence < 0.5
            assert "错误" in result.content


# 测试数据和工具函数
@pytest.fixture
def sample_rag_context():
    """示例RAG上下文"""
    return RAGContext(
        query="什么是FPGA",
        plan=SimpleRetrievalPlan(),
        iteration=0,
        accumulated_knowledge=[],
        context_metadata={'test': True}
    )

@pytest.fixture
def sample_generation_result():
    """示例生成结果"""
    from layers.intelligent_context.rag_system import GenerationResult, GenerationMode
    return GenerationResult(
        generated_content="FPGA是可编程逻辑器件",
        confidence_score=0.8,
        generation_metadata={'sources': [{'id': 'doc1'}]},
        mode_used=GenerationMode.GUIDED
    )

@pytest.fixture
def sample_agentic_response():
    """示例Agentic响应"""
    return AgenticResponse(
        content="详细的FPGA介绍内容",
        confidence=0.85,
        iterations_used=2,
        quality_dimensions={
            'relevance': 0.9,
            'accuracy': 0.8,
            'completeness': 0.85,
            'clarity': 0.8
        },
        sources=[{'id': 'doc1'}, {'id': 'doc2'}],
        metadata={'processing_time': 1.5}
    ) 