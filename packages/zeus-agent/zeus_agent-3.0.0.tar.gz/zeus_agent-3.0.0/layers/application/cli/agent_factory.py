#!/usr/bin/env python3
"""
Agent Factory - Zeus开发体验层核心组件
真正的Agent创建、管理和部署工厂

核心功能:
- 声明式Agent创建
- 模板驱动开发 
- 配置自动生成
- 知识库自动集成
- 最佳实践内置
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """Agent类型"""
    OPENAI = "openai"
    AUTOGEN = "autogen" 
    LANGGRAPH = "langgraph"
    FPGA_EXPERT = "fpga_expert"
    CODE_EXPERT = "code_expert"
    DATA_ANALYST = "data_analyst"
    CUSTOM = "custom"


class TemplateType(Enum):
    """模板类型"""
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    FPGA_BASIC = "fpga_basic"
    FPGA_ADVANCED = "fpga_advanced"
    VERIFICATION_EXPERT = "verification_expert"


@dataclass
class AgentSpec:
    """Agent规格定义"""
    name: str
    agent_type: AgentType
    template_type: TemplateType
    model: str
    capabilities: List[str]
    knowledge_domains: List[str]
    system_message: Optional[str] = None
    workspace_path: Optional[str] = None
    config_overrides: Optional[Dict] = None


@dataclass
class AgentCreationResult:
    """Agent创建结果"""
    success: bool
    agent_path: Path
    config_path: Path
    main_script: Path
    generated_files: List[Path]
    error_message: Optional[str] = None


class AgentTemplateManager:
    """Agent模板管理器"""
    
    def __init__(self, templates_root: Path):
        self.templates_root = templates_root
        self.ensure_template_structure()
    
    def ensure_template_structure(self):
        """确保模板目录结构存在"""
        template_dirs = [
            "agent_templates/basic",
            "agent_templates/advanced", 
            "agent_templates/enterprise",
            "agent_templates/fpga_expert",
            "agent_templates/verification_expert",
            "project_templates",
            "capability_templates",
            "knowledge_templates"
        ]
        
        for dir_path in template_dirs:
            (self.templates_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_template_config(self, template_type: TemplateType) -> Dict:
        """获取模板配置"""
        template_configs = {
            TemplateType.BASIC: {
                "base_capabilities": ["chat", "information_retrieval"],
                "knowledge_domains": ["general"],
                "file_templates": ["basic_agent.py", "config.yaml", "requirements.txt"],
                "dependencies": ["openai", "pyyaml", "rich"]
            },
            TemplateType.ADVANCED: {
                "base_capabilities": ["chat", "information_retrieval", "code_generation", "analysis"],
                "knowledge_domains": ["general", "programming"],
                "file_templates": ["advanced_agent.py", "config.yaml", "knowledge_config.yaml", "requirements.txt"],
                "dependencies": ["openai", "pyyaml", "rich", "langchain", "chromadb"]
            },
            TemplateType.FPGA_ADVANCED: {
                "base_capabilities": ["testbench_generation", "timing_analysis", "synthesis_optimization", "debug_assistance"],
                "knowledge_domains": ["fpga", "verilog", "verification", "timing"],
                "file_templates": ["fpga_expert_agent.py", "fpga_config.yaml", "fpga_knowledge.yaml", "fpga_templates.yaml"],
                "dependencies": ["openai", "pyyaml", "rich", "pathlib", "re"]
            },
            TemplateType.VERIFICATION_EXPERT: {
                "base_capabilities": ["testbench_generation", "coverage_analysis", "assertion_generation", "uvm_support"],
                "knowledge_domains": ["verification", "uvm", "systemverilog", "coverage"],
                "file_templates": ["verification_expert.py", "verification_config.yaml", "uvm_templates.yaml"],
                "dependencies": ["openai", "pyyaml", "rich", "jinja2"]
            }
        }
        
        return template_configs.get(template_type, template_configs[TemplateType.BASIC])
    
    def generate_agent_files(self, spec: AgentSpec, target_path: Path) -> List[Path]:
        """生成Agent文件"""
        template_config = self.get_template_config(spec.template_type)
        generated_files = []
        
        # 创建目录结构
        self.create_agent_structure(target_path)
        
        # 生成主配置文件
        config_file = self.generate_config_file(spec, target_path, template_config)
        generated_files.append(config_file)
        
        # 生成主Agent文件
        agent_file = self.generate_agent_file(spec, target_path, template_config)
        generated_files.append(agent_file)
        
        # 生成requirements.txt
        req_file = self.generate_requirements_file(spec, target_path, template_config)
        generated_files.append(req_file)
        
        # 生成README.md
        readme_file = self.generate_readme_file(spec, target_path)
        generated_files.append(readme_file)
        
        # 为FPGA专家生成额外文件
        if spec.agent_type == AgentType.FPGA_EXPERT:
            additional_files = self.generate_fpga_specific_files(spec, target_path)
            generated_files.extend(additional_files)
        
        return generated_files
    
    def create_agent_structure(self, target_path: Path):
        """创建Agent目录结构"""
        dirs = [
            "config",
            "knowledge", 
            "templates",
            "tests",
            "tools",
            "adapters"
        ]
        
        for dir_name in dirs:
            (target_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def generate_config_file(self, spec: AgentSpec, target_path: Path, template_config: Dict) -> Path:
        """生成配置文件"""
        config = {
            "agent": {
                "name": spec.name,
                "version": "1.0.0",
                "type": spec.agent_type.value,
                "description": f"Zeus平台{spec.name} Agent",
                "created_at": datetime.now().isoformat(),
                "model": spec.model,
                "system_message": spec.system_message or f"You are {spec.name}, an AI assistant built on Zeus AI Platform."
            },
            "capabilities": {cap: {"enabled": True} for cap in spec.capabilities},
            "knowledge_domains": {domain: {"priority": "high"} for domain in spec.knowledge_domains},
            "zeus_integration": {
                "enhanced_rag": True,
                "semantic_cache": True,
                "intelligent_routing": True,
                "reinforcement_learning": True,
                "performance_monitoring": True
            },
            "ai_backend": {
                "provider": "openai",
                "model": spec.model,
                "max_tokens": 4000,
                "temperature": 0.7
            }
        }
        
        # 应用配置覆盖
        if spec.config_overrides:
            config.update(spec.config_overrides)
        
        config_path = target_path / "config" / f"{spec.name.lower()}.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, indent=2, allow_unicode=True)
        
        return config_path
    
    def generate_agent_file(self, spec: AgentSpec, target_path: Path, template_config: Dict) -> Path:
        """生成主Agent文件"""
        if spec.agent_type == AgentType.FPGA_EXPERT:
            agent_code = self.generate_fpga_expert_code(spec)
        else:
            agent_code = self.generate_basic_agent_code(spec)
        
        agent_path = target_path / f"{spec.name.lower()}_agent.py"
        with open(agent_path, 'w', encoding='utf-8') as f:
            f.write(agent_code)
        
        return agent_path
    
    def generate_fpga_expert_code(self, spec: AgentSpec) -> str:
        """生成FPGA专家Agent代码"""
        return f'''#!/usr/bin/env python3
"""
{spec.name} - FPGA设计专家Agent
基于Zeus AI Platform构建

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Zeus Platform Version: 2.0.0
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Zeus平台导入 - 正确的开发体验层接口
from zeus import Agent, capability, knowledge_enhanced, fpga_tools
from zeus.domains import FPGADomain, VerificationDomain
from zeus.capabilities import TestbenchGeneration, TimingAnalysis, SynthesisOptimization


@Agent.create(config="{spec.name.lower()}.yaml")
class {spec.name}Agent:
    """
    {spec.name} - Zeus平台FPGA设计专家
    
    核心能力:
    - 智能Testbench生成
    - 时序分析和优化
    - 综合优化建议
    - FPGA调试支持
    """
    
    @capability("testbench_generation")
    @knowledge_enhanced(domain=FPGADomain.VERIFICATION)
    async def generate_testbench(self, module_file: str, 
                                test_scenarios: List[str] = None,
                                coverage_target: float = 0.95) -> Dict[str, Any]:
        """
        智能生成Verilog testbench
        
        Args:
            module_file: Verilog模块文件路径
            test_scenarios: 测试场景列表 ["basic", "edge_case", "stress"]
            coverage_target: 目标覆盖率 (0.0-1.0)
        
        Returns:
            生成结果包含testbench代码、覆盖率报告、质量评分
        """
        # Zeus自动处理知识检索、模板匹配、代码生成
        result = await self.zeus.generate_with_templates(
            template_type="verilog_testbench",
            context={{
                "module_file": module_file,
                "test_scenarios": test_scenarios or ["basic"],
                "coverage_target": coverage_target
            }}
        )
        
        return result
    
    @capability("timing_analysis")
    @knowledge_enhanced(domain=FPGADomain.TIMING)
    async def analyze_timing(self, design_file: str, 
                           constraints_file: str = None,
                           target_frequency: float = None) -> Dict[str, Any]:
        """
        时序分析和优化建议
        
        Args:
            design_file: 设计文件路径
            constraints_file: 时序约束文件
            target_frequency: 目标频率 (MHz)
        
        Returns:
            时序分析结果和优化建议
        """
        result = await self.zeus.analyze_with_tools(
            analysis_type="timing",
            inputs={{
                "design": design_file,
                "constraints": constraints_file,
                "frequency": target_frequency
            }}
        )
        
        return result
    
    @capability("synthesis_optimization")
    @knowledge_enhanced(domain=FPGADomain.SYNTHESIS)
    async def optimize_synthesis(self, design_file: str,
                               optimization_goal: str = "balanced") -> Dict[str, Any]:
        """
        综合优化建议
        
        Args:
            design_file: 设计文件路径
            optimization_goal: 优化目标 ["area", "speed", "power", "balanced"]
        
        Returns:
            优化建议和预期效果
        """
        result = await self.zeus.optimize_design(
            design_file=design_file,
            goal=optimization_goal,
            domain="fpga_synthesis"
        )
        
        return result
    
    @capability("debug_assistance")
    @knowledge_enhanced(domain=FPGADomain.DEBUG)
    async def debug_issue(self, error_description: str,
                         design_files: List[str] = None,
                         log_files: List[str] = None) -> Dict[str, Any]:
        """
        FPGA调试助手
        
        Args:
            error_description: 错误描述
            design_files: 相关设计文件
            log_files: 错误日志文件
        
        Returns:
            问题分析和解决方案
        """
        result = await self.zeus.diagnose_and_solve(
            problem=error_description,
            context_files=design_files or [],
            logs=log_files or [],
            domain="fpga_debug"
        )
        
        return result


# 演示函数
async def demo_{spec.name.lower()}():
    """演示{spec.name}的核心功能"""
    agent = {spec.name}Agent()
    
    print(f"🚀 {spec.name} FPGA专家Agent演示")
    print("=" * 50)
    
    # 演示testbench生成
    print("\\n📝 演示: 智能Testbench生成")
    tb_result = await agent.generate_testbench(
        module_file="counter.v",
        test_scenarios=["basic", "edge_case"],
        coverage_target=0.95
    )
    print(f"   生成结果: {{tb_result.get('status', 'success')}}")
    
    # 演示时序分析
    print("\\n⏱️  演示: 时序分析")
    timing_result = await agent.analyze_timing(
        design_file="my_design.v",
        target_frequency=100.0
    )
    print(f"   分析结果: {{timing_result.get('status', 'success')}}")
    
    print("\\n✅ 演示完成！")


if __name__ == "__main__":
    asyncio.run(demo_{spec.name.lower()}())
'''
    
    def generate_basic_agent_code(self, spec: AgentSpec) -> str:
        """生成基础Agent代码"""
        return f'''#!/usr/bin/env python3
"""
{spec.name} - AI Assistant Agent
基于Zeus AI Platform构建

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import asyncio
from typing import Dict, List, Any

from zeus import Agent, capability, knowledge_enhanced


@Agent.create(config="{spec.name.lower()}.yaml")
class {spec.name}Agent:
    """
    {spec.name} - Zeus平台AI助手
    """
    
    @capability("chat")
    @knowledge_enhanced(domain="general")
    async def chat(self, message: str, context: Dict = None) -> str:
        """智能对话功能"""
        response = await self.zeus.chat(
            message=message,
            context=context or {{}}
        )
        return response
    
    @capability("information_retrieval")
    @knowledge_enhanced(domain="general")
    async def retrieve_information(self, query: str) -> Dict[str, Any]:
        """信息检索功能"""
        result = await self.zeus.retrieve(
            query=query,
            domain="general"
        )
        return result


if __name__ == "__main__":
    agent = {spec.name}Agent()
    print(f"🚀 {spec.name} Agent已启动")
'''
    
    def generate_requirements_file(self, spec: AgentSpec, target_path: Path, template_config: Dict) -> Path:
        """生成requirements.txt"""
        requirements = template_config.get("dependencies", ["openai", "pyyaml"])
        
        req_path = target_path / "requirements.txt"
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("# Zeus AI Platform Agent Dependencies\\n")
            f.write(f"# Generated for {spec.name} Agent\\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            for req in requirements:
                f.write(f"{req}\\n")
        
        return req_path
    
    def generate_readme_file(self, spec: AgentSpec, target_path: Path) -> Path:
        """生成README.md"""
        readme_content = f'''# {spec.name} Agent

> 基于Zeus AI Platform构建的智能Agent

## 🎯 Agent概述

**{spec.name}** 是运行在Zeus AI Platform上的{spec.agent_type.value}类型Agent，具备以下核心能力：

{chr(10).join([f"- {cap}" for cap in spec.capabilities])}

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置Agent
编辑 `config/{spec.name.lower()}.yaml` 文件，配置您的API密钥和偏好设置。

### 3. 运行Agent
```bash
python {spec.name.lower()}_agent.py
```

### 4. 使用Zeus CLI
```bash
# 启动对话
zeus agent chat --name {spec.name}

# 查看Agent信息
zeus agent info {spec.name}

# 部署Agent
zeus agent deploy {spec.name} --environment production
```

## 📋 功能详情

### 核心能力
{chr(10).join([f"- **{cap}**: Zeus平台自动化{cap}处理" for cap in spec.capabilities])}

### 知识领域
{chr(10).join([f"- **{domain}**: 专业{domain}知识库集成" for domain in spec.knowledge_domains])}

## 🛠️ 配置选项

Agent的行为可以通过 `config/{spec.name.lower()}.yaml` 文件进行配置：

- **AI后端**: OpenAI, Anthropic, 本地模型
- **知识增强**: 启用/禁用RAG系统
- **性能监控**: 响应时间、成本跟踪
- **语义缓存**: 提升响应速度和降低成本

## 📊 性能特性

基于Zeus AI Platform，{spec.name}具备：

- **智能路由**: 自动选择最佳知识源
- **语义缓存**: 平均21x响应速度提升
- **成本优化**: 高达99.9%的重复查询成本节省
- **自学习**: 基于反馈的强化学习优化

## 🔧 开发和扩展

### 添加新能力
```python
@capability("new_capability")
@knowledge_enhanced(domain="your_domain")
async def new_method(self, param: str) -> Dict:
    return await self.zeus.process(param)
```

### 自定义知识库
1. 将文档放入 `knowledge/` 目录
2. 运行 `zeus knowledge build --agent {spec.name}`
3. Agent自动集成新知识

## 📈 监控和调试

```bash
# 查看性能指标
zeus monitor --agent {spec.name}

# 查看路由决策日志
zeus logs --agent {spec.name} --type routing

# 分析缓存效果
zeus cache stats --agent {spec.name}
```

## 🤝 支持

- 📖 [Zeus Platform文档](https://github.com/fpga1988/zeus)
- 💬 [社区讨论](https://github.com/fpga1988/zeus/discussions)
- 🐛 [问题反馈](https://github.com/fpga1988/zeus/issues)

---

**由Zeus AI Platform自动生成** - {datetime.now().strftime('%Y年%m月%d日')}
'''
        
        readme_path = target_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_path
    
    def generate_fpga_specific_files(self, spec: AgentSpec, target_path: Path) -> List[Path]:
        """为FPGA专家生成特定文件"""
        generated_files = []
        
        # 生成FPGA知识配置
        fpga_knowledge_config = {
            "fpga_knowledge": {
                "verilog_patterns": {
                    "module_templates": "templates/verilog/",
                    "testbench_templates": "templates/testbench/",
                    "constraint_templates": "templates/constraints/"
                },
                "tool_configs": {
                    "vivado": {"version": "2023.1", "tcl_scripts": "tools/vivado/"},
                    "quartus": {"version": "22.1", "qsf_templates": "tools/quartus/"}
                },
                "verification_libraries": {
                    "uvm": {"version": "1.2", "base_classes": "knowledge/uvm/"},
                    "svunit": {"enabled": True, "test_templates": "templates/svunit/"}
                }
            }
        }
        
        fpga_config_path = target_path / "config" / "fpga_knowledge.yaml"
        with open(fpga_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(fpga_knowledge_config, f, indent=2)
        generated_files.append(fpga_config_path)
        
        # 创建模板目录和示例文件
        template_dirs = [
            "templates/verilog",
            "templates/testbench", 
            "templates/constraints",
            "tools/vivado",
            "tools/quartus",
            "knowledge/uvm"
        ]
        
        for template_dir in template_dirs:
            (target_path / template_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成示例Verilog模板
        counter_template = target_path / "templates" / "verilog" / "counter.v"
        with open(counter_template, 'w') as f:
            f.write('''// Counter Module Template
module counter #(
    parameter WIDTH = 4
)(
    input clk,
    input rst_n,
    input enable,
    output reg [WIDTH-1:0] count
);

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        count <= {WIDTH{1'b0}};
    end else if (enable) begin
        count <= count + 1;
    end
end

endmodule
''')
        generated_files.append(counter_template)
        
        return generated_files


class ZeusAgentFactory:
    """Zeus Agent工厂 - 开发体验层核心组件"""
    
    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path.cwd() / "workspace"
        self.agents_root = self.workspace_root / "agents"
        self.templates_root = Path(__file__).parent.parent.parent.parent / "cfg" / "templates"
        
        self.template_manager = AgentTemplateManager(self.templates_root)
        
        # 确保目录结构
        self.agents_root.mkdir(parents=True, exist_ok=True)
    
    async def create_agent(self, spec: AgentSpec) -> AgentCreationResult:
        """
        创建新Agent - Zeus开发体验层主入口
        
        Args:
            spec: Agent规格定义
            
        Returns:
            AgentCreationResult: 创建结果
        """
        try:
            # 1. 验证Agent规格
            validation_result = self._validate_spec(spec)
            if not validation_result["valid"]:
                return AgentCreationResult(
                    success=False,
                    agent_path=Path(),
                    config_path=Path(),
                    main_script=Path(),
                    generated_files=[],
                    error_message=validation_result["error"]
                )
            
            # 2. 确定Agent路径
            agent_path = self.agents_root / spec.name.lower()
            if agent_path.exists():
                return AgentCreationResult(
                    success=False,
                    agent_path=agent_path,
                    config_path=Path(),
                    main_script=Path(),
                    generated_files=[],
                    error_message=f"Agent {spec.name} already exists at {agent_path}"
                )
            
            # 3. 创建Agent目录
            agent_path.mkdir(parents=True)
            
            # 4. 生成Agent文件
            generated_files = self.template_manager.generate_agent_files(spec, agent_path)
            
            # 5. 确定主要文件路径
            config_path = agent_path / "config" / f"{spec.name.lower()}.yaml"
            main_script = agent_path / f"{spec.name.lower()}_agent.py"
            
            print(f"✅ 成功创建Agent: {spec.name}")
            print(f"   📁 位置: {agent_path}")
            print(f"   📋 配置: {config_path}")
            print(f"   🐍 主脚本: {main_script}")
            print(f"   📄 生成文件: {len(generated_files)}个")
            
            return AgentCreationResult(
                success=True,
                agent_path=agent_path,
                config_path=config_path,
                main_script=main_script,
                generated_files=generated_files
            )
            
        except Exception as e:
            return AgentCreationResult(
                success=False,
                agent_path=Path(),
                config_path=Path(),
                main_script=Path(),
                generated_files=[],
                error_message=f"创建Agent失败: {str(e)}"
            )
    
    def _validate_spec(self, spec: AgentSpec) -> Dict[str, Any]:
        """验证Agent规格"""
        if not spec.name or not spec.name.replace('_', '').isalnum():
            return {"valid": False, "error": "Agent名称无效，只能包含字母、数字和下划线"}
        
        if not spec.capabilities:
            return {"valid": False, "error": "至少需要指定一个能力"}
        
        if not spec.knowledge_domains:
            return {"valid": False, "error": "至少需要指定一个知识领域"}
        
        return {"valid": True}
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出已存在的Agent"""
        agents = []
        
        if not self.agents_root.exists():
            return agents
        
        for agent_dir in self.agents_root.iterdir():
            if agent_dir.is_dir():
                config_file = agent_dir / "config" / f"{agent_dir.name}.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        
                        agents.append({
                            "名称": config.get("agent", {}).get("name", agent_dir.name),
                            "类型": config.get("agent", {}).get("type", "unknown"),
                            "版本": config.get("agent", {}).get("version", "1.0.0"),
                            "路径": str(agent_dir),
                            "状态": "ready" if (agent_dir / f"{agent_dir.name}_agent.py").exists() else "incomplete"
                        })
                    except Exception:
                        agents.append({
                            "名称": agent_dir.name,
                            "类型": "unknown",
                            "版本": "unknown",
                            "路径": str(agent_dir),
                            "状态": "error"
                        })
        
        return agents
    
    async def delete_agent(self, agent_name: str, force: bool = False) -> bool:
        """删除Agent"""
        agent_path = self.agents_root / agent_name.lower()
        
        if not agent_path.exists():
            print(f"❌ Agent {agent_name} 不存在")
            return False
        
        if not force:
            confirm = input(f"确定要删除 {agent_name} 及其所有文件吗？(y/N): ")
            if confirm.lower() != 'y':
                return False
        
        try:
            shutil.rmtree(agent_path)
            print(f"✅ 已删除Agent: {agent_name}")
            return True
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False


# 使用示例和测试
if __name__ == "__main__":
    async def demo_agent_factory():
        factory = ZeusAgentFactory()
        
        # 创建FPGA专家Agent
        spec = AgentSpec(
            name="Ares",
            agent_type=AgentType.FPGA_EXPERT,
            template_type=TemplateType.FPGA_ADVANCED,
            model="gpt-4o-mini",
            capabilities=["testbench_generation", "timing_analysis", "synthesis_optimization", "debug_assistance"],
            knowledge_domains=["fpga", "verilog", "verification", "timing"],
            system_message="You are Ares, a professional FPGA design expert built on Zeus AI Platform."
        )
        
        result = await factory.create_agent(spec)
        if result.success:
            print(f"🎉 Agent创建成功！")
            print(f"   主文件: {result.main_script}")
        else:
            print(f"❌ 创建失败: {result.error_message}")
    
    asyncio.run(demo_agent_factory()) 