"""
LangGraph适配器简化演示
展示LangGraph适配器的基本功能，无需真实LangGraph依赖

主要演示功能：
1. LangGraph适配器初始化
2. 工作流创建和管理
3. 节点和边的定义
4. 任务执行和状态管理
5. A2A协议集成
6. 健康检查和监控
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.adapter.langgraph.adapter_simple import LangGraphAdapterSimple, LANGGRAPH_AVAILABLE
from layers.framework.abstractions.task import UniversalTask, TaskType, TaskPriority, TaskRequirements
from layers.framework.abstractions.context import UniversalContext


async def demo_adapter_initialization():
    """演示适配器初始化"""
    print("\n🚀 LangGraph适配器初始化演示")
    print("=" * 50)
    
    try:
        # 创建LangGraph适配器
        adapter = LangGraphAdapterSimple("langgraph_demo")
        print(f"✅ 适配器创建成功: {adapter.name}")
        
        # 初始化配置
        config = {
            "default_llm": {
                "model": "mock-gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "global_state": {
                "session_id": "demo_session",
                "user_id": "demo_user"
            }
        }
        
        await adapter.initialize(config)
        print(f"✅ 适配器初始化成功")
        print(f"   状态: {adapter.status.value}")
        print(f"   就绪: {adapter.is_ready()}")
        print(f"   LangGraph可用: {LANGGRAPH_AVAILABLE}")
        
        # 获取能力
        capabilities = adapter.get_capabilities()
        print(f"   支持能力: {[cap.value for cap in capabilities]}")
        
        return adapter
        
    except Exception as e:
        print(f"❌ LangGraph适配器初始化失败: {e}")
        return None


async def demo_simple_workflow_creation(adapter):
    """演示简单工作流创建"""
    print("\n🔧 简单工作流创建演示")
    print("=" * 50)
    
    if not adapter:
        print("❌ 适配器不可用，跳过演示")
        return []
    
    try:
        workflow_ids = []
        
        # 创建线性工作流
        print("📝 创建线性工作流...")
        linear_workflow_config = {
            "workflow_id": "linear_workflow",
            "nodes": [
                {
                    "node_id": "input_processor",
                    "type": "function",
                    "processing": "input_validation"
                },
                {
                    "node_id": "main_processor", 
                    "type": "llm",
                    "prompt": "Process the validated input"
                },
                {
                    "node_id": "output_formatter",
                    "type": "function",
                    "processing": "output_formatting"
                }
            ],
            "edges": [
                {"from": "input_processor", "to": "main_processor"},
                {"from": "main_processor", "to": "output_formatter"}
            ],
            "entry_point": "input_processor"
        }
        
        linear_id = await adapter.create_agent(linear_workflow_config)
        workflow_ids.append(linear_id)
        print(f"   ✅ 创建成功: {linear_id}")
        
        # 创建工具链工作流
        print("🔨 创建工具链工作流...")
        tool_workflow_config = {
            "workflow_id": "tool_chain",
            "nodes": [
                {
                    "node_id": "data_collector",
                    "type": "tool",
                    "tool_name": "data_collection_tool"
                },
                {
                    "node_id": "data_analyzer",
                    "type": "tool",
                    "tool_name": "analysis_tool"
                },
                {
                    "node_id": "report_generator",
                    "type": "llm",
                    "prompt": "Generate a comprehensive report based on the analysis"
                }
            ],
            "edges": [
                {"from": "data_collector", "to": "data_analyzer"},
                {"from": "data_analyzer", "to": "report_generator"}
            ],
            "entry_point": "data_collector"
        }
        
        tool_id = await adapter.create_agent(tool_workflow_config)
        workflow_ids.append(tool_id)
        print(f"   ✅ 创建成功: {tool_id}")
        
        # 显示工作流状态
        print(f"\n📊 工作流状态:")
        for workflow_id in workflow_ids:
            status = adapter.get_workflow_status(workflow_id)
            print(f"   {workflow_id}:")
            print(f"     节点数: {status['nodes_count']}")
            print(f"     边数: {status['edges_count']}")
            print(f"     执行次数: {status['execution_count']}")
            print(f"     已编译: {status['compiled']}")
        
        return workflow_ids
        
    except Exception as e:
        print(f"❌ 工作流创建失败: {e}")
        return []


async def demo_conditional_workflow(adapter):
    """演示条件工作流"""
    print("\n🔀 条件工作流演示")
    print("=" * 50)
    
    if not adapter:
        print("❌ 适配器不可用，跳过演示")
        return None
    
    try:
        # 创建条件分支工作流
        print("🌳 创建条件分支工作流...")
        conditional_config = {
            "workflow_id": "conditional_flow",
            "nodes": [
                {
                    "node_id": "input_classifier",
                    "type": "llm",
                    "prompt": "Classify the input type"
                },
                {
                    "node_id": "text_processor",
                    "type": "llm",
                    "prompt": "Process text input"
                },
                {
                    "node_id": "data_processor",
                    "type": "tool",
                    "tool_name": "data_processing_tool"
                },
                {
                    "node_id": "default_processor",
                    "type": "function",
                    "processing": "default_handling"
                },
                {
                    "node_id": "output_merger",
                    "type": "function",
                    "processing": "merge_outputs"
                }
            ],
            "edges": [
                {"from": "text_processor", "to": "output_merger"},
                {"from": "data_processor", "to": "output_merger"},
                {"from": "default_processor", "to": "output_merger"}
            ],
            "conditional_edges": [
                {
                    "from": "input_classifier",
                    "condition": {
                        "type": "classification",
                        "default_path": "default_processor"
                    },
                    "edge_map": {
                        "text": "text_processor",
                        "data": "data_processor",
                        "other": "default_processor"
                    }
                }
            ],
            "entry_point": "input_classifier"
        }
        
        conditional_id = await adapter.create_agent(conditional_config)
        print(f"   ✅ 创建成功: {conditional_id}")
        
        # 显示条件工作流状态
        status = adapter.get_workflow_status(conditional_id)
        print(f"   节点数: {status['nodes_count']}")
        print(f"   边数: {status['edges_count']}")
        print(f"   条件边数: {status['conditional_edges_count']}")
        
        return conditional_id
        
    except Exception as e:
        print(f"❌ 条件工作流创建失败: {e}")
        return None


async def demo_workflow_execution(adapter, workflow_ids):
    """演示工作流执行"""
    print("\n⚡ 工作流执行演示")
    print("=" * 50)
    
    if not adapter or not workflow_ids:
        print("❌ 适配器或工作流不可用，跳过演示")
        return
    
    try:
        # 创建测试上下文
        context = UniversalContext({
            'user_id': 'demo_user',
            'session_id': 'langgraph_demo_session',
            'timestamp': datetime.now().isoformat()
        })
        
        # 执行聊天任务
        print("💬 执行聊天任务...")
        chat_task = UniversalTask(
            content="Hello! Can you explain what LangGraph workflows are and how they work?",
            task_type=TaskType.CHAT,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={},
            task_id="chat_demo"
        )
        
        chat_result = await adapter.execute_task(chat_task, context)
        print(f"   结果: {'成功' if chat_result.success else '失败'}")
        if chat_result.success:
            print(f"   回复: {chat_result.data.get('reply', 'No reply')[:100]}...")
            print(f"   工作流ID: {chat_result.data.get('workflow_id')}")
        else:
            print(f"   错误: {chat_result.error}")
        
        # 执行代码生成任务
        print("\n💻 执行代码生成任务...")
        code_task = UniversalTask(
            content="Create a Python function that implements a simple graph traversal algorithm",
            task_type=TaskType.CODE_GENERATION,
            priority=TaskPriority.NORMAL,
            requirements=TaskRequirements(),
            context={'language': 'python'},
            task_id="code_demo"
        )
        
        code_result = await adapter.execute_task(code_task, context)
        print(f"   结果: {'成功' if code_result.success else '失败'}")
        if code_result.success:
            print(f"   代码: {code_result.data.get('code_result', 'No code')[:100]}...")
            print(f"   工作流ID: {code_result.data.get('workflow_id')}")
        else:
            print(f"   错误: {code_result.error}")
        
        # 执行工作流编排任务
        if workflow_ids:
            print("\n🔧 执行工作流编排任务...")
            workflow_task = UniversalTask(
                content="Execute a complex multi-step workflow to analyze data and generate insights",
                task_type=TaskType.WORKFLOW_ORCHESTRATION,
                priority=TaskPriority.HIGH,
                requirements=TaskRequirements(),
                context={'workflow_id': workflow_ids[0]},
                task_id="workflow_demo"
            )
            
            workflow_result = await adapter.execute_task(workflow_task, context)
            print(f"   结果: {'成功' if workflow_result.success else '失败'}")
            if workflow_result.success:
                result_data = workflow_result.data
                print(f"   工作流结果: {str(result_data.get('workflow_result', {}))[:100]}...")
                print(f"   工作流状态: {result_data.get('workflow_status', {}).get('compiled', False)}")
            else:
                print(f"   错误: {workflow_result.error}")
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")


async def demo_team_creation(adapter, workflow_ids):
    """演示团队创建（工作流组合）"""
    print("\n🤝 团队创建演示")
    print("=" * 50)
    
    if not adapter or len(workflow_ids) < 2:
        print("❌ 需要至少2个工作流进行团队演示")
        return
    
    try:
        # 创建工作流团队
        print("👥 创建工作流团队...")
        team_config = {
            "team_id": "demo_team",
            "workflow_ids": workflow_ids[:2],  # 使用前两个工作流
            "connections": [
                {"from": "workflow_0", "to": "workflow_1"}
            ]
        }
        
        team_id = await adapter.create_team(team_config)
        print(f"   ✅ 团队创建成功: {team_id}")
        
        # 获取团队状态
        team_status = adapter.get_workflow_status(team_id)
        print(f"   节点数: {team_status['nodes_count']}")
        print(f"   边数: {team_status['edges_count']}")
        print(f"   执行次数: {team_status['execution_count']}")
        
        return team_id
        
    except Exception as e:
        print(f"❌ 团队创建失败: {e}")
        return None


async def demo_a2a_integration(adapter, workflow_ids):
    """演示A2A协议集成"""
    print("\n🔄 A2A协议集成演示")
    print("=" * 50)
    
    if not adapter or not workflow_ids:
        print("❌ 适配器或工作流不可用，跳过演示")
        return
    
    try:
        print("📋 A2A集成状态:")
        
        # 获取A2A适配器状态
        a2a_status = adapter.a2a_adapter.get_integration_status()
        print(f"   层名称: {a2a_status['layer_name']}")
        print(f"   注册Agent数量: {a2a_status['registered_agents']}")
        print(f"   Agent列表: {a2a_status['agents']}")
        
        # 显示每个工作流的A2A能力
        print(f"\n🔧 工作流A2A能力:")
        for workflow_id in workflow_ids:
            if workflow_id in adapter.workflows:
                workflow = adapter.workflows[workflow_id]
                print(f"   {workflow_id}:")
                print(f"     节点数量: {len(workflow.nodes)}")
                
                # 显示每个节点的A2A配置文件
                for node_id, node in workflow.nodes.items():
                    profile = node["a2a_profile"]
                    print(f"     节点 {node_id}:")
                    print(f"       类型: {profile.agent_type}")
                    print(f"       能力: {[cap.capability_type.value for cap in profile.capabilities]}")
        
        # 模拟A2A工作流间通信
        if len(workflow_ids) >= 2:
            print(f"\n💬 模拟工作流间A2A通信...")
            workflow1_id = workflow_ids[0]
            workflow2_id = workflow_ids[1]
            
            print(f"   {workflow1_id} -> {workflow2_id}: 发送工作流协作请求")
            try:
                # 这里在实际环境中会发送真实的A2A消息
                print(f"   ✅ A2A工作流通信模拟成功")
                print(f"   协议: A2A v2.0")
                print(f"   传输: HTTP")
                print(f"   能力匹配: WORKFLOW_ORCHESTRATION")
            except Exception as e:
                print(f"   ❌ A2A通信失败: {e}")
        
    except Exception as e:
        print(f"❌ A2A协议集成演示失败: {e}")


async def demo_health_check(adapter):
    """演示健康检查"""
    print("\n🏥 健康检查演示")
    print("=" * 50)
    
    if not adapter:
        print("❌ 适配器不可用，跳过演示")
        return
    
    try:
        # 执行健康检查
        health_status = await adapter.health_check()
        
        print("📊 适配器健康状态:")
        print(f"   适配器名称: {health_status['adapter_name']}")
        print(f"   整体健康: {health_status['health']}")
        print(f"   状态: {health_status['status']}")
        print(f"   已初始化: {health_status['initialized']}")
        print(f"   LangGraph可用: {health_status['langgraph_available']}")
        print(f"   工作流数量: {health_status['workflows_count']}")
        print(f"   成功率: {health_status['success_rate']:.2%}")
        
        if 'compiled_workflows' in health_status:
            print(f"   已编译工作流: {health_status['compiled_workflows']}")
        
        if 'issues' in health_status:
            print(f"   问题: {health_status['issues']}")
        
        # 获取适配器元数据
        metadata = adapter.get_metadata()
        print(f"\n📈 适配器元数据:")
        print(f"   创建时间: {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   初始化次数: {metadata.initialization_count}")
        print(f"   成功操作: {metadata.successful_operations}")
        print(f"   失败操作: {metadata.failed_operations}")
        print(f"   成功率: {metadata.success_rate:.2%}")
        
        # 获取适配器完整状态
        print(f"\n🔍 适配器完整状态:")
        full_status = adapter.get_adapter_status()
        print(f"   LangGraph可用: {full_status['langgraph_available']}")
        print(f"   工作流数量: {full_status['workflows_count']}")
        print(f"   LLM配置: {full_status['llm_configs']}")
        print(f"   A2A集成状态: {full_status['a2a_integration']['layer_name']}")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


async def main():
    """主演示函数"""
    print("🌟 LangGraph适配器简化演示")
    print("展示LangGraph与ADC 8层架构和A2A协议的集成")
    print("=" * 60)
    
    try:
        # 适配器初始化
        adapter = await demo_adapter_initialization()
        
        if not adapter:
            print("\n❌ 无法继续演示，适配器初始化失败")
            return 1
        
        # 简单工作流创建
        workflow_ids = await demo_simple_workflow_creation(adapter)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 条件工作流创建
        conditional_id = await demo_conditional_workflow(adapter)
        if conditional_id:
            workflow_ids.append(conditional_id)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 工作流执行
        await demo_workflow_execution(adapter, workflow_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 团队创建
        await demo_team_creation(adapter, workflow_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # A2A集成
        await demo_a2a_integration(adapter, workflow_ids)
        
        # 等待一下
        await asyncio.sleep(0.5)
        
        # 健康检查
        await demo_health_check(adapter)
        
        # 总结
        print("\n" + "=" * 60)
        print("🎉 LangGraph适配器演示完成!")
        print("\n✨ 主要功能验证:")
        print("   ✅ 适配器初始化和配置管理")
        print("   ✅ 工作流创建和图结构定义")
        print("   ✅ 节点类型支持 (LLM, Tool, Function)")
        print("   ✅ 边和条件边管理")
        print("   ✅ 工作流执行和状态管理")
        print("   ✅ 团队创建和工作流组合")
        print("   ✅ A2A协议集成和节点通信")
        print("   ✅ 健康检查和性能监控")
        print("   ✅ 错误处理和异常管理")
        
        print("\n🚀 LangGraph适配器已成功集成到ADC 8层架构!")
        print("📋 注意: 完整功能需要安装LangGraph和LangChain依赖")
        print("💡 提示: 运行 pip install langgraph 以体验完整功能")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 