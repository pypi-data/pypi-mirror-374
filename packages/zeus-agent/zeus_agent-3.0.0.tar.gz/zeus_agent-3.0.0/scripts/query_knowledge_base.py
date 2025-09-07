#!/usr/bin/env python3
"""
知识库查询工具
演示如何查询和使用构建的知识库
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import re


class KnowledgeBaseQuery:
    """知识库查询器"""
    
    def __init__(self, knowledge_base_path: str):
        self.kb_path = Path(knowledge_base_path)
        self.knowledge_data = self._load_knowledge_base()
        self.knowledge_items = self.knowledge_data.get('knowledge_items', [])
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """加载知识库"""
        if not self.kb_path.exists():
            raise FileNotFoundError(f"知识库文件不存在: {self.kb_path}")
        
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        # 兼容两种格式的知识库
        metadata = self.knowledge_data.get('metadata', {})
        statistics = self.knowledge_data.get('statistics', {})
        
        # 如果没有statistics字段，从metadata中获取信息
        if not statistics and metadata:
            statistics = {
                'total_items': metadata.get('total_items', len(self.knowledge_items)),
                'total_chunks': sum(len(item.get('chunks', [])) for item in self.knowledge_items),
                'processed_files': len(self.knowledge_items),  # 估算值
                'total_files': len(self.knowledge_items)  # 估算值
            }
        
        return {
            'metadata': metadata,
            'statistics': statistics,
            'total_items': len(self.knowledge_items)
        }
    
    def search_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """按关键词搜索"""
        keyword_lower = keyword.lower()
        results = []
        
        for item in self.knowledge_items:
            relevance_score = 0.0
            
            # 标题匹配
            if keyword_lower in item['title'].lower():
                relevance_score += 2.0
            
            # 标签匹配
            for tag in item.get('tags', []):
                if keyword_lower in tag.lower():
                    relevance_score += 1.0
            
            # 内容匹配
            for chunk in item.get('chunks', []):
                if keyword_lower in chunk['content'].lower():
                    relevance_score += 0.5
                    break
            
            # 关键词匹配
            for chunk in item.get('chunks', []):
                for kw in chunk.get('keywords', []):
                    if keyword_lower in kw.lower():
                        relevance_score += 0.3
                        break
            
            if relevance_score > 0:
                results.append({
                    'item': item,
                    'relevance_score': relevance_score
                })
        
        # 按相关度排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def search_by_type(self, knowledge_type: str) -> List[Dict[str, Any]]:
        """按知识类型搜索"""
        results = []
        for item in self.knowledge_items:
            if item.get('knowledge_type') == knowledge_type:
                results.append(item)
        return results
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """按标签搜索"""
        tag_lower = tag.lower()
        results = []
        for item in self.knowledge_items:
            for item_tag in item.get('tags', []):
                if tag_lower in item_tag.lower():
                    results.append(item)
                    break
        return results
    
    def get_item_by_id(self, item_id: str) -> Dict[str, Any]:
        """根据ID获取知识项"""
        for item in self.knowledge_items:
            if item.get('item_id') == item_id:
                return item
        return None
    
    def list_all_tags(self) -> List[str]:
        """列出所有标签"""
        all_tags = set()
        for item in self.knowledge_items:
            all_tags.update(item.get('tags', []))
        return sorted(list(all_tags))
    
    def list_all_types(self) -> List[str]:
        """列出所有知识类型"""
        all_types = set()
        for item in self.knowledge_items:
            all_types.add(item.get('knowledge_type'))
        return sorted(list(all_types))
    
    def get_chunk_content(self, item_id: str, chunk_id: str = None) -> str:
        """获取知识块内容"""
        item = self.get_item_by_id(item_id)
        if not item:
            return ""
        
        if chunk_id:
            for chunk in item.get('chunks', []):
                if chunk.get('chunk_id') == chunk_id:
                    return chunk.get('content', '')
            return ""
        else:
            # 返回所有块的内容
            contents = []
            for chunk in item.get('chunks', []):
                contents.append(chunk.get('content', ''))
            return '\n\n'.join(contents)


def print_search_results(results: List[Dict[str, Any]], show_content: bool = False):
    """打印搜索结果"""
    if not results:
        print("❌ 没有找到相关结果")
        return
    
    print(f"🔍 找到 {len(results)} 个相关结果:\n")
    
    for i, result in enumerate(results, 1):
        if 'item' in result:  # 关键词搜索结果
            item = result['item']
            relevance = result['relevance_score']
            print(f"{i}. 📄 **{item['title']}** (相关度: {relevance:.1f})")
        else:  # 直接的item结果
            item = result
            print(f"{i}. 📄 **{item['title']}**")
        
        print(f"   类型: {item['knowledge_type']}")
        print(f"   标签: {', '.join(item.get('tags', []))}")
        print(f"   块数: {len(item.get('chunks', []))}")
        print(f"   来源: {item.get('source_file', 'Unknown')}")
        
        if show_content and item.get('chunks'):
            # 显示第一个块的摘要
            first_chunk = item['chunks'][0]
            summary = first_chunk.get('summary', '')
            if len(summary) > 200:
                summary = summary[:200] + "..."
            print(f"   摘要: {summary}")
        
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="知识库查询工具")
    parser.add_argument("knowledge_base", help="知识库JSON文件路径")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 统计信息命令
    stats_parser = subparsers.add_parser('stats', help='显示知识库统计信息')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索知识')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.add_argument('--limit', '-l', type=int, default=5, help='结果数量限制')
    search_parser.add_argument('--content', '-c', action='store_true', help='显示内容摘要')
    
    # 按类型搜索命令
    type_parser = subparsers.add_parser('type', help='按类型搜索')
    type_parser.add_argument('knowledge_type', help='知识类型')
    type_parser.add_argument('--content', '-c', action='store_true', help='显示内容摘要')
    
    # 按标签搜索命令
    tag_parser = subparsers.add_parser('tag', help='按标签搜索')
    tag_parser.add_argument('tag_name', help='标签名称')
    tag_parser.add_argument('--content', '-c', action='store_true', help='显示内容摘要')
    
    # 列出标签命令
    list_tags_parser = subparsers.add_parser('list-tags', help='列出所有标签')
    
    # 列出类型命令
    list_types_parser = subparsers.add_parser('list-types', help='列出所有知识类型')
    
    # 查看内容命令
    content_parser = subparsers.add_parser('content', help='查看知识项内容')
    content_parser.add_argument('item_id', help='知识项ID')
    content_parser.add_argument('--chunk', help='特定块ID')
    
    args = parser.parse_args()
    
    try:
        # 创建查询器
        query = KnowledgeBaseQuery(args.knowledge_base)
        
        if args.command == 'stats':
            stats = query.get_stats()
            metadata = stats['metadata']
            statistics = stats['statistics']
            
            print("📊 知识库统计信息")
            print("=" * 40)
            print(f"领域: {metadata.get('domain', 'Unknown')}")
            print(f"创建时间: {metadata.get('created_time', 'Unknown')}")
            print(f"构建器版本: {metadata.get('builder_version', metadata.get('processor_version', 'Unknown'))}")
            print(f"知识项总数: {statistics.get('total_items', statistics.get('total_knowledge_items', len(query.knowledge_items)))}")
            print(f"知识块总数: {statistics.get('total_chunks', sum(len(item.get('chunks', [])) for item in query.knowledge_items))}")
            print(f"处理文档数: {statistics.get('processed_files', statistics.get('successful_documents', 0))}")
            success_rate = statistics.get('successful_documents', 0) / max(statistics.get('total_documents', 1), 1) * 100
            print(f"成功率: {success_rate:.1f}%")
            
        elif args.command == 'search':
            results = query.search_by_keyword(args.keyword, args.limit)
            print(f"🔍 搜索关键词: '{args.keyword}'")
            print_search_results(results, args.content)
            
        elif args.command == 'type':
            results = query.search_by_type(args.knowledge_type)
            print(f"📂 知识类型: '{args.knowledge_type}'")
            print_search_results(results, args.content)
            
        elif args.command == 'tag':
            results = query.search_by_tag(args.tag_name)
            print(f"🏷️  标签: '{args.tag_name}'")
            print_search_results(results, args.content)
            
        elif args.command == 'list-tags':
            tags = query.list_all_tags()
            print("🏷️  所有标签:")
            for tag in tags:
                print(f"  - {tag}")
            
        elif args.command == 'list-types':
            types = query.list_all_types()
            print("📂 所有知识类型:")
            for ktype in types:
                print(f"  - {ktype}")
            
        elif args.command == 'content':
            content = query.get_chunk_content(args.item_id, args.chunk)
            if content:
                print(f"📄 知识项内容 (ID: {args.item_id}):")
                print("=" * 60)
                print(content)
            else:
                print(f"❌ 未找到知识项: {args.item_id}")
                
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main()) 