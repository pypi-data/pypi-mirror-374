"""
Prompt Analyzer - 提示词分析器
提供提示词的质量分析和评估功能
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptAnalyzer:
    """提示词分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.analysis_rules = self._load_analysis_rules()
    
    def _load_analysis_rules(self) -> Dict[str, Any]:
        """加载分析规则"""
        return {
            "quality_indicators": {
                "clarity": ["clear", "specific", "detailed", "precise", "explicit"],
                "structure": ["guidelines:", "instructions:", "steps:", "format:", "example:"],
                "specificity": ["{{", "}}", "specific", "concrete", "detailed"],
                "completeness": ["complete", "comprehensive", "thorough", "full"],
                "consistency": ["consistent", "uniform", "standardized"]
            },
            "risk_indicators": {
                "vague": ["maybe", "perhaps", "possibly", "might", "could"],
                "ambiguous": ["unclear", "vague", "ambiguous", "unclear"],
                "incomplete": ["incomplete", "partial", "missing", "lacking"],
                "conflicting": ["but", "however", "although", "nevertheless"]
            },
            "best_practices": {
                "role_definition": ["you are", "your role", "your purpose"],
                "context_provided": ["context:", "background:", "situation:"],
                "output_format": ["format:", "output:", "response format:"],
                "constraints": ["constraints:", "limitations:", "requirements:"]
            }
        }
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """分析提示词"""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()),
                "quality_scores": {},
                "risk_assessment": {},
                "best_practices": {},
                "suggestions": [],
                "overall_score": 0
            }
            
            # 质量评分
            analysis["quality_scores"] = self._analyze_quality(prompt)
            
            # 风险评估
            analysis["risk_assessment"] = self._assess_risks(prompt)
            
            # 最佳实践检查
            analysis["best_practices"] = self._check_best_practices(prompt)
            
            # 生成建议
            analysis["suggestions"] = self._generate_suggestions(analysis)
            
            # 计算总体评分
            analysis["overall_score"] = self._calculate_overall_score(analysis)
            
            self.logger.info(f"Prompt analysis completed. Overall score: {analysis['overall_score']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze prompt: {e}")
            return {"error": str(e)}
    
    def _analyze_quality(self, prompt: str) -> Dict[str, float]:
        """分析质量指标"""
        quality_scores = {}
        prompt_lower = prompt.lower()
        
        for indicator, keywords in self.analysis_rules["quality_indicators"].items():
            score = 0
            for keyword in keywords:
                if keyword in prompt_lower:
                    score += 1
            
            # 标准化评分 (0-100)
            max_score = len(keywords)
            quality_scores[indicator] = (score / max_score) * 100 if max_score > 0 else 0
        
        return quality_scores
    
    def _assess_risks(self, prompt: str) -> Dict[str, Any]:
        """评估风险"""
        risk_assessment = {
            "risk_level": "low",
            "risk_factors": [],
            "risk_score": 0
        }
        
        prompt_lower = prompt.lower()
        total_risks = 0
        
        for risk_type, keywords in self.analysis_rules["risk_indicators"].items():
            risk_count = sum(1 for keyword in keywords if keyword in prompt_lower)
            if risk_count > 0:
                risk_assessment["risk_factors"].append({
                    "type": risk_type,
                    "count": risk_count,
                    "keywords": [k for k in keywords if k in prompt_lower]
                })
                total_risks += risk_count
        
        # 计算风险评分
        risk_assessment["risk_score"] = min(total_risks * 10, 100)
        
        # 确定风险等级
        if risk_assessment["risk_score"] >= 70:
            risk_assessment["risk_level"] = "high"
        elif risk_assessment["risk_score"] >= 40:
            risk_assessment["risk_level"] = "medium"
        else:
            risk_assessment["risk_level"] = "low"
        
        return risk_assessment
    
    def _check_best_practices(self, prompt: str) -> Dict[str, Any]:
        """检查最佳实践"""
        best_practices = {
            "practices_followed": [],
            "practices_missing": [],
            "compliance_score": 0
        }
        
        prompt_lower = prompt.lower()
        total_practices = len(self.analysis_rules["best_practices"])
        followed_practices = 0
        
        for practice, keywords in self.analysis_rules["best_practices"].items():
            if any(keyword in prompt_lower for keyword in keywords):
                best_practices["practices_followed"].append(practice)
                followed_practices += 1
            else:
                best_practices["practices_missing"].append(practice)
        
        # 计算合规评分
        best_practices["compliance_score"] = (followed_practices / total_practices) * 100 if total_practices > 0 else 0
        
        return best_practices
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于质量评分的建议
        quality_scores = analysis["quality_scores"]
        if quality_scores.get("clarity", 0) < 60:
            suggestions.append("Add more specific and clear instructions")
        
        if quality_scores.get("structure", 0) < 60:
            suggestions.append("Include structured guidelines or step-by-step instructions")
        
        if quality_scores.get("specificity", 0) < 60:
            suggestions.append("Add more specific details and concrete examples")
        
        # 基于风险评估的建议
        risk_assessment = analysis["risk_assessment"]
        if risk_assessment["risk_level"] == "high":
            suggestions.append("Reduce ambiguous language and clarify instructions")
        
        if risk_assessment["risk_level"] == "medium":
            suggestions.append("Review and clarify potentially unclear instructions")
        
        # 基于最佳实践的建议
        best_practices = analysis["best_practices"]
        missing_practices = best_practices.get("practices_missing", [])
        
        if "role_definition" in missing_practices:
            suggestions.append("Clearly define the AI's role and purpose")
        
        if "context_provided" in missing_practices:
            suggestions.append("Provide relevant context and background information")
        
        if "output_format" in missing_practices:
            suggestions.append("Specify the expected output format")
        
        if "constraints" in missing_practices:
            suggestions.append("Include any constraints or limitations")
        
        # 基于长度的建议
        if analysis["prompt_length"] < 100:
            suggestions.append("Consider adding more context and details")
        
        if analysis["prompt_length"] > 2000:
            suggestions.append("Consider breaking down into smaller, focused prompts")
        
        return suggestions
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """计算总体评分"""
        # 质量评分权重
        quality_weight = 0.4
        quality_score = sum(analysis["quality_scores"].values()) / len(analysis["quality_scores"]) if analysis["quality_scores"] else 0
        
        # 风险评分权重 (风险越低越好)
        risk_weight = 0.3
        risk_score = 100 - analysis["risk_assessment"]["risk_score"]
        
        # 最佳实践评分权重
        practice_weight = 0.3
        practice_score = analysis["best_practices"]["compliance_score"]
        
        # 计算加权总分
        overall_score = (
            quality_score * quality_weight +
            risk_score * risk_weight +
            practice_score * practice_weight
        )
        
        return round(overall_score, 2)
    
    def analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """分析提示词复杂度"""
        complexity = {
            "readability_score": 0,
            "cognitive_load": "low",
            "complexity_factors": [],
            "simplification_suggestions": []
        }
        
        # 计算可读性评分 (简化的Flesch Reading Ease)
        sentences = re.split(r'[.!?]+', prompt)
        words = prompt.split()
        syllables = self._count_syllables(prompt)
        
        if len(sentences) > 0 and len(words) > 0:
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words) if len(words) > 0 else 0
            
            # 简化的可读性公式
            readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            complexity["readability_score"] = max(0, min(100, readability_score))
        
        # 评估认知负荷
        if complexity["readability_score"] >= 80:
            complexity["cognitive_load"] = "low"
        elif complexity["readability_score"] >= 60:
            complexity["cognitive_load"] = "medium"
        else:
            complexity["cognitive_load"] = "high"
        
        # 识别复杂度因素
        if avg_sentence_length > 20:
            complexity["complexity_factors"].append("Long sentences")
            complexity["simplification_suggestions"].append("Break down long sentences")
        
        if avg_syllables_per_word > 2:
            complexity["complexity_factors"].append("Complex vocabulary")
            complexity["simplification_suggestions"].append("Use simpler words")
        
        if len(sentences) > 10:
            complexity["complexity_factors"].append("Too many sentences")
            complexity["simplification_suggestions"].append("Combine related sentences")
        
        return complexity
    
    def _count_syllables(self, text: str) -> int:
        """计算音节数 (简化版本)"""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return count
    
    def analyze_prompt_effectiveness(self, prompt: str, expected_outcome: str = "") -> Dict[str, Any]:
        """分析提示词有效性"""
        effectiveness = {
            "goal_clarity": 0,
            "action_orientation": 0,
            "measurability": 0,
            "effectiveness_score": 0,
            "improvement_areas": []
        }
        
        prompt_lower = prompt.lower()
        
        # 目标清晰度
        goal_indicators = ["goal", "objective", "purpose", "aim", "target"]
        effectiveness["goal_clarity"] = sum(1 for indicator in goal_indicators if indicator in prompt_lower) * 20
        
        # 行动导向
        action_indicators = ["do", "perform", "execute", "create", "generate", "analyze", "solve"]
        effectiveness["action_orientation"] = sum(1 for indicator in action_indicators if indicator in prompt_lower) * 15
        
        # 可测量性
        measurable_indicators = ["format:", "output:", "response:", "result:", "example:"]
        effectiveness["measurability"] = sum(1 for indicator in measurable_indicators if indicator in prompt_lower) * 20
        
        # 计算有效性评分
        effectiveness["effectiveness_score"] = min(
            effectiveness["goal_clarity"] + 
            effectiveness["action_orientation"] + 
            effectiveness["measurability"], 
            100
        )
        
        # 识别改进领域
        if effectiveness["goal_clarity"] < 40:
            effectiveness["improvement_areas"].append("Clarify the goal or objective")
        
        if effectiveness["action_orientation"] < 30:
            effectiveness["improvement_areas"].append("Add specific actions to be performed")
        
        if effectiveness["measurability"] < 40:
            effectiveness["improvement_areas"].append("Specify expected output format")
        
        return effectiveness 