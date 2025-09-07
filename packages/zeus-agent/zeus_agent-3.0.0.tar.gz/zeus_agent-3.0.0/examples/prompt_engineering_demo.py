#!/usr/bin/env python3
"""
Prompt Engineering Demo - 提示词工程演示
演示ADC中提示词工程系统的核心功能
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入提示词工程模块
from layers.framework.prompt_engineering import (
    PromptManager,
    PromptTemplate,
    PromptOptimizer,
    PromptConverter,
    PromptAnalyzer,
    TemplateType,
    PromptCategory
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_prompt_engineering():
    """演示提示词工程功能"""
    logger.info("🚀 === ADC 提示词工程系统演示 ===")
    
    # 创建提示词管理器
    prompt_manager = PromptManager()
    
    try:
        # 演示1: 模板管理
        logger.info("\n📋 演示1: 提示词模板管理")
        
        # 列出所有模板
        templates = prompt_manager.list_templates()
        logger.info(f"✅ 系统内置模板数量: {len(templates)}")
        
        for template in templates[:3]:  # 显示前3个模板
            logger.info(f"  - {template['name']} ({template['template_type']})")
        
        # 演示2: 创建系统提示词
        logger.info("\n🎯 演示2: 创建系统提示词")
        
        system_prompt = await prompt_manager.create_system_prompt(
            agent_type="programming",
            capabilities=["Python", "JavaScript", "SQL"],
            personality="professional",
            context="Web开发项目"
        )
        
        logger.info("✅ 编程助手系统提示词创建成功:")
        logger.info(f"   长度: {len(system_prompt)} 字符")
        logger.info(f"   包含关键词: {'Python' in system_prompt}, {'JavaScript' in system_prompt}")
        
        # 演示3: 创建工作流提示词
        logger.info("\n⚙️ 演示3: 创建工作流提示词")
        
        workflow_prompt = await prompt_manager.create_workflow_prompt(
            workflow_name="数据分析工作流",
            step_name="数据清洗",
            step_type="data_processing",
            step_description="清洗和预处理输入数据",
            expected_output="清洗后的数据集",
            previous_steps=["数据收集"],
            current_input="原始CSV数据",
            available_resources=["pandas", "numpy"],
            constraints=["内存限制: 8GB", "时间限制: 30分钟"]
        )
        
        logger.info("✅ 工作流步骤提示词创建成功:")
        logger.info(f"   长度: {len(workflow_prompt)} 字符")
        logger.info(f"   包含步骤信息: {'数据清洗' in workflow_prompt}")
        
        # 演示4: 提示词优化
        logger.info("\n🔧 演示4: 提示词优化")
        
        # 创建一个需要优化的提示词
        raw_prompt = """
        Please, could you very kindly help me with this task? 
        You should maybe possibly create some code for me.
        I'm not really sure what I need exactly, but perhaps you could do something useful.
        """
        
        optimizer = PromptOptimizer()
        optimized_prompt = await optimizer.optimize_prompt(
            raw_prompt,
            TemplateType.SYSTEM_PROMPT,
            "advanced"
        )
        
        logger.info("✅ 提示词优化完成:")
        logger.info(f"   原始长度: {len(raw_prompt)} 字符")
        logger.info(f"   优化后长度: {len(optimized_prompt)} 字符")
        logger.info(f"   移除了冗余词汇: {'please' not in optimized_prompt.lower()}")
        
        # 演示5: 提示词分析
        logger.info("\n📊 演示5: 提示词质量分析")
        
        analyzer = PromptAnalyzer()
        analysis = await analyzer.analyze_prompt(system_prompt)
        
        logger.info("✅ 提示词分析完成:")
        logger.info(f"   总体评分: {analysis['overall_score']}/100")
        logger.info(f"   质量评分: {analysis['quality_scores']}")
        logger.info(f"   风险等级: {analysis['risk_assessment']['risk_level']}")
        logger.info(f"   建议数量: {len(analysis['suggestions'])}")
        
        if analysis['suggestions']:
            logger.info("   改进建议:")
            for suggestion in analysis['suggestions'][:3]:
                logger.info(f"     - {suggestion}")
        
        # 演示6: 格式转换
        logger.info("\n🔄 演示6: 提示词格式转换")
        
        converter = PromptConverter()
        
        # 转换为不同框架格式
        openai_format = converter.convert_to_openai_format(system_prompt, "general")
        autogen_format = converter.convert_to_autogen_format(system_prompt, "general")
        
        logger.info("✅ 格式转换完成:")
        logger.info(f"   OpenAI格式长度: {len(openai_format)} 字符")
        logger.info(f"   AutoGen格式长度: {len(autogen_format)} 字符")
        logger.info(f"   支持的格式: {converter.get_supported_formats()}")
        
        # 演示7: 批量创建提示词
        logger.info("\n📦 演示7: 批量创建提示词")
        
        batch_requests = [
            {
                "template_id": "system_assistant",
                "variables": {"context": "通用助手"},
                "optimization_level": "basic"
            },
            {
                "template_id": "analysis_assistant", 
                "variables": {
                    "analysis_type": "数据分析",
                    "data_context": "用户数据",
                    "output_format": "JSON格式"
                },
                "optimization_level": "advanced"
            }
        ]
        
        batch_results = await prompt_manager.batch_create_prompts(batch_requests)
        
        logger.info("✅ 批量创建完成:")
        for i, result in enumerate(batch_results, 1):
            if result['success']:
                logger.info(f"   提示词 {i}: 创建成功 ({len(result['data']['content'])} 字符)")
            else:
                logger.info(f"   提示词 {i}: 创建失败 - {result['error']}")
        
        # 演示8: 提示词链
        logger.info("\n🔗 演示8: 提示词链创建")
        
        chain_config = [
            {
                "step_id": "step_1",
                "template_id": "system_assistant",
                "variables": {"context": "第一步：理解需求"},
                "optimization_level": "basic"
            },
            {
                "step_id": "step_2", 
                "template_id": "analysis_assistant",
                "variables": {
                    "analysis_type": "需求分析",
                    "data_context": "用户输入",
                    "output_format": "结构化分析"
                },
                "optimization_level": "advanced",
                "output_variables": {
                    "analysis_result": "analysis_output"
                }
            }
        ]
        
        chain_results = await prompt_manager.create_prompt_chain(chain_config)
        
        logger.info("✅ 提示词链创建完成:")
        for step in chain_results:
            if step['success']:
                logger.info(f"   步骤 {step['step_id']}: 成功")
            else:
                logger.info(f"   步骤 {step['step_id']}: 失败 - {step['error']}")
        
        # 总结
        logger.info("\n🎉 === 提示词工程演示完成 ===")
        logger.info("✅ 提示词模板管理功能正常")
        logger.info("✅ 系统提示词创建功能正常")
        logger.info("✅ 工作流提示词创建功能正常")
        logger.info("✅ 提示词优化功能正常")
        logger.info("✅ 提示词分析功能正常")
        logger.info("✅ 格式转换功能正常")
        logger.info("✅ 批量创建功能正常")
        logger.info("✅ 提示词链功能正常")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 演示过程中发生错误: {e}")
        return False


async def demo_custom_template():
    """演示自定义模板创建"""
    logger.info("\n🎨 === 自定义模板创建演示 ===")
    
    try:
        # 创建自定义模板
        custom_template = PromptTemplate(
            template_id="custom_code_review",
            name="代码审查助手",
            description="专门用于代码审查的提示词模板",
            template_type=TemplateType.SYSTEM_PROMPT,
            category=PromptCategory.PROGRAMMING,
            content="""You are an expert code reviewer specializing in {{languages}}.

