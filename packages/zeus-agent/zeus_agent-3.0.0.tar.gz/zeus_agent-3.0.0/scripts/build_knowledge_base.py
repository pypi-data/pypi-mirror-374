#!/usr/bin/env python3
"""
通用知识库构建脚本
支持任何领域的文档处理和知识库构建
"""

import asyncio
import sys
import logging
from pathlib import Path
import argparse
from typing import Optional

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from layers.intelligent_context.document_knowledge_processor import process_documents_to_knowledge

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def build_knowledge_base(
    docs_path: str,
    domain: str,
    output_path: Optional[str] = None,
    config_overrides: Optional[dict] = None
):
    """
    构建知识库
    
    Args:
        docs_path: 文档目录路径
        domain: 领域标识 (如: fpga, ai, web等)
        output_path: 输出路径 (可选)
        config_overrides: 配置覆盖 (可选)
    """
    
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        raise FileNotFoundError(f"文档目录不存在: {docs_path}")
    
    logger.info(f"🚀 开始构建 {domain} 领域知识库")
    logger.info(f"📁 文档目录: {docs_dir.absolute()}")
    
    # 默认输出路径
    if not output_path:
        output_path = project_root / "knowledge_bases" / domain
    
    output_dir = Path(output_path)
    logger.info(f"📤 输出目录: {output_dir.absolute()}")
    
    # 默认配置
    default_config = {
        'chunking': {
            'chunk_size': 600,
            'overlap_size': 80,
            'preserve_code_blocks': True,
        },
        'quality_control': {
            'min_quality_threshold': 0.6,
        },
        'agentic_rag': {
            'max_iterations': 3,
            'enable_reflection': True,
            'enable_planning': True,
        }
    }
    
    # 应用配置覆盖
    if config_overrides:
        default_config.update(config_overrides)
    
    try:
        # 处理文档并生成知识库
        knowledge_file = await process_documents_to_knowledge(
            document_paths=docs_dir,
            domain=domain,
            output_path=output_dir,
            config=default_config
        )
        
        logger.info(f"✅ 知识库构建完成!")
        logger.info(f"📄 知识库文件: {knowledge_file}")
        logger.info(f"📊 处理报告: {Path(knowledge_file).parent / f'{domain}_processing_report.md'}")
        
        return knowledge_file
        
    except Exception as e:
        logger.error(f"❌ 知识库构建失败: {e}")
        raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="通用知识库构建工具")
    
    parser.add_argument(
        "docs_path",
        help="文档目录路径"
    )
    
    parser.add_argument(
        "--domain", "-d",
        default="general",
        help="领域标识 (如: fpga, ai, web等)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出目录路径 (可选)"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=600,
        help="文本分块大小 (默认: 600)"
    )
    
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.6,
        help="质量阈值 (默认: 0.6)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 构建配置覆盖
    config_overrides = {
        'chunking': {
            'chunk_size': args.chunk_size,
        },
        'quality_control': {
            'min_quality_threshold': args.quality_threshold,
        }
    }
    
    # 运行构建
    try:
        asyncio.run(build_knowledge_base(
            docs_path=args.docs_path,
            domain=args.domain,
            output_path=args.output,
            config_overrides=config_overrides
        ))
    except KeyboardInterrupt:
        logger.info("构建被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"构建失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 