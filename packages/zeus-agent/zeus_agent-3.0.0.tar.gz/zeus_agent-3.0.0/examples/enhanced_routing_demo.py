#!/usr/bin/env python3
"""
增强路由系统演示
展示动态权重、用户画像、反馈学习、决策审计等高级功能

演示内容：
1. 用户画像对路由决策的影响
2. 对话上下文的连续性
3. 动态权重调整
4. 反馈学习循环
5. 决策审计日志
6. 降级策略
7. 不同路由器类型对比
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from layers.intelligent_context.enhanced_knowledge_router import (
    EnhancedKnowledgeRouter, UserProfile, UserRole, ConversationContext, 
    ContextType, RoutingFeedback, FeedbackType, RouterFactory
)


async def demo_user_profiling_impact():
    """演示用户画像对路由决策的影响"""
    print("👤 用户画像影响演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    # 创建不同角色的用户画像
    beginner_user = UserProfile(
        user_id="beginner_001",
        role=UserRole.BEGINNER,
        expertise_domains=["basic_electronics"],
        preferred_detail_level="low",
        cost_sensitivity=0.8,
        speed_preference=0.9
    )
    
    expert_user = UserProfile(
        user_id="expert_001", 
        role=UserRole.EXPERT,
        expertise_domains=["fpga_design", "verilog", "timing_analysis"],
        preferred_detail_level="high",
        cost_sensitivity=0.2,
        speed_preference=0.3
    )
    
    researcher_user = UserProfile(
        user_id="researcher_001",
        role=UserRole.RESEARCHER,
        expertise_domains=["fpga_architecture", "optimization"],
        preferred_detail_level="high",
        cost_sensitivity=0.1,
        speed_preference=0.2
    )
    
    # 同一个查询，不同用户画像
    query = "如何优化FPGA设计的时序性能？"
    print(f"🔍 测试查询: {query}")
    
    users = [
        ("初学者", beginner_user),
        ("专家", expert_user), 
        ("研究者", researcher_user)
    ]
    
    for user_type, user_profile in users:
        print(f"\n--- {user_type}用户 ---")
        decision = await router.route_query(query, user_profile=user_profile)
        
        print(f"   路由结果: {decision.primary_source.value}")
        print(f"   置信度: {decision.confidence:.3f}")
        print(f"   成本: {decision.estimated_cost:.2f}")
        print(f"   延迟: {decision.expected_latency:.1f}s")
        print(f"   推理: {decision.reasoning[:80]}...")


async def demo_context_awareness():
    """演示对话上下文感知"""
    print("\n💬 对话上下文感知演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    expert_user = UserProfile(
        user_id="expert_002",
        role=UserRole.EXPERT
    )
    
    # 模拟一个对话会话
    context = ConversationContext(
        conversation_id="conv_001",
        context_type=ContextType.STANDALONE
    )
    
    queries = [
        ("什么是FPGA状态机？", ContextType.STANDALONE),
        ("状态机的最佳实践有哪些？", ContextType.FOLLOW_UP),
        ("如何调试状态机的时序问题？", ContextType.DEEP_DIVE),
        ("我的状态机不工作，怎么排查？", ContextType.TROUBLESHOOTING)
    ]
    
    print("🔄 模拟对话流程:")
    
    for i, (query, ctx_type) in enumerate(queries, 1):
        context.context_type = ctx_type
        context.previous_queries.append(query)
        
        print(f"\n{i}. {ctx_type.value}: {query}")
        
        decision = await router.route_query(
            query, 
            user_profile=expert_user, 
            context=context
        )
        
        context.previous_decisions.append(decision)
        
        print(f"   路由: {decision.primary_source.value} (置信度: {decision.confidence:.3f})")
        print(f"   推理: {decision.reasoning[:60]}...")


async def demo_dynamic_weights():
    """演示动态权重调整"""
    print("\n⚖️ 动态权重调整演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    # 不同偏好的用户
    cost_sensitive_user = UserProfile(
        user_id="cost_user",
        role=UserRole.INTERMEDIATE,
        cost_sensitivity=0.9,  # 非常在意成本
        speed_preference=0.8   # 也很在意速度
    )
    
    quality_focused_user = UserProfile(
        user_id="quality_user", 
        role=UserRole.EXPERT,
        cost_sensitivity=0.1,  # 不在意成本
        speed_preference=0.2   # 不在意速度
    )
    
    query = "设计一个高性能的FPGA乘法器"
    
    print(f"🔍 测试查询: {query}")
    
    users = [
        ("成本敏感用户", cost_sensitive_user),
        ("质量优先用户", quality_focused_user)
    ]
    
    for user_type, user_profile in users:
        print(f"\n--- {user_type} ---")
        
        # 计算该用户的动态权重
        weights = await router._calculate_dynamic_weights(
            user_profile, None, await router._basic_query_analysis(query)
        )
        
        print("   动态权重:")
        for key, weight in weights.items():
            print(f"     {key}: {weight:.3f}")
        
        decision = await router.route_query(query, user_profile=user_profile)
        print(f"   最终决策: {decision.primary_source.value} (成本: {decision.estimated_cost:.2f})")


async def demo_feedback_learning():
    """演示反馈学习循环"""
    print("\n🧠 反馈学习演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    print("📊 学习前的权重:")
    for key, weight in router.learned_weights.items():
        print(f"   {key}: {weight:.3f}")
    
    # 模拟一系列用户反馈
    feedbacks = [
        RoutingFeedback("decision_001", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_002", FeedbackType.THUMBS_DOWN),
        RoutingFeedback("decision_003", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_004", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_005", FeedbackType.THUMBS_DOWN),
        RoutingFeedback("decision_006", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_007", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_008", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_009", FeedbackType.THUMBS_UP),
        RoutingFeedback("decision_010", FeedbackType.THUMBS_UP),  # 触发学习
    ]
    
    print(f"\n📝 模拟 {len(feedbacks)} 个用户反馈...")
    
    for feedback in feedbacks:
        await router.add_feedback(feedback)
    
    print("\n📊 学习后的权重:")
    for key, weight in router.learned_weights.items():
        print(f"   {key}: {weight:.3f}")
    
    # 测试学习效果
    query = "FPGA时钟域交叉设计"
    decision_before = await router.route_query(query)
    print(f"\n🎯 学习后的决策: {decision_before.primary_source.value} (置信度: {decision_before.confidence:.3f})")


async def demo_decision_audit():
    """演示决策审计日志"""
    print("\n📊 决策审计日志演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    user = UserProfile(
        user_id="audit_user",
        role=UserRole.INTERMEDIATE
    )
    
    # 执行几个查询生成审计日志
    queries = [
        "什么是FPGA？",
        "如何设计状态机？",
        "Verilog语法错误怎么调试？"
    ]
    
    print("🔍 执行查询并记录审计日志:")
    
    for query in queries:
        decision = await router.route_query(query, user_profile=user)
        print(f"   查询: {query[:30]}... → {decision.primary_source.value}")
    
    print(f"\n📋 审计日志统计:")
    print(f"   总决策数: {len(router.audit_logs)}")
    print(f"   成功决策: {sum(1 for log in router.audit_logs if log.success)}")
    print(f"   平均执行时间: {sum(log.execution_time_ms for log in router.audit_logs) / len(router.audit_logs):.2f}ms")
    
    # 显示最近的审计日志
    if router.audit_logs:
        latest_log = router.audit_logs[-1]
        print(f"\n📄 最新审计日志:")
        print(f"   ID: {latest_log.log_id}")
        print(f"   时间: {latest_log.timestamp.strftime('%H:%M:%S')}")
        print(f"   用户: {latest_log.user_id}")
        print(f"   查询: {latest_log.query}")
        print(f"   决策: {latest_log.final_decision.primary_source.value}")
        print(f"   执行时间: {latest_log.execution_time_ms:.2f}ms")


async def demo_fallback_strategies():
    """演示降级策略"""
    print("\n🛡️ 降级策略演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    # 模拟不同类型的错误
    error_scenarios = [
        ("knowledge_base_error", "知识库服务不可用"),
        ("web_search_timeout", "网络搜索超时"),
        ("unknown_error", "未知系统错误")
    ]
    
    print("🚨 模拟系统故障场景:")
    
    for error_type, error_msg in error_scenarios:
        print(f"\n--- {error_msg} ---")
        
        fallback_decision = await router._execute_fallback_strategy(
            "FPGA设计问题", None, None, error_msg
        )
        
        print(f"   降级决策: {fallback_decision.primary_source.value}")
        print(f"   推理: {fallback_decision.reasoning}")
        print(f"   置信度: {fallback_decision.confidence:.2f}")


async def demo_router_comparison():
    """演示不同路由器类型对比"""
    print("\n🔄 路由器类型对比演示")
    print("=" * 50)
    
    # 创建不同类型的路由器
    routers = {
        "增强路由器": RouterFactory.create_router("enhanced"),
        "成本优先路由器": RouterFactory.create_router("cost_first"),
        "ML路由器": RouterFactory.create_router("ml_based")
    }
    
    query = "如何优化FPGA功耗？"
    user = UserProfile(user_id="compare_user", role=UserRole.EXPERT)
    
    print(f"🔍 测试查询: {query}")
    print("\n📊 不同路由器的决策对比:")
    
    for router_name, router in routers.items():
        print(f"\n--- {router_name} ---")
        
        try:
            decision = await router.route_query(query, user_profile=user)
            print(f"   决策: {decision.primary_source.value}")
            print(f"   置信度: {decision.confidence:.3f}")
            print(f"   成本: {decision.estimated_cost:.2f}")
            print(f"   推理: {decision.reasoning[:50]}...")
        except Exception as e:
            print(f"   ❌ 路由失败: {e}")
        
        # 显示路由器信息
        info = router.get_router_info()
        print(f"   类型: {info['router_type']} v{info['version']}")


async def demo_cost_budget_control():
    """演示成本预算控制"""
    print("\n💰 成本预算控制演示")
    print("=" * 50)
    
    router = EnhancedKnowledgeRouter()
    
    # 模拟高成本敏感用户
    budget_user = UserProfile(
        user_id="budget_user",
        role=UserRole.INTERMEDIATE,
        cost_sensitivity=0.95  # 极度成本敏感
    )
    
    context = ConversationContext(
        conversation_id="budget_session",
        session_cost_used=8.5  # 已使用8.5，接近每日预算10.0
    )
    
    queries = [
        "简单概念查询：什么是FPGA？",
        "复杂创造性任务：设计一个完整的UART控制器",
        "最新信息查询：2024年最新FPGA技术趋势"
    ]
    
    print("💳 预算状态:")
    print(f"   每日预算: {router.cost_budget['daily_limit']}")
    print(f"   已使用: {context.session_cost_used}")
    print(f"   剩余: {router.cost_budget['daily_limit'] - context.session_cost_used}")
    print(f"   紧急阈值: {router.cost_budget['emergency_threshold'] * 100}%")
    
    print(f"\n🔍 预算控制下的路由决策:")
    
    for query in queries:
        print(f"\n查询: {query}")
        
        decision = await router.route_query(
            query.split("：")[1], 
            user_profile=budget_user, 
            context=context
        )
        
        print(f"   路由: {decision.primary_source.value}")
        print(f"   成本: {decision.estimated_cost:.2f}")
        print(f"   推理: {decision.reasoning[:60]}...")
        
        # 更新会话成本
        context.session_cost_used += decision.estimated_cost


async def main():
    """主演示函数"""
    print("🚀 增强路由系统完整演示")
    print("展示动态权重、用户画像、反馈学习等高级功能")
    print("=" * 60)
    
    # 1. 用户画像影响
    await demo_user_profiling_impact()
    
    # 2. 对话上下文感知
    await demo_context_awareness()
    
    # 3. 动态权重调整
    await demo_dynamic_weights()
    
    # 4. 反馈学习
    await demo_feedback_learning()
    
    # 5. 决策审计
    await demo_decision_audit()
    
    # 6. 降级策略
    await demo_fallback_strategies()
    
    # 7. 路由器对比
    await demo_router_comparison()
    
    # 8. 成本预算控制
    await demo_cost_budget_control()
    
    print("\n🎉 增强路由演示完成!")
    
    print("\n💡 增强功能总结:")
    print("   ✅ 用户画像感知 - 不同角色获得个性化路由")
    print("   ✅ 动态权重调整 - 根据用户偏好和上下文调整")
    print("   ✅ 对话上下文连续性 - 保持会话一致性")
    print("   ✅ 反馈学习循环 - 系统越用越聪明")
    print("   ✅ 决策审计日志 - 完整的可观测性")
    print("   ✅ 降级策略 - 故障时的优雅处理")
    print("   ✅ 成本预算控制 - 智能成本管理")
    print("   ✅ 多路由器策略 - 灵活的策略选择")
    
    print("\n🚀 这些增强功能让我们的RAG系统:")
    print("   1. 更智能 - 基于用户和上下文的个性化决策")
    print("   2. 更可靠 - 故障转移和降级策略")
    print("   3. 更可观测 - 完整的决策审计和监控")
    print("   4. 更可优化 - 反馈学习持续改进")
    print("   5. 更经济 - 智能成本控制和预算管理")
    
    print("\n🎊 这就是行业标杆级的智能路由系统！")


if __name__ == "__main__":
    asyncio.run(main()) 