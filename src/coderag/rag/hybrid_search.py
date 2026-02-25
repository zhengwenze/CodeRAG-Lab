from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from coderag.rag.fulltext_search import FullTextSearcher
from coderag.settings import settings


class HybridSearcher:
    """混合搜索引擎：向量检索 + 全文搜索并行查询
    
    借鉴 AIFlowy 的混合检索架构设计，实现：
    - 向量库与全文搜索引擎并行查询
    - 结果合并与去重
    - 可配置的结果融合策略
    """
    
    def __init__(
        self,
        fulltext_searcher: Optional[FullTextSearcher] = None,
        vector_weight: float = 0.5,
        fulltext_weight: float = 0.5,
        enable_parallel: bool = True,
        max_workers: int = 2
    ):
        """初始化混合搜索引擎
        
        Args:
            fulltext_searcher: 全文搜索引擎实例
            vector_weight: 向量检索结果权重 (0-1)
            fulltext_weight: 全文检索结果权重 (0-1)
            enable_parallel: 是否启用并行查询
            max_workers: 并行查询的最大线程数
        """
        self.fulltext_searcher = fulltext_searcher
        self.vector_weight = vector_weight
        self.fulltext_weight = fulltext_weight
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers
        
        total_weight = vector_weight + fulltext_weight
        if total_weight > 0:
            self.vector_weight = vector_weight / total_weight
            self.fulltext_weight = fulltext_weight / total_weight
    
    def set_vector_searcher(self, vector_search_func):
        """设置向量检索函数
        
        Args:
            vector_search_func: 向量检索函数，签名为 (query, top_k) -> List[Dict]
        """
        self.vector_search_func = vector_search_func
    
    def set_fulltext_searcher(self, searcher: FullTextSearcher):
        """设置全文搜索引擎"""
        self.fulltext_searcher = searcher
    
    def search(
        self,
        query: str,
        embedding: Optional[List[float]] = None,
        top_k: int = 10,
        min_similarity: float = 0.0,
        use_fulltext: bool = True,
        use_vector: bool = True
    ) -> List[Dict[str, Any]]:
        """执行混合搜索
        
        Args:
            query: 查询文本
            embedding: 查询向量 (用于向量检索)
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值
            use_fulltext: 是否使用全文检索
            use_vector: 是否使用向量检索
            
        Returns:
            合并排序后的结果列表
        """
        results = {}
        
        if self.enable_parallel:
            results = self._parallel_search(
                query, embedding, top_k, use_fulltext, use_vector
            )
        else:
            results = self._sequential_search(
                query, embedding, top_k, use_fulltext, use_vector
            )
        
        combined = self._merge_results(
            results, top_k, min_similarity
        )
        
        return combined
    
    def _parallel_search(
        self,
        query: str,
        embedding: Optional[List[float]],
        top_k: int,
        use_fulltext: bool,
        use_vector: bool
    ) -> Dict[str, List[Dict[str, Any]]]:
        """并行执行向量和全文搜索"""
        results = {"vector": [], "fulltext": []}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            if use_vector and hasattr(self, 'vector_search_func') and embedding:
                futures['vector'] = executor.submit(
                    self.vector_search_func, query, embedding, top_k * 2
                )
            
            if use_fulltext and self.fulltext_searcher:
                futures['fulltext'] = executor.submit(
                    self.fulltext_searcher.search, query, top_k * 2
                )
            
            for key, future in futures.items():
                try:
                    results[key] = future.result() or []
                except Exception as e:
                    print(f"{key} search failed: {e}")
                    results[key] = []
        
        return results
    
    def _sequential_search(
        self,
        query: str,
        embedding: Optional[List[float]],
        top_k: int,
        use_fulltext: bool,
        use_vector: bool
    ) -> Dict[str, List[Dict[str, Any]]]:
        """顺序执行向量和全文搜索"""
        results = {"vector": [], "fulltext": []}
        
        if use_vector and hasattr(self, 'vector_search_func') and embedding:
            try:
                results["vector"] = self.vector_search_func(
                    query, embedding, top_k * 2
                ) or []
            except Exception as e:
                print(f"Vector search failed: {e}")
        
        if use_fulltext and self.fulltext_searcher:
            try:
                results["fulltext"] = self.fulltext_searcher.search(
                    query, top_k * 2
                ) or []
            except Exception as e:
                print(f"Fulltext search failed: {e}")
        
        return results
    
    def _merge_results(
        self,
        results: Dict[str, List[Dict[str, Any]]],
        top_k: int,
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        """合并搜索结果
        
        1. 去重 (基于 doc_id)
        2. 分数归一化
        3. 加权融合
        4. 排序并返回 top_k
        """
        unique_docs = {}
        
        vector_results = results.get("vector", [])
        fulltext_results = results.get("fulltext", [])
        
        vector_max = max(
            (doc.get("score", 0) for doc in vector_results),
            default=1.0
        )
        fulltext_max = max(
            (doc.get("score", 0) for doc in fulltext_results),
            default=1.0
        )
        
        for doc in vector_results:
            doc_id = doc.get("id") or doc.get("file_path", "")
            if doc_id not in unique_docs:
                unique_docs[doc_id] = doc.copy()
                unique_docs[doc_id]["sources"] = ["vector"]
            else:
                unique_docs[doc_id]["sources"].append("vector")
            
            if vector_max > 0:
                unique_docs[doc_id]["normalized_vector_score"] = (
                    doc.get("score", 0) / vector_max
                )
        
        for doc in fulltext_results:
            doc_id = doc.get("id") or doc.get("file_path", "")
            if doc_id not in unique_docs:
                unique_docs[doc_id] = doc.copy()
                unique_docs[doc_id]["sources"] = ["fulltext"]
            else:
                unique_docs[doc_id]["sources"].append("fulltext")
            
            if fulltext_max > 0:
                unique_docs[doc_id]["normalized_fulltext_score"] = (
                    doc.get("score", 0) / fulltext_max
                )
        
        combined_docs = list(unique_docs.values())
        
        for doc in combined_docs:
            vector_score = doc.get("normalized_vector_score", 0)
            fulltext_score = doc.get("normalized_fulltext_score", 0)
            
            doc["combined_score"] = (
                self.vector_weight * vector_score +
                self.fulltext_weight * fulltext_score
            )
            
            doc["sources"] = list(set(doc.get("sources", [])))
        
        filtered_docs = [
            doc for doc in combined_docs
            if doc.get("combined_score", 0) >= min_similarity
        ]
        
        filtered_docs.sort(
            key=lambda x: x.get("combined_score", 0),
            reverse=True
        )
        
        for i, doc in enumerate(filtered_docs):
            doc["rank"] = i + 1
        
        return filtered_docs[:top_k]
    
    def add_to_fulltext_index(self, documents: List[Dict[str, Any]]) -> int:
        """添加文档到全文索引
        
        Args:
            documents: 文档列表
            
        Returns:
            添加的文档数量
        """
        if not self.fulltext_searcher:
            return 0
        
        return self.fulltext_searcher.add_documents(documents)
    
    def clear_fulltext_index(self):
        """清空全文索引"""
        if self.fulltext_searcher:
            self.fulltext_searcher.clear_index()
    
    def __repr__(self) -> str:
        return (
            f"HybridSearcher("
            f"vector_weight={self.vector_weight}, "
            f"fulltext_weight={self.fulltext_weight}, "
            f"parallel={self.enable_parallel})"
        )


def create_hybrid_searcher(
    fulltext_index_dir: str = "data/whoosh_index",
    vector_weight: float = 0.5,
    fulltext_weight: float = 0.5,
    **kwargs
) -> HybridSearcher:
    """创建混合搜索引擎实例的便捷函数
    
    Args:
        fulltext_index_dir: 全文索引目录
        vector_weight: 向量权重
        fulltext_weight: 全文权重
        **kwargs: 其他参数
        
    Returns:
        HybridSearcher 实例
    """
    fulltext_searcher = FullTextSearcher(index_dir=fulltext_index_dir)
    return HybridSearcher(
        fulltext_searcher=fulltext_searcher,
        vector_weight=vector_weight,
        fulltext_weight=fulltext_weight,
        **kwargs
    )