Your code review expertise includes:
- Code quality and best practices
- Security vulnerabilities and risks
- Performance optimization opportunities
- Maintainability and readability
- Testing coverage and quality

Review guidelines:
- Be constructive and specific in feedback
- Provide actionable suggestions for improvement
- Consider both technical and business requirements
- Highlight critical issues that need immediate attention
- Suggest alternative approaches when appropriate

Code to review: {{code_snippet}}
Programming language: {{languages}}
Review focus: {{review_focus}}
Output format: {{output_format}}""",
            variables=["languages", "code_snippet", "review_focus", "output_format"],
            tags=["code-review", "programming", "quality"]
        )
        
        # 注册模板
        prompt_manager = PromptManager()
        prompt_manager.register_template(custom_template)
        
        # 使用自定义模板
        review_prompt = await prompt_manager.create_prompt(
            template_id="custom_code_review",
            variables={
                "languages": "Python, JavaScript",
                "code_snippet": "def calculate_sum(a, b): return a + b",
                "review_focus": "security and performance",
                "output_format": "structured feedback"
            },
            optimization_level="advanced"
        )
        
        logger.info("✅ 自定义模板创建和使用成功:")
        logger.info(f"   模板名称: {custom_template.name}")
        logger.info(f"   模板类型: {custom_template.template_type.value}")
        logger.info(f"   变量数量: {len(custom_template.variables)}")
        logger.info(f"   生成的提示词长度: {len(review_prompt['content'])} 字符")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 自定义模板演示失败: {e}")
        return False


async def main():
    """主函数"""
    success1 = await demo_prompt_engineering()
    success2 = await demo_custom_template()
    
    if success1 and success2:
        logger.info("\n🎊 === 所有演示成功完成 ===")
        return True
    else:
        logger.error("\n❌ === 部分演示失败 ===")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 