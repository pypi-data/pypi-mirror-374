"""
Prompt Template System - 提示词模板系统
提供可复用的提示词模板和变量替换功能
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """模板类型"""
    SYSTEM_PROMPT = "system_prompt"
    USER_PROMPT = "user_prompt"
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    REACT = "react"
    FUNCTION_CALLING = "function_calling"
    MULTI_AGENT = "multi_agent"
    WORKFLOW = "workflow"


class PromptCategory(Enum):
    """提示词分类"""
    GENERAL = "general"
    PROGRAMMING = "programming"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    RESEARCH = "research"
    COLLABORATION = "collaboration"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


@dataclass
class PromptTemplate:
    """提示词模板"""
    
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    category: PromptCategory
    content: str
    variables: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.template_id:
            self.template_id = str(uuid.uuid4())
        
        # 提取模板中的变量
        self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """提取模板中的变量"""
        pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(pattern, self.content)
        return list(set(variables))
    
    def render(self, **kwargs) -> str:
        """渲染模板"""
        try:
            # 检查必需变量
            missing_vars = [var for var in self.variables if var not in kwargs]
            if missing_vars:
                raise ValueError(f"Missing required variables: {missing_vars}")
            
            # 渲染模板
            rendered = self.content
            for var, value in kwargs.items():
                placeholder = f"{{{{{var}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render template {self.template_id}: {e}")
            raise
    
    def add_example(self, input_data: Dict[str, Any], output: str, metadata: Dict[str, Any] = None):
        """添加示例"""
        example = {
            "input": input_data,
            "output": output,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        self.examples.append(example)
        self.updated_at = datetime.now()
    
    def get_examples(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取示例"""
        return self.examples[-limit:] if limit else self.examples
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template_type": self.template_type.value,
            "category": self.category.value,
            "content": self.content,
            "variables": self.variables,
            "examples": self.examples,
            "metadata": self.metadata,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """从字典创建模板"""
        return cls(
            template_id=data.get("template_id", ""),
            name=data["name"],
            description=data["description"],
            template_type=TemplateType(data["template_type"]),
            category=PromptCategory(data["category"]),
            content=data["content"],
            variables=data.get("variables", []),
            examples=data.get("examples", []),
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            tags=data.get("tags", [])
        )


class PromptTemplateRegistry:
    """提示词模板注册表"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        default_templates = [
            # 通用系统提示词
            PromptTemplate(
                template_id="system_assistant",
                name="通用助手系统提示词",
                description="通用的AI助手系统提示词模板",
                template_type=TemplateType.SYSTEM_PROMPT,
                category=PromptCategory.GENERAL,
                content="""You are a helpful AI assistant. You are designed to help users with various tasks.

Your capabilities include:
- Answering questions and providing information
- Helping with problem-solving and analysis
- Assisting with creative tasks
- Supporting learning and education

Guidelines:
- Be helpful, accurate, and honest
- If you're not sure about something, say so
- Provide clear and concise responses
- Be respectful and professional
- Follow user instructions carefully

Current context: {{context}}""",
                variables=["context"]
            ),
            
            # 编程助手
            PromptTemplate(
                template_id="programming_assistant",
                name="编程助手系统提示词",
                description="专门用于编程任务的系统提示词",
                template_type=TemplateType.SYSTEM_PROMPT,
                category=PromptCategory.PROGRAMMING,
                content="""You are an expert programming assistant specializing in {{languages}}.

Your programming expertise includes:
- Code review and optimization
- Debugging and problem-solving
- Best practices and design patterns
- Documentation and comments
- Testing and quality assurance

Guidelines:
- Write clean, readable, and maintainable code
- Follow language-specific conventions and best practices
- Provide explanations for complex logic
- Suggest improvements and alternatives
- Include error handling where appropriate
- Consider performance and security implications

Current project: {{project_name}}
Programming languages: {{languages}}
Code style: {{code_style}}""",
                variables=["languages", "project_name", "code_style"]
            ),
            
            # 分析助手
            PromptTemplate(
                template_id="analysis_assistant",
                name="分析助手系统提示词",
                description="专门用于数据分析任务的系统提示词",
                template_type=TemplateType.SYSTEM_PROMPT,
                category=PromptCategory.ANALYSIS,
                content="""You are an expert data analyst and researcher.

