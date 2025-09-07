#!/usr/bin/env python3
"""
Cognitive Agent Demo - 认知Agent演示
展示完整的认知架构功能：感知、推理、记忆、学习、通信
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from layers.cognitive.cognitive_agent import CognitiveAgent, AgentIdentity
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext, ContextEntry
from layers.cognitive.learning import Skill


async def create_demo_agent() -> CognitiveAgent:
    """创建演示用的认知Agent"""
    
    # 创建Agent身份
    identity = AgentIdentity(
        agent_id="demo_cognitive_agent_001",
        name="Demo Cognitive Agent",
        role="AI Assistant",
        description="A demonstration of cognitive architecture capabilities",
        goals=[
            "Help users solve problems",
            "Learn from interactions", 
            "Provide intelligent responses"
        ],
        values=["helpfulness", "accuracy", "continuous_learning"],
        personality_traits={
            "curiosity": 0.8,
            "patience": 0.9,
            "creativity": 0.7,
            "analytical": 0.85
        },
        expertise_domains=["problem_solving", "analysis", "communication"]
    )
    
    # 创建配置
    config = {
        "perception": {
            "text": {"enable_sentiment": True},
            "context": {"max_entries": 50},
            "intent": {"confidence_threshold": 0.6}
        },
        "reasoning": {
            "logical": {"enable_consistency_check": True},
            "causal": {"max_depth": 3},
            "planning": {"max_steps": 10}
        },
        "memory": {
            "working": {"capacity": 7, "decay_time": 300},
            "episodic": {"max_episodes": 1000},
            "semantic": {"max_concepts": 500},
            "consolidation": {"consolidation_threshold": 0.7}
        },
        "learning": {
            "supervised": {"learning_rate": 0.1},
            "reinforcement": {"epsilon": 0.1, "discount_factor": 0.9},
            "experience_buffer": {"capacity": 1000}
        },
        "communication": {
            "message_bus": {"queue": {"max_size": 1000}},
            "team_protocol": {"default_timeout": 300}
        }
    }
    
    # 创建认知Agent
    agent = CognitiveAgent(identity, config)
    
    return agent


async def demo_basic_cognitive_flow():
    """演示基本认知流程"""
    print("\n" + "="*60)
    print("🧠 认知Agent基本流程演示")
    print("="*60)
    
    # 创建Agent
    agent = await create_demo_agent()
    
    try:
        # 初始化Agent
        print("\n📋 正在初始化认知Agent...")
        await agent.initialize()
        print(f"✅ Agent '{agent.identity.name}' 初始化完成")
        
        # 创建测试任务
        task = UniversalTask(
            content="分析人工智能在医疗领域的应用前景，并提出三个具体的应用场景建议",
            task_type=TaskType.ANALYSIS,
            priority=1,
            metadata={"domain": "healthcare", "complexity": "high"}
        )
        
        # 创建上下文
        context = UniversalContext()
        context.set("user_expertise", "intermediate", {"confidence": 0.8})
        context.set("domain_focus", "healthcare_ai", {"importance": 0.9})
        context.set("output_format", "structured_analysis", {"preference": "detailed"})
        
        print(f"\n🎯 执行任务: {task.content[:50]}...")
        
        # 执行任务
        result = await agent.execute(task, context)
        
        print(f"\n📊 执行结果:")
        print(f"状态: {result.status.value}")
        print(f"内容: {result.content}")
        print(f"执行时间: {result.metadata.get('execution_time', 0):.2f}秒")
        print(f"感知置信度: {result.metadata.get('perception_confidence', 0):.2f}")
        print(f"推理置信度: {result.metadata.get('reasoning_confidence', 0):.2f}")
        
        # 显示Agent状态
        status_info = agent.get_status_info()
        print(f"\n🤖 Agent状态:")
        print(f"认知状态: {status_info['cognitive_state']}")
        print(f"整体性能: {status_info['cognitive_metrics']['overall_performance']:.2f}")
        print(f"记忆效率: {status_info['cognitive_metrics']['memory_efficiency']:.2f}")
        print(f"学习进度: {status_info['cognitive_metrics']['learning_progress']:.2f}")
        
    finally:
        # 关闭Agent
        await agent.shutdown()
        print("\n🔚 Agent已关闭")


async def demo_memory_system():
    """演示记忆系统"""
    print("\n" + "="*60)
    print("🧠 记忆系统演示")
    print("="*60)
    
    agent = await create_demo_agent()
    
    try:
        await agent.initialize()
        
        # 存储不同类型的记忆
        print("\n📝 存储记忆...")
        
        # 工作记忆
        await agent.memory_system.store_memory(
            content="用户询问关于机器学习的问题",
            memory_type=agent.memory_system.working_memory.__class__.__name__.replace('Manager', '').lower(),
            importance=0.7
        )
        
        # 情景记忆
        await agent.memory_system.store_memory(
            content="与用户讨论AI应用",
            memory_type="episodic",
            event="用户对话",
            participants=["user_001", agent.identity.agent_id],
            importance=0.8
        )
        
        # 语义记忆
        await agent.memory_system.store_memory(
            content="人工智能是计算机科学的一个分支",
            memory_type="semantic",
            concept="人工智能",
            definition="模拟人类智能的计算机系统",
            confidence=0.95
        )
        
        # 程序记忆
        await agent.memory_system.store_memory(
            content="问题解决流程",
            memory_type="procedural",
            name="问题解决",
            description="系统性解决问题的步骤",
            steps=[
                {"step": 1, "action": "理解问题"},
                {"step": 2, "action": "分析问题"},
                {"step": 3, "action": "生成方案"},
                {"step": 4, "action": "评估方案"},
                {"step": 5, "action": "实施方案"}
            ]
        )
        
        print("✅ 记忆存储完成")
        
        # 检索记忆
        print("\n🔍 检索记忆...")
        memory_results = await agent.memory_system.retrieve_memory("人工智能")
        
        for memory_type, memories in memory_results.items():
            print(f"\n{memory_type.upper()} 记忆:")
            for i, memory in enumerate(memories[:2]):  # 显示前2个结果
                if hasattr(memory, 'content'):
                    print(f"  {i+1}. {str(memory.content)[:100]}...")
                elif hasattr(memory, 'concept'):
                    print(f"  {i+1}. 概念: {memory.concept}")
                elif hasattr(memory, 'event'):
                    print(f"  {i+1}. 事件: {memory.event}")
                elif hasattr(memory, 'name'):
                    print(f"  {i+1}. 程序: {memory.name}")
        
        # 获取记忆统计
        memory_stats = await agent.memory_system.get_memory_statistics()
        print(f"\n📊 记忆统计:")
        print(f"工作记忆: {memory_stats['working_memory']['active_items']}/{memory_stats['working_memory']['capacity']}")
        print(f"情景记忆: {memory_stats['episodic_memory']['total_episodes']}")
        print(f"语义记忆: {memory_stats['semantic_memory']['total_concepts']}")
        print(f"程序记忆: {memory_stats['procedural_memory']['total_procedures']}")
        
    finally:
        await agent.shutdown()


async def demo_learning_system():
    """演示学习系统"""
    print("\n" + "="*60)
    print("🎓 学习系统演示")
    print("="*60)
    
    agent = await create_demo_agent()
    
    try:
        await agent.initialize()
        
        # 添加技能
        print("\n🛠️ 添加技能...")
        
        skills = [
            Skill(
                skill_id="data_analysis",
                name="数据分析",
                description="分析和解释数据的能力",
                proficiency_level=0.6
            ),
            Skill(
                skill_id="creative_writing",
                name="创意写作", 
                description="创作有创意的文本内容",
                proficiency_level=0.4
            ),
            Skill(
                skill_id="logical_reasoning",
                name="逻辑推理",
                description="进行逻辑思维和推理",
                proficiency_level=0.7
            )
        ]
        
        for skill in skills:
            agent.learning_module.add_skill(skill)
            print(f"  ✅ 添加技能: {skill.name} (熟练度: {skill.proficiency_level:.1f})")
        
        # 练习技能
        print("\n💪 练习技能...")
        
        practice_sessions = [
            ("data_analysis", {"success": True, "quality": 0.8}),
            ("data_analysis", {"success": True, "quality": 0.9}),
            ("creative_writing", {"success": False, "quality": 0.3}),
            ("creative_writing", {"success": True, "quality": 0.6}),
            ("logical_reasoning", {"success": True, "quality": 0.95})
        ]
        
        for skill_id, practice_data in practice_sessions:
            result = await agent.learning_module.practice_skill(skill_id, practice_data)
            if result.get("success"):
                print(f"  📈 {skill_id}: 熟练度 {result['new_proficiency']:.2f} (+{result['proficiency_gain']:.3f})")
            else:
                print(f"  ❌ {skill_id}: 练习失败 - {result.get('error', '未知错误')}")
        
        # 获取学习建议
        print("\n💡 学习建议:")
        recommendations = agent.learning_module.get_learning_recommendations()
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['type']}: {rec.get('skill_name', rec.get('skill_id', '未知'))}")
            if 'progress_needed' in rec:
                print(f"     需要提升: {rec['progress_needed']:.2f}")
            if 'estimated_sessions' in rec:
                print(f"     预估练习: {rec['estimated_sessions']} 次")
        
        # 获取学习统计
        learning_stats = agent.learning_module.get_learning_statistics()
        skill_stats = learning_stats['skill_acquisition']
        
        print(f"\n📊 学习统计:")
        print(f"总技能数: {skill_stats['total_skills']}")
        print(f"平均熟练度: {skill_stats['average_proficiency']:.2f}")
        print(f"练习次数: {skill_stats['total_practice_sessions']}")
        print(f"技能分布: {skill_stats['skills_by_proficiency']}")
        
    finally:
        await agent.shutdown()


async def demo_communication_system():
    """演示通信系统"""
    print("\n" + "="*60)
    print("💬 通信系统演示")
    print("="*60)
    
    # 创建两个Agent进行通信演示
    agent1 = await create_demo_agent()
    agent1.identity.agent_id = "agent_001"
    agent1.identity.name = "Alice"
    
    agent2 = await create_demo_agent()
    agent2.identity.agent_id = "agent_002"
    agent2.identity.name = "Bob"
    
    try:
        await agent1.initialize()
        await agent2.initialize()
        
        print(f"✅ 初始化完成: {agent1.identity.name} 和 {agent2.identity.name}")
        
        # 发送点对点消息
        print("\n📤 发送点对点消息...")
        success = await agent1.communication_manager.send_message(
            sender_id=agent1.identity.agent_id,
            receiver_id=agent2.identity.agent_id,
            content="你好，Bob！我是Alice，很高兴认识你。",
            message_type="greeting"
        )
        
        if success:
            print("  ✅ 消息发送成功")
        else:
            print("  ❌ 消息发送失败")
        
        # 创建通信通道
        print("\n🔗 创建通信通道...")
        channel_id = await agent1.communication_manager.create_communication_channel(
            channel_name="AI协作讨论",
            participants=[agent1.identity.agent_id, agent2.identity.agent_id],
            description="AI Agent之间的协作讨论通道"
        )
        print(f"  ✅ 通道创建成功: {channel_id}")
        
        # 主题订阅
        print("\n📡 主题订阅...")
        topic = "ai_research"
        
        await agent1.communication_manager.subscribe_to_topic(agent1.identity.agent_id, topic)
        await agent2.communication_manager.subscribe_to_topic(agent2.identity.agent_id, topic)
        
        print(f"  ✅ 两个Agent都订阅了主题: {topic}")
        
        # 发布到主题
        print("\n📢 发布主题消息...")
        await agent1.communication_manager.publish_to_topic(
            sender_id=agent1.identity.agent_id,
            topic=topic,
            content={
                "title": "AI研究进展分享",
                "content": "最新的认知架构研究表明，多模态感知能力对AI系统的智能水平有重要影响。",
                "tags": ["认知架构", "多模态", "AI研究"]
            }
        )
        print("  ✅ 主题消息发布成功")
        
        # 获取通信统计
        print("\n📊 通信统计:")
        comm_stats = agent1.communication_manager.get_communication_statistics()
        
        print(f"点对点消息: {comm_stats['communication_stats'].get('point_to_point_messages', 0)}")
        print(f"广播消息: {comm_stats['communication_stats'].get('broadcast_messages', 0)}")
        print(f"主题消息: {comm_stats['communication_stats'].get('topic_messages', 0)}")
        print(f"创建通道: {comm_stats['communication_stats'].get('created_channels', 0)}")
        print(f"订阅数: {comm_stats['communication_stats'].get('subscriptions', 0)}")
        
        # 短暂等待处理消息
        await asyncio.sleep(1)
        
    finally:
        await agent1.shutdown()
        await agent2.shutdown()


async def demo_complete_cognitive_scenario():
    """演示完整认知场景"""
    print("\n" + "="*60)
    print("🎭 完整认知场景演示")
    print("="*60)
    
    agent = await create_demo_agent()
    
    try:
        await agent.initialize()
        
        # 场景：用户咨询AI助手关于学习编程的建议
        print("\n📝 场景: 用户咨询编程学习建议")
        
        # 第一轮对话
        task1 = UniversalTask(
            content="我是一个编程初学者，想学习Python，但不知道从哪里开始，能给我一些建议吗？",
            task_type=TaskType.CONSULTATION,
            metadata={"user_level": "beginner", "topic": "programming"}
        )
        
        context1 = UniversalContext()
        context1.set("user_background", "编程初学者", {"confidence": 0.9})
        context1.set("learning_goal", "Python编程", {"priority": "high"})
        
        print("\n🤖 Agent处理第一个咨询...")
        result1 = await agent.execute(task1, context1)
        print(f"回复: {result1.content}")
        
        # 模拟用户反馈和第二轮对话
        await asyncio.sleep(1)
        
        task2 = UniversalTask(
            content="谢谢你的建议！我对数据科学特别感兴趣，Python在这方面有什么优势吗？",
            task_type=TaskType.ANALYSIS,
            metadata={"follow_up": True, "interest": "data_science"}
        )
        
        context2 = UniversalContext()
        context2.set("previous_topic", "Python学习", {"relevance": 0.8})
        context2.set("user_interest", "数据科学", {"confidence": 0.9})
        context2.set("conversation_context", result1.content, {"importance": 0.7})
        
        print("\n🤖 Agent处理第二个咨询...")
        result2 = await agent.execute(task2, context2)
        print(f"回复: {result2.content}")
        
        # 展示Agent的学习和记忆
        print("\n🧠 Agent的学习和记忆状况:")
        
        # 检索相关记忆
        memory_results = await agent.memory_system.retrieve_memory("Python编程")
        print(f"相关记忆数量: {sum(len(memories) for memories in memory_results.values())}")
        
        # 显示认知指标变化
        status_info = agent.get_status_info()
        metrics = status_info['cognitive_metrics']
        
        print(f"整体性能: {metrics['overall_performance']:.2f}")
        print(f"记忆效率: {metrics['memory_efficiency']:.2f}")
        print(f"学习进度: {metrics['learning_progress']:.2f}")
        print(f"通信效果: {metrics['communication_effectiveness']:.2f}")
        
        # 显示执行历史
        execution_history = status_info['execution_history']
        print(f"\n📈 执行历史: 总共 {execution_history['total_executions']} 次执行")
        
        for i, execution in enumerate(execution_history['recent_executions'], 1):
            print(f"  {i}. {execution['task_content']} ({'成功' if execution['success'] else '失败'})")
        
    finally:
        await agent.shutdown()


async def main():
    """主演示函数"""
    print("🚀 认知Agent演示程序启动")
    print("这个演示将展示完整的认知架构功能")
    
    demos = [
        ("基本认知流程", demo_basic_cognitive_flow),
        ("记忆系统", demo_memory_system), 
        ("学习系统", demo_learning_system),
        ("通信系统", demo_communication_system),
        ("完整认知场景", demo_complete_cognitive_scenario)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎯 开始演示: {demo_name}")
            await demo_func()
            print(f"✅ {demo_name} 演示完成")
        except Exception as e:
            print(f"❌ {demo_name} 演示出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 演示间隔
        await asyncio.sleep(1)
    
    print("\n🎉 所有演示完成！")
    print("\n📋 演示总结:")
    print("- ✅ 感知引擎: 多模态输入处理、意图识别、实体提取")
    print("- ✅ 推理引擎: 逻辑推理、因果推理、决策制定、规划")
    print("- ✅ 记忆系统: 工作记忆、情景记忆、语义记忆、程序记忆")
    print("- ✅ 学习模块: 技能习得、经验积累、模式识别")
    print("- ✅ 通信系统: 消息传递、主题订阅、团队协作")
    print("- ✅ 认知Agent: 完整的认知流程整合")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main()) 