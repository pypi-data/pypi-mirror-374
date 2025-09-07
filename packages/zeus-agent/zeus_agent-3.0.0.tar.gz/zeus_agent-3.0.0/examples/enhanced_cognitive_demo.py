#!/usr/bin/env python3
"""
Enhanced Cognitive Demo
增强认知演示 - 验证新的感知、推理和记忆管理功能

演示以下增强功能：
1. 增强的框架抽象层：任务执行流程、上下文管理、结果处理
2. 深化的认知架构层：基础感知模块、简单推理能力、完善记忆管理
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 基础设施层导入
from layers.infrastructure.logging import get_logger

# 框架抽象层导入（增强版）
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskRequirements
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult, ResultStatus, ResultType

# 认知架构层导入（新增模块）
from layers.cognitive.perception import PerceptionEngine, TextPerceptor, StructuredDataPerceptor
from layers.cognitive.reasoning import ReasoningEngine, LogicalReasoner, CausalReasoner
from layers.cognitive.memory import MemorySystem

logger = get_logger("enhanced_cognitive_demo")


class EnhancedCognitiveDemo:
    """增强认知演示类"""
    
    def __init__(self):
        self.perception_engine = None
        self.reasoning_engine = None
        self.memory_system = None
    
    async def initialize(self):
        """初始化认知组件"""
        logger.info("🧠 初始化增强认知演示")
        
        # 初始化感知引擎
        self.perception_engine = PerceptionEngine()
        logger.info("✅ 感知引擎初始化完成")
        
        # 初始化推理引擎
        self.reasoning_engine = ReasoningEngine()
        logger.info("✅ 推理引擎初始化完成")
        
        # 初始化记忆系统
        self.memory_system = MemorySystem()
        logger.info("✅ 记忆系统初始化完成")
    
    async def run_demo(self):
        """运行增强认知演示"""
        logger.info("🚀 开始运行增强认知演示")
        
        # 演示1: 增强的任务执行流程
        await self._demo_enhanced_task_execution()
        
        # 演示2: 完善的上下文管理
        await self._demo_enhanced_context_management()
        
        # 演示3: 加强的结果处理
        await self._demo_enhanced_result_processing()
        
        # 演示4: 基础感知模块
        await self._demo_basic_perception()
        
        # 演示5: 简单推理能力
        await self._demo_simple_reasoning()
        
        # 演示6: 完善的记忆管理
        await self._demo_enhanced_memory_management()
        
        logger.info("🎉 增强认知演示运行完成")
    
    async def _demo_enhanced_task_execution(self):
        """演示增强的任务执行流程"""
        logger.info("\n" + "="*60)
        logger.info("📋 演示1: 增强的任务执行流程")
        logger.info("="*60)
        
        try:
            # 创建带有详细要求的任务
            requirements = TaskRequirements(
                capabilities=["text_processing", "analysis"],
                max_execution_time=30,  # 30秒
                memory_limit=100,       # 100MB
                preferred_framework="openai"
            )
            
            task = UniversalTask(
                content="分析以下文本的情感倾向和主要主题：我今天心情很好，学习了很多关于人工智能的知识。",
                task_type=TaskType.ANALYSIS,
                requirements=requirements,
                task_id="enhanced_demo_task_001"
            )
            
            # 验证任务
            validation_errors = task.validate()
            if validation_errors:
                logger.info(f"❌ 任务验证失败: {validation_errors}")
                return
            
            logger.info(f"✅ 任务验证通过: {task.content[:50]}...")
            
            # 检查任务是否可以执行
            if task.can_execute():
                logger.info("✅ 任务可以执行")
                
                # 开始执行
                task.start()
                logger.info(f"🎯 任务开始执行，ID: {task.id}")
                
                # 添加检查点
                task.add_checkpoint("validation_complete", {"status": "passed"})
                task.add_checkpoint("execution_started", {"timestamp": "now"})
                
                # 模拟执行过程
                await asyncio.sleep(0.1)  # 模拟处理时间
                
                # 创建结果
                result = UniversalResult(
                    content="分析结果：情感倾向为积极，主要主题为人工智能学习",
                    status=ResultStatus.SUCCESS,
                    result_type=ResultType.ANALYSIS
                )
                result.set_confidence_score(0.85)
                
                # 完成任务
                task.complete(result)
                
                logger.info(f"✅ 任务执行完成")
                logger.info(f"⏱️  执行时间: {task.get_elapsed_time():.3f}秒")
                logger.info(f"📊 检查点数量: {len(task.get_checkpoints())}")
                
            else:
                logger.info("❌ 任务无法执行")
        
        except Exception as e:
            logger.error(f"❌ 任务执行演示失败: {e}")
    
    async def _demo_enhanced_context_management(self):
        """演示完善的上下文管理"""
        logger.info("\n" + "="*60)
        logger.info("🗂️  演示2: 完善的上下文管理")
        logger.info("="*60)
        
        try:
            # 创建上下文
            context = UniversalContext({
                "user_id": "demo_user",
                "session_id": "demo_session_001",
                "language": "zh-CN"
            })
            
            logger.info("✅ 创建基础上下文")
            
            # 添加更多上下文信息
            context.set("current_task", "认知演示", {"priority": "high"})
            context.set("user_preferences", {"theme": "dark", "notifications": True})
            context.set("conversation_history", ["Hello", "你好", "How are you?"])
            
            logger.info(f"📝 上下文条目数: {len(context.keys())}")
            
            # 创建快照
            snapshot_id = context.create_snapshot("demo_snapshot")
            logger.info(f"📸 创建快照: {snapshot_id}")
            
            # 修改上下文
            context.set("current_task", "修改后的任务")
            context.set("new_data", "这是新添加的数据")
            
            # 按类型过滤
            string_data = context.filter_by_type(str)
            logger.info(f"📊 字符串类型数据: {len(string_data)}个")
            
            # 按前缀过滤
            user_data = context.filter_by_prefix("user_")
            logger.info(f"🔍 用户相关数据: {len(user_data)}个")
            
            # 获取最近变更
            recent_changes = context.get_recent_changes(minutes=1)
            logger.info(f"⏰ 最近变更: {len(recent_changes)}个")
            
            # 恢复快照
            if context.restore_snapshot(snapshot_id):
                logger.info("🔄 快照恢复成功")
            else:
                logger.info("❌ 快照恢复失败")
            
            # 内存使用情况
            memory_usage = context.get_memory_usage()
            logger.info(f"💾 内存使用: {memory_usage['estimated_total_size_bytes']}字节")
            
        except Exception as e:
            logger.error(f"❌ 上下文管理演示失败: {e}")
    
    async def _demo_enhanced_result_processing(self):
        """演示加强的结果处理"""
        logger.info("\n" + "="*60)
        logger.info("📊 演示3: 加强的结果处理")
        logger.info("="*60)
        
        try:
            # 创建第一个结果
            result1 = UniversalResult(
                content="人工智能是一个快速发展的领域，涉及机器学习、深度学习等技术。",
                status=ResultStatus.SUCCESS,
                result_type=ResultType.ANALYSIS
            )
            result1.set_confidence_score(0.8)
            result1.add_artifact({"type": "summary", "content": "AI技术概述"})
            result1.add_citation("https://example.com/ai-overview")
            
            # 创建第二个结果
            result2 = UniversalResult(
                content="机器学习算法可以从数据中学习模式，提高预测准确性。",
                status=ResultStatus.SUCCESS,
                result_type=ResultType.ANALYSIS
            )
            result2.set_confidence_score(0.75)
            result2.add_artifact({"type": "data", "content": "ML算法分析"})
            
            logger.info("✅ 创建了两个分析结果")
            
            # 验证结果
            validation1 = result1.validate()
            validation2 = result2.validate()
            
            if not validation1 and not validation2:
                logger.info("✅ 结果验证通过")
            
            # 计算质量分数
            quality1 = result1.get_quality_score()
            quality2 = result2.get_quality_score()
            
            logger.info(f"📈 结果1质量分数: {quality1:.3f}")
            logger.info(f"📈 结果2质量分数: {quality2:.3f}")
            
            # 检查置信度
            if result1.has_high_confidence():
                logger.info("✅ 结果1具有高置信度")
            
            # 合并结果
            merged_result = result1.merge_with(result2, strategy='combine')
            logger.info(f"🔄 合并结果质量分数: {merged_result.get_quality_score():.3f}")
            
            # 提取关键见解
            insights = merged_result.extract_key_insights()
            if insights:
                logger.info(f"💡 关键见解: {len(insights)}个")
                for insight in insights:
                    logger.info(f"   - {insight}")
            
            # 获取性能指标
            metrics = merged_result.get_performance_metrics()
            logger.info(f"📊 性能指标: 质量分数 {metrics['quality_score']:.3f}")
            
            # 创建摘要
            summary = merged_result.create_summary()
            logger.info(f"📋 结果摘要: 成功={summary['success']}, 内容长度={summary['content_length']}")
            
        except Exception as e:
            logger.error(f"❌ 结果处理演示失败: {e}")
    
    async def _demo_basic_perception(self):
        """演示基础感知模块"""
        logger.info("\n" + "="*60)
        logger.info("👁️  演示4: 基础感知模块")
        logger.info("="*60)
        
        try:
            # 文本感知
            text_data = "今天天气很好，我很开心！我正在学习人工智能相关的知识，包括机器学习和深度学习。"
            
            perception_result = await self.perception_engine.perceive(text_data)
            
            logger.info(f"✅ 文本感知完成")
            logger.info(f"📝 感知类型: {perception_result.perception_type.value}")
            logger.info(f"🎯 置信度: {perception_result.confidence:.3f}")
            
            if hasattr(perception_result, 'sentiment'):
                logger.info(f"😊 情感倾向: {perception_result.sentiment.value}")
                logger.info(f"📊 情感分数: {perception_result.sentiment_score:.3f}")
            
            if hasattr(perception_result, 'keywords'):
                logger.info(f"🔑 关键词: {', '.join(perception_result.keywords[:5])}")
            
            if hasattr(perception_result, 'entities'):
                logger.info(f"🏷️  实体数量: {len(perception_result.entities)}")
            
            # 结构化数据感知
            structured_data = {
                "user_info": {
                    "name": "张三",
                    "age": 25,
                    "interests": ["AI", "机器学习", "编程"]
                },
                "session_data": {
                    "start_time": "2024-01-15T10:00:00",
                    "actions": ["login", "browse", "search"]
                }
            }
            
            struct_result = await self.perception_engine.perceive(structured_data)
            logger.info(f"📊 结构化数据感知完成")
            logger.info(f"🗂️  数据类型: {struct_result.metadata.get('type', 'unknown')}")
            logger.info(f"🔢 键数量: {struct_result.metadata.get('key_count', 0)}")
            
            # 批量感知
            batch_data = [
                "这是第一条测试文本",
                {"test": "data", "value": 123},
                "This is an English text for testing"
            ]
            
            batch_results = await self.perception_engine.batch_perceive(batch_data)
            logger.info(f"📦 批量感知完成: {len(batch_results)}个结果")
            
            # 感知统计
            stats = self.perception_engine.get_perception_stats()
            logger.info(f"📈 感知统计: 总计{stats['total']}次，平均置信度{stats['average_confidence']:.3f}")
            
        except Exception as e:
            logger.error(f"❌ 感知模块演示失败: {e}")
    
    async def _demo_simple_reasoning(self):
        """演示简单推理能力"""
        logger.info("\n" + "="*60)
        logger.info("🤔 演示5: 简单推理能力")
        logger.info("="*60)
        
        try:
            # 逻辑推理
            logical_premises = [
                "如果天气晴朗，那么我们可以去公园。",
                "今天天气晴朗。",
                "因此我们可以去公园。"
            ]
            
            logical_result = await self.reasoning_engine.reason(logical_premises)
            logger.info(f"🧮 逻辑推理完成")
            logger.info(f"📝 结论: {logical_result.conclusion}")
            logger.info(f"🎯 置信度: {logical_result.confidence:.3f}")
            logger.info(f"📊 置信度等级: {logical_result.get_confidence_level().value}")
            
            # 因果推理
            causal_premises = [
                "因为下雨，所以地面湿润。",
                "由于交通拥堵，导致上班迟到。"
            ]
            
            causal_result = await self.reasoning_engine.reason(causal_premises)
            logger.info(f"🔗 因果推理完成")
            logger.info(f"📝 结论: {causal_result.conclusion}")
            logger.info(f"🎯 置信度: {causal_result.confidence:.3f}")
            
            # 类比推理
            analogy_premises = [
                "学习就像建造房屋，需要打好基础。",
                "编程就像写作，需要清晰的逻辑。"
            ]
            
            analogy_result = await self.reasoning_engine.reason(analogy_premises)
            logger.info(f"🔄 类比推理完成")
            logger.info(f"📝 结论: {analogy_result.conclusion}")
            logger.info(f"🎯 置信度: {analogy_result.confidence:.3f}")
            
            # 归纳推理
            inductive_premises = [
                "第一只天鹅是白色的。",
                "第二只天鹅是白色的。",
                "第三只天鹅是白色的。"
            ]
            
            inductive_result = await self.reasoning_engine.reason(inductive_premises)
            logger.info(f"📈 归纳推理完成")
            logger.info(f"📝 结论: {inductive_result.conclusion}")
            logger.info(f"🎯 置信度: {inductive_result.confidence:.3f}")
            
            # 多角度推理
            multi_premises = [
                "如果努力学习，那么会取得好成绩。",
                "因为努力学习，所以获得了奖学金。"
            ]
            
            multi_results = await self.reasoning_engine.multi_perspective_reasoning(multi_premises)
            logger.info(f"🔍 多角度推理完成: {len(multi_results)}个结果")
            
            for i, result in enumerate(multi_results, 1):
                logger.info(f"   结果{i}: {result.reasoning_type.value} - {result.confidence:.3f}")
            
            # 推理统计
            stats = self.reasoning_engine.get_reasoning_stats()
            logger.info(f"📊 推理统计: 总计{stats['total']}次推理")
            
        except Exception as e:
            logger.error(f"❌ 推理能力演示失败: {e}")
    
    async def _demo_enhanced_memory_management(self):
        """演示完善的记忆管理"""
        logger.info("\n" + "="*60)
        logger.info("🧠 演示6: 完善的记忆管理")
        logger.info("="*60)
        
        try:
            # 存储一些记忆
            from layers.cognitive.memory import MemoryType
            await self.memory_system.store_memory("今天学习了人工智能", MemoryType.EPISODIC, type="learning")
            await self.memory_system.store_memory("明天要参加会议", MemoryType.EPISODIC, type="schedule")
            await self.memory_system.store_memory("喜欢喝咖啡", MemoryType.SEMANTIC, type="preference")
            
            logger.info("✅ 存储了3条记忆")
            
            # 检索记忆
            ai_memories = await self.memory_system.retrieve_memory("人工智能", max_results=2)
            logger.info(f"🔍 检索到{len(ai_memories)}条相关记忆")
            
            # 创建记忆快照
            snapshot_id = await self.memory_system.create_memory_snapshot("demo_snapshot")
            logger.info(f"📸 创建记忆快照: {snapshot_id}")
            
            # 添加更多记忆
            await self.memory_system.store_memory("学习了深度学习算法", MemoryType.EPISODIC, type="learning")
            await self.memory_system.store_memory("完成了项目演示", MemoryType.EPISODIC, type="achievement")
            
            # 获取记忆统计
            stats = await self.memory_system.get_memory_stats()
            logger.info(f"📊 记忆统计:")
            logger.info(f"   工作记忆: {stats['working_memory']['active_items']}项")
            logger.info(f"   情景记忆: {stats['episodic_memory']['total_episodes']}个情景")
            logger.info(f"   语义记忆: {stats['semantic_memory']['total_concepts']}个概念")
            
            # 优化记忆
            optimization_results = await self.memory_system.optimize_memory()
            logger.info(f"🔧 记忆优化完成:")
            
            for memory_type, results in optimization_results.items():
                if results:
                    logger.info(f"   {memory_type}: 优化前{results.get('items_before', 0)} -> 优化后{results.get('items_after', 0)}")
            
            # 获取总记忆数量
            total_memories = await self.memory_system.get_total_memory_count()
            logger.info(f"🔢 总记忆数量: {total_memories}")
            
            # 获取内存使用估算
            memory_usage = await self.memory_system.get_memory_usage_estimate()
            total_mb = memory_usage['total_bytes'] / (1024 * 1024)
            logger.info(f"💾 内存使用估算: {total_mb:.2f}MB")
            
            # 导出记忆数据
            exported_data = await self.memory_system.export_memory_data()
            logger.info(f"📤 导出记忆数据: {len(exported_data)}字符")
            
            # 恢复快照
            if await self.memory_system.restore_memory_snapshot(snapshot_id):
                logger.info("🔄 记忆快照恢复成功")
            else:
                logger.info("❌ 记忆快照恢复失败")
            
            # 列出快照
            snapshots = self.memory_system.list_memory_snapshots()
            logger.info(f"📋 记忆快照列表: {len(snapshots)}个快照")
            
        except Exception as e:
            logger.error(f"❌ 记忆管理演示失败: {e}")


async def main():
    """主函数"""
    print("🧠 增强认知演示")
    print("=" * 80)
    print("本演示将验证以下增强功能：")
    print("1. 增强的框架抽象层：任务执行流程、上下文管理、结果处理")
    print("2. 深化的认知架构层：基础感知模块、简单推理能力、完善记忆管理")
    print("=" * 80)
    print()
    
    demo = EnhancedCognitiveDemo()
    
    try:
        # 初始化
        await demo.initialize()
        
        # 运行演示
        await demo.run_demo()
        
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        logger.error(f"❌ 演示运行失败: {e}")
        print(f"\n❌ 演示失败: {e}")
    finally:
        print("\n🎉 增强认知演示完成！")


if __name__ == "__main__":
    asyncio.run(main()) 