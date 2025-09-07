#!/usr/bin/env python3
"""
Universal Document Knowledge Processor
通用文档知识处理器 - 供所有Agent使用

核心功能:
1. 多格式文档解析和预处理
2. 基于Agentic RAG的智能内容分析
3. 自动知识抽取和结构化
4. 向量化和语义索引
5. 质量评估和持续优化
6. 增量更新和版本管理
"""

import asyncio
import logging
import hashlib
import mimetypes
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum

# 文档处理库
try:
    import PyPDF2
    import docx
    import markdown
    from bs4 import BeautifulSoup
    ADVANCED_PARSING_AVAILABLE = True
except ImportError:
    ADVANCED_PARSING_AVAILABLE = False
    logging.warning("高级文档处理库未安装，将使用基础解析功能")

# 项目导入
from .agentic_rag_system import AgenticRAGProcessor, QueryComplexity
from .rag_system import RAGSystem
from ..framework.abstractions.context import UniversalContext
from ..framework.abstractions.task import UniversalTask

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """支持的文档类型"""
    PDF = "pdf"
    MARKDOWN = "markdown"
    WORD = "word"
    TEXT = "text"
    CODE = "code"
    HTML = "html"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    UNKNOWN = "unknown"


class KnowledgeType(Enum):
    """知识类型分类"""
    CONCEPT = "concept"                 # 概念定义
    PROCEDURE = "procedure"             # 操作流程
    PATTERN = "pattern"                 # 设计模式
    EXAMPLE = "example"                 # 实例代码
    REFERENCE = "reference"             # 参考资料
    BEST_PRACTICE = "best_practice"     # 最佳实践
    TROUBLESHOOTING = "troubleshooting" # 故障排除
    TOOL_GUIDE = "tool_guide"          # 工具指南
    API_DOC = "api_doc"                # API文档
    TUTORIAL = "tutorial"               # 教程指南


