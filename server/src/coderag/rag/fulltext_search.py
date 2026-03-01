from typing import List, Dict, Any, Optional
import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, And, Or
import shutil


class FullTextSearcher:
    """基于 Whoosh 的全文搜索引擎
    
    提供本地全文检索功能，支持：
    - 多种分词器
    - 短语搜索
    - 模糊搜索
    - 权重配置
    """
    
    def __init__(
        self,
        index_dir: str = "data/whoosh_index",
        schema_fields: Optional[Dict[str, str]] = None
    ):
        """初始化全文搜索引擎
        
        Args:
            index_dir: 索引存储目录
            schema_fields: 自定义 schema 字段定义
        """
        self.index_dir = index_dir
        self.index = None
        self.schema = self._build_schema(schema_fields)
        self._init_index()
    
    def _build_schema(self, custom_fields: Optional[Dict[str, str]] = None) -> Schema:
        """构建索引 schema
        
        Args:
            custom_fields: 自定义字段配置
            
        Returns:
            Whoosh Schema 对象
        """
        fields = {
            "id": ID(stored=True, unique=True),
            "content": TEXT(stored=True, spelling=True),
            "file_path": ID(stored=True),
            "start_line": NUMERIC(stored=True),
            "end_line": NUMERIC(stored=True),
        }
        
        if custom_fields:
            fields.update(custom_fields)
        
        return Schema(**fields)
    
    def _init_index(self):
        """初始化索引目录"""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir, exist_ok=True)
        
        if index.exists_in(self.index_dir):
            self.index = index.open_dir(self.index_dir)
        else:
            self.index = index.create_in(self.index_dir, self.schema)
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """批量添加文档到索引
        
        Args:
            documents: 文档列表，每项需包含 'id' 和 'content' 字段
            
        Returns:
            添加的文档数量
        """
        if not documents:
            return 0
        
        writer = self.index.writer()
        doc_count = 0
        
        for doc in documents:
            doc_id = doc.get('id', doc.get('file_path', f"doc_{doc_count}"))
            
            writer.add_document(
                id=doc_id,
                content=doc.get('content', ''),
                file_path=doc.get('file_path', ''),
                start_line=doc.get('start_line', 0),
                end_line=doc.get('end_line', 0),
            )
            doc_count += 1
        
        writer.commit()
        return doc_count
    
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """更新单个文档
        
        Args:
            doc_id: 文档 ID
            document: 文档内容
            
        Returns:
            是否更新成功
        """
        try:
            writer = self.index.writer()
            writer.update_document(
                id=doc_id,
                content=document.get('content', ''),
                file_path=document.get('file_path', ''),
                start_line=document.get('start_line', 0),
                end_line=document.get('end_line', 0),
            )
            writer.commit()
            return True
        except Exception as e:
            print(f"Failed to update document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        try:
            writer = self.index.writer()
            writer.delete_by_term('id', doc_id)
            writer.commit()
            return True
        except Exception:
            return False
    
    def search(
        self,
        query_str: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
        boost: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """搜索文档
        
        Args:
            query_str: 查询字符串
            limit: 返回结果数量
            fields: 搜索字段列表，None 时默认搜索 content
            boost: 字段权重配置
            
        Returns:
            搜索结果列表
        """
        if not query_str:
            return []
        
        with self.index.searcher() as searcher:
            if fields is None:
                fields = ["content"]
            
            if len(fields) == 1:
                parser = QueryParser(fields[0], schema=self.schema)
            else:
                parser = MultifieldParser(fields, schema=self.schema)
            
            query = parser.parse(query_str)
            results = searcher.search(query, limit=limit)
            
            search_results = []
            for hit in results:
                result = {
                    "id": hit["id"],
                    "content": hit["content"],
                    "file_path": hit["file_path"],
                    "start_line": hit.get("start_line", 0),
                    "end_line": hit.get("end_line", 0),
                    "score": hit.score,
                }
                search_results.append(result)
            
            return search_results
    
    def search_by_filter(
        self,
        query_str: str,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """带过滤条件的搜索
        
        Args:
            query_str: 查询字符串
            filters: 过滤条件
            limit: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        if not query_str:
            return []
        
        with self.index.searcher() as searcher:
            parser = QueryParser("content", schema=self.schema)
            query = parser.parse(query_str)
            
            filter_queries = []
            for field, value in filters.items():
                if isinstance(value, str):
                    filter_queries.append(Term(field, value))
                elif isinstance(value, (list, tuple)):
                    or_queries = [Term(field, v) for v in value]
                    filter_queries.append(Or(or_queries))
            
            if filter_queries:
                query = And([query] + filter_queries)
            
            results = searcher.search(query, limit=limit)
            
            search_results = []
            for hit in results:
                result = {
                    "id": hit["id"],
                    "content": hit["content"],
                    "file_path": hit["file_path"],
                    "start_line": hit.get("start_line", 0),
                    "end_line": hit.get("end_line", 0),
                    "score": hit.score,
                }
                search_results.append(result)
            
            return search_results
    
    def suggest(self, prefix: str, field: str = "content", limit: int = 5) -> List[str]:
        """获取搜索建议（自动补全）
        
        Args:
            prefix: 输入前缀
            field: 字段名
            limit: 返回建议数量
            
        Returns:
            建议列表
        """
        if not prefix:
            return []
        
        with self.index.searcher() as searcher:
            reader = searcher.reader()
            suggestions = []
            
            for fields in reader.all_stored_fields():
                if field in fields:
                    text = fields[field].lower()
                    if text.startswith(prefix.lower()):
                        suggestions.append(fields[field])
                        if len(suggestions) >= limit:
                            break
            
            return suggestions
    
    def clear_index(self):
        """清空索引"""
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)
        os.makedirs(self.index_dir, exist_ok=True)
        self.index = index.create_in(self.index_dir, self.schema)
    
    def get_doc_count(self) -> int:
        """获取索引中的文档数量"""
        with self.index.searcher() as searcher:
            return searcher.doc_count()
    
    def __repr__(self) -> str:
        return f"FullTextSearcher(index_dir='{self.index_dir}', doc_count={self.get_doc_count()})"


def create_searcher(
    index_dir: str = "data/whoosh_index",
    **kwargs
) -> FullTextSearcher:
    """创建全文搜索引擎实例的便捷函数
    
    Args:
        index_dir: 索引目录
        **kwargs: 其他参数
        
    Returns:
        FullTextSearcher 实例
    """
    return FullTextSearcher(index_dir=index_dir, **kwargs)
