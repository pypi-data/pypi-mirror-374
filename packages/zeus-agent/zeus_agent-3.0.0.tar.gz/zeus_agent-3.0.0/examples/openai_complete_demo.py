#!/usr/bin/env python3
"""
OpenAI Complete Flow Demo
OpenAI完整流程演示

验证以下层次的集成：
1. 基础设施层 - 配置管理、日志记录
2. 适配器层 - OpenAI适配器
3. 框架抽象层 - UniversalAgent接口
4. 认知架构层 - 感知、推理、记忆
5. 业务能力层 - 协作和工作流
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
from layers.infrastructure.config.config_manager import ConfigManager

# 适配器层导入
from layers.adapter.openai.adapter import OpenAIAdapter
from layers.adapter.openai.agent_wrapper import OpenAIAgentWrapper

# 框架抽象层导入
from layers.framework.abstractions.agent import AgentCapability
from layers.framework.abstractions.task import UniversalTask, TaskType
from layers.framework.abstractions.context import UniversalContext
from layers.framework.abstractions.result import UniversalResult

# 认知架构层导入
from layers.cognitive.cognitive_agent import CognitiveAgent

# 业务能力层导入
from layers.business.teams.collaboration_manager import CollaborationManager, CollaborationPattern
from layers.business.workflows.workflow_engine import WorkflowEngine, WorkflowStepType

logger = get_logger("openai_complete_demo")


class OpenAICompleteDemo:
    """OpenAI完整流程演示类"""
    
    def __init__(self):
        self.config_manager = None
        self.openai_adapter = None
        self.agent_wrapper = None
        self.cognitive_agent = None
        self.collaboration_manager = None
        self.workflow_engine = None
    
    async def initialize(self):
        """初始化所有组件"""
        logger.info("🚀 开始初始化OpenAI完整流程演示")
        
        # 1. 初始化基础设施层
        await self._initialize_infrastructure()
        
        # 2. 初始化适配器层
        await self._initialize_adapter()
        
        # 3. 初始化框架抽象层
        await self._initialize_framework()
        
        # 4. 初始化认知架构层
        await self._initialize_cognitive()
        
        # 5. 初始化业务能力层
        await self._initialize_business()
        
        logger.info("✅ 所有组件初始化完成")
    
    async def _initialize_infrastructure(self):
        """初始化基础设施层"""
        logger.info("📋 初始化基础设施层...")
        
        # 配置管理器
        self.config_manager = ConfigManager()
        
        # 检查环境变量
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️  OPENAI_API_KEY未设置，将使用模拟模式")
        else:
            logger.info("✅ OpenAI API密钥已设置")
    
    async def _initialize_adapter(self):
        """初始化适配器层"""
        logger.info("🔌 初始化适配器层...")
        
        # OpenAI适配器
        self.openai_adapter = OpenAIAdapter("demo_adapter")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            config = {
                "api_key": api_key,
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 2000
            }
            await self.openai_adapter.initialize(config)
            logger.info("✅ OpenAI适配器初始化完成")
        else:
            logger.info("🔄 使用模拟模式初始化适配器")
    
    async def _initialize_framework(self):
        """初始化框架抽象层"""
        logger.info("🏗️ 初始化框架抽象层...")
        
        # Agent包装器
        if self.openai_adapter:
            self.agent_wrapper = OpenAIAgentWrapper(
                name="DemoAgent",
                adapter=self.openai_adapter,
                description="演示用的OpenAI Agent",
                config={
                    "system_message": "You are a helpful AI assistant focused on demonstrating the ADC framework capabilities.",
                    "model_config": "default"
                }
            )
            logger.info("✅ Agent包装器创建完成")
    
    async def _initialize_cognitive(self):
        """初始化认知架构层"""
        logger.info("🧠 初始化认知架构层...")
        
        if self.agent_wrapper:
            self.cognitive_agent = CognitiveAgent(
                name="CognitiveDemoAgent",
                base_agent=self.agent_wrapper,
                config={
                    "memory_capacity": 1000,
                    "learning_enabled": True,
                    "perception_modules": ["text", "context"],
                    "reasoning_strategy": "chain_of_thought"
                }
            )
            logger.info("✅ 认知Agent创建完成")
    
    async def _initialize_business(self):
        """初始化业务能力层"""
        logger.info("🏢 初始化业务能力层...")
        
        # 协作管理器
        self.collaboration_manager = CollaborationManager()
        logger.info("✅ 协作管理器创建完成")
        
        # 工作流引擎
        self.workflow_engine = WorkflowEngine()
        logger.info("✅ 工作流引擎创建完成")
    
    async def run_demo(self):
        """运行完整演示"""
        logger.info("🎯 开始运行完整演示")
        
        # 演示1: 基础对话能力
        await self._demo_basic_conversation()
        
        # 演示2: 任务执行能力
        await self._demo_task_execution()
        
        # 演示3: 认知能力
        await self._demo_cognitive_abilities()
        
        # 演示4: 业务协作能力
        await self._demo_business_collaboration()
        
        logger.info("🎉 完整演示运行完成")
    
    async def _demo_basic_conversation(self):
        """演示基础对话能力"""
        logger.info("\n" + "="*50)
        logger.info("📱 演示1: 基础对话能力")
        logger.info("="*50)
        
        if not self.agent_wrapper:
            logger.info("⏭️  跳过对话演示（OpenAI API未配置）")
            return
        
        try:
            # 简单对话
            response = await self.agent_wrapper.chat(
                "Hello! Please introduce yourself and explain what you can do.",
                []
            )
            logger.info(f"🤖 Agent回复: {response}")
            
            # 代码生成
            code_result = await self.agent_wrapper.generate_code(
                "Create a simple Python function that calculates the factorial of a number",
                "python"
            )
            
            if code_result and not code_result.get("error"):
                logger.info(f"💻 生成的代码:\n{code_result.get('code', 'N/A')}")
                logger.info(f"📝 代码说明: {code_result.get('explanation', 'N/A')}")
            else:
                logger.info(f"❌ 代码生成失败: {code_result.get('explanation', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"❌ 对话演示失败: {e}")
    
    async def _demo_task_execution(self):
        """演示任务执行能力"""
        logger.info("\n" + "="*50)
        logger.info("📋 演示2: 任务执行能力")
        logger.info("="*50)
        
        if not self.agent_wrapper:
            logger.info("⏭️  跳过任务演示（OpenAI API未配置）")
            return
        
        try:
            # 创建通用任务
            task = UniversalTask(
                id="demo_task_001",
                name="Text Analysis Task",
                task_type=TaskType.ANALYSIS,
                description="Analyze the sentiment and key topics of a given text",
                parameters={
                    "text": "I love working with AI agents! They are incredibly helpful and efficient.",
                    "analysis_type": "sentiment_and_topics"
                }
            )
            
            # 创建上下文
            context = UniversalContext(
                conversation_history=[],
                metadata={"demo_mode": True}
            )
            
            # 执行任务
            logger.info(f"🎯 执行任务: {task.name}")
            result = await self.agent_wrapper.execute_task(task, context)
            
            if result.status.value == "success":
                logger.info(f"✅ 任务执行成功")
                logger.info(f"📊 结果: {result.data}")
            else:
                logger.info(f"❌ 任务执行失败: {result.error_info}")
            
        except Exception as e:
            logger.error(f"❌ 任务执行演示失败: {e}")
    
    async def _demo_cognitive_abilities(self):
        """演示认知能力"""
        logger.info("\n" + "="*50)
        logger.info("🧠 演示3: 认知能力")
        logger.info("="*50)
        
        if not self.cognitive_agent:
            logger.info("⏭️  跳过认知演示（认知Agent未初始化）")
            return
        
        try:
            # 感知能力
            perception_result = await self.cognitive_agent.perceive({
                "text": "The weather is beautiful today, perfect for a walk in the park.",
                "context": "casual conversation"
            })
            logger.info(f"👁️  感知结果: {perception_result}")
            
            # 推理能力
            reasoning_result = await self.cognitive_agent.reason({
                "problem": "If it takes 5 minutes to cook 1 egg, how long does it take to cook 3 eggs?",
                "context": "logical reasoning"
            })
            logger.info(f"🤔 推理结果: {reasoning_result}")
            
            # 记忆能力
            await self.cognitive_agent.remember("demo_key", "This is a demo memory item")
            memory_result = await self.cognitive_agent.recall("demo_key")
            logger.info(f"💭 记忆结果: {memory_result}")
            
        except Exception as e:
            logger.error(f"❌ 认知能力演示失败: {e}")
    
    async def _demo_business_collaboration(self):
        """演示业务协作能力"""
        logger.info("\n" + "="*50)
        logger.info("🏢 演示4: 业务协作能力")
        logger.info("="*50)
        
        try:
            # 协作模式演示
            if self.collaboration_manager:
                logger.info("👥 创建协作任务...")
                
                # 模拟团队成员
                team_members = [
                    {"id": "agent1", "name": "AnalysisAgent", "role": "analyst"},
                    {"id": "agent2", "name": "WriterAgent", "role": "writer"}
                ]
                
                collaboration_task = {
                    "id": "collab_demo_001",
                    "name": "Content Creation Collaboration",
                    "description": "Analyze requirements and create content",
                    "pattern": CollaborationPattern.PIPELINE,
                    "members": team_members
                }
                
                result = await self.collaboration_manager.execute_collaboration(collaboration_task)
                logger.info(f"🤝 协作执行结果: {result.get('status', 'unknown')}")
            
            # 工作流演示
            if self.workflow_engine:
                logger.info("🔄 创建工作流...")
                
                workflow_def = {
                    "id": "demo_workflow_001",
                    "name": "Simple Analysis Workflow",
                    "description": "A simple workflow for text analysis",
                    "steps": [
                        {
                            "id": "step1",
                            "name": "Input Processing",
                            "type": WorkflowStepType.TASK,
                            "config": {"task_type": "preprocessing"}
                        },
                        {
                            "id": "step2", 
                            "name": "Analysis",
                            "type": WorkflowStepType.TASK,
                            "config": {"task_type": "analysis"},
                            "dependencies": ["step1"]
                        }
                    ]
                }
                
                execution = await self.workflow_engine.execute_workflow(
                    workflow_def, 
                    {"input_text": "Sample text for analysis"}
                )
                logger.info(f"⚙️  工作流执行结果: {execution.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ 业务协作演示失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理资源...")
        
        if self.openai_adapter:
            self.openai_adapter.cleanup()
        
        logger.info("✅ 资源清理完成")


async def main():
    """主函数"""
    print("🚀 OpenAI完整流程演示")
    print("=" * 60)
    print("本演示将验证ADC框架的五个核心层次：")
    print("1. 基础设施层 - 配置管理、日志记录")
    print("2. 适配器层 - OpenAI适配器")
    print("3. 框架抽象层 - UniversalAgent接口")
    print("4. 认知架构层 - 感知、推理、记忆")
    print("5. 业务能力层 - 协作和工作流")
    print("=" * 60)
    print()
    
    # 检查OpenAI API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: OPENAI_API_KEY未设置")
        print("   部分功能将以模拟模式运行")
        print("   设置方法: export OPENAI_API_KEY='your-api-key'")
        print()
    
    demo = OpenAICompleteDemo()
    
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
        # 清理资源
        await demo.cleanup()
        print("\n🎉 演示完成！")


if __name__ == "__main__":
    asyncio.run(main()) 