Your analysis capabilities include:
- Data interpretation and insights
- Statistical analysis and modeling
- Trend identification and forecasting
- Comparative analysis and benchmarking
- Report generation and visualization

Guidelines:
- Provide evidence-based insights
- Use clear and logical reasoning
- Consider multiple perspectives
- Highlight key findings and implications
- Suggest actionable recommendations
- Be objective and unbiased

Analysis type: {{analysis_type}}
Data context: {{data_context}}
Output format: {{output_format}}""",
                variables=["analysis_type", "data_context", "output_format"]
            ),
            
            # 多Agent协作
            PromptTemplate(
                template_id="multi_agent_collaboration",
                name="多Agent协作提示词",
                description="用于多Agent协作场景的提示词模板",
                template_type=TemplateType.MULTI_AGENT,
                category=PromptCategory.COLLABORATION,
                content="""You are part of a multi-agent team working on: {{task_description}}

Your role: {{agent_role}}
Your expertise: {{expertise}}
Your responsibilities: {{responsibilities}}

Collaboration guidelines:
- Communicate clearly with other agents
- Share relevant information and insights
- Coordinate actions and avoid conflicts
- Support team goals and objectives
- Provide constructive feedback
- Maintain professional relationships

Team members: {{team_members}}
Current phase: {{current_phase}}
Next steps: {{next_steps}}""",
                variables=["task_description", "agent_role", "expertise", "responsibilities", 
                          "team_members", "current_phase", "next_steps"]
            ),
            
            # 工作流步骤
            PromptTemplate(
                template_id="workflow_step",
                name="工作流步骤提示词",
                description="用于工作流步骤执行的提示词模板",
                template_type=TemplateType.WORKFLOW,
                category=PromptCategory.WORKFLOW,
                content="""You are executing a workflow step in the context of: {{workflow_name}}

Step information:
- Step name: {{step_name}}
- Step type: {{step_type}}
- Step description: {{step_description}}
- Expected output: {{expected_output}}

Execution context:
- Previous steps: {{previous_steps}}
- Current input: {{current_input}}
- Available resources: {{available_resources}}
- Constraints: {{constraints}}

Instructions:
- Execute this step according to the specifications
- Use the provided input and resources
- Generate the expected output format
- Handle any errors or exceptions appropriately
- Update the execution status

Step configuration: {{step_config}}""",
                variables=["workflow_name", "step_name", "step_type", "step_description",
                          "expected_output", "previous_steps", "current_input", 
                          "available_resources", "constraints", "step_config"]
            )
        ]
        
        for template in default_templates:
            self.register_template(template)
    
    def register_template(self, template: PromptTemplate) -> None:
        """注册模板"""
        self.templates[template.template_id] = template
        logger.info(f"Registered prompt template: {template.name} ({template.template_id})")
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def find_templates(self, 
                      template_type: Optional[TemplateType] = None,
                      category: Optional[PromptCategory] = None,
                      tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """查找模板"""
        results = []
        
        for template in self.templates.values():
            if template_type and template.template_type != template_type:
                continue
            if category and template.category != category:
                continue
            if tags and not any(tag in template.tags for tag in tags):
                continue
            results.append(template)
        
        return results
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有模板"""
        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "template_type": template.template_type.value,
                "category": template.category.value,
                "variables": template.variables,
                "version": template.version,
                "tags": template.tags
            }
            for template in self.templates.values()
        ]
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"Deleted prompt template: {template_id}")
            return True
        return False
    
    def export_templates(self, template_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """导出模板"""
        if template_ids is None:
            templates_to_export = self.templates.values()
        else:
            templates_to_export = [
                self.templates[tid] for tid in template_ids 
                if tid in self.templates
            ]
        
        return {
            "exported_at": datetime.now().isoformat(),
            "templates": [template.to_dict() for template in templates_to_export]
        }
    
    def import_templates(self, templates_data: Dict[str, Any]) -> List[str]:
        """导入模板"""
        imported_ids = []
        
        for template_data in templates_data.get("templates", []):
            try:
                template = PromptTemplate.from_dict(template_data)
                self.register_template(template)
                imported_ids.append(template.template_id)
            except Exception as e:
                logger.error(f"Failed to import template: {e}")
        
        return imported_ids 