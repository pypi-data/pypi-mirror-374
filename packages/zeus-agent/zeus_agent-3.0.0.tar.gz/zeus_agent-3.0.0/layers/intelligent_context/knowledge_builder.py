"""
知识库构建器
支持多种格式的知识源，构建结构化的FPGA专业知识库

支持的知识源格式：
- Markdown文档 (.md)
- YAML结构化数据 (.yaml)
- JSON数据 (.json)
- 代码示例 (.v, .sv, .vhd)
- PDF技术文档
- 网页内容
- API文档
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import json
import re
import hashlib

from .integrated_knowledge_service import IntegratedKnowledgeService, KnowledgeItem

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeSource:
    """知识源定义"""
    name: str
    source_type: str  # markdown, yaml, json, verilog, pdf, web, api
    file_path: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1=highest, 5=lowest
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeChunk:
    """知识块"""
    content: str
    title: str
    source: str
    chunk_type: str  # concept, example, reference, pattern, best_practice
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)  # 关联的其他知识块


class KnowledgeBuilder:
    """
    知识库构建器
    
    功能：
    - 多格式知识源解析
    - 智能内容分块
    - 知识关系提取
    - 自动标签生成
    - 知识质量评估
    """
    
    def __init__(self, knowledge_service: IntegratedKnowledgeService):
        """初始化知识库构建器"""
        self.knowledge_service = knowledge_service
        self.sources: List[KnowledgeSource] = []
        self.chunks: List[KnowledgeChunk] = []
        
        # 知识分类模式
        self.knowledge_patterns = {
            'verilog_module': r'module\s+(\w+)',
            'always_block': r'always\s*@',
            'wire_declaration': r'wire\s+.*?;',
            'reg_declaration': r'reg\s+.*?;',
            'parameter': r'parameter\s+\w+\s*=',
            'testbench': r'module\s+tb_\w+',
            'constraint': r'constraint\s+\w+',
            'assertion': r'assert\s*\(',
            'timing_constraint': r'create_clock|set_input_delay|set_output_delay',
            'best_practice': r'(最佳实践|best practice|推荐|建议)',
            'common_mistake': r'(常见错误|错误|问题|注意)',
            'design_pattern': r'(设计模式|pattern|模板)'
        }
        
        logger.info("🏗️ 知识库构建器初始化完成")
    
    def add_source(self, source: KnowledgeSource):
        """添加知识源"""
        self.sources.append(source)
        logger.info(f"📋 添加知识源: {source.name} ({source.source_type})")
    
    async def build_knowledge_base(self, output_stats: bool = True) -> Dict[str, Any]:
        """构建知识库"""
        logger.info("🏗️ 开始构建FPGA知识库...")
        
        stats = {
            'sources_processed': 0,
            'chunks_created': 0,
            'knowledge_items_stored': 0,
            'processing_time': 0,
            'errors': []
        }
        
        start_time = datetime.now()
        
        try:
            # 1. 处理所有知识源
            for source in self.sources:
                try:
                    await self._process_source(source)
                    stats['sources_processed'] += 1
                except Exception as e:
                    error_msg = f"处理知识源失败 {source.name}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            # 2. 存储知识块到知识库
            for chunk in self.chunks:
                try:
                    knowledge_item = KnowledgeItem(
                        content=chunk.content,
                        metadata={
                            'title': chunk.title,
                            'source': chunk.source,
                            'chunk_type': chunk.chunk_type,
                            'tags': chunk.tags,
                            'relationships': chunk.relationships,
                            **chunk.metadata
                        }
                    )
                    
                    await self.knowledge_service.add_knowledge(knowledge_item)
                    stats['knowledge_items_stored'] += 1
                    
                except Exception as e:
                    error_msg = f"存储知识块失败: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            stats['chunks_created'] = len(self.chunks)
            stats['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ 知识库构建完成:")
            logger.info(f"   - 处理知识源: {stats['sources_processed']} 个")
            logger.info(f"   - 创建知识块: {stats['chunks_created']} 个")
            logger.info(f"   - 存储知识项: {stats['knowledge_items_stored']} 个")
            logger.info(f"   - 处理时间: {stats['processing_time']:.2f} 秒")
            
            if stats['errors']:
                logger.warning(f"⚠️ 处理过程中发生 {len(stats['errors'])} 个错误")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 知识库构建失败: {e}")
            raise
    
    async def _process_source(self, source: KnowledgeSource):
        """处理单个知识源"""
        logger.debug(f"📖 处理知识源: {source.name}")
        
        if source.source_type == "markdown":
            await self._process_markdown(source)
        elif source.source_type == "yaml":
            await self._process_yaml(source)
        elif source.source_type == "json":
            await self._process_json(source)
        elif source.source_type == "verilog":
            await self._process_verilog(source)
        elif source.source_type == "systemverilog":
            await self._process_systemverilog(source)
        elif source.source_type == "directory":
            await self._process_directory(source)
        else:
            logger.warning(f"⚠️ 不支持的知识源类型: {source.source_type}")
    
    async def _process_markdown(self, source: KnowledgeSource):
        """处理Markdown文档"""
        if not source.file_path or not Path(source.file_path).exists():
            raise FileNotFoundError(f"Markdown文件不存在: {source.file_path}")
        
        with open(source.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按标题分块
        sections = self._split_markdown_by_headers(content)
        
        for section in sections:
            if len(section['content'].strip()) < 50:  # 跳过太短的内容
                continue
            
            # 分析内容类型
            chunk_type = self._analyze_content_type(section['content'])
            
            # 提取标签
            tags = self._extract_tags(section['content'])
            tags.extend(source.tags)
            
            chunk = KnowledgeChunk(
                content=section['content'],
                title=section['title'] or f"{source.name} - Section",
                source=source.name,
                chunk_type=chunk_type,
                metadata={
                    'file_path': source.file_path,
                    'section_level': section['level'],
                    'word_count': len(section['content'].split()),
                    **source.metadata
                },
                tags=list(set(tags))  # 去重
            )
            
            self.chunks.append(chunk)
    
    async def _process_yaml(self, source: KnowledgeSource):
        """处理YAML结构化数据"""
        if not source.file_path or not Path(source.file_path).exists():
            raise FileNotFoundError(f"YAML文件不存在: {source.file_path}")
        
        with open(source.file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 递归处理YAML结构
        await self._process_yaml_structure(data, source, [])
    
    async def _process_yaml_structure(self, data: Any, source: KnowledgeSource, path: List[str]):
        """递归处理YAML结构"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = path + [key]
                
                if isinstance(value, str) and len(value) > 50:
                    # 字符串内容作为知识块
                    chunk = KnowledgeChunk(
                        content=value,
                        title=f"{source.name} - {' > '.join(current_path)}",
                        source=source.name,
                        chunk_type="structured_data",
                        metadata={
                            'yaml_path': '.'.join(current_path),
                            'data_type': 'string',
                            **source.metadata
                        },
                        tags=source.tags + current_path
                    )
                    self.chunks.append(chunk)
                
                elif isinstance(value, (dict, list)):
                    await self._process_yaml_structure(value, source, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = path + [str(i)]
                await self._process_yaml_structure(item, source, current_path)
    
    async def _process_verilog(self, source: KnowledgeSource):
        """处理Verilog代码文件"""
        if not source.file_path or not Path(source.file_path).exists():
            raise FileNotFoundError(f"Verilog文件不存在: {source.file_path}")
        
        with open(source.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取模块
        modules = self._extract_verilog_modules(content)
        
        for module in modules:
            chunk = KnowledgeChunk(
                content=module['content'],
                title=f"Verilog Module: {module['name']}",
                source=source.name,
                chunk_type="verilog_module",
                metadata={
                    'module_name': module['name'],
                    'parameters': module.get('parameters', []),
                    'ports': module.get('ports', []),
                    'file_path': source.file_path,
                    **source.metadata
                },
                tags=source.tags + ['verilog', 'module', module['name']]
            )
            self.chunks.append(chunk)
    
    async def _process_systemverilog(self, source: KnowledgeSource):
        """处理SystemVerilog代码文件"""
        if not source.file_path or not Path(source.file_path).exists():
            raise FileNotFoundError(f"SystemVerilog文件不存在: {source.file_path}")
        
        with open(source.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取模块
        modules = self._extract_verilog_modules(content)
        
        for module in modules:
            chunk = KnowledgeChunk(
                content=module['content'],
                title=f"SystemVerilog Module: {module['name']}",
                source=source.name,
                chunk_type="systemverilog_module",
                metadata={
                    'module_name': module['name'],
                    'parameters': module.get('parameters', []),
                    'ports': module.get('ports', []),
                    'file_path': source.file_path,
                    **source.metadata
                },
                tags=source.tags + ['systemverilog', 'module', module['name']]
            )
            self.chunks.append(chunk)
    
    async def _process_directory(self, source: KnowledgeSource):
        """处理目录中的所有文件"""
        if not source.file_path:
            raise ValueError("目录源必须指定file_path")
        
        directory = Path(source.file_path)
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"目录不存在: {source.file_path}")
        
        # 支持的文件扩展名
        supported_extensions = {
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.v': 'verilog',
            '.sv': 'systemverilog',
            '.vhd': 'vhdl'
        }
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                file_source = KnowledgeSource(
                    name=f"{source.name}/{file_path.relative_to(directory)}",
                    source_type=supported_extensions[file_path.suffix],
                    file_path=str(file_path),
                    metadata={**source.metadata, 'parent_directory': source.file_path},
                    tags=source.tags + [file_path.stem],
                    priority=source.priority
                )
                
                await self._process_source(file_source)
    
    def _split_markdown_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """按标题分割Markdown内容"""
        lines = content.split('\n')
        sections = []
        current_section = {'title': None, 'level': 0, 'content': ''}
        
        for line in lines:
            # 检查是否为标题
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # 保存当前段落
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # 开始新段落
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    'title': title,
                    'level': level,
                    'content': line + '\n'
                }
            else:
                current_section['content'] += line + '\n'
        
        # 添加最后一个段落
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_verilog_modules(self, content: str) -> List[Dict[str, Any]]:
        """提取Verilog模块"""
        modules = []
        
        # 匹配模块定义
        module_pattern = r'module\s+(\w+)\s*(?:\#\s*\([^)]*\))?\s*\([^)]*\)\s*;(.*?)endmodule'
        matches = re.finditer(module_pattern, content, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            module_name = match.group(1)
            module_content = match.group(0)
            
            # 提取参数
            param_pattern = r'parameter\s+(\w+)\s*=\s*([^,;]+)'
            parameters = re.findall(param_pattern, module_content)
            
            # 提取端口
            port_pattern = r'(input|output|inout)\s+(?:wire|reg)?\s*(?:\[[^\]]*\])?\s*(\w+)'
            ports = re.findall(port_pattern, module_content)
            
            modules.append({
                'name': module_name,
                'content': module_content,
                'parameters': [{'name': p[0], 'value': p[1]} for p in parameters],
                'ports': [{'direction': p[0], 'name': p[1]} for p in ports]
            })
        
        return modules
    
    def _analyze_content_type(self, content: str) -> str:
        """分析内容类型"""
        content_lower = content.lower()
        
        # 检查各种模式
        for pattern_name, pattern in self.knowledge_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                return pattern_name
        
        # 根据关键词判断
        if any(keyword in content_lower for keyword in ['example', '示例', '例子']):
            return 'example'
        elif any(keyword in content_lower for keyword in ['concept', '概念', '定义']):
            return 'concept'
        elif any(keyword in content_lower for keyword in ['reference', '参考', '文档']):
            return 'reference'
        elif any(keyword in content_lower for keyword in ['best practice', '最佳实践', '建议']):
            return 'best_practice'
        else:
            return 'general'
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取内容标签"""
        tags = []
        content_lower = content.lower()
        
        # FPGA相关标签
        fpga_keywords = [
            'fpga', 'verilog', 'systemverilog', 'vhdl',
            'xilinx', 'altera', 'intel', 'vivado', 'quartus',
            'synthesis', 'simulation', 'timing', 'constraint',
            'clock', 'reset', 'state machine', 'pipeline',
            'fifo', 'memory', 'dsp', 'pcie', 'axi', 'uart', 'spi'
        ]
        
        for keyword in fpga_keywords:
            if keyword in content_lower:
                tags.append(keyword.replace(' ', '_'))
        
        return tags
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        chunk_types = {}
        tag_counts = {}
        source_counts = {}
        
        for chunk in self.chunks:
            # 统计块类型
            chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
            
            # 统计标签
            for tag in chunk.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 统计来源
            source_counts[chunk.source] = source_counts.get(chunk.source, 0) + 1
        
        return {
            'total_chunks': len(self.chunks),
            'total_sources': len(self.sources),
            'chunk_types': chunk_types,
            'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'source_distribution': source_counts
        }


# 便利函数

async def build_fpga_knowledge_base(knowledge_dir: str = "./workspace/agents/fpga_expert/knowledge") -> Dict[str, Any]:
    """便利函数：构建FPGA知识库"""
    knowledge_service = IntegratedKnowledgeService()
    await knowledge_service.initialize()
    
    builder = KnowledgeBuilder(knowledge_service)
    
    # 添加知识库目录作为源
    knowledge_path = Path(knowledge_dir)
    if knowledge_path.exists():
        builder.add_source(KnowledgeSource(
            name="FPGA Knowledge Base",
            source_type="directory",
            file_path=str(knowledge_path),
            tags=['fpga', 'knowledge_base'],
            priority=1
        ))
    
    return await builder.build_knowledge_base() 