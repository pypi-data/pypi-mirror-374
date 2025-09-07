"""
Prompt Optimizer - 提示词优化器
提供提示词的智能优化功能
"""

import re
import logging
from typing import Dict, Any, List, Optional
from .prompt_template import TemplateType

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """提示词优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载优化规则"""
        return {
            "basic": [
                {
                    "name": "remove_extra_whitespace",
                    "description": "移除多余的空格和换行",
                    "pattern": r'\s+',
                    "replacement": ' ',
                    "apply": True
                },
                {
                    "name": "trim_whitespace",
                    "description": "修剪首尾空格",
                    "pattern": r'^\s+|\s+$',
                    "replacement": '',
                    "apply": True
                }
            ],
            "advanced": [
                {
                    "name": "improve_clarity",
                    "description": "提高清晰度",
                    "patterns": [
                        (r'\b(please|kindly)\b', ''),
                        (r'\b(very|really|quite)\b', ''),
                        (r'\b(you should|you must|you need to)\b', ''),
                    ],
                    "apply": True
                },
                {
                    "name": "add_structure",
                    "description": "添加结构化格式",
                    "apply": True
                }
            ],
            "expert": [
                {
                    "name": "semantic_optimization",
                    "description": "语义优化",
                    "apply": True
                },
                {
                    "name": "context_enhancement",
                    "description": "上下文增强",
                    "apply": True
                }
            ]
        }
    
    async def optimize_prompt(self,
                            prompt: str,
                            template_type: TemplateType,
                            optimization_level: str = "basic") -> str:
        """优化提示词"""
        try:
            optimized_prompt = prompt
            
            # 应用基础优化
            if optimization_level in ["basic", "advanced", "expert"]:
                optimized_prompt = self._apply_basic_optimization(optimized_prompt)
            
            # 应用高级优化
            if optimization_level in ["advanced", "expert"]:
                optimized_prompt = self._apply_advanced_optimization(optimized_prompt)
            
            # 应用专家级优化
            if optimization_level == "expert":
                optimized_prompt = await self._apply_expert_optimization(optimized_prompt, template_type)
            
            # 应用模板类型特定优化
            optimized_prompt = self._apply_template_specific_optimization(optimized_prompt, template_type)
            
            self.logger.info(f"Prompt optimized with level: {optimization_level}")
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to optimize prompt: {e}")
            return prompt
    
    def _apply_basic_optimization(self, prompt: str) -> str:
        """应用基础优化"""
        optimized = prompt
        
        # 移除多余空格
        optimized = re.sub(r'\s+', ' ', optimized)
        
        # 修剪首尾空格
        optimized = optimized.strip()
        
        # 标准化换行符
        optimized = optimized.replace('\r\n', '\n').replace('\r', '\n')
        
        return optimized
    
    def _apply_advanced_optimization(self, prompt: str) -> str:
        """应用高级优化"""
        optimized = prompt
        
        # 移除冗余词汇
        redundant_words = [
            (r'\b(please|kindly)\b', ''),
            (r'\b(very|really|quite)\b', ''),
            (r'\b(you should|you must|you need to)\b', ''),
            (r'\b(obviously|clearly|evidently)\b', ''),
        ]
        
        for pattern, replacement in redundant_words:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        # 添加结构化格式
        if "Instructions:" in optimized or "Guidelines:" in optimized:
            # 确保格式一致
            optimized = re.sub(r'Instructions:\s*', 'Instructions:\n', optimized)
            optimized = re.sub(r'Guidelines:\s*', 'Guidelines:\n', optimized)
        
        return optimized
    
    async def _apply_expert_optimization(self, prompt: str, template_type: TemplateType) -> str:
        """应用专家级优化"""
        optimized = prompt
        
        # 根据模板类型进行特定优化
        if template_type == TemplateType.SYSTEM_PROMPT:
            optimized = self._optimize_system_prompt(optimized)
        elif template_type == TemplateType.WORKFLOW:
            optimized = self._optimize_workflow_prompt(optimized)
        elif template_type == TemplateType.MULTI_AGENT:
            optimized = self._optimize_multi_agent_prompt(optimized)
        
        return optimized
    
    def _optimize_system_prompt(self, prompt: str) -> str:
        """优化系统提示词"""
        optimized = prompt
        
        # 确保角色定义清晰
        if "You are" not in optimized:
            optimized = "You are a helpful AI assistant.\n\n" + optimized
        
        # 添加行为准则
        if "Guidelines:" not in optimized and "Instructions:" not in optimized:
            guidelines = """
Guidelines:
- Be helpful, accurate, and honest
- If you're not sure about something, say so
- Provide clear and concise responses
- Be respectful and professional
"""
            optimized += guidelines
        
        return optimized
    
    def _optimize_workflow_prompt(self, prompt: str) -> str:
        """优化工作流提示词"""
        optimized = prompt
        
        # 确保步骤信息清晰
        if "Step information:" not in optimized:
            optimized = optimized.replace("Step information:", "Step Information:")
        
        # 添加执行状态更新
        if "Update the execution status" not in optimized:
            optimized += "\n- Update the execution status after completion"
        
        return optimized
    
    def _optimize_multi_agent_prompt(self, prompt: str) -> str:
        """优化多Agent提示词"""
        optimized = prompt
        
        # 确保协作指导清晰
        if "Collaboration guidelines:" not in optimized:
            collaboration_guidelines = """
Collaboration guidelines:
- Communicate clearly with other agents
- Share relevant information and insights
- Coordinate actions and avoid conflicts
- Support team goals and objectives
"""
            optimized += collaboration_guidelines
        
        return optimized
    
    def _apply_template_specific_optimization(self, prompt: str, template_type: TemplateType) -> str:
        """应用模板类型特定优化"""
        optimized = prompt
        
        # 根据模板类型添加特定优化
        if template_type == TemplateType.CHAIN_OF_THOUGHT:
            optimized = self._optimize_chain_of_thought(optimized)
        elif template_type == TemplateType.REACT:
            optimized = self._optimize_react_prompt(optimized)
        elif template_type == TemplateType.FUNCTION_CALLING:
            optimized = self._optimize_function_calling(optimized)
        
        return optimized
    
    def _optimize_chain_of_thought(self, prompt: str) -> str:
        """优化思维链提示词"""
        optimized = prompt
        
        # 确保包含思考步骤指导
        if "Let's approach this step by step" not in optimized:
            optimized += "\n\nLet's approach this step by step:"
        
        return optimized
    
    def _optimize_react_prompt(self, prompt: str) -> str:
        """优化ReAct提示词"""
        optimized = prompt
        
        # 确保包含观察-思考-行动循环
        react_format = """
Please follow this format:
Thought: I need to think about this step by step
Action: the action to take
Observation: the result of the action
... (repeat Thought/Action/Observation if needed)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""
        
        if "Thought:" not in optimized:
            optimized += react_format
        
        return optimized
    
    def _optimize_function_calling(self, prompt: str) -> str:
        """优化函数调用提示词"""
        optimized = prompt
        
        # 确保包含函数调用指导
        if "available functions" not in optimized.lower():
            optimized += "\n\nUse the available functions when needed to complete the task."
        
        return optimized
    
    def analyze_prompt_quality(self, prompt: str) -> Dict[str, Any]:
        """分析提示词质量"""
        analysis = {
            "length": len(prompt),
            "word_count": len(prompt.split()),
            "clarity_score": 0,
            "structure_score": 0,
            "specificity_score": 0,
            "suggestions": []
        }
        
        # 清晰度评分
        clarity_indicators = [
            "clear", "specific", "detailed", "precise", "explicit"
        ]
        analysis["clarity_score"] = sum(1 for indicator in clarity_indicators if indicator in prompt.lower())
        
        # 结构化评分
        structure_indicators = [
            "guidelines:", "instructions:", "steps:", "format:", "example:"
        ]
        analysis["structure_score"] = sum(1 for indicator in structure_indicators if indicator in prompt.lower())
        
        # 具体性评分
        specificity_indicators = [
            "{{", "}}", "specific", "concrete", "detailed"
        ]
        analysis["specificity_score"] = sum(1 for indicator in specificity_indicators if indicator in prompt.lower())
        
        # 生成建议
        if analysis["clarity_score"] < 2:
            analysis["suggestions"].append("Add more specific instructions")
        
        if analysis["structure_score"] < 2:
            analysis["suggestions"].append("Add structured guidelines or instructions")
        
        if analysis["specificity_score"] < 2:
            analysis["suggestions"].append("Include more specific details or variables")
        
        if len(prompt) < 50:
            analysis["suggestions"].append("Consider adding more context and details")
        
        if len(prompt) > 1000:
            analysis["suggestions"].append("Consider breaking down into smaller, focused prompts")
        
        return analysis 