class KnowledgeLevel(Enum):
    """知识难度级别"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class DocumentMetadata:
    """文档元数据"""
    file_path: str
    file_name: str
    file_size: int
    file_type: DocumentType
    mime_type: str
    created_time: str
    modified_time: str
    encoding: str = "utf-8"
    language: str = "auto"
    author: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    domain: Optional[str] = None        # 领域标识 (如: fpga, ai, web等)
    processing_time: float = 0.0
    quality_score: float = 0.0


@dataclass
class KnowledgeChunk:
    """知识块"""
    chunk_id: str
    content: str
    chunk_type: str                     # text, code, diagram, table, etc.
    semantic_summary: str
    keywords: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeItem:
    """知识项"""
    item_id: str
    title: str
    knowledge_type: KnowledgeType
    level: KnowledgeLevel
    domain: str                         # 领域标识
    chunks: List[KnowledgeChunk]
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_items: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    complexity_score: float = 0.5
    usage_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    source_documents: List[str] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    document_path: str
    knowledge_items: List[KnowledgeItem] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UniversalDocumentKnowledgeProcessor:
    """
    通用文档知识处理器
    
    设计原则:
    1. 领域无关 - 支持任何领域的文档处理
    2. 可扩展 - 支持新的文档类型和处理策略
    3. 高质量 - 基于Agentic RAG的智能分析
    4. 高效率 - 批量处理和缓存优化
    5. 易集成 - 简单的API接口
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
        
        # 初始化Agentic RAG处理器
        self.agentic_rag = AgenticRAGProcessor(
            config=self.config.get('agentic_rag', {})
        )
        
        # 处理统计
        self.stats = {
            'total_documents': 0,
            'successful_documents': 0,
            'failed_documents': 0,
            'total_knowledge_items': 0,
            'total_processing_time': 0.0,
            'avg_quality_score': 0.0,
            'supported_formats': self._get_supported_formats()
        }
        
        # 缓存
        self._embedding_cache = {}
        self._analysis_cache = {}
        
        logger.info(f"UniversalDocumentKnowledgeProcessor initialized")
        logger.info(f"Supported formats: {self.stats['supported_formats']}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            # 基础配置
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'supported_extensions': [
                '.pdf', '.md', '.txt', '.docx', '.html', '.htm',
                '.py', '.js', '.java', '.cpp', '.c', '.h',
                '.v', '.sv', '.vhd', '.vhdl',  # 硬件描述语言
                '.yaml', '.yml', '.json', '.xml', '.csv'
            ],
            'encoding_detection': True,
            'language_detection': True,
            
            # 内容处理配置
            'chunking': {
                'chunk_size': 512,
                'overlap_size': 64,
                'min_chunk_size': 100,
                'max_chunk_size': 1024,
                'preserve_code_blocks': True,
                'preserve_tables': True
            },
            
            # Agentic分析配置
            'agentic_rag': {
                'max_iterations': 3,
                'quality_threshold': 0.8,
                'enable_reflection': True,
                'enable_planning': True,
                'enable_learning': True
            },
            
            # 知识提取配置
            'knowledge_extraction': {
                'enable_auto_classification': True,
                'enable_concept_detection': True,
                'enable_relationship_mining': True,
                'min_confidence_threshold': 0.6
            },
            
            # 质量控制配置
            'quality_control': {
                'min_quality_threshold': 0.6,
                'enable_auto_improvement': True,
                'enable_duplicate_detection': True,
                'enable_consistency_check': True
            },
            
            # 向量化配置
            'vectorization': {
                'model': 'sentence-transformers/all-mpnet-base-v2',
                'dimension': 768,
                'batch_size': 32,
                'cache_embeddings': True
            },
            
            # 缓存配置
            'caching': {
                'enable_analysis_cache': True,
                'enable_embedding_cache': True,
                'cache_ttl': 3600 * 24,  # 24小时
                'max_cache_size': 1000
            }
        }
    
    def _get_supported_formats(self) -> List[str]:
        """获取支持的文档格式"""
        basic_formats = ['.txt', '.md', '.json', '.yaml', '.yml', '.csv']
        
        if ADVANCED_PARSING_AVAILABLE:
            return self.config['supported_extensions']
        else:
            # 只返回基础格式
            return [ext for ext in self.config['supported_extensions'] 
                   if ext in basic_formats]
    
    async def process_documents(self, 
                              document_paths: Union[str, Path, List[Union[str, Path]]], 
                              domain: str = "general",
                              batch_mode: bool = True) -> List[ProcessingResult]:
        """
        处理文档并提取知识
        
        Args:
            document_paths: 文档路径或路径列表
            domain: 领域标识 (如: fpga, ai, web等)
            batch_mode: 是否批量并行处理
            
        Returns:
            处理结果列表
        """
        # 标准化输入
        if isinstance(document_paths, (str, Path)):
            paths = [Path(document_paths)]
        else:
            paths = [Path(p) for p in document_paths]
        
        # 如果输入是目录，递归查找文档
        all_paths = []
        for path in paths:
            if path.is_dir():
                all_paths.extend(self._scan_directory(path))
            elif path.is_file():
                all_paths.append(path)
        
        logger.info(f"开始处理 {len(all_paths)} 个文档，领域: {domain}")
        start_time = datetime.now()
        
        # 过滤支持的格式
        supported_paths = [p for p in all_paths if p.suffix.lower() in self.stats['supported_formats']]
        if len(supported_paths) < len(all_paths):
            logger.warning(f"跳过 {len(all_paths) - len(supported_paths)} 个不支持的文件")
        
        # 处理文档
        if batch_mode and len(supported_paths) > 1:
            results = await self._process_batch(supported_paths, domain)
        else:
            results = []
            for path in supported_paths:
                result = await self._process_single_document(path, domain)
                results.append(result)
        
        # 更新统计
        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats['total_documents'] += len(supported_paths)
        self.stats['successful_documents'] += sum(1 for r in results if r.success)
        self.stats['failed_documents'] += sum(1 for r in results if not r.success)
        self.stats['total_processing_time'] += processing_time
        
        # 计算知识项总数和平均质量
        total_items = sum(len(r.knowledge_items) for r in results if r.success)
        self.stats['total_knowledge_items'] += total_items
        
        quality_scores = []
        for result in results:
            if result.success:
                for item in result.knowledge_items:
                    quality_scores.append(item.quality_score)
        
        if quality_scores:
            self.stats['avg_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        logger.info(f"文档处理完成: 成功 {sum(1 for r in results if r.success)}/{len(results)}")
        logger.info(f"提取知识项: {total_items}, 平均质量: {self.stats['avg_quality_score']:.3f}")
        
        return results
    
    def _scan_directory(self, directory: Path) -> List[Path]:
        """递归扫描目录中的文档文件"""
        document_files = []
        
        for ext in self.stats['supported_formats']:
            # 递归查找指定格式的文件
            pattern = f"**/*{ext}"
            document_files.extend(directory.glob(pattern))
        
        return list(set(document_files))  # 去重
    
    async def _process_batch(self, paths: List[Path], domain: str) -> List[ProcessingResult]:
        """批量并行处理文档"""
        tasks = [self._process_single_document(path, domain) for path in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"文档 {paths[i]} 处理失败: {result}")
                processed_results.append(ProcessingResult(
                    success=False,
                    document_path=str(paths[i]),
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_document(self, path: Path, domain: str) -> ProcessingResult:
        """处理单个文档"""
        logger.debug(f"处理文档: {path}")
        start_time = datetime.now()
        
        try:
            # 1. 解析文档
            doc_metadata, content = await self._parse_document(path, domain)
            
            # 2. Agentic内容分析
            analysis_result = await self._analyze_content_with_agentic_rag(
                content, doc_metadata, domain
            )
            
            # 3. 知识提取和结构化
            knowledge_items = await self._extract_knowledge_items(
                content, doc_metadata, analysis_result, domain
            )
            
            # 4. 质量评估和优化
            validated_items = await self._validate_and_optimize_knowledge(knowledge_items)
            
            # 5. 向量化处理
            await self._vectorize_knowledge_items(validated_items)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                document_path=str(path),
                knowledge_items=validated_items,
                processing_time=processing_time,
                metadata={
                    'document_metadata': doc_metadata.__dict__,
                    'analysis_result': analysis_result,
                    'total_chunks': sum(len(item.chunks) for item in validated_items)
                }
            )
            
        except Exception as e:
            logger.error(f"文档 {path} 处理失败: {e}")
            return ProcessingResult(
                success=False,
                document_path=str(path),
                processing_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _parse_document(self, path: Path, domain: str) -> Tuple[DocumentMetadata, str]:
        """解析文档内容"""
        # 检查文件
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        if path.stat().st_size > self.config['max_file_size']:
            raise ValueError(f"文件过大: {path.stat().st_size} bytes")
        
        # 检测文档类型
        doc_type = self._detect_document_type(path)
        
        # 创建元数据
        metadata = DocumentMetadata(
            file_path=str(path),
            file_name=path.name,
            file_size=path.stat().st_size,
            file_type=doc_type,
            mime_type=mimetypes.guess_type(str(path))[0] or "unknown",
            created_time=datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
            modified_time=datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            domain=domain
        )
        
        # 提取内容
        content = await self._extract_content_by_type(path, doc_type)
        
        # 自动检测标题
        if not metadata.title:
            metadata.title = self._extract_title(content, path.name)
        
        return metadata, content
    
    def _detect_document_type(self, path: Path) -> DocumentType:
        """检测文档类型"""
        suffix = path.suffix.lower()
        
        type_mapping = {
            '.pdf': DocumentType.PDF,
            '.md': DocumentType.MARKDOWN,
            '.markdown': DocumentType.MARKDOWN,
            '.txt': DocumentType.TEXT,
            '.docx': DocumentType.WORD,
            '.doc': DocumentType.WORD,
            '.html': DocumentType.HTML,
            '.htm': DocumentType.HTML,
            '.yaml': DocumentType.YAML,
            '.yml': DocumentType.YAML,
            '.json': DocumentType.JSON,
            '.xml': DocumentType.XML,
            '.csv': DocumentType.CSV,
            # 代码文件
            '.py': DocumentType.CODE,
            '.js': DocumentType.CODE,
            '.java': DocumentType.CODE,
            '.cpp': DocumentType.CODE,
            '.c': DocumentType.CODE,
            '.h': DocumentType.CODE,
            '.v': DocumentType.CODE,
            '.sv': DocumentType.CODE,
            '.vhd': DocumentType.CODE,
            '.vhdl': DocumentType.CODE,
        }
        
        return type_mapping.get(suffix, DocumentType.UNKNOWN)
    
    async def _extract_content_by_type(self, path: Path, doc_type: DocumentType) -> str:
        """根据类型提取内容"""
        if doc_type == DocumentType.TEXT:
            return self._read_text_file(path)
        elif doc_type == DocumentType.MARKDOWN:
            return await self._extract_markdown_content(path)
        elif doc_type == DocumentType.PDF:
            return await self._extract_pdf_content(path)
        elif doc_type == DocumentType.WORD:
            return await self._extract_word_content(path)
        elif doc_type == DocumentType.CODE:
            return await self._extract_code_content(path)
        elif doc_type == DocumentType.HTML:
            return await self._extract_html_content(path)
        elif doc_type in [DocumentType.YAML, DocumentType.JSON, DocumentType.XML]:
            return await self._extract_structured_content(path, doc_type)
        elif doc_type == DocumentType.CSV:
            return await self._extract_csv_content(path)
        else:
            return self._read_text_file(path)  # 默认按文本处理
    
    def _read_text_file(self, path: Path) -> str:
        """读取文本文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 如果都失败，用二进制模式读取并忽略错误
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    async def _extract_markdown_content(self, path: Path) -> str:
        """提取Markdown内容"""
        content = self._read_text_file(path)
        
        # 保留原始Markdown格式
        return content
    
    async def _extract_pdf_content(self, path: Path) -> str:
        """提取PDF内容"""
        if not ADVANCED_PARSING_AVAILABLE:
            raise ImportError("PDF处理库未安装")
        
        content_parts = []
        try:
            with open(path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            content_parts.append(f"# Page {page_num + 1}\n\n{text}")
                    except Exception as e:
                        logger.warning(f"PDF页面 {page_num + 1} 提取失败: {e}")
            
            return '\n\n---\n\n'.join(content_parts)
            
        except Exception as e:
            logger.error(f"PDF文件 {path} 处理失败: {e}")
            return f"# PDF文档: {path.name}\n\n[PDF内容提取失败: {e}]"
    
    async def _extract_word_content(self, path: Path) -> str:
        """提取Word文档内容"""
        if not ADVANCED_PARSING_AVAILABLE:
            raise ImportError("Word处理库未安装")
        
        try:
            doc = docx.Document(path)
            paragraphs = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    paragraphs.append(text)
            
            return '\n\n'.join(paragraphs)
            
        except Exception as e:
            logger.error(f"Word文档 {path} 处理失败: {e}")
            return f"# Word文档: {path.name}\n\n[Word内容提取失败: {e}]"
    
    async def _extract_code_content(self, path: Path) -> str:
        """提取代码内容"""
        content = self._read_text_file(path)
        
        # 确定编程语言
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.v': 'verilog',
            '.sv': 'systemverilog',
            '.vhd': 'vhdl',
            '.vhdl': 'vhdl'
        }
        
        language = language_map.get(path.suffix.lower(), 'text')
        
        return f"# Code File: {path.name}\n\n```{language}\n{content}\n```"
    
    async def _extract_html_content(self, path: Path) -> str:
        """提取HTML内容"""
        html_content = self._read_text_file(path)
        
        if ADVANCED_PARSING_AVAILABLE:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 提取标题
                title = soup.find('title')
                title_text = title.get_text() if title else path.name
                
                # 移除脚本和样式
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # 提取文本内容
                text_content = soup.get_text()
                
                return f"# {title_text}\n\n{text_content}"
                
            except Exception as e:
                logger.warning(f"HTML解析失败: {e}")
        
        # 简单的HTML标签移除
        text_content = re.sub(r'<[^>]+>', '', html_content)
        return f"# HTML文档: {path.name}\n\n{text_content}"
    
    async def _extract_structured_content(self, path: Path, doc_type: DocumentType) -> str:
        """提取结构化内容"""
        content = self._read_text_file(path)
        
        try:
            if doc_type == DocumentType.YAML:
                data = yaml.safe_load(content)
            elif doc_type == DocumentType.JSON:
                data = json.loads(content)
            else:  # XML等其他格式
                return f"# {doc_type.value.upper()}文档: {path.name}\n\n```\n{content}\n```"
            
            # 转换为可读格式
            readable_content = self._convert_dict_to_text(data)
            return f"# {doc_type.value.upper()}文档: {path.name}\n\n{readable_content}\n\n## 原始内容\n\n```{doc_type.value}\n{content}\n```"
            
        except Exception as e:
            logger.warning(f"结构化数据解析失败: {e}")
            return f"# {doc_type.value.upper()}文档: {path.name}\n\n```\n{content}\n```"
    
    async def _extract_csv_content(self, path: Path) -> str:
        """提取CSV内容"""
        content = self._read_text_file(path)
        lines = content.split('\n')
        
        if len(lines) > 100:  # 如果行数太多，只取前100行
            lines = lines[:100]
            content = '\n'.join(lines) + '\n\n[... 内容已截断 ...]'
        
        return f"# CSV数据: {path.name}\n\n```csv\n{content}\n```"
    
    def _convert_dict_to_text(self, data: Any, level: int = 0) -> str:
        """将字典转换为可读文本"""
        if level > 5:  # 防止无限递归
            return str(data)
        
        indent = "  " * level
        result = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result.append(f"{indent}**{key}**:")
                    result.append(self._convert_dict_to_text(value, level + 1))
                else:
                    result.append(f"{indent}**{key}**: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                result.append(f"{indent}{i + 1}. {self._convert_dict_to_text(item, level)}")
        else:
            return str(data)
        
        return '\n'.join(result)
    
    def _extract_title(self, content: str, filename: str) -> str:
        """提取文档标题"""
        lines = content.split('\n')
        
        # 查找Markdown标题
        for line in lines[:10]:  # 只检查前10行
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # 查找其他格式的标题
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith(('```', '<!--', '//', '/*')):
                return line
        
        # 使用文件名
        return filename.replace('_', ' ').replace('-', ' ').title()
    
    async def _analyze_content_with_agentic_rag(self, 
                                              content: str, 
                                              metadata: DocumentMetadata, 
                                              domain: str) -> Dict[str, Any]:
        """使用Agentic RAG分析内容"""
        # 检查缓存
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"analysis_{content_hash}"
        
        if (self.config['caching']['enable_analysis_cache'] and 
            cache_key in self._analysis_cache):
            return self._analysis_cache[cache_key]
        
        try:
            # 构建分析查询
            analysis_queries = [
                f"分析这个{domain}领域文档的主要内容和结构",
                "识别文档中的关键概念、术语和知识点",
                "判断文档的类型、难度级别和目标受众",
                "提取文档中的重要信息、最佳实践和注意事项"
            ]
            
            analysis_results = []
            
            # 限制内容长度以避免token超限
            content_preview = content[:2000] if len(content) > 2000 else content
            
            for query in analysis_queries:
                try:
                    # 创建上下文
                    context = UniversalContext()
                    context.set('content', content_preview)
                    context.set('document_info', metadata.__dict__)
                    context.set('domain', domain)
                    context.set('analysis_query', query)
                    
                    # 使用Agentic RAG分析
                    response = await self.agentic_rag.process(query, context)
                    
                    analysis_results.append({
                        'query': query,
                        'response': response.content,
                        'confidence': response.confidence,
                        'iterations': response.iterations_used
                    })
                    
                except Exception as e:
                    logger.warning(f"分析查询失败: {query}, 错误: {e}")
                    continue
            
            # 综合分析结果
            synthesized_result = self._synthesize_analysis_results(
                analysis_results, content, metadata, domain
            )
            
            # 缓存结果
            if self.config['caching']['enable_analysis_cache']:
                self._analysis_cache[cache_key] = synthesized_result
                
                # 限制缓存大小
                if len(self._analysis_cache) > self.config['caching']['max_cache_size']:
                    # 移除最旧的条目
                    oldest_key = next(iter(self._analysis_cache))
                    del self._analysis_cache[oldest_key]
            
            return synthesized_result
            
        except Exception as e:
            logger.error(f"Agentic内容分析失败: {e}")
            # 返回基础分析结果
            return self._basic_content_analysis(content, metadata, domain)
    
    def _synthesize_analysis_results(self, 
                                   analysis_results: List[Dict], 
                                   content: str, 
                                   metadata: DocumentMetadata,
                                   domain: str) -> Dict[str, Any]:
        """综合分析结果"""
        if not analysis_results:
            return self._basic_content_analysis(content, metadata, domain)
        
        # 提取关键信息
        topics = set()
        concepts = set()
        keywords = set()
        
        for result in analysis_results:
            response = result['response'].lower()
            
            # 简单的关键词提取
            if domain == 'fpga':
                fpga_terms = [
                    'fpga', 'verilog', 'systemverilog', 'vhdl', '时序', '综合',
                    '验证', '仿真', '约束', '时钟', '复位', '状态机', 'fifo',
                    'ram', 'rom', 'dsp', 'pll', 'mmcm', 'clb', 'lut', 'ff'
                ]
                found_terms = [term for term in fpga_terms if term in response]
                topics.update(found_terms[:5])
                concepts.update(found_terms[:10])
        
        # 确定知识类型
        knowledge_type = self._determine_knowledge_type(content, metadata)
        
        # 确定难度级别
        knowledge_level = self._determine_knowledge_level(content, analysis_results)
        
        # 生成标签
        suggested_tags = list(topics.union(concepts))[:10]
        
        return {
            'topics': list(topics),
            'concepts': list(concepts),
            'keywords': list(keywords),
            'knowledge_type': knowledge_type.value,
            'knowledge_level': knowledge_level.value,
            'suggested_tags': suggested_tags,
            'analysis_confidence': sum(r['confidence'] for r in analysis_results) / len(analysis_results),
            'total_iterations': sum(r['iterations'] for r in analysis_results),
            'complexity_score': self._calculate_complexity_score(content, analysis_results)
        }
    
    def _basic_content_analysis(self, content: str, metadata: DocumentMetadata, domain: str) -> Dict[str, Any]:
        """基础内容分析（当Agentic分析失败时使用）"""
        # 基于规则的简单分析
        knowledge_type = self._determine_knowledge_type(content, metadata)
        knowledge_level = self._determine_knowledge_level(content, [])
        
        # 简单关键词提取
        common_keywords = []
        if domain == 'fpga':
            fpga_keywords = [
                'fpga', 'verilog', 'systemverilog', 'vhdl', 'synthesis',
                'simulation', 'timing', 'constraint', 'clock', 'reset'
            ]
            content_lower = content.lower()
            common_keywords = [kw for kw in fpga_keywords if kw in content_lower]
        
        return {
            'topics': common_keywords[:5],
            'concepts': common_keywords[:10],
            'keywords': common_keywords,
            'knowledge_type': knowledge_type.value,
            'knowledge_level': knowledge_level.value,
            'suggested_tags': common_keywords[:8],
            'analysis_confidence': 0.5,
            'total_iterations': 0,
            'complexity_score': 0.5,
            'fallback_analysis': True
        }
    
    def _determine_knowledge_type(self, content: str, metadata: DocumentMetadata) -> KnowledgeType:
        """确定知识类型"""
        content_lower = content.lower()
        filename_lower = metadata.file_name.lower()
        
        # 基于内容特征判断
        if any(word in content_lower for word in ['什么是', '定义', '概念', 'definition', 'concept']):
            return KnowledgeType.CONCEPT
        elif any(word in content_lower for word in ['步骤', '流程', '如何', 'how to', 'procedure', 'step']):
            return KnowledgeType.PROCEDURE
        elif any(word in content_lower for word in ['模式', '模板', 'pattern', 'template']):
            return KnowledgeType.PATTERN
        elif '```' in content or metadata.file_type == DocumentType.CODE:
            return KnowledgeType.EXAMPLE
        elif any(word in content_lower for word in ['api', '接口', 'interface', 'function', 'method']):
            return KnowledgeType.API_DOC
        elif any(word in content_lower for word in ['教程', '指南', 'tutorial', 'guide']):
            return KnowledgeType.TUTORIAL
        elif any(word in content_lower for word in ['问题', '错误', '故障', 'error', 'issue', 'problem']):
            return KnowledgeType.TROUBLESHOOTING
        elif any(word in content_lower for word in ['最佳', '建议', '实践', 'best', 'practice', 'tip']):
            return KnowledgeType.BEST_PRACTICE
        elif any(word in content_lower for word in ['工具', 'tool', '软件', 'software']):
            return KnowledgeType.TOOL_GUIDE
        else:
            return KnowledgeType.REFERENCE
    
    def _determine_knowledge_level(self, content: str, analysis_results: List[Dict]) -> KnowledgeLevel:
        """确定知识难度级别"""
        content_lower = content.lower()
        
        # 高级/专家级指标
        advanced_indicators = [
            'advanced', '高级', '复杂', '深入', '架构', 'architecture',
            '算法', 'algorithm', '优化', 'optimization', '性能', 'performance'
        ]
        
        expert_indicators = [
            'expert', '专家', '内核', 'kernel', '底层', 'low-level',
            '源码', 'source code', '实现', 'implementation'
        ]
        
        # 初级指标
        beginner_indicators = [
            'basic', '基础', '入门', '简单', 'simple', '介绍', 'introduction',
            '开始', 'getting started', '第一', 'first'
        ]
        
        # 计算指标得分
        expert_score = sum(1 for indicator in expert_indicators if indicator in content_lower)
        advanced_score = sum(1 for indicator in advanced_indicators if indicator in content_lower)
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in content_lower)
        
        # 基于长度和复杂性
        if len(content) > 5000:
            advanced_score += 1
        if content.count('```') > 3:  # 多个代码块
            advanced_score += 1
        
        # 决策逻辑
        if expert_score > 0 or advanced_score > 2:
            return KnowledgeLevel.EXPERT if expert_score > advanced_score else KnowledgeLevel.ADVANCED
        elif advanced_score > 0 or len(content) > 2000:
            return KnowledgeLevel.INTERMEDIATE
        else:
            return KnowledgeLevel.BEGINNER
    
    def _calculate_complexity_score(self, content: str, analysis_results: List[Dict]) -> float:
        """计算复杂度分数"""
        score = 0.3  # 基础分数
        
        # 基于内容长度
        length_score = min(len(content) / 10000, 0.3)
        score += length_score
        
        # 基于代码块数量
        code_blocks = content.count('```')
        code_score = min(code_blocks * 0.05, 0.2)
        score += code_score
        
        # 基于分析置信度
        if analysis_results:
            avg_confidence = sum(r['confidence'] for r in analysis_results) / len(analysis_results)
            confidence_score = (avg_confidence - 0.5) * 0.2
            score += confidence_score
        
        return min(max(score, 0.1), 1.0)
    
    async def _extract_knowledge_items(self, 
                                     content: str, 
                                     metadata: DocumentMetadata, 
                                     analysis_result: Dict[str, Any], 
                                     domain: str) -> List[KnowledgeItem]:
        """提取知识项"""
        knowledge_items = []
        
        # 智能分块
        chunks = await self._intelligent_chunking(content, metadata, analysis_result)
        
        # 如果内容较短，创建单个知识项
        if len(chunks) <= 3:
            item = KnowledgeItem(
                item_id=hashlib.md5(f"{metadata.file_path}_main".encode()).hexdigest()[:12],
                title=metadata.title or f"{metadata.file_name}",
                knowledge_type=KnowledgeType(analysis_result['knowledge_type']),
                level=KnowledgeLevel(analysis_result['knowledge_level']),
                domain=domain,
                chunks=chunks,
                tags=analysis_result.get('suggested_tags', []),
                complexity_score=analysis_result.get('complexity_score', 0.5),
                source_documents=[metadata.file_path]
            )
            knowledge_items.append(item)
        else:
            # 创建多个知识项
            items = await self._create_multiple_knowledge_items(
                chunks, metadata, analysis_result, domain
            )
            knowledge_items.extend(items)
        
        return knowledge_items
    
    async def _intelligent_chunking(self, 
                                  content: str, 
                                  metadata: DocumentMetadata, 
                                  analysis_result: Dict[str, Any]) -> List[KnowledgeChunk]:
        """智能分块"""
        chunks = []
        chunk_size = self.config['chunking']['chunk_size']
        overlap_size = self.config['chunking'].get('overlap_size', 64)
        
        # 基于内容类型的分块策略
        if '```' in content and self.config['chunking'].get('preserve_code_blocks', True):
            # 代码内容特殊处理
            chunks = await self._chunk_code_content(content, metadata, analysis_result)
        elif metadata.file_type == DocumentType.MARKDOWN:
            # Markdown按标题分块
            chunks = await self._chunk_markdown_content(content, metadata, analysis_result)
        else:
            # 通用文本分块
            chunks = await self._chunk_text_content(content, metadata, analysis_result)
        
        return chunks
    
    async def _chunk_code_content(self, content: str, metadata: DocumentMetadata, analysis_result: Dict[str, Any]) -> List[KnowledgeChunk]:
        """代码内容分块"""
        chunks = []
        parts = content.split('```')
        
        chunk_index = 0
        for i, part in enumerate(parts):
            if not part.strip():
                continue
            
            if i % 2 == 0:  # 文本部分
                if part.strip():
                    chunk = KnowledgeChunk(
                        chunk_id=f"{metadata.file_name}_text_{chunk_index}",
                        content=part.strip(),
                        chunk_type="text",
                        semantic_summary=self._generate_text_summary(part.strip()),
                        keywords=self._extract_simple_keywords(part.strip(), analysis_result.get('keywords', []))
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            else:  # 代码部分
                lines = part.strip().split('\n')
                language = lines[0] if lines and lines[0] in ['python', 'javascript', 'verilog', 'systemverilog', 'java', 'cpp'] else 'text'
                code_content = '\n'.join(lines[1:]) if language in (lines[0] if lines else '') else part.strip()
                
                chunk = KnowledgeChunk(
                    chunk_id=f"{metadata.file_name}_code_{chunk_index}",
                    content=code_content,
                    chunk_type="code",
                    semantic_summary=self._generate_code_summary(code_content, language),
                    keywords=self._extract_code_keywords(code_content, language),
                    metadata={'language': language}
                )
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
    
    async def _chunk_markdown_content(self, content: str, metadata: DocumentMetadata, analysis_result: Dict[str, Any]) -> List[KnowledgeChunk]:
        """Markdown内容按标题分块"""
        chunks = []
        
        # 按标题分割
        sections = re.split(r'\n(#{1,6}\s+.+)', content)
        
        current_section = ""
        current_title = ""
        chunk_index = 0
        
        for i, section in enumerate(sections):
            if re.match(r'^#{1,6}\s+', section):  # 标题行
                # 保存前一个section
                if current_section.strip():
                    chunk = KnowledgeChunk(
                        chunk_id=f"{metadata.file_name}_section_{chunk_index}",
                        content=current_section.strip(),
                        chunk_type="text",
                        semantic_summary=current_title or self._generate_text_summary(current_section[:200]),
                        keywords=self._extract_simple_keywords(current_section, analysis_result.get('keywords', [])),
                        metadata={'section_title': current_title}
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                current_title = section.strip()
                current_section = section + "\n"
            else:
                current_section += section
        
        # 处理最后一个section
        if current_section.strip():
            chunk = KnowledgeChunk(
                chunk_id=f"{metadata.file_name}_section_{chunk_index}",
                content=current_section.strip(),
                chunk_type="text",
                semantic_summary=current_title or self._generate_text_summary(current_section[:200]),
                keywords=self._extract_simple_keywords(current_section, analysis_result.get('keywords', [])),
                metadata={'section_title': current_title}
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _chunk_text_content(self, content: str, metadata: DocumentMetadata, analysis_result: Dict[str, Any]) -> List[KnowledgeChunk]:
        """通用文本分块"""
        chunks = []
        chunk_size = self.config['chunking']['chunk_size']
        overlap_size = self.config['chunking'].get('overlap_size', 64)
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # 检查是否超过块大小
            if len(current_chunk + paragraph) > chunk_size and current_chunk:
                # 创建当前块
                chunk = KnowledgeChunk(
                    chunk_id=f"{metadata.file_name}_chunk_{chunk_index}",
                    content=current_chunk.strip(),
                    chunk_type="text",
                    semantic_summary=self._generate_text_summary(current_chunk.strip()),
                    keywords=self._extract_simple_keywords(current_chunk, analysis_result.get('keywords', []))
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # 开始新块，保留重叠
                if overlap_size > 0:
                    overlap_text = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # 处理最后一个块
        if current_chunk.strip():
            chunk = KnowledgeChunk(
                chunk_id=f"{metadata.file_name}_chunk_{chunk_index}",
                content=current_chunk.strip(),
                chunk_type="text",
                semantic_summary=self._generate_text_summary(current_chunk.strip()),
                keywords=self._extract_simple_keywords(current_chunk, analysis_result.get('keywords', []))
            )
            chunks.append(chunk)
        
        return chunks
    
    def _generate_text_summary(self, text: str) -> str:
        """生成文本摘要"""
        # 简化版摘要生成
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text[:150] + "..." if len(text) > 150 else text
        else:
            return sentences[0].strip() + "。"
    
    def _generate_code_summary(self, code: str, language: str) -> str:
        """生成代码摘要"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if language in ['verilog', 'systemverilog']:
            # 查找模块定义
            for line in non_empty_lines:
                if 'module' in line.lower():
                    return f"Verilog模块: {line.strip()}"
            
            # 查找always块
            for line in non_empty_lines:
                if 'always' in line.lower():
                    return f"Verilog逻辑: {line.strip()}"
        
        elif language == 'python':
            # 查找函数或类定义
            for line in non_empty_lines:
                if line.strip().startswith(('def ', 'class ')):
                    return f"Python代码: {line.strip()}"
        
        return f"{language}代码片段 ({len(non_empty_lines)}行)"
    
    def _extract_simple_keywords(self, text: str, suggested_keywords: List[str]) -> List[str]:
        """简单关键词提取"""
        text_lower = text.lower()
        found_keywords = []
        
        # 使用建议的关键词
        for keyword in suggested_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # 添加一些通用技术关键词
        common_keywords = [
            'function', 'class', 'method', 'variable', 'parameter',
            'algorithm', 'data', 'structure', 'pattern', 'example'
        ]
        
        for keyword in common_keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords[:8]  # 限制关键词数量
    
    def _extract_code_keywords(self, code: str, language: str) -> List[str]:
        """提取代码关键词"""
        keywords = []
        code_lower = code.lower()
        
        if language in ['verilog', 'systemverilog']:
            verilog_keywords = [
                'module', 'endmodule', 'always', 'assign', 'wire', 'reg',
                'input', 'output', 'parameter', 'localparam', 'function',
                'task', 'case', 'if', 'else', 'for', 'while', 'generate'
            ]
            keywords = [kw for kw in verilog_keywords if kw in code_lower]
            
        elif language == 'python':
            python_keywords = [
                'def', 'class', 'import', 'from', 'if', 'else', 'elif',
                'for', 'while', 'try', 'except', 'with', 'return', 'yield'
            ]
            keywords = [kw for kw in python_keywords if kw in code_lower]
        
        return keywords[:10]
    
    async def _create_multiple_knowledge_items(self, 
                                             chunks: List[KnowledgeChunk], 
                                             metadata: DocumentMetadata, 
                                             analysis_result: Dict[str, Any], 
                                             domain: str) -> List[KnowledgeItem]:
        """创建多个知识项"""
        items = []
        
        # 按chunk类型或主题分组
        chunk_groups = self._group_chunks(chunks)
        
        for group_name, group_chunks in chunk_groups.items():
            if not group_chunks:
                continue
            
            item = KnowledgeItem(
                item_id=hashlib.md5(f"{metadata.file_path}_{group_name}".encode()).hexdigest()[:12],
                title=f"{metadata.title} - {group_name}",
                knowledge_type=KnowledgeType(analysis_result['knowledge_type']),
                level=KnowledgeLevel(analysis_result['knowledge_level']),
                domain=domain,
                chunks=group_chunks,
                tags=analysis_result.get('suggested_tags', [])[:5],
                complexity_score=analysis_result.get('complexity_score', 0.5),
                source_documents=[metadata.file_path]
            )
            items.append(item)
        
        return items
    
    def _group_chunks(self, chunks: List[KnowledgeChunk]) -> Dict[str, List[KnowledgeChunk]]:
        """对chunks进行分组"""
        groups = {}
        
        for chunk in chunks:
            # 基于chunk类型分组
            if chunk.chunk_type == "code":
                language = chunk.metadata.get('language', 'code')
                group_name = f"代码示例_{language}"
            elif chunk.chunk_type == "text":
                # 基于section标题分组
                section_title = chunk.metadata.get('section_title')
                if section_title:
                    group_name = section_title.replace('#', '').strip()
                else:
                    group_name = "文档内容"
            else:
                group_name = chunk.chunk_type
            
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(chunk)
        
        return groups
    
    async def _validate_and_optimize_knowledge(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """验证和优化知识项"""
        validated_items = []
        
        for item in knowledge_items:
            # 质量评估
            quality_score = await self._assess_knowledge_quality(item)
            item.quality_score = quality_score
            
            # 只保留高质量的知识项
            if quality_score >= self.config['quality_control']['min_quality_threshold']:
                validated_items.append(item)
            else:
                logger.debug(f"知识项质量不达标: {item.title} (分数: {quality_score:.3f})")
        
        return validated_items
    
    async def _assess_knowledge_quality(self, item: KnowledgeItem) -> float:
        """评估知识质量"""
        quality_factors = []
        
        # 1. 内容完整性 (30%)
        total_content_length = sum(len(chunk.content) for chunk in item.chunks)
        completeness = min(total_content_length / 300, 1.0)  # 300字符为基准
        quality_factors.append(completeness * 0.3)
        
        # 2. 结构化程度 (25%)
        has_code = any(chunk.chunk_type == "code" for chunk in item.chunks)
        has_summary = all(chunk.semantic_summary for chunk in item.chunks)
        structure_score = (0.5 if has_code else 0.3) + (0.2 if has_summary else 0.0)
        quality_factors.append(min(structure_score, 0.25))
        
        # 3. 关键词覆盖 (20%)
        total_keywords = sum(len(chunk.keywords) for chunk in item.chunks)
        keyword_coverage = min(total_keywords / 3, 1.0)  # 3个关键词为基准
        quality_factors.append(keyword_coverage * 0.2)
        
        # 4. 元数据完整性 (25%)
        metadata_score = 0
        metadata_score += 0.1 if item.title else 0
        metadata_score += 0.05 if item.tags else 0
        metadata_score += 0.05 if item.domain else 0
        metadata_score += 0.05 if len(item.chunks) > 0 else 0
        quality_factors.append(metadata_score)
        
        return sum(quality_factors)
    
    async def _vectorize_knowledge_items(self, knowledge_items: List[KnowledgeItem]):
        """向量化知识项"""
        if not self.config['vectorization'].get('model'):
            return
        
        # 这里应该集成实际的向量化模型
        # 现在先模拟向量化过程
        vector_dim = self.config['vectorization']['dimension']
        
        for item in knowledge_items:
            for chunk in item.chunks:
                # 检查缓存
                content_hash = hashlib.md5(chunk.content.encode()).hexdigest()
                
                if (self.config['caching']['enable_embedding_cache'] and 
                    content_hash in self._embedding_cache):
                    chunk.embeddings = self._embedding_cache[content_hash]
                else:
                    # 模拟向量生成（实际应该调用embedding模型）
                    chunk.embeddings = [0.1] * vector_dim
                    
                    # 缓存结果
                    if self.config['caching']['enable_embedding_cache']:
                        self._embedding_cache[content_hash] = chunk.embeddings
    
    async def save_knowledge_base(self, 
                                knowledge_items: List[KnowledgeItem], 
                                output_path: Union[str, Path],
                                domain: str = "general") -> str:
        """保存知识库到文件"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建知识库数据
        knowledge_data = {
            'metadata': {
                'domain': domain,
                'total_items': len(knowledge_items),
                'created_time': datetime.now().isoformat(),
                'processor_version': '1.0.0',
                'config': self.config
            },
            'statistics': self.stats,
            'knowledge_items': []
        }
        
        # 序列化知识项
        for item in knowledge_items:
            item_data = {
                'item_id': item.item_id,
                'title': item.title,
                'knowledge_type': item.knowledge_type.value,
                'level': item.level.value,
                'domain': item.domain,
                'tags': item.tags,
                'prerequisites': item.prerequisites,
                'related_items': item.related_items,
                'quality_score': item.quality_score,
                'complexity_score': item.complexity_score,
                'usage_count': item.usage_count,
                'last_updated': item.last_updated,
                'version': item.version,
                'source_documents': item.source_documents,
                'chunks': [
                    {
                        'chunk_id': chunk.chunk_id,
                        'content': chunk.content,
                        'chunk_type': chunk.chunk_type,
                        'semantic_summary': chunk.semantic_summary,
                        'keywords': chunk.keywords,
                        'embeddings': chunk.embeddings,
                        'metadata': chunk.metadata
                    }
                    for chunk in item.chunks
                ]
            }
            knowledge_data['knowledge_items'].append(item_data)
        
        # 保存到文件
        knowledge_file = output_dir / f"{domain}_knowledge_base.json"
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        report = self._generate_processing_report(knowledge_items, domain)
        report_file = output_dir / f"{domain}_processing_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"知识库已保存: {knowledge_file}")
        logger.info(f"处理报告: {report_file}")
        
        return str(knowledge_file)
    
    def _generate_processing_report(self, knowledge_items: List[KnowledgeItem], domain: str) -> str:
        """生成处理报告"""
        # 统计信息
        total_items = len(knowledge_items)
        total_chunks = sum(len(item.chunks) for item in knowledge_items)
        avg_quality = sum(item.quality_score for item in knowledge_items) / total_items if total_items > 0 else 0.0
        
        # 类型分布
        type_counts = {}
        level_counts = {}
        
        for item in knowledge_items:
            type_key = item.knowledge_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            level_key = item.level.value
            level_counts[level_key] = level_counts.get(level_key, 0) + 1
        
        report = f"""# {domain.title()}领域知识库处理报告

## 处理概况
- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **领域**: {domain}
- **总文档数**: {self.stats['total_documents']}
- **成功处理**: {self.stats['successful_documents']}
- **失败处理**: {self.stats['failed_documents']}
- **成功率**: {self.stats['successful_documents'] / max(self.stats['total_documents'], 1) * 100:.1f}%

## 知识库统计
- **知识项总数**: {total_items}
- **知识块总数**: {total_chunks}
- **平均质量分数**: {avg_quality:.3f}
- **总处理时间**: {self.stats['total_processing_time']:.2f}秒
- **平均处理时间**: {self.stats['total_processing_time'] / max(self.stats['total_documents'], 1):.2f}秒/文档

## 知识分布

### 按类型分布
"""
        
        for type_name, count in type_counts.items():
            percentage = count / total_items * 100 if total_items > 0 else 0
            report += f"- {type_name}: {count}项 ({percentage:.1f}%)\n"
        
        report += "\n### 按难度级别分布\n"
        for level_name, count in level_counts.items():
            percentage = count / total_items * 100 if total_items > 0 else 0
            report += f"- {level_name}: {count}项 ({percentage:.1f}%)\n"
        
        # 质量分析
        high_quality = sum(1 for item in knowledge_items if item.quality_score > 0.8)
        medium_quality = sum(1 for item in knowledge_items if 0.6 <= item.quality_score <= 0.8)
        low_quality = sum(1 for item in knowledge_items if item.quality_score < 0.6)
        
        report += f"""
## 质量分析
- **高质量** (>0.8): {high_quality}项 ({high_quality/max(total_items, 1)*100:.1f}%)
- **中等质量** (0.6-0.8): {medium_quality}项 ({medium_quality/max(total_items, 1)*100:.1f}%)
- **待改进** (<0.6): {low_quality}项 ({low_quality/max(total_items, 1)*100:.1f}%)

## 处理配置
- **分块大小**: {self.config['chunking']['chunk_size']}字符
- **重叠大小**: {self.config['chunking'].get('overlap_size', 64)}字符
- **质量阈值**: {self.config['quality_control']['min_quality_threshold']}
- **向量维度**: {self.config['vectorization']['dimension']}

## 支持的格式
{', '.join(self.stats['supported_formats'])}

---
**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**处理器版本**: UniversalDocumentKnowledgeProcessor v1.0.0
"""
        
        return report
    
    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.stats.copy()
    
    def clear_cache(self):
        """清理缓存"""
        self._embedding_cache.clear()
        self._analysis_cache.clear()
        logger.info("缓存已清理")


# 便捷函数
async def process_documents_to_knowledge(document_paths: Union[str, Path, List[Union[str, Path]]], 
                                       domain: str = "general",
                                       output_path: str = None,
                                       config: Dict[str, Any] = None) -> str:
    """
    便捷函数：处理文档并生成知识库
    
    Args:
        document_paths: 文档路径或路径列表
        domain: 领域标识
        output_path: 输出路径
        config: 自定义配置
        
    Returns:
        知识库文件路径
    """
    processor = UniversalDocumentKnowledgeProcessor(config)
    
    # 处理文档
    results = await processor.process_documents(document_paths, domain)
    
    # 收集所有成功的知识项
    all_knowledge_items = []
    for result in results:
        if result.success:
            all_knowledge_items.extend(result.knowledge_items)
    
    # 保存知识库
    if not output_path:
        output_path = f"./{domain}_knowledge_base"
    
    knowledge_file = await processor.save_knowledge_base(
        all_knowledge_items, output_path, domain
    )
    
    return knowledge_file


if __name__ == "__main__":
    # 使用示例
    async def main():
        # 处理FPGA文档
        knowledge_file = await process_documents_to_knowledge(
            document_paths="./fpga_docs",
            domain="fpga",
            output_path="./fpga_knowledge_base"
        )
        print(f"FPGA知识库已生成: {knowledge_file}")
    
    asyncio.run(main()) 