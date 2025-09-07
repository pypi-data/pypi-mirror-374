#!/usr/bin/env python3
"""
OpenAI Focus Demo
专注核心流程的OpenAI演示

验证以下核心层次：
1. 基础设施层 - 配置管理、日志记录
2. 适配器层 - OpenAI适配器
3. 框架抽象层 - UniversalAgent接口
4. 业务能力层 - 基础协作功能
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

logger = get_logger("openai_focus_demo")


class OpenAIFocusDemo:
    """OpenAI专注演示类"""
    
    def __init__(self):
        self.config_manager = None
        self.openai_adapter = None
        self.agent_wrapper = None
    
    async def initialize(self):
        """初始化核心组件"""
        logger.info("🚀 开始初始化OpenAI核心流程演示")
        
        # 1. 初始化基础设施层
        await self._initialize_infrastructure()
        
        # 2. 初始化适配器层
        await self._initialize_adapter()
        
        # 3. 初始化框架抽象层
        await self._initialize_framework()
        
        logger.info("✅ 核心组件初始化完成")
    
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
        self.openai_adapter = OpenAIAdapter("focus_demo_adapter")
        
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
                name="FocusAgent",
                adapter=self.openai_adapter,
                description="专注演示用的OpenAI Agent",
                config={
                    "system_message": "You are a helpful AI assistant demonstrating the ADC framework core capabilities. Keep responses clear and concise.",
                    "model_config": "default"
                }
            )
            logger.info("✅ Agent包装器创建完成")
    
    async def run_demo(self):
        """运行专注演示"""
        logger.info("🎯 开始运行专注演示")
        
        # 演示1: 基础对话能力
        await self._demo_basic_conversation()
        
        # 演示2: 任务执行能力
        await self._demo_task_execution()
        
        # 演示3: 代码生成能力
        await self._demo_code_generation()
        
        # 演示4: 分析能力
        await self._demo_analysis()
        
        logger.info("🎉 专注演示运行完成")
    
    async def _demo_basic_conversation(self):
        """演示基础对话能力"""
        logger.info("\n" + "="*50)
        logger.info("💬 演示1: 基础对话能力")
        logger.info("="*50)
        
        if not self.agent_wrapper:
            logger.info("⏭️  跳过对话演示（OpenAI API未配置）")
            return
        
        try:
            questions = [
                "Hello! Please introduce yourself briefly.",
                "What are the core layers in the ADC framework?",
                "How does the adapter pattern work in ADC?"
            ]
            
            conversation_history = []
            
            for question in questions:
                logger.info(f"👤 用户: {question}")
                
                response = await self.agent_wrapper.chat(question, conversation_history)
                logger.info(f"🤖 Agent: {response}")
                
                # 更新对话历史
                conversation_history.append({"role": "user", "content": question})
                conversation_history.append({"role": "assistant", "content": response})
                
                # 限制历史长度
                if len(conversation_history) > 6:
                    conversation_history = conversation_history[-6:]
            
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
                content="Analyze the benefits of using a layered architecture in AI agent frameworks. Focus on: layered architecture in AI frameworks, benefits and advantages",
                task_type=TaskType.ANALYSIS,
                task_id="focus_demo_task_001",
                context={
                    "topic": "layered architecture in AI frameworks",
                    "focus": "benefits and advantages"
                }
            )
            
            # 创建上下文
            context = UniversalContext(
                conversation_history=[],
                metadata={"demo_mode": True, "focus": "core_layers"}
            )
            
            # 执行任务
            logger.info(f"🎯 执行任务: {task.name}")
            result = await self.agent_wrapper.execute_task(task, context)
            
            if result.status.value == "success":
                logger.info(f"✅ 任务执行成功")
                logger.info(f"📊 分析结果: {result.data}")
            else:
                logger.info(f"❌ 任务执行失败: {result.error_info}")
            
        except Exception as e:
            logger.error(f"❌ 任务执行演示失败: {e}")
    
    async def _demo_code_generation(self):
        """演示代码生成能力"""
        logger.info("\n" + "="*50)
        logger.info("💻 演示3: 代码生成能力")
        logger.info("="*50)
        
        if not self.agent_wrapper:
            logger.info("⏭️  跳过代码生成演示（OpenAI API未配置）")
            return
        
        try:
            # 生成适配器模式示例
            code_request = {
                "description": "Create a simple adapter pattern example in Python that demonstrates how to adapt different interfaces",
                "language": "python",
                "requirements": ["clear comments", "simple example", "follows adapter pattern"]
            }
            
            logger.info(f"🛠️  生成代码: {code_request['description']}")
            result = await self.agent_wrapper.generate_code(
                code_request["description"],
                code_request["language"]
            )
            
            if result and not result.get("error"):
                logger.info(f"✅ 代码生成成功")
                logger.info(f"💻 生成的代码:\n{result.get('code', 'N/A')}")
                logger.info(f"📝 代码说明: {result.get('explanation', 'N/A')}")
            else:
                logger.info(f"❌ 代码生成失败: {result.get('explanation', 'Unknown error') if result else 'No result'}")
            
        except Exception as e:
            logger.error(f"❌ 代码生成演示失败: {e}")
    
    async def _demo_analysis(self):
        """演示分析能力"""
        logger.info("\n" + "="*50)
        logger.info("🔍 演示4: 文本分析能力")
        logger.info("="*50)
        
        if not self.agent_wrapper:
            logger.info("⏭️  跳过分析演示（OpenAI API未配置）")
            return
        
        try:
            # 分析ADC框架的优势
            analysis_text = """
            The Agent Development Center (ADC) framework uses a 7-layer architecture:
            Infrastructure, Adapter, Framework Abstraction, Cognitive Architecture, 
            Business Capability, Application, and DevX layers. This design promotes
            modularity, scalability, and maintainability while providing a unified
            interface for different AI frameworks.
            """
            
            # 创建分析任务
            task = UniversalTask(
                content=f"Analyze the given text about ADC framework architecture: {analysis_text.strip()}",
                task_type=TaskType.ANALYSIS,
                task_id="analysis_demo_001",
                context={
                    "text": analysis_text.strip(),
                    "analysis_type": "architecture_benefits"
                }
            )
            
            context = UniversalContext(
                conversation_history=[],
                metadata={"analysis_focus": "architecture"}
            )
            
            logger.info("🔍 分析ADC框架架构文本...")
            result = await self.agent_wrapper.execute_task(task, context)
            
            if result.status.value == "success":
                logger.info(f"✅ 文本分析完成")
                logger.info(f"📊 分析结果: {result.data}")
            else:
                logger.info(f"❌ 文本分析失败: {result.error_info}")
            
        except Exception as e:
            logger.error(f"❌ 分析演示失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理资源...")
        
        if self.openai_adapter:
            self.openai_adapter.cleanup()
        
        logger.info("✅ 资源清理完成")


async def main():
    """主函数"""
    print("🎯 OpenAI专注核心流程演示")
    print("=" * 60)
    print("本演示专注于验证ADC框架的核心层次：")
    print("1. 基础设施层 - 配置管理、日志记录")
    print("2. 适配器层 - OpenAI适配器")
    print("3. 框架抽象层 - UniversalAgent接口")
    print("4. 业务能力层 - 基础功能")
    print("=" * 60)
    print()
    
    # 检查OpenAI API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: OPENAI_API_KEY未设置")
        print("   部分功能将以模拟模式运行")
        print("   设置方法: export OPENAI_API_KEY='your-api-key'")
        print()
    else:
        print("✅ OpenAI API密钥已设置，将运行完整演示")
        print()
    
    demo = OpenAIFocusDemo()
    
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