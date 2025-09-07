"""
Prompt Converter - 提示词转换器
提供不同框架间的提示词格式转换功能
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PromptConverter:
    """提示词转换器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.conversion_rules = self._load_conversion_rules()
    
    def _load_conversion_rules(self) -> Dict[str, Dict[str, Any]]:
        """加载转换规则"""
        return {
            "openai": {
                "system_format": "system",
                "user_format": "user",
                "assistant_format": "assistant",
                "function_format": "function"
            },
            "autogen": {
                "system_format": "system_message",
                "user_format": "user_message",
                "assistant_format": "assistant_message",
                "function_format": "function_call"
            },
            "langgraph": {
                "system_format": "system",
                "user_format": "user",
                "assistant_format": "assistant",
                "function_format": "function"
            },
            "crewai": {
                "system_format": "role",
                "user_format": "task",
                "assistant_format": "response",
                "function_format": "tools"
            }
        }
    
    async def convert_prompt(self,
                           prompt: str,
                           source_format: str,
                           target_format: str) -> str:
        """转换提示词格式"""
        try:
            if source_format == target_format:
                return prompt
            
            # 获取转换规则
            source_rules = self.conversion_rules.get(source_format, {})
            target_rules = self.conversion_rules.get(target_format, {})
            
            if not source_rules or not target_rules:
                self.logger.warning(f"Unsupported format conversion: {source_format} -> {target_format}")
                return prompt
            
            # 执行转换
            converted_prompt = self._apply_conversion_rules(
                prompt, source_rules, target_rules
            )
            
            self.logger.info(f"Converted prompt from {source_format} to {target_format}")
            return converted_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to convert prompt: {e}")
            return prompt
    
    def _apply_conversion_rules(self,
                               prompt: str,
                               source_rules: Dict[str, Any],
                               target_rules: Dict[str, Any]) -> str:
        """应用转换规则"""
        converted = prompt
        
        # 转换系统消息格式
        if "system" in source_rules and "system" in target_rules:
            converted = self._convert_system_format(converted, source_rules, target_rules)
        
        # 转换用户消息格式
        if "user" in source_rules and "user" in target_rules:
            converted = self._convert_user_format(converted, source_rules, target_rules)
        
        # 转换助手消息格式
        if "assistant" in source_rules and "assistant" in target_rules:
            converted = self._convert_assistant_format(converted, source_rules, target_rules)
        
        # 转换函数调用格式
        if "function" in source_rules and "function" in target_rules:
            converted = self._convert_function_format(converted, source_rules, target_rules)
        
        return converted
    
    def _convert_system_format(self,
                              prompt: str,
                              source_rules: Dict[str, Any],
                              target_rules: Dict[str, Any]) -> str:
        """转换系统消息格式"""
        converted = prompt
        
        # OpenAI -> AutoGen
        if source_rules.get("system_format") == "system" and target_rules.get("system_format") == "system_message":
            converted = re.sub(r'<system>', '<system_message>', converted)
            converted = re.sub(r'</system>', '</system_message>', converted)
        
        # AutoGen -> OpenAI
        elif source_rules.get("system_format") == "system_message" and target_rules.get("system_format") == "system":
            converted = re.sub(r'<system_message>', '<system>', converted)
            converted = re.sub(r'</system_message>', '</system>', converted)
        
        # CrewAI -> OpenAI
        elif source_rules.get("system_format") == "role" and target_rules.get("system_format") == "system":
            converted = re.sub(r'<role>', '<system>', converted)
            converted = re.sub(r'</role>', '</system>', converted)
        
        return converted
    
    def _convert_user_format(self,
                            prompt: str,
                            source_rules: Dict[str, Any],
                            target_rules: Dict[str, Any]) -> str:
        """转换用户消息格式"""
        converted = prompt
        
        # OpenAI -> AutoGen
        if source_rules.get("user_format") == "user" and target_rules.get("user_format") == "user_message":
            converted = re.sub(r'<user>', '<user_message>', converted)
            converted = re.sub(r'</user>', '</user_message>', converted)
        
        # AutoGen -> OpenAI
        elif source_rules.get("user_format") == "user_message" and target_rules.get("user_format") == "user":
            converted = re.sub(r'<user_message>', '<user>', converted)
            converted = re.sub(r'</user_message>', '</user>', converted)
        
        # CrewAI -> OpenAI
        elif source_rules.get("user_format") == "task" and target_rules.get("user_format") == "user":
            converted = re.sub(r'<task>', '<user>', converted)
            converted = re.sub(r'</task>', '</user>', converted)
        
        return converted
    
    def _convert_assistant_format(self,
                                 prompt: str,
                                 source_rules: Dict[str, Any],
                                 target_rules: Dict[str, Any]) -> str:
        """转换助手消息格式"""
        converted = prompt
        
        # OpenAI -> AutoGen
        if source_rules.get("assistant_format") == "assistant" and target_rules.get("assistant_format") == "assistant_message":
            converted = re.sub(r'<assistant>', '<assistant_message>', converted)
            converted = re.sub(r'</assistant>', '</assistant_message>', converted)
        
        # AutoGen -> OpenAI
        elif source_rules.get("assistant_format") == "assistant_message" and target_rules.get("assistant_format") == "assistant":
            converted = re.sub(r'<assistant_message>', '<assistant>', converted)
            converted = re.sub(r'</assistant_message>', '</assistant>', converted)
        
        # CrewAI -> OpenAI
        elif source_rules.get("assistant_format") == "response" and target_rules.get("assistant_format") == "assistant":
            converted = re.sub(r'<response>', '<assistant>', converted)
            converted = re.sub(r'</response>', '</assistant>', converted)
        
        return converted
    
    def _convert_function_format(self,
                                prompt: str,
                                source_rules: Dict[str, Any],
                                target_rules: Dict[str, Any]) -> str:
        """转换函数调用格式"""
        converted = prompt
        
        # OpenAI -> AutoGen
        if source_rules.get("function_format") == "function" and target_rules.get("function_format") == "function_call":
            converted = re.sub(r'<function>', '<function_call>', converted)
            converted = re.sub(r'</function>', '</function_call>', converted)
        
        # AutoGen -> OpenAI
        elif source_rules.get("function_format") == "function_call" and target_rules.get("function_format") == "function":
            converted = re.sub(r'<function_call>', '<function>', converted)
            converted = re.sub(r'</function_call>', '</function>', converted)
        
        # CrewAI -> OpenAI
        elif source_rules.get("function_format") == "tools" and target_rules.get("function_format") == "function":
            converted = re.sub(r'<tools>', '<function>', converted)
            converted = re.sub(r'</tools>', '</function>', converted)
        
        return converted
    
    def convert_to_openai_format(self, prompt: str, source_format: str) -> str:
        """转换为OpenAI格式"""
        return self._apply_conversion_rules(
            prompt,
            self.conversion_rules.get(source_format, {}),
            self.conversion_rules.get("openai", {})
        )
    
    def convert_to_autogen_format(self, prompt: str, source_format: str) -> str:
        """转换为AutoGen格式"""
        return self._apply_conversion_rules(
            prompt,
            self.conversion_rules.get(source_format, {}),
            self.conversion_rules.get("autogen", {})
        )
    
    def convert_to_langgraph_format(self, prompt: str, source_format: str) -> str:
        """转换为LangGraph格式"""
        return self._apply_conversion_rules(
            prompt,
            self.conversion_rules.get(source_format, {}),
            self.conversion_rules.get("langgraph", {})
        )
    
    def convert_to_crewai_format(self, prompt: str, source_format: str) -> str:
        """转换为CrewAI格式"""
        return self._apply_conversion_rules(
            prompt,
            self.conversion_rules.get(source_format, {}),
            self.conversion_rules.get("crewai", {})
        )
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        return list(self.conversion_rules.keys())
    
    def validate_format(self, format_name: str) -> bool:
        """验证格式是否支持"""
        return format_name in self.conversion_rules 