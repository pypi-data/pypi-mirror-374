"""
Prompt Manager - 提示词管理器
提供提示词的统一管理、优化和分发功能
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

from .prompt_template import PromptTemplate, PromptTemplateRegistry, TemplateType, PromptCategory
from .prompt_optimizer import PromptOptimizer
from .prompt_converter import PromptConverter
from .prompt_analyzer import PromptAnalyzer

logger = logging.getLogger(__name__)


class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        self.template_registry = PromptTemplateRegistry()
        self.optimizer = PromptOptimizer()
        self.converter = PromptConverter()
        self.analyzer = PromptAnalyzer()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def create_prompt(self, 
                          template_id: str,
                          variables: Dict[str, Any],
                          optimization_level: str = "basic") -> Dict[str, Any]:
        """创建提示词"""
        try:
            # 获取模板
            template = self.template_registry.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # 渲染模板
            prompt_content = template.render(**variables)
            
            # 优化提示词
            if optimization_level != "none":
                optimized_prompt = await self.optimizer.optimize_prompt(
                    prompt_content, 
                    template.template_type,
                    optimization_level
                )
            else:
                optimized_prompt = prompt_content
            
            # 分析提示词
            analysis = await self.analyzer.analyze_prompt(optimized_prompt)
            
            return {
                "prompt_id": f"prompt_{int(datetime.now().timestamp())}",
                "template_id": template_id,
                "template_name": template.name,
                "template_type": template.template_type.value,
                "category": template.category.value,
                "content": optimized_prompt,
                "variables": variables,
                "analysis": analysis,
                "created_at": datetime.now().isoformat(),
                "optimization_level": optimization_level
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create prompt: {e}")
            raise
    
    async def create_system_prompt(self, 
                                 agent_type: str,
                                 capabilities: List[str],
                                 personality: str = "professional",
                                 context: str = "") -> str:
        """创建系统提示词"""
        try:
            # 根据Agent类型选择模板
            if agent_type == "programming":
                template_id = "programming_assistant"
                variables = {
                    "languages": ", ".join(capabilities),
                    "project_name": context or "current project",
                    "code_style": "clean and maintainable"
                }
            elif agent_type == "analysis":
                template_id = "analysis_assistant"
                variables = {
                    "analysis_type": "general",
                    "data_context": context or "provided data",
                    "output_format": "structured analysis"
                }
            elif agent_type == "collaboration":
                template_id = "multi_agent_collaboration"
                variables = {
                    "task_description": context or "team collaboration",
                    "agent_role": "team member",
                    "expertise": ", ".join(capabilities),
                    "responsibilities": "contribute to team goals",
                    "team_members": "multiple agents",
                    "current_phase": "planning",
                    "next_steps": "execute assigned tasks"
                }
            else:
                template_id = "system_assistant"
                variables = {
                    "context": context or "general assistance"
                }
            
            # 创建提示词
            prompt_data = await self.create_prompt(template_id, variables)
            return prompt_data["content"]
            
        except Exception as e:
            self.logger.error(f"Failed to create system prompt: {e}")
            # 返回默认系统提示词
            return "You are a helpful AI assistant. Please help the user with their request."
    
    async def create_workflow_prompt(self,
                                   workflow_name: str,
                                   step_name: str,
                                   step_type: str,
                                   step_description: str,
                                   expected_output: str,
                                   previous_steps: List[str] = None,
                                   current_input: str = "",
                                   available_resources: List[str] = None,
                                   constraints: List[str] = None,
                                   step_config: Dict[str, Any] = None) -> str:
        """创建工作流步骤提示词"""
        try:
            variables = {
                "workflow_name": workflow_name,
                "step_name": step_name,
                "step_type": step_type,
                "step_description": step_description,
                "expected_output": expected_output,
                "previous_steps": ", ".join(previous_steps or []),
                "current_input": current_input,
                "available_resources": ", ".join(available_resources or []),
                "constraints": ", ".join(constraints or []),
                "step_config": json.dumps(step_config or {})
            }
            
            prompt_data = await self.create_prompt("workflow_step", variables)
            return prompt_data["content"]
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow prompt: {e}")
            return f"Execute the workflow step: {step_name} - {step_description}"
    
    async def convert_prompt_format(self,
                                  prompt: str,
                                  target_format: str,
                                  source_format: str = "general") -> str:
        """转换提示词格式"""
        try:
            return await self.converter.convert_prompt(
                prompt, 
                source_format, 
                target_format
            )
        except Exception as e:
            self.logger.error(f"Failed to convert prompt format: {e}")
            return prompt
    
    async def optimize_prompt(self,
                            prompt: str,
                            template_type: TemplateType,
                            optimization_level: str = "basic") -> str:
        """优化提示词"""
        try:
            return await self.optimizer.optimize_prompt(
                prompt, 
                template_type, 
                optimization_level
            )
        except Exception as e:
            self.logger.error(f"Failed to optimize prompt: {e}")
            return prompt
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """分析提示词"""
        try:
            return await self.analyzer.analyze_prompt(prompt)
        except Exception as e:
            self.logger.error(f"Failed to analyze prompt: {e}")
            return {"error": str(e)}
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.template_registry.get_template(template_id)
    
    def find_templates(self,
                      template_type: Optional[TemplateType] = None,
                      category: Optional[PromptCategory] = None,
                      tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """查找模板"""
        return self.template_registry.find_templates(template_type, category, tags)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有模板"""
        return self.template_registry.list_templates()
    
    def register_template(self, template: PromptTemplate) -> None:
        """注册模板"""
        self.template_registry.register_template(template)
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        return self.template_registry.delete_template(template_id)
    
    def export_templates(self, template_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """导出模板"""
        return self.template_registry.export_templates(template_ids)
    
    def import_templates(self, templates_data: Dict[str, Any]) -> List[str]:
        """导入模板"""
        return self.template_registry.import_templates(templates_data)
    
    async def batch_create_prompts(self,
                                 prompt_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量创建提示词"""
        results = []
        
        for request in prompt_requests:
            try:
                prompt_data = await self.create_prompt(
                    template_id=request["template_id"],
                    variables=request["variables"],
                    optimization_level=request.get("optimization_level", "basic")
                )
                results.append({
                    "success": True,
                    "data": prompt_data,
                    "request": request
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "request": request
                })
        
        return results
    
    async def create_prompt_chain(self,
                                chain_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创建提示词链"""
        chain_results = []
        context = {}
        
        for step_config in chain_config:
            try:
                # 合并上下文变量
                variables = {**context, **step_config.get("variables", {})}
                
                # 创建提示词
                prompt_data = await self.create_prompt(
                    template_id=step_config["template_id"],
                    variables=variables,
                    optimization_level=step_config.get("optimization_level", "basic")
                )
                
                # 更新上下文
                if "output_variables" in step_config:
                    for var_name, var_path in step_config["output_variables"].items():
                        # 这里可以根据实际输出解析变量
                        context[var_name] = f"output_from_{step_config['template_id']}"
                
                chain_results.append({
                    "step_id": step_config.get("step_id", f"step_{len(chain_results)}"),
                    "success": True,
                    "prompt_data": prompt_data,
                    "context": context.copy()
                })
                
            except Exception as e:
                chain_results.append({
                    "step_id": step_config.get("step_id", f"step_{len(chain_results)}"),
                    "success": False,
                    "error": str(e),
                    "context": context.copy()
                })
        
        return chain_results


# 全局提示词管理器实例
prompt_manager = PromptManager